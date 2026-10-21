import sys, json, re
sys.path.insert(0, '.')
from common import get
from known import known
K = known()
queries = ["calcite Raman spectra", "calcite Raman peak positions", "Mg-calcite Raman", "calcite Raman high pressure", "calcite Raman temperature dependence",
           "calcium carbonate polymorphs Raman", "Raman spectroscopy carbonate minerals calcite", "biogenic calcite Raman", "calcite lattice modes Raman",
           "Raman calcite isotope", "Raman calcite single crystal polarized", "Raman spectra carbonates calcite dolomite magnesite", "Raman speleothem calcite",
           "Raman foraminifera calcite", "Raman calcite mortar", "Raman calcite pigment lime white", "Raman calcite meteorite", "Raman calcite shell prismatic layer",
           "Raman calcite coccolith", "Raman echinoderm calcite magnesium"]
prefixes = {"10.5194": "Copernicus", "10.3389": "Frontiers", "10.2465": "JSTAGE-JMPS", "10.2343": "JSTAGE-analsci", "10.2138": "AmMin", "10.3749": "CanMin",
            "10.7185": "GeochemPersp", "10.26434": "ChemRxiv", "10.31223": "EarthArXiv", "10.22541": "ESSOAr", "10.1038": "Nature", "10.1186": "BMC", "10.1007": "Springer",
            "10.1127": "Schweizerbart", "10.2113": "GSW?", "10.2343/geochemj": "geochemj"}
out = {}
def run(q, filt=None, rows=40):
    p = {"query.bibliographic": q, "rows": rows, "select": "DOI,title,issued,container-title,license,author,type"}
    if filt: p["filter"] = filt
    try:
        r = get("https://api.crossref.org/works", params=p, min_gap=1.5)
    except Exception as e:
        print("exc", q, e); return
    if r.status_code != 200: print("fail", q, filt, r.status_code); return
    for it in r.json()["message"]["items"]:
        d = it["DOI"].lower()
        t = (it.get("title") or [""])[0]
        if d in K or d in out: continue
        y = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
        lic = [l["URL"] for l in it.get("license", []) if "creativecommons" in l["URL"] or "open" in l["URL"].lower()]
        au = (it.get("author") or [{}])[0].get("family", "")
        out[d] = dict(t=t, y=y, j=(it.get("container-title") or [""])[0], lic=bool(lic), au=au, type=it.get("type"), q=q)
for q in queries:
    run(q)
    print(q, len(out), flush=True)
for pf, name in prefixes.items():
    for q in ["calcite Raman spectra", "calcium carbonate Raman", "carbonate Raman"]:
        run(q, filt="prefix:" + pf.split("/")[0] if "/" not in pf or pf.startswith("10.") and pf.count("/") == 0 else None, rows=30)
    print(pf, len(out), flush=True)
json.dump(out, open("cr_results.json", "w"), indent=1)
kw = re.compile(r"raman", re.I)
for d, v in sorted(out.items(), key=lambda kv: (kv[1]["y"] or 0)):
    if kw.search(v["t"]) or "calcite" in v["t"].lower() or "carbonate" in v["t"].lower():
        print(d, v["y"], v["au"], "|", v["t"][:100], "|", v["j"][:30], "| OA" if v["lic"] else "")
