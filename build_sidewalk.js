// Build data/sidewalk_national.js — national sidewalk inventory, 2023-06 vs 2026-06,
// aggregated to (county, district) level for a choropleth comparison.
//
// Source: MOTC 全國人行道資料 (open data), two snapshots:
//   2023-06  ~/Taitung_Mobility/人行道空間/SideWalk_202306/SIDEWALK_202306.geojson  (TWD97 TM2, EPSG:3826)
//   2026-06  ~/Taitung_Mobility/人行道空間/SIDEWALK_202606/SIDEWALK_<county>_202606_WGS84.geojson  (WGS84, per county)
//
// Fields (per official 說明.txt):
//   NAME 道路名稱 · PSTART/PEND 起訖點 · SW_DIRECT 1東/南側 2西/北側 3徒步區
//   SW_LENG 長度(m) · SW_WTH 人行道寬度(m) · SWW_WTH 淨寬(m)
//   SW_RAMP 路緣斜坡設置數量，或 "N"/null 表示「此處無須設置」
//   COUNTY_NA 縣市 · VILL_NAME 鄉鎮市區
//
// We aggregate to (county, district) — no geometry is needed for a choropleth,
// so the (large) polygon coordinates are never parsed, only the flat
// "properties": {...} object (regex-extracted, whole-file single pass).
//
// Ramp-gap logic: SW_RAMP is a count of installed curb ramps, UNLESS the location
// doesn't need one (2023: "N"; 2026: null). So among segments that DO need a ramp,
// SW_RAMP === 0 is a genuine accessibility gap (needed, not installed).
const fs = require('fs');
const path = require('path');

const SRC_2023 = path.join(process.env.HOME, 'Taitung_Mobility/人行道空間/SideWalk_202306/SIDEWALK_202306.geojson');
const DIR_2026 = path.join(process.env.HOME, 'Taitung_Mobility/人行道空間/SIDEWALK_202606');

const norm = s => (s || '').trim().replace(/臺/g, '台');

// Known source-data quirks vs. official district names (districts.geojson):
// - 頭份/員林 were upgraded 鎮→市 in 2015; the sidewalk data still uses the old name.
// - 2 segments in the 嘉義縣 file are mistagged COUNTY_NA (西區 belongs to 嘉義市).
// 那瑪夏(高雄市) and 東引鄉(連江縣) are valid districts but absent from this repo's
// districts.geojson boundary file (pre-existing gap, same as the accident maps) —
// their totals still roll up correctly at the county level; only the per-district
// choropleth can't shade them (no polygon to shade).
const RENAME = {
  '苗栗縣|頭份鎮': ['苗栗縣', '頭份市'],
  '彰化縣|員林鎮': ['彰化縣', '員林市'],
  '嘉義縣|西區': ['嘉義市', '西區'],
};
function applyRename(county, dist) {
  const key = county + '|' + dist;
  return RENAME[key] || [county, dist];
}

function emptyStat() {
  return { n: 0, lenM: 0, wthSum: 0, netSum: 0, rampNeed: 0, rampGap: 0 };
}

