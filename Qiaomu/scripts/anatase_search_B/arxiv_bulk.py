"""Collect arXiv ids for anatase/TiO2 papers (many queries, paged), save to arxiv_pool.json"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get, HERE
import xml.etree.ElementTree as ET
ns = {"a": "http://www.w3.org/2005/Atom", "ar": "http://arxiv.org/schemas/atom"}
POOL = os.path.join(HERE, "arxiv_pool.json")
pool = json.load(open(POOL)) if os.path.exists(POOL) else {}
queries = ["abs:anatase", "abs:TiO2 AND abs:Raman", "abs:titania AND abs:Raman", "abs:\"titanium dioxide\" AND abs:Raman", "abs:TiO2 AND abs:nanoparticles", "abs:TiO2 AND abs:\"thin films\"", "abs:TiO2 AND abs:nanotubes", "abs:TiO2 AND abs:photocatalytic", "abs:TiO2 AND abs:doped", "abs:TiO2 AND abs:phonon", "abs:rutile AND abs:anatase", "abs:TiO2 AND abs:\"magnetron sputtering\"", "abs:TiO2 AND abs:\"atomic layer deposition\"", "abs:TiO2 AND abs:\"sol-gel\"", "abs:TiO2 AND abs:hydrothermal", "abs:TiO2 AND abs:\"oxygen vacancies\""]
for q in queries:
    for start in range(0, 400, 100):
        r = get("http://export.arxiv.org/api/query", params={"search_query": q, "start": start, "max_results": 100, "sortBy": "relevance"}, gap=3)
        if r.status_code != 200:
            print("ERR", q, start, r.status_code); break
        root = ET.fromstring(r.content)
        ents = root.findall("a:entry", ns)
        for e in ents:
            aid = e.find("a:id", ns).text.split("/abs/")[-1]
            aid = re.sub(r"v\d+$", "", aid)
            if aid in pool: continue
            title = re.sub(r"\s+", " ", e.find("a:title", ns).text.strip())
            summ = re.sub(r"\s+", " ", e.find("a:summary", ns).text.strip())
            doi = e.find("ar:doi", ns); jr = e.find("ar:journal_ref", ns)
            pool[aid] = dict(title=title, year=e.find("a:published", ns).text[:4], doi=doi.text if doi is not None else "", jr=jr.text if jr is not None else "", raman="raman" in (title + summ).lower(), anat=bool(re.search(r"anatase|tio2|tio\$_2\$|titania|titanium dioxide", (title + summ).lower())))
        print(q, start, len(ents), len(pool), flush=True)
        if len(ents) < 100: break
json.dump(pool, open(POOL, "w"), indent=0)
print("TOTAL", len(pool), "anat", sum(v["anat"] for v in pool.values()), "raman+anat", sum(v["anat"] and v["raman"] for v in pool.values()))
