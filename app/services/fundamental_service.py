from __future__ import annotations
import math
import pandas as pd
from app.services.financial_import_service import load_financial_history, load_latest_quarterly
from app.services.real_kline_service import load_history


def _safe(v, default=0.0):
    try:
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return default
        return float(v)
    except Exception:
        return default


def build_latest_fundamentals(stock_id: str) -> dict:
    fin = load_financial_history(stock_id)
    hist = load_history(stock_id, 5)
    if fin is None or fin.empty or hist.empty:
        return {}
    fin = fin.sort_values("year").reset_index(drop=True)
    last = fin.iloc[-1].to_dict()
    prev = fin.iloc[max(len(fin)-4, 0):]
    close = _safe(hist.iloc[-1]["close"])
    eps = _safe(last.get("eps"))
    book_value_per_share = None
    if "shares_outstanding_m" in fin.columns:
        shares = _safe(last.get("shares_outstanding_m"), 0)
        if shares:
            book_value_per_share = (_safe(last.get("equity"), 0) * 1000000) / (shares * 1000000)
    pe = round(close / eps, 2) if close and eps > 0 else None
    pb = round(close / book_value_per_share, 2) if close and book_value_per_share else None
    revenue_series = pd.to_numeric(prev["revenue"], errors="coerce").dropna()
    cagr = 0.0
    if len(revenue_series) >= 2 and revenue_series.iloc[0] > 0:
        years = len(revenue_series)-1
        cagr = ((revenue_series.iloc[-1] / revenue_series.iloc[0]) ** (1/years) - 1) * 100
    return {
        "pe": pe,
        "pb": pb,
        "roe": round(_safe(last.get("roe")), 2) if last.get("roe") is not None else None,
        "gross_margin": round(_safe(last.get("gross_margin")), 2) if last.get("gross_margin") is not None else None,
        "revenue_cagr_3y": round(cagr, 2),
        "eps": eps,
        "latest_revenue": _safe(last.get("revenue")),
        "latest_free_cf": _safe(last.get("free_cf")),
    }


def build_quarterly_fundamentals(stock_id: str) -> dict:
    q = load_latest_quarterly(stock_id)
    return q or {"revenue_yoy": [], "gross_margin": [], "roe": [], "eps": []}
