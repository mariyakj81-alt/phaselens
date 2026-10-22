"""Score a PDF/text for anatase Raman evidence. Usage: python -P screen.py file.pdf [title words...]"""
import sys, re, fitz
MODES={"Eg1":(139,150),"Eg2":(193,203),"B1g1":(393,405),"A1g/B1g2":(507,525),"Eg3":(632,645)}
def pdf_text(path):
    d=fitz.open(path); pages=[p.get_text() for p in d]; return pages
def score(text):
    t=text.replace("\u2212","-")
    nraman=len(re.findall(r"Raman",t))
    nanat=len(re.findall(r"anatase",t,re.I))
    found={}
    for name,(lo,hi) in MODES.items():
        c=0
        for m in re.finditer(r"(?<![\d.])(\d{3})(?:\.\d+)?(?![\d])",t):
            v=int(m.group(1))
            if lo<=v<=hi:
                ctx=t[max(0,m.start()-80):m.end()+80]
                if re.search(r"cm|Raman|mode|E\s?g|B\s?1g|A\s?1g|shift",ctx): c+=1
        found[name]=c
    return nraman,nanat,found
def snippets(text,n=6):
    out=[]
    for m in re.finditer(r"(14[0-9](?:\.\d)?\s*(?:cm|and|,))",text):
        out.append(text[max(0,m.start()-100):m.end()+120].replace("\n"," "))
        if len(out)>=n: break
    return out
if __name__=="__main__":
    path=sys.argv[1]
    pages=pdf_text(path)
    full="\n".join(pages)
    nr,na,f=score(full)
    first=pages[0][:300].replace("\n"," ")
    print(f"pages={len(pages)} Raman={nr} anatase={na} modes={f}")
    print("FIRST:",first)
    if len(sys.argv)>2:
        words=[w.lower() for w in sys.argv[2:]]
        hit=sum(w in pages[0].lower() for w in words)
        print(f"title words on p1: {hit}/{len(words)}")
