import time, os, urllib.parse, requests
UA = "RamanLitResearch/0.1 (academic literature collection; contact via project repo)"
_last = {}
def get(url, params=None, min_gap=10.0, timeout=60, stream=False, headers=None):
    host = urllib.parse.urlparse(url).netloc
    gap = _last.get(host, 0) + min_gap - time.time()
    if gap > 0:
        time.sleep(gap)
    h = {"User-Agent": UA}
    if headers:
        h.update(headers)
    try:
        r = requests.get(url, params=params, headers=h, timeout=timeout, stream=stream, allow_redirects=True)
    finally:
        _last[host] = time.time()
    return r

def save_pdf(url, dest, min_gap=10.0, timeout=(20, 120)):
    r = get(url, min_gap=min_gap, timeout=timeout)
    ok = r.status_code == 200 and r.content[:5] == b"%PDF-"
    if ok:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "wb").write(r.content)
    return r.status_code, r.headers.get("content-type"), len(r.content), ok
