"""Build a pool of Europe PMC OA papers (full-text match) and score their full-text XML for anatase Raman evidence."""
import requests, json, time, sys, os, re, html
UA={"User-Agent":"Mozilla/5.0 (compatible; RamanLitResearch/0.1; academic use)"}
HERE=os.path.dirname(__file__)
POOL=os.path.join(HERE,"epmc_pool.json")
pool=json.load(open(POOL,encoding="utf-8")) if os.path.exists(POOL) else {}
def search(q,pages=3):
    cm="*"
    for p in range(pages):
        r=requests.get("https://www.ebi.ac.uk/europepmc/webservices/rest/search",params={"query":q,"format":"json","resultType":"lite","pageSize":100,"cursorMark":cm,"sort":"CITED desc"},headers=UA,timeout=60)
        d=r.json()
        for x in d["resultList"]["result"]:
            if x.get("pmcid") and x["pmcid"] not in pool:
                pool[x["pmcid"]]={"title":x["title"],"year":x.get("pubYear"),"doi":x.get("doi"),"journal":x.get("journalTitle"),"author":x.get("authorString","")[:40],"score":None}
        nc=d.get("nextCursorMark")
        if not nc or nc==cm: break
        cm=nc; time.sleep(1.5)
MODES={"Eg1":(139,150),"Eg2":(193,203),"B1g1":(393,405),"A1g":(507,525),"Eg3":(632,645)}
def score_xml(x):
    t=re.sub(r"<[^>]+>"," ",x); t=html.unescape(t)
    nr=len(re.findall(r"Raman",t)); na=len(re.findall(r"anatase",t,re.I))
    nm={}
    for k,(lo,hi) in MODES.items():
        c=0
        for m in re.finditer(r"(?<![\d.])(\d{3})(?:\.\d+)?(?![\d])",t):
            v=int(m.group(1))
            if lo<=v<=hi:
                ctx=t[max(0,m.start()-80):m.end()+80]
                if re.search(r"cm|Raman|mode|shift",ctx): c+=1
        nm[k]=c
    sym=len(re.findall(r"\bE\s?g\b|\bB\s?1g\b|\bA\s?1g\b",t))
    return {"raman":nr,"anatase":na,"modes":nm,"sym":sym,"modehit":sum(1 for v in nm.values() if v)}
if __name__=="__main__":
    qs=sys.argv[1:]
    for q in qs:
        search(q); print("pool",len(pool),flush=True)
    json.dump(pool,open(POOL,"w",encoding="utf-8"))
    todo=[k for k,v in pool.items() if v["score"] is None]
    print("to score",len(todo),flush=True)
    for i,k in enumerate(todo):
        try:
            r=requests.get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{k}/fullTextXML",headers=UA,timeout=90)
            if r.status_code==200: pool[k]["score"]=score_xml(r.text)
            else: pool[k]["score"]={"err":r.status_code}
        except Exception as e:
            pool[k]["score"]={"err":str(e)[:50]}
        if i%20==0:
            json.dump(pool,open(POOL,"w",encoding="utf-8")); print(i,flush=True)
        time.sleep(1.2)
    json.dump(pool,open(POOL,"w",encoding="utf-8"))
    print("done")
