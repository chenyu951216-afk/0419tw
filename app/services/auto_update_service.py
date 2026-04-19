from __future__ import annotations
from pathlib import Path
import json
import threading
import time
from datetime import datetime, timedelta

from app.core.config import (
    AUTO_UPDATE_DAILY,
    AUTO_UPDATE_FETCH_FINANCIALS,
    AUTO_UPDATE_FETCH_NEWS,
    AUTO_UPDATE_HOUR,
    AUTO_UPDATE_MINUTE,
    APP_DATA_DIR,
    AUTO_UPDATE_PRICE_LIMIT,
    AUTO_UPDATE_FINANCIAL_LIMIT,
    AUTO_UPDATE_NEWS_LIMIT,
    AUTO_UPDATE_BUILD_RANKING,
    YFINANCE_BATCH_SIZE,
    YFINANCE_BATCH_PAUSE,
    YFINANCE_MAX_SYMBOLS_PER_RUN,
)
from app.services.stock_universe_service import fetch_stock_universe, load_stock_universe
from app.services.market_data_service import update_symbol_history
from app.services.mops_financial_service import fetch_financial_history_from_mops
from app.services.news_service import fetch_symbol_news
from app.services.ranking_service import build_rankings

STATUS_PATH = Path(APP_DATA_DIR) / "update_status.json"
_LOCK = threading.Lock()
_STARTED = False
_RUNNING = False


def _write_status(payload: dict):
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATUS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_update_status() -> dict:
    if STATUS_PATH.exists():
        try:
            return json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _target_rows(limit: int | None = None) -> list[dict]:
    fetch_stock_universe(force=False)
    uni = load_stock_universe()
    rows = uni.to_dict(orient="records")
    effective_limit = limit or AUTO_UPDATE_PRICE_LIMIT or YFINANCE_MAX_SYMBOLS_PER_RUN
    if effective_limit:
        rows = rows[:effective_limit]
    return rows


def run_full_refresh(limit: int | None = None, force_price_full: bool = False) -> dict:
    global _RUNNING
    with _LOCK:
        _RUNNING = True
        started_at = datetime.utcnow().isoformat() + "Z"
        rows = _target_rows(limit)
        price_rows = rows[: min(len(rows), AUTO_UPDATE_PRICE_LIMIT or len(rows))]
        financial_rows = rows[: min(len(rows), AUTO_UPDATE_FINANCIAL_LIMIT or 0)] if AUTO_UPDATE_FETCH_FINANCIALS else []
        news_rows = rows[: min(len(rows), AUTO_UPDATE_NEWS_LIMIT or 0)] if AUTO_UPDATE_FETCH_NEWS else []
        results = {
            "status": "running",
            "started_at": started_at,
            "price_target": len(price_rows),
            "financial_target": len(financial_rows),
            "news_target": len(news_rows),
            "updated_prices": 0,
            "updated_financials": 0,
            "updated_news": 0,
            "errors": [],
        }
        _write_status(results)
        try:
            for idx, row in enumerate(price_rows, start=1):
                sid = str(row["stock_id"])
                try:
                    update_symbol_history(sid, force_full=force_price_full)
                    results["updated_prices"] += 1
                except Exception as e:
                    results["errors"].append({"stock_id": sid, "stage": "price", "error": str(e)})
                if idx % max(YFINANCE_BATCH_SIZE, 1) == 0 and idx < len(price_rows):
                    time.sleep(max(YFINANCE_BATCH_PAUSE, 0))
                if idx % 5 == 0:
                    _write_status(results)

            for row in financial_rows:
                sid = str(row["stock_id"])
                try:
                    fetch_financial_history_from_mops(sid)
                    results["updated_financials"] += 1
                except Exception as e:
                    results["errors"].append({"stock_id": sid, "stage": "financial", "error": str(e)})

            for row in news_rows:
                sid = str(row["stock_id"])
                try:
                    fetch_symbol_news(sid)
                    results["updated_news"] += 1
                except Exception as e:
                    results["errors"].append({"stock_id": sid, "stage": "news", "error": str(e)})

            if AUTO_UPDATE_BUILD_RANKING:
                ranking = build_rankings(force=True)
                results["ranking_top5"] = [f"{x['stock_id']} {x['name']}" for x in ranking.get("top5", [])]
            results["status"] = "success"
            results["finished_at"] = datetime.utcnow().isoformat() + "Z"
            _write_status(results)
            return results
        except Exception as e:
            results["status"] = "failed"
            results["finished_at"] = datetime.utcnow().isoformat() + "Z"
            results["fatal_error"] = str(e)
            _write_status(results)
            return results
        finally:
            _RUNNING = False


def start_background_refresh(limit: int | None = None, force_price_full: bool = False) -> dict:
    global _RUNNING
    if _RUNNING:
        status = load_update_status() or {}
        status["status"] = status.get("status", "running")
        status["message"] = "已有背景更新執行中"
        _write_status(status)
        return status

    def _runner():
        run_full_refresh(limit=limit, force_price_full=force_price_full)

    status = {
        "status": "queued",
        "queued_at": datetime.utcnow().isoformat() + "Z",
        "message": "背景更新已啟動",
        "limit": limit,
        "force_price_full": force_price_full,
    }
    _write_status(status)
    t = threading.Thread(target=_runner, daemon=True)
    t.start()
    return status


def _seconds_until_target(hour: int, minute: int) -> float:
    now = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()


def _daily_loop():
    while True:
        time.sleep(max(_seconds_until_target(AUTO_UPDATE_HOUR, AUTO_UPDATE_MINUTE), 30))
        try:
            start_background_refresh()
        except Exception as e:
            _write_status({"status": "failed", "error": str(e), "failed_at": datetime.utcnow().isoformat() + "Z"})


def start_scheduler_if_needed():
    global _STARTED
    if _STARTED or not AUTO_UPDATE_DAILY:
        return
    t = threading.Thread(target=_daily_loop, daemon=True)
    t.start()
    _STARTED = True
