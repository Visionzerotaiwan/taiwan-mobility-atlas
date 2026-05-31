"""Add 中/EN language toggle + partner logo to the national choropleth page.

Static text → dual <span class="t-zh">/<span class="t-en"> swapped by CSS on
body.lang-en. Dynamic JS strings → L(zh,en) helper + re-render on toggle.
"""
import re
from pathlib import Path

P = Path("/Users/yunching0513/Taitung_Mobility/taiwan-mobility-atlas/index.html")
s = P.read_text()

def rep(old, new, n=1, required=True):
    global s
    c = s.count(old)
    if c == 0 and required:
        raise SystemExit("NOT FOUND: " + old[:90])
    s = s.replace(old, new, n if n else -1)

def dual(zh, en):
    return f'<span class="t-zh">{zh}</span><span class="t-en">{en}</span>'

# ---------------------------------------------------------------- CSS
rep("</style>", """
/* ── i18n + logo ── */
.t-en { display: none; }
body.lang-en .t-zh { display: none; }
body.lang-en .t-en { display: inline; }
.t-en-b { display: none; }
body.lang-en .t-zh-b { display: none; }
body.lang-en .t-en-b { display: block; }
.lang-toggle {
  position: fixed; top: 14px; right: 14px; z-index: 2000;
  display: flex; border: 1.5px solid var(--black); background: var(--white);
  font-family: var(--font-en); font-size: 11px; font-weight: 600;
  box-shadow: 0 1px 4px rgba(0,0,0,0.12);
}
.lang-toggle .lt-opt { padding: 6px 12px; cursor: pointer; letter-spacing: 0.08em; color: var(--grey-2); }
.lang-toggle .lt-opt.active { background: var(--black); color: var(--white); }
.partner-logos {
  background: var(--white); padding: 36px 24px; text-align: center;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08); margin-top: 56px;
}
.partner-logos .pl-label {
  font-family: var(--font-en); font-size: 9px; letter-spacing: 0.25em;
  text-transform: uppercase; color: var(--grey-2); margin-bottom: 18px;
}
.partner-logos img { max-width: 560px; width: 100%; height: auto; }
</style>""")

# ---------------------------------------------------------------- toggle button
rep('<body>\n<div class="shell">',
    '<body>\n<div class="lang-toggle" id="langToggle"><span class="lt-opt" data-lang="zh">中</span><span class="lt-opt" data-lang="en">EN</span></div>\n<div class="shell">')

# ---------------------------------------------------------------- header
rep('<div class="title-zh">台灣全國交通安全面量圖｜十年回顧</div>',
    '<div class="title-zh">' + dual('台灣全國交通安全面量圖｜十年回顧', 'Taiwan National Road-Safety Choropleth · 10-Year Review') + '</div>')

# ---------------------------------------------------------------- section labels
for zh_full, en in [
    ('01 — Decade Overview 全國十年總覽', '01 — Decade Overview'),
    ('02 — 22 Counties 縣市深度地圖', '02 — 22 Counties'),
    ('03 — District-Level Choropleth 行政區面量圖', '03 — District-Level Choropleth'),
    ('04 — County Choropleth 縣市死亡熱力圖', '04 — County Choropleth'),
    ('05 — Notes 資料說明', '05 — Notes'),
]:
    rep(f'<div class="section-label">{zh_full}</div>',
        f'<div class="section-label">{dual(zh_full, en)}</div>')

# ---------------------------------------------------------------- cover
rep('>17,175<sup>人</sup>', '>17,175<sup>' + dual('人', 'deaths') + '</sup>')
rep('<div class="big-label-zh">十年內全台道路 A1 死亡人數</div>',
    '<div class="big-label-zh">' + dual('十年內全台道路 A1 死亡人數', 'A1 road deaths nationwide, last 10 years') + '</div>')
rep('<div class="span-meta">364 個鄉鎮市區 · 22 個縣市 · 平均每年 1,718 人</div>',
    '<div class="span-meta">' + dual('364 個鄉鎮市區 · 22 個縣市 · 平均每年 1,718 人', '364 districts · 22 counties · ~1,718 deaths per year') + '</div>')
