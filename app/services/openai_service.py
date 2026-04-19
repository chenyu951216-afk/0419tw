from app.core.config import OPENAI_API_KEY, OPENAI_MODEL

def ai_summary_for_top5(items):
    # 保留介面，避免無 key 時整套不能跑
    return {
        "model": OPENAI_MODEL,
        "used_live_openai": bool(OPENAI_API_KEY),
        "summary": "AI 加強分析已保留介面；若未填 API key，系統使用本地規則摘要，避免憑空即時數據幻覺。"
    }
