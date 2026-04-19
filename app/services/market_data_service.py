from __future__ import annotations
from pathlib import Path
import json
import random
import time
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import requests

from app.core.config import (
    PRICE_HISTORY_DIR,
    YFINANCE_ENABLED,
    YFINANCE_START,
    YFINANCE_PERIOD,
    YFINANCE_FORCE_FULL_REFRESH,
    YFINANCE_MAX_RETRIES,
    YFINANCE_RETRY_SLEEP,
    YFINANCE_REQUEST_PAUSE,
    YFINANCE_INCREMENTAL_OVERLAP_DAYS,
)
from app.services.stock_universe_service import get_stock_meta

PRICE_DIR = Path(PRICE_HISTORY_DIR)
PRICE_DIR.mkdir(parents=True, exist_ok=True)
META_DIR = PRICE_DIR / "_meta"
META_DIR.mkdir(parents=True, exist_ok=True)
SESSION = requests.Session()


def _clean_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    rename = {}
    for c in df.columns:
        cl = str(c).lower()
        if cl in {"date", "open", "high", "low", "close", "volume"}:
            rename[c] = cl
    df = df.rename(columns=rename)
    if "date" not in df.columns:
        idx_name = df.index.name or "index"
        df = df.reset_index().rename(columns={idx_name: "date"})
        if "date" not in df.columns:
            df = df.rename(columns={df.columns[0]: "date"})
    cols = [c for c in ["date", "open", "high", "low", "close", "volume"] if c in df.columns]
    out = df[cols].copy()
    out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    for c in ["open", "high", "low", "close", "volume"]:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")
        else:
            out[c] = None
    out = out.dropna(subset=["date", "open", "high", "low", "close"]).drop_duplicates(subset=["date"]).sort_values("date")
    out["volume"] = out["volume"].fillna(0)
    return out[["date", "open", "high", "low", "close", "volume"]]


def _history_path(stock_id: str) -> Path:
    return PRICE_DIR / f"{stock_id}.csv"


def _meta_path(stock_id: str) -> Path:
    return META_DIR / f"{stock_id}.json"


def load_saved_history(stock_id: str) -> pd.DataFrame:
    path = _history_path(stock_id)
    if path.exists():
        try:
            return _clean_ohlcv(pd.read_csv(path))
        except Exception:
            return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])
    return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])


def _ticker_candidates(stock_id: str) -> list[str]:
    meta = get_stock_meta(stock_id)
    candidates = []
    primary = meta.get("yf_symbol")
    if primary:
        candidates.append(primary)
    for s in [f"{stock_id}.TW", f"{stock_id}.TWO"]:
        if s not in candidates:
            candidates.append(s)
    return candidates


def _is_rate_limit_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return "ratelimit" in text or "too many requests" in text or "rate limited" in text


def fetch_history_yfinance(stock_id: str, start: Optional[str] = None, period: Optional[str] = None) -> pd.DataFrame:
    if not YFINANCE_ENABLED:
        return pd.DataFrame()
    import yfinance as yf
    last_error = None
    for ticker in _ticker_candidates(stock_id):
        for attempt in range(1, YFINANCE_MAX_RETRIES + 1):
            try:
                kwargs = {"auto_adjust": False, "progress": False, "threads": False}
                if start:
                    kwargs["start"] = start
                else:
                    kwargs["period"] = period or YFINANCE_PERIOD
                df = yf.download(ticker, **kwargs)
                time.sleep(YFINANCE_REQUEST_PAUSE)
                out = _clean_ohlcv(df)
                if not out.empty:
                    return out
            except Exception as exc:
                last_error = exc
                sleep_s = YFINANCE_RETRY_SLEEP * attempt + random.uniform(0, 1.5)
                if _is_rate_limit_error(exc):
                    sleep_s += 5
                time.sleep(sleep_s)
    if last_error:
        raise last_error
    return pd.DataFrame()


def save_history(stock_id: str, df: pd.DataFrame, source: str = "yfinance") -> str:
    path = _history_path(stock_id)
    clean = _clean_ohlcv(df)
    clean.to_csv(path, index=False, encoding="utf-8-sig")
    payload = {
        "source": source,
        "rows": int(len(clean)),
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "latest_date": clean.iloc[-1]["date"] if not clean.empty else None,
    }
    _meta_path(stock_id).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)


def _merge_history(old_df: pd.DataFrame, new_df: pd.DataFrame) -> pd.DataFrame:
    if old_df is None or old_df.empty:
        return _clean_ohlcv(new_df)
    if new_df is None or new_df.empty:
        return _clean_ohlcv(old_df)
    merged = pd.concat([_clean_ohlcv(old_df), _clean_ohlcv(new_df)], ignore_index=True)
    merged = merged.drop_duplicates(subset=["date"], keep="last").sort_values("date").reset_index(drop=True)
    return merged


def update_symbol_history(stock_id: str, start: Optional[str] = None, force_full: bool = False) -> dict:
    existing = load_saved_history(stock_id)
    effective_force_full = force_full or YFINANCE_FORCE_FULL_REFRESH or existing.empty
    fetch_start = start or YFINANCE_START
    fetch_period = None
    if not effective_force_full and not existing.empty:
        try:
            last_date = pd.to_datetime(existing["date"].iloc[-1])
            fetch_start = (last_date - timedelta(days=YFINANCE_INCREMENTAL_OVERLAP_DAYS)).strftime("%Y-%m-%d")
        except Exception:
            fetch_start = None
            fetch_period = YFINANCE_PERIOD
    try:
        fresh = fetch_history_yfinance(stock_id, start=fetch_start, period=fetch_period)
    except Exception as exc:
        if not existing.empty:
            return {
                "stock_id": stock_id,
                "rows": len(existing),
                "saved_to": str(_history_path(stock_id)),
                "latest_date": existing.iloc[-1].get("date"),
                "latest_close": float(existing.iloc[-1].get("close", 0) or 0),
                "used_cache": True,
                "warning": str(exc),
            }
        raise ValueError(f"抓不到 {stock_id} 歷史K線: {exc}")
    if fresh.empty and not existing.empty:
        return {
            "stock_id": stock_id,
            "rows": len(existing),
            "saved_to": str(_history_path(stock_id)),
            "latest_date": existing.iloc[-1].get("date"),
            "latest_close": float(existing.iloc[-1].get("close", 0) or 0),
            "used_cache": True,
            "warning": "最新抓取為空，保留既有資料",
        }
    merged = _merge_history(existing, fresh)
    if merged.empty:
        raise ValueError(f"抓不到 {stock_id} 歷史K線")
    path = save_history(stock_id, merged, source="yfinance")
    latest = merged.iloc[-1].to_dict()
    return {
        "stock_id": stock_id,
        "rows": len(merged),
        "saved_to": path,
        "latest_date": latest.get("date"),
        "latest_close": float(latest.get("close", 0) or 0),
        "fetched_rows": int(len(fresh)),
        "used_cache": False,
    }