for zh, en in [
    ('A1 死亡事故件數', 'A1 fatal crash events'),
    ('機車為最脆弱用路人', 'Motorcyclist = most-vulnerable party'),
    ('行人受害', 'Pedestrian victims'),
    ('十年累計第一', 'Highest 10-yr total'),
]:
    rep(f'<div class="kpi-zh">{zh}</div>', f'<div class="kpi-zh">{dual(zh, en)}</div>')

# ---------------------------------------------------------------- navigator card
rep('<div class="card-zh">點選任一縣市，進入該地的完整互動地圖（事故點位、熱力圖、優先治理路段、幹線疊圖、逐年趨勢、行政區面量）</div>',
    '<div class="card-zh">' + dual('點選任一縣市，進入該地的完整互動地圖（事故點位、熱力圖、優先治理路段、幹線疊圖、逐年趨勢、行政區面量）',
        'Tap any county to open its full interactive map — crash points, heatmap, priority road segments, highway overlay, yearly trend, district choropleth') + '</div>')

# ---------------------------------------------------------------- filter pills
for zh, en in [
    ('>全部<', '>All<'), ('>機車<', '>Motorcycle<'), ('>汽/貨車<', '>Car/Truck<'),
    ('>行人<', '>Pedestrian<'), ('>自行車/慢車<', '>Bicycle<'),
    ('>每萬人 Per 10k<', '>Per 10k<'), ('>A1 事故數量<', '>A1 events<'),
    ('>A1 死亡數<', '>A1 deaths<'), ('>每十萬人 Per 100k<', '>Per 100k<'),
]:
    zh_inner = zh[1:-1]; en_inner = en[1:-1]
    rep(zh, '>' + dual(zh_inner, en_inner) + '<')

# ---------------------------------------------------------------- district detail empty
rep('''<div class="detail-empty" id="detailEmpty">
        點選任一行政區（區/鄉/鎮/市）以查看分布
        <span class="en">Click a district on the map</span>
      </div>''',
    '''<div class="detail-empty" id="detailEmpty">
        <span class="t-zh">點選任一行政區（區/鄉/鎮/市）以查看分布</span>
        <span class="en t-en" style="display:none">Click a district on the map to inspect</span>
        <span class="en t-zh">Click a district on the map</span>
      </div>''')

# District Detail heading
rep('<h3>District Detail — 行政區明細</h3>',
    '<h3>District Detail' + dual('<span class="t-zh"> — 行政區明細</span>'.replace('<span class="t-zh">','').replace('</span>',''), '') + '</h3>')
# simpler: wrap the ZH appendage only
s = s.replace('<h3>District Detail<span class="t-zh"></span><span class="t-en"></span></h3>',
              '<h3>District Detail<span class="t-zh"> — 行政區明細</span></h3>')

# ---------------------------------------------------------------- county card
rep('<h4>Ranking · 全 22 縣市</h4>',
    '<h4>Ranking<span class="t-zh"> · 全 22 縣市</span><span class="t-en"> · all 22 counties</span></h4>')
rep('<div class="card-zh">點選縣市進入完整地圖 · 顏色＝當前指標、長條＝相對比例</div>',
    '<div class="card-zh">' + dual('點選縣市進入完整地圖 · 顏色＝當前指標、長條＝相對比例',
        'Tap a county for its full map · colour = current metric, bar = relative scale') + '</div>')
rep('<div class="card-zh">關於本面量圖</div>',
    '<div class="card-zh">' + dual('關於本面量圖', 'About this choropleth') + '</div>')

