import sys,re,fitz,glob,os
RANGES=[(138,160),(190,210),(388,412),(505,530),(625,655)]
def inr(v): return any(lo<=v<=hi for lo,hi in RANGES)
def wins(path,n=3,w=230):
    t=" ".join(p.get_text() for p in fitz.open(path)).replace("−","-"); t=re.sub(r"\s+"," ",t)
    # cut references
    i=t.rfind("References"); 
    if i>len(t)*0.5: t=t[:i]
    out=[];last=-1000
    for m in re.finditer(r"(?<![\d.])(\d{3})(?:\.\d+)?(?![\d])",t):
        v=int(m.group(1))
        if inr(v) and m.start()-last>w:
            ctx=t[max(0,m.start()-w//2):m.start()+w//2]
            vals=[int(x) for x in re.findall(r"(?<![\d.])(\d{3})(?:\.\d+)?(?![\d])",ctx) if inr(int(x))]
            if len(set(vals))>=2 and re.search(r"cm|Raman",ctx) and not re.search(r"\[\d+\]\s*$|et al",ctx[-30:]):
                out.append(ctx); last=m.start()
        if len(out)>=n: break
    return out
if __name__=="__main__":
    for d in sys.argv[1:]:
        print("==",d)
        for c in wins(os.path.join(d,"paper.pdf")): print("   >",c)
