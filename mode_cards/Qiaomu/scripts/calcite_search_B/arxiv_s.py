import sys, re
sys.path.insert(0, '.')
from common import get
seen = {}
for q in ['abs:calcite AND abs:Raman', 'abs:"calcium carbonate" AND abs:Raman', 'abs:aragonite AND abs:Raman', 'abs:carbonate AND abs:Raman AND abs:mineral', 'ti:calcite', 'abs:calcite AND abs:phonon', 'abs:CaCO3 AND abs:Raman', 'abs:dolomite AND abs:Raman', 'abs:limestone AND abs:Raman', 'abs:Mg-calcite', 'abs:vaterite AND abs:Raman', 'abs:"carbonate minerals" AND abs:spectroscopy']:
    r = get("http://export.arxiv.org/api/query", params={"search_query": q, "max_results": 50, "sortBy": "relevance"}, min_gap=4)
    for e in re.findall(r"<entry>(.*?)</entry>", r.text, re.S):
        i = re.search(r"<id>(.*?)</id>", e).group(1); t = re.sub(r"\s+", " ", re.search(r"<title>(.*?)</title>", e, re.S).group(1))
        ab = re.sub(r"\s+", " ", re.search(r"<summary>(.*?)</summary>", e, re.S).group(1)).lower()
        y = re.search(r"<published>(\d{4})", e).group(1)
        if "raman" in ab and re.search(r"calcite|caco|carbonate|aragonite|dolomite", ab + t.lower()) and i not in seen:
            seen[i] = (y, t[:100], ab.count("calcite"))
for k, v in sorted(seen.items(), key=lambda kv: -kv[1][2]): print(k, *v, sep=" | ")
