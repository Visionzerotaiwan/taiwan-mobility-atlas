"""Transform the proven Taitung single-city page into a parameterized
city.html?c=<slug> that drives header / map / data from window.CITIES META
and loads data/<slug>.js + data/<slug>.highways.geojson."""
from pathlib import Path

SRC = Path("/Users/yunching0513/Taitung_Mobility/taitung-mobility-atlas/index.html")
DST = Path("/Users/yunching0513/Taitung_Mobility/taiwan-mobility-atlas/city.html")

s = SRC.read_text()

def rep(old, new, required=True):
    global s
    if old not in s:
        if required: raise SystemExit(f"NOT FOUND:\n{old[:120]}")
        return
    s = s.replace(old, new, 1)

# 1. <title>
rep('<title>台東縣交通安全地圖 · Taitung Traffic Safety Map · 2016–2025</title>',
    '<title>台灣交通安全地圖｜各縣市 · Taiwan Mobility Atlas</title>')

# 2. data script tags → cities.js index (data file loaded dynamically by bootstrap)
rep('<script src="taitung_a1.js"></script>\n<script src="district_pop.js"></script>',
    '<script src="data/cities.js"></script>')

# 3. data globals
rep('const DATA = window.TAITUNG_A1 || [];', 'const DATA = window.CITY_A1 || [];')
rep('const YEARLY = window.TAITUNG_YEARLY || [];', 'const YEARLY = window.CITY_YEARLY || [];')
rep('const POP = window.DISTRICT_POP || {};', 'const POP = window.CITY_POP || {};')
rep("const POP_YEAR = window.POPULATION_YEAR || '—';", "const POP_YEAR = '2013';")

# 4. map center/zoom → META
rep('center: [22.9, 121.05],\n    zoom: 9,',
    'center: (window.__META && window.__META.center) || [23.7, 121.0],\n    zoom: (window.__META && window.__META.zoom) || 9,')

# 5. highways path
rep("fetch('highways.geojson')",
    "fetch('data/' + (window.__SLUG || 'taipei') + '.highways.geojson')")

# 6. header block
rep('''<div class="page-header">
  <div class="logo-mark">
    Taitung<br>Mobility<br>Atlas
  </div>
  <div class="title-block">
    <h1>Taitung Traffic Safety Map · 10-year Review 2016 — 2025</h1>
    <div class="title-zh">台東縣交通安全地圖｜十年回顧</div>
  </div>
  <div class="meta">
    A1 Fatal Crash Data<br>
    <strong>民 105 — 114 / 2016 — 2025</strong>
  </div>
</div>''',
'''<div class="page-header">
  <a class="logo-mark" href="./" title="返回全國地圖" style="text-decoration:none;color:inherit">
    ← Taiwan<br>Mobility<br>Atlas
  </a>
  <div class="title-block">
    <h1 id="hdrH1">Traffic Safety Map · 10-year Review 2016 — 2025</h1>
    <div class="title-zh" id="hdrTitleZh">交通安全地圖｜十年回顧</div>
  </div>
  <div class="meta">
    <select id="citySelect" aria-label="選擇縣市"></select><br>
    <span style="font-family:var(--font-en);font-size:9px;letter-spacing:0.18em">A1 · 2016 — 2025</span>
  </div>
</div>''')

# 7. big-label-en id
rep('<div class="big-label-en">Lives lost on Taitung roads · 24 h fatalities · 2016 — 2025</div>',
    '<div class="big-label-en" id="bigLabelEn">Lives lost on these roads · 24 h fatalities · 2016 — 2025</div>')

