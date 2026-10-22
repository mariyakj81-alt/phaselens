import sys, json, re
sys.path.insert(0, '.')
from common import get
from known import known
K = known()
g = json.load(open("refgraph.json"))
core = {"CAL010", "CAL019", "CAL020", "CAL021", "CAL024", "CAL027", "CAL032", "CAL009", "CAL014", "CAL007", "CAL030", "CAL033", "CAL028", "CAL004", "CAL025"}
cand = [(v[0], k, v[1]) for k, v in g.items() if k not in K and (v[0] >= 2 or any(w in core for w in v[1]))]
cand.sort(reverse=True)
print(len(cand))
out = []
for c, d, who in cand:
    r = get("https://api.crossref.org/works/" + d, min_gap=0.6)
    if r.status_code != 200: continue
    m = r.json()["message"]
    t = (m.get("title") or [""])[0]
    if not re.search(r"raman|vibrat|spectr|carbonate|calcite|calcium|aragonite|shell|coral|biomin|mortar|lime|cement|crystal", t, re.I): continue
    y = (m.get("issued", {}).get("date-parts") or [[None]])[0][0]
    out.append((c, d, y, (m.get("author") or [{}])[0].get("family", ""), t[:95], (m.get("container-title") or [""])[0][:25], ",".join(who)))
for o in out: print(*o, sep=" | ")
