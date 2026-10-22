import requests, json, time, sys, html, os
UA={"User-Agent":"Mozilla/5.0 (compatible; RamanLitResearch/0.1; academic use)"}
BASE="https://www.ebi.ac.uk/europepmc/webservices/rest/search"
STORE=os.path.join(os.path.dirname(__file__),"epmc_candidates.json")
store=json.load(open(STORE,encoding="utf-8")) if os.path.exists(STORE) else {}
queries=sys.argv[1:]
for q in queries:
    r=requests.get(BASE,params={"query":q,"format":"json","resultType":"core","pageSize":100},headers=UA,timeout=60)
    d=r.json()
    print("Q:",q,"hits",d.get("hitCount"))
    for x in d["resultList"]["result"]:
        key=x.get("doi") or x.get("pmcid") or x.get("id")
        new = key not in store
        store[key]={k:x.get(k) for k in ("pmcid","pubYear","isOpenAccess","hasSuppl","title","doi","authorString","journalTitle","abstractText")}
        if new:
            t=html.unescape(x["title"]).replace("<sub>","").replace("</sub>","").replace("<i>","").replace("</i>","")
            print(f'{x.get("pmcid","-"):12} {x.get("pubYear")} OA={x.get("isOpenAccess")} SI={x.get("hasSuppl")} | {(x.get("authorString") or "")[:18]} | {t[:100]} | {x.get("doi")}')
    time.sleep(1.5)
json.dump(store,open(STORE,"w",encoding="utf-8"))
