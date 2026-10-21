import sys,re,os,glob
import fitz
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cfg_A import STAGE
pm=sys.argv[1]; pat=sys.argv[2]; W=int(sys.argv[3]) if len(sys.argv)>3 else 200
files=[os.path.join(STAGE,pm,"paper.pdf")]+sorted(glob.glob(os.path.join(STAGE,pm,"SI","*.pdf")))
for f in files:
    d=fitz.open(f)
    for i,p in enumerate(d):
        t=re.sub(r"\s+"," ",p.get_text())
        for m in re.finditer(pat,t,re.I):
            print(os.path.basename(f),"p%d"%(i+1),"...",t[max(0,m.start()-W):m.end()+W])
