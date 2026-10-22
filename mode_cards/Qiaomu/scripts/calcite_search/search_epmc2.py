import sys,re,json; sys.path.insert(0,'.')
from common import get
OUT=sys.argv[1]
qs = ['(TITLE:"calcite" OR ABSTRACT:"calcite") AND (TITLE:"Raman" OR ABSTRACT:"Raman") AND OPEN_ACCESS:y',
      '(TITLE:"calcium carbonate" OR ABSTRACT:"calcium carbonate") AND (TITLE:"Raman" OR ABSTRACT:"Raman") AND OPEN_ACCESS:y',
      '(ABSTRACT:"Mg-calcite" OR ABSTRACT:"magnesian calcite" OR ABSTRACT:"high-Mg calcite") AND ABSTRACT:"Raman" AND OPEN_ACCESS:y',
      '(ABSTRACT:"carbonate" AND ABSTRACT:"Raman" AND (ABSTRACT:"calcite" OR ABSTRACT:"CaCO3")) AND OPEN_ACCESS:y']
res={}
for q in qs:
    cursor="*"; tot=0
    for page in range(6):
        r=get("https://www.ebi.ac.uk/europepmc/webservices/rest/search", params={"query":q,"format":"json","resultType":"core","pageSize":100,"cursorMark":cursor}, min_gap=1)
        if r.status_code!=200: print("fail",r.status_code); break
        j=r.json()
        for w in j["resultList"]["result"]:
            k=w.get("pmcid") or w.get("doi") or w.get("id")
            res.setdefault(k,{"pmcid":w.get("pmcid"),"doi":w.get("doi"),"title":w.get("title"),"year":w.get("pubYear"),"journal":w.get("journalTitle"),"cited":w.get("citedByCount"),"license":w.get("license"),"suppl":w.get("hasSuppl"),"abs":(w.get("abstractText") or "")[:1500]})
            tot+=1
        nc=j.get("nextCursorMark")
        if not nc or nc==cursor or len(j["resultList"]["result"])<100: break
        cursor=nc
    print(j.get("hitCount"), q[:70], tot, len(res), flush=True)
json.dump(res,open(OUT,"w"),indent=1)
