"""Add 中/EN toggle + partner logo to the parameterized county page (city.html)."""
from pathlib import Path

P = Path("/Users/yunching0513/Taitung_Mobility/taiwan-mobility-atlas/city.html")
s = P.read_text()

def rep(old, new, required=True):
    global s
    if old not in s:
        if required: raise SystemExit("NOT FOUND:\n" + old[:120])
        return
    s = s.replace(old, new, 1)

def dual(zh, en):
    return f'<span class="t-zh">{zh}</span><span class="t-en">{en}</span>'

# ---------------- CSS ----------------
rep("</style>", """
/* ── i18n + logo ── */
.t-en { display: none; }
body.lang-en .t-zh { display: none; }
body.lang-en .t-en { display: inline; }
.t-en-b { display: none; }
body.lang-en .t-zh-b { display: none; }
body.lang-en .t-en-b { display: block; }
body.lang-en #hdrTitleZh { display: none; }
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

# ---------------- toggle button ----------------
rep('<body>\n<div class="shell">',
    '<body>\n<div class="lang-toggle" id="langToggle"><span class="lt-opt" data-lang="zh">中</span><span class="lt-opt" data-lang="en">EN</span></div>\n<div class="shell">')

# ---------------- section labels ----------------
for zh_full, en in [
    ('01 — Decade Overview 十年總覽', '01 — Decade Overview'),
    ('02 — Year-over-Year 逐年趨勢', '02 — Year-over-Year'),
    ('03 — Spatial Distribution 空間分布', '03 — Spatial Distribution'),
    ('04 — Headline Finding 關鍵發現', '04 — Headline Finding'),
    ('05 — Breakdown 多維拆解', '05 — Breakdown'),
    ('06 — Notes 資料說明', '06 — Notes'),
]:
    rep(f'<div class="section-label">{zh_full}</div>',
        f'<div class="section-label">{dual(zh_full, en)}</div>')

# ---------------- cover ----------------
rep('<div class="big-num" id="bigDeaths">419<sup>人</sup></div>',
    '<div class="big-num" id="bigDeaths">419<sup>' + dual('人','deaths') + '</sup></div>')
rep('<div class="big-label-zh">十年內因交通事故失去的生命</div>',
    '<div class="big-label-zh">' + dual('十年內因交通事故失去的生命','Lives lost to road crashes over 10 years') + '</div>')
rep('<div class="span-meta">平均每年 <strong id="avgDeaths">42</strong> 人；最高為 <strong id="peakYear">2023</strong> 年 <strong id="peakDeaths">52</strong> 人</div>',
    '<div class="span-meta"><span class="t-zh">平均每年 <strong id="avgDeaths">42</strong> 人；最高為 <strong id="peakYear">2023</strong> 年 <strong id="peakDeaths">52</strong> 人</span>'
    '<span class="t-en" style="display:none">avg <strong>42</strong>/yr · peak <strong>2023</strong> at <strong>52</strong></span></div>')
for zh, en in [
    ('A1 死亡事故件數', 'A1 fatal crash events'),
    ('機車為主要事故方', 'Motorcyclist victims'),
    ('行人事故', 'Pedestrian victims'),
    ('2025 年死亡人數', '2025 deaths'),
]:
    rep(f'<div class="kpi-zh">{zh}</div>', f'<div class="kpi-zh">{dual(zh, en)}</div>')
rep('<div class="kpi-num" id="kMoto">226<small>件</small></div>',
    '<div class="kpi-num" id="kMoto">226<small>' + dual('件','ev') + '</small></div>')
rep('<div class="kpi-num" id="kPed">—<small>件</small></div>',
    '<div class="kpi-num" id="kPed">—<small>' + dual('件','ev') + '</small></div>')
rep('<div class="kpi-num" id="kLatest">32<small>人</small></div>',
    '<div class="kpi-num" id="kLatest">32<small>' + dual('人','d') + '</small></div>')

# ---------------- year-over-year ----------------
rep('<div class="card-zh">2016 – 2025 死亡事故件數與死亡人數年度變化</div>',
    '<div class="card-zh">' + dual('2016 – 2025 死亡事故件數與死亡人數年度變化','Annual crash events & deaths, 2016 – 2025') + '</div>')
rep('<div class="item"><span class="swatch" style="background:#C8D400;height:6px"></span>事故件數 Events</div>',
    '<div class="item"><span class="swatch" style="background:#C8D400;height:6px"></span>' + dual('事故件數 Events','Events') + '</div>')
rep('<div class="item dashed"><span class="swatch"></span>死亡人數 Deaths</div>',
    '<div class="item dashed"><span class="swatch"></span>' + dual('死亡人數 Deaths','Deaths') + '</div>')
rep('<div class="card-zh">年度受害者運具組成（最弱勢用路人）</div>',
    '<div class="card-zh">' + dual('年度受害者運具組成（最弱勢用路人）','Annual victim-mode composition (most-vulnerable user)') + '</div>')
for zh, en in [('機車','Motorcycle'),('汽/貨車','Car/Truck'),('行人','Pedestrian'),('慢車','Bicycle'),('其他','Other')]:
    rep(f'height:10px"></span>{zh}</div>', f'height:10px"></span>{dual(zh, en)}</div>')
rep('<div class="card-zh">最新年度數字（與十年平均比較）</div>',
    '<div class="card-zh">' + dual('最新年度數字（與十年平均比較）','Latest year vs the 10-year average') + '</div>')
rep('<div class="card-zh">十年內各鄉鎮市死亡人數熱力圖（深色＝該年死亡人數較高）</div>',
    '<div class="card-zh">' + dual('十年內各鄉鎮市死亡人數熱力圖（深色＝該年死亡人數較高）','District × year death heatmap (darker = more deaths that year)') + '</div>')
rep('Scale · 顏色由淺至深表示該年死亡人數 0 → 10+',
    dual('Scale · 顏色由淺至深表示該年死亡人數 0 → 10+','Scale · light → dark = 0 → 10+ deaths that year'))

# ---------------- spatial: pills / legend ----------------
rep('title="2016 年無經緯度資料"', 'title="No coordinates for 2016"')
rep('title="2017 年無經緯度資料"', 'title="No coordinates for 2017"')
for zh, en in [('>全部<','>All<'), ('>機車<','>Motorcycle<'), ('>汽/貨車<','>Car/Truck<'),
               ('>行人<','>Pedestrian<'), ('>自行車/慢車<','>Bicycle<')]:
    rep(zh, '>' + dual(zh[1:-1], en[1:-1]) + '<')
rep('<span class="cat-pill active" data-view="points">點位 Points</span>',
    '<span class="cat-pill active" data-view="points">' + dual('點位 Points','Points') + '</span>')
rep('<span class="cat-pill" data-view="heat">熱力 Heatmap</span>',
    '<span class="cat-pill" data-view="heat">' + dual('熱力 Heatmap','Heatmap') + '</span>')
rep('<span class="cat-pill" data-view="both">兩者 Both</span>',
    '<span class="cat-pill" data-view="both">' + dual('兩者 Both','Both') + '</span>')
rep('<span class="cat-pill" data-base="minimal">簡潔</span>',
    '<span class="cat-pill" data-base="minimal">' + dual('簡潔','Minimal') + '</span>')
rep('<span class="cat-pill active" data-base="roads">道路</span>',
    '<span class="cat-pill active" data-base="roads">' + dual('道路','Roads') + '</span>')
rep('<span class="cat-pill" data-base="satellite">衛星</span>',
    '<span class="cat-pill" data-base="satellite">' + dual('衛星','Satellite') + '</span>')
rep('<span class="cat-pill active" data-hwy="on">顯示</span>',
    '<span class="cat-pill active" data-hwy="on">' + dual('顯示','Show') + '</span>')
rep('<span class="cat-pill" data-hwy="off">隱藏</span>',
    '<span class="cat-pill" data-hwy="off">' + dual('隱藏','Hide') + '</span>')
for zh, en in [('機車 Motorcycle','Motorcycle'),('汽/貨車 Car/Truck','Car/Truck'),
               ('行人 Pedestrian','Pedestrian'),('慢車 Bicycle','Bicycle'),('其他 Other','Other')]:
    rep(f'</span>{zh}</div>', '</span>' + dual(zh, en) + '</div>')
rep('margin-right:2px"></span>國道</div>', 'margin-right:2px"></span>' + dual('國道','Freeway') + '</div>')
rep('margin-right:2px"></span>快速公路</div>', 'margin-right:2px"></span>' + dual('快速公路','Expressway') + '</div>')
rep('margin-right:2px"></span>省道</div>', 'margin-right:2px"></span>' + dual('省道','Provincial Hwy') + '</div>')

# event detail empty
rep('<h3>Event Detail — 事件明細</h3>', '<h3>Event Detail<span class="t-zh"> — 事件明細</span></h3>')
rep('點選地圖上任一圓點以查看事故細節',
    '<span class="t-zh">點選地圖上任一圓點以查看事故細節</span><span class="t-en" style="display:none">Click any dot on the map for crash details</span>')

# hotspots header
rep('Top Hotspots · 優先治理路段', 'Top Hotspots<span class="t-zh"> · 優先治理路段</span>')
rep('能解析道路名稱與里程者以「~3 公里路段」聚合（標記 ⚑ 路段）；其餘以 ~300 公尺方格聚合。依累計死亡人數排序前 10 名。點選列可在地圖上定位。',
    '<span class="t-zh">能解析道路名稱與里程者以「~3 公里路段」聚合（標記 ⚑ 路段）；其餘以 ~300 公尺方格聚合。依累計死亡人數排序前 10 名。點選列可在地圖上定位。</span>'
    '<span class="t-en" style="display:none">Locations with a road name + km are clustered into ~3 km segments (marked ⚑); others into ~300 m cells. Top 10 by cumulative deaths. Click a row to locate it.</span>')

# insight label
rep('<div class="ilabel-en">Key Insight · 整體觀察</div>',
    '<div class="ilabel-en">Key Insight<span class="t-zh"> · 整體觀察</span></div>')

# breakdown subtitles + sort pills
rep('<div class="card-zh">各行政區死亡人數（全部，可滾動）</div>',
    '<div class="card-zh">' + dual('各行政區死亡人數（全部，可滾動）','Deaths by district (all, scrollable)') + '</div>')
rep('<span class="pill active" data-sort="abs">累計 Total</span>',
    '<span class="pill active" data-sort="abs">' + dual('累計 Total','Total') + '</span>')
rep('<span class="pill" data-sort="rate">每萬人 Per 10k</span>',
    '<span class="pill" data-sort="rate">' + dual('每萬人 Per 10k','Per 10k') + '</span>')
rep('<div class="card-zh">受害者運具類別（取事件中最弱勢用路人）</div>',
    '<div class="card-zh">' + dual('受害者運具類別（取事件中最弱勢用路人）','Victim mode (most-vulnerable user per event)') + '</div>')
rep('<div class="card-zh">道路類別 · 僅 2018+ 資料</div>',
    '<div class="card-zh">' + dual('道路類別 · 僅 2018+ 資料','Road class · 2018+ only') + '</div>')
rep('<div class="card-zh">事故發生時光線狀況 · 僅 2018+</div>',
    '<div class="card-zh">' + dual('事故發生時光線狀況 · 僅 2018+','Lighting at time of crash · 2018+') + '</div>')
rep('<div class="card-zh">事故發生時段（24 小時分布）</div>',
    '<div class="card-zh">' + dual('事故發生時段（24 小時分布）','Time of day (24-hour distribution)') + '</div>')
rep('<div class="card-zh">事故發生月份</div>',
    '<div class="card-zh">' + dual('事故發生月份','Month of crash') + '</div>')

# notes (block dual)
rep('<div class="card-zh" style="margin-bottom:14px">關於本地圖</div>',
    '<div class="card-zh" style="margin-bottom:14px">' + dual('關於本地圖','About this map') + '</div>')
NOTE1_ZH = '''<p style="font-size:13px;font-weight:300;line-height:1.85;color:var(--grey-1);max-width:780px">
      本地圖整理自<strong>內政部警政署 A1 級道路交通事故</strong>公開資料，
      篩選發生於<span id="noteCounty">該縣市</span>之事故，年度範圍為民國 105 至 114 年（2016–2025）。
      A1 為「造成人員當場或 24 小時內死亡」之事故等級，每筆事件可能涉及多位當事人。
    </p>'''
NOTE1_EN = '''<p class="t-en-b" style="font-size:13px;font-weight:300;line-height:1.85;color:var(--grey-1);max-width:780px">
      Compiled from the <strong>National Police Agency A1 (fatal) road-crash</strong> open dataset, filtered to crashes in
      <span id="noteCountyEn">this county</span>, covering 2016–2025. A1 = a crash where someone died on the spot or within 24 hours;
      each event may involve several parties.
    </p>'''
rep(NOTE1_ZH, NOTE1_ZH.replace('<p style=', '<p class="t-zh-b" style=', 1) + '\n' + NOTE1_EN)

NOTE2_ZH = '''<p style="font-size:13px;font-weight:300;line-height:1.85;color:var(--grey-1);max-width:780px;margin-top:10px">
      不同年度的資料完整度不同：<strong>2016、2017、2021</strong> 為「簡式」欄位
      （僅含時間、地點、傷亡、車種），<strong>2018、2019、2020、2022 — 2025</strong> 為完整欄位
      （含天候、光線、道路類別、肇因等）；<strong>2016 與 2017</strong> 完全無經緯度資訊，
      故地圖僅顯示 2018 年後之事件，但所有年份皆納入趨勢與時間／月份分布之統計。
    </p>'''
NOTE2_EN = '''<p class="t-en-b" style="font-size:13px;font-weight:300;line-height:1.85;color:var(--grey-1);max-width:780px;margin-top:10px">
      Field completeness varies by year: <strong>2016, 2017, 2021</strong> use a simplified schema (time, place, casualties, vehicle only);
      <strong>2018–2020, 2022–2025</strong> are full (weather, lighting, road class, cause, …). <strong>2016 & 2017</strong> have no coordinates,
      so the map shows 2018+ events only — but all years count in the trend and time/month sections.
    </p>'''
rep(NOTE2_ZH, NOTE2_ZH.replace('<p style=', '<p class="t-zh-b" style=', 1) + '\n' + NOTE2_EN)

NOTE3_ZH = '''<p style="font-size:13px;font-weight:300;line-height:1.85;color:var(--grey-1);max-width:780px;margin-top:10px">
      <strong>「運具類別」採用受害者邏輯</strong>：每筆事件以其中<strong>最弱勢用路人</strong>之運具為類別
      （優先序：行人 &gt; 自行車/慢車 &gt; 機車 &gt; 汽/貨車）。這與 A1 原始資料的「當事者順位 P1」不同 ——
      左轉小客車撞死行人之案件，P1 是駕駛、運具為汽車，但本地圖會把該事件歸類為「行人」。
      此調整反映「誰真正在道路上喪生」之問題，與政策關切的「弱勢用路人保護」一致。
      原始 P1 分類保留於每筆事件的 <code style="font-family:var(--font-en);font-size:11px;background:var(--grey-4);padding:1px 4px">principal_mode</code> 欄位。
    </p>'''
NOTE3_EN = '''<p class="t-en-b" style="font-size:13px;font-weight:300;line-height:1.85;color:var(--grey-1);max-width:780px;margin-top:10px">
      <strong>Victim-based mode</strong>: each event is classified by its <strong>most-vulnerable road user</strong>
      (priority: pedestrian &gt; bicycle/slow vehicle &gt; motorcycle &gt; car/truck) — unlike the raw "party-1" field. A left-turning car
      that kills a pedestrian has the driver (a car) as party-1 in the raw data, but is classified here as "pedestrian." This answers
      "who actually dies on the road," matching the policy focus on protecting vulnerable users. The original party-1 class is kept in each
      event's <code style="font-family:var(--font-en);font-size:11px;background:var(--grey-4);padding:1px 4px">principal_mode</code> field.
    </p>'''
rep(NOTE3_ZH, NOTE3_ZH.replace('<p style=', '<p class="t-zh-b" style=', 1) + '\n' + NOTE3_EN)

NOTE4_ZH = '''<p style="font-size:13px;font-weight:300;line-height:1.85;color:var(--grey-1);max-width:780px;margin-top:10px">
      <strong>幹線道路圖層</strong>：地圖上的紅／橙／藍線為國道、快速公路、省道，
      資料來源為<strong>交通部公路局 ROAD_國省道(含快速公路)_1150409 圖資</strong>
      （TWD97/TM2 經緯度轉換、Douglas-Peucker 15m 簡化）。可在地圖上方「幹線 Hwys」按鈕切換顯示與隱藏。
    </p>'''
NOTE4_EN = '''<p class="t-en-b" style="font-size:13px;font-weight:300;line-height:1.85;color:var(--grey-1);max-width:780px;margin-top:10px">
      <strong>Highway overlay</strong>: red/orange/blue lines are national freeways, expressways and provincial highways, from the
      <strong>MOTC Highway Bureau ROAD_國省道(含快速公路)_1150409</strong> dataset (TWD97/TM2 → WGS84, Douglas-Peucker 15 m). Toggle via the
      "幹線 Hwys" buttons above the map.
    </p>'''
rep(NOTE4_ZH, NOTE4_ZH.replace('<p style=', '<p class="t-zh-b" style=', 1) + '\n' + NOTE4_EN)

# footer tags
rep('<span class="tag lime">交通安全</span>', '<span class="tag lime">' + dual('交通安全','Traffic Safety') + '</span>')
rep('<span class="tag">十年回顧</span>', '<span class="tag">' + dual('十年回顧','10-Year Review') + '</span>')

# partner logo before footer
rep('<footer>', '''<div class="partner-logos">
  <div class="pl-label t-zh">資料夥伴 · 合作單位</div>
  <div class="pl-label t-en" style="display:none">In partnership with</div>
  <img src="assets/tcan_vzt_logo.png" alt="TCAN 台灣氣候行動網路 · Vision Zero Taiwan 還路於民行人路權促進會">
</div>

<footer>''')

# ================= JS =================
# i18n core (define TT before main + bootstrap). Insert after data/cities.js tag.
rep('<script src="data/cities.js"></script>\n<script>',
    '''<script src="data/cities.js"></script>
<script>
window.__LANG = (function(){ try { return localStorage.getItem('lang') || 'zh'; } catch(e){ return 'zh'; } })();
function TT(zh, en) { return window.__LANG === 'en' ? en : zh; }
function setLang(l) {
  window.__LANG = l;
  document.body.classList.toggle('lang-en', l === 'en');
  document.documentElement.lang = l === 'en' ? 'en' : 'zh-TW';
  try { localStorage.setItem('lang', l); } catch(e) {}
  document.querySelectorAll('#langToggle .lt-opt').forEach(o => o.classList.toggle('active', o.dataset.lang === l));
  if (window.__buildSelect) window.__buildSelect();
  if (window.__rerender) window.__rerender();
}
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('#langToggle .lt-opt').forEach(o =>
    o.addEventListener('click', () => setLang(o.dataset.lang)));
  setLang(window.__LANG);
});
</script>
<script>''')

# --- snapshot rows ---
rep("['事故件數 Events', latest.events, avg('events')],",
    "[TT('事故件數','Events'), latest.events, avg('events')],")
rep("['死亡人數 Deaths', latest.deaths, avg('deaths')],",
    "[TT('死亡人數','Deaths'), latest.deaths, avg('deaths')],")
rep("['機車主因 Motorcycle', latest.by_mode['機車']||0, Math.round(YEARLY.reduce((s,y)=>s+(y.by_mode['機車']||0),0)/YEARLY.length)],",
    "[TT('機車主因','Motorcycle'), latest.by_mode['機車']||0, Math.round(YEARLY.reduce((s,y)=>s+(y.by_mode['機車']||0),0)/YEARLY.length)],")

# snapshot footer
rep('十年高峰：<strong style="color:#1A1A1A">${peak.year} 年 · ${peak.deaths} 人</strong><br>',
    "${TT('十年高峰：','Decade peak: ')}<strong style=\"color:#1A1A1A\">${peak.year}${TT(' 年 · ',' · ')}${peak.deaths}${TT(' 人',' deaths')}</strong><br>")
rep("最近一年較十年平均<span style=\"color:${latest.deaths<avg('deaths')?'#A8B200':'#D94F3D'};font-weight:500\"> ${latest.deaths<avg('deaths')?'低':'高'} ${Math.abs(latest.deaths-avg('deaths'))} 人</span>。",
    "${TT('最近一年較十年平均','Latest year vs 10-yr avg:')}<span style=\"color:${latest.deaths<avg('deaths')?'#A8B200':'#D94F3D'};font-weight:500\"> ${latest.deaths<avg('deaths')?TT('低','−'):TT('高','+')} ${Math.abs(latest.deaths-avg('deaths'))}${TT(' 人',' deaths')}</span>。")

# header labels (snapshot Metric/2025/10y avg header row) — find the EN-ish header cells
rep(">Metric</div>", ">Metric</div>", required=False)

# hotspots empty + rows
rep("el.innerHTML = '<div style=\"font-size:11px;color:#888;padding:24px 0;font-weight:300\">— 篩選條件下無熱點資料 —</div>';",
    "el.innerHTML = `<div style=\"font-size:11px;color:#888;padding:24px 0;font-weight:300\">— ${TT('篩選條件下無熱點資料','No hotspots under this filter')} —</div>`;")
rep("'<span style=\"margin-left:8px;font-family:var(--font-en);font-size:8.5px;letter-spacing:0.15em;color:var(--gold);text-transform:uppercase\">⚑ 路段</span>'",
    "'<span style=\"margin-left:8px;font-family:var(--font-en);font-size:8.5px;letter-spacing:0.15em;color:var(--gold);text-transform:uppercase\">⚑ '+TT('路段','segment')+'</span>'")
rep('<div class="meta">${h.sublabel}<span class="sep">·</span>${h.events} 件<span class="sep">·</span>${h.yrRange}</div>',
    '<div class="meta">${h.sublabel}<span class="sep">·</span>${h.events} ${TT(\'件\',\'ev\')}<span class="sep">·</span>${h.yrRange}</div>')
rep('<div class="deaths">${h.deaths}<small>死亡</small></div>',
    '<div class="deaths">${h.deaths}<small>${TT(\'死亡\',\'deaths\')}</small></div>')

# event detail panel
rep("partiesBlock = `<div class=\"parties-list\"><h3 style=\"margin-bottom:4px\">Parties — 當事人</h3>${parties}</div>`;",
    "partiesBlock = `<div class=\"parties-list\"><h3 style=\"margin-bottom:4px\">Parties${TT(' — 當事人','')}</h3>${parties}</div>`;")
rep('<h3 style="margin-bottom:4px">Vehicles — 車種</h3>',
    '<h3 style="margin-bottom:4px">Vehicles${TT(\' — 車種\',\'\')}</h3>')
rep("<strong>${ev.road_type || '—'}</strong> · 速限 ${ev.speed_limit || '—'} ·",
    "<strong>${ev.road_type || '—'}</strong> · ${TT('速限','limit')} ${ev.speed_limit || '—'} ·")
rep("<strong>${ev.cause_main || '尚未發現肇事因素'}</strong>",
    "<strong>${ev.cause_main || TT('尚未發現肇事因素','Cause not yet determined')}</strong>")
rep("SIMPLIFIED RECORD · 簡式資料，僅含時間／地點／傷亡／車種",
    "SIMPLIFIED RECORD${TT(' · 簡式資料，僅含時間／地點／傷亡／車種',' · time/place/casualties/vehicle only')}")
rep('<span class="dval"><strong>${ev.deaths}</strong> 死 / ${ev.injuries} 傷</span>',
    '<span class="dval"><strong>${ev.deaths}</strong> ${TT(\'死\',\'dead\')} / ${ev.injuries} ${TT(\'傷\',\'injured\')}</span>')

# district list units
rep("const popTxt  = r.pop  != null ? (r.pop >= 10000 ? (r.pop/10000).toFixed(1)+'萬' : String(r.pop)) : '—';",
    "const popTxt  = r.pop  != null ? (r.pop >= 10000 ? (r.pop/10000).toFixed(1)+TT('萬','0k') : String(r.pop)) : '—';")
rep('<div class="d-rate">${rateTxt}<small>/萬 · ${popTxt}</small></div>',
    '<div class="d-rate">${rateTxt}<small>${TT(\'/萬\',\'/10k\')} · ${popTxt}</small></div>')

# breakdown empty states
rep("el.innerHTML = '<div style=\"font-size:11px;color:#888;font-weight:300\">— 篩選條件下無資料 —</div>'; return;",
    "el.innerHTML = `<div style=\"font-size:11px;color:#888;font-weight:300\">— ${TT('篩選條件下無資料','No data under this filter')} —</div>`; return;")

# KPI units
rep("document.getElementById('bigDeaths').innerHTML = `${totalDeaths}<sup>人</sup>`;",
    "document.getElementById('bigDeaths').innerHTML = `${totalDeaths}<sup>${TT('人','deaths')}</sup>`;")
rep("document.getElementById('kMoto').innerHTML = `${moto}<small>件</small>`;",
    "document.getElementById('kMoto').innerHTML = `${moto}<small>${TT('件','ev')}</small>`;")
rep("document.getElementById('kPed').innerHTML = `${ped}<small>件</small>`;",
    "document.getElementById('kPed').innerHTML = `${ped}<small>${TT('件','ev')}</small>`;")
rep("document.getElementById('kLatest').innerHTML = `${latest.deaths}<small>人</small>`;",
    "document.getElementById('kLatest').innerHTML = `${latest.deaths}<small>${TT('人','d')}</small>`;")

# genInsight bilingual
rep("""    const el = document.getElementById('insightText');
    if (el) el.innerHTML =
      '過去十年間，每年約有 <strong>' + avg + '</strong> 人在' + zh + '道路上喪生。' +
      '以「事件中最弱勢用路人」為基準：<strong>機車</strong>受害 <strong>' + moto + '</strong> 件（' + pct(moto) + '%）、' +
      '行人 ' + ped + ' 件（' + pct(ped) + '%）、自行車/慢車 ' + slow + ' 件（' + pct(slow) + '%）— ' +
      '合計<strong>弱勢用路人 ' + pct(vuln) + '%</strong>。<br>' +
      '十年高峰為 <strong>' + peak.year + '</strong> 年（' + peak.deaths + ' 人）；最近一年 ' + latest.year + ' 為 ' + latest.deaths + ' 人。' +
      '<strong>' + topD[0] + '</strong>累計 ' + topD[1] + ' 人，為' + zh + unitWord + '之最，是優先治理區域。';""",
"""    const enName = (window.__META && window.__META.en) || zh;
    const el = document.getElementById('insightText');
    if (!el) return;
    if (window.__LANG === 'en') {
      el.innerHTML =
        'Over the past decade, about <strong>' + avg + '</strong> people died on ' + enName + "'s roads each year. " +
        'Classified by the most-vulnerable user in each event: <strong>motorcyclists</strong> in <strong>' + moto + '</strong> events (' + pct(moto) + '%), ' +
        'pedestrians ' + ped + ' (' + pct(ped) + '%), bicycle/slow ' + slow + ' (' + pct(slow) + '%) — ' +
        '<strong>vulnerable users total ' + pct(vuln) + '%</strong>.<br>' +
        'The decade peak was <strong>' + peak.year + '</strong> (' + peak.deaths + ' deaths); the latest year ' + latest.year + ' had ' + latest.deaths + '. ' +
        '<strong>' + topD[0] + '</strong> has the most cumulative deaths (' + topD[1] + '), a priority area.';
    } else {
      el.innerHTML =
        '過去十年間，每年約有 <strong>' + avg + '</strong> 人在' + zh + '道路上喪生。' +
        '以「事件中最弱勢用路人」為基準：<strong>機車</strong>受害 <strong>' + moto + '</strong> 件（' + pct(moto) + '%）、' +
        '行人 ' + ped + ' 件（' + pct(ped) + '%）、自行車/慢車 ' + slow + ' 件（' + pct(slow) + '%）— ' +
        '合計<strong>弱勢用路人 ' + pct(vuln) + '%</strong>。<br>' +
        '十年高峰為 <strong>' + peak.year + '</strong> 年（' + peak.deaths + ' 人）；最近一年 ' + latest.year + ' 為 ' + latest.deaths + ' 人。' +
        '<strong>' + topD[0] + '</strong>累計 ' + topD[1] + ' 人，為' + zh + unitWord + '之最，是優先治理區域。';
    }""")

# expose __rerender inside __main (hook at the genInsight() call near init)
rep("""  genInsight();
  const bounds = L.latLngBounds(filteredOnMap().map(e => [e.lat, e.lon]));""",
"""  window.__rerender = () => {
    renderTrend(); renderYearStacks(); renderSnapshot(); renderHeatmap();
    renderMap(); renderBreakdowns(); renderHotspots(); genInsight();
  };
  genInsight();
  const bounds = L.latLngBounds(filteredOnMap().map(e => [e.lat, e.lon]));""")

# bootstrap: county switcher → expose buildSelect (lang-aware) + noteCountyEn
rep("""  // County switcher (sorted by deaths desc, as CITIES already is)
  const sel = document.getElementById('citySelect');
  if (sel) {
    CITIES.forEach(c => {
      const o = document.createElement('option');
      o.value = c.slug; o.textContent = c.zh + ' (' + c.deaths + ')';
      if (c.slug === slug) o.selected = true;
      sel.appendChild(o);
    });
    sel.addEventListener('change', () => { location.search = '?c=' + sel.value; });
  }""",
"""  // County switcher (sorted by deaths desc, as CITIES already is)
  const sel = document.getElementById('citySelect');
  if (sel) {
    window.__buildSelect = function () {
      sel.innerHTML = '';
      CITIES.forEach(c => {
        const o = document.createElement('option');
        o.value = c.slug;
        o.textContent = (window.__LANG === 'en' ? c.en : c.zh) + ' (' + c.deaths + ')';
        if (c.slug === slug) o.selected = true;
        sel.appendChild(o);
      });
    };
    window.__buildSelect();
    sel.addEventListener('change', () => { location.search = '?c=' + sel.value; });
  }
  if (m) { const nce = document.getElementById('noteCountyEn'); if (nce) nce.textContent = m.en; }""")

# error message
rep("'<p style=\"padding:40px;font-family:sans-serif\">找不到資料檔：data/' + slug + '.js</p>'",
    "'<p style=\"padding:40px;font-family:sans-serif\">' + TT('找不到資料檔：','Data file not found: ') + 'data/' + slug + '.js</p>'")

P.write_text(s)
print("city.html i18n applied;", len(s), "bytes")
import re as _re
print("empty t-zh spans:", len(_re.findall(r'<span class="t-zh"></span>', s)))
print("Leaflet L. calls:", len(_re.findall(r'\bL\.(map|tileLayer|geoJSON|latLngBounds|layerGroup|heatLayer)', s)))
