// Build data/sidewalks26/<slug>.geojson — per-segment sidewalk polygons for the
// segment-level map overlay in sidewalk.html, one file per county, loaded on demand.
//
// Source: MOTC 全國人行道資料 2026-06 per-county WGS84 files (no reprojection needed).
// Shrink strategy (same as the existing data/sidewalks/ files used by city.html):
//   - coordinates rounded to 6 decimals (~0.11 m, adequate for 1–5 m wide polygons)
//   - properties stripped to { n: 路名, v: 鄉鎮市區, w: 寬度, c: 淨寬, r: 斜坡數|null }
//   - no geometric simplification (polygons are already small)
// Counties are processed one at a time to bound memory (largest source is 117 MB).
// Run: node --max-old-space-size=6144 build_sidewalk_segments.js
const fs = require('fs');
const path = require('path');

const DIR_2026 = path.join(process.env.HOME, 'Taitung_Mobility/人行道空間/SIDEWALK_202606');
const OUT_DIR = 'data/sidewalks26';

global.window = {};
require('./data/cities.js');
const CITIES = global.window.CITIES;
// source filenames use 台; cities.js zh names also use 台 → direct match
const bySlug = {};
CITIES.forEach(c => { bySlug[c.slug] = c.zh; });

fs.mkdirSync(OUT_DIR, { recursive: true });

const round6 = v => Math.round(v * 1e6) / 1e6;

// Douglas-Peucker ring simplification. Tolerance 3e-6° ≈ 0.33 m — far below
// sidewalk widths (1–5 m), but it strips the dense arc-tessellation vertices
// that dominate the source files (corner radii traced with dozens of points).
const DP_TOL = 3e-6;
function perpDist(p, a, b) {
  const dx = b[0] - a[0], dy = b[1] - a[1];
  const len2 = dx * dx + dy * dy;
  if (!len2) return Math.hypot(p[0] - a[0], p[1] - a[1]);
  const t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / len2;
  const cx = a[0] + Math.max(0, Math.min(1, t)) * dx, cy = a[1] + Math.max(0, Math.min(1, t)) * dy;
  return Math.hypot(p[0] - cx, p[1] - cy);
}
function dp(points, tol) {
  if (points.length <= 2) return points;
  let maxD = 0, idx = 0;
  const a = points[0], b = points[points.length - 1];
  for (let i = 1; i < points.length - 1; i++) {
    const d = perpDist(points[i], a, b);
    if (d > maxD) { maxD = d; idx = i; }
  }
  if (maxD <= tol) return [a, b];
  return dp(points.slice(0, idx + 1), tol).slice(0, -1).concat(dp(points.slice(idx), tol));
}
function simplifyRing(ring) {
  // ring is closed (first == last). Simplify the open part, re-close, keep ≥4 pts.
  const open = ring.slice(0, -1);
  if (open.length <= 3) return ring.map(pt => [round6(pt[0]), round6(pt[1])]);
  const simp = dp(open, DP_TOL);
  const out = (simp.length >= 3 ? simp : open).map(pt => [round6(pt[0]), round6(pt[1])]);
  out.push(out[0]);
  return out;
}
function processGeom(coords, depth) {
  // MultiPolygon: [poly][ring][pt]; Polygon: [ring][pt]
  if (typeof coords[0][0][0] === 'number') return coords.map(simplifyRing);  // array of rings
  return coords.map(poly => processGeom(poly));
}

let totalOut = 0;
const summary = [];
for (const c of CITIES) {
  const src = path.join(DIR_2026, `SIDEWALK_${c.zh}_202606_WGS84.geojson`);
  if (!fs.existsSync(src)) { console.log(`⚠ missing source for ${c.zh}`); continue; }
  const geo = JSON.parse(fs.readFileSync(src, 'utf8'));
  const feats = [];
  for (const f of geo.features) {
    if (!f.geometry || !f.geometry.coordinates) continue;
    const p = f.properties || {};
    let ramp = p.SW_RAMP;
    if (ramp === 'N' || ramp === undefined || ramp === '') ramp = null;   // null = no ramp needed here
    else if (typeof ramp === 'string') ramp = parseFloat(ramp);
    feats.push({
      type: 'Feature',
      properties: {
        n: p.NAME || '',
        v: p.VILL_NAME || '',
        w: p.SW_WTH != null ? +(+p.SW_WTH).toFixed(2) : null,
        c: p.SWW_WTH != null ? +(+p.SWW_WTH).toFixed(2) : null,
        r: Number.isFinite(ramp) ? ramp : null,
      },
      geometry: { type: f.geometry.type, coordinates: processGeom(f.geometry.coordinates) },
    });
  }
  const out = { type: 'FeatureCollection', features: feats };
  const outPath = path.join(OUT_DIR, `${c.slug}.geojson`);
  const json = JSON.stringify(out);
  fs.writeFileSync(outPath, json);
  totalOut += json.length;
  summary.push({ county: c.zh, slug: c.slug, segments: feats.length, mb: +(json.length / 1048576).toFixed(2) });
  console.log(`${c.zh.padEnd(4)} ${String(feats.length).padStart(6)} segs → ${outPath} (${(json.length / 1048576).toFixed(2)} MB)`);
}
console.log('\nTotal output:', (totalOut / 1048576).toFixed(1), 'MB across', summary.length, 'counties');