# ---------------------------------------------------------------- notes paragraphs (block dual)
NOTES = [
    ('''<p style="font-size:13px;font-weight:300;line-height:1.85;color:var(--grey-1);max-width:780px">
      本面量圖整理自<strong>內政部警政署 A1 級道路交通事故</strong>公開資料，
      涵蓋年度民國 105 至 114 年（2016–2025），共 16,713 件事件、17,175 人死亡，
      分布於 364 個鄉鎮市區（22 個縣市）。
    </p>''',
     '''<p class="t-en-b" style="font-size:13px;font-weight:300;line-height:1.85;color:var(--grey-1);max-width:780px">
      Built from the <strong>National Police Agency A1 (fatal) road-crash</strong> open dataset,
      covering 2016–2025 — 16,713 events, 17,175 deaths, across 364 districts (22 counties).
    </p>'''),
    ('''<p style="font-size:13px;font-weight:300;line-height:1.85;color:var(--grey-1);max-width:780px;margin-top:10px">
      <strong>受害者運具邏輯</strong>：每筆事件以其中<strong>最脆弱用路人</strong>之運具為類別
      （優先序：行人 &gt; 自行車/慢車 &gt; 機車 &gt; 汽/貨車）。例如左轉小客車撞死行人，
      在原資料 P1 為駕駛、運具為汽車，本地圖會歸類為「行人」。
    </p>''',
     '''<p class="t-en-b" style="font-size:13px;font-weight:300;line-height:1.85;color:var(--grey-1);max-width:780px;margin-top:10px">
      <strong>Victim-mode logic</strong>: each event is classified by its <strong>most-vulnerable road user</strong>
      (priority: pedestrian &gt; bicycle/slow vehicle &gt; motorcycle &gt; car/truck). E.g. a left-turning car that
      kills a pedestrian is recorded with the driver as party-1 (a car) in the raw data, but is classified here as “pedestrian”.
    </p>'''),
    ('''<p style="font-size:13px;font-weight:300;line-height:1.85;color:var(--grey-1);max-width:780px;margin-top:10px">
      <strong>每萬人率</strong>：採用<strong>戶政司 dataset 8410 民國 102 年</strong>之人口數作為分母，
      可呈現「不只看絕對數量，而是相對風險」之治理優先序。2013 vs 2025 期間人口分布變化有限，
      適用於相對比較。
    </p>''',
     '''<p class="t-en-b" style="font-size:13px;font-weight:300;line-height:1.85;color:var(--grey-1);max-width:780px;margin-top:10px">
      <strong>Per-capita rates</strong> use population from <strong>MOI Household-Registration dataset 8410 (2013)</strong>
      as the denominator, surfacing relative risk rather than raw counts. Population shifts 2013→2025 are modest, so the
      comparison holds.
    </p>'''),
    ('''<p style="font-size:13px;font-weight:300;line-height:1.85;color:var(--grey-1);max-width:780px;margin-top:10px">
      <strong>邊界圖資</strong>：依 g0v/twgeojson 之鄉鎮市區界（1982 年版，整併至 2014 年後行政地理）。
      連江縣東引鄉與台東縣綠島鄉等少數島嶼之邊界與資料皆有侷限。
    </p>''',
     '''<p class="t-en-b" style="font-size:13px;font-weight:300;line-height:1.85;color:var(--grey-1);max-width:780px;margin-top:10px">
      <strong>Boundaries</strong> from g0v/twgeojson district polygons (1982 edition, normalised to post-2014 administrative
      geography). A few small islands (Lienchiang–Dongyin, Taitung–Green Island) have limited boundary/data coverage.
    </p>'''),
]
for zh_p, en_p in NOTES:
    # mark the zh <p> as t-zh-b and append the en <p> after it
    zh_marked = zh_p.replace('<p style=', '<p class="t-zh-b" style=', 1)
    rep(zh_p, zh_marked + '\n' + en_p)

# ---------------------------------------------------------------- footer tag + partner logo
rep('<span class="tag lime">面量圖</span>',
    '<span class="tag lime">' + dual('面量圖', 'Choropleth') + '</span>')

rep('<footer>', '''<div class="partner-logos">
  <div class="pl-label t-zh">資料夥伴 · 合作單位</div>
  <div class="pl-label t-en" style="display:none">In partnership with</div>
  <img src="assets/tcan_vzt_logo.png" alt="TCAN 台灣氣候行動網路 · Vision Zero Taiwan 還路於民行人路權促進會">
</div>

<footer>''')

# ================================================================ JS
# L() helper + lang bootstrap, injected right after <body>'s first app <script> opens.
# Place a global lang module before the navigator IIFE.
rep('<script src="data/cities.js"></script>\n<script>',
    '''<script src="data/cities.js"></script>
<script>
// ── i18n core ──
window.__LANG = (function(){ try { return localStorage.getItem('lang') || 'zh'; } catch(e){ return 'zh'; } })();
function L(zh, en) { return window.__LANG === 'en' ? en : zh; }
function setLang(l) {
  window.__LANG = l;
  document.body.classList.toggle('lang-en', l === 'en');
  document.documentElement.lang = l === 'en' ? 'en' : 'zh-TW';
  try { localStorage.setItem('lang', l); } catch(e) {}
  document.querySelectorAll('#langToggle .lt-opt').forEach(o => o.classList.toggle('active', o.dataset.lang === l));
  if (window.__renderNav) window.__renderNav();
  if (window.__rerender) window.__rerender();
}
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('#langToggle .lt-opt').forEach(o =>
    o.addEventListener('click', () => setLang(o.dataset.lang)));
  setLang(window.__LANG);
});
</script>
<script>''')

