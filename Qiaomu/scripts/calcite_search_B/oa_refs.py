import sys, json, re, urllib.parse
sys.path.insert(0, '.')
from common import get
from known import known
K = known()
blocked = re.compile(r"mdpi\.com|wiley|pubs\.rsc|link\.springer|sciencedirect|pubs\.acs|iopscience|tandfonline|academic\.oup|hal\.science|opus4|europepmc|ncbi\.nlm|aps\.org|aip\.|degruyter|geoscienceworld|nature\.com", re.I)
lines = open("refrank.txt", encoding="utf-8").read().splitlines()[1:]
dois = []
for l in lines:
    m = re.match(r"\d+ \| (10\.[^ ]+) \| (\w+) \| ([^|]*)\| (.*)", l)
    if m and m.group(1) not in K: dois.append((m.group(1), m.group(2), m.group(3).strip(), m.group(4)[:70]))
print(len(dois), flush=True)
for d, y, au, t in dois:
    if not re.search(r"raman|vibrat|spectr|calcite|carbonate|aragonite|vaterite|coral|shell|mortar|biomin|ikaite|CaCO", t, re.I): continue
    x = get("https://api.openalex.org/works/https://doi.org/" + urllib.parse.quote(d, safe="/"), params={"select": "open_access,locations"}, min_gap=0.8)
    if x.status_code != 200: continue
    w = x.json()
    locs = [(l.get("version"), (l.get("pdf_url") or l.get("landing_page_url") or "")) for l in w.get("locations", []) if l.get("is_oa") and (l.get("pdf_url") or l.get("landing_page_url"))]
    good = [l for l in locs if not blocked.search(l[1]) or "nature.com" in l[1]]
    if good: print(d, y, au, "|", t, "|", [(v, u[:95]) for v, u in good][:2], flush=True)
