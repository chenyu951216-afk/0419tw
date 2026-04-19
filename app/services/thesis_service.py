from __future__ import annotations
from app.services.dividend_service import analyze_dividend, dividend_score
from app.services.valuation_service import dcf_valuation, ev_ebitda_valuation, valuation_score

def _risk_flags(fundamentals: dict, dcf_result: dict, ev_result: dict, dividend_info: dict, tech: dict) -> list[str]:
    flags = []
    if dcf_result.get("dcf_margin_of_safety", 0) < 0: flags.append("DCF 顯示安全邊際不足")
    if ev_result.get("ev_ebitda", 0) > 15: flags.append("EV/EBITDA 偏高")
    if dividend_info.get("dividend_cover_ratio", 0) < 0.8: flags.append("股利覆蓋率偏弱")
    if fundamentals.get("gross_margin", 0) < 15: flags.append("毛利率偏低")
    if tech.get("max_dd_120", -100) < -35: flags.append("近 120 日回撤較大")
    return flags[:5]

def _build_text(stock: dict, fundamentals: dict, qtrend: dict, ftrend: dict, valuation: dict, dividend_info: dict) -> dict:
    positives = []
    if valuation["dcf"]["dcf_margin_of_safety"] >= 20: positives.append("內在價值明顯高於現價，安全邊際不錯")
    if valuation["ev"]["ev_ebitda"] and valuation["ev"]["ev_ebitda"] < 10: positives.append("EV/EBITDA 位於偏低區間")
    if fundamentals.get("roe", 0) >= 15: positives.append("ROE 具一定資本報酬品質")
    if ftrend.get("fcf_positive_years", 0) >= 3: positives.append("自由現金流已連續多年為正")
    if dividend_info.get("dividend_years", 0) >= 5: positives.append("具多年配息紀錄")
    if qtrend.get("quarterly_positive"): positives.append("多季財報趨勢仍在改善")
    risks = []
    if valuation["dcf"]["dcf_margin_of_safety"] < 10: risks.append("估值保護墊不算厚")
    if dividend_info.get("dividend_cover_ratio", 0) < 1.0: risks.append("股利對自由現金流覆蓋不算充裕")
    if fundamentals.get("pe", 99) > 20: risks.append("本益比不算低，重估空間可能受限")
    summary = "；".join(positives[:3]) if positives else "仍需更多財務與估值證據。"
    conclusion = "適合長期持有/觀察" if valuation["score"]["valuation_score"] >= 12 and dividend_info.get("dividend_label") != "低" else "先觀察"
    return {"thesis_summary": summary, "thesis_bullets": positives[:6], "thesis_risks": risks[:5], "thesis_conclusion": conclusion}

def build_long_term_thesis(stock: dict, fundamentals: dict, tech: dict, qtrend: dict, ftrend: dict, financial_history: list[dict], discount_rate: float = 0.10, terminal_growth: float = 0.025) -> dict:
    current_price = tech.get("last_close", 0)
    dcf = dcf_valuation(current_price, financial_history, discount_rate=discount_rate, terminal_growth=terminal_growth)
    ev = ev_ebitda_valuation(current_price, fundamentals, financial_history)
    val_score = valuation_score(dcf, ev)
    dividend_info = analyze_dividend(financial_history)
    div_score = dividend_score(dividend_info)
    risks = _risk_flags(fundamentals, dcf, ev, dividend_info, tech)
    text = _build_text(stock, fundamentals, qtrend, ftrend, {"dcf": dcf, "ev": ev, "score": val_score}, dividend_info)
    return {**dcf, **ev, **val_score, **dividend_info, **div_score, "risk_flags": risks, **text}
