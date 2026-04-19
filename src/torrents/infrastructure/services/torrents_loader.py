import asyncio
import re
import urllib.parse
from pathlib import Path
from urllib.parse import quote

import aiohttp
import requests
import unicodedata
import difflib
import logging

from aiohttp import ClientTimeout
from scrapers.x1337 import Scraper1337, Params1337, Category1337, Order1337
from slugify import slugify

from src.torrents.domain.entities import TorrentCreate
from src.utils.files import read_lines


def improved_clean_title(raw_name: str) -> str:
    s = (raw_name or "")
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\[.*?\]|\(.*?\)|\{.*?\}", " ", s)
    s = re.sub(r"\b(?:v|version|update|patch)\s*[\d\.]+\w*\b", " ", s, flags=re.IGNORECASE)
    s = s.replace('_', ' ').replace('.', ' ').replace('/', ' ')
    parts = [p.strip() for p in re.split(r'[-–—|]', s) if p.strip()]
    if parts:
        s = max(parts, key=lambda p: len(re.sub(r'[^A-Za-z0-9]', '', p)))

    garbage = [
        'repack', 'fitgirl', 'dodi', 'xatab', 'corepack', 'catalyst', 'mechanic', 'gog',
        'plaza', 'kaos', 'razor1911', 'skidrow', 'pkg', 'nsp', 'ps4', 'ps5', 'xbox', 'switch',
        'multirepack', 'cracfix', 'prophet', 'dodge', 'doge'
    ]
    pattern = r"\b(?:" + '|'.join(re.escape(w) for w in garbage) + r")\b"
    s = re.sub(pattern, ' ', s, flags=re.IGNORECASE)
    s = re.sub(r'\bMULTI[iI]?\d+\b', ' ', s)
    s = re.sub(r"\b(?:incl|including|with dlc|all dlc|deluxe edition|complete edition|maxed out edition)\b", ' ', s, flags=re.IGNORECASE)
    s = re.sub(r"[^A-Za-z0-9 :'\-]", ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def normalize_for_match(name: str) -> str:
    if not name:
        return ""
    n = unicodedata.normalize("NFKC", name).casefold()
    n = re.sub(r'[^a-z0-9\s]', ' ', n)
    n = re.sub(r'\s+', ' ', n).strip()
    return n


def fuzzy_match(a: str, b: str, threshold: float = 0.88):
    a_n = normalize_for_match(a)
    b_n = normalize_for_match(b)
    if not a_n or not b_n:
        return False, 0.0
    ratio = difflib.SequenceMatcher(None, a_n, b_n).ratio()
    return (ratio >= threshold), ratio


class TorrentSearchProvider:

    def is_black_list(self, name: str):
        names = ["dodi", "DODI"]
        name = name.lower()
        for n in names:
            if n in name:
                return True
        return False

    async def search(self, query: str, size: int = 100) -> list[dict]:
        trackers = await read_lines("static/txt/trackers.txt")
        trackers = [f"tr={tr}" for tr in trackers if tr]
        trackers = "&".join(trackers)
        url = f"https://torrents-csv.com/service/search?q={query}&size={size}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()

                    torrents = []
                    for item in data.get('torrents', []):
                        info_hash = item['infohash']
                        name = item['name']
                        if self.is_black_list(name):
                            continue

                        size_bytes = item['size_bytes']
                        magnet = f"magnet:?xt=urn:btih:{info_hash}&dn={urllib.parse.quote(name)}&{trackers}"

                        torrents.append({
                            "name": name,
                            "magnet": magnet,
                            "size": size_bytes,
                            "seeders": item.get('seeders', 0)
                        })
                    return torrents
        return []
