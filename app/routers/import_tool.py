from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from app.services.history_import_service import normalize_and_save, batch_import_folder, imported_symbols
from app.services.financial_import_service import (
    normalize_and_save_financial, batch_import_financial_folder, imported_financial_symbols,
)
from app.services.auto_update_service import start_background_refresh, load_update_status
from app.core.config import now_tw, V13_BATCH_IMPORT_DIR, V13_FINANCIAL_IMPORT_DIR

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/import-tool")
def import_tool_page(request: Request):
    return templates.TemplateResponse("import_tool.html", {
        "request": request,
        "result": None,
        "batch_result": None,
        "financial_result": None,
        "financial_batch_result": None,
        "refresh_result": load_update_status(),
        "symbols": imported_symbols(),
        "financial_symbols": imported_financial_symbols(),
        "batch_dir": V13_BATCH_IMPORT_DIR,
        "financial_batch_dir": V13_FINANCIAL_IMPORT_DIR,
        "now_tw": now_tw()
    })

@router.post("/import-tool")
def import_tool(request: Request, filepath: str = Form(...), symbol: str = Form(...)):
    try:
        result = normalize_and_save(filepath, symbol)
    except Exception as e:
        result = {"error": str(e)}
    return templates.TemplateResponse("import_tool.html", {
        "request": request,
        "result": result,
        "batch_result": None,
        "financial_result": None,
        "financial_batch_result": None,
        "refresh_result": load_update_status(),
        "symbols": imported_symbols(),
        "financial_symbols": imported_financial_symbols(),
        "batch_dir": V13_BATCH_IMPORT_DIR,
        "financial_batch_dir": V13_FINANCIAL_IMPORT_DIR,
        "now_tw": now_tw()
    })

@router.post("/import-tool/batch")
def import_tool_batch(request: Request, folderpath: str = Form("")):
    try:
        batch_result = batch_import_folder(folderpath or None)
    except Exception as e:
        batch_result = {"error": str(e)}
    return templates.TemplateResponse("import_tool.html", {
        "request": request,
        "result": None,
        "batch_result": batch_result,
        "financial_result": None,
        "financial_batch_result": None,
        "refresh_result": load_update_status(),
        "symbols": imported_symbols(),
        "financial_symbols": imported_financial_symbols(),
        "batch_dir": folderpath or V13_BATCH_IMPORT_DIR,
        "financial_batch_dir": V13_FINANCIAL_IMPORT_DIR,
        "now_tw": now_tw()
    })

@router.post('/import-tool/financial')
def import_financial(request: Request, financial_filepath: str = Form(...), financial_symbol: str = Form(...)):
    try:
        financial_result = normalize_and_save_financial(financial_filepath, financial_symbol)
    except Exception as e:
        financial_result = {'error': str(e)}
    return templates.TemplateResponse('import_tool.html', {
        'request': request,
        'result': None,
        'batch_result': None,
        'financial_result': financial_result,
        'financial_batch_result': None,
        'refresh_result': load_update_status(),
        'symbols': imported_symbols(),
        'financial_symbols': imported_financial_symbols(),
        'batch_dir': V13_BATCH_IMPORT_DIR,
        'financial_batch_dir': V13_FINANCIAL_IMPORT_DIR,
        'now_tw': now_tw(),
    })

@router.post('/import-tool/financial-batch')
def import_financial_batch(request: Request, financial_folderpath: str = Form("")):
    try:
        financial_batch_result = batch_import_financial_folder(financial_folderpath or None)
    except Exception as e:
        financial_batch_result = {'error': str(e)}
    return templates.TemplateResponse('import_tool.html', {
        'request': request,
        'result': None,
        'batch_result': None,
        'financial_result': None,
        'financial_batch_result': financial_batch_result,
        'refresh_result': load_update_status(),
        'symbols': imported_symbols(),
        'financial_symbols': imported_financial_symbols(),
        'batch_dir': V13_BATCH_IMPORT_DIR,
        'financial_batch_dir': financial_folderpath or V13_FINANCIAL_IMPORT_DIR,
        'now_tw': now_tw(),
    })

@router.post('/import-tool/refresh-all')
def refresh_all(request: Request, limit: int = Form(0), force_full: bool = Form(False)):
    refresh_result = start_background_refresh(limit=limit or None, force_price_full=force_full)
    return templates.TemplateResponse('import_tool.html', {
        'request': request,
        'result': None,
        'batch_result': None,
        'financial_result': None,
        'financial_batch_result': None,
        'refresh_result': refresh_result,
        'symbols': imported_symbols(),
        'financial_symbols': imported_financial_symbols(),
        'batch_dir': V13_BATCH_IMPORT_DIR,
        'financial_batch_dir': V13_FINANCIAL_IMPORT_DIR,
        'now_tw': now_tw(),
    })
