from pathlib import Path
import json
import pandas as pd
from app.core.config import V13_FINANCIAL_IMPORT_DIR, V13_FINANCIAL_STORE_DIR, V13_FINANCIAL_EXTENSIONS
from app.services.mops_financial_service import load_annual_financial_history, load_quarterly_fundamentals

STORE = Path(V13_FINANCIAL_STORE_DIR)
STORE.mkdir(parents=True, exist_ok=True)
BATCH = Path(V13_FINANCIAL_IMPORT_DIR)
BATCH.mkdir(parents=True, exist_ok=True)
LATEST_DIR = STORE / "latest"
LATEST_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED = ["year","revenue","gross_margin","roe","eps","operating_cf","capex","free_cf","dividend"]
ALIASES = {
    "year": ["year","年度","fiscal_year"],
    "revenue": ["revenue","營收"],
    "gross_margin": ["gross_margin","毛利率"],
    "roe": ["roe"],
    "eps": ["eps"],
    "operating_cf": ["operating_cf","operating_cash_flow","營業現金流"],
    "capex": ["capex","資本支出"],
    "free_cf": ["free_cf","fcf","自由現金流"],
    "dividend": ["dividend","股利","cash_dividend"],
}


def _symbol_from_path(path: Path) -> str:
    return path.stem.split("_")[0].strip()


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
        raise ValueError(f"缺少財報欄位: {missing}")
    out = df[EXPECTED].copy()
    out = out.sort_values('year')
    return out


def normalize_and_save_financial(filepath: str, symbol: str):
    df = pd.read_csv(filepath)
    out = _normalize_df(df)
    saved = STORE / f"{symbol}_financial.csv"
    out.to_csv(saved, index=False, encoding='utf-8-sig')
    return {"symbol": symbol, "rows": len(out), "saved_to": str(saved)}


def batch_import_financial_folder(folderpath: str | None = None):
    folder = Path(folderpath) if folderpath else BATCH
    folder.mkdir(parents=True, exist_ok=True)
    results = []
    imported_count = 0
    for p in sorted(folder.iterdir()):
        if not p.is_file() or p.suffix.lower() not in V13_FINANCIAL_EXTENSIONS:
            continue
        symbol = _symbol_from_path(p)
        try:
            res = normalize_and_save_financial(str(p), symbol)
            imported_count += 1
            results.append({**res, 'status': 'ok'})
        except Exception as e:
            results.append({'symbol': symbol, 'file': str(p), 'status': 'error', 'error': str(e)})
    return {'folder': str(folder), 'imported_count': imported_count, 'results': results}


def auto_scan_default_financial_folder():
    return batch_import_financial_folder(str(BATCH))


def imported_financial_symbols():
    local = sorted(p.stem.replace('_financial','') for p in STORE.glob('*_financial.csv'))
    return sorted(set(local))


def load_financial_history(symbol: str):
    path = STORE / f"{symbol}_financial.csv"
    if path.exists():
        return pd.read_csv(path)
    return load_annual_financial_history(symbol)


def load_latest_quarterly(symbol: str) -> dict | None:
    path = LATEST_DIR / f"{symbol}_latest.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return load_quarterly_fundamentals(symbol)