function aggregateFile(text, store) {
  const propsRe = /"properties":\s*\{([^}]*)\}/g;
  let m;
  let n = 0;
  while ((m = propsRe.exec(text)) !== null) {
    n++;
    const p = m[1];
    let county = norm((p.match(/"COUNTY_NA":\s*"([^"]*)"/) || [])[1]);
    let dist = norm((p.match(/"VILL_NAME":\s*"([^"]*)"/) || [])[1]);
    if (!county || !dist) continue;
    [county, dist] = applyRename(county, dist);
    const len = parseFloat((p.match(/"SW_LENG":\s*([\d.]+)/) || [])[1]) || 0;
    const wth = parseFloat((p.match(/"SW_WTH":\s*([\d.]+)/) || [])[1]) || 0;
    const net = parseFloat((p.match(/"SWW_WTH":\s*([\d.]+)/) || [])[1]) || 0;
    const rampM = p.match(/"SW_RAMP":\s*("[^"]*"|null|[\d.]+)/);
    let rampRaw = rampM ? rampM[1] : null;
    // 2023 encodes SW_RAMP as a quoted string ("0", "N"); strip quotes so
    // parseFloat below doesn't choke on the leading '"' and silently read 0.
    if (rampRaw && rampRaw.startsWith('"') && rampRaw.endsWith('"')) rampRaw = rampRaw.slice(1, -1);
    const rampNotNeeded = rampRaw == null || rampRaw === 'null' || rampRaw === 'N';

    store.county[county] = store.county[county] || emptyStat();
    store.dist[county] = store.dist[county] || {};
    store.dist[county][dist] = store.dist[county][dist] || emptyStat();
    const cs = store.county[county], ds = store.dist[county][dist];
    for (const s of [cs, ds]) {
      s.n++; s.lenM += len; s.wthSum += wth * len; s.netSum += net * len;
      if (!rampNotNeeded) {
        s.rampNeed++;
        const rampVal = parseFloat(rampRaw);
        if (rampVal === 0) s.rampGap++;
      }
    }
  }
  return n;
}

function finalize(store) {
  const fin = (s) => ({
    n: s.n,
    length_km: +(s.lenM / 1000).toFixed(3),
    avg_wth: s.lenM ? +(s.wthSum / s.lenM).toFixed(2) : 0,
    avg_net_wth: s.lenM ? +(s.netSum / s.lenM).toFixed(2) : 0,
    ramp_need: s.rampNeed,
    ramp_gap: s.rampGap,
    ramp_gap_rate: s.rampNeed ? +(s.rampGap / s.rampNeed * 100).toFixed(1) : null,
  });
  const county = {}; for (const c in store.county) county[c] = fin(store.county[c]);
  const dist = {};
  for (const c in store.dist) { dist[c] = {}; for (const d in store.dist[c]) dist[c][d] = fin(store.dist[c][d]); }
  return { county, dist };
}

const result = {};

// ---- 2023 (single national file) ----
console.log('Reading 2023 file...');
const store23 = { county: {}, dist: {} };
const text23 = fs.readFileSync(SRC_2023, 'utf8');
const n23 = aggregateFile(text23, store23);
console.log('2023 features parsed:', n23);
result['2023'] = finalize(store23);

// ---- 2026 (per-county WGS84 files) ----
console.log('Reading 2026 files...');
const store26 = { county: {}, dist: {} };
let n26 = 0;
const files26 = fs.readdirSync(DIR_2026).filter(f => f.endsWith('_WGS84.geojson'));
for (const f of files26) {
  const text = fs.readFileSync(path.join(DIR_2026, f), 'utf8');
  n26 += aggregateFile(text, store26);
}
console.log('2026 features parsed:', n26, 'from', files26.length, 'files');
result['2026'] = finalize(store26);

// ---- cross-check district names against the atlas's own districts.geojson ----
const districts = JSON.parse(fs.readFileSync('districts.geojson', 'utf8'));
const knownPairs = new Set(districts.features.map(f => norm(f.properties.COUNTYNAME) + '|' + norm(f.properties.TOWNNAME)));
const unmatched = new Set();
for (const yr of ['2023', '2026']) {
  for (const c in result[yr].dist) {
    for (const d in result[yr].dist[c]) {
      if (!knownPairs.has(c + '|' + d)) unmatched.add(`${yr}: ${c} / ${d}`);
    }
  }
}
const KNOWN_GAPS = new Set(['高雄市 / 那瑪夏區', '高雄市 / 那瑪夏', '連江縣 / 東引鄉']);
const trueUnmatched = [...unmatched].filter(u => !KNOWN_GAPS.has(u.split(': ')[1]));
if (trueUnmatched.length) {
  console.log('\n⚠ UNEXPECTED unmatched (county/district) pairs:', trueUnmatched.length);
  trueUnmatched.forEach(u => console.log('  ', u));
} else {
  console.log('\n✓ no unexpected unmatched pairs (only the 2 known districts.geojson boundary gaps remain, if any)');
}

// ---- national totals ----
const natTotals = {};
for (const yr of ['2023', '2026']) {
  let n = 0, len = 0;
  for (const c in result[yr].county) { n += result[yr].county[c].n; len += result[yr].county[c].length_km; }
  natTotals[yr] = { n, length_km: +len.toFixed(1) };
}
console.log('\nNational totals:', JSON.stringify(natTotals));

const out = `// AUTO-GENERATED by build_sidewalk.js — do not edit by hand.
// National sidewalk inventory aggregated by (county, district), 2023-06 vs 2026-06.
// Source: MOTC 全國人行道資料開放資料 (open data), snapshots 202306 / 202606.
// Per-district fields: n (segment count), length_km, avg_wth (m, length-weighted),
// avg_net_wth (m, length-weighted clear width), ramp_need, ramp_gap, ramp_gap_rate (%).
window.SIDEWALK_NATIONAL = {
  years: ['2023', '2026'],
  national: ${JSON.stringify(natTotals)},
  by_county: ${JSON.stringify({ '2023': result['2023'].county, '2026': result['2026'].county })},
  by_district: ${JSON.stringify({ '2023': result['2023'].dist, '2026': result['2026'].dist })}
};
`;
fs.writeFileSync('data/sidewalk_national.js', out);
console.log('\nWrote data/sidewalk_national.js —', (out.length / 1024 / 1024).toFixed(2), 'MB');
