import requests, json, time, sys, os, html, re
UA={"User-Agent":"Mozilla/5.0 (compatible; RamanLitResearch/0.1; academic use)"}
STORE=os.path.join(os.path.dirname(__file__),"oa_candidates.json")
store=json.load(open(STORE,encoding="utf-8")) if os.path.exists(STORE) else {}
pages=int(os.environ.get("PAGES","3")); pat=re.compile(os.environ.get("PAT","raman|phonon|vibrat|spectro|lattice dynamics"),re.I)
extra=os.environ.get("EXTRA","open_access.is_oa:true")
for q in sys.argv[1:]:
  for page in range(1,pages+1):
    r=requests.get("https://api.openalex.org/works",params={"filter":"title_and_abstract.search:"+q+","+extra,"sort":"cited_by_count:desc","per-page":50,"page":page,"select":"id,doi,title,publication_year,cited_by_count,open_access,best_oa_location,primary_location,authorships,locations"},headers=UA,timeout=60)
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
        pdfs=[l.get("pdf_url") for l in (w.get("locations") or []) if l.get("pdf_url")]
        store[k]={"title":w["title"],"year":w["publication_year"],"cites":w["cited_by_count"],"is_oa":oa.get("is_oa"),"pdf":bl.get("pdf_url"),"pdfs":pdfs,"landing":bl.get("landing_page_url"),"journal":((pl.get("source") or {}).get("display_name")),"author":au}
        if new and pat.search(w["title"] or ""):
            print(f'{w["publication_year"]} c={w["cited_by_count"]:4} pdfs={len(pdfs)} | {au[:14]} | {html.unescape(w["title"] or "")[:100]} | {(w["doi"] or "").replace("https://doi.org/","")} | {(store[k]["journal"] or "")[:30]}')
    time.sleep(2)
json.dump(store,open(STORE,"w",encoding="utf-8"))
