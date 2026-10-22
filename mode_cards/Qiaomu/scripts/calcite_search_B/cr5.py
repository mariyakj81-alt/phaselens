import sys, json, re
sys.path.insert(0, '.')
from common import get
from known import known
K = known()
out = {}
qs = ["calcite Raman spectroscopy", "Raman spectra carbonate calcite peak"]
for y in range(1996, 2027):
    for q in qs:
        p = {"query.bibliographic": q, "rows": 100, "filter": f"from-pub-date:{y}-01-01,until-pub-date:{y}-12-31,type:journal-article,has-abstract:true", "select": "DOI,title,issued,container-title,author,abstract"}
        try:
            r = get("https://api.crossref.org/works", params=p, min_gap=1.0)
        except Exception as e:
            print("exc", y, q); continue
        if r.status_code != 200: print("fail", y, r.status_code); continue
        for it in r.json()["message"]["items"]:
            d = it["DOI"].lower()
            if d in K or d in out: continue
            ab = re.sub(r"<[^>]+>", " ", it.get("abstract", "") or "").lower()
            t = (it.get("title") or [""])[0]
            txt = ab + " " + t.lower()
            if "raman" in txt and ("calcite" in txt or "caco3" in txt or "calcium carbonate" in txt or "mg-calcite" in txt):
                out[d] = (y, (it.get("author") or [{}])[0].get("family", ""), t[:110], (it.get("container-title") or [""])[0][:28], ab.count("calcite"))
    print(y, len(out), flush=True)
json.dump(out, open("cr5.json", "w"))
