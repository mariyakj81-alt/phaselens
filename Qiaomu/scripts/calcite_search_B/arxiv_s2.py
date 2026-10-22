import sys, re, json
sys.path.insert(0, '.')
from common import get
seen = {}
qs = ['abs:calcite', 'abs:CaCO3', 'abs:"calcium carbonate"', 'abs:aragonite', 'abs:vaterite', 'ti:carbonate AND abs:spectroscopy', 'abs:limestone AND abs:spectroscopy', 'abs:biomineral', 'abs:"Mg-calcite" OR abs:"magnesian calcite"', 'abs:speleothem', 'abs:coccolith', 'abs:"carbonate precipitation"', 'abs:MICP']
for q in qs:
    for start in (0, 100, 200):
        r = get("http://export.arxiv.org/api/query", params={"search_query": q, "max_results": 100, "start": start, "sortBy": "relevance"}, min_gap=4)
        ents = re.findall(r"<entry>(.*?)</entry>", r.text, re.S)
        if not ents: break
        for e in ents:
            i = re.search(r"<id>(.*?)</id>", e).group(1); t = re.sub(r"\s+", " ", re.search(r"<title>(.*?)</title>", e, re.S).group(1))
            ab = re.sub(r"\s+", " ", re.search(r"<summary>(.*?)</summary>", e, re.S).group(1)).lower()
            y = re.search(r"<published>(\d{4})", e).group(1)
            cat = re.search(r'<arxiv:primary_category[^>]*term="([^"]+)"', e).group(1)
            seen[i] = (y, cat, t[:110], "raman" in ab)
    print(q, len(seen), flush=True)
json.dump(seen, open("arxiv_pool.json", "w"))
