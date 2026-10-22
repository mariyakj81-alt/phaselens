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
flag=sys.argv[1]; minR=int(sys.argv[2]); minA=int(sys.argv[3])
rows=[]
for k,v in s.items():
    if 'raman' not in v or (v.get('doi') or '').lower() in seen: continue
    if flag in v['flags'] and v['raman']>=minR and v['anatase']>=minA:
        rows.append((v['raman'],k))
rows.sort(reverse=True)
print(flag,len(rows))
for r,k in rows[:int(sys.argv[4]) if len(sys.argv)>4 else 40]:
    v=s[k]; print(f"{k} {p[k]['year']} R{v['raman']} A{v['anatase']} mm{len(v['modes_meas'])} ma{len(v['modes_all'])} fw{v['fwhm']} tb{v['rtab']} {v['lasers']} S={p[k]['hasSuppl']} | {re.sub(r'<[^>]+>','',p[k]['title'])[:80]}")
