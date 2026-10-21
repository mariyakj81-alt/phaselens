import sys,os,re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cfg_A import CACHE
import dossier_A as D
N=int(os.environ.get("N","6")); W=int(os.environ.get("W","500"))
for pm in sys.argv[1:]:
    paras=D.paras_of(os.path.join(CACHE,pm+".xml"))
    print("#####",pm)
    k=0
    for p in paras:
        if re.search(r"(?i)raman",p) and (re.search(r"(?i)\bnm\b|laser|excitation|spectrometer|objective",p) or re.search(r"(?i)calcite",p)):
            print(" *",p[:W]); k+=1
            if k>=N: break
