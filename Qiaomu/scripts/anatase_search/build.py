"""Build paper folders for anatase/ from specs.py. Usage: python -P build.py [ids...]  (ids = 1-based spec indices; default all)
Downloads only from: AWS PMC OA bucket, Europe PMC REST, or files already staged (verified) in the scratchpad stage dir. No challenge evasion."""
import os, sys, json, re, shutil, time, zipfile, unicodedata, requests
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
import dl, getpmc, screen
from specs import SPECS
ROOT=os.path.abspath(os.path.join(HERE,"..",".."))
OUT=os.path.join(ROOT,"anatase")
STAGE=os.environ["STAGE"]
STATE=os.path.join(HERE,"build_state.json")
state=json.load(open(STATE,encoding="utf-8")) if os.path.exists(STATE) else {}
def ascii_(s): return re.sub(r"[^A-Za-z0-9]","",unicodedata.normalize("NFKD",s).encode("ascii","ignore").decode())
def crossref(doi):
    r=requests.get("https://api.crossref.org/works/"+doi,headers=dl.UA,timeout=60)
    if r.status_code!=200: return {}
    m=r.json()["message"]
    t=re.sub(r"<[^>]+>","",(m.get("title") or [""])[0])
    au=(m.get("author") or [{}])[0]
    y=(m.get("issued",{}).get("date-parts",[[None]])[0][0])
    return {"title":re.sub(r"\s+"," ",t),"first_author":au.get("family",""),"given":au.get("given",""),"year":y,"journal":(m.get("container-title") or [""])[0]}
IMG=re.compile(r"(?:-|_)(?:g|f|fig|figure)\d+[A-Za-z0-9_]*\.(?:gif|jpg|jpeg|png|tif|tiff)$",re.I)
def unzip_safe(zpath,dest):
    os.makedirs(dest,exist_ok=True); out=[]
    z=zipfile.ZipFile(zpath)
    for n in z.namelist():
        p=os.path.realpath(os.path.join(dest,n))
        if not p.startswith(os.path.realpath(dest)+os.sep): continue
        if n.endswith("/"): os.makedirs(p,exist_ok=True); continue
        os.makedirs(os.path.dirname(p),exist_ok=True)
        open(p,"wb").write(z.read(n)); out.append(p)
    return out
DATAEXT={".xlsx",".xls",".csv",".txt",".dat",".tsv",".json",".spc",".jdx",".opju",".jnb",".xlsm",".ods"}
def process(i,spec,override=None):
    doi=spec["doi"]
    meta=state.get(doi,{}).get("meta") or crossref(doi); time.sleep(1)
    meta=dict(meta); meta.update(override or {})
    fa=ascii_(meta.get("first_author") or "Unknown"); yr=meta.get("year")
    folder=f"ANA{i:02d}_{fa}{yr}"
    d=os.path.join(OUT,folder); os.makedirs(d,exist_ok=True)
    rec={"folder":folder,"meta":meta,"spec":spec}
    pdf=os.path.join(d,"paper.pdf")
    if spec.get("pmc"):
        res=getpmc.get(spec["pmc"],d)   # writes paper.pdf, fulltext.xml, SI/supplementary.zip + SI/unzipped
        rec["pmc_res"]={k:v for k,v in res.items() if k!="si_files"}
        rec["si_listing"]=res.get("si_files",[])
        rec["src_url"]=res.get("pdf")
    else:
        shutil.copyfile(os.path.join(STAGE,spec["stage"]),pdf); rec["src_url"]=spec["src_url"]
    # tidy SI: drop article-figure images, unzip nested zips, mirror data files
    sid=os.path.join(d,"SI"); ded=os.path.join(d,"data")
    si_files=[]; data_files=[]
    if os.path.isdir(sid):
        ud=os.path.join(sid,"unzipped")
        if os.path.isdir(ud):
            for root,_,files in os.walk(ud):
                for f in files:
                    p=os.path.join(root,f)
                    if IMG.search(f): os.remove(p)
            # unzip nested zips
            for root,_,files in list(os.walk(ud)):
                for f in files:
                    if f.lower().endswith(".zip"):
                        p=os.path.join(root,f)
                        try: unzip_safe(p,os.path.join(root,os.path.splitext(f)[0]+"_x"))
                        except Exception as e: rec.setdefault("zip_err",[]).append(str(e))
        # keep supplementary.zip only if unzipped has content
        for root,_,files in os.walk(sid):
            for f in files:
                p=os.path.join(root,f); rel=os.path.relpath(p,d).replace("\\","/")
                if os.path.splitext(f)[1].lower() in DATAEXT:
                    os.makedirs(ded,exist_ok=True)
                    tgt=os.path.join(ded,re.sub(r"[\/]+","__",os.path.relpath(p,sid)))
                    shutil.copyfile(p,tgt); data_files.append(os.path.relpath(tgt,d).replace("\\","/"))
                si_files.append(rel)
        if not si_files or all(f.endswith("supplementary.zip") for f in si_files):
            # only the zip with no useful content -> remove SI dir
            if not os.path.isdir(os.path.join(sid,"unzipped")) or not any(os.scandir(os.path.join(sid,"unzipped"))):
                shutil.rmtree(sid,ignore_errors=True); si_files=[]
    rec["si_files"]=si_files; rec["data_files"]=data_files
    state[doi]=rec
    json.dump(state,open(STATE,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
    return rec
if __name__=="__main__":
    ids=[int(x) for x in sys.argv[1:]] or list(range(1,len(SPECS)+1))
    for i in ids:
        spec=SPECS[i-1]
        try:
            rec=process(i,spec)
            print(i,rec["folder"],"| SI",len(rec["si_files"]),"| data",len(rec["data_files"]),"|",rec.get("src_url","")[:70],flush=True)
        except Exception as e:
            print(i,spec["doi"],"ERR",e,flush=True)
