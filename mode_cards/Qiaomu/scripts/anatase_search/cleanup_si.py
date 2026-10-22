import os, shutil, sys, re
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
OUT=os.path.join(ROOT,"anatase")
IMGEXT={".gif",".jpg",".jpeg",".png",".tif",".tiff",".bmp"}
for folder in sorted(os.listdir(OUT)):
    d=os.path.join(OUT,folder); sid=os.path.join(d,"SI"); ud=os.path.join(sid,"unzipped")
    if not os.path.isdir(sid): continue
    if not os.path.isdir(ud) or not os.path.exists(os.path.join(sid,'supplementary.zip')):
        continue   # already cleaned or nothing to do
    real_files=[]; real_dirs=[]
    for name in os.listdir(ud):
        p=os.path.join(ud,name)
        if os.path.isdir(p) and name.endswith("_x"): real_dirs.append((name,p)); continue
        if os.path.isfile(p) and os.path.splitext(name)[1].lower() not in IMGEXT: real_files.append((name,p))
    tmp=os.path.join(d,"SI_new"); os.makedirs(tmp,exist_ok=True)
    for name,p in real_files: shutil.copyfile(p,os.path.join(tmp,name))
    for name,p in real_dirs:
        dest=os.path.join(tmp,"unzipped",name[:-2]); os.makedirs(os.path.dirname(dest),exist_ok=True); shutil.copytree(p,dest)
    shutil.rmtree(sid)
    if any(os.scandir(tmp)): os.rename(tmp,sid)
    else: shutil.rmtree(tmp)
    print(folder,"->",[os.path.relpath(os.path.join(r,f),d).replace("\\","/") for r,_,fs in os.walk(os.path.join(d,"SI")) for f in fs] if os.path.isdir(os.path.join(d,"SI")) else "no SI")
