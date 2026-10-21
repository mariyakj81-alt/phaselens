import sys, json, re
sys.path.insert(0, '.')
from common import get
from known import known
K = known()
# preprint servers via Crossref prefix filter
res = {}
for pf, name in [("10.26434", "ChemRxiv"), ("10.31223", "EarthArXiv"), ("10.22541", "ESSOAr"), ("10.48550", "arXiv"), ("10.21203", "ResearchSquare"), ("10.20944", "Preprints.org"), ("10.1101", "bioRxiv")]:
    for q in ["calcite Raman", "calcium carbonate Raman spectroscopy", "carbonate minerals Raman spectra", "Mg-calcite Raman", "biogenic carbonate Raman", "CaCO3 polymorph Raman"]:
        r = get("https://api.crossref.org/works", params={"query.bibliographic": q, "filter": f"prefix:{pf}", "rows": 25, "select": "DOI,title,issued,author"}, min_gap=1.2)
        if r.status_code != 200: print("fail", pf, q, r.status_code); continue
        for it in r.json()["message"]["items"]:
            t = (it.get("title") or [""])[0]
            d = it["DOI"].lower()
            if re.search(r"raman|vibrational", t, re.I) and re.search(r"calcite|carbonate|CaCO|calcium|aragonite|shell|coral|lime|mortar|biomin", t, re.I):
                res[d] = (name, (it.get("issued", {}).get("date-parts") or [[None]])[0][0], (it.get("author") or [{}])[0].get("family", ""), t[:130])
for d, v in sorted(res.items(), key=lambda kv: kv[1][0]):
    print(d, v, "KNOWN" if d in K else "")
# arXiv API
r = get("http://export.arxiv.org/api/query", params={"search_query": 'all:calcite AND all:Raman', "max_results": 50}, min_gap=4)
for m in re.finditer(r"<entry>.*?<id>(.*?)</id>.*?<title>(.*?)</title>", r.text, re.S):
    print("arXiv", m.group(1), re.sub(r"\s+", " ", m.group(2))[:120])
