import sys, json, re
sys.path.insert(0, '.')
from common import get
from known import known
K = known()
def run(prefix, qs, pat, rows=100, extra=""):
    out = {}
    for q in qs:
        for off in (0, 100):
            p = {"query.bibliographic": q, "rows": rows, "offset": off, "filter": f"prefix:{prefix}" + extra, "select": "DOI,title,issued,container-title,author,abstract"}
            r = get("https://api.crossref.org/works", params=p, min_gap=1.0)
            if r.status_code != 200: print("fail", r.status_code); continue
            for it in r.json()["message"]["items"]:
                d = it["DOI"].lower()
                if d in K or d in out: continue
                t = (it.get("title") or [""])[0]; ab = it.get("abstract", "") or ""
                if re.search(pat, t + " " + ab, re.I):
                    out[d] = ((it.get("issued", {}).get("date-parts") or [[None]])[0][0], (it.get("author") or [{}])[0].get("family", ""), t[:110], (it.get("container-title") or [""])[0][:25])
    return out
pref = sys.argv[1]
res = run(pref, ["Raman calcite", "Raman spectroscopy carbonate", "Raman spectra calcium carbonate", "micro-Raman carbonate mineral", "Raman biogenic carbonate"], r"raman")
for d, v in sorted(res.items(), key=lambda kv: kv[1][0] or 0): print(d, *v, sep=" | ")
