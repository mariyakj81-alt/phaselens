"""Collect all Europe PMC OA records matching anatase AND Raman (lite metadata) -> pool_all.json"""
import requests, json, time, os
UA={"User-Agent":"Mozilla/5.0 (compatible; RamanLitResearch/0.1; academic use)"}
HERE=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(HERE,"pool_all.json")
pool={}
def run(q):
    cm="*"
    while True:
        r=requests.get("https://www.ebi.ac.uk/europepmc/webservices/rest/search",params={"query":q+" AND OPEN_ACCESS:y","format":"json","resultType":"lite","pageSize":500,"cursorMark":cm},headers=UA,timeout=120)
        d=r.json()
        res=d["resultList"]["result"]
        for x in res:
            if x.get("pmcid"):
                pool.setdefault(x["pmcid"],{"title":x.get("title"),"year":x.get("pubYear") or (x.get("firstPublicationDate") or "")[:4],"doi":x.get("doi"),"journal":x.get("journalTitle"),"authors":x.get("authorString","")[:60],"hasSuppl":x.get("hasSuppl"),"cited":x.get("citedByCount")})
        nc=d.get("nextCursorMark")
        print(q,len(pool),flush=True)
        if not res or not nc or nc==cm: break
        cm=nc; time.sleep(2)
for q in ['"anatase" AND "Raman"']:
    run(q)
json.dump(pool,open(OUT,"w",encoding="utf-8"))
print("total",len(pool))
