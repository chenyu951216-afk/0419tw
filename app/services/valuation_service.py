from __future__ import annotations
from math import isfinite

def _safe_float(v, default=0.0):
    try:
        x = float(v)
        return x if isfinite(x) else default
    except Exception:
        return default

def cagr(start: float, end: float, periods: int) -> float:
    start = _safe_float(start)
    end = _safe_float(end)
    if start <= 0 or end <= 0 or periods <= 0:
        return 0.0
    return (end / start) ** (1 / periods) - 1

def estimate_shares_outstanding_m(current_price: float, fundamentals: dict, records: list[dict]) -> float:
    current_price = max(_safe_float(current_price, 1), 1)
    latest = sorted(records or [], key=lambda x: x.get("year", 0))[-1] if records else {}
    eps = max(_safe_float(fundamentals.get("eps", latest.get("eps", 0)), 0.5), 0.5)
    pe = max(_safe_float(fundamentals.get("pe", 12), 12), 1)
    revenue = max(_safe_float(latest.get("revenue", 0), 100), 100)
    net_income = max(current_price / pe * eps * 10, revenue * 0.06)
    shares = max(net_income / eps, 10)
    return round(shares, 2)

def dcf_valuation(current_price: float, records: list[dict], discount_rate: float = 0.10, terminal_growth: float = 0.025, projection_years: int = 5) -> dict:
    current_price = _safe_float(current_price)
    years = sorted(records or [], key=lambda x: x.get("year", 0))
    if not years:
        return {"dcf_value_per_share": 0.0, "dcf_margin_of_safety": 0.0, "dcf_total_value": 0.0, "shares_outstanding_m": 0.0, "dcf_assumptions": {"discount_rate": 10.0, "terminal_growth": 2.5, "growth_rate": 0.0}}
    latest = years[-1]
    shares_outstanding_m = max(_safe_float(latest.get("shares_outstanding_m", 0), 0), 0)
    if shares_outstanding_m <= 0:
        shares_outstanding_m = estimate_shares_outstanding_m(current_price, {}, years)
    fcf_series = [max(_safe_float(r.get("free_cf", 0.0), 0.01), 0.01) for r in years[-5:]]
    growth = cagr(fcf_series[0], fcf_series[-1], max(len(fcf_series)-1, 1))
    growth = max(-0.05, min(growth, 0.18))
    if growth >= discount_rate:
        growth = discount_rate - 0.02
    projected = []
    cash = fcf_series[-1]
    for _ in range(projection_years):
        cash *= (1 + growth)
        projected.append(cash)
    pv_sum = sum(cf / ((1 + discount_rate) ** i) for i, cf in enumerate(projected, start=1))
    terminal_cf = projected[-1] * (1 + terminal_growth)
    terminal_value = terminal_cf / max(discount_rate - terminal_growth, 0.01)
    pv_terminal = terminal_value / ((1 + discount_rate) ** projection_years)
    total_value = pv_sum + pv_terminal
    per_share = total_value / shares_outstanding_m
    mos = ((per_share - current_price) / current_price * 100) if current_price > 0 else 0.0
    return {"dcf_value_per_share": round(per_share, 2), "dcf_margin_of_safety": round(mos, 2), "dcf_total_value": round(total_value, 2), "shares_outstanding_m": round(shares_outstanding_m, 2), "dcf_assumptions": {"discount_rate": round(discount_rate*100,2), "terminal_growth": round(terminal_growth*100,2), "growth_rate": round(growth*100,2)}}

def ev_ebitda_valuation(current_price: float, fundamentals: dict, records: list[dict]) -> dict:
    years = sorted(records or [], key=lambda x: x.get("year", 0))
    if not years:
        return {"ev": 0.0, "ebitda": 0.0, "ev_ebitda": 0.0, "ev_ebitda_label": "資料不足", "net_debt_proxy": 0.0}
    latest = years[-1]
    revenue = _safe_float(latest.get("revenue", 0), 0)
    operating_cf = _safe_float(latest.get("operating_cf", 0), 0)
    capex = abs(_safe_float(latest.get("capex", 0), 0))
    ebitda = max(operating_cf + capex, revenue * 0.06)
    shares = max(_safe_float(latest.get("shares_outstanding_m", 0), 0), 0)
    if shares <= 0:
        shares = estimate_shares_outstanding_m(current_price, fundamentals, years)
    market_cap = current_price * shares
    pb = _safe_float(fundamentals.get("pb", 1.5), 1.5)
    roe = _safe_float(fundamentals.get("roe", 10), 10)
    net_debt = max(0, revenue * max(0.03, min(0.15, 0.08 + (1.8 - pb) * 0.02 + (12 - roe) * 0.001)))
    ev = market_cap + net_debt
    multiple = ev / ebitda if ebitda > 0 else 0.0
    label = "低估" if 0 < multiple < 8 else "合理" if multiple <= 15 else "偏貴"
    return {"ev": round(ev, 2), "ebitda": round(ebitda, 2), "ev_ebitda": round(multiple, 2), "ev_ebitda_label": label, "net_debt_proxy": round(net_debt, 2)}

def valuation_score(dcf_result: dict, ev_result: dict) -> dict:
    mos = _safe_float(dcf_result.get("dcf_margin_of_safety", 0), 0)
    ev_mult = _safe_float(ev_result.get("ev_ebitda", 0), 0)
    score = 0.0
    if mos >= 30: score += 20
    elif mos >= 15: score += 14
    elif mos >= 0: score += 8
    elif mos >= -15: score += 3
    if 0 < ev_mult < 8: score += 10
    elif ev_mult <= 12: score += 7
    elif ev_mult <= 16: score += 4
    return {"valuation_score": round(score, 2), "valuation_label": "低估" if score >= 22 else "觀察" if score >= 12 else "普通"}
