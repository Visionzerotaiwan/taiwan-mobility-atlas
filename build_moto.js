// build_moto.js — aggregate 機車 (motorcyclist) A1 fatalities 2016–2025
// across all 22 counties into data/moto.json (national + per-county).
// Run: node build_moto.js
const fs = require('fs');
const path = require('path');
const DATA = path.join(__dirname, 'data');

global.window = {};
require(path.join(DATA, 'cities.js'));
const CITIES = window.window ? window.window.CITIES : window.CITIES;

// ── Cause grouping (keyword priority — order matters) ───────────────
function causeGroup(c) {
  if (!c) return '不明／未填';
  if (/酒醉|吸食違禁|酒駕/.test(c)) return '酒（毒）駕';
  if (/逆向/.test(c)) return '逆向行駛';
  if (/超速|未依規定減速/.test(c)) return '超速／未減速';
  if (/未注意車前|恍神|分心|手持行動電話/.test(c)) return '未注意車前／分心';
  if (/讓車|未讓|起步|停車操作/.test(c)) return '未依規定讓車（路權）';
  if (/轉彎|迴轉|變換車道|蛇行|方向不定|倒車/.test(c)) return '違規轉彎／變換車道';
  if (/號誌|標誌|標線|閃光|闖紅燈|禁制|二段式|禁行|遵行方向/.test(c)) return '違反號誌／標誌';
  if (/安全間隔|安全距離|超車|搶道|爭.道|未靠右/.test(c)) return '未保持安全距離／搶道';
  if (/不明|尚未發現|無法釐清|跡證不足/.test(c)) return '不明／未填';
  return '其他（機件、生理、裝載等）';
}
const CAUSE_ORDER = [
  '未注意車前／分心', '未依規定讓車（路權）', '違反號誌／標誌',
  '違規轉彎／變換車道', '酒（毒）駕', '超速／未減速',
  '未保持安全距離／搶道', '逆向行駛', '其他（機件、生理、裝載等）', '不明／未填'
];

function ageBucket(a) {
  if (typeof a !== 'number' || a <= 0 || a >= 120) return null;
  return a < 18 ? '<18' : a < 25 ? '18–24' : a < 35 ? '25–34' : a < 45 ? '35–44'
       : a < 55 ? '45–54' : a < 65 ? '55–64' : a < 75 ? '65–74' : '75+';
}
const AGE_ORDER = ['<18','18–24','25–34','35–44','45–54','55–64','65–74','75+'];

// Light → day / night-lit / night-dark / dusk
function lightBucket(l) {
  if (!l) return null;
  if (/日間/.test(l)) return '日間';
  if (/晨|暮/.test(l)) return '晨暮';
  if (/未開啟|故障|無照明/.test(l)) return '夜間-照明不足';
  if (/夜間|有照明/.test(l)) return '夜間-有照明';
  return null;
}
// Road shape → intersection / midblock
function shapeBucket(s) {
  if (!s) return null;
  if (/交岔/.test(s)) return '路口';
  if (/單路/.test(s)) return '路段（單路）';
  return '其他';
}
// Speed bands
function speedBand(s) {
  const v = parseInt(s, 10);
  if (!v || v < 0 || v > 130) return null;
  return v <= 30 ? '≤30' : v <= 40 ? '40' : v <= 50 ? '50' : v <= 60 ? '60' : '≥70';
}
const SPEED_ORDER = ['≤30','40','50','60','≥70'];

// Weather → clear / cloudy / rain / other
function weatherBucket(w) {
  if (!w) return null;
  if (/晴/.test(w)) return '晴';
  if (/陰/.test(w)) return '陰';
  if (/雨/.test(w)) return '雨';
  return '其他（霧、風）';
}
const ROAD_ORDER = ['市區道路','村里道路','省道','縣道','鄉道','其他'];
function roadBucket(r){
  if(!r) return null;
  if(/市區/.test(r)) return '市區道路';
  if(/村里/.test(r)) return '村里道路';
  if(/省道/.test(r)) return '省道';
  if(/縣道/.test(r)) return '縣道';
  if(/鄉道/.test(r)) return '鄉道';
  return '其他';
}

function findMotoParty(e) {
  if (!e.parties || !e.parties.length) return null;
  const motos = e.parties.filter(p => p.vehicle_main === '機車');
  if (motos.length === 1) return motos[0];
  if (motos.length > 1) return motos.find(p => p.order !== '1') || motos[0];
  return null;
}

