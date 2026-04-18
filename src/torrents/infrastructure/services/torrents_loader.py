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
    TRACKERS = """
udp://tracker.opentrackr.org:1337/announce
udp://open.stealth.si:80/announce
udp://utracker.ghostchu-services.top:6969/announce
udp://tracker.wepzone.net:6969/announce
udp://tracker.torrent.eu.org:451/announce
udp://tracker.theoks.net:6969/announce
udp://tracker.srv00.com:6969/announce
udp://tracker.qu.ax:6969/announce
udp://tracker.darkness.services:6969/announce
udp://tracker.bittor.pw:1337/announce
udp://tracker.004430.xyz:1337/announce
udp://tracker-udp.gbitt.info:80/announce
udp://t.overflow.biz:6969/announce
udp://leet-tracker.moe:1337/announce
udp://explodie.org:6969/announce
udp://bittorrent-tracker.e-n-c-r-y-p-t.net:1337/announce
udp://bandito.byterunner.io:6969/announce
udp://wepzone.net:6969/announce
udp://udp.tracker.projectk.org:23333/announce
udp://tracker.yume-hatsuyuki.moe:6969/announce
udp://tracker.tvunderground.org.ru:3218/announce
udp://tracker.tryhackx.org:6969/announce
udp://tracker.torrust-demo.com:6969/announce
udp://tracker.therarbg.to:6969/announce
udp://tracker.t-1.org:6969/announce
udp://tracker.plx.im:6969/announce
udp://tracker.playground.ru:6969/announce
udp://tracker.opentorrent.top:6969/announce
udp://tracker.ixuexi.click:6969/announce
udp://tracker.gmi.gd:6969/announce
udp://tracker.fnix.net:6969/announce
udp://tracker.flatuslifir.is:6969/announce
udp://tracker.filemail.com:6969/announce
udp://tracker.ducks.party:1984/announce
udp://tracker.dler.org:6969/announce
udp://tracker.ddunlimited.net:6969/announce
udp://tracker.corpscorp.online:80/announce
udp://tracker.bluefrog.pw:2710/announce
udp://tracker.1h.is:1337/announce
udp://tr4ck3r.duckdns.org:6969/announce
udp://torrentclub.online:54123/announce
udp://seedpeer.net:6969/announce
udp://rekcart.duckdns.org:15480/announce
udp://ns575949.ip-51-222-82.net:6969/announce
udp://martin-gebhardt.eu:25/announce
udp://ipv4announce.sktorrent.eu:6969/announce
udp://evan.im:6969/announce
udp://6ahddutb1ucc3cp.ru:6969/announce
"""

    async def search(self, query: str) -> list[dict]:
        url = f"https://torrents-csv.com/service/search?q={query}&size=30"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()

                    torrents = []
                    for item in data.get('torrents', []):
                        info_hash = item['infohash']
                        name = item['name']
                        size_bytes = item['size_bytes']

                        magnet = f"magnet:?xt=urn:btih:{info_hash}&dn={name}"
                        print(improved_clean_title(name))

                        torrents.append({
                            "name": name,
                            "magnet": magnet,
                            "size": size_bytes,
                            "seeders": item.get('seeders', 'N/A')
                        })
                    return torrents
        return []
