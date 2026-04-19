from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.core.paths import TEMPLATES_DIR
from app.services.ranking_service import get_rankings
from app.services.openai_service import ai_summary_for_top5
from app.services.auto_update_service import load_update_status
from app.core.config import now_tw

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@router.get("/")
def dashboard(request: Request):
    data = get_rankings()
    ai = ai_summary_for_top5(data.get("top5", []))
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "now_tw": now_tw(),
        "top5": data.get("top5", []),
        "treasure": data.get("treasure", []),
        "ai": ai,
        "update_status": load_update_status(),
    })
