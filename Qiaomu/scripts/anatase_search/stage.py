"""Stage candidate PDFs into scratchpad staging dir and screen them. Usage: python -P stage.py cands.json  (list of {doi,urls[]})"""
import json, sys, os, re
sys.path.insert(0,os.path.dirname(__file__))
import dl, screen
STAGE=os.environ["STAGE"]
cands=json.load(open(sys.argv[1]))
os.makedirs(STAGE,exist_ok=True)
res={}
rp=os.path.join(STAGE,"stage_results.json")
if os.path.exists(rp): res=json.load(open(rp))
for c in cands:
    doi=c["doi"]; safe=re.sub(r"[^A-Za-z0-9._-]","_",doi); out=os.path.join(STAGE,safe+".pdf")
    if doi in res and res[doi].get("ok"): continue
    ok=False; msgs=[]
    for u in c["urls"]:
        ok,msg=dl.fetch(u,out)
        msgs.append(u[:70]+" -> "+msg[:110])
        if ok:
            try:
                pages=screen.pdf_text(out); full="\n".join(pages)
                nr,na,f=screen.score(full)
                res[doi]={"ok":True,"url":u,"pages":len(pages),"raman":nr,"anatase":na,"modes":f,"first":pages[0][:200].replace("\n"," ")}
            except Exception as e:
                ok=False; msgs.append("fitz fail "+str(e)); os.remove(out); continue
            break
    if not ok: res[doi]={"ok":False,"msgs":msgs}
    print(doi, json.dumps(res[doi],ensure_ascii=False)[:420],flush=True)
    json.dump(res,open(rp,"w"))
