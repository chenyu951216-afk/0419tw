from dataclasses import dataclass, asdict
import math
import pandas as pd
from app.core.config import V13_TRADING_FEE_RATE, V13_TAX_RATE, V13_SLIPPAGE_BPS

@dataclass
class BtResult:
    strategy: str
    window: int
    trades: int
    winrate: float
    avg_return: float
    max_drawdown: float
    profit_factor: float
    expectancy: float
    sharpe_like: float


def _net_return(entry: float, exit_: float) -> float:
    slip = V13_SLIPPAGE_BPS / 10000.0
    entry_eff = entry * (1 + slip)
    exit_eff = exit_ * (1 - slip)
    gross = (exit_eff / entry_eff) - 1
    costs = (V13_TRADING_FEE_RATE * 2) + V13_TAX_RATE
    return gross - costs


def _max_drawdown_from_slice(df: pd.DataFrame) -> float:
    peak = df["close"].cummax()
    dd = (df["close"] / peak) - 1
    return float(dd.min() * 100)


def _calc_atr(df: pd.DataFrame, idx: int, length: int = 14) -> float:
    sub = df.iloc[max(0, idx-length+1):idx+1].copy()
    tr = pd.concat([
        (sub["high"] - sub["low"]).abs(),
        (sub["high"] - sub["close"].shift(1)).abs(),
        (sub["low"] - sub["close"].shift(1)).abs(),
    ], axis=1).max(axis=1)
    return float(tr.mean()) if not tr.empty else 0.0


def run_strategy(df: pd.DataFrame, strategy: str, window: int = 5) -> BtResult:
    df = df.copy()
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna().reset_index(drop=True)
    closes = df["close"]
    highs = df["high"]
    lows = df["low"]
    ma20 = closes.rolling(20).mean()
    ma60 = closes.rolling(60).mean()
    rets=[]
    dds=[]
    for i in range(60, len(df)-window-1):
        cond=False
        if strategy == "breakout":
            cond = closes.iloc[i] > highs.iloc[i-20:i].max() and closes.iloc[i] > ma20.iloc[i]
        elif strategy == "pullback":
            cond = closes.iloc[i] > ma20.iloc[i] and lows.iloc[i] <= ma20.iloc[i] * 1.01 and ma20.iloc[i] > ma60.iloc[i]
        elif strategy == "trend_follow":
            cond = closes.iloc[i] > ma20.iloc[i] > ma60.iloc[i] and closes.iloc[i] > closes.iloc[i-5]
        elif strategy == "mean_revert":
            atr = _calc_atr(df, i)
            cond = closes.iloc[i] < ma20.iloc[i] - atr * 1.2 and ma20.iloc[i] > ma60.iloc[i]
        if cond:
            entry = closes.iloc[i]
            stop = max(entry - _calc_atr(df, i) * 2.0, entry * 0.88)
            take = entry + (entry - stop) * 2.0
            exit_ = closes.iloc[i+window]
            future = df.iloc[i+1:i+window+1]
            if not future.empty:
                if float(future["low"].min()) <= stop:
                    exit_ = stop
                elif float(future["high"].max()) >= take:
                    exit_ = take
            r = _net_return(entry, exit_)
            rets.append(r)
            dds.append(_max_drawdown_from_slice(df.iloc[i:i+window+1]))
    trades = len(rets)
    if not trades:
        return BtResult(strategy, window, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    wins = [r for r in rets if r > 0]
    losses = [-r for r in rets if r <= 0]
    pf = (sum(wins) / sum(losses)) if losses and sum(losses)>0 else (999 if wins else 0)
    avg = sum(rets) / trades
    std = pd.Series(rets).std(ddof=0) or 0.0
    sharpe_like = (avg / std * math.sqrt(trades)) if std > 0 else 0.0
    return BtResult(
        strategy=strategy,
        window=window,
        trades=trades,
        winrate=round(len(wins) / trades * 100, 2),
        avg_return=round(avg * 100, 2),
        max_drawdown=round(min(dds), 2),
        profit_factor=round(pf, 2) if pf != 999 else 999.0,
        expectancy=round(avg * 100, 2),
        sharpe_like=round(sharpe_like, 2),
    )


def multi_strategy_backtest(df: pd.DataFrame):
    results=[]
    for strategy in ["breakout","pullback","trend_follow","mean_revert"]:
        for window in [3,5,10,15]:
            results.append(run_strategy(df, strategy, window))
    best = sorted(results, key=lambda x: (x.profit_factor, x.winrate, x.avg_return, x.sharpe_like), reverse=True)[0]
    return {
        "best_strategy": best.strategy,
        "best_window": best.window,
        "formal_winrate": best.winrate,
        "avg_return": best.avg_return,
        "max_drawdown": best.max_drawdown,
        "profit_factor": best.profit_factor,
        "trades": best.trades,
        "expectancy": best.expectancy,
        "sharpe_like": best.sharpe_like,
        "all_results": [asdict(r) for r in results]
    }
