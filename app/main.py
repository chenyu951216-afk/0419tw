from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import dashboard, ranking, treasure, import_tool, backtest, thesis
from app.core.config import (
    V13_AUTO_SCAN_IMPORT_DIR,
    V13_AUTO_SCAN_FINANCIAL_DIR,
    AUTO_UPDATE_ON_STARTUP,
    AUTO_UPDATE_INITIAL_LIMIT,
    AUTO_UPDATE_RUN_IN_BACKGROUND,
)
from app.services.history_import_service import auto_scan_default_import_folder
from app.services.financial_import_service import auto_scan_default_financial_folder
from app.services.auto_update_service import start_background_refresh, run_full_refresh, start_scheduler_if_needed

app = FastAPI(title="TW Stock Bot v16 穩定版")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(dashboard.router)
app.include_router(ranking.router)
app.include_router(treasure.router)
app.include_router(import_tool.router)
app.include_router(backtest.router)
app.include_router(thesis.router)

@app.on_event("startup")
def startup_scan_import_folder():
    if V13_AUTO_SCAN_IMPORT_DIR:
        try:
            auto_scan_default_import_folder()
        except Exception:
            pass
    if V13_AUTO_SCAN_FINANCIAL_DIR:
        try:
            auto_scan_default_financial_folder()
        except Exception:
            pass
    start_scheduler_if_needed()
    if AUTO_UPDATE_ON_STARTUP:
        try:
            if AUTO_UPDATE_RUN_IN_BACKGROUND:
                start_background_refresh(limit=AUTO_UPDATE_INITIAL_LIMIT)
            else:
                run_full_refresh(limit=AUTO_UPDATE_INITIAL_LIMIT)
        except Exception:
            pass
