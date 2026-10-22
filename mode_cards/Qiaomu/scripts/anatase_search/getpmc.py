"""Fetch a PMC OA paper: PDF (AWS PMC OA open-data bucket), JATS xml + SI zip (Europe PMC REST).
Usage: python -P getpmc.py PMCID OUTDIR   (OUTDIR = paper folder; creates paper.pdf, fulltext.xml, SI/)"""
import sys, os, requests, time, zipfile, io, json
sys.path.insert(0,os.path.dirname(__file__))
import dl
def get(pmc,out):
    os.makedirs(out,exist_ok=True)
    res={}
    # find latest version in bucket
    pdf=None
    for v in (1,2,3):
        u=f"https://pmc-oa-opendata.s3.amazonaws.com/{pmc}.{v}/{pmc}.{v}.pdf"
        ok,msg=dl.fetch(u,os.path.join(out,"paper.pdf"),gap=3)
        if ok: pdf=u; break
    res["pdf"]=pdf
    try:
        meta=requests.get(f"https://pmc-oa-opendata.s3.amazonaws.com/{pmc}.1/{pmc}.1.json",headers=dl.UA,timeout=60)
        res["license"]=meta.json().get("license_code") if meta.status_code==200 else None
    except Exception: pass
    time.sleep(2)
    x=requests.get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML",headers=dl.UA,timeout=90)
    if x.status_code==200:
        open(os.path.join(out,"fulltext.xml"),"wb").write(x.content); res["xml"]=True
    time.sleep(2)
    s=requests.get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/supplementaryFiles",headers=dl.UA,timeout=120)
    res["suppl_status"]=s.status_code
    if s.status_code==200 and s.content[:2]==b"PK":
        sd=os.path.join(out,"SI"); os.makedirs(sd,exist_ok=True)
        open(os.path.join(sd,"supplementary.zip"),"wb").write(s.content)
        try:
            z=zipfile.ZipFile(io.BytesIO(s.content)); names=z.namelist()
            ud=os.path.join(sd,"unzipped"); os.makedirs(ud,exist_ok=True)
            for n in names:
                p=os.path.realpath(os.path.join(ud,n))
                if not p.startswith(os.path.realpath(ud)): continue   # zip-slip guard
                if n.endswith("/"): os.makedirs(p,exist_ok=True); continue
                os.makedirs(os.path.dirname(p),exist_ok=True)
                open(p,"wb").write(z.read(n))
            res["si_files"]=names
        except Exception as e: res["si_err"]=str(e)
    else:
        res["suppl_head"]=s.content[:150].decode("latin1","replace")
    return res
if __name__=="__main__":
    print(json.dumps(get(sys.argv[1],sys.argv[2]),indent=1)[:1500])
