"""Aggregate age × victim-mode × accident-type from all 22 city.js files,
writing data/age_type.json for the national page's new analysis section.

Caveat: only full-schema years (2018–2020, 2022–2025) carry per-party age.
2016 & 2017 (simple) and 2021 (simple) have no age data and are omitted from
the age cross-tabs but counted in the overall coverage stats.
"""
import json
import re
import glob
from pathlib import Path
from collections import Counter, defaultdict

DATA_DIR = Path("/Users/yunching0513/Taitung_Mobility/taiwan-mobility-atlas/data")

# Age brackets (Taiwan-standard road-safety brackets)
BRACKETS = [
    ("0-14",  0, 14),    # 兒童 Children
    ("15-24", 15, 24),   # 青少年 Youth
    ("25-44", 25, 44),   # 青壯年 Young adult
    ("45-64", 45, 64),   # 中壯年 Middle-aged
    ("65-74", 65, 74),   # 前期高齡 Young-old
    ("75+",   75, 200),  # 高齡 Old-old
]
def bracket(age: int) -> str:
    for label, lo, hi in BRACKETS:
        if lo <= age <= hi:
            return label
    return "—"

# Victim-mode priority order (most vulnerable first)
VULN = {"人":0, "慢車":1, "機車":2, "汽車":3, "其他":4}
def classify(s: str) -> str:
    v = s or ""
    if "機車" in v: return "機車"
    if "客車" in v or "貨車" in v or "曳引" in v: return "汽車"
    if "行人" in v or v.strip() == "人": return "人"
    if "自行車" in v or "慢車" in v: return "慢車"
    return "其他"

# Accident-type normalization: collapse 2018-2020 vs 2022+ naming variants.
TYPE_MAP = {
    "車輛本身":      "車輛本身",       # single-vehicle (old name)
    "汽(機)車本身":  "車輛本身",       # single-vehicle (new name)
    "人與車":        "人與車",         # ped-vehicle (old)
    "人與汽(機)車":  "人與車",         # ped-vehicle (new)
    "車與車":        "車與車",         # vehicle-vehicle
    "平交道事故":    "平交道事故",     # rail crossing (rare)
}
def norm_type(t: str) -> str:
    return TYPE_MAP.get((t or "").strip(), "其他")

def victim_party(parties):
    """Pick the most-vulnerable party for an event (matches the site's victim_mode)."""
    if not parties: return None
    best, best_rank = None, 99
    for p in parties:
        text = (p.get("vehicle_main","") or "") + (p.get("vehicle_sub","") or "")
        m = classify(text)
        r = VULN.get(m, 9)
        if r < best_rank:
            best_rank, best = r, p
    return best

# ────────────────────────────── load ──────────────────────────────
city_files = sorted(f for f in glob.glob(str(DATA_DIR / "*.js"))
                    if not f.endswith("cities.js") and not f.endswith(".highways.geojson"))
print(f"Reading {len(city_files)} city files")

# Aggregations
total_events = 0
events_with_age_and_type = 0

by_age          = Counter()
by_age_mode     = defaultdict(lambda: Counter())   # by_age_mode[age][mode]
by_age_type     = defaultdict(lambda: Counter())   # by_age_type[age][type]
by_age_year     = defaultdict(lambda: Counter())   # by_age_year[age][year]
combo_tally     = Counter()                        # (age, mode, type) → count

mode_totals = Counter()
type_totals = Counter()

for f in city_files:
    raw = open(f, encoding="utf-8").read()
    m = re.search(r"window\.CITY_A1\s*=\s*(\[.*?\]);\s*window\.CITY_YEARLY", raw, re.S)
    if not m: continue
    events = json.loads(m.group(1))
    for e in events:
        total_events += 1
        if not e.get("parties"):
            continue
        vp = victim_party(e["parties"])
        if not vp: continue
        age = vp.get("age")
        if not isinstance(age, int) or age < 0 or age > 120:
            continue
        atype = norm_type(e.get("accident_main",""))
        if atype == "其他":
            continue
        events_with_age_and_type += 1

        ab = bracket(age)
        vmode = e.get("mode") or classify((vp.get("vehicle_main","") or "") + (vp.get("vehicle_sub","") or ""))

        by_age[ab] += 1
        by_age_mode[ab][vmode] += 1
        by_age_type[ab][atype] += 1
        by_age_year[ab][str(e.get("year",""))] += 1
        combo_tally[(ab, vmode, atype)] += 1
        mode_totals[vmode] += 1
        type_totals[atype] += 1

# Top actionable (age, mode, type) combos by count
top_combos = [
    {"age": a, "mode": m, "type": t, "count": c}
    for (a, m, t), c in combo_tally.most_common(15)
]

out = {
    "coverage": {
        "total_events": total_events,
        "events_used": events_with_age_and_type,
        "years_covered": ["2018","2019","2020","2022","2023","2024","2025"],
        "years_missing": ["2016","2017","2021"],
        "note_zh": "年齡與事故態樣分析僅涵蓋完整欄位年份（2018–2020、2022–2025）；2016、2017、2021 為簡式欄位無此資料。",
        "note_en": "Age × accident-type analysis covers only full-schema years (2018–2020, 2022–2025); 2016, 2017, 2021 use a simplified schema without these fields.",
    },
    "brackets":     [b[0] for b in BRACKETS],
    "modes":        ["機車","汽車","人","慢車","其他"],
    "types":        ["車與車","車輛本身","人與車","平交道事故"],
    "by_age":       dict(by_age),
    "by_age_mode":  {k: dict(v) for k,v in by_age_mode.items()},
    "by_age_type":  {k: dict(v) for k,v in by_age_type.items()},
    "by_age_year":  {k: dict(v) for k,v in by_age_year.items()},
    "top_combos":   top_combos,
    "mode_totals":  dict(mode_totals),
    "type_totals":  dict(type_totals),
}

out_path = DATA_DIR / "age_type.json"
out_path.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
print(f"\nWrote {out_path} ({out_path.stat().st_size/1024:.1f} KB)")
print(f"Coverage: {events_with_age_and_type:,} / {total_events:,} events ({events_with_age_and_type/total_events*100:.1f}%)")
print(f"\nBy bracket: {dict(by_age)}")
print(f"\nTop combos:")
for c in top_combos[:10]:
    print(f"  {c['age']:>6} × {c['mode']:<4} × {c['type']:<8}  →  {c['count']:>4}")
