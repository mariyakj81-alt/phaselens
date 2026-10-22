import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_A import *
qs = ['"calcite" AND "Raman" AND OPEN_ACCESS:y',
 '"calcite" AND "Raman" AND "cm-1" AND OPEN_ACCESS:y',
 '(TITLE:"calcite" OR ABSTRACT:"calcite") AND "Raman" AND OPEN_ACCESS:y',
 '(TITLE_ABS:"calcite") AND (TITLE_ABS:"Raman") AND OPEN_ACCESS:y',
 '"calcite" AND "Raman" AND "1086" AND OPEN_ACCESS:y',
 '"calcite" AND "Raman" AND "1085" AND OPEN_ACCESS:y',
 ]
for q in qs:
    r = get(EPMC, params={"query":q,"format":"json","resultType":"lite","pageSize":1}, min_gap=0.5)
    print(r.json().get("hitCount"), q)
