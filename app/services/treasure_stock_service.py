from app.core.config import (
    TREASURE_MAX_PE, TREASURE_MAX_PB, TREASURE_MIN_ROE, TREASURE_MIN_GROSS_MARGIN,
    TREASURE_MIN_3Y_REVENUE_CAGR, TREASURE_MIN_REV_Q_UP, TREASURE_MIN_GM_Q_UP,
    TREASURE_MIN_ROE_Q_UP, TREASURE_MIN_FCF_MARGIN, TREASURE_MIN_DIVIDEND_YEARS,
    TREASURE_MIN_OCF_STABLE_YEARS, TREASURE_MIN_FCF_POSITIVE_YEARS,
)
from app.services.thesis_service import build_long_term_thesis

def _up_count(series):
    cnt = 0
    for a, b in zip(series[:-1], series[1:]):
        if b >= a:
            cnt += 1
    return cnt

def compute_quarterly_trend(q: dict) -> dict:
    rev = q.get("revenue_yoy", [])
    gm = q.get("gross_margin", [])
    roe = q.get("roe", [])
    eps = q.get("eps", [])
    rev_up = _up_count(rev) if len(rev) >= 2 else 0
    gm_up = _up_count(gm) if len(gm) >= 2 else 0
    roe_up = _up_count(roe) if len(roe) >= 2 else 0
    eps_up = _up_count(eps) if len(eps) >= 2 else 0
    score = rev_up * 8 + gm_up * 6 + roe_up * 6 + eps_up * 5
    positive = rev_up >= TREASURE_MIN_REV_Q_UP and gm_up >= TREASURE_MIN_GM_Q_UP and roe_up >= TREASURE_MIN_ROE_Q_UP
    tags = []
    if rev_up: tags.append(f"營收YOY連升 {rev_up} 季")
    if gm_up: tags.append(f"毛利率連升 {gm_up} 季")
    if roe_up: tags.append(f"ROE連升 {roe_up} 季")
    if eps_up: tags.append(f"EPS連升 {eps_up} 季")
    return {"quarterly_trend_score": score, "quarterly_positive": positive, "quarterly_rev_up": rev_up, "quarterly_gm_up": gm_up, "quarterly_roe_up": roe_up, "quarterly_eps_up": eps_up, "quarterly_tags": tags[:4]}

