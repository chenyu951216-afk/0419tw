# TW Stock Bot v16 穩定防封鎖版

這版重點是讓 Zeabur 可以長時間穩跑，不再因為 yfinance 連續大量抓取而整站 500。

## 穩定化重點
- 價格更新改成「增量更新」：有舊資料時只抓最近 3 個月，並自動合併。
- yfinance 加入 retry / backoff / request pause / batch pause。
- 啟動更新改成背景執行，不阻塞 Web 啟動。
- 頁面改讀排名快照，不在每次開頁面時即時重抓資料。
- 抓價失敗時保留既有快取，不讓整個服務直接炸掉。
- 手動刷新改成背景任務。

## Zeabur 建議啟動指令
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## 必要 Persistent Volume
掛載 `/data`

## 建議環境變數
請看 `.env.example`


## Zeabur 最終部署

建議直接用 Dockerfile 部署。

- Start Command：`uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}`
- Health Check：`/healthz`
- Persistent Volume：掛到 `/data`
- 若不需要 AI，不用放 `OPENAI_API_KEY`。
- 若要 AI 分析，再填：`OPENAI_ENABLED=true`、`OPENAI_API_KEY=...`
