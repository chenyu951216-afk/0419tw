from __future__ import annotations
from pathlib import Path
import json
import re
from typing import Iterable
import pandas as pd
import requests

from app.core.config import UNIVERSE_DIR
from app.services.sample_data_service import stock_master as sample_stock_master

UNIVERSE_PATH = Path(UNIVERSE_DIR)
UNIVERSE_PATH.mkdir(parents=True, exist_ok=True)
UNIVERSE_FILE = UNIVERSE_PATH / "tw_stock_universe.csv"
META_FILE = UNIVERSE_PATH / "tw_stock_universe_meta.json"

TWSE_URL = "https://openapi.twse.com.tw/v1/opendata/t187ap03_L"
TPEX_URL = "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap03_O"
SESSION = requests.Session()


def _request_json(url: str):
    r = SESSION.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


def _normalize_rows(rows: Iterable[dict], market: str) -> list[dict]:
    out = []
    for row in rows:
        symbol = str(row.get("公司代號") or row.get("SecuritiesCompanyCode") or "").strip()
        name = str(row.get("公司簡稱") or row.get("CompanyName") or row.get("公司名稱") or "").strip()
        industry = str(row.get("產業別") or row.get("Industry") or "其他").strip() or "其他"
        if not re.fullmatch(r"\d{4}", symbol):
            continue
        out.append({
            "stock_id": symbol,
            "name": name or symbol,
            "industry": industry,
            "market": market,
            "yf_symbol": f"{symbol}.TW" if market == "TWSE" else f"{symbol}.TWO",
        })
    return out


def fetch_stock_universe(force: bool = False) -> pd.DataFrame:
    if UNIVERSE_FILE.exists() and not force:
        return pd.read_csv(UNIVERSE_FILE)

    rows = []
    try:
        rows.extend(_normalize_rows(_request_json(TWSE_URL), "TWSE"))
    except Exception:
        pass
    try:
        rows.extend(_normalize_rows(_request_json(TPEX_URL), "TPEX"))
    except Exception:
        pass

    if not rows:
        rows = []
        for row in sample_stock_master():
            rows.append({**row, "market": "TWSE", "yf_symbol": f"{row['stock_id']}.TW"})

    df = pd.DataFrame(rows).drop_duplicates(subset=["stock_id"]).sort_values("stock_id")
    df.to_csv(UNIVERSE_FILE, index=False, encoding="utf-8-sig")
    META_FILE.write_text(json.dumps({"rows": len(df)}, ensure_ascii=False, indent=2), encoding="utf-8")
    return df


def load_stock_universe() -> pd.DataFrame:
    if UNIVERSE_FILE.exists():
        return pd.read_csv(UNIVERSE_FILE)
    return fetch_stock_universe(force=True)


def get_stock_meta(stock_id: str) -> dict:
    df = load_stock_universe()
    row = df[df["stock_id"].astype(str) == str(stock_id)]
    if row.empty:
        return {"stock_id": str(stock_id), "name": str(stock_id), "industry": "未知", "market": "未知", "yf_symbol": f"{stock_id}.TW"}
    return row.iloc[0].to_dict()
