import html
import re
import urllib.parse
import aiohttp
import unicodedata
import logging

from src.utils.files import read_lines


class TorrentSearchProvider:
    TRASH_WORDS = {
        "repack", "fitgirl", "dodi", "xatab", "corepack", "catalyst",
        "mechanic", "mechanics", "gog", "plaza", "kaos", "razor1911", "skidrow",
        "pkg", "nsp", "xci", "iso", "reloaded", "prophet", "elamigos", "nosteam",
        "steamrip", "cpy", "rld", "codex", "decepticon", "qoob", "brick", "mr",
        "dj", "selizen", "selezen", "wanterlude", "darksiders", "rjaa", "rg",
        "gameloaded",
    }

    QUALITY_WORDS = {
        "1080p", "720p", "2160p", "480p", "4k", "web", "webrip", "webdl", "web-dl",
        "bluray", "brrip", "hdrip", "dvdrip", "r5", "remux", "x264", "x265", "hevc",
        "avc", "aac", "dts", "flac", "mp3", "10bit", "8bit", "lossless", "multi",
        "multi2", "multi3", "multi4", "multi5", "multi6", "multi7", "multi8",
        "multi9", "multi10", "eng", "english", "rus", "russian",
    }

    PLATFORM_WORDS = {
        "pc", "windows", "linux", "mac", "ps3", "ps4", "ps5", "xbox", "xbox360",
        "xboxone", "switch", "android", "ios", "macos", "steam", "gog",
    }

    EDITION_WORDS = {
        "complete", "deluxe", "gold", "ultimate", "premium", "goty", "game",
        "edition", "remastered", "enhanced", "anniversary", "collection", "bundle",
        "all", "dlc", "with", "include", "including",
    }

    VERSION_RE = re.compile(
        r"\b(?:v|ver|version|build|update|patch|upd)\s*[\d]+(?:[.\-]\d+)*(?:[a-z])?\b",
        re.IGNORECASE,
    )
    YEAR_RE = re.compile(r"^(19\d{2}|20\d{2})$")

    def __init__(self):
        self.name = None
        self.trackers = None

    def is_black_list(self, name: str) -> bool:
        bad = ("dodi", "igruha")
        low = (name or "").casefold()
        return any(x in low for x in bad)

    async def search(self, name: str, size: int = 100) -> list[dict]:
        trackers = await read_lines("static/txt/trackers.txt")
        trackers = [f"tr={tr}" for tr in trackers if tr]
        self.trackers = "&".join(trackers)

        url = f"https://torrents-csv.com/service/search?q={urllib.parse.quote(name)}&size={size}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return []

                data = await response.json()
                logging.info("Search query: %s | Found torrents: %s", name, len(data.get("torrents", [])))

                torrents = []
                for item in data.get("torrents", []):
                    magnet_data = self.check_magnet(item, name)
                    if magnet_data:
                        torrents.append(magnet_data)
                return torrents

    def _tokenize(self, text: str) -> list[str]:
        text = html.unescape(text or "")
        text = unicodedata.normalize("NFKC", text).casefold()
        text = re.sub(r"[\u200b-\u200f\ufeff]", "", text)
        text = text.replace("’", "").replace("'", "")
        text = text.translate(str.maketrans({
            "_": " ",
            ".": " ",
            "/": " ",
            "\\": " ",
            "|": " ",
            "–": " ",
            "—": " ",
            ":": " ",
            "™": " ",
            "©": " ",
            "®": " ",
        }))
        text = re.sub(r"[^a-z0-9]+", " ", text)
        return [t for t in text.split() if t]

    def _is_noise_token(self, token: str) -> bool:
        if not token:
            return True
        if token in self.TRASH_WORDS:
            return True
        if token in self.QUALITY_WORDS:
            return True
        if token in self.PLATFORM_WORDS:
            return True
        if token in self.EDITION_WORDS:
            return True
        if re.fullmatch(r"multi\d+", token):
            return True
        if re.fullmatch(r"\d+p", token):
            return True
        return False

    def _normalize_title(self, text: str) -> str:
        tokens = []
        for tok in self._tokenize(text):
            if self._is_noise_token(tok):
                continue
            if self.YEAR_RE.fullmatch(tok):
                tokens.append(tok)
                continue
            tokens.append(tok)
        return " ".join(tokens)

    def _title_coverage(self, candidate: str, original: str) -> float:
        c = set(self._tokenize(self._normalize_title(candidate)))
        o = set(self._tokenize(self._normalize_title(original)))
        if not c or not o:
            return 0.0
        return len(c & o) / len(o)

    def _has_trigger_words(self, text: str) -> bool:
        tokens = set(self._tokenize(text))
        return any(
            t in tokens
            for t in (self.TRASH_WORDS | self.QUALITY_WORDS | self.PLATFORM_WORDS | self.EDITION_WORDS)
        )

    def _accept_magnet(self, magnet_name: str, original_name: str) -> bool:
        if self.is_black_list(magnet_name):
            return False

        candidate_norm = self._normalize_title(magnet_name)
        original_norm = self._normalize_title(original_name)

        if not candidate_norm or not original_norm:
            return False

        candidate_tokens = set(candidate_norm.split())
        original_tokens = set(original_norm.split())

        if not candidate_tokens or not original_tokens:
            return False

        if original_norm in candidate_norm or candidate_norm in original_norm:
            return True

        overlap = len(candidate_tokens & original_tokens)
        coverage = overlap / len(original_tokens)

        has_noise = self._has_trigger_words(magnet_name)

        if has_noise:
            threshold = 0.72
        else:
            threshold = 0.45

        if len(original_tokens) <= 2:
            threshold = 0.35 if not has_noise else 0.6

        return coverage >= threshold

    def check_magnet(self, item: dict, name: str) -> None | dict:
        info_hash = item["infohash"]
        magnet_name = item["name"]

        if not self._accept_magnet(magnet_name, name):
            return None

        logging.info("Magnet name - %s, Original name - %s", magnet_name, name)

        size_bytes = item["size_bytes"]
        magnet = f"magnet:?xt=urn:btih:{info_hash}&dn={urllib.parse.quote(name)}&{self.trackers}"

        return {
            "name": magnet_name,
            "magnet": magnet,
            "size": size_bytes,
            "seeders": item.get("seeders", 0),
        }