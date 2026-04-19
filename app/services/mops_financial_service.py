from __future__ import annotations
from pathlib import Path
import json
import re
from typing import Optional
import pandas as pd
import requests
from bs4 import BeautifulSoup

from app.core.config import FUNDAMENTALS_DIR, MOPS_ENABLED
from app.services.stock_universe_service import get_stock_meta

BASE = Path(FUNDAMENTALS_DIR)
BASE.mkdir(parents=True, exist_ok=True)
ANNUAL_DIR = BASE / "annual"
QUARTERLY_DIR = BASE / "quarterly"
LATEST_DIR = BASE / "latest"
META_DIR = BASE / "_meta"
for p in [ANNUAL_DIR, QUARTERLY_DIR, LATEST_DIR, META_DIR]:
    p.mkdir(parents=True, exist_ok=True)

SESSION = requests.Session()
USER_AGENT = {"User-Agent": "Mozilla/5.0"}

MOPS_ENDPOINTS = {
    "income": "https://mops.twse.com.tw/mops/web/ajax_t163sb04",
    "balance": "https://mops.twse.com.tw/mops/web/ajax_t163sb05",
    "cashflow": "https://mops.twse.com.tw/mops/web/ajax_t163sb20",
}


def _roc_year(year: int) -> int:
    return year - 1911


def _market_code(stock_id: str) -> str:
    meta = get_stock_meta(stock_id)
    return "sii" if meta.get("market") == "TWSE" else "otc"


def _extract_first_number(text: str) -> Optional[float]:
    if text is None:
        return None
    text = str(text).replace(",", "").strip()
    m = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(m.group()) if m else None


def _find_value(html_tables: list[pd.DataFrame], aliases: list[str]) -> Optional[float]:
    keys = [a.lower() for a in aliases]
    for table in html_tables:
        work = table.copy()
        work.columns = [str(c) for c in work.columns]
        for idx in range(len(work)):
            row_text = " ".join(str(x) for x in work.iloc[idx].tolist()).lower()
            if any(k in row_text for k in keys):
                numbers = [_extract_first_number(v) for v in work.iloc[idx].tolist()]
                numbers = [v for v in numbers if v is not None]
                if numbers:
                    return numbers[-1]
    return None


def _post_statement(stock_id: str, year: int, season: int, endpoint: str) -> list[pd.DataFrame]:
    if not MOPS_ENABLED:
        return []
    payload = {
        "encodeURIComponent": 1,
        "step": 1,
        "firstin": 1,
        "off": 1,
        "TYPEK": _market_code(stock_id),
        "year": str(_roc_year(year)),
        "season": str(season),
        "co_id": str(stock_id),
    }
    r = SESSION.post(endpoint, data=payload, headers=USER_AGENT, timeout=30)
    r.raise_for_status()
    html = r.text
    try:
        return pd.read_html(html)
    except Exception:
        soup = BeautifulSoup(html, "html.parser")
        if soup.find(string=re.compile("查無資料|does not exist|沒有資料", re.I)):
            return []
        return []


def fetch_quarterly_financials(stock_id: str, year: int, season: int) -> dict:
    income = _post_statement(stock_id, year, season, MOPS_ENDPOINTS["income"])
    balance = _post_statement(stock_id, year, season, MOPS_ENDPOINTS["balance"])
    cashflow = _post_statement(stock_id, year, season, MOPS_ENDPOINTS["cashflow"])
    if not income and not balance and not cashflow:
        raise ValueError(f"{stock_id} {year}Q{season} 無MOPS資料")

    revenue = _find_value(income, ["營業收入", "收入合計", "revenue", "net revenue"])
    gross_margin = _find_value(income, ["毛利率", "gross margin"])
    eps = _find_value(income, ["基本每股盈餘", "基本每股(盈餘)", "eps", "earnings per share"])
    assets = _find_value(balance, ["資產總額", "assets total", "total assets"])
    equity = _find_value(balance, ["權益總額", "權益總計", "total equity", "equity attributable"])
    operating_cf = _find_value(cashflow, ["營業活動之淨現金流入", "營業活動之淨現金流出", "operating activities", "net cash flows from operating activities"])
    capex = _find_value(cashflow, ["取得不動產、廠房及設備", "purchase of property", "capital expenditures"])

    roe = (eps / (equity / max((assets or equity or 1), 1)) if eps is not None and equity not in (None, 0) and assets not in (None, 0) else None)
    record = {
        "quarter": f"{year}Q{season}",
        "year": year,
        "season": season,
        "revenue": revenue,
        "gross_margin": gross_margin,
        "roe": roe,
        "eps": eps,
        "operating_cf": operating_cf,
        "capex": capex,
        "free_cf": (operating_cf - abs(capex)) if operating_cf is not None and capex is not None else None,
        "source": "MOPS_HTML",
    }
    return record


