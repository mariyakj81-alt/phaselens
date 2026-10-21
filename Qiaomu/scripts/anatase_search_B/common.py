"""Shared helpers for ANATASE search agent B. Honest UA, per-host throttle, no challenge evasion."""
import requests, os, time, json, urllib.parse, sys
UA = {"User-Agent": "Mozilla/5.0 (compatible; RamanLitResearch/0.1; academic use)"}
HERE = os.path.dirname(os.path.abspath(__file__))
LAST = os.path.join(HERE, ".host_last.json")
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
STAGE = r"C:\Users\yqm12\AppData\Local\Temp\claude\G--My-Drive-Qiaomu-Coding-LLM-Hackason\6904f568-fbff-48aa-b9f2-a1642df7e094\scratchpad\B_stage"
os.makedirs(STAGE, exist_ok=True)
GAPS = {"arxiv.org": 3, "export.arxiv.org": 3}


def throttle(url, gap=None):
    host = urllib.parse.urlparse(url).netloc
    if gap is None:
        gap = GAPS.get(host, 10)
    try:
        d = json.load(open(LAST)) if os.path.exists(LAST) else {}
    except Exception:
        d = {}
    wait = d.get(host, 0) + gap - time.time()
    if wait > 0:
        time.sleep(wait)
    d[host] = time.time()
    try:
        tmp = LAST + "." + str(os.getpid())
        json.dump(d, open(tmp, "w"))
        os.replace(tmp, LAST)
    except Exception:
        pass


def get(url, params=None, gap=None, timeout=90, stream=False, headers=None):
    throttle(url, gap)
    h = dict(UA)
    if headers:
        h.update(headers)
    return requests.get(url, params=params, headers=h, timeout=timeout, allow_redirects=True, stream=stream)


def fetch(url, out, want_pdf=True, gap=None, timeout=(20, 90)):
    try:
        r = get(url, gap=gap, timeout=timeout)
    except Exception as e:
        return False, f"EXC {e}"
    ct = r.headers.get("content-type", "")
    body = r.content
    if r.status_code != 200:
        return False, f"HTTP {r.status_code} ct={ct} final={r.url[:120]}"
    if want_pdf and body[:4] != b"%PDF":
        snippet = body[:200].decode("latin1", "replace").replace("\n", " ")
        return False, f"not pdf ct={ct} final={r.url[:120]} head={snippet[:100]}"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "wb").write(body)
    return True, f"OK {len(body)} bytes ct={ct} final={r.url[:120]}"


def claim(doi):
    """Append claim and check for earlier claim by A. Returns True if we own it."""
    path = os.path.join(ROOT, "anatase", "_claims.txt")
    key = doi.strip().lower()
    lines = open(path, encoding="utf-8").read().splitlines()
    for ln in lines[1:]:
        p = ln.split("\t")
        if len(p) >= 2 and p[0].strip().lower() == key:
            return p[1] == "B"
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(f"{doi}\tB\t{time.strftime('%H:%M:%S')}\n")
    lines = open(path, encoding="utf-8").read().splitlines()
    for ln in lines[1:]:
        p = ln.split("\t")
        if len(p) >= 2 and p[0].strip().lower() == key:
            return p[1] == "B"
    return True
