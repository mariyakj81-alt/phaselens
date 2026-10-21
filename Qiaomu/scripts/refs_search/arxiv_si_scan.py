import sys,re,os,json
sys.path.insert(0,os.path.dirname(__file__))
from common import *
import fitz
S="C:/Users/yqm12/AppData/Local/Temp/claude/G--My-Drive-Qiaomu-Coding-LLM-Hackason/6904f568-fbff-48aa-b9f2-a1642df7e094/scratchpad/refs_search_x/si_scan/"
os.makedirs(S,exist_ok=True)
qs=['all:silicon AND all:"second-order Raman"','all:silicon AND all:"two-phonon Raman"','all:silicon AND all:Raman AND all:"520" AND all:"2TO"',
    'all:silicon AND all:Raman AND all:"2TA"','ti:silicon AND ti:Raman AND abs:wafer', 'all:"Raman" AND all:"crystalline silicon" AND all:"linewidth" AND all:"520.5"']
seen={}
for q in qs:
    r=get("http://export.arxiv.org/api/query", params={"search_query":q,"max_results":25,"sortBy":"relevance"}, min_gap=3)
    for e in re.findall(r'<entry>(.*?)</entry>', r.text, re.S):
        aid=re.search(r'<id>http://arxiv.org/abs/(.*?)</id>',e).group(1)
        title=re.sub(r'\s+',' ',re.search(r'<title>(.*?)</title>',e,re.S).group(1))
        seen[aid]=title
print(len(seen))
res=[]
for aid,title in seen.items():
    fn=S+aid.replace('/','_').split('v')[0]+".pdf"
    if not os.path.exists(fn):
        try:
            r=get("https://arxiv.org/pdf/"+aid,min_gap=3,timeout=(20,90))
        except Exception as ex:
            print("ERR",aid,ex); continue
        if r.content[:5]!=b'%PDF-': continue
        open(fn,"wb").write(r.content)
    try:
        d=fitz.open(fn); t="".join(p.get_text() for p in d)
    except Exception as ex:
        continue
    ram=t.count("Raman"); n2to=len(re.findall(r'2\s*TO',t)); n2ta=len(re.findall(r'2\s*TA',t))
    f1=len(re.findall(r'\b52[01](\.\d+)?\b|\b520(\.\d+)?\b',t)); f2=len(re.findall(r'\b(29\d|30\d)(\.\d+)?\b',t)); f3=len(re.findall(r'\b(9[3-9]\d)(\.\d+)?\b',t))
    res.append((aid,title[:90],ram,n2to,n2ta,f1,f2,f3))
res.sort(key=lambda x:-(x[3]>0)-(x[4]>0)-(x[5]>0)-(x[2]>10))
for x in res[:30]: print(x)