def save_quarterly_financials(stock_id: str, records: list[dict]) -> str:
    df = pd.DataFrame(records).drop_duplicates(subset=["quarter"]).sort_values(["year", "season"])
    path = QUARTERLY_DIR / f"{stock_id}_quarterly.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return str(path)


def save_annual_financials(stock_id: str, records: list[dict]) -> str:
    df = pd.DataFrame(records).drop_duplicates(subset=["year"]).sort_values("year")
    path = ANNUAL_DIR / f"{stock_id}_financial.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return str(path)


def save_latest_fundamentals(stock_id: str, latest: dict) -> str:
    path = LATEST_DIR / f"{stock_id}_latest.json"
    path.write_text(json.dumps(latest, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)


def fetch_financial_history_from_mops(stock_id: str, start_year: int = 2020, end_year: Optional[int] = None) -> dict:
    today_year = pd.Timestamp.today().year
    end_year = end_year or today_year
    q_records = []
    annual = []
    for year in range(start_year, end_year + 1):
        year_rows = []
        for season in [1, 2, 3, 4]:
            try:
                row = fetch_quarterly_financials(stock_id, year, season)
                q_records.append(row)
                year_rows.append(row)
            except Exception:
                continue
        if year_rows:
            revenue = sum(r.get("revenue") or 0 for r in year_rows)
            avg_gm = pd.Series([r.get("gross_margin") for r in year_rows], dtype="float64").dropna()
            avg_roe = pd.Series([r.get("roe") for r in year_rows], dtype="float64").dropna()
            annual.append({
                "year": year,
                "revenue": revenue if revenue else None,
                "gross_margin": float(avg_gm.mean()) if not avg_gm.empty else None,
                "roe": float(avg_roe.mean()) if not avg_roe.empty else None,
                "eps": sum((r.get("eps") or 0) for r in year_rows) or None,
                "operating_cf": sum((r.get("operating_cf") or 0) for r in year_rows) or None,
                "capex": sum(abs(r.get("capex") or 0) for r in year_rows) or None,
                "free_cf": sum((r.get("free_cf") or 0) for r in year_rows) or None,
                "dividend": None,
            })
    if not annual:
        raise ValueError(f"{stock_id} MOPS 財報抓取失敗")
    q_path = save_quarterly_financials(stock_id, q_records)
    a_path = save_annual_financials(stock_id, annual)
    latest_q = pd.DataFrame(q_records).sort_values(["year", "season"]).tail(4)
    latest = {
        "stock_id": stock_id,
        "revenue_yoy": latest_q["revenue"].fillna(0).pct_change().fillna(0).mul(100).round(2).tolist(),
        "gross_margin": latest_q["gross_margin"].fillna(0).round(2).tolist(),
        "roe": latest_q["roe"].fillna(0).round(2).tolist(),
        "eps": latest_q["eps"].fillna(0).round(2).tolist(),
    }
    latest_path = save_latest_fundamentals(stock_id, latest)
    (META_DIR / f"{stock_id}.json").write_text(json.dumps({"annual_rows": len(annual), "quarter_rows": len(q_records)}, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"stock_id": stock_id, "annual_rows": len(annual), "quarter_rows": len(q_records), "annual_path": a_path, "quarterly_path": q_path, "latest_path": latest_path}


def load_annual_financial_history(stock_id: str) -> Optional[pd.DataFrame]:
    path = ANNUAL_DIR / f"{stock_id}_financial.csv"
    if path.exists():
        return pd.read_csv(path)
    return None


def load_quarterly_fundamentals(stock_id: str) -> Optional[dict]:
    path = LATEST_DIR / f"{stock_id}_latest.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    q_path = QUARTERLY_DIR / f"{stock_id}_quarterly.csv"
    if not q_path.exists():
        return None
    df = pd.read_csv(q_path).sort_values(["year", "season"]).tail(4)
    return {
        "stock_id": stock_id,
        "revenue_yoy": df["revenue"].fillna(0).pct_change().fillna(0).mul(100).round(2).tolist(),
        "gross_margin": df["gross_margin"].fillna(0).round(2).tolist(),
        "roe": df["roe"].fillna(0).round(2).tolist(),
        "eps": df["eps"].fillna(0).round(2).tolist(),
    }
