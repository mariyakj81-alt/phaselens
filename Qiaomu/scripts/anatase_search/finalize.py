"""Reorder/rename existing folders to the final ANA01..ANA33 layout and build any new ones. python -P finalize.py"""
import os, sys, json, shutil, re
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
os.environ.setdefault("STAGE","")
import build
ROOT=build.ROOT; OUT=build.OUT; state=build.state
# (doi, override-or-None, new-spec-or-None)
FINAL=[
 ("10.1088/0022-3727/33/8/305",{"first_author":"Zhang","given":"W. F."},None),
 ("10.1002/jrs.2427",{"first_author":"Gupta","given":"S. K."},None),
 ("10.12693/aphyspola.115.771",None,None),
 ("10.12693/aphyspola.116.99",None,None),
 ("10.2174/1874186x00902010015",None,None),
 ("10.15407/spqeo13.03.309",{"first_author":"Strelchuk","given":"V. V."},None),
 ("10.1021/acs.jpcc.6b05282",None,None),
 ("10.3390/bios11040102",None,None),
 ("10.3390/s23052596",None,None),
 ("10.3390/nano15070498",None,None),
 ("10.3390/molecules25081854",None,None),
 ("10.1021/acsomega.3c08122",None,None),
 ("10.1038/s41598-020-64392-8",None,None),
 ("10.3390/ma13225280",None,None),
 ("10.1039/d4ra00852a",None,None),
 ("10.1038/s41598-020-67367-x",None,None),
 ("10.1038/srep32171",None,None),
 ("10.3390/nano10030430",None,None),
 ("10.3390/nano14131130",None,None),
 ("10.1039/d0ra10648h",None,None),
 ("10.1039/c8ra00626a",None,None),
 ("10.3906/kim-2106-55",{"first_author":"Hamdi","given":"D.","year":2022},None),
 ("10.1021/acsomega.5c08955",None,None),
 ("10.1038/s41598-022-19824-y",None,None),
 ("10.3390/nano9040535",None,None),
 ("10.3390/ma16155494",None,None),
 ("10.1098/rsos.171811",None,None),
 ("10.3390/nano12091501",None,dict(doi="10.3390/nano12091501",pmc="PMC9104741",found="EuropePMC",oa="Y")),
 ("10.1039/d2na00390b",None,dict(doi="10.1039/d2na00390b",pmc="PMC9846715",found="EuropePMC",oa="Y")),
 ("10.1039/d6ra03562k",None,dict(doi="10.1039/d6ra03562k",pmc="PMC13456038",found="EuropePMC",oa="Y")),
 ("10.1038/s41598-022-09684-x",None,dict(doi="10.1038/s41598-022-09684-x",pmc="PMC8979959",found="EuropePMC",oa="Y",extra=True)),
 ("10.3390/nano11092311",None,None),
]
DROP=["10.1039/d0ra02929g","10.3390/polym8030068","10.1038/s41598-022-26343-3","10.3390/nano13182584","10.1063/1.1619212","10.3390/ma16020639"]
if __name__=="__main__":
    # 1. move existing to temp names
    tmp={}
    for doi,_,_ in FINAL:
        if doi in state:
            old=os.path.join(OUT,state[doi]["folder"]); t=old+"__tmp"
            if os.path.isdir(old): os.rename(old,t); tmp[doi]=t
    for doi in DROP:
        if doi in state:
            old=os.path.join(OUT,state[doi]["folder"])
            if os.path.isdir(old): shutil.rmtree(old); print("dropped",state[doi]["folder"])
    for n,(doi,ov,newspec) in enumerate(FINAL,1):
        if doi in tmp:
            rec=state[doi]; meta=dict(rec["meta"]); meta.update(ov or {})
            fa=build.ascii_(meta.get("first_author") or "Unknown"); yr=meta.get("year")
            folder=f"ANA{n:02d}_{fa}{yr}"
            os.rename(tmp[doi],os.path.join(OUT,folder))
            rec["folder"]=folder; rec["meta"]=meta
            print(n,folder)
        else:
            spec=newspec
            # build.process names folder with its index i -> n
            rec=build.process(n,spec,ov)
            print(n,rec["folder"],"(new)")
        build.state[doi]=state[doi]
    json.dump(state,open(build.STATE,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
