from __future__ import annotations
from statistics import mean, pstdev

def _safe(v, default=0.0):
    try: return float(v)
    except Exception: return default

def analyze_dividend(records: list[dict]) -> dict:
    years = sorted(records or [], key=lambda x: x.get("year", 0))
    if not years:
        return {"dividend_years": 0, "dividend_streak": 0, "dividend_growth_rate": 0.0, "dividend_stability_score": 0.0, "dividend_cover_ratio": 0.0, "dividend_label": "資料不足"}
    dividends = [_safe(r.get("dividend", 0)) for r in years]
    paid = [d for d in dividends if d > 0]
    years_paid = len(paid)
    streak = cur = 0
    for d in dividends:
        if d > 0:
            cur += 1
            streak = max(streak, cur)
        else:
            cur = 0
    growth = ((paid[-1]/paid[0]) ** (1/max(len(paid)-1,1)) - 1)*100 if len(paid)>=2 and paid[0] > 0 else 0.0
    avg_paid = mean(paid) if paid else 0.0
    volatility = pstdev(paid) if len(paid) >= 2 else 0.0
    stability = max(0.0, 100 - (volatility / avg_paid * 100)) if avg_paid else 0.0
    cover_ratios = []
    for r in years:
        shares = _safe(r.get("shares_outstanding_m", 0), 0)
        d = _safe(r.get("dividend", 0), 0)
        fcf = _safe(r.get("free_cf", 0), 0)
        total_div = shares * d if shares > 0 else 0.0
        if total_div > 0:
            cover_ratios.append(fcf / total_div)
    cover = mean(cover_ratios) if cover_ratios else 0.0
    label = "高"
    if years_paid < 3 or stability < 50 or cover < 0.8: label = "中"
    if years_paid < 2 or cover < 0.5: label = "低"
    return {"dividend_years": years_paid, "dividend_streak": streak, "dividend_growth_rate": round(growth,2), "dividend_stability_score": round(stability,2), "dividend_cover_ratio": round(cover,2), "dividend_label": label}

def dividend_score(dividend_info: dict) -> dict:
    years = float(dividend_info.get("dividend_years", 0))
    growth = float(dividend_info.get("dividend_growth_rate", 0))
    stability = float(dividend_info.get("dividend_stability_score", 0))
    cover = float(dividend_info.get("dividend_cover_ratio", 0))
    score = min(years * 1.8, 8)
    if growth > 0: score += min(growth / 2, 6)
    score += min(stability / 10, 8)
    if cover >= 1.2: score += 8
    elif cover >= 0.8: score += 5
    elif cover >= 0.5: score += 2
    return {"dividend_score": round(score, 2)}
