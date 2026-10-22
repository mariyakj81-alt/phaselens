import sys, json, csv, re, urllib.parse
sys.path.insert(0, '.')
from common import get
from known import known, ROOT
K = known()
A = set(r["doi"].lower() for r in csv.DictReader(open(ROOT + "/calcite/papers_new_A.csv", encoding="utf-8")))
c = json.load(open("cites_core1.json"))
minc = int(sys.argv[1]); out = sys.argv[2]
try: res = json.load(open(out))
except Exception: res = {}
todo = [d for d, v in c.items() if v[0] >= minc and d not in K and d not in A and d not in res]
print(len(todo), flush=True)
for i, d in enumerate(todo):
    try:
        r = get("https://api.openalex.org/works/https://doi.org/" + urllib.parse.quote(d, safe="/"), params={"select": "title,publication_year,open_access,locations,type"}, min_gap=0.6)
    except Exception as e:
        continue
    if r.status_code != 200: res[d] = None; continue
    w = r.json()
    locs = [(l.get("version"), (l.get("pdf_url") or l.get("landing_page_url") or "")) for l in w.get("locations", []) if l.get("is_oa") and (l.get("pdf_url") or l.get("landing_page_url"))]
    res[d] = {"t": w.get("title"), "y": w.get("publication_year"), "oa": w.get("open_access", {}).get("oa_status"), "locs": locs[:5], "n": c[d][0]}
    if i % 100 == 0:
        json.dump(res, open(out, "w")); print(i, flush=True)
json.dump(res, open(out, "w"))
