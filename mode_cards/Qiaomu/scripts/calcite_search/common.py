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
