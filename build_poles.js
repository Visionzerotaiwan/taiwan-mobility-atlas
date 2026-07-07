// Build data/poles/<slug>.json — Taipower utility-pole positions per county,
// for the sidewalk-obstacle overlay in sidewalk.html §03.
//
// Source: Taipower pole registry CSV (縣市,行政區,鄉里,圖號座標,形式,桿號,TWD_97_X,TWD_97_Y),
// ~2.73M rows, TWD97 TM2 (EPSG:3826). Output: [[lat,lng], ...] (WGS84, 6 dp),
// type/id dropped (84% are 水泥桿; the overlay only needs positions).
// Streaming + per-county buckets; run: node build_poles.js "<csv path>"
const fs = require('fs');
const readline = require('readline');
const path = require('path');

const SRC = process.argv[2] || path.join(process.env.HOME, 'Downloads/all (2).csv');
const OUT_DIR = 'data/poles';

// ── TWD97 TM2 → WGS84 (inverse Transverse Mercator, GRS80) ────────────
// Main island uses the 121°E zone (EPSG:3826); the offshore counties
// 澎湖/金門/連江 use the 119°E zone (EPSG:3825).
const a = 6378137, f = 1 / 298.257222101, k0 = 0.9999, FE = 250000;
const e2 = 2 * f - f * f, ep2 = e2 / (1 - e2);
const e1 = (1 - Math.sqrt(1 - e2)) / (1 + Math.sqrt(1 - e2));
const M1 = 1 - e2 / 4 - 3 * e2 * e2 / 64 - 5 * e2 * e2 * e2 / 256;
const OFFSHORE_119 = new Set(['澎湖縣', '金門縣', '連江縣']);
function twd97ToWgs84(x, y, lon0) {
  const M = y / k0;
  const mu = M / (a * M1);
  const phi1 = mu
    + (3 * e1 / 2 - 27 * Math.pow(e1, 3) / 32) * Math.sin(2 * mu)
    + (21 * e1 * e1 / 16 - 55 * Math.pow(e1, 4) / 32) * Math.sin(4 * mu)
    + (151 * Math.pow(e1, 3) / 96) * Math.sin(6 * mu)
    + (1097 * Math.pow(e1, 4) / 512) * Math.sin(8 * mu);
  const sin1 = Math.sin(phi1), cos1 = Math.cos(phi1), tan1 = Math.tan(phi1);
  const C1 = ep2 * cos1 * cos1;
  const T1 = tan1 * tan1;
  const N1 = a / Math.sqrt(1 - e2 * sin1 * sin1);
  const R1 = a * (1 - e2) / Math.pow(1 - e2 * sin1 * sin1, 1.5);
  const D = (x - FE) / (N1 * k0);
  const lat = phi1 - (N1 * tan1 / R1) * (
    D * D / 2
    - (5 + 3 * T1 + 10 * C1 - 4 * C1 * C1 - 9 * ep2) * Math.pow(D, 4) / 24
    + (61 + 90 * T1 + 298 * C1 + 45 * T1 * T1 - 252 * ep2 - 3 * C1 * C1) * Math.pow(D, 6) / 720);
  const lon = lon0 * Math.PI / 180 + (
    D
    - (1 + 2 * T1 + C1) * Math.pow(D, 3) / 6
    + (5 - 2 * C1 + 28 * T1 - 3 * C1 * C1 + 8 * ep2 + 24 * T1 * T1) * Math.pow(D, 5) / 120) / cos1;
  return [lat * 180 / Math.PI, lon * 180 / Math.PI];
}

// ── county name → slug ────────────────────────────────────────────────
global.window = {};
require('./data/cities.js');
const CITIES = global.window.CITIES;
const norm = s => (s || '').replace(/臺/g, '台');
const zh2slug = {};
CITIES.forEach(c => { zh2slug[norm(c.zh)] = c.slug; });

// ── stream, convert, bucket ───────────────────────────────────────────
fs.mkdirSync(OUT_DIR, { recursive: true });
const buckets = {};   // slug -> array of "[lat,lng]" strings
let total = 0, bad = 0, unknownCounty = 0;

const rl = readline.createInterface({ input: fs.createReadStream(SRC), crlfDelay: Infinity });
let header = true;
rl.on('line', line => {
  if (header) { header = false; return; }
  // simple CSV: all fields quoted, no embedded commas observed
  const cols = line.split('","').map(s => s.replace(/^"|"$/g, ''));
  if (cols.length < 8) { bad++; return; }
  const slug = zh2slug[norm(cols[0])];
  if (!slug) { unknownCounty++; return; }
  const x = parseFloat(cols[6]), y = parseFloat(cols[7]);
  if (!Number.isFinite(x) || !Number.isFinite(y) || x <= 0 || y <= 0) { bad++; return; }
  const [lat, lng] = twd97ToWgs84(x, y, OFFSHORE_119.has(norm(cols[0])) ? 119 : 121);
  if (lat < 21.5 || lat > 26.5 || lng < 118 || lng > 122.5) { bad++; return; }
  (buckets[slug] = buckets[slug] || []).push(`[${lat.toFixed(6)},${lng.toFixed(6)}]`);
  total++;
});
rl.on('close', () => {
  let outBytes = 0;
  const summary = [];
  for (const c of CITIES) {
    const arr = buckets[c.slug];
    if (!arr || !arr.length) continue;
    const json = `[${arr.join(',')}]`;
    fs.writeFileSync(path.join(OUT_DIR, `${c.slug}.json`), json);
    outBytes += json.length;
    summary.push(`${c.zh.padEnd(4)} ${String(arr.length).padStart(7)} poles  ${(json.length / 1048576).toFixed(2)} MB`);
  }
  console.log(summary.join('\n'));
  console.log(`\nconverted ${total.toLocaleString()} · skipped bad ${bad} · unknown county ${unknownCounty}`);
  console.log(`output total ${(outBytes / 1048576).toFixed(1)} MB across ${summary.length} files`);
  // spot-check: first Nantou pole should be ~23.93N 120.82E (中寮鄉)
  const spot = buckets.nantou && buckets.nantou[0];
  console.log('spot-check nantou[0]:', spot);
});
