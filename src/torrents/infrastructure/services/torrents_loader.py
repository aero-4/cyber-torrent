import asyncio
import re
import unicodedata
import difflib
import logging

from scrapers.x1337 import Scraper1337, Params1337, Category1337, Order1337


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


async def sync_search_and_save(name: str, fuzzy_threshold: float = 0.88):
    scraper = Scraper1337()
    params = Params1337(
        name=name,
        category=Category1337.GAMES,
        order_column=Order1337.TIME,
        order_ascending=False
    )

    results = scraper.find_torrents(params, (1, 2, 3, 4, 5))

    matches = []

    for t in results:
        cleaned = improved_clean_title(t.name)
        if not cleaned:
            continue
        if cleaned.casefold() == game.title.casefold():
            matches.append((t, cleaned))
            continue
        if normalize_for_match(cleaned) == normalize_for_match(game.title):
            matches.append((t, cleaned))
            continue
        matched, ratio = fuzzy_match(cleaned, game.title, threshold=fuzzy_threshold)
        if matched:
            matches.append((t, cleaned))

    if not matches:
        logging.debug(f"No matches found for {game.title}")
        return

    for t, cleaned in matches:
        print(t, cleaned)
        try:
            print(scraper.get_torrent_info(t))
        except Exception:
            logging.exception(f"Failed to get torrent info for {t.name}")

        if getattr(t, 'seeders', 0) <= 0:
            logging.debug(f"Skipping {t.name} (no seeders)")
            continue

asyncio.run(sync_search_and_save("god of war"))