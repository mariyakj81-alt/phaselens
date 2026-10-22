import time, json, os, urllib.parse, requests
UA = "Mozilla/5.0 (compatible; RamanLitResearch/0.1; academic use)"
_last = {}
def get(url, params=None, min_gap=1.0, timeout=60, stream=False, headers=None, retries=2):
    host = urllib.parse.urlparse(url).netloc
    h = {"User-Agent": UA}
    if headers: h.update(headers)
    err = None
    for attempt in range(retries + 1):
        gap = _last.get(host, 0) + min_gap - time.time()
        if gap > 0: time.sleep(gap)
        try:
            r = requests.get(url, params=params, headers=h, timeout=timeout, stream=stream, allow_redirects=True)
            _last[host] = time.time()
            return r
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            _last[host] = time.time(); err = e
            if isinstance(e, requests.exceptions.SSLError) and "CERTIFICATE_VERIFY_FAILED" in str(e): break
            time.sleep(3)
    raise err
