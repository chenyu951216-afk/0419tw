import pandas as pd
import numpy as np

def build_features(df: pd.DataFrame) -> dict:
    df = df.copy()
    for c in ["open","high","low","close","volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna().reset_index(drop=True)
    if len(df) < 30:
        return {"ma20": None, "ma60": None, "atr_pct": None, "pct_20d": 0, "pct_60d": 0, "volume_ratio_20": 1, "max_dd_120": 0}
    df["ma20"] = df["close"].rolling(20).mean()
    df["ma60"] = df["close"].rolling(60).mean()
    tr = pd.concat([
        (df["high"] - df["low"]).abs(),
        (df["high"] - df["close"].shift(1)).abs(),
        (df["low"] - df["close"].shift(1)).abs(),
    ], axis=1).max(axis=1)
    atr = tr.rolling(14).mean().iloc[-1]
    close = df["close"].iloc[-1]
    rollmax = df["close"].rolling(120).max()
    max_dd = ((df["close"] / rollmax) - 1).min()
    return {
        "last_close": float(close),
        "ma20": float(df["ma20"].iloc[-1]),
        "ma60": float(df["ma60"].iloc[-1]) if not pd.isna(df["ma60"].iloc[-1]) else float(df["ma20"].iloc[-1]),
        "atr_pct": float((atr / close) * 100) if close else 0.0,
        "pct_20d": float((close / df["close"].iloc[-20]) - 1) * 100,
        "pct_60d": float((close / df["close"].iloc[-60]) - 1) * 100 if len(df) >= 60 else 0.0,
        "volume_ratio_20": float(df["volume"].iloc[-1] / max(df["volume"].tail(20).mean(), 1)),
        "max_dd_120": float(max_dd * 100) if not np.isnan(max_dd) else 0.0,
        "recent_high_20": float(df["high"].tail(20).max()),
        "recent_low_20": float(df["low"].tail(20).min()),
    }
