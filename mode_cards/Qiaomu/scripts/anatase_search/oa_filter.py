import requests, json, time, sys, os, html
UA={"User-Agent":"Mozilla/5.0 (compatible; RamanLitResearch/0.1; academic use)"}
STORE=os.path.join(os.path.dirname(__file__),"oa_candidates.json")
store=json.load(open(STORE,encoding="utf-8")) if os.path.exists(STORE) else {}
pages=int(os.environ.get("PAGES","2"))
for q in sys.argv[1:]:
  for page in range(1,pages+1):
    r=requests.get("https://api.openalex.org/works",params={"filter":"title_and_abstract.search:"+q,"sort":"cited_by_count:desc","per-page":50,"page":page,"select":"id,doi,title,publication_year,cited_by_count,open_access,best_oa_location,primary_location,authorships"},headers=UA,timeout=60)
    if r.status_code!=200:
        print("ERR",r.status_code,r.text[:200]); break
    d=r.json()
    if page==1: print("Q:",q,"count",d["meta"]["count"])
    for w in d["results"]:
        k=w["doi"] or w["id"]
        new=k not in store
        oa=w.get("open_access") or {}
        bl=w.get("best_oa_location") or {}
        pl=w.get("primary_location") or {}
        au=(w["authorships"][0]["author"]["display_name"] if w["authorships"] else "")
        store[k]={"title":w["title"],"year":w["publication_year"],"cites":w["cited_by_count"],"is_oa":oa.get("is_oa"),"pdf":bl.get("pdf_url"),"landing":bl.get("landing_page_url"),"journal":((pl.get("source") or {}).get("display_name")),"author":au}
        if new:
            print(f'{w["publication_year"]} c={w["cited_by_count"]:5} OA={int(bool(oa.get("is_oa")))} pdf={int(bool(bl.get("pdf_url")))} | {au[:16]} | {html.unescape(w["title"] or "")[:95]} | {(w["doi"] or "").replace("https://doi.org/","")} | {store[k]["journal"]}')
    time.sleep(2)
json.dump(store,open(STORE,"w",encoding="utf-8"))
