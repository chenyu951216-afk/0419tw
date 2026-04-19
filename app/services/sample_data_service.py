import random
from datetime import timedelta
import pandas as pd
from app.core.config import now_tw

SAMPLE_STOCKS = [
    ("2330", "台積電", "半導體"),
    ("2317", "鴻海", "電子代工"),
    ("2382", "廣達", "AI伺服器"),
    ("2308", "台達電", "電源"),
    ("2454", "聯發科", "IC設計"),
    ("3017", "奇鋐", "散熱"),
    ("3324", "雙鴻", "散熱"),
    ("1519", "華城", "重電"),
    ("1609", "大亞", "電線電纜"),
    ("3661", "世芯-KY", "ASIC"),
]

def sample_history(stock_id: str, days: int = 260) -> pd.DataFrame:
    seed = sum(ord(c) for c in stock_id)
    random.seed(seed)
    start_price = random.randint(40, 700)
    rows = []
    dt = now_tw().date() - timedelta(days=days*1.5)
    price = float(start_price)
    count = 0
    while count < days:
        if dt.weekday() < 5:
            drift = random.uniform(-0.02, 0.03)
            o = price * (1 + random.uniform(-0.01, 0.01))
            c = max(10, o * (1 + drift))
            h = max(o, c) * (1 + random.uniform(0, 0.02))
            l = min(o, c) * (1 - random.uniform(0, 0.02))
            v = random.randint(2000, 50000)
            rows.append({"date": dt.isoformat(), "open": round(o,2), "high": round(h,2), "low": round(l,2), "close": round(c,2), "volume": v})
            price = c
            count += 1
        dt += timedelta(days=1)
    return pd.DataFrame(rows)

def sample_fundamentals():
    data = {
        "2330": {"pe": 22, "pb": 5.6, "roe": 30, "gross_margin": 53, "revenue_cagr_3y": 18, "eps": 38},
        "2317": {"pe": 12, "pb": 1.3, "roe": 11, "gross_margin": 9, "revenue_cagr_3y": 7, "eps": 10},
        "2382": {"pe": 16, "pb": 2.7, "roe": 17, "gross_margin": 17, "revenue_cagr_3y": 12, "eps": 15},
        "2308": {"pe": 20, "pb": 4.2, "roe": 22, "gross_margin": 32, "revenue_cagr_3y": 11, "eps": 13},
        "2454": {"pe": 24, "pb": 4.5, "roe": 24, "gross_margin": 48, "revenue_cagr_3y": 15, "eps": 52},
        "3017": {"pe": 18, "pb": 5.0, "roe": 28, "gross_margin": 24, "revenue_cagr_3y": 26, "eps": 16},
        "3324": {"pe": 17, "pb": 4.8, "roe": 26, "gross_margin": 23, "revenue_cagr_3y": 22, "eps": 14},
        "1519": {"pe": 13, "pb": 2.1, "roe": 15, "gross_margin": 21, "revenue_cagr_3y": 16, "eps": 8},
        "1609": {"pe": 11, "pb": 1.4, "roe": 12, "gross_margin": 14, "revenue_cagr_3y": 9, "eps": 4},
        "3661": {"pe": 28, "pb": 7.5, "roe": 21, "gross_margin": 30, "revenue_cagr_3y": 35, "eps": 30},
    }
    return data

