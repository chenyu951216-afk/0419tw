from pathlib import Path
import shutil
import pandas as pd
from app.core.config import V13_BATCH_IMPORT_DIR, V13_IMPORTED_DIR, V13_AUTO_SCAN_EXTENSIONS

TARGET = Path(V13_IMPORTED_DIR)
TARGET.mkdir(parents=True, exist_ok=True)
BATCH = Path(V13_BATCH_IMPORT_DIR)
BATCH.mkdir(parents=True, exist_ok=True)

EXPECTED = ["date","open","high","low","close","volume"]
ALIASES = {
    "date": ["date","日期"],
    "open": ["open","開盤"],
    "high": ["high","最高"],
    "low": ["low","最低"],
    "close": ["close","收盤"],
    "volume": ["volume","成交量"],
}

def _normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    cols = {c.lower(): c for c in df.columns}
    rename = {}
    for target, names in ALIASES.items():
        for n in names:
            if n.lower() in cols:
                rename[cols[n.lower()]] = target
                break
    df = df.rename(columns=rename)
    missing = [c for c in EXPECTED if c not in df.columns]
    if missing:
        raise ValueError(f"缺少欄位: {missing}")
    out = df[EXPECTED].copy()
    out["date"] = out["date"].astype(str)
    return out

def _symbol_from_path(path: Path) -> str:
    return path.stem.split("_")[0].strip()


def normalize_and_save(filepath: str, symbol: str):
    df = pd.read_csv(filepath)
    out = _normalize_df(df)
    saved = TARGET / f"{symbol}.csv"
    out.to_csv(saved, index=False, encoding="utf-8-sig")
    return {"symbol": symbol, "rows": len(out), "saved_to": str(saved)}


def batch_import_folder(folderpath: str | None = None):
    folder = Path(folderpath) if folderpath else BATCH
    folder.mkdir(parents=True, exist_ok=True)
    results = []
    imported_count = 0
    for p in sorted(folder.iterdir()):
        if not p.is_file() or p.suffix.lower() not in V13_AUTO_SCAN_EXTENSIONS:
            continue
        symbol = _symbol_from_path(p)
        try:
            res = normalize_and_save(str(p), symbol)
            imported_count += 1
            results.append({**res, "status": "ok"})
        except Exception as e:
            results.append({"symbol": symbol, "file": str(p), "status": "error", "error": str(e)})
    return {"folder": str(folder), "imported_count": imported_count, "results": results}


def auto_scan_default_import_folder():
    return batch_import_folder(str(BATCH))


def imported_symbols():
    return sorted(p.stem for p in TARGET.glob("*.csv"))


def move_uploaded_sample_to_batch(filepath: str):
    src = Path(filepath)
    dst = BATCH / src.name
    shutil.copy(src, dst)
    return str(dst)
