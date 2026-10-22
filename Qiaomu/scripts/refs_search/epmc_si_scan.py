import sys,re,os,json
sys.path.insert(0,os.path.dirname(__file__))
from common import *
S="C:/Users/yqm12/AppData/Local/Temp/claude/G--My-Drive-Qiaomu-Coding-LLM-Hackason/6904f568-fbff-48aa-b9f2-a1642df7e094/scratchpad/refs_search_x/epmc_si/"
os.makedirs(S,exist_ok=True)
qs=['"silicon" AND "Raman" AND ("2TA" OR "2TO") AND ("520" OR "521") AND OPEN_ACCESS:y',
    '"Si wafer" AND "Raman" AND ("2TA" OR "2TO" OR "second-order") AND OPEN_ACCESS:y',
    '"crystalline silicon" AND "Raman" AND "2TO" AND OPEN_ACCESS:y',
    '"c-Si" AND "Raman" AND ("2TA" OR "2TO") AND OPEN_ACCESS:y',
    '"silicon" AND "Raman" AND "second-order" AND "phonon" AND ("TA" AND "TO") AND OPEN_ACCESS:y AND (TITLE:"silicon" OR TITLE:"Si")']
ids={}
for q in qs:
    cur="*"
    for page in range(2):
        r=get("https://www.ebi.ac.uk/europepmc/webservices/rest/search",params={"query":q,"format":"json","pageSize":100,"resultType":"lite","cursorMark":cur},min_gap=1)
        j=r.json()
        for x in j['resultList']['result']:
            if x.get('pmcid'): ids[x['pmcid']]=(x.get('title','')[:90],x.get('pubYear'),x.get('doi'))
        nc=j.get('nextCursorMark')
        if not nc or nc==cur or len(j['resultList']['result'])<100: break
        cur=nc
print(len(ids))
rows=[]
for pid,(title,yr,doi) in ids.items():
    fn=S+pid+".xml"
    if not os.path.exists(fn):
        r=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pid}/fullTextXML",min_gap=1,timeout=(20,60))
        if r.status_code!=200: continue
        open(fn,"wb").write(r.content)
    t=re.sub(r'<[^>]+>',' ',open(fn,encoding="utf-8",errors="ignore").read())
    ram=t.count("Raman")
    n2to=len(re.findall(r'2\s*TO\b',t)); n2ta=len(re.findall(r'2\s*TA\b',t))
    f1=len(re.findall(r'\b52[01](\.\d+)?\b|\b520(\.\d+)?\b',t)); f2=len(re.findall(r'\b(29\d|30\d)(\.\d+)?\b',t)); f3=len(re.findall(r'\b(9[3-9]\d)(\.\d+)?\b',t))
    fw=len(re.findall(r'FWHM|full width',t))
    rows.append((pid,yr,title,ram,n2to,n2ta,f1,f2,f3,fw))
rows.sort(key=lambda x:-(min(x[4],3)+min(x[5],3)+min(x[6],3)+min(x[7],3)+min(x[8],3)+min(x[3],10)/5))
for x in rows[:30]: print(x)
