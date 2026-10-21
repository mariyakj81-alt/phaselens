import time, json, os, urllib.parse, requests
UA = "Mozilla/5.0 (compatible; RamanLitResearch/0.1; academic use)"
_last = {}
def get(url, params=None, min_gap=1.0, timeout=60, stream=False, headers=None):
    host = urllib.parse.urlparse(url).netloc
    gap = _last.get(host, 0) + min_gap - time.time()
    if gap > 0: time.sleep(gap)
    h = {"User-Agent": UA}
    if headers: h.update(headers)
    try:
        r = requests.get(url, params=params, headers=h, timeout=timeout, stream=stream, allow_redirects=True)
    finally:
        _last[host] = time.time()
    return r
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
def epmc_search(q, page_size=100, max_n=2000, result_type="core", sort=None):
    cursor = "*"; out = []; hits = None
    while len(out) < max_n:
        p = {"query": q, "format": "json", "resultType": result_type, "pageSize": page_size, "cursorMark": cursor}
        if sort: p["sort"] = sort
        r = get(EPMC, params=p, min_gap=0.5)
        if r.status_code != 200:
            print("EPMC fail", r.status_code, q[:60]); break
        j = r.json(); hits = j.get("hitCount")
        res = j["resultList"]["result"]
        out += res
        nc = j.get("nextCursorMark")
        if not res or not nc or nc == cursor: break
        cursor = nc
    return hits, out
