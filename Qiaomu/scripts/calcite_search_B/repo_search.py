import sys, json, re, requests
sys.path.insert(0, '.')
from common import get, UA
seen = {}
def add(src, id_, title, year, desc, files=None):
    key = (src, id_)
    if key in seen: return
    seen[key] = (year, title[:120], re.sub(r"<[^>]+>", " ", desc or "")[:200].replace("\n", " "))
# Zenodo
for q in ['calcite Raman', 'Raman spectra calcite', 'Raman carbonate', 'CaCO3 Raman spectra', 'Mg-calcite Raman', 'calcite "Raman" spectra dataset']:
    for page in (1, 2):
        r = get("https://zenodo.org/api/records", params={"q": q, "size": 25, "page": page, "type": "dataset", "sort": "bestmatch"}, min_gap=3)
        if r.status_code != 200: print("zenodo", r.status_code, q); break
        for h in r.json()["hits"]["hits"]:
            m = h["metadata"]
            t = m.get("title", ""); dsc = m.get("description", "")
            if re.search(r"raman", t + dsc, re.I) and re.search(r"calcite|calcium carbonate|CaCO|carbonate", t + dsc, re.I):
                add("zenodo", h.get("doi"), t, m.get("publication_date", "")[:4], dsc)
print("zenodo", len(seen), flush=True)
# Dryad
for q in ['calcite Raman', 'Raman carbonate', 'Raman spectra calcite aragonite', 'Mg-calcite']:
    r = get("https://datadryad.org/api/v2/search", params={"q": q, "per_page": 50}, min_gap=3)
    if r.status_code != 200: print("dryad", r.status_code); continue
    for h in r.json().get("_embedded", {}).get("stash:datasets", []):
        t = h.get("title", ""); ab = h.get("abstract", "")
        if re.search(r"raman", t + ab, re.I) and re.search(r"calcite|calcium carbonate|CaCO|carbonate", t + ab, re.I):
            add("dryad", h.get("identifier"), t, (h.get("publicationDate") or "")[:4], ab)
print("dryad", len(seen), flush=True)
# Figshare
for q in ['calcite Raman', 'Raman spectra calcite', 'Raman carbonate', 'calcium carbonate Raman']:
    for page in (1, 2):
        try:
            r = requests.post("https://api.figshare.com/v2/articles/search", json={"search_for": q, "page_size": 100, "page": page, "item_type": 3}, headers={"User-Agent": UA}, timeout=60)
        except Exception as e:
            print("figshare exc", e); break
        if r.status_code != 200: print("figshare", r.status_code); break
        for h in r.json():
            t = h.get("title", "")
            if re.search(r"raman", t, re.I) or True:
                add("figshare", h.get("doi"), t, str(h.get("published_date", ""))[:4], "")
print("figshare", len(seen), flush=True)
for k, v in sorted(seen.items(), key=lambda kv: kv[0][0]):
    print(k, v)
