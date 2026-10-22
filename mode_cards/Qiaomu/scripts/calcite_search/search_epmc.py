import sys,re,json; sys.path.insert(0,'.')
from common import get
OUT=sys.argv[1]
qs = ['"calcite" AND "Raman" AND "1086" AND "712" AND "282" AND OPEN_ACCESS:y',
      '"calcite" AND "Raman" AND "1085" AND "713" AND "281" AND OPEN_ACCESS:y',
      '"calcite" AND "Raman" AND "1087" AND "154" AND "1436" AND OPEN_ACCESS:y',
      '"calcite" AND "Raman" AND "1749" AND OPEN_ACCESS:y',
      '"calcite" AND "Raman" AND "FWHM" AND "1086" AND OPEN_ACCESS:y',
      '"calcite" AND "Raman" AND "lattice mode" AND OPEN_ACCESS:y',
      '"Mg-calcite" AND "Raman" AND "1086" AND OPEN_ACCESS:y',
      '"calcite" AND "Raman" AND "532 nm" AND "1086" AND OPEN_ACCESS:y',
      '"calcite" AND "Raman" AND "785 nm" AND "1086" AND OPEN_ACCESS:y',
      '"calcite" AND "Raman" AND "514" AND "1086" AND OPEN_ACCESS:y',
      '"calcite" AND "Raman" AND "633 nm" AND "1086" AND OPEN_ACCESS:y',
      '"calcite" AND "Raman" AND "488 nm" AND "1086" AND OPEN_ACCESS:y',
      '"calcite" AND "Raman" AND "1086" AND "high pressure" AND OPEN_ACCESS:y',
      '"calcite" AND "Raman" AND "1086" AND "temperature" AND "peak position" AND OPEN_ACCESS:y',
      '"calcite" AND "Raman" AND "1086" AND "aragonite" AND "vaterite" AND OPEN_ACCESS:y',
      '"calcite" AND "Raman" AND "1086" AND "supplementary" AND HAS_SUPPL:y',
]
res={}
for q in qs:
    r=get("https://www.ebi.ac.uk/europepmc/webservices/rest/search", params={"query":q,"format":"json","resultType":"core","pageSize":100,"sort":"CITED desc"}, min_gap=1)
    if r.status_code!=200: print("fail",q[:60],r.status_code); continue
    j=r.json(); n=0
    for w in j["resultList"]["result"]:
        k=w.get("pmcid") or w.get("doi") or w.get("id")
        e=res.setdefault(k,{"pmcid":w.get("pmcid"),"doi":w.get("doi"),"title":w.get("title"),"year":w.get("pubYear"),"journal":w.get("journalTitle"),"cited":w.get("citedByCount"),"license":w.get("license"),"suppl":w.get("hasSuppl"),"q":[]})
        e["q"].append(len(e["q"])); n+=1
    print(j.get("hitCount"), q[:80], n, len(res), flush=True)
json.dump(res,open(OUT,"w"),indent=1)
