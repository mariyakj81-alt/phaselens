import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_all as S
from concurrent.futures import ThreadPoolExecutor
pool=json.load(open(S.POOL,encoding="utf-8"))
keys=list(pool)[::-1]
def w(k):
    S.fetch_one(k); time.sleep(0.4)
with ThreadPoolExecutor(4) as ex:
    list(ex.map(w,keys))
print("done")
