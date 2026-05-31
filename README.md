# Taiwan Mobility Atlas — National Choropleth

台灣全國交通安全面量圖｜十年回顧（民 105–114 / 2016–2025）

互動式行政區面量圖，呈現全台 364 個鄉鎮市區十年 A1 死亡事故的空間分布。
可依**受害者運具**（行人 / 機車 / 汽車 / 慢車）、**年度**、**絕對／每萬人率**動態切換。

## 線上預覽

GitHub Pages：`https://yunching0513.github.io/taiwan-mobility-atlas/`

姊妹專案（單縣市深度版）：
- [Taipei](https://github.com/yunching0513/taipei-mobility-atlas) · [Taichung](https://github.com/yunching0513/taichung-mobility-atlas) · [Tainan](https://github.com/yunching0513/tainan-mobility-atlas) · [Taitung](https://github.com/yunching0513/taitung-mobility-atlas) · [Yilan](https://github.com/yunching0513/yilan-mobility-atlas)

## 全國總覽

- **17,175 人**於 2016–2025 年因 A1 事故死亡
- **16,713 件**事件分布於 **364 個鄉鎮市區 · 22 個縣市**
- 平均每年 ~1,718 人

## 互動

- **Victim 篩選**：全部 / 機車 / 行人 / 汽貨車 / 自行車慢車
- **Year 篩選**：全部 + 2016–2025
- **Metric 切換**：累計 Total vs 每萬人 Per 10k
  - 累計：絕對死亡人數
  - 每萬人：以民國 102 年人口資料為分母的相對風險
- **點擊任一行政區**：右側顯示完整明細（10 年死亡、件數、每萬人率、運具分布、年度走勢）
- **Hover**：顯示區名 + 當前篩選下數值 + 人口

## 資料來源

| 資料 | 來源 |
|---|---|
| A1 事故 | 內政部警政署，透過 [data.gov.tw](https://data.gov.tw/) 取得 |
| 鄉鎮市區人口 | 內政部戶政司，dataset 8410（民國 102 年） |
| 行政區界 | g0v/twgeojson 之 twTown1982 + 整併至 2014 年後地理 |

## 方法論

### 受害者運具分類

每筆事件以**最脆弱用路人**為類別（行人 > 自行車/慢車 > 機車 > 汽/貨車）。
這修正了「以肇因主要當事者 P1 為分類」的偏誤 — 例如左轉小客車撞死行人，
P1 是駕駛、運具為汽車，但本地圖會把該事件歸類為「行人」。

### 行政區邊界整併

1982 年版邊界經以下整併以符合現代行政地理：
- 台北縣 → 新北市，台中縣+台中市 → 台中市
- 台南縣+台南市 → 台南市，高雄縣+高雄市 → 高雄市
- 桃園縣 → 桃園市
- 員林鎮 → 員林市（2015 升格）、頭份鎮 → 頭份市（2015 升格）
- 直轄市內部 鄉/鎮/市 統一改為 區

### 已知侷限

- 連江縣東引鄉、台東縣綠島鄉等少數小島之邊界與 A1 資料皆有缺口（影響 4 死，占全體 0.02%）
- 2013 人口資料與 2016–2025 死亡資料時間不對齊（人口變化 <20%，可接受）

## 檔案

```
index.html             # 主頁面（單檔含 CSS + Leaflet + 互動）
agg.json               # 各區聚合（10y deaths / by_mode / by_year / by_mode_year）
districts.geojson      # 365 個行政區邊界
populations.json       # 368 個區的人口（民國 102 年）
```

## 開發者

吳昀慶 · Designed for Taiwan road safety analysis

## 授權

程式碼：MIT。資料：依政府資料開放平臺授權條款。
