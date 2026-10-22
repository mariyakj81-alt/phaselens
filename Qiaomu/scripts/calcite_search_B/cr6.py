import sys, json, re
sys.path.insert(0, '.')
from common import get
from known import known
K = known()
cont = sys.argv[1]
pat = sys.argv[2] if len(sys.argv) > 2 else r"calcite|CaCO|calcium carbonate|lime|mortar|carbonate"
out = {}
for q in ["Raman calcite", "Raman spectroscopy lime mortar plaster", "micro-Raman carbonate pigment", "Raman limestone marble stone", "Raman spectroscopy shell", "Raman calcium carbonate"]:
    for off in (0, 100):
        r = get("https://api.crossref.org/works", params={"query.bibliographic": q, "query.container-title": cont, "rows": 100, "offset": off, "select": "DOI,title,issued,container-title,author,abstract"}, min_gap=1.0)
        if r.status_code != 200: continue
        for it in r.json()["message"]["items"]:
            d = it["DOI"].lower()
            if d in K or d in out: continue
            if cont.lower() not in (it.get("container-title") or [""])[0].lower(): continue
            ab = re.sub(r"<[^>]+>", " ", it.get("abstract", "") or "")
            t = (it.get("title") or [""])[0]
            if re.search("raman", t + ab, re.I) and re.search(pat, t + ab, re.I):
                out[d] = ((it.get("issued", {}).get("date-parts") or [[None]])[0][0], (it.get("author") or [{}])[0].get("family", ""), t[:100], len(re.findall("calcite", ab, re.I)))
for d, v in sorted(out.items(), key=lambda kv: kv[1][0] or 0): print(d, *v, sep=" | ")
