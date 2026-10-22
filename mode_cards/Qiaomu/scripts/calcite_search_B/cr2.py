import sys, json, re
sys.path.insert(0, '.')
from common import get
from known import known
K = known()
terms = ["calcite Raman", "Raman spectroscopy calcite", "Raman spectra calcite", "Raman calcium carbonate", "Raman spectroscopy calcium carbonate", "Raman spectra carbonate minerals",
         "Raman carbonate", "Raman Mg-calcite", "Raman magnesian calcite", "Raman aragonite calcite", "Raman vaterite", "Raman biogenic carbonate", "Raman shell calcite",
         "Raman limestone", "Raman marble", "Raman speleothem", "Raman high pressure carbonate", "Raman carbonate temperature", "Raman lattice modes carbonate",
         "Raman dolomite", "Raman spectra carbonates calcite group", "Raman coral skeleton", "Raman foraminifera", "Raman coccolith", "Raman echinoderm", "Raman otolith",
         "Raman mortar lime", "Raman carbonate meteorite", "Raman carbonate pigment", "micro-Raman carbonate", "Raman polymorph CaCO3", "Raman amorphous calcium carbonate calcite",
         "Raman calcite crystal orientation", "Raman calcite isotope", "Raman spectra rocks carbonate", "Raman carbonate cement", "Raman travertine", "Raman carbonatite"]
out = {}
for q in terms:
    for off in (0, 50):
        p = {"query.title": q, "rows": 50, "offset": off, "select": "DOI,title,issued,container-title,license,author,type", "filter": "type:journal-article"}
        try:
            r = get("https://api.crossref.org/works", params=p, min_gap=1.2)
        except Exception as e:
            print("exc", q, e); continue
        if r.status_code != 200: print("fail", q, r.status_code); continue
        for it in r["message"]["items"] if False else r.json()["message"]["items"]:
            d = it["DOI"].lower()
            if d in K or d in out: continue
            t = (it.get("title") or [""])[0]
            if not re.search(r"raman", t, re.I): continue
            y = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
            lic = [l["URL"] for l in it.get("license", []) if "creativecommons" in l["URL"]]
            out[d] = dict(t=t, y=y, j=(it.get("container-title") or [""])[0], lic=lic[:1], au=(it.get("author") or [{}])[0].get("family", ""))
    print(q, len(out), flush=True)
json.dump(out, open("cr2_results.json", "w"), indent=1)