def sample_quarterly_fundamentals():
    return {
        "2330": {"revenue_yoy":[8,12,16,18],"gross_margin":[49,50,52,53],"roe":[26,27,29,30],"eps":[8.0,8.8,9.5,10.2]},
        "2317": {"revenue_yoy":[3,4,6,7],"gross_margin":[7.8,8.1,8.5,9.0],"roe":[9.8,10.1,10.5,11.0],"eps":[2.0,2.2,2.5,2.7]},
        "2382": {"revenue_yoy":[6,8,10,12],"gross_margin":[15.5,16.0,16.4,17.0],"roe":[13,14,16,17],"eps":[2.8,3.1,3.5,3.9]},
        "2308": {"revenue_yoy":[4,7,9,11],"gross_margin":[28,29,31,32],"roe":[18,19,21,22],"eps":[2.4,2.8,3.0,3.3]},
        "2454": {"revenue_yoy":[7,9,12,15],"gross_margin":[44,45,47,48],"roe":[21,22,23,24],"eps":[11,12,13,14]},
        "3017": {"revenue_yoy":[12,16,20,26],"gross_margin":[20,21,23,24],"roe":[20,22,25,28],"eps":[2.6,3.0,3.5,4.0]},
        "3324": {"revenue_yoy":[10,14,18,22],"gross_margin":[19,20,22,23],"roe":[19,21,24,26],"eps":[2.4,2.7,3.0,3.4]},
        "1519": {"revenue_yoy":[6,9,12,16],"gross_margin":[18,19,20,21],"roe":[12,13,14,15],"eps":[1.4,1.6,1.9,2.1]},
        "1609": {"revenue_yoy":[1,3,6,9],"gross_margin":[10,11,12.5,14],"roe":[9,9.5,10.5,12],"eps":[0.7,0.8,0.9,1.0]},
        "3661": {"revenue_yoy":[18,24,30,35],"gross_margin":[24,26,28,30],"roe":[16,18,20,21],"eps":[5.5,6.3,7.0,7.6]},
    }

def stock_master():
    return [{"stock_id": sid, "name": name, "industry": ind} for sid, name, ind in SAMPLE_STOCKS]


SHARES_OUTSTANDING_MAP = {"2330": 25930, "2317": 13800, "2382": 9400, "2308": 5200, "2454": 860, "3017": 760, "3324": 420, "1519": 360, "1609": 950, "3661": 210}

