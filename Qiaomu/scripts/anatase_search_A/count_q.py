import requests, sys, time
UA={"User-Agent":"Mozilla/5.0 (compatible; RamanLitResearch/0.1; academic use)"}
for q in sys.argv[1:]:
    r=requests.get("https://www.ebi.ac.uk/europepmc/webservices/rest/search",params={"query":q+" AND OPEN_ACCESS:y","format":"json","resultType":"lite","pageSize":1},headers=UA,timeout=60)
    print(r.json().get("hitCount"),q)
    time.sleep(1)
