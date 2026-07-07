# Taiwan Mobility Atlas — 工作 Session 交接筆記
（由 Claude Code 產生，供在手機 Claude 上接續工作用。更新時間：2026-07-02）

## 這是什麼
台灣道路交通安全資料視覺化網站（非官方倡議專案），與「還路於民 Vision Zero Taiwan × TCAN 台灣氣候行動網絡」。
- **原始碼／資料**：GitHub `yunching0513/taiwan-mobility-atlas`（main 分支）
- **線上網站**：https://yunching0513.github.io/taiwan-mobility-atlas/
- 本機工作目錄：`/Users/yunching0513/Taitung_Mobility/taiwan-mobility-atlas`

## 資料口徑（最重要的觀念）
- 全站主數據＝ **A1（當場或 24 小時內死亡）**，十年（2016–2025）合計 **17,175 人**。這是唯一逐案、含經緯度與運具的開放資料，所有地圖都靠它。
- 官方頭條用 **30 日死亡**口徑（國際標準），同期約 **29,018（≈29,000）人**。差額約 11,843＝車禍後 24 小時–30 日間死亡者（歸 A2）。A1÷30日 ≈ 0.59，內部一致。
- 首頁 §01 有「為什麼是 17,175」對照模組完整說明。資料來源：內政部警政署 A1 開放資料；30 日數字 roadsafety.tw／tadd.org.tw。

## 首頁（index.html）章節結構（目前 01–13）
01 十年總覽 · 02 傷亡趨勢 · 03 縣市深度地圖 · 04 行政區面量圖 · 05 縣市熱力圖 ·
**06 全國事故點位與最危險路段**（點點圖＋最危險十路段合併，可切 點位／熱力／兩者，按運具＋年份篩選；點事故點看細節彈窗；點排行列在上方地圖定位＋看街景）·
07 年齡×事故態樣 · 08 性別視角 · 09 結構的代價 · 10 國際比較 · 11 氣候證據 · 12 雙齊零願景 · 13 資料說明

其他頁：city.html（22 縣市互動頁）、moto.html（機車十年解析）、vision.html（雙齊零＋五大訴求）、climate.html、international.html、whitepaper.html、nearby.html、三張列印頁。

## 資料建置腳本（node 執行，於工作目錄）
- `build_national_points.js` → `data/national_points.js`（13,708 個可定位 A1 點；含日期/時間/傷亡/地點；per-county bbox 過濾跑掉座標）
- `build_hotspots.js` → `data/hotspots_national.js`（全國最危險 top10 路段，按運具；已過濾地理編碼「中心點傾印」假熱點）
- `build_moto.js` → `data/moto.json` / `moto.js`

## 中文文案三規則（每批修訂都要套用，中英同步）
1. **中文標點一律全形**：，。、：；？！（）「」。例外不動：數字千分位（17,175）、小數（0.59）、年份（2016–2025）、網址、英文、程式碼。
2. **「死亡口徑／口徑」→「資料分類／分類」**（英文 calibre→classification）。
3. **少用破折號「——」**，改用「：」。英文的 em-dash 保留。

## 目前進度：全站「論述」10 批次逐段修訂
- **Batch 1 首頁開場＋§01 口徑框架 — ✅ 已完成**（commit ac09085，三規則已套用）
- **Batch 2 §02–§06 趨勢與地圖導言 — 🔶 進行中**：已把文字列給使用者檢視（編號 ⑰–㉚）。待辦小修：⑱ §02 政策論述那句的單破折號「—」→「：」、㉑「（區/鄉/鎮/市）」斜線→頓號「、」；其餘等使用者指定語意微調。
- Batch 3 §07 年齡＋§08 性別＋§09 結構
- Batch 4 §10–§13 收尾＋方法＋頁尾
- Batch 5–7 moto.html（§01–04／§05–08／§09–11 倡議＋方法）※ 批 7 價值論述最敏感
- Batch 8 vision.html 雙齊零＋五大訴求
- Batch 9 whitepaper.html ＋ international.html
- Batch 10 climate.html ＋ city.html 模板敘事 ＋ nearby ＋ 列印頁

## 如何接續（在手機 Claude 上）
把這份筆記貼給 Claude，說「接續 Taiwan Mobility Atlas 的論述修訂，從 Batch 2 待辦或我指定的批次開始」。實際改檔仍需在有 repo 的環境（本機 Claude Code）進行；手機上可先討論／確認要改的語意，再回到 Claude Code 執行、預覽、commit、push。

## 待使用者決定的兩件事
1. 標點全形要「現在一次掃全站」還是「逐批進行」（目前逐批）。
2. §02 政策論述語氣要更強或更溫和。