def sample_financial_histories():
    data = {
        "2330": [
            {"year":2020,"revenue":13390,"gross_margin":53.1,"roe":25.7,"eps":19.97,"operating_cf":6600,"capex":3100,"free_cf":3500,"dividend":10.0},
            {"year":2021,"revenue":15870,"gross_margin":51.6,"roe":28.3,"eps":23.01,"operating_cf":7000,"capex":3200,"free_cf":3800,"dividend":11.0},
            {"year":2022,"revenue":22640,"gross_margin":59.6,"roe":36.0,"eps":39.20,"operating_cf":11000,"capex":5200,"free_cf":5800,"dividend":11.0},
            {"year":2023,"revenue":21600,"gross_margin":54.4,"roe":28.6,"eps":32.34,"operating_cf":9800,"capex":4900,"free_cf":4900,"dividend":12.0},
            {"year":2024,"revenue":25000,"gross_margin":55.5,"roe":31.0,"eps":38.0,"operating_cf":12000,"capex":5500,"free_cf":6500,"dividend":14.0},
        ],
        "2317": [
            {"year":2020,"revenue":53600,"gross_margin":6.1,"roe":9.2,"eps":8.0,"operating_cf":3500,"capex":1100,"free_cf":2400,"dividend":4.2},
            {"year":2021,"revenue":59000,"gross_margin":6.3,"roe":10.0,"eps":9.0,"operating_cf":3800,"capex":1200,"free_cf":2600,"dividend":4.5},
            {"year":2022,"revenue":66200,"gross_margin":6.4,"roe":10.6,"eps":10.1,"operating_cf":4100,"capex":1400,"free_cf":2700,"dividend":5.0},
            {"year":2023,"revenue":62500,"gross_margin":6.2,"roe":10.5,"eps":9.7,"operating_cf":3900,"capex":1300,"free_cf":2600,"dividend":5.2},
            {"year":2024,"revenue":65000,"gross_margin":6.8,"roe":11.3,"eps":10.4,"operating_cf":4300,"capex":1300,"free_cf":3000,"dividend":5.4},
        ],
        "2382": [
            {"year":2020,"revenue":10200,"gross_margin":12.2,"roe":12.1,"eps":6.0,"operating_cf":620,"capex":160,"free_cf":460,"dividend":4.5},
            {"year":2021,"revenue":11100,"gross_margin":12.6,"roe":13.4,"eps":6.8,"operating_cf":710,"capex":170,"free_cf":540,"dividend":5.0},
            {"year":2022,"revenue":12000,"gross_margin":13.6,"roe":14.8,"eps":7.6,"operating_cf":840,"capex":190,"free_cf":650,"dividend":5.5},
            {"year":2023,"revenue":13100,"gross_margin":15.1,"roe":16.1,"eps":8.9,"operating_cf":980,"capex":220,"free_cf":760,"dividend":6.0},
            {"year":2024,"revenue":14500,"gross_margin":17.0,"roe":17.2,"eps":10.0,"operating_cf":1130,"capex":260,"free_cf":870,"dividend":6.5},
        ],
        "2308": [
            {"year":2020,"revenue":2820,"gross_margin":30.1,"roe":18.4,"eps":8.1,"operating_cf":450,"capex":120,"free_cf":330,"dividend":5.0},
            {"year":2021,"revenue":3150,"gross_margin":31.0,"roe":19.2,"eps":8.8,"operating_cf":500,"capex":130,"free_cf":370,"dividend":5.5},
            {"year":2022,"revenue":3600,"gross_margin":32.0,"roe":20.6,"eps":10.0,"operating_cf":560,"capex":140,"free_cf":420,"dividend":6.0},
            {"year":2023,"revenue":3900,"gross_margin":31.5,"roe":21.4,"eps":11.2,"operating_cf":600,"capex":150,"free_cf":450,"dividend":6.5},
            {"year":2024,"revenue":4300,"gross_margin":32.5,"roe":22.1,"eps":12.1,"operating_cf":680,"capex":165,"free_cf":515,"dividend":7.0},
        ],
        "2454": [
            {"year":2020,"revenue":3200,"gross_margin":43.5,"roe":18.0,"eps":26.0,"operating_cf":680,"capex":90,"free_cf":590,"dividend":15.0},
            {"year":2021,"revenue":4100,"gross_margin":45.0,"roe":20.2,"eps":35.0,"operating_cf":820,"capex":110,"free_cf":710,"dividend":18.0},
            {"year":2022,"revenue":5480,"gross_margin":48.0,"roe":24.0,"eps":52.0,"operating_cf":1020,"capex":130,"free_cf":890,"dividend":22.0},
            {"year":2023,"revenue":4800,"gross_margin":46.5,"roe":22.6,"eps":48.0,"operating_cf":950,"capex":135,"free_cf":815,"dividend":25.0},
            {"year":2024,"revenue":5200,"gross_margin":48.5,"roe":24.2,"eps":55.0,"operating_cf":1080,"capex":150,"free_cf":930,"dividend":28.0},
        ],
        "3017": [
            {"year":2020,"revenue":1800,"gross_margin":18.0,"roe":15.0,"eps":5.2,"operating_cf":230,"capex":80,"free_cf":150,"dividend":3.0},
            {"year":2021,"revenue":2200,"gross_margin":19.5,"roe":18.0,"eps":6.4,"operating_cf":280,"capex":90,"free_cf":190,"dividend":3.5},
            {"year":2022,"revenue":2900,"gross_margin":21.5,"roe":22.0,"eps":8.5,"operating_cf":360,"capex":110,"free_cf":250,"dividend":4.2},
            {"year":2023,"revenue":3500,"gross_margin":23.0,"roe":25.0,"eps":10.8,"operating_cf":430,"capex":125,"free_cf":305,"dividend":5.0},
            {"year":2024,"revenue":4200,"gross_margin":24.5,"roe":28.0,"eps":13.2,"operating_cf":510,"capex":145,"free_cf":365,"dividend":5.8},
        ],
        "3324": [
            {"year":2020,"revenue":1200,"gross_margin":17.5,"roe":14.0,"eps":3.8,"operating_cf":180,"capex":60,"free_cf":120,"dividend":2.0},
            {"year":2021,"revenue":1500,"gross_margin":19.0,"roe":17.0,"eps":4.5,"operating_cf":220,"capex":70,"free_cf":150,"dividend":2.5},
            {"year":2022,"revenue":1900,"gross_margin":20.8,"roe":20.0,"eps":5.6,"operating_cf":280,"capex":80,"free_cf":200,"dividend":3.0},
            {"year":2023,"revenue":2300,"gross_margin":22.0,"roe":23.0,"eps":6.8,"operating_cf":330,"capex":92,"free_cf":238,"dividend":3.8},
            {"year":2024,"revenue":2700,"gross_margin":23.2,"roe":25.0,"eps":7.8,"operating_cf":390,"capex":100,"free_cf":290,"dividend":4.2},
        ],
        "1519": [
            {"year":2020,"revenue":540,"gross_margin":18.0,"roe":11.0,"eps":2.2,"operating_cf":65,"capex":18,"free_cf":47,"dividend":1.8},
            {"year":2021,"revenue":620,"gross_margin":18.5,"roe":12.0,"eps":2.5,"operating_cf":72,"capex":20,"free_cf":52,"dividend":2.0},
            {"year":2022,"revenue":760,"gross_margin":19.5,"roe":13.4,"eps":3.0,"operating_cf":84,"capex":22,"free_cf":62,"dividend":2.3},
            {"year":2023,"revenue":910,"gross_margin":20.5,"roe":14.1,"eps":3.6,"operating_cf":95,"capex":24,"free_cf":71,"dividend":2.6},
            {"year":2024,"revenue":1060,"gross_margin":21.0,"roe":15.0,"eps":4.2,"operating_cf":108,"capex":26,"free_cf":82,"dividend":3.0},
        ],
        "1609": [
            {"year":2020,"revenue":260,"gross_margin":10.5,"roe":8.1,"eps":1.2,"operating_cf":28,"capex":12,"free_cf":16,"dividend":0.7},
            {"year":2021,"revenue":290,"gross_margin":11.0,"roe":8.8,"eps":1.4,"operating_cf":32,"capex":13,"free_cf":19,"dividend":0.8},
            {"year":2022,"revenue":340,"gross_margin":12.2,"roe":9.5,"eps":1.8,"operating_cf":38,"capex":14,"free_cf":24,"dividend":1.0},
            {"year":2023,"revenue":390,"gross_margin":13.0,"roe":10.2,"eps":2.1,"operating_cf":44,"capex":15,"free_cf":29,"dividend":1.2},
            {"year":2024,"revenue":430,"gross_margin":14.0,"roe":11.2,"eps":2.5,"operating_cf":50,"capex":16,"free_cf":34,"dividend":1.4},
        ],
        "3661": [
            {"year":2020,"revenue":900,"gross_margin":22.0,"roe":12.0,"eps":8.0,"operating_cf":140,"capex":60,"free_cf":80,"dividend":3.0},
            {"year":2021,"revenue":1200,"gross_margin":24.5,"roe":15.0,"eps":10.5,"operating_cf":180,"capex":70,"free_cf":110,"dividend":4.0},
            {"year":2022,"revenue":1650,"gross_margin":27.0,"roe":18.0,"eps":14.0,"operating_cf":240,"capex":85,"free_cf":155,"dividend":5.0},
            {"year":2023,"revenue":2100,"gross_margin":28.5,"roe":19.5,"eps":17.5,"operating_cf":295,"capex":95,"free_cf":200,"dividend":6.0},
            {"year":2024,"revenue":2650,"gross_margin":30.0,"roe":21.0,"eps":21.0,"operating_cf":360,"capex":110,"free_cf":250,"dividend":7.0},
        ],
    }
    for sid, rows in data.items():
        shares = SHARES_OUTSTANDING_MAP.get(sid, 1000)
        for r in rows:
            r.setdefault("shares_outstanding_m", shares)
    return data
