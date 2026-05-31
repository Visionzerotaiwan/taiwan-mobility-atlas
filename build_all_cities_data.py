"""Extract all 22 counties' A1 events → taiwan-mobility-atlas/data/<slug>.js

Each file sets:
  window.CITY_A1     = [ ...events... ]   (full per-event detail w/ parties)
  window.CITY_YEARLY = [ ...yearly... ]
  window.CITY_POP    = { district: population }

Plus a shared data/cities.js index with META for every county (display
names, map center, zoom, totals) — consumed by both city.html and the
national navigator.
"""
import csv
import json
import re
import sys
from pathlib import Path
from collections import defaultdict, Counter

BASE = Path("/Users/yunching0513/Taitung_Mobility/資料")
OUT = Path("/Users/yunching0513/Taitung_Mobility/taiwan-mobility-atlas/data")
OUT.mkdir(parents=True, exist_ok=True)

YEARS = [
    (105, 2016, "105年度A1交通事故資料.csv", "simple"),
    (106, 2017, "106年度A1交通事故資料.csv", "simple"),
    (107, 2018, "2018年度A1交通事故資料.csv", "full"),
    (108, 2019, "2019年度A1交通事故資料.csv", "full"),
    (109, 2020, "2020年度A1交通事故資料.csv", "full"),
    (110, 2021, "110年度A1交通事故資料.csv", "simple"),
    (111, 2022, "111年度A1交通事故資料.csv", "full"),
    (112, 2023, "112年度A1交通事故資料.csv", "full"),
    (113, 2024, "113年度A1交通事故資料.csv", "full"),
    (114, 2025, "114年度A1交通事故資料.csv", "full"),
]

# slug → config. `prefixes` are normalized (台) county strings the raw 發生地點
# may begin with (we test both 臺/台 by normalizing first). `municipal` = uses 區.
COUNTIES = {
    "taipei":     dict(zh="台北市", en="Taipei City",       municipal=True,  center=[25.07,121.55], zoom=11),
    "newtaipei":  dict(zh="新北市", en="New Taipei City",   municipal=True,  center=[25.00,121.52], zoom=10),
    "taoyuan":    dict(zh="桃園市", en="Taoyuan City",      municipal=True,  center=[24.96,121.22], zoom=10),
    "taichung":   dict(zh="台中市", en="Taichung City",     municipal=True,  center=[24.18,120.80], zoom=10),
    "tainan":     dict(zh="台南市", en="Tainan City",       municipal=True,  center=[23.05,120.25], zoom=10),
    "kaohsiung":  dict(zh="高雄市", en="Kaohsiung City",    municipal=True,  center=[22.85,120.50], zoom=9),
    "keelung":    dict(zh="基隆市", en="Keelung City",      municipal=True,  center=[25.13,121.73], zoom=12),
    "hsinchucity":dict(zh="新竹市", en="Hsinchu City",      municipal=True,  center=[24.81,120.97], zoom=12),
    "chiayicity": dict(zh="嘉義市", en="Chiayi City",       municipal=True,  center=[23.48,120.45], zoom=12),
    "hsinchu":    dict(zh="新竹縣", en="Hsinchu County",    municipal=False, center=[24.72,121.13], zoom=10),
    "miaoli":     dict(zh="苗栗縣", en="Miaoli County",     municipal=False, center=[24.50,120.90], zoom=10),
    "changhua":   dict(zh="彰化縣", en="Changhua County",   municipal=False, center=[24.00,120.45], zoom=10),
    "nantou":     dict(zh="南投縣", en="Nantou County",     municipal=False, center=[23.87,120.95], zoom=9),
    "yunlin":     dict(zh="雲林縣", en="Yunlin County",     municipal=False, center=[23.72,120.40], zoom=10),
    "chiayi":     dict(zh="嘉義縣", en="Chiayi County",     municipal=False, center=[23.45,120.40], zoom=10),
    "pingtung":   dict(zh="屏東縣", en="Pingtung County",   municipal=False, center=[22.55,120.55], zoom=9),
    "yilan":      dict(zh="宜蘭縣", en="Yilan County",      municipal=False, center=[24.70,121.73], zoom=10),
    "hualien":    dict(zh="花蓮縣", en="Hualien County",    municipal=False, center=[23.80,121.40], zoom=8),
    "taitung":    dict(zh="台東縣", en="Taitung County",    municipal=False, center=[22.90,121.05], zoom=9),
    "penghu":     dict(zh="澎湖縣", en="Penghu County",     municipal=False, center=[23.57,119.62], zoom=10),
    "kinmen":     dict(zh="金門縣", en="Kinmen County",     municipal=False, center=[24.43,118.32], zoom=11),
    "lienchiang": dict(zh="連江縣", en="Lienchiang County", municipal=False, center=[26.15,119.95], zoom=9),
}

