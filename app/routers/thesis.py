from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.core.paths import TEMPLATES_DIR
from app.services.ranking_service import build_rankings
from app.core.config import now_tw

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@router.get("/thesis")
def thesis(request: Request):
    data = build_rankings()
    return templates.TemplateResponse("thesis.html", {"request": request, "rows": data["treasure"], "now_tw": now_tw()})