function blankAgg() {
  return {
    motoDeaths: 0, allDeaths: 0, fullRecs: 0,
    byYear: {}, byYearAll: {},
    cause: {}, weather: {}, light: {}, road: {}, shape: {}, speed: {},
    age: {}, gender: {}, helmet: {}, hour: {},
    single: 0, multi: 0, accSub: {}
  };
}
function bump(o, k, n) { if (k == null) return; o[k] = (o[k] || 0) + (n || 1); }

function ingest(agg, e) {
  const d = e.deaths || 1;
  agg.allDeaths += d;
  agg.byYearAll[e.year] = (agg.byYearAll[e.year] || 0) + d;
  if (e.mode !== '機車') return;
  agg.motoDeaths += d;
  agg.byYear[e.year] = (agg.byYear[e.year] || 0) + d;
  if (e.time && e.time.length >= 2) {
    const h = parseInt(e.time.slice(0, 2), 10);
    if (h >= 0 && h < 24) bump(agg.hour, String(h).padStart(2, '0'));
  }
  if (e.schema !== 'full') return;
  agg.fullRecs++;
  bump(agg.cause, causeGroup(e.cause_main));
  bump(agg.weather, weatherBucket(e.weather));
  bump(agg.light, lightBucket(e.light));
  bump(agg.road, roadBucket(e.road_type));
  bump(agg.shape, shapeBucket(e.road_shape_main));
  bump(agg.speed, speedBand(e.speed_limit));
  bump(agg.accSub, e.accident_sub || '(未填)');
  const vh = (e.parties || []).filter(p => p.vehicle_main && p.vehicle_main !== '人');
  if (vh.length <= 1) agg.single++; else agg.multi++;
  const mp = findMotoParty(e);
  if (mp) {
    if (mp.gender === '男' || mp.gender === '女') bump(agg.gender, mp.gender);
    bump(agg.age, ageBucket(mp.age));
    // helmet status
    if (mp.protection) {
      const p = mp.protection;
      const hb = /未戴|未繫/.test(p) ? '未戴安全帽'
        : /半罩/.test(p) && /非半罩/.test(p) === false ? '半罩式安全帽'
        : /安全帽|安全帶/.test(p) ? '戴安全帽'
        : '不明';
      bump(agg.helmet, hb);
    }
  }
}

// Build
const nat = blankAgg();
const counties = {};
for (const c of CITIES) {
  const p = path.join(DATA, c.slug + '.js');
  if (!fs.existsSync(p)) { console.error('MISSING', c.slug); continue; }
  delete require.cache[require.resolve(p)];
  window.CITY_A1 = undefined;
  require(p);
  const arr = window.CITY_A1 || [];
  const agg = blankAgg();
  for (const e of arr) { ingest(agg, e); ingest(nat, e); }
  agg.zh = c.zh; agg.en = c.en; agg.slug = c.slug;
  agg.share = agg.allDeaths ? +(agg.motoDeaths / agg.allDeaths * 100).toFixed(1) : 0;
  counties[c.slug] = agg;
}
nat.share = nat.allDeaths ? +(nat.motoDeaths / nat.allDeaths * 100).toFixed(1) : 0;

const out = {
  generated: '2026-06-22',
  meta: {
    years: [2016, 2025],
    causeOrder: CAUSE_ORDER, ageOrder: AGE_ORDER,
    speedOrder: SPEED_ORDER, roadOrder: ROAD_ORDER
  },
  national: nat,
  counties
};
fs.writeFileSync(path.join(DATA, 'moto.json'), JSON.stringify(out));
// also a JS-wrapped copy for file:// loading without fetch/CORS
fs.writeFileSync(path.join(DATA, 'moto.js'), 'window.MOTO=' + JSON.stringify(out) + ';');

// sanity print
console.log('national moto deaths:', nat.motoDeaths, '/ all', nat.allDeaths, '=', nat.share + '%');
console.log('full recs:', nat.fullRecs);
console.log('cause groups:', JSON.stringify(nat.cause, null, 1));
console.log('weather:', JSON.stringify(nat.weather));
console.log('light:', JSON.stringify(nat.light));
console.log('shape:', JSON.stringify(nat.shape));
console.log('road:', JSON.stringify(nat.road));
console.log('speed:', JSON.stringify(nat.speed));
console.log('age:', JSON.stringify(nat.age));
console.log('gender:', JSON.stringify(nat.gender));
console.log('helmet:', JSON.stringify(nat.helmet));
console.log('single/multi:', nat.single, nat.multi);
