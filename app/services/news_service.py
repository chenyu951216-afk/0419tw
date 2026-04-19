from __future__ import annotations
from pathlib import Path
import json
import urllib.parse
import requests
import xml.etree.ElementTree as ET

from app.core.config import NEWS_DIR, NEWS_ENABLED, AUTO_UPDATE_MAX_NEWS_PER_SYMBOL
from app.services.stock_universe_service import get_stock_meta

BASE = Path(NEWS_DIR)
BASE.mkdir(parents=True, exist_ok=True)
SESSION = requests.Session()


def fetch_symbol_news(stock_id: str, max_items: int = AUTO_UPDATE_MAX_NEWS_PER_SYMBOL) -> dict:
    if not NEWS_ENABLED:
        return {"stock_id": stock_id, "items": []}
    meta = get_stock_meta(stock_id)
    query = urllib.parse.quote(f"{stock_id} {meta.get('name', '')} 台股")
    url = f"https://news.google.com/rss/search?q={query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    r = SESSION.get(url, timeout=20)
    r.raise_for_status()
    root = ET.fromstring(r.text)
    items = []
    for item in root.findall("./channel/item")[:max_items]:
        items.append({
            "title": item.findtext("title"),
            "link": item.findtext("link"),
            "pubDate": item.findtext("pubDate"),
            "source": item.findtext("source"),
        })
    path = BASE / f"{stock_id}.json"
    path.write_text(json.dumps({"stock_id": stock_id, "items": items}, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"stock_id": stock_id, "items": items}


def load_symbol_news(stock_id: str) -> list[dict]:
    path = BASE / f"{stock_id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8")).get("items", [])
    return []
