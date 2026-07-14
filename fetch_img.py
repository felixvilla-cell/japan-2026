#!/usr/bin/env python3
"""Fetch Wikimedia Commons images. Usage: python3 fetch_img.py jobs.json
jobs.json = [{"terms":["term1","term2"], "out":"/abs/path.jpg"}, ...]
Tries each term until one yields an image. Compresses with sips after."""
import sys, json, os, urllib.request, urllib.parse, subprocess
UA={'User-Agent':'FelixTripDeck/1.0 (personal itinerary; felix.a.villa@gsmsllc.com)'}

def search(term):
    api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({
        "action":"query","generator":"search","gsrsearch":term,"gsrnamespace":6,
        "gsrlimit":10,"prop":"imageinfo","iiprop":"url|mime|size","iiurlwidth":1300,"format":"json"})
    d=json.load(urllib.request.urlopen(urllib.request.Request(api,headers=UA),timeout=30))
    pages=(d.get("query") or {}).get("pages") or {}
    best=None
    for p in pages.values():
        ii=(p.get("imageinfo") or [{}])[0]
        if ii.get("mime") not in ("image/jpeg","image/png"): continue
        url=ii.get("thumburl") or ii.get("url"); w=ii.get("thumbwidth") or 0
        if not url: continue
        if best is None or w>best[1]: best=(url,w)
    return best[0] if best else None

def fetch(terms,out):
    if os.path.exists(out) and os.path.getsize(out)>8000: return "skip"
    for t in terms:
        try:
            url=search(t)
            if not url: continue
            data=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=60).read()
            if len(data)<8000: continue
            open(out,"wb").write(data)
            subprocess.run(["sips","-Z","1300","--setProperty","formatOptions","58",out],
                           stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            return "OK:"+t
        except Exception as e:
            continue
    return "MISS"

jobs=json.load(open(sys.argv[1]))
ok=miss=0
for j in jobs:
    r=fetch(j["terms"], j["out"])
    if r.startswith("OK") or r=="skip": ok+=1
    else: miss+=1
    print(r, "->", os.path.basename(j["out"]))
print(f"done: {ok} ok, {miss} miss")
