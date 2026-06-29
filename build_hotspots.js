// Build data/hotspots_national.json — the 10 most dangerous road segments
// nationwide, by victim type (all / 機車 / 汽車 / 人 / 慢車).
//
// Replicates city.html's hotspot clustering exactly:
//   • road name + km marker → ~3 km segment cluster
//   • otherwise              → ~300 m spatial grid cell
// ranked by cumulative A1 deaths, top 10.
//
// Difference from the per-county version: the cluster key is PREFIXED WITH THE
// COUNTY, so repeated road numbers (縣道/鄉道) or generic names (市區道路) in
// different counties never merge into one false national hotspot.
//
// Only coord-bearing events are used (same as the map / dot map); the ~3,000
// coordinate-less simplified-year records are excluded.
const fs = require('fs');

const ROAD_RE = /(台\d+(?:乙|甲|丙)?線|縣道\d+|鄉道[\w\d]*|市區道路|產業道路)/;
const KM_RE = /(\d+)\s*公里/;
const SEG_KM = 3;
const SPATIAL_GRID = 0.003;
const MODES = ['機車', '汽車', '人', '慢車', '其他'];
const norm = s => (s || '').replace(/臺/g, '台');

global.window = {};
require('./data/cities.js');
const CITIES = global.window.CITIES;

// Gather every coord-bearing A1 event, tagged with county.
const ALL = [];
CITIES.forEach(c => {
  const file = `./data/${c.slug}.js`;
  global.window = {};
  delete require.cache[require.resolve(file)];
  require(file);
  (global.window.CITY_A1 || []).forEach(r => {
    if (!+r.lat || !+r.lon) return;
    ALL.push({
      lat: +r.lat, lon: +r.lon, deaths: r.deaths || 0, year: r.year,
      mode: r.mode, district: r.district || '', location: r.location || '',
      countySlug: c.slug, countyZh: c.zh, countyEn: c.en,
    });
  });
});

