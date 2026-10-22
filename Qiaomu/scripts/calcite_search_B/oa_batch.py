import sys, json, re, urllib.parse
sys.path.insert(0, '.')
from common import get
from known import known
K = known()
pool = {}
for f in ("cr2_results.json", "cr_results.json"):
    pool.update(json.load(open(f)))
inc = re.compile(r"calcite|carbonate|CaCO|aragonite|vaterite|limestone|marble|mortar|cement|speleothem|foram|coccol|otolith|echino|biominer|pearl|shell|coral|lime\b|travertine|dolomite|stromatolit|chondrite|meteorite|Mg-", re.I)
exc = re.compile(r"core.?shell|SERS|surface.enhanced|shell-isolated|propylene|ethylene|dimethyl|lithium|battery|electrolyte|molten|hydration shell|ethylene|polymer|CdSe|nanowire|aluminate|glass|apatite|enamel|teeth|tooth|hydrotalcite|uranyl|silicate hydrate|CO2 capture|solution", re.I)
sel = []
for d, v in pool.items():
    t = v["t"]
    if d in K or (v.get("y") or 0) < 1980: continue
    if not re.search("raman", t, re.I): continue
    if inc.search(t) and not exc.search(t): sel.append((d, v))
print(len(sel), flush=True)
for d, v in sorted(sel, key=lambda x: x[1]["y"] or 0):
    r = get("https://api.openalex.org/works/https://doi.org/" + urllib.parse.quote(d, safe="/"), params={"select": "open_access,locations"}, min_gap=0.8)
    if r.status_code != 200: print(d, r.status_code); continue
    w = r.json(); oa = w.get("open_access", {}).get("oa_status")
    locs = [(l.get("version"), (l.get("pdf_url") or l.get("landing_page_url") or "")[:90]) for l in w.get("locations", []) if l.get("is_oa")]
    if oa != "closed": print(d, v["y"], v["au"], "|", v["t"][:80], "|", oa, "|", locs[:3], flush=True)