# ---------- shared helpers ----------
def norm(s): return (s or "").replace("臺", "台")

def parse_casualties(s):
    d = i = 0
    if not s: return 0, 0
    m = re.search(r"死亡(\d+)", s); d = int(m.group(1)) if m else 0
    m = re.search(r"受傷(\d+)", s); i = int(m.group(1)) if m else 0
    return d, i

ROC_DT = re.compile(r"(\d+)年(\d+)月(\d+)日\s+(\d+)時(\d+)分(\d+)秒")
def parse_simple_dt(s):
    m = ROC_DT.match(s)
    if not m: return "", "", 0, 0
    roc, mo, day, hh, mm, ss = map(int, m.groups())
    return f"{roc+1911:04d}{mo:02d}{day:02d}", f"{hh:02d}{mm:02d}{ss:02d}", roc+1911, mo

def classify_mode(s):
    v = s or ""
    if "機車" in v: return "機車"
    if "客車" in v or "貨車" in v or "曳引" in v: return "汽車"
    if "行人" in v or v.strip() == "人": return "人"
    if "自行車" in v or "慢車" in v: return "慢車"
    return "其他"

VULN = {"人":0,"慢車":1,"機車":2,"汽車":3,"其他":4}
def victim_mode(parties):
    if not parties: return "其他"
    ms = set()
    for p in parties:
        ms.add(classify_mode((p.get("vehicle_main","") or "")+(p.get("vehicle_sub","") or "")))
    return min(ms, key=lambda m: VULN.get(m,9))

def fix_coords(lon, lat):
    if 21 <= lon <= 26 and 119 <= lat <= 123: return lat, lon
    return lon, lat

def primary_simple(v): return (v or "").split(";")[0]

# District resolution: prefer 區 for municipalities, 鄉鎮市 otherwise.
DRE_KU  = re.compile(r"^(?:.+?[縣市])(.{1,4}?區)")
DRE_OTH = re.compile(r"^(?:.+?[縣市])(.{1,4}?[鄉鎮市])")
def resolve_district(loc_after_county, municipal):
    if municipal:
        m = DRE_KU.match(loc_after_county) or DRE_OTH.match(loc_after_county)
    else:
        m = DRE_OTH.match(loc_after_county) or DRE_KU.match(loc_after_county)
    if not m: return None
    d = norm(m.group(1))
    # collapse repeated-city artifacts ("北區新竹市…")
    if d.endswith(("市","縣")) and any(c in d[:-1] for c in "鄉鎮區"):
        mm = re.search(r"^(.{1,4}?[鄉鎮區])", d)
        if mm: d = mm.group(1)
    return d

# ---------- load all CSVs once, bucket events per county ----------
buckets = defaultdict(list)   # slug -> [event dict]
# Build a county-prefix → slug map on normalized names
PREFIX2SLUG = {cfg["zh"]: slug for slug, cfg in COUNTIES.items()}

