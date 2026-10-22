"""Polite downloader. Usage: dl.py URL OUT [--pdf]. Honest UA, per-host 10s throttle, no challenge evasion."""
import requests, sys, os, time, json, urllib.parse
UA={"User-Agent":"Mozilla/5.0 (compatible; RamanLitResearch/0.1; academic use)"}
LAST=os.path.join(os.path.dirname(__file__),".host_last.json")
def throttle(url,gap=10):
    host=urllib.parse.urlparse(url).netloc
    d=json.load(open(LAST)) if os.path.exists(LAST) else {}
    wait=d.get(host,0)+gap-time.time()
    if wait>0: time.sleep(wait)
    d[host]=time.time(); json.dump(d,open(LAST,"w"))
def fetch(url,out,want_pdf=True,gap=10,timeout=90):
    throttle(url,gap)
    try:
        r=requests.get(url,headers=UA,timeout=timeout,allow_redirects=True)
    except Exception as e:
        return False,f"EXC {e}"
    ct=r.headers.get("content-type","")
    body=r.content
    if r.status_code!=200: return False,f"HTTP {r.status_code} ct={ct} final={r.url[:120]}"
    if want_pdf and not body[:4]==b"%PDF": 
        snippet=body[:200].decode("latin1","replace").replace("\n"," ")
        return False,f"not pdf ct={ct} final={r.url[:120]} head={snippet[:100]}"
    os.makedirs(os.path.dirname(out) or ".",exist_ok=True)
    open(out,"wb").write(body)
    return True,f"OK {len(body)} bytes ct={ct} final={r.url[:120]}"
if __name__=="__main__":
    ok,msg=fetch(sys.argv[1],sys.argv[2],want_pdf=("--nopdf" not in sys.argv))
    print(ok,msg)
