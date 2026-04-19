import re
import urllib.parse
import aiohttp
import unicodedata
import logging

from src.utils.files import read_lines


class TorrentSearchProvider:

    def __init__(self):
        self.name = None
        self.trackers = None

    def is_black_list(self, name: str):
        names = ["dodi", "DODI"]
        name = name.lower()
        for n in names:
            if n in name:
                return True
        return False

    async def search(self, name: str, size: int = 100) -> list[dict]:
        trackers = await read_lines("static/txt/trackers.txt")
        trackers = [f"tr={tr}" for tr in trackers if tr]
        self.trackers = "&".join(trackers)

        url = f"https://torrents-csv.com/service/search?q={name}&size={size}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()

                    logging.info(f"Search query: {name} | Found torrents: {len(data.get("torrents"))}")

                    torrents = []
                    for item in data.get('torrents', []):
                        magnet_data = self.check_magnet(item, name)
                        if not magnet_data:
                            continue
                        torrents.append(magnet_data)
                    return torrents

    def check_magnet(self, item: dict, name: str) -> None | dict:
        info_hash = item['infohash']
        magnet_name = item['name']

        if self.is_black_list(magnet_name):
            return None

        if self._remove_trash_magnet_string(magnet_name) != name:
            return None

        size_bytes = item['size_bytes']
        magnet = f"magnet:?xt=urn:btih:{info_hash}&dn={urllib.parse.quote(name)}&{self.trackers}"

        return {
            "name": magnet_name,
            "magnet": magnet,
            "size": size_bytes,
            "seeders": item.get('seeders', 0)
        }

    def _remove_trash_magnet_string(self, raw_name: str, tags_repackers: str = None) -> str:
        if not tags_repackers:
            tags_repackers = [
                'repack', 'fitgirl', 'dodi', 'xatab', 'corepack', 'catalyst', 'mechanic', 'gog',
                'plaza', 'kaos', 'razor1911', 'skidrow', 'pkg', 'nsp', 'ps4', 'ps5', 'xbox', 'switch',
                'multirepack', 'cracfix', 'prophet', 'dodge', 'doge'
            ]
        s = (raw_name or "")
        s = unicodedata.normalize("NFKC", s)
        s = re.sub(r"\[.*?\]|\(.*?\)|\{.*?\}", " ", s)
        s = re.sub(r"\b(?:v|version|update|patch)\s*[\d\.]+\w*\b", " ", s, flags=re.IGNORECASE)
        s = s.replace('_', ' ').replace('.', ' ').replace('/', ' ')
        parts = [p.strip() for p in re.split(r'[-–—|]', s) if p.strip()]
        if parts:
            s = max(parts, key=lambda p: len(re.sub(r'[^A-Za-z0-9]', '', p)))

        pattern = r"\b(?:" + '|'.join(re.escape(w) for w in tags_repackers) + r")\b"
        s = re.sub(pattern, ' ', s, flags=re.IGNORECASE)
        s = re.sub(r'\bMULTI[iI]?\d+\b', ' ', s)
        s = re.sub(r"\b(?:incl|including|with dlc|all dlc|deluxe edition|complete edition|maxed out edition)\b", ' ', s, flags=re.IGNORECASE)
        s = re.sub(r"[^A-Za-z0-9 :'\-]", ' ', s)
        s = re.sub(r'\s+', ' ', s).strip()

        return s
