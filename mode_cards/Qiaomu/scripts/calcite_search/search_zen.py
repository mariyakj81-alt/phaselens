import sys,re,json; sys.path.insert(0,'.')
from common import get
qs=["calcite Raman","Raman calcite spectra data","calcium carbonate Raman","CaCO3 Raman spectra","Mg-calcite Raman","carbonate Raman spectra","aragonite vaterite calcite Raman data","Raman spectra shell calcite","Raman spectra carbonate minerals high pressure","calcite high pressure Raman diamond anvil","Raman foraminifera calcite","Raman spectra limestone marble calcite","calcite Raman temperature","vaterite Raman spectra", "amorphous calcium carbonate Raman", "biomineral Raman spectra calcite"]
seen={}
for q in qs:
    for typ in ["dataset","publication"]:
      for page in [1,2]:
        r=get("https://zenodo.org/api/records", params={"q":q,"size":25,"page":page,"type":typ}, min_gap=3)
        if r.status_code!=200: print("fail",q,typ,r.status_code); break
        for h in r.json()["hits"]["hits"]:
            md=h["metadata"]; txt=(md.get("title","")+" "+re.sub(r"<.*?>"," ",md.get("description",""))).lower()
            if "raman" in txt and ("calcite" in txt or "caco" in txt or "calcium carbonate" in txt or "carbonate" in txt) and h["id"] not in seen:
                seen[h["id"]]=(md.get("publication_date"), md.get("title")[:110], md.get("doi"), [(f["key"],f["size"]) for f in h.get("files",[])][:4], [(x.get("relation"),x.get("identifier")) for x in md.get("related_identifiers",[])][:3])
for k,v in seen.items(): print(k, v)
print(len(seen))
