"""Extract national A1 dataset with county + district resolved per event.

Output: events.json (full), agg.json (district × victim_mode × year),
plus a county_district_table.json for reference.

District key = '臺/台'-normalised county + town, e.g. ('新北市', '板橋區').
"""
import csv
import json
import re
import sys
from pathlib import Path
from collections import defaultdict, Counter

BASE = Path("/Users/yunching0513/Taitung_Mobility/資料")
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

# 22 counties as appear in raw data. We normalize 臺 → 台 to merge string variants.
COUNTY_RE = re.compile(
    r"^(?:臺?|台?)(臺北市|台北市|新北市|桃園市|臺中市|台中市|臺南市|台南市|高雄市|"
    r"宜蘭縣|新竹縣|苗栗縣|彰化縣|南投縣|雲林縣|嘉義縣|嘉義市|新竹市|基隆市|"
    r"屏東縣|花蓮縣|臺東縣|台東縣|澎湖縣|金門縣|連江縣)"
)
# Prefer 區 suffix when the city is a 直轄市 (post-2010 administrative geography).
# Without preference, 「臺南市左鎮區」 would match 「左鎮」 first because 鎮 is in
# the character class. Try 區 first, fall back to 鄉/鎮/市.
DISTRICT_RE_KU  = re.compile(r"^(?:臺?|台?)(?:.+?[縣市])(.{1,4}?區)")
DISTRICT_RE_OTH = re.compile(r"^(?:臺?|台?)(?:.+?[縣市])(.{1,4}?[鄉鎮市])")
MUNICIPAL_COUNTIES = {'新北市', '台中市', '台南市', '高雄市', '桃園市', '台北市'}

def norm(s: str) -> str:
    return (s or "").replace("臺", "台")

def parse_casualties(s: str):
    deaths = injuries = 0
    if not s: return 0, 0
    m = re.search(r"死亡(\d+)", s); deaths = int(m.group(1)) if m else 0
    m = re.search(r"受傷(\d+)", s); injuries = int(m.group(1)) if m else 0
    return deaths, injuries

ROC_DT_RE = re.compile(r"(\d+)年(\d+)月(\d+)日\s+(\d+)時(\d+)分(\d+)秒")
def parse_simple_datetime(s: str):
    m = ROC_DT_RE.match(s)
    if not m: return "", "", 0, 0
    roc, mo, day, hh, mm, ss = map(int, m.groups())
    year = roc + 1911
    return f"{year:04d}{mo:02d}{day:02d}", f"{hh:02d}{mm:02d}{ss:02d}", year, mo

def classify_mode(s: str) -> str:
    v = s or ""
    if "機車" in v: return "機車"
    if "客車" in v or "貨車" in v or "曳引" in v: return "汽車"
    if "行人" in v or v.strip() == "人": return "人"
    if "自行車" in v or "慢車" in v: return "慢車"
    return "其他"

VULN_RANK = {"人": 0, "慢車": 1, "機車": 2, "汽車": 3, "其他": 4}
def victim_mode(parties):
    if not parties: return "其他"
    modes = set()
    for p in parties:
        text = (p.get("vehicle_main","") or "") + (p.get("vehicle_sub","") or "")
        modes.add(classify_mode(text))
    return min(modes, key=lambda m: VULN_RANK.get(m, 9))

def fix_coords(lon, lat):
    if 21 <= lon <= 26 and 119 <= lat <= 123:
        return lat, lon
    return lon, lat

def resolve_location(loc: str):
    if not loc:
        return None, None
    cm = COUNTY_RE.match(loc)
    if not cm:
        return None, None
    county = norm(cm.group(1))
    # For 直轄市 prefer 區; otherwise try 鄉鎮市 first, fall back to 區.
    if county in MUNICIPAL_COUNTIES:
        dm = DISTRICT_RE_KU.match(loc) or DISTRICT_RE_OTH.match(loc)
    else:
        dm = DISTRICT_RE_OTH.match(loc) or DISTRICT_RE_KU.match(loc)
    district = norm(dm.group(1)) if dm else None
    # Edge case: location with repeated city name like "新竹市北區新竹市東大路…"
    # caused district to absorb "北區新竹市". Only truncate if the captured
    # district ends with 市/縣 AND a 鄉/鎮/區 appears before it.
    if district and district.endswith(("市", "縣")) and any(c in district[:-1] for c in "鄉鎮區"):
        import re as _re
        m = _re.search(r"^(.{1,4}?[鄉鎮區])", district)
        if m: district = m.group(1)
    return county, district

