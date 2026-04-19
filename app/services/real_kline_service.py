from pathlib import Path
import pandas as pd
from app.core.config import PRICE_HISTORY_DIR, V13_IMPORTED_DIR, USE_SAMPLE_DATA, RANKING_MIN_HISTORY_DAYS, ALLOW_LIVE_FETCH_ON_READ
from app.services.market_data_service import update_symbol_history
from app.services.sample_data_service import sample_history

BASE = Path(PRICE_HISTORY_DIR)
IMPORTED = Path(V13_IMPORTED_DIR)


def list_available_symbols():
    symbols = set()
    for root in [BASE, IMPORTED]:
        if root.exists():
            for p in root.glob("*.csv"):
                symbols.add(p.stem)
    return sorted(symbols)


def _normalize_loaded(df: pd.DataFrame) -> pd.DataFrame:
    cols = {c.lower(): c for c in df.columns}
    mapping = {}
    for k in ["date", "open", "high", "low", "close", "volume"]:
        if k in cols:
            mapping[cols[k]] = k
    df = df.rename(columns=mapping)
    needed = ["date", "open", "high", "low", "close", "volume"]
    for c in needed:
        if c not in df.columns:
            raise ValueError(f"缺少K線欄位 {c}")
    out = df[needed].copy()
    out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    for c in ["open", "high", "low", "close", "volume"]:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    out = out.dropna(subset=["date", "open", "high", "low", "close"]).drop_duplicates(subset=["date"]).sort_values("date")
    out["volume"] = out["volume"].fillna(0)
    return out.reset_index(drop=True)


def _load_from_path(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])
    return _normalize_loaded(pd.read_csv(path))


def load_history(stock_id: str, min_rows: int = RANKING_MIN_HISTORY_DAYS) -> pd.DataFrame:
    for folder in [IMPORTED, BASE]:
        path = folder / f"{stock_id}.csv"
        if path.exists():
            df = _load_from_path(path)
            if len(df) >= min_rows:
                return df.tail(len(df))
            if not df.empty:
                return df
    if ALLOW_LIVE_FETCH_ON_READ:
        try:
            update_symbol_history(stock_id)
            path = BASE / f"{stock_id}.csv"
            if path.exists():
                return _load_from_path(path)
        except Exception:
            pass
    if USE_SAMPLE_DATA:
        return sample_history(stock_id, max(min_rows, 220))
    return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])