# Navigator → expose as window.__renderNav
rep('''(function () {
  const CITIES = window.CITIES || [];
  window.__COUNTY2SLUG = {};
  CITIES.forEach(c => { window.__COUNTY2SLUG[c.zh] = c.slug; });
  const grid = document.getElementById('navGrid');
  if (!grid || !CITIES.length) return;
  const maxD = Math.max(...CITIES.map(c => c.deaths), 1);
  grid.innerHTML = CITIES.map(c =>
    `<a class="nav-chip" href="city.html?c=${c.slug}">
       <span class="nc-zh">${c.zh}</span>
       <span class="nc-en">${c.en}</span>
       <span class="nc-deaths">${c.deaths.toLocaleString()} 死 · ${c.events.toLocaleString()} 件</span>
       <span class="nc-bar"><span class="nc-fill" style="width:${c.deaths/maxD*100}%"></span></span>
     </a>`
  ).join('');
})();''',
'''(function () {
  const CITIES = window.CITIES || [];
  window.__COUNTY2SLUG = {};
  CITIES.forEach(c => { window.__COUNTY2SLUG[c.zh] = c.slug; });
  const grid = document.getElementById('navGrid');
  if (!grid || !CITIES.length) return;
  const maxD = Math.max(...CITIES.map(c => c.deaths), 1);
  window.__renderNav = function () {
    grid.innerHTML = CITIES.map(c =>
      `<a class="nav-chip" href="city.html?c=${c.slug}">
         <span class="nc-zh">${window.__LANG === 'en' ? c.en : c.zh}</span>
         <span class="nc-en">${window.__LANG === 'en' ? c.zh : c.en}</span>
         <span class="nc-deaths">${L(c.deaths.toLocaleString()+' 死 · '+c.events.toLocaleString()+' 件', c.deaths.toLocaleString()+' deaths · '+c.events.toLocaleString()+' events')}</span>
         <span class="nc-bar"><span class="nc-fill" style="width:${c.deaths/maxD*100}%"></span></span>
       </a>`
    ).join('');
  };
  window.__renderNav();
})();''')

# ---- dynamic strings in main app ----
rep("`Quintile · ${state.metric === 'rate' ? '每萬人 A1 事故' : 'A1 事故數量'}`;",
    "`Quintile · ${state.metric === 'rate' ? L('每萬人 A1 事故','A1 events per 10k') : L('A1 事故數量','A1 events')}`;")

rep("""        ? `${districts.features.length} districts shown`
        : `${totalShown.toLocaleString()} 件 A1 事故${state.mode==='all' && state.year==='all' ? '' : '（篩選後）'}`;""",
"""        ? `${districts.features.length} ${L('行政區','districts')}`
        : `${totalShown.toLocaleString()} ${L('件 A1 事故','A1 events')}${state.mode==='all' && state.year==='all' ? '' : L('（篩選後）',' (filtered)')}`;""")

rep("`Quintile · ${countyState.metric === 'per100k' ? '每十萬人死亡' : 'A1 死亡數'}`;",
    "`Quintile · ${countyState.metric === 'per100k' ? L('每十萬人死亡','Deaths per 100k') : L('A1 死亡數','A1 deaths')}`;")

rep("""    document.getElementById('countyStat').textContent =
      `全國 ${totDeaths.toLocaleString()} 死 · ${natRate.toFixed(1)} / 10萬`;""",
"""    document.getElementById('countyStat').textContent =
      L(`全國 ${totDeaths.toLocaleString()} 死 · ${natRate.toFixed(1)} / 10萬`, `Nationwide ${totDeaths.toLocaleString()} deaths · ${natRate.toFixed(1)} per 100k`);""")