# Extract
events = []
unresolved = Counter()
for roc, cy, fname, schema in YEARS:
    path = BASE / f"{roc}年傷亡道路交通事故資料" / fname
    if not path.exists():
        print(f"MISSING: {path}", file=sys.stderr); continue
    with open(path, newline='', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))

    if schema == "simple":
        for row in rows:
            loc = row.get("發生地點", "")
            county, district = resolve_location(loc)
            if not county:
                unresolved[loc[:24]] += 1; continue
            date, time, _, month = parse_simple_datetime(row.get("發生時間",""))
            deaths, injuries = parse_casualties(row.get("死亡受傷人數",""))
            try:
                lon = float(row.get("經度") or 0); lat = float(row.get("緯度") or 0)
                lon, lat = fix_coords(lon, lat)
            except ValueError:
                lon = lat = 0.0
            veh = row.get("車種","")
            pseudo = [{"vehicle_main": v} for v in (veh or "").split(";") if v]
            mode = victim_mode(pseudo) if pseudo else "其他"
            events.append({
                "schema":"simple","year":cy,"month":month,"date":date,"time":time,
                "county":county,"district":district,"location":loc,
                "lon":lon,"lat":lat,"deaths":deaths,"injuries":injuries,
                "mode": mode,
            })
    else:
        by_key = {}
        for row in rows:
            loc = row.get("發生地點","")
            county, district = resolve_location(loc)
            if not county:
                unresolved[loc[:24]] += 1; continue
            key = (row["發生日期"], row["發生時間"], row.get("經度",""), row.get("緯度",""), loc)
            by_key.setdefault(key, []).append(row)
        for key, group in by_key.items():
            first = group[0]
            loc = first.get("發生地點","")
            county, district = resolve_location(loc)
            try:
                lon = float(first.get("經度") or 0); lat = float(first.get("緯度") or 0)
                lon, lat = fix_coords(lon, lat)
            except ValueError:
                lon = lat = 0.0
            deaths, injuries = parse_casualties(first.get("死亡受傷人數",""))
            month = int(first.get("發生月份") or 0)
            parties = []
            for r in group:
                parties.append({
                    "vehicle_main": r.get("當事者區分-類別-大類別名稱-車種",""),
                    "vehicle_sub":  r.get("當事者區分-類別-子類別名稱-車種",""),
                })
            events.append({
                "schema":"full","year":cy,"month":month,
                "date":first["發生日期"],"time":(first.get("發生時間","") or "").zfill(6),
                "county":county,"district":district,"location":loc,
                "lon":lon,"lat":lat,"deaths":deaths,"injuries":injuries,
                "mode": victim_mode(parties),
            })

events.sort(key=lambda e: (e["date"], e["time"]))

OUT = Path("/Users/yunching0513/Taitung_Mobility/build_national")
OUT.mkdir(exist_ok=True)
(OUT / "events.json").write_text(json.dumps(events, ensure_ascii=False, separators=(",",":")))

# Aggregate
# Key: (county, district)
agg = defaultdict(lambda: {
    "deaths":0, "events":0, "by_mode": Counter(), "by_year": Counter(),
    "by_mode_year": defaultdict(lambda: Counter()),
})
for e in events:
    k = (e["county"], e["district"])
    a = agg[k]
    a["deaths"] += e["deaths"]
    a["events"] += 1
    a["by_mode"][e["mode"]] += 1
    a["by_year"][e["year"]] += 1
    a["by_mode_year"][e["mode"]][e["year"]] += 1

agg_out = []
for (county, district), v in agg.items():
    agg_out.append({
        "county": county, "district": district,
        "deaths": v["deaths"], "events": v["events"],
        "by_mode": dict(v["by_mode"]),
        "by_year": {str(k): v2 for k,v2 in v["by_year"].items()},
        "by_mode_year": {m: {str(y): c for y,c in yc.items()} for m,yc in v["by_mode_year"].items()},
    })
agg_out.sort(key=lambda r: -r["deaths"])
(OUT / "agg.json").write_text(json.dumps(agg_out, ensure_ascii=False, separators=(",",":")))

# Quick stats
print(f"Events: {len(events)}")
print(f"Total deaths: {sum(e['deaths'] for e in events)}")
print(f"Unique (county, district): {len(agg)}")
print(f"Events with no resolvable county: {sum(unresolved.values())}")
if unresolved:
    print("Top unresolved location prefixes:")
    for s, c in unresolved.most_common(5):
        print(f"  {c}× '{s}'")
# County-level totals
by_county = Counter()
for e in events: by_county[e['county']] += e['deaths']
print("\nDeaths by county (10y):")
for c, d in by_county.most_common():
    print(f"  {c}: {d}")
