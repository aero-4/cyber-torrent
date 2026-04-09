import asyncio
import re
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

    async def search(self, query: str, timeout: float = 10.0) -> list[TorrentCreate]:
        base_url = f"https://apibay.org/q.php?q={query}"

        async with aiohttp.ClientSession(timeout=ClientTimeout(timeout)) as session:
            response = await session.get(base_url)
            response.raise_for_status()

            results = await response.json()

            if not results or results[0].get('id') == '0':
                return []

            torrents = []
            for item in results:
                name = item.get('name')
                info_hash = item.get('info_hash')
                seeders = item.get('seeders')
                magnet = f"magnet:?xt=urn:btih:{info_hash}&dn={quote(name)}"

                torrents.append(
                    TorrentCreate(name=name,
                                  seeders=seeders,
                                  magnet=magnet,
                                  slug=slugify(name))
                )

        return torrents
