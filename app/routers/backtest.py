from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.services.ranking_service import get_rankings
from app.core.config import now_tw

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/backtest")
def backtest(request: Request):
    data = get_rankings()
    return templates.TemplateResponse("backtest.html", {
        "request": request,
        "rows": data.get("ranking", []),
        "now_tw": now_tw(),
    })
