"""Verify every anatase/ANAnn_*/paper.pdf: %PDF magic, opens in PyMuPDF, title words on page 1, Raman evidence windows, laser lines. Writes verify_report.json. Run with python -P."""
import os, sys, re, json, fitz, glob
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(os.path.join(HERE,"..",".."))
OUT=os.path.join(ROOT,"anatase")
state=json.load(open(os.path.join(HERE,"build_state.json"),encoding="utf-8"))
byfolder={v["folder"]:(k,v) for k,v in state.items()}
RANGES={"Eg1":(138,160),"Eg2":(190,210),"B1g1":(388,412),"A1g/B1g2":(505,530),"Eg3":(625,655)}
def norm(s): return re.sub(r"[^a-z0-9 ]"," ",s.lower().replace("−","-"))
def analyse(path,title):
    raw=open(path,"rb").read(8)
    ok_magic=raw[:4]==b"%PDF"
    d=fitz.open(path); pages=[p.get_text() for p in d]
    first=norm(pages[0]); tw=[w for w in norm(title).split() if len(w)>3]
    hit=sum(1 for w in tw if w in first)
    full=" ".join(pages); flat=re.sub(r"\s+"," ",full.replace("−","-"))
    nraman=len(re.findall("Raman",flat)); nanat=len(re.findall("anatase",flat,re.I))
    # evidence windows
    nums=[]
    for m in re.finditer(r"(?<![\d.])(\d{3})(?:\.\d+)?(?![\d])",flat):
        v=int(m.group(1))
        for k,(lo,hi) in RANGES.items():
            if lo<=v<=hi: nums.append((m.start(),k,m.group(0)))
    best=(0,None)
    for i,(pos,k,_) in enumerate(nums):
        win=[(p,kk) for p,kk,_ in nums if pos<=p<=pos+260]
        ks=set(kk for _,kk in win)
        if len(ks)>best[0]:
            end=max(p for p,_ in win)
            ctx=flat[max(0,pos-60):end+40]
            if re.search(r"cm|Raman|shift",flat[max(0,pos-300):end+100]): best=(len(ks),ctx)
    # page of best
    bp=None
    if best[1]:
        probe=re.sub(r"\s+"," ",best[1])[20:60]
        for i,p in enumerate(pages):
            if probe and probe in re.sub(r"\s+"," ",p.replace("−","-")): bp=i+1; break
    lasers=sorted(set(re.findall(r"(\d{3}(?:\.\d+)?)\s*nm(?=[^.]{0,100}(?:laser|excitation|Raman|line|He-Ne|Ar))",flat))|set(re.findall(r"(?:laser|excitation|Raman|He-Ne|Ar\+?|argon)[^.]{0,100}?(\d{3}(?:\.\d+)?)\s*nm",flat)),key=float)
    lasers=[l for l in lasers if 320<=float(l)<=1100]
    sym=len(re.findall(r"\bE\s?g\b|\bB\s?1g\b|\bA\s?1g\b",flat))
    return {"magic":ok_magic,"pages":len(pages),"title_hit":f"{hit}/{len(tw)}","raman":nraman,"anatase":nanat,"sym":sym,"modes_in_best_window":best[0],"best_window":best[1],"best_page":bp,"lasers":lasers}
rep={}
for folder in sorted(os.listdir(OUT)):
    p=os.path.join(OUT,folder,"paper.pdf")
    if not os.path.exists(p): continue
    doi,v=byfolder.get(folder,(None,{}))
    title=(v.get("meta") or {}).get("title","")
    try: r=analyse(p,title)
    except Exception as e: r={"error":str(e)}
    r["doi"]=doi; r["title"]=title
    rep[folder]=r
json.dump(rep,open(os.path.join(HERE,"verify_report.json"),"w",encoding="utf-8"),indent=1,ensure_ascii=False)
for f,r in rep.items():
    print(f,"|",r.get("magic"),r.get("pages"),"title",r.get("title_hit"),"Raman",r.get("raman"),"anat",r.get("anatase"),"sym",r.get("sym"),"win",r.get("modes_in_best_window"),"p",r.get("best_page"),"lasers",r.get("lasers"))
