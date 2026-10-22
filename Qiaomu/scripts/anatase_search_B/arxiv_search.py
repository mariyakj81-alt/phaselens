import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get
import xml.etree.ElementTree as ET
ns = {"a": "http://www.w3.org/2005/Atom", "ar": "http://arxiv.org/schemas/atom"}
queries = sys.argv[1:]
seen = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "arxiv_hits.json"))) if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "arxiv_hits.json")) else {}
old=set(seen)
for q in queries:
    r = get("http://export.arxiv.org/api/query", params={"search_query": q, "max_results": 100, "sortBy": "relevance"}, gap=3)
    if r.status_code != 200:
        print("ERR", q, r.status_code); continue
    root = ET.fromstring(r.content)
    for e in root.findall("a:entry", ns):
        aid = e.find("a:id", ns).text.split("/abs/")[-1]
        if aid in seen: continue
        title = re.sub(r"\s+", " ", e.find("a:title", ns).text.strip())
        summ = re.sub(r"\s+", " ", e.find("a:summary", ns).text.strip())
        doi = e.find("ar:doi", ns)
        jr = e.find("ar:journal_ref", ns)
        pub = e.find("a:published", ns).text[:4]
        txt = (title + " " + summ).lower()
        seen[aid] = dict(title=title, year=pub, doi=doi.text if doi is not None else "", jr=jr.text if jr is not None else "", summ=summ, raman="raman" in txt, anatase=("anatase" in txt or "tio2" in txt or "tio$_2$" in txt or "titania" in txt or "titanium dioxide" in txt))
for k, v in seen.items():
    if k in old: continue
    if v["anatase"] and v["raman"]:
        print(k, v["year"], "|", v["title"][:120], "|", v["doi"], "|", v["jr"][:60])
print("---- anatase only / raman only counts", sum(v["anatase"] for v in seen.values()), sum(v["raman"] for v in seen.values()))
for k, v in []:
    if v["anatase"] and not v["raman"]:
        print("  (anatase only)", k, v["year"], v["title"][:100])
json.dump(seen, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "arxiv_hits.json"), "w"), indent=1)
