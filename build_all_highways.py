"""Convert MOTC 國省道 shapefile → per-county GeoJSON into the national repo's
data/ folder, named data/<slug>.highways.geojson, for all 22 counties."""
import json
import shapefile
from pathlib import Path
from pyproj import Transformer

SRC = Path('/Users/yunching0513/Downloads/國省道(含快速公路)_1150409/ROAD_國省道(含快速公路)_1150409.shp')
OUT = Path('/Users/yunching0513/Taitung_Mobility/taiwan-mobility-atlas/data')

# county zh (normalized) → slug. Shapefile COUNTY uses 臺 variants; we normalize.
COUNTY2SLUG = {
    "台北市":"taipei","新北市":"newtaipei","桃園市":"taoyuan","台中市":"taichung",
    "台南市":"tainan","高雄市":"kaohsiung","基隆市":"keelung","新竹市":"hsinchucity",
    "嘉義市":"chiayicity","新竹縣":"hsinchu","苗栗縣":"miaoli","彰化縣":"changhua",
    "南投縣":"nantou","雲林縣":"yunlin","嘉義縣":"chiayi","屏東縣":"pingtung",
    "宜蘭縣":"yilan","花蓮縣":"hualien","台東縣":"taitung","澎湖縣":"penghu",
    "金門縣":"kinmen","連江縣":"lienchiang",
}
CLASS_MAP = {'HU':'國道','HW':'國道','1E':'快速公路','1U':'省道','1W':'省道'}
to_wgs = Transformer.from_crs('EPSG:3826', 'EPSG:4326', always_xy=True)

def simplify(points, tol=15):
    if len(points) <= 2: return points
    def pd(p,a,b):
        ax,ay=a; bx,by=b; px,py=p; dx,dy=bx-ax,by-ay
        if dx==0 and dy==0: return ((px-ax)**2+(py-ay)**2)**0.5
        t=max(0,min(1,((px-ax)*dx+(py-ay)*dy)/(dx*dx+dy*dy)))
        qx,qy=ax+t*dx,ay+t*dy
        return ((px-qx)**2+(py-qy)**2)**0.5
    def dp(pts,eps):
        if len(pts)<=2: return pts
        md=0; idx=0
        for i in range(1,len(pts)-1):
            d=pd(pts[i],pts[0],pts[-1])
            if d>md: md=d; idx=i
        if md>eps:
            return dp(pts[:idx+1],eps)[:-1]+dp(pts[idx:],eps)
        return [pts[0],pts[-1]]
    return dp(points,tol)

def norm(s): return (s or "").replace("臺","台")

sf = shapefile.Reader(str(SRC), encoding='utf-8')
buckets = {slug: [] for slug in COUNTY2SLUG.values()}
for sr in sf.iterShapeRecords():
    r = sr.record
    county = norm(r['COUNTY'])
    slug = COUNTY2SLUG.get(county)
    if not slug: continue
    rc = CLASS_MAP.get(r['ROADCLASS1'], '其他')
    shape = sr.shape
    parts = list(shape.parts) + [len(shape.points)]
    lines = []
    for i in range(len(parts)-1):
        seg = simplify(shape.points[parts[i]:parts[i+1]], 15)
        ll = [list(to_wgs.transform(x,y)) for x,y in seg]
        if len(ll) >= 2: lines.append(ll)
    if not lines: continue
    geom = {"type":"LineString","coordinates":lines[0]} if len(lines)==1 \
           else {"type":"MultiLineString","coordinates":lines}
    buckets[slug].append({
        "type":"Feature",
        "properties":{"class":rc,"num":(r['ROADNUM'] or '').strip(),
                      "name":(r['ROADNAME'] or '').strip(),"alias":(r['ROADALIAS'] or '').strip()},
        "geometry":geom,
    })

from collections import Counter
for slug, feats in buckets.items():
    p = OUT / f"{slug}.highways.geojson"
    p.write_text(json.dumps({"type":"FeatureCollection","features":feats},
                            ensure_ascii=False, separators=(',',':')))
    bc = Counter(f['properties']['class'] for f in feats)
    print(f"  {slug:<12} {len(feats):>5} seg  {dict(bc)}  ({p.stat().st_size//1024} KB)")
