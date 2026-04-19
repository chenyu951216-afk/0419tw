from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.services.ranking_service import get_rankings
from app.core.config import now_tw

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/treasure")
def treasure(request: Request):
    data = get_rankings()
    return templates.TemplateResponse("treasure.html", {
        "request": request,
        "rows": data.get("treasure", []),
        "now_tw": now_tw(),
    })
