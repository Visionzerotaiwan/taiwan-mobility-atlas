// Official "30-day" road-traffic death counts (A30 口徑 — death within 30 days of the crash).
// This is the headline figure cited internationally and by Taiwan's MOTC, and the number
// the public usually has in mind (~3,000 deaths/year).
//
// It is NOT the Atlas's primary series. Every map and ranking on this site is built on the
// A1 open dataset (death on scene or within 24 hours) — the ONLY case-level data that is
// geocoded and broken down per vehicle/party, which is what makes spatial analysis possible.
// A1 runs at ~0.59 of the 30-day count; the gap is people who died 24 h–30 days after the
// crash, which are recorded as A2 events at the time and never re-tallied into A1.
//
// We surface both calibres explicitly so the 24h-vs-30day distinction is unmissable.
//
// Source: 交通部道安資訊平臺 / roadsafety.tw「30 日死亡人數」;
//         A30 歷年彙整 — 台灣酒駕防制社會關懷協會 https://tadd.org.tw/situation56.htm
//         (verified against roadsafety.tw Custom dashboard, 2026-06).
window.OFFICIAL_30DAY = {
  source_zh: '交通部道安資訊平臺／roadsafety.tw「30 日死亡人數」;A30 歷年彙整 tadd.org.tw',
  source_en: 'MOTC Road Safety Information Platform / roadsafety.tw "30-day deaths"; A30 series, tadd.org.tw',
  by_year: {
    2016: 2847, 2017: 2697, 2018: 2780, 2019: 2865, 2020: 2972,
    2021: 2962, 2022: 3064, 2023: 3023, 2024: 2950, 2025: 2858
  },
  total: 29018   // sum 2016–2025
};
