#!/usr/bin/env python3
"""Aug 2 arrival shift: 13 days -> 12, merge Asakusa/Skytree into the
Akihabara day, real United flight info on first/last days, renumber
everything. Asserted string surgery, same pattern as prior edits.
NOTE: confirmation number (PNR) deliberately NOT published -- public page."""
import re, os, sys

CLONE = "/Users/felixvilla/japan-2026-work"
SRC = "/Users/felixvilla/Projects/felix-assistant/reports/japan-trip"
MAP = {2: 3, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 8, 10: 9, 11: 10, 12: 11, 13: 12}

def rep1(t, old, new, label=""):
    n = t.count(old)
    assert n == 1, f"rep1[{label}]: expected 1 occurrence, got {n}: {old[:80]!r}"
    return t.replace(old, new)

def li_block(s, start):
    assert s.startswith("<li>", start), f"li_block: not at <li>: {s[start:start+30]!r}"
    depth = 0
    for m in re.finditer(r"<li[ >]|</li>", s[start:]):
        depth += 1 if m.group(0).startswith("<li") else -1
        if depth == 0:
            return s[start:start + m.end()]
    raise AssertionError("li_block: unbalanced")

def beat_li(t, marker):
    i = t.find(marker)
    assert i != -1, f"beat marker missing: {marker}"
    j = t.rfind("<li><button", 0, i)
    assert j != -1
    return li_block(t, j)

def flight_beat(title, blurb, spots, tips):
    sp = "".join(f'<div class="pspot"><b>{b}</b><span>{s}</span></div>' for b, s in spots)
    tp = "".join(f"<li>{x}</li>" for x in tips)
    return ('<li><button class="lnk" type="button" aria-expanded="false">'
            '<span class="dot">&bull;</span><span class="txt"><b>' + title + "</b> &mdash; "
            + blurb + '</span><span class="go">+</span></button>'
            '<div class="panel"><div class="inner"><div class="pspots">' + sp +
            '</div><div class="ptips"><h4>Good to know</h4><ul>' + tp +
            "</ul></div></div></div></li>")

# ---------------------------------------------------------------- index.html
p = os.path.join(CLONE, "index.html")
t = open(p).read()
orig_len = len(t)

# -- extract pieces from card 2 before deleting it
senso = beat_li(t, "<b>Senso-ji</b>")
skytree = beat_li(t, "<b>Tokyo Skytree</b>")

starts = [m.start() for m in re.finditer(r'<article class="day', t)]
assert len(starts) == 13
card2 = t[starts[1]:starts[2]]
assert 'id="day-2"' in card2 and "Old Tokyo Meets New" in card2
assert card2.rstrip().endswith("</article>"), card2[-80:]
m = re.search(r'<ul class="remix-alts">', card2)
assert m
depth, alts_end = 0, None
for mm in re.finditer(r"<ul[ >]|</ul>", card2[m.start():]):
    depth += 1 if mm.group(0).startswith("<ul") else -1
    if depth == 0:
        alts_end = m.start() + mm.start()
        break
assert alts_end
card2_alts = card2[m.end():alts_end]  # inner <li>s of card 2's remix options
assert "Street Kart" in card2_alts

# -- delete card 2
t = t.replace(card2, "", 1)
assert 'id="day-2"' not in t

# -- card 1: date, intro, flight beat
t = rep1(t, "Shinjuku by night &middot; Sat Aug 1",
         "Land at Narita + Shinjuku by night &middot; Sun Aug 2", "card1 tag")
m = re.search(r"<p>Arrival day, so the only goal[^<]*</p>", t)
assert m, "card1 intro not found"
t = t.replace(m.group(0),
    "<p>Wheels up from O&#x27;Hare Saturday morning, land at Narita 2:10 PM Sunday. "
    "Drop the bags in Shinjuku, then one rule: stay awake until dark and let the neon do the work.</p>", 1)
fb = flight_beat(
    "The flight over", "ORD &rarr; LAX &rarr; Narita, lands 2:10 PM",
    [("UA 2373 &middot; Sat Aug 1", "Chicago O&#x27;Hare 6:00 AM to Los Angeles 8:27 AM. Early alarm, worth it."),
     ("UA 32 &middot; Sat Aug 1", "LAX 10:55 AM across the Pacific. You cross the date line and land Tokyo Narita 2:10 PM Sunday."),
     ("Narita &rarr; Shinjuku", "Narita Express straight to Shinjuku Station, about 80 minutes. Hotel by 5 PM."),
     ("Seats", "22B / 35B on the way out, both of us ticketed through, economy.")],
    ["Stay awake until at least 9 PM local. That one rule beats the jet lag.",
     "Grab Suica cards at the airport station, they work on trains and konbini everywhere.",
     "Passports out the night before. Triple-check.",])
