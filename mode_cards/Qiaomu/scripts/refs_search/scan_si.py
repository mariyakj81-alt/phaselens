import sys,re,os
sys.path.insert(0,os.path.dirname(__file__))
from common import *
import fitz
S="C:/Users/yqm12/AppData/Local/Temp/claude/G--My-Drive-Qiaomu-Coding-LLM-Hackason/6904f568-fbff-48aa-b9f2-a1642df7e094/scratchpad/refs_search_x/"
def scan(u,n,gap):
    r=get(u,min_gap=gap,timeout=(20,120))
    print(u,r.status_code,r.headers.get('content-type'),len(r.content))
    if r.content[:5]!=b'%PDF-': return
    open(S+n,"wb").write(r.content)
    d=fitz.open(S+n); t="".join(p.get_text() for p in d)
    open(S+n+".txt","w",encoding="utf-8").write(t)
    print("  pages",len(d),"|",t[:200].replace("\n"," "))
    for lab,pat in [("1st",r'\b5[12]\d(\.\d+)?\b'),("2TA",r'\b(29\d|30\d)(\.\d+)?\b'),("2TO",r'\b(9[3-9]\d|10[0-2]\d)(\.\d+)?\b')]:
        print("  ",lab,len(re.findall(pat,t)),"Raman",t.count("Raman"),"2TO",len(re.findall(r'2\s*TO',t)),"2TA",len(re.findall(r'2\s*TA',t)))
if __name__=="__main__":
    for u,n,g in [("https://arxiv.org/pdf/cond-mat/0406096","si1.pdf",3),("https://arxiv.org/pdf/1002.2692","si2.pdf",3),("https://arxiv.org/pdf/1103.4833","si3.pdf",3),("https://www.tara.tcd.ie/bitstreams/9d2d37ef-a12d-49c0-bac4-57e778179cdd/download","si4.pdf",10)]:
        scan(u,n,g)