def compute_financial_quality(fin_hist: list[dict] | None) -> dict:
    if not fin_hist:
        return {'financial_trend_score': 0, 'financial_reasons': [], 'fcf_positive_years': 0, 'dividend_years': 0, 'ocf_positive_years': 0, 'avg_fcf_margin': 0, 'revenue_years_up': 0, 'eps_years_up': 0, 'gm_years_up': 0, 'roe_years_up': 0}
    years = sorted(fin_hist, key=lambda x: x.get('year', 0))
    revenue = [x.get('revenue', 0) for x in years]
    gm = [x.get('gross_margin', 0) for x in years]
    roe = [x.get('roe', 0) for x in years]
    eps = [x.get('eps', 0) for x in years]
    ocf = [x.get('operating_cf', 0) for x in years]
    fcf = [x.get('free_cf', 0) for x in years]
    div = [x.get('dividend', 0) for x in years]
    fcf_margin = [((y.get('free_cf',0) or 0)/(y.get('revenue',0) or 1)*100) if y.get('revenue',0) else 0 for y in years]
    revenue_up = _up_count(revenue)
    eps_up = _up_count(eps)
    gm_up = _up_count(gm)
    roe_up = _up_count(roe)
    fcf_positive_years = sum(1 for x in fcf if x > 0)
    dividend_years = sum(1 for x in div if x > 0)
    ocf_positive_years = sum(1 for x in ocf if x > 0)
    avg_fcf_margin = round(sum(fcf_margin) / len(fcf_margin), 2) if fcf_margin else 0
    score = revenue_up * 6 + eps_up * 6 + gm_up * 4 + roe_up * 4
    if fcf_positive_years >= TREASURE_MIN_FCF_POSITIVE_YEARS: score += 12
    if dividend_years >= TREASURE_MIN_DIVIDEND_YEARS: score += 10
    if ocf_positive_years >= TREASURE_MIN_OCF_STABLE_YEARS: score += 10
    if avg_fcf_margin >= TREASURE_MIN_FCF_MARGIN: score += 12
    reasons = []
    if revenue_up: reasons.append(f"年度營收連升 {revenue_up} 次")
    if eps_up: reasons.append(f"年度EPS連升 {eps_up} 次")
    if gm_up: reasons.append(f"年度毛利率連升 {gm_up} 次")
    if roe_up: reasons.append(f"年度ROE連升 {roe_up} 次")
    if fcf_positive_years >= TREASURE_MIN_FCF_POSITIVE_YEARS: reasons.append(f"自由現金流正值 {fcf_positive_years} 年")
    if dividend_years >= TREASURE_MIN_DIVIDEND_YEARS: reasons.append(f"連續配息 {dividend_years} 年")
    if ocf_positive_years >= TREASURE_MIN_OCF_STABLE_YEARS: reasons.append(f"營業現金流正值 {ocf_positive_years} 年")
    if avg_fcf_margin >= TREASURE_MIN_FCF_MARGIN: reasons.append(f"平均FCF率 {avg_fcf_margin}%")
    return {'financial_trend_score': score, 'financial_reasons': reasons[:8], 'fcf_positive_years': fcf_positive_years, 'dividend_years': dividend_years, 'ocf_positive_years': ocf_positive_years, 'avg_fcf_margin': avg_fcf_margin, 'revenue_years_up': revenue_up, 'eps_years_up': eps_up, 'gm_years_up': gm_up, 'roe_years_up': roe_up}

def score_treasure(stock: dict, fundamentals: dict, tech: dict, bt: dict, quarterly: dict, fin_hist: list[dict] | None = None) -> dict:
    pe = fundamentals.get("pe") if fundamentals.get("pe") is not None else 99
    pb = fundamentals.get("pb") if fundamentals.get("pb") is not None else 99
    roe = fundamentals.get("roe") or 0
    gm = fundamentals.get("gross_margin") or 0
    cagr = fundamentals.get("revenue_cagr_3y") or 0
    qtrend = compute_quarterly_trend(quarterly)
    ftrend = compute_financial_quality(fin_hist)
    thesis = build_long_term_thesis(stock, fundamentals, tech, qtrend, ftrend, fin_hist or [])
    value_score = thesis.get("valuation_score", 0)
    quality_score = 0
    if roe >= TREASURE_MIN_ROE: quality_score += 10
    if gm >= TREASURE_MIN_GROSS_MARGIN: quality_score += 8
    if cagr >= TREASURE_MIN_3Y_REVENUE_CAGR: quality_score += 8
    if tech.get("max_dd_120", 0) > -25: quality_score += 6
    if bt.get("formal_winrate", 0) >= 45: quality_score += 4
    quality_score += min(qtrend["quarterly_trend_score"], 18)
    quality_score += min(ftrend["financial_trend_score"], 22)
    quality_score += min(thesis.get("dividend_score", 0), 12)
    treasure_score = round(value_score * 1.2 + quality_score, 2)
    reasons = []
    if pe <= TREASURE_MAX_PE: reasons.append(f"本益比 {pe} 偏低")
    if pb <= TREASURE_MAX_PB: reasons.append(f"股價淨值比 {pb} 偏低")
    reasons.extend(qtrend["quarterly_tags"])
    reasons.extend(ftrend["financial_reasons"])
    reasons.extend(thesis.get("thesis_bullets", []))
    return {**qtrend, **ftrend, **thesis, "treasure_score": treasure_score, "is_treasure_candidate": treasure_score >= 82, "treasure_reasons": reasons[:12], "long_term_note": "偏長期低估/品質型觀察；已納入 DCF、EV/EBITDA、股利穩定度、多季財報趨勢與多年現金流。"}
