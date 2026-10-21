import sys, json, re
sys.path.insert(0, '.')
from common import get
from known import known
K = known()
out = {}
lics = ["https://creativecommons.org/licenses/by/4.0/", "https://creativecommons.org/licenses/by/3.0/", "https://creativecommons.org/licenses/by-nc/4.0/", "https://creativecommons.org/licenses/by-nc-nd/4.0/", "https://creativecommons.org/licenses/by-nc-nd/3.0/", "https://creativecommons.org/licenses/by-nc/3.0/"]
qs = ["calcite Raman spectra peak positions", "Raman spectroscopy calcium carbonate calcite", "Mg-calcite Raman carbonate", "carbonate minerals Raman"]
for lic in lics:
    for q in qs:
        for off in (0, 50):
            p = {"query": q, "rows": 50, "offset": off, "filter": f"license.url:{lic},type:journal-article", "select": "DOI,title,issued,container-title,author"}
            r = get("https://api.crossref.org/works", params=p, min_gap=1.0)
            if r.status_code != 200: print("fail", r.status_code); continue
            for it in r.json()["message"]["items"]:
                d = it["DOI"].lower()
                if d in K or d in out: continue
                t = (it.get("title") or [""])[0]
                if not re.search(r"calcite|carbonate|CaCO|calcium|aragonite|lime|mortar|limestone|marble|shell|coral|speleothem|foram|coccol|cement|biomineral", t, re.I): continue
                out[d] = ((it.get("issued", {}).get("date-parts") or [[None]])[0][0], (it.get("author") or [{}])[0].get("family", ""), t[:110], (it.get("container-title") or [""])[0][:28])
    print(lic[-12:], len(out), flush=True)
json.dump(out, open("cr3.json", "w"))
for d, v in sorted(out.items(), key=lambda kv: kv[1][3]): print(d, *v, sep=" | ")
