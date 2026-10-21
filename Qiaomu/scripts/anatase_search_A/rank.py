import json, re, sys, csv, os
D='scripts/anatase_search_A/'
p=json.load(open(D+'pool_all.json'));s=json.load(open(D+'scores_all.json'))
seen=set()
for row in csv.DictReader(open('anatase/papers.csv',encoding='utf-8')): seen.add(row['doi'].lower().strip())
for row in csv.DictReader(open('anatase/candidates_rejected.csv',encoding='utf-8')):
    for d in row['doi'].split(';'): seen.add(d.lower().strip())
if os.path.exists(D+'decided.txt'):
    for l in open(D+'decided.txt'):
        l=l.strip().split()[0] if l.strip() else ''
        if l: seen.add(l.lower())
def q(v):
    if 'raman' not in v: return -1
    mm=len(v['modes_meas']); ma=len(v['modes_all'])
    return min(mm,5)*3+min(ma,5)+(2 if v['sym']>=3 else 0)+(2 if v['rtab'] else 0)+(1 if v['fwhm'] else 0)+min(v['raman'],40)/10+min(v['anatase'],40)/20
rows=[(k,q(v)) for k,v in s.items() if (v.get('doi') or '').lower() not in seen]
rows.sort(key=lambda x:-x[1])
lo=int(sys.argv[1]) if len(sys.argv)>1 else 0; hi=int(sys.argv[2]) if len(sys.argv)>2 else 60
print(len(rows),'candidates after exclusion')
for k,sc in rows[lo:hi]:
    v=s[k]
    print(k,p[k]['year'],'q%.0f'%sc,'R',v['raman'],'A',v['anatase'],'mm',len(v['modes_meas']),'ma',len(v['modes_all']),'sym',v['sym'],'fw',v['fwhm'],'tab',v['rtab'],v['lasers'],p[k]['hasSuppl'],'|',re.sub(r'<[^>]+>','',p[k]['title'])[:70])
