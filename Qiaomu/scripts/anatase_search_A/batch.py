"""Sequentially build a list of PMC articles with consecutive IDs. Usage: batch.py START_ID PMC1 PMC2 ...   (log to stdout)"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_A
start = int(sys.argv[1])
for i, pmc in enumerate(sys.argv[2:]):
    aid = f"ANA{start+i:03d}" if start < 900 else f"ANAX{start-900+i:02d}"
    try:
        r = build_A.build(pmc, aid)
        if r is None or not r.get("pdf_url"):
            print("FAILED", pmc, aid, flush=True)
    except Exception as e:
        print("ERR", pmc, aid, repr(e)[:200], flush=True)