# 8. insight prose → computed
rep('''      <div class="itext">
        過去十年間，每年約有 <strong id="avgDeaths2">42</strong> 人在台東縣道路上喪生。
        以「事件中最弱勢用路人」為基準：<strong>機車</strong>受害者佔 <strong id="motoCount">226</strong> 件（56%）、
        行人 53 件（13%）、自行車/慢車 15 件（4%）— 合計<strong>弱勢用路人達 73%</strong>。<br>
        2023 年為十年高峰（52 人），2025 年降至 32 人，是否為趨勢翻轉仍需持續觀察。
        <strong>台東市</strong>累計 148 人，遠高於其他鄉鎮，是優先治理區域。
      </div>''',
    '      <div class="itext" id="insightText"></div>')

# 9. Notes prose — make county-name dynamic
rep('篩選發生於台東縣（含原文之「臺東縣」）之事故，年度範圍為民國 105 至 114 年（2016–2025）。',
    '篩選發生於<span id="noteCounty">該縣市</span>之事故，年度範圍為民國 105 至 114 年（2016–2025）。')

# 10. footer
rep('<div>Taitung Mobility Atlas · 01 — Traffic Safety · Designed by 吳昀慶</div>',
    '<div>Taiwan Mobility Atlas · Traffic Safety · Designed by 吳昀慶</div>')

# 10b. null-guard KPI/insight elements that genInsight now owns
rep("""    document.getElementById('avgDeaths').textContent = Math.round(YEARLY.reduce((s,y)=>s+y.deaths,0)/YEARLY.length);
    document.getElementById('avgDeaths2').textContent = Math.round(YEARLY.reduce((s,y)=>s+y.deaths,0)/YEARLY.length);

    const pctMoto = events ? Math.round(moto / events * 100) : 0;
    document.getElementById('motoPct').innerHTML = `${pctMoto}<small>%</small>`;
    document.getElementById('motoCount').textContent = moto;""",
"""    document.getElementById('avgDeaths').textContent = Math.round(YEARLY.reduce((s,y)=>s+y.deaths,0)/YEARLY.length);
    const _ad2 = document.getElementById('avgDeaths2'); if (_ad2) _ad2.textContent = Math.round(YEARLY.reduce((s,y)=>s+y.deaths,0)/YEARLY.length);

    const pctMoto = events ? Math.round(moto / events * 100) : 0;
    const _mp = document.getElementById('motoPct'); if (_mp) _mp.innerHTML = `${pctMoto}<small>%</small>`;
    const _mcEl = document.getElementById('motoCount'); if (_mcEl) _mcEl.textContent = moto;""")

# 11. wrap main IIFE → named function + bootstrap loader
rep('<script>\n(() => {\n  const DATA = window.CITY_A1 || [];',
    '<script>\nfunction __main() {\n  const DATA = window.CITY_A1 || [];')