for roc, cy, fname, schema in YEARS:
    path = BASE / f"{roc}年傷亡道路交通事故資料" / fname
    if not path.exists():
        print(f"MISSING {path}", file=sys.stderr); continue
    with open(path, newline='', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))

    if schema == "simple":
        for row in rows:
            loc = norm(row.get("發生地點",""))
            # county = first matching prefix
            slug = None; county_zh = None
            for cz, sg in PREFIX2SLUG.items():
                if loc.startswith(cz):
                    slug, county_zh = sg, cz; break
            if not slug: continue
            after = loc[len(county_zh):]
            municipal = COUNTIES[slug]["municipal"]
            district = resolve_district(loc, municipal)
            date, time, _, month = parse_simple_dt(row.get("發生時間",""))
            deaths, inj = parse_casualties(row.get("死亡受傷人數",""))
            try:
                lon = float(row.get("經度") or 0); lat = float(row.get("緯度") or 0)
                lon, lat = fix_coords(lon, lat)
            except ValueError:
                lon = lat = 0.0
            veh = row.get("車種","")
            pseudo = [{"vehicle_main": v} for v in (veh or "").split(";") if v]
            buckets[slug].append({
                "schema":"simple","year":cy,"month":month,"date":date,"time":time,
                "location":loc,"district":district or "其他","lon":lon,"lat":lat,
                "deaths":deaths,"injuries":inj,
                "mode": victim_mode(pseudo) if pseudo else "其他",
                "principal_mode": classify_mode(primary_simple(veh)),
                "principal_vehicle": primary_simple(veh), "vehicles_raw": veh,
                "weather":"","light":"","road_type":"","speed_limit":"",
                "road_shape_main":"","road_shape_sub":"","surface":"","signal":"",
                "accident_main":"","accident_sub":"","cause_main":"","parties":[],
            })
    else:
        by_key = defaultdict(list)
        for row in rows:
            loc = norm(row.get("發生地點",""))
            slug = None; county_zh = None
            for cz, sg in PREFIX2SLUG.items():
                if loc.startswith(cz):
                    slug, county_zh = sg, cz; break
            if not slug: continue
            key = (slug, row["發生日期"], row["發生時間"], row.get("經度",""), row.get("緯度",""), loc)
            by_key[key].append(row)
        for key, group in by_key.items():
            slug = key[0]
            first = group[0]
            loc = norm(first.get("發生地點",""))
            municipal = COUNTIES[slug]["municipal"]
            district = resolve_district(loc, municipal)
            try:
                lon = float(first.get("經度") or 0); lat = float(first.get("緯度") or 0)
                lon, lat = fix_coords(lon, lat)
            except ValueError:
                lon = lat = 0.0
            deaths, inj = parse_casualties(first.get("死亡受傷人數",""))
            month = int(first.get("發生月份") or 0)
            p1 = next((r for r in group if (r.get("當事者順位") or "")=="1"), group[0])
            pm = p1.get("當事者區分-類別-大類別名稱-車種","")
            ps = p1.get("當事者區分-類別-子類別名稱-車種","")
            parties = []
            for r in group:
                age_raw = r.get("當事者事故發生時年齡","")
                try:
                    age = int(age_raw); age = None if age < 0 else age
                except ValueError:
                    age = None
                parties.append({
                    "order": r.get("當事者順位",""),
                    "vehicle_main": r.get("當事者區分-類別-大類別名稱-車種",""),
                    "vehicle_sub":  r.get("當事者區分-類別-子類別名稱-車種",""),
                    "gender": r.get("當事者屬-性-別名稱",""),
                    "age": age,
                    "protection": r.get("保護裝備名稱",""),
                    "action_main": r.get("當事者行動狀態大類別名稱",""),
                    "action_sub": r.get("當事者行動狀態子類別名稱",""),
                    "cause_individual": r.get("肇因研判子類別名稱-個別",""),
                })
            buckets[slug].append({
                "schema":"full","year":cy,"month":month,
                "date":first["發生日期"],"time":(first.get("發生時間","") or "").zfill(6),
                "location":loc,"district":district or "其他","lon":lon,"lat":lat,
                "deaths":deaths,"injuries":inj,
                "mode": victim_mode(parties),
                "principal_mode": classify_mode(pm+ps),
                "principal_vehicle": pm + (("·"+ps) if ps else ""),
                "vehicles_raw": ";".join(
                    (r.get("當事者區分-類別-大類別名稱-車種","") or "")
                    + ("-"+r.get("當事者區分-類別-子類別名稱-車種","") if r.get("當事者區分-類別-子類別名稱-車種") else "")
                    for r in group),
                "weather":first.get("天候名稱",""),"light":first.get("光線名稱",""),
                "road_type":first.get("道路類別-第1當事者-名稱",""),
                "speed_limit":first.get("速限-第1當事者",""),
                "road_shape_main":first.get("道路型態大類別名稱",""),
                "road_shape_sub":first.get("道路型態子類別名稱",""),
                "surface":first.get("路面狀況-路面狀態名稱",""),
                "signal":first.get("號誌-號誌種類名稱",""),
                "accident_main":first.get("事故類型及型態大類別名稱",""),
                "accident_sub":first.get("事故類型及型態子類別名稱",""),
                "cause_main":first.get("肇因研判子類別名稱-主要",""),
                "parties":parties,
            })

