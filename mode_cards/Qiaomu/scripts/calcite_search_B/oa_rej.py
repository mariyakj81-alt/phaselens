import sys, json, re, csv, urllib.parse
sys.path.insert(0, '.')
from common import get
from known import ROOT
rows = list(csv.DictReader(open(ROOT + "/calcite/candidates_rejected.csv", encoding="utf-8")))
blocked = re.compile(r"mdpi\.com|wiley|pubs\.rsc|link\.springer|sciencedirect|pubs\.acs|iopscience|tandfonline|academic\.oup|hal\.science|opus4|doi\.org|europepmc|ncbi\.nlm|aps\.org|aip\.|degruyter|gsw|geoscienceworld", re.I)
for r in rows:
    d = r["doi"].strip().lower()
    if not d or not re.search(r"needs_manual", r["reason"]): continue
    x = get("https://api.openalex.org/works/https://doi.org/" + urllib.parse.quote(d, safe="/"), params={"select": "open_access,locations"}, min_gap=0.8)
    if x.status_code != 200: continue
    w = x.json()
    locs = [(l.get("version"), (l.get("pdf_url") or l.get("landing_page_url") or "")) for l in w.get("locations", []) if (l.get("pdf_url") or l.get("landing_page_url"))]
    good = [l for l in locs if not blocked.search(l[1])]
    if good: print(d, "|", r["title"][:60], "|", [(v, u[:100]) for v, u in good][:3], flush=True)