# Add genInsight call + insight generator inside main, and convert trailing IIFE close.
# Insert genInsight definition + call right before the final fitBounds block.
rep('''  const bounds = L.latLngBounds(filteredOnMap().map(e => [e.lat, e.lon]));
  if (bounds.isValid()) map.fitBounds(bounds, { padding: [24, 24] });
})();
</script>''',
'''  genInsight();
  const bounds = L.latLngBounds(filteredOnMap().map(e => [e.lat, e.lon]));
  if (bounds.isValid()) map.fitBounds(bounds, { padding: [24, 24] });

  function genInsight() {
    const total = DATA.length;
    const deaths = DATA.reduce((s,e)=>s+e.deaths,0);
    const avg = Math.round(deaths / (YEARLY.length || 1));
    const mc = {}; DATA.forEach(e => mc[e.mode] = (mc[e.mode]||0) + 1);
    const moto = mc['機車']||0, ped = mc['人']||0, slow = mc['慢車']||0;
    const vuln = moto + ped + slow;
    const pct = n => total ? Math.round(n/total*100) : 0;
    const peak = YEARLY.reduce((a,b)=> (b.deaths>a.deaths?b:a), YEARLY[0]||{deaths:0,year:'—'});
    const latest = YEARLY[YEARLY.length-1] || {deaths:0,year:'—'};
    const dd = {}; DATA.forEach(e => dd[e.district] = (dd[e.district]||0) + e.deaths);
    const topD = Object.entries(dd).sort((a,b)=>b[1]-a[1])[0] || ['—',0];
    const zh = (window.__META && window.__META.zh) || '該縣市';
    const unitWord = zh.endsWith('市') ? '行政區' : '鄉鎮市區';
    const pe = document.getElementById('motoPct'); if (pe) pe.innerHTML = pct(moto) + '<small>%</small>';
    const el = document.getElementById('insightText');
    if (el) el.innerHTML =
      '過去十年間，每年約有 <strong>' + avg + '</strong> 人在' + zh + '道路上喪生。' +
      '以「事件中最弱勢用路人」為基準：<strong>機車</strong>受害 <strong>' + moto + '</strong> 件（' + pct(moto) + '%）、' +
      '行人 ' + ped + ' 件（' + pct(ped) + '%）、自行車/慢車 ' + slow + ' 件（' + pct(slow) + '%）— ' +
      '合計<strong>弱勢用路人 ' + pct(vuln) + '%</strong>。<br>' +
      '十年高峰為 <strong>' + peak.year + '</strong> 年（' + peak.deaths + ' 人）；最近一年 ' + latest.year + ' 為 ' + latest.deaths + ' 人。' +
      '<strong>' + topD[0] + '</strong>累計 ' + topD[1] + ' 人，為' + zh + unitWord + '之最，是優先治理區域。';
  }
}

// ── Bootstrap: resolve ?c=<slug>, drive header/META, load data, run ──
(function () {
  const CITIES = window.CITIES || [];
  const META = {}; CITIES.forEach(c => META[c.slug] = c);
  const params = new URLSearchParams(location.search);
  let slug = params.get('c') || 'taipei';
  if (!META[slug]) slug = CITIES.length ? CITIES[0].slug : 'taipei';
  const m = META[slug];
  window.__SLUG = slug;
  window.__META = m;

  if (m) {
    document.title = m.zh + '交通安全地圖 · ' + m.en + ' · 2016–2025';
    const h1 = document.getElementById('hdrH1');
    if (h1) h1.textContent = m.en + ' Traffic Safety Map · 10-year Review 2016 — 2025';
    const tz = document.getElementById('hdrTitleZh');
    if (tz) tz.textContent = m.zh + '交通安全地圖｜十年回顧';
    const be = document.getElementById('bigLabelEn');
    if (be) be.textContent = 'Lives lost on ' + m.en + ' roads · 24 h fatalities · 2016 — 2025';
    const nc = document.getElementById('noteCounty');
    if (nc) nc.textContent = m.zh;
  }
  // County switcher (sorted by deaths desc, as CITIES already is)
  const sel = document.getElementById('citySelect');
  if (sel) {
    CITIES.forEach(c => {
      const o = document.createElement('option');
      o.value = c.slug; o.textContent = c.zh + ' (' + c.deaths + ')';
      if (c.slug === slug) o.selected = true;
      sel.appendChild(o);
    });
    sel.addEventListener('change', () => { location.search = '?c=' + sel.value; });
  }
  // Load the county data file, then run the app
  const sc = document.createElement('script');
  sc.src = 'data/' + slug + '.js';
  sc.onload = () => { window.DISTRICT_POP = window.CITY_POP; __main(); };
  sc.onerror = () => {
    document.body.insertAdjacentHTML('afterbegin',
      '<p style="padding:40px;font-family:sans-serif">找不到資料檔：data/' + slug + '.js</p>');
  };
  document.head.appendChild(sc);
})();
</script>''')

DST.write_text(s)
print(f"Wrote city.html ({len(s)} bytes)")

# Leftover audit
import re
leftovers = [l for l in s.splitlines() if 'Taitung' in l or '台東' in l or 'TAITUNG' in l]
print(f"Remaining Taitung/台東 refs: {len(leftovers)}")
for l in leftovers[:10]:
    print("  " + l.strip()[:100])