# county ranking row rate sub-label
rep("<div class=\"c-rate\">${r.rate.toFixed(1)}<small>/10萬 · ${r.deaths} 死</small></div>",
    "<div class=\"c-rate\">${r.rate.toFixed(1)}<small>${L('/10萬 · '+r.deaths+' 死', '/100k · '+r.deaths+' d')}</small></div>")

# county tooltip
rep("""          `<strong>${cy}</strong><br>${d.toLocaleString()} 死 · ${r.toFixed(1)} / 10萬` +
          `<br><span style="opacity:.7;font-family:'Space Grotesk';font-size:10px">人口 ${p.toLocaleString()} · 點選進入</span>`,""",
"""          `<strong>${cy}</strong><br>` + L(`${d.toLocaleString()} 死 · ${r.toFixed(1)} / 10萬`, `${d.toLocaleString()} deaths · ${r.toFixed(1)} per 100k`) +
          `<br><span style="opacity:.7;font-family:'Space Grotesk';font-size:10px">` + L(`人口 ${p.toLocaleString()} · 點選進入`, `pop ${p.toLocaleString()} · click to open`) + `</span>`,""")

# district tooltip
rep("""        const label = state.metric === 'rate'
          ? `${v.toFixed(2)} / 萬`
          : `${v} 件`;""",
"""        const label = state.metric === 'rate'
          ? `${v.toFixed(2)} ${L('/ 萬','/10k')}`
          : `${v} ${L('件','events')}`;""")
rep("(pop ? `<br><span style=\"opacity:0.7;font-family:'Space Grotesk';font-size:10px\">人口 ${pop.toLocaleString()}</span>` : ''),",
    "(pop ? `<br><span style=\"opacity:0.7;font-family:'Space Grotesk';font-size:10px\">${L('人口','pop')} ${pop.toLocaleString()}</span>` : ''),")

# renderDetail strings
rep("""        <div class="detail-county">${county} · No A1 fatalities recorded</div>
        ${pop ? `<div style="font-size:11px;color:var(--grey-2);">人口 ${pop.toLocaleString()}</div>` : ''}
        ${countyLink}""",
"""        <div class="detail-county">${county} · ${L('查無 A1 死亡紀錄','No A1 fatalities recorded')}</div>
        ${pop ? `<div style="font-size:11px;color:var(--grey-2);">${L('人口','pop')} ${pop.toLocaleString()}</div>` : ''}
        ${countyLink}""")
rep("? `<a class=\"detail-link\" href=\"city.html?c=${slug}\">前往 ${county} 完整地圖 →</a>`",
    "? `<a class=\"detail-link\" href=\"city.html?c=${slug}\">${L('前往 '+county+' 完整地圖 →','Open '+county+' full map →')}</a>`")
rep("<div class=\"detail-county\">${county} · ${pop ? pop.toLocaleString() + ' 人' : 'population N/A'}</div>",
    "<div class=\"detail-county\">${county} · ${pop ? pop.toLocaleString() + L(' 人',' people') : L('人口從缺','population N/A')}</div>")
rep("<div class=\"stat-val\">${totalDeaths}<small>人</small></div>",
    "<div class=\"stat-val\">${totalDeaths}<small>${L('人','deaths')}</small></div>")
rep("<div class=\"stat-val\">${totalEvents}<small>件</small></div>",
    "<div class=\"stat-val\">${totalEvents}<small>${L('件','events')}</small></div>")
rep("<div class=\"stat-val\">${rate != null ? rate.toFixed(2) : '—'}<small>/萬</small></div>",
    "<div class=\"stat-val\">${rate != null ? rate.toFixed(2) : '—'}<small>${L('/萬','/10k')}</small></div>")

# expose __rerender after recompute defs (hook at the final init calls)
rep("""  recompute();
  recomputeCounty();
  // County map needs a size invalidation once laid out
  setTimeout(() => countyMap.invalidateSize(), 200);""",
"""  window.__rerender = () => { recompute(); recomputeCounty(); };
  recompute();
  recomputeCounty();
  // County map needs a size invalidation once laid out
  setTimeout(() => countyMap.invalidateSize(), 200);""")

P.write_text(s)
print("national i18n applied;", len(s), "bytes")
# leftover audit: stray empty dual spans
import re as _re
bad = _re.findall(r'<span class="t-zh"></span>', s)
print("empty t-zh spans:", len(bad))