// Strip county/district prefix + trailing address detail → core road name(s).
// "高雄市鳥松區神農路330號前0.0公尺" → ["神農路"];  "A路 / B街" → ["A路","B街"]
function roadCores(loc) {
  const out = [];
  (loc || '').split('/').forEach(s => {
    s = s.trim();
    let prev;
    do { prev = s; s = s.replace(/^.{2,3}[市縣].{1,4}[區鄉鎮市裡里]/, ''); } while (s !== prev); // strip doubled prefixes
    s = s.replace(/[\d前與及（(].*$/, '').trim();
    if (s && !out.includes(s)) out.push(s);   // dedupe within a location
  });
  return out;
}

function clusterKey(ev) {
  const roadM = ev.location.match(ROAD_RE);
  const kmM = ev.location.match(KM_RE);
  if (roadM && kmM) {
    const seg = Math.floor(parseInt(kmM[1], 10) / SEG_KM);
    return { kind: 'road', key: `${ev.countySlug}|${roadM[1]}#${seg}` };
  }
  const lat = Math.round(ev.lat / SPATIAL_GRID);
  const lon = Math.round(ev.lon / SPATIAL_GRID);
  return { kind: 'grid', key: `${ev.countySlug}|g${lat}_${lon}` };
}

function computeHotspots(events, topN) {
  const bins = new Map();
  events.forEach(e => {
    const ck = clusterKey(e);
    if (!bins.has(ck.key)) bins.set(ck.key, { kind: ck.kind, evs: [] });
    bins.get(ck.key).evs.push(e);
  });
  return Array.from(bins.values()).map(b => {
    const deaths = b.evs.reduce((s, e) => s + e.deaths, 0);
    const lead = b.evs.slice().sort((a, c) => (c.deaths - a.deaths) || a.year - c.year)[0];
    const distCnt = {};
    b.evs.forEach(e => { distCnt[e.district] = (distCnt[e.district] || 0) + 1; });
    const districts = Object.entries(distCnt).sort((a, c) => c[1] - a[1]).map(([d]) => d);
    const yrs = Array.from(new Set(b.evs.map(e => e.year))).sort();
    const yrRange = yrs.length === 1 ? `${yrs[0]}` : `${yrs[0]}–${yrs[yrs.length - 1]}`;
    const breakdown = {};
    MODES.forEach(m => breakdown[m] = 0);
    b.evs.forEach(e => { breakdown[MODES.includes(e.mode) ? e.mode : '其他'] += e.deaths; });

    // Clean, human label. Highways → designator + km range; urban → road core(s).
    const HWY_RE = /(國道\d+|台\d+(?:乙|甲|丙)?線|縣道?\d+線?|鄉道\S+|快速公路|省道)/;
    const hwyM = lead.location.match(HWY_RE);
    let label;
    if (hwyM) {
      const kms = b.evs.map(e => {
        const m = e.location.match(/(\d+)\s*公里/) || e.location.match(/(\d+(?:\.\d+)?)\s*[Kk]/);
        return m ? parseFloat(m[1]) : null;
      }).filter(v => v != null);
      let kmLabel = '';
      if (kms.length) { const lo = Math.min(...kms), hi = Math.max(...kms); kmLabel = Math.floor(lo) === Math.ceil(hi) ? `${Math.round(lo)}k` : `${Math.floor(lo)}–${Math.ceil(hi)}k`; }
      label = `${hwyM[1].replace('號', '')} ${kmLabel}`.trim();
    } else {
      const freq = {};
      b.evs.forEach(e => roadCores(e.location).forEach(r => { freq[r] = (freq[r] || 0) + 1; }));
      const top = Object.entries(freq).sort((a, c) => c[1] - a[1]).map(([r]) => r);
      label = top.slice(0, 2).join(' × ') ||
        ((lead.location.split('/')[0] || lead.location)
          .replace(/^.{2,3}[市縣].{1,4}[區鄉鎮市]/, '').replace(/^.{2,3}[市縣].{1,4}[區鄉鎮市]/, '')
          .replace(/前\s*\d+\.?\d*\s*公尺.*$/, '').replace(/[（(].*$/, '').trim() || lead.location);
    }
    const uniquePts = new Set(b.evs.map(e => `${e.lat.toFixed(5)}_${e.lon.toFixed(5)}`)).size;
    const roadSet = new Set();
    b.evs.forEach(e => roadCores(e.location).forEach(r => roadSet.add(r)));
    // Centroid-artifact test: a geocoder fallback bucket merges unrelated crashes,
    // so it spans many districts / many distinct roads. A real spot/segment does not.
    const suspect = districts.length >= 3 || roadSet.size >= 4;
    return {
      deaths, events: b.evs.length,
      lat: +(b.evs.reduce((s, e) => s + e.lat, 0) / b.evs.length).toFixed(5),
      lon: +(b.evs.reduce((s, e) => s + e.lon, 0) / b.evs.length).toFixed(5),
      label, districts: districts.slice(0, 2),
      countyZh: lead.countyZh, countyEn: lead.countyEn, countySlug: lead.countySlug,
      yrRange, kind: b.kind,
      isSegment: b.kind === 'road' && uniquePts === 1 && b.evs.length >= 3,
      _suspect: suspect,
      breakdown,
    };
  })
    .filter(h => !h._suspect)   // drop geocoder centroid dumps
    .sort((a, c) => (c.deaths - a.deaths) || (c.events - a.events))
    .slice(0, topN)
    .map(({ _suspect, ...h }) => h);   // strip debug field
}

const out = { modes: ['all', ...MODES.slice(0, 4)], by_mode: {} };
out.by_mode.all = computeHotspots(ALL, 10);
MODES.slice(0, 4).forEach(m => {
  out.by_mode[m] = computeHotspots(ALL.filter(e => e.mode === m), 10);
});

const js = `// AUTO-GENERATED by build_hotspots.js — do not edit by hand.
// The 10 most dangerous road segments nationwide, by victim type, ranked by
// cumulative A1 deaths (2016–2025). Geocoder centroid-dump clusters (events
// spanning many districts/roads at one fallback coordinate) are excluded.
window.NATIONAL_HOTSPOTS = ${JSON.stringify(out, null, 0)};
`;
fs.writeFileSync('data/hotspots_national.js', js);
console.log('events used:', ALL.length, '· file KB:', (js.length / 1024).toFixed(1));
['all', '機車', '汽車', '人', '慢車'].forEach(m => {
  console.log(`\n── TOP 10 · ${m} ──`);
  out.by_mode[m].forEach((h, i) =>
    console.log(`${String(i + 1).padStart(2)}. ${h.deaths}死 ${h.events}件 · ${h.label} · ${h.countyZh} ${h.districts.join('/')} · ${h.yrRange}${h.isSegment ? ' ⚑' : ''}`));
});
