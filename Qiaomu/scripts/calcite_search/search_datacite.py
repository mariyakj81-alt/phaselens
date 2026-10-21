import sys,re,json; sys.path.insert(0,'.')
from common import get
qs=["calcite Raman","calcium carbonate Raman spectra","Mg-calcite Raman","carbonate Raman spectra","calcite Raman spectroscopy dataset","Raman spectra calcite aragonite","Raman spectra biogenic calcite","Raman spectra carbonate minerals","calcite polymorph Raman","CaCO3 Raman"]
seen={}
for q in qs:
    for page in (1,2,3):
        r=get("https://api.datacite.org/dois", params={"query":q,"resource-type-id":"dataset","page[size]":100,"page[number]":page}, min_gap=2)
        if r.status_code!=200: print("fail",q,page,r.status_code); break
        d=r.json().get("data",[])
        if not d: break
        for it in d:
            a=it["attributes"]; title=(a.get("titles") or [{}])[0].get("title","") or ""
            desc=" ".join(x.get("description","") for x in (a.get("descriptions") or []))
            txt=(title+" "+desc).lower()
            if "raman" in txt and ("calcite" in txt or "caco" in txt or "calcium carbonate" in txt):
                if it["id"] not in seen:
                    seen[it["id"]]=(a.get("publicationYear"), a.get("publisher"), title[:110], [ (x.get("relatedIdentifier"),x.get("relationType")) for x in (a.get("relatedIdentifiers") or [])][:3])
    print(q, len(seen), flush=True)
for k,v in sorted(seen.items(), key=lambda kv: kv[1][0] or 0, reverse=True): print(k, v)
