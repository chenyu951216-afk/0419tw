import os
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

TZ_NAME = os.getenv("TZ_NAME", os.getenv("TZ", "Asia/Taipei"))
TZ = ZoneInfo(TZ_NAME)

def now_tw():
    return datetime.now(TZ)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
OPENAI_MONTHLY_BUDGET_TWD = float(os.getenv("OPENAI_MONTHLY_BUDGET_TWD", "500"))

DATA_MODE = os.getenv("DATA_MODE", "real")
USE_SAMPLE_DATA = os.getenv("USE_SAMPLE_DATA", "false").lower() == "true"
FORCE_TWSE_API = os.getenv("FORCE_TWSE_API", "false").lower() == "true"

V13_ENABLE_IMPORT_TOOL = os.getenv("V13_ENABLE_IMPORT_TOOL", "true").lower() == "true"
V13_ENABLE_COST_BACKTEST = os.getenv("V13_ENABLE_COST_BACKTEST", "true").lower() == "true"
V13_ENABLE_TREASURE_SCREEN = os.getenv("V13_ENABLE_TREASURE_SCREEN", "true").lower() == "true"

V13_TRADING_FEE_RATE = float(os.getenv("V13_TRADING_FEE_RATE", os.getenv("BACKTEST_FEE_RATE", "0.001425")))
V13_TAX_RATE = float(os.getenv("V13_TAX_RATE", os.getenv("BACKTEST_TAX_RATE", "0.003")))
V13_SLIPPAGE_BPS = float(os.getenv("V13_SLIPPAGE_BPS", "8"))

TREASURE_MAX_PE = float(os.getenv("TREASURE_MAX_PE", "14"))
TREASURE_MAX_PB = float(os.getenv("TREASURE_MAX_PB", "1.6"))
TREASURE_MIN_ROE = float(os.getenv("TREASURE_MIN_ROE", "10"))
TREASURE_MIN_GROSS_MARGIN = float(os.getenv("TREASURE_MIN_GROSS_MARGIN", "18"))
TREASURE_MIN_3Y_REVENUE_CAGR = float(os.getenv("TREASURE_MIN_3Y_REVENUE_CAGR", "5"))
TREASURE_MIN_REV_Q_UP = int(os.getenv("TREASURE_MIN_REV_Q_UP", "3"))
TREASURE_MIN_GM_Q_UP = int(os.getenv("TREASURE_MIN_GM_Q_UP", "2"))
TREASURE_MIN_ROE_Q_UP = int(os.getenv("TREASURE_MIN_ROE_Q_UP", "2"))
TREASURE_MIN_FCF_MARGIN = float(os.getenv("TREASURE_MIN_FCF_MARGIN", "3"))
TREASURE_MIN_DIVIDEND_YEARS = int(os.getenv("TREASURE_MIN_DIVIDEND_YEARS", "3"))
TREASURE_MIN_OCF_STABLE_YEARS = int(os.getenv("TREASURE_MIN_OCF_STABLE_YEARS", "3"))
TREASURE_MIN_FCF_POSITIVE_YEARS = int(os.getenv("TREASURE_MIN_FCF_POSITIVE_YEARS", "2"))

V14_ENABLE_VALUATION = os.getenv("V14_ENABLE_VALUATION", "true").lower() == "true"
DCF_DISCOUNT_RATE = float(os.getenv("DCF_DISCOUNT_RATE", "0.10"))
DCF_GROWTH_RATE = float(os.getenv("DCF_GROWTH_RATE", "0.025"))
TREASURE_MIN_MARGIN_OF_SAFETY = float(os.getenv("TREASURE_MIN_MARGIN_OF_SAFETY", "15"))
DIVIDEND_STABILITY_WEIGHT = float(os.getenv("DIVIDEND_STABILITY_WEIGHT", "1.0"))

APP_DATA_DIR = os.getenv("APP_DATA_DIR", os.getenv("DATA_DIR", "data"))
PRICE_HISTORY_DIR = os.getenv("PRICE_HISTORY_DIR", os.getenv("KLINE_DIR", f"{APP_DATA_DIR}/history"))
FUNDAMENTALS_DIR = os.getenv("FUNDAMENTALS_DIR", os.getenv("FINANCIAL_DIR", f"{APP_DATA_DIR}/fundamentals"))
NEWS_DIR = os.getenv("NEWS_DIR", f"{APP_DATA_DIR}/news")
RANKING_DIR = os.getenv("RANKING_DIR", f"{APP_DATA_DIR}/ranking")
UNIVERSE_DIR = os.getenv("UNIVERSE_DIR", f"{APP_DATA_DIR}/universe")
CACHE_DIR = os.getenv("CACHE_DIR", f"{APP_DATA_DIR}/cache")
V13_BATCH_IMPORT_DIR = os.getenv("V13_BATCH_IMPORT_DIR", f"{APP_DATA_DIR}/batch_import")
V13_IMPORTED_DIR = os.getenv("V13_IMPORTED_DIR", f"{APP_DATA_DIR}/imported")
V13_AUTO_SCAN_IMPORT_DIR = os.getenv("V13_AUTO_SCAN_IMPORT_DIR", "true").lower() == "true"
V13_AUTO_SCAN_EXTENSIONS = [x.strip() for x in os.getenv("V13_AUTO_SCAN_EXTENSIONS", ".csv").split(",") if x.strip()]
V13_FINANCIAL_IMPORT_DIR = os.getenv("V13_FINANCIAL_IMPORT_DIR", f"{APP_DATA_DIR}/financial_batch")
V13_FINANCIAL_STORE_DIR = os.getenv("V13_FINANCIAL_STORE_DIR", f"{APP_DATA_DIR}/financials")
V13_AUTO_SCAN_FINANCIAL_DIR = os.getenv("V13_AUTO_SCAN_FINANCIAL_DIR", "true").lower() == "true"
V13_FINANCIAL_EXTENSIONS = [x.strip() for x in os.getenv("V13_FINANCIAL_EXTENSIONS", ".csv").split(",") if x.strip()]

