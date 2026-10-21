import sys,re,json,time; sys.path.insert(0,'.')
from common import get
OUT=sys.argv[1]
qs=["calcite Raman spectrum","calcite Raman peak positions","Raman spectroscopy calcite high pressure","calcite Raman temperature","Mg calcite Raman","biogenic calcite Raman spectroscopy","calcium carbonate polymorphs Raman calcite aragonite vaterite","calcite lattice modes Raman","calcite Raman isotope","calcite Raman laser excitation wavelength","calcite Raman single crystal polarization","carbonate Raman spectra calcite dolomite magnesite","calcite nanoparticles Raman","calcite Raman shock","amorphous calcium carbonate calcite Raman","speleothem calcite Raman","calcite Raman cement mortar","limestone marble Raman calcite","calcite shells Raman mollusc","echinoderm calcite Raman","foraminifera Raman Mg calcite", "coccolithophore Raman calcite", "calcite Raman microfluidic precipitation in situ", "calcite Raman Mars", "calcite Raman anharmonic"]
res={}
for q in qs:
    for off in (0,100):
        r=get("https://api.semanticscholar.org/graph/v1/paper/search", params={"query":q,"fields":"title,year,externalIds,openAccessPdf,venue,abstract","limit":100,"offset":off}, min_gap=3)
        if r.status_code!=200: print("fail",q,off,r.status_code); time.sleep(5); continue
        for p in r.json().get("data",[]):
            doi=(p["externalIds"] or {}).get("DOI")
            if not doi: continue
            e=res.setdefault(doi.lower(),{"doi":doi.lower(),"title":p["title"],"year":p["year"],"venue":p["venue"],"oa":(p.get("openAccessPdf") or {}).get("url"),"abs":(p.get("abstract") or "")[:600],"n":0})
            e["n"]+=1
    print(q,len(res),flush=True)
json.dump(res,open(OUT,"w"),indent=1)
