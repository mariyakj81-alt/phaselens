"""Print compact anatase-Raman evidence from a PDF: laser lines, mode-number sentences, table hints. Usage: python -P evidence.py file.pdf [maxsnips]"""
import sys, re, fitz
def main(path,maxs=4):
    d=fitz.open(path); txt="\n".join(p.get_text() for p in d).replace("\u2212","-")
    flat=re.sub(r"\s+"," ",txt)
    lasers=sorted(set(re.findall(r"(\d{3}(?:\.\d+)?)\s*nm(?=[^.]{0,80}(?:laser|excitation|Raman|line))",flat)) | set(re.findall(r"(?:laser|excitation|Raman)[^.]{0,80}?(\d{3}(?:\.\d+)?)\s*nm",flat)))
    lasers=[l for l in lasers if 300<=float(l)<=1100]
    sn=[]
    for m in re.finditer(r"(?<![\d.])(14[0-9]|19[5-9]|20[0-3]|39[5-9]|40[0-2]|51[0-9]|52[0-2]|63[5-9]|64[0-5])(?:\.\d+)?(?![\d])",flat):
        ctx=flat[max(0,m.start()-110):m.end()+110]
        if re.search(r"cm|Eg|E g|B1g|A1g|B 1g|A 1g",ctx) and re.search(r"Raman|mode|peak|band",ctx):
            sn.append(ctx)
    # dedupe by overlap
    out=[];last=-999
    for s in sn:
        if not out or s[:40] not in out[-1]:
            out.append(s)
    print("LASER nm:",lasers[:8])
    print("tables:",len(re.findall(r"\bTable\s?\d",flat)),"| 'Raman' count",len(re.findall("Raman",flat)))
    for s in out[:maxs]: print("  >>",s)
if __name__=="__main__":
    main(sys.argv[1],int(sys.argv[2]) if len(sys.argv)>2 else 4)
