import json, re, sys, csv, os
D='scripts/anatase_search_A/'
p=json.load(open(D+'pool_all.json'));s=json.load(open(D+'scores_all.json'))
seen=set()
for row in csv.DictReader(open('anatase/papers.csv',encoding='utf-8')): seen.add(row['doi'].lower().strip())
for row in csv.DictReader(open('anatase/candidates_rejected.csv',encoding='utf-8')):
    for d in row['doi'].split(';'): seen.add(d.lower().strip())
if os.path.exists(D+'decided.txt'):
    for l in open(D+'decided.txt'):
        t=l.strip().split()
        if t: seen.add(t[0].lower())
def sub(v):
    if 'raman' not in v: return -1
    mm=len(v['modes_meas'])
    if mm<2 or v['anatase']<6: return -1
    return min(v['raman'],50)*0.2+min(v['nshift'],8)+(2 if v['fwhm'] else 0)+(3 if v['rtab'] else 0)+min(v['sym'],10)*0.4+min(v['nfigR'],4)*0.8+min(v['best_cnt'],5)*1.5+min(mm,5)
rows=[(k,sub(v)) for k,v in s.items() if (v.get('doi') or '').lower() not in seen]
rows=[r for r in rows if r[1]>0]
rows.sort(key=lambda x:-x[1])
lo=int(sys.argv[1]); hi=int(sys.argv[2])
print(len(rows),'ranked candidates')
for k,sc in rows[lo:hi]:
    v=s[k]
    print(f"{k} {p[k]['year']} s{sc:.0f} R{v['raman']} A{v['anatase']} mm{len(v['modes_meas'])} sh{v['nshift']} fw{v['fwhm']} tb{v['rtab']} {v['lasers']} S={p[k]['hasSuppl']} | {re.sub(r'<[^>]+>','',p[k]['title'])[:75]}")
    if len(sys.argv)>3: print('     ',v['best_sent'][:260])
