import sys, json, re, urllib.parse
sys.path.insert(0, '.')
from common import get
o = json.load(open(sys.argv[1]))
for d, v in sorted(o.items(), key=lambda kv: kv[1][0]):
    r = get("https://api.openalex.org/works/https://doi.org/" + urllib.parse.quote(d, safe="/"), params={"select": "open_access,locations"}, min_gap=0.8)
    if r.status_code != 200: print(d, r.status_code); continue
    w = r.json(); oa = w.get("open_access", {}).get("oa_status")
    locs = [(l.get("version"), (l.get("pdf_url") or l.get("landing_page_url") or "")[:85]) for l in w.get("locations", []) if l.get("is_oa")]
    print(d, v[0], v[1], "|", v[2][:75], "|", v[3][:18], "|", oa, "|", locs[:2], flush=True)