AUTO_UPDATE_ON_STARTUP = os.getenv("AUTO_UPDATE_ON_STARTUP", "true").lower() == "true"
AUTO_UPDATE_DAILY = os.getenv("AUTO_UPDATE_DAILY", "true").lower() == "true"
AUTO_UPDATE_HOUR = int(os.getenv("AUTO_UPDATE_HOUR", "19"))
AUTO_UPDATE_MINUTE = int(os.getenv("AUTO_UPDATE_MINUTE", "30"))
AUTO_UPDATE_FETCH_NEWS = os.getenv("AUTO_UPDATE_FETCH_NEWS", "true").lower() == "true"
AUTO_UPDATE_FETCH_FINANCIALS = os.getenv("AUTO_UPDATE_FETCH_FINANCIALS", "true").lower() == "true"
AUTO_UPDATE_TOP_LIQUIDITY_COUNT = int(os.getenv("AUTO_UPDATE_TOP_LIQUIDITY_COUNT", "300"))
AUTO_UPDATE_LOOKBACK_DAYS = int(os.getenv("AUTO_UPDATE_LOOKBACK_DAYS", "1200"))
AUTO_UPDATE_MAX_NEWS_PER_SYMBOL = int(os.getenv("AUTO_UPDATE_MAX_NEWS_PER_SYMBOL", "8"))
AUTO_UPDATE_PRICE_LIMIT = int(os.getenv("AUTO_UPDATE_PRICE_LIMIT", "60"))
AUTO_UPDATE_FINANCIAL_LIMIT = int(os.getenv("AUTO_UPDATE_FINANCIAL_LIMIT", "30"))
AUTO_UPDATE_NEWS_LIMIT = int(os.getenv("AUTO_UPDATE_NEWS_LIMIT", "30"))
AUTO_UPDATE_BUILD_RANKING = os.getenv("AUTO_UPDATE_BUILD_RANKING", "true").lower() == "true"
AUTO_UPDATE_INITIAL_LIMIT = int(os.getenv("AUTO_UPDATE_INITIAL_LIMIT", "20"))
AUTO_UPDATE_RUN_IN_BACKGROUND = os.getenv("AUTO_UPDATE_RUN_IN_BACKGROUND", "true").lower() == "true"
AUTO_UPDATE_REBUILD_SNAPSHOT_IF_MISSING = os.getenv("AUTO_UPDATE_REBUILD_SNAPSHOT_IF_MISSING", "true").lower() == "true"

YFINANCE_ENABLED = os.getenv("YFINANCE_ENABLED", "true").lower() == "true"
YFINANCE_START = os.getenv("YFINANCE_START", "2010-01-01")
YFINANCE_PERIOD = os.getenv("YFINANCE_PERIOD", "3mo")
YFINANCE_FORCE_FULL_REFRESH = os.getenv("YFINANCE_FORCE_FULL_REFRESH", "false").lower() == "true"
YFINANCE_MAX_RETRIES = int(os.getenv("YFINANCE_MAX_RETRIES", "3"))
YFINANCE_RETRY_SLEEP = float(os.getenv("YFINANCE_RETRY_SLEEP", "6"))
YFINANCE_REQUEST_PAUSE = float(os.getenv("YFINANCE_REQUEST_PAUSE", "1.2"))
YFINANCE_BATCH_SIZE = int(os.getenv("YFINANCE_BATCH_SIZE", "8"))
YFINANCE_BATCH_PAUSE = float(os.getenv("YFINANCE_BATCH_PAUSE", "15"))
YFINANCE_INCREMENTAL_OVERLAP_DAYS = int(os.getenv("YFINANCE_INCREMENTAL_OVERLAP_DAYS", "10"))
YFINANCE_MAX_SYMBOLS_PER_RUN = int(os.getenv("YFINANCE_MAX_SYMBOLS_PER_RUN", "60"))
ALLOW_LIVE_FETCH_ON_READ = os.getenv("ALLOW_LIVE_FETCH_ON_READ", "false").lower() == "true"

MOPS_ENABLED = os.getenv("MOPS_ENABLED", "true").lower() == "true"
NEWS_ENABLED = os.getenv("NEWS_ENABLED", "true").lower() == "true"
RANKING_MIN_HISTORY_DAYS = int(os.getenv("RANKING_MIN_HISTORY_DAYS", "120"))
RANKING_USE_CACHED_SNAPSHOT = os.getenv("RANKING_USE_CACHED_SNAPSHOT", "true").lower() == "true"
RANKING_SNAPSHOT_MAX_AGE_MINUTES = int(os.getenv("RANKING_SNAPSHOT_MAX_AGE_MINUTES", "180"))