i = t.find('<ul class="beats">')
assert i != -1
t = t[:i + len('<ul class="beats">')] + fb + t[i + len('<ul class="beats">'):]

# -- card 4 (Akihabara) becomes the merged Old Tokyo + Arcade day
t = rep1(t, "<h2>Arcade Heaven</h2>", "<h2>Old Tokyo, Then Arcade Heaven</h2>", "card4 h2")
t = rep1(t, "Akihabara + Ueno &middot; Tue Aug 4",
         "Asakusa + Skytree + Akihabara &middot; Tue Aug 4", "card4 tag")
m = re.search(r"<p>Whole buildings that are nothing but arcades[^<]*</p>", t)
assert m, "card4 intro not found"
t = t.replace(m.group(0),
    "<p>A temple from the 600s at sunrise, a 634m tower by noon &mdash; then whole buildings "
    "that are nothing but arcades, wrapped in anime billboards. Old Tokyo and Electric Town in one loaded day.</p>", 1)
# insert Senso-ji + Skytree beats at the top of card 4's beats
i = t.find("<b>Akihabara</b>")
assert i != -1
j = t.rfind('<ul class="beats">', 0, i)
assert j != -1
ins = j + len('<ul class="beats">')
t = t[:ins] + senso + skytree + t[ins:]
# drop the Ueno beat
ueno = beat_li(t, "<b>Ueno</b>")
t = t.replace(ueno, "", 1)
# remix: fix the stale Ueno reference, append card 2's remix options
assert "Keep Ueno as a mellow morning," in t
t = rep1(t, "Keep Ueno as a mellow morning,", "Do Senso-ji and Skytree before lunch,", "remix why")
i = t.find("Akihabara: Hard Mode")
assert i != -1
m = re.search(r'<ul class="remix-alts">', t[i:])
assert m
t = t[:i + m.end()] + card2_alts + t[i + m.end():]

# -- renumber ids, alts, day-nums (ascending old order is collision-safe)
for old in range(3, 14):
    new = MAP[old]
    t = rep1(t, f'id="day-{old}"', f'id="day-{new}"', f"id {old}")
    t = rep1(t, f'alt="Day {old}"', f'alt="Day {new}"', f"alt {old}")
    t = rep1(t, f"<small>Day</small><b>{old}</b>", f"<small>Day</small><b>{new}</b>", f"num {old}")

# -- daynav: regenerate 1..12
m = re.search(r'(<a href="#day-\d+">\d+</a>\s*)+', t)
assert m
t = t.replace(m.group(0), "".join(f'<a href="#day-{n}">{n}</a>' for n in range(1, 13)), 1)

# -- JS chapter split: Tokyo is now days 1-4
t = rep1(t, "n<=5 ?", "n<=4 ?", "chap split")

# -- hero + week divider + closing copy
t = rep1(t, "August 1 &ndash; 13, 2026</b> &nbsp;&middot;&nbsp; 13 days",
         "August 1 &ndash; 13, 2026</b> &nbsp;&middot;&nbsp; 12 days", "hero days")
t = rep1(t, "Week One &middot; Aug 1&ndash;5", "Week One &middot; Aug 2&ndash;5", "wk1 divider")
t = rep1(t, "Thirteen days, done right.", "Twelve days, done right.", "13 copy")

# -- last day card: flight home beat at the end of its beats
fb2 = flight_beat(
    "The flight home", "KIX 4:55 PM &rarr; SFO &rarr; ORD 8:26 PM, same Thursday",
    [("UA 34 &middot; Thu Aug 13", "Kansai 4:55 PM to San Francisco 11:05 AM the same day &mdash; you land before you took off. Time zones giveth back."),
     ("UA 2250 &middot; Thu Aug 13", "SFO 1:54 PM, into O&#x27;Hare 8:26 PM. Home in time to sleep in your own bed."),
     ("Getting to KIX", "About 70 minutes from Osaka Castle by Haruka express or the rapi:t. Leave the castle by 1:30 PM.")],
    ["Be at KIX by 2 PM &mdash; international check-in plus tax-free paperwork takes a minute.",
     "Do the souvenir sweep the night before, not on the way out.",
     "SFO connection is under 3 hours with immigration &mdash; tight but standard. No checked-bag drama if you pack carry-on smart."])
