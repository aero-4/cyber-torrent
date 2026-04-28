import html
import re
import urllib.parse
import aiohttp
import unicodedata
import logging

from src.utils.files import read_lines


class TorrentSearchProvider:
    # Теги репакеров и платформ, которые мы ПРОСТО ИГНОРИРУЕМ при сравнении названий
    # (Они легитимны для игр, мы их удаляем, чтобы сравнить "Thief" и "Thief")
    GAME_TAGS = {
        "repack", "fitgirl", "dodi", "xatab", "corepack", "catalyst",
        "mechanic", "mechanics", "gog", "plaza", "kaos", "razor1911", "skidrow",
        "reloaded", "prophet", "elamigos", "nosteam", "steamrip", "cpy", "rld",
        "codex", "decepticon", "qoob", "brick", "mr", "dj", "selizen", "selezen",
        "wanterlude", "darksiders", "rjaa", "rg", "gameloaded", "pc", "windows",
        "linux", "mac", "steam", "multi", "eng", "rus", "ru", "en", "complete",
        "deluxe", "gold", "ultimate", "premium", "goty", "game", "edition",
        "remastered", "enhanced", "anniversary", "collection", "bundle", "dlc",
        "update", "patch", "build", "iso", "crack", "license"
    }

    # СТОП-СЛОВА: Если мы видим это в названии, это 100% фильм, сериал, музыка или книга. БРАКУЕМ СРАЗУ.
    MEDIA_TRASH_RE = re.compile(
        r"\b("
        r"1080p|720p|2160p|4k|480p|"  # Разрешения кино
        r"bluray|brrip|bdrip|dvdrip|web-?dl|webrip|hdtv|"  # Источники
        r"x264|x265|hevc|avc|10bit|hdr|"  # Кодеки видео
        r"yify|yts|tigole|eztv|rmteam|flux|oft|r00t|"  # Релиз-группы кино/тв
        r"s\d{1,2}e\d{1,2}|s\d{1,2}|season|"  # Сериалы (S01E01, S01)
        r"aac\s?5\.1|dts-hd|atmos|ddp5\.1|"  # Аудио кино
        r"flac|mp3|alac|"  # Музыка
        r"epub|mobi|pdf"  # Книги
        r")\b",
        re.IGNORECASE
    )

    # Регулярки для вычищения мусора (версии, года), чтобы они не ломали математику слов
    VERSION_RE = re.compile(r"\b(?:v|ver|version|build|update|patch|upd)\s*[\d]+(?:[.\-]\d+)*(?:[a-z])?\b", re.IGNORECASE)
    YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
    MULTI_RE = re.compile(r"\bmulti\d+\b", re.IGNORECASE)

    def __init__(self):
        self.name = None
        self.trackers_string = ""
        self._trackers_loaded = False

    async def _load_trackers(self):
        if not self._trackers_loaded:
            try:
                trackers = await read_lines("static/txt/trackers.txt")
                trackers = [f"tr={urllib.parse.quote(tr)}" for tr in trackers if tr]
                self.trackers_string = "&".join(trackers)
            except Exception as e:
                logging.error("Failed to load trackers: %s", e)
                self.trackers_string = ""
            self._trackers_loaded = True

    def is_black_list(self, name: str) -> bool:
        bad = ("igruha",)  # Убрал dodi, иначе ты не скачаешь нормальные репаки
        low = (name or "").casefold()
        return any(x in low for x in bad)

    def _is_media_trash(self, name: str) -> bool:
        """Проверяет, является ли торрент фильмом, сериалом или музыкой."""
        return bool(self.MEDIA_TRASH_RE.search(name))

    def _get_clean_tokens(self, text: str) -> list[str]:
        """Очищает строку и разбивает на полезные слова."""
        text = html.unescape(text or "")
        text = unicodedata.normalize("NFKC", text).casefold()

        text = self.VERSION_RE.sub(" ", text)
        text = self.YEAR_RE.sub(" ", text)
        text = self.MULTI_RE.sub(" ", text)

        # Заменяем всю пунктуацию на пробелы
        text = re.sub(r"[^a-z0-9]+", " ", text)

        tokens = []
        for t in text.split():
            # Добавляем только те слова, которые не являются тегами игр
            if t and t not in self.GAME_TAGS:
                tokens.append(t)
        return tokens

    def _accept_magnet(self, magnet_name: str, original_name: str) -> bool:
        # 1. Жесткие блэклисты
        if self.is_black_list(magnet_name) or self._is_media_trash(magnet_name):
            return False

        # 2. Получаем чистые токены (без годов, версий и тегов FitGirl)
        orig_tokens = self._get_clean_tokens(original_name)
        cand_tokens = self._get_clean_tokens(magnet_name)

        if not orig_tokens or not cand_tokens:
            return False

        # 3. Математика слов
        overlap = len(set(cand_tokens) & set(orig_tokens))
        coverage = overlap / len(orig_tokens)

        # Доля "мусора" в самом торренте. Если искали Thief(1), а нашли Thief Simulator(2) -> ratio = 0.5
        candidate_ratio = overlap / max(len(cand_tokens), 1)

        # 4. Логика принятия решений
        if len(orig_tokens) == 1:
            # Для однословных запросов (Thief, Doom, Control) совпадение должно быть идеальным.
            # Если в названии есть хоть одно лишнее слово (Simulator) — бракуем.
            return coverage == 1.0 and candidate_ratio == 1.0

        if len(orig_tokens) == 2:
            # Для двух слов (Thief Simulator) допускаем 1-2 лишних слова в торренте, но не больше
            return coverage == 1.0 and candidate_ratio >= 0.5

        # Для длинных названий допускаем незначительную потерю слов
        return coverage >= 0.75 and candidate_ratio >= 0.4

    def check_magnet(self, item: dict, name: str) -> None | dict:
        info_hash = item.get("infohash")
        magnet_name = item.get("name", "")

        if not info_hash or not magnet_name:
            return None

        if not self._accept_magnet(magnet_name, name):
            return None

        logging.info("Magnet MATCHED: %s (Original: %s)", magnet_name, name)

        size_bytes = item.get("size_bytes", 0)
        size_gb = float(round(size_bytes / (1024 * 1024 * 1024), 2))
        magnet = f"magnet:?xt=urn:btih:{info_hash}&dn={urllib.parse.quote(magnet_name)}"

        if self.trackers_string:
            magnet += f"&{self.trackers_string}"

        return {
            "name": magnet_name,
            "magnet": magnet,
            "size": size_gb,
            "seeders": item.get("seeders", 0),
        }

    async def search(self, name: str, size: int = 100) -> list[dict]:
        await self._load_trackers()

        url = f"https://torrents-csv.com/service/search?q={urllib.parse.quote(name)}&size={size}"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status != 200:
                        logging.warning("Torrents-csv returned status %s", response.status)
                        return []
                    data = await response.json()
            except Exception as e:
                logging.error("Network error while fetching torrents: %s", e)
                return []

        logging.info("Search query: %s | Found raw torrents: %s", name, len(data.get("torrents", [])))

        torrents = []
        for item in data.get("torrents", []):
            magnet_data = self.check_magnet(item, name)
            if magnet_data:
                torrents.append(magnet_data)

        torrents.sort(key=lambda x: x["seeders"], reverse=True)
        return torrents