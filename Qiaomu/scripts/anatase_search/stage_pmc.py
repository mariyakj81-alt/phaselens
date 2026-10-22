import json, sys, os
sys.path.insert(0,os.path.dirname(__file__))
import dl, screen
STAGE=os.environ["STAGE"]; os.makedirs(STAGE,exist_ok=True)
for pmc in sys.argv[1:]:
    out=os.path.join(STAGE,pmc+".pdf")
    ok=False
    for v in (1,2):
        ok,msg=dl.fetch(f"https://pmc-oa-opendata.s3.amazonaws.com/{pmc}.{v}/{pmc}.{v}.pdf",out,gap=1)
        if ok: break
    if not ok: print(pmc,"FAIL",msg[:100]); continue
    pages=screen.pdf_text(out); full="\n".join(pages); nr,na,f=screen.score(full)
    print(pmc,f"pages={len(pages)} Raman={nr} anat={na}",f,"|",pages[0][:100].replace("\n"," "),flush=True)
