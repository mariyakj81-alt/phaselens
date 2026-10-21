import sys,os,json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_A import *
OUT = sys.argv[1]
qs = ['"calcite" AND "Raman" AND OPEN_ACCESS:y',
      '"Mg-calcite" AND "Raman" AND OPEN_ACCESS:y',
      '"magnesian calcite" AND "Raman" AND OPEN_ACCESS:y',
      '"CaCO3" AND "Raman" AND ("1086" OR "1085" OR "1087") AND OPEN_ACCESS:y',
      '"calcium carbonate" AND "Raman" AND ("1086" OR "1085" OR "1087") AND OPEN_ACCESS:y']
res = {}
for q in qs:
    hits, out = epmc_search(q, max_n=3000)
    n0=len(res)
    for w in out:
        k = w.get("pmcid") or w.get("doi") or w.get("id")
        if k in res: continue
        res[k] = {"pmcid": w.get("pmcid"), "doi": (w.get("doi") or "").lower(), "title": w.get("title"), "year": w.get("pubYear"),
                  "journal": w.get("journalTitle"), "cited": w.get("citedByCount"), "license": w.get("license"), "suppl": w.get("hasSuppl"),
                  "abstract": (w.get("abstractText") or "")[:1500], "authors": w.get("authorString"), "source": w.get("source"), "inEPMC": w.get("inEPMC"), "inPMC": w.get("inPMC"),
                  "pubType": str(w.get("pubTypeList"))[:120]}
    print(hits, len(out), "new", len(res)-n0, q, flush=True)
json.dump(res, open(OUT, "w"), indent=1)
print("total", len(res))