i = t.find("<b>Osaka Castle</b>")
assert i != -1
j = t.find('<div class="remix"', i)
assert j != -1
k = t.rfind("</ul>", i, j)
assert k != -1
t = t[:k] + fb2 + t[k:]

assert len([m for m in re.finditer(r'<article class="day', t)]) == 12
assert t.count('class="day fav"') == 2 and 'id="day-3"' in t and 'id="day-9"' in t
open(p, "w").write(t)
print(f"index.html: {orig_len} -> {len(t)} bytes, 12 day cards")

# ---------------------------------------------------------- tokyo-week-one deck
for root in (CLONE, SRC):
    p = os.path.join(root, "tokyo-week-one.html")
    d = open(p).read()
    starts = [m.start() for m in re.finditer(r"<article", d)]
    assert len(starts) == 5, p
    card2 = d[starts[1]:starts[2]]
    assert "Old Tokyo Meets New" in card2
    # pull the three page links out of the deck's day-2 card
    links = re.findall(r'<li><a class="lnk"[^>]*href="pages/(?:sensoji|skytree)\.html".*?</a></li>', card2, re.S)
    assert len(links) == 2, len(links)
    d = d.replace(card2, "", 1)
    d = rep1(d, "<h2>Arcade Heaven</h2>", "<h2>Old Tokyo, Then Arcade Heaven</h2>", "deck h2")
    d = rep1(d, '<div class="tag">Akihabara + Ueno</div>',
             '<div class="tag">Asakusa + Skytree + Akihabara</div>', "deck tag")
    # add senso/skytree links at top of that card's beats, drop the ueno link
    i = d.find('href="pages/akihabara.html"')
    assert i != -1
    j = d.rfind('<ul class="beats">', 0, i)
    ins = j + len('<ul class="beats">')
    d = d[:ins] + "".join(links) + d[ins:]
    m = re.search(r'\s*<li><a class="lnk"[^>]*href="pages/ueno\.html".*?</a></li>', d, re.S)
    assert m
    d = d.replace(m.group(0), "", 1)
    # renumber 3,4,5 -> 2,3,4
    for old in (3, 4, 5):
        d = rep1(d, f"<small>Day</small><b>{old}</b>", f"<small>Day</small><b>{MAP[old]}</b>", f"deck num {old}")
    d = d.replace("August 1 &ndash; 13, 2026", "August 1 &ndash; 13, 2026", 1)  # dates line unchanged
    if "13 days" in d:
        d = rep1(d, "13 days", "12 days", "deck days")
    open(p, "w").write(d)
    print(f"{p}: 4 cards")

# -------------------------------------------------------- kyoto-osaka deck
for root in (CLONE, SRC):
    p = os.path.join(root, "kyoto-osaka-week-two.html")
    d = open(p).read()
    for old in range(6, 14):
        pat = f"<small>Day</small><b>{old}</b>"
        if pat in d:
            d = rep1(d, pat, f"<small>Day</small><b>{MAP[old]}</b>", f"wk2 num {old}")
        else:
            # some decks label as Day N in other markup; fail loudly if neither
            assert re.search(rf">Day {old}<", d), f"wk2: no Day {old} marker"
            d = rep1(d, f">Day {old}<", f">Day {MAP[old]}<", f"wk2 alt num {old}")
    if "13 days" in d:
        d = rep1(d, "13 days", "12 days", "wk2 days")
    open(p, "w").write(d)
    print(f"{p}: renumbered")

# -------------------------------------------------------------- pages badges
n_badge = 0
for root in (CLONE, SRC):
    pdir = os.path.join(root, "pages")
    for f in sorted(os.listdir(pdir)):
        if not f.endswith(".html"):
            continue
        fp = os.path.join(pdir, f)
        d = open(fp).read()
        m = re.search(r'<div class="badge">Day (\d+)</div>', d)
        if not m:
            continue
        old = int(m.group(1))
        new = MAP.get(old, old)
        if new != old:
            d = d.replace(m.group(0), f'<div class="badge">Day {new}</div>', 1)
            open(fp, "w").write(d)
            n_badge += 1
print(f"page badges renumbered: {n_badge}")

# ------------------------------------------------------------- builder dicts
for fn in ("build_pages.py", "build_week2.py"):
    fp = os.path.join(SRC, fn)
    d = open(fp).read()
    d2 = re.sub(r"day=(\d+)(?=[,)])", lambda m: f"day={MAP.get(int(m.group(1)), int(m.group(1)))}", d)
    assert d2 != d
    open(fp, "w").write(d2)
    print(f"{fn}: day= values remapped")

print("ALL OK")