# ---------- population (from national populations.json) ----------
pops = json.load(open("/Users/yunching0513/Taitung_Mobility/build_national/populations.json"))

# ---------- write per-county files + build index META ----------
index_meta = []
for slug, cfg in COUNTIES.items():
    events = sorted(buckets.get(slug, []), key=lambda e: (e["date"], e["time"]))
    # yearly summary
    yearly = {}
    for e in events:
        y = e["year"]
        s = yearly.setdefault(y, {"year":y,"events":0,"deaths":0,"injuries":0,"with_coords":0,
            "by_mode":Counter(),"by_district":Counter(),"by_month":Counter(),
            "by_hour":Counter(),"by_road":Counter(),"by_light":Counter()})
        s["events"]+=1; s["deaths"]+=e["deaths"]; s["injuries"]+=e["injuries"]
        if e["lon"] and e["lat"]: s["with_coords"]+=1
        s["by_mode"][e["mode"]]+=1
        s["by_district"][e["district"]]+=e["deaths"]
        s["by_month"][e["month"]]+=1
        try: s["by_hour"][int(e["time"][:2])]+=1
        except ValueError: pass
        if e.get("road_type"): s["by_road"][e["road_type"]]+=1
        if e.get("light"): s["by_light"][e["light"]]+=1
    def ser(s):
        return {**{k:v for k,v in s.items() if not isinstance(v,Counter)},
                **{k:dict(v) for k,v in s.items() if isinstance(v,Counter)}}
    yearly_serial = [ser(yearly[y]) for y in sorted(yearly)]
    county_pop = pops.get(cfg["zh"], {})

    js = (
        f"// {cfg['zh']} ({cfg['en']}) — A1 fatal crashes 2016–2025\n"
        f"window.CITY_A1 = {json.dumps(events, ensure_ascii=False, separators=(',',':'))};\n"
        f"window.CITY_YEARLY = {json.dumps(yearly_serial, ensure_ascii=False, separators=(',',':'))};\n"
        f"window.CITY_POP = {json.dumps(county_pop, ensure_ascii=False, separators=(',',':'))};\n"
    )
    (OUT / f"{slug}.js").write_text(js)

    deaths = sum(e["deaths"] for e in events)
    coords = sum(1 for e in events if e["lon"] and e["lat"])
    index_meta.append({
        "slug": slug, "zh": cfg["zh"], "en": cfg["en"],
        "municipal": cfg["municipal"], "center": cfg["center"], "zoom": cfg["zoom"],
        "events": len(events), "deaths": deaths, "with_coords": coords,
    })

index_meta.sort(key=lambda m: -m["deaths"])
(OUT / "cities.js").write_text(
    "window.CITIES = " + json.dumps(index_meta, ensure_ascii=False, separators=(',',':')) + ";\n"
)

# report
print(f"{'slug':<12}{'county':<8}{'events':>7}{'deaths':>7}{'coords':>7}")
tot_d = tot_e = 0
for m in index_meta:
    print(f"{m['slug']:<12}{m['zh']:<8}{m['events']:>7}{m['deaths']:>7}{m['with_coords']:>7}")
    tot_d += m["deaths"]; tot_e += m["events"]
print(f"{'TOTAL':<20}{tot_e:>7}{tot_d:>7}")
