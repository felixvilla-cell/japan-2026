#!/usr/bin/env python3
"""Second pass: fix 2 duplicate panels + make remix options expandable with images+info."""
import re, json, html, os

WORK = "/Users/felixvilla/japan-2026-work"
SRC = f"{WORK}/index.html"
s = open(SRC, encoding="utf-8").read()

enr = {int(k): v for k, v in json.load(open(f"{WORK}/remix_enriched.json")).items()}
manifest = json.load(open(f"{WORK}/remix_img_manifest.json"))
panel = json.load(open(f"{WORK}/japan_panel.json"))
orig = {int(d["day"]): d for lst in panel["remixes"] for d in lst}

def esc(t): return html.escape(str(t), quote=False)
def exists(rel): return os.path.getsize(os.path.join(WORK, rel)) > 8000 if os.path.exists(os.path.join(WORK, rel)) else False

# ---------------------------------------------------------------- CSS additions
css_add = """
  .remix-alts li{padding:0;overflow:hidden;}
  .remix-alts .lnk{display:flex;gap:11px;align-items:center;width:100%;padding:11px 13px;box-sizing:border-box;background:none;border:0;font:inherit;text-align:left;color:#dbe7ea;cursor:pointer;border-radius:9px;transition:background .2s;}
  @media(hover:hover){.remix-alts .lnk:hover{background:rgba(63,224,224,.08);}}
  .remix-alts .lnk:active{background:rgba(63,224,224,.12);}
  .remix-alts .lnk .txt{flex:1;font-size:14.5px;line-height:1.5;}
  .remix-alts .lnk b{color:#ff8fbf;border:0;display:inline;}
  .remix-alts .lnk .rblurb{color:#bcd0d6;}
  .remix-alts .go{flex:none;width:24px;height:24px;border-radius:50%;background:var(--neon);color:#061018;font-size:16px;font-weight:800;line-height:24px;text-align:center;transition:transform .25s ease;}
  .remix-alts .lnk[aria-expanded="true"] .go{transform:rotate(45deg);background:var(--neon2);color:#fff;}
  .remix-alts .panel .inner{border-top:1px dashed rgba(63,224,224,.22);padding:4px 13px 14px;}
  .ralt-desc{font-size:13.8px;color:#cfe6ea;line-height:1.55;margin:12px 0 0;}
  .remix-alts .ptips{margin-top:12px;background:rgba(6,16,24,.5);border:1px solid rgba(63,224,224,.2);}
  .remix-alts .ptips h4{color:var(--neon);}
  .remix-alts .ptips li:before{background:var(--neon2);border-color:var(--neon);}
  body.remix-on .remix{max-height:9000px;}
"""
i1 = s.rindex("</style>")
s = s[:i1] + css_add + s[i1:]

# ---------------------------------------------------------------- JS: broaden expand handler to all .lnk
assert "document.querySelectorAll('.beats .lnk')" in s
s = s.replace("document.querySelectorAll('.beats .lnk')", "document.querySelectorAll('.lnk')", 1)

# ---------------------------------------------------------------- helpers
def gallery(figs):
    figs = [f for f in figs if exists(f)]
    if not figs: return ""
    cells = "".join(f'<figure><img data-src="{f}" alt="" decoding="async"></figure>' for f in figs)
    return f'<div class="pgal">{cells}</div>'

def spots_html(spots):
    return '<div class="pspots">' + "".join(
        f'<div class="pspot"><b>{esc(n)}</b><span>{esc(d)}</span></div>' for n, d in spots) + '</div>'

def tips_html(title, tips):
    return (f'<div class="ptips"><h4>{esc(title)}</h4><ul>' +
            "".join(f'<li>{esc(t)}</li>' for t in tips) + '</ul></div>')

# ---------------------------------------------------------------- remix block builder (expandable)
def build_remix2(day):
    o = orig[day]; e = enr[day]
    alts_html = ""
    for ai, a in enumerate(o["alts"]):
        ea = e[ai] if ai < len(e) else {}
        name = a["name"]; blurb = a["blurb"]
        desc = ea.get("desc", ""); facts = ea.get("facts", [])
        figs = manifest.get(f"{day}-{ai}", [])
        gal = gallery(figs)
        inner = gal
        if desc: inner += f'<p class="ralt-desc">{esc(desc)}</p>'
        if facts: inner += tips_html("Quick facts", facts)
        panel = (f'<div class="panel"><div class="inner">{inner}</div></div>') if inner else ""
        go = '<span class="go">+</span>' if inner else ''
        exp = 'aria-expanded="false"' if inner else 'aria-expanded="false" disabled'
        alts_html += (
            f'<li><button class="lnk" type="button" {exp}>'
            f'<span class="txt"><b>{esc(name)}</b> <span class="rblurb">{esc(blurb)}</span></span>{go}</button>'
            f'{panel}</li>')
    return (
        '<div class="remix"><div class="box">'
        '<div class="remix-head"><span class="remix-tag">&#10022; Felix’s Remix</span>'
        f'<h3>{esc(o["remixTitle"])}</h3><p class="remix-vibe">{esc(o["vibe"])}</p></div>'
        f'<p class="remix-why">{esc(o["why"])}</p>'
        f'<ul class="remix-alts">{alts_html}</ul></div></div>')

# ---------------------------------------------------------------- dup fixes
POWERUP_SPOTS = [
    ("Mario Kart: Koopa's Challenge", "AR-headset kart race through Bowser's Castle, the land's flagship ride and worth any wait."),
    ("Power-Up Bands", "Wristbands that link to the USJ app; punch real question blocks, collect coins and keys, tracked per person. Dad vs Felix."),
    ("Key challenges", "Beat the themed mini-games scattered around the land to earn keys for the Bowser Jr. boss showdown."),
    ("Live scoreboard", "The app ranks your coins and stamps in real time, so settle who's really Player One by park close."),
    ("Kinopio's Cafe", "Refuel inside a giant Toad mushroom between rounds, the best-themed lunch in the park."),
]
POWERUP_TIPS = ["Buy a band in-park, one each.", "Link it in the USJ app first thing.", "Hit blocks and mini-games early, before lines."]
OKO_SPOTS = [
    ("Hiroshima-style", "Layered, not mixed: a thin crepe, a mountain of cabbage, noodles, egg, and pork, griddled in stacks."),
    ("Okonomimura", "A building of around 25 griddle stalls over three floors, pick any counter and sit down."),
    ("Eat off the teppan", "It's served straight on the hot griddle; eat it with the little metal spatula, the hera."),
    ("Otafuku sauce", "The sweet-savory brown sauce that defines it, slathered on and offered on the side."),
    ("The local debate", "Hiroshima folks will insist their layered version beats Osaka's mixed one. Judge for yourself."),
]
OKO_TIPS = ["Grab a counter seat around the griddle.", "Expect a wait at the famous stalls.", "Okonomimura is near Hondori and the Peace Park."]

def fix_beat(art, label, figs, spots, tips_title, tips):
    gal = gallery(figs)
    newinner = gal + spots_html(spots) + tips_html(tips_title, tips)
    pat = re.compile(r'(<b>' + re.escape(label) + r'</b>.*?<div class="panel"><div class="inner">).*?(</div></div></li>)', re.S)
    new, n = pat.subn(lambda m: m.group(1) + newinner + m.group(2), art, count=1)
    assert n == 1, f"dup-fix miss: {label}"
    return new

# ---------------------------------------------------------------- transform each article
def xform(m):
    art = m.group(0)
    day = int(re.search(r'<div class="day-num"><small>Day</small><b>(\d+)</b>', art).group(1))
    if day == 10:
        art = fix_beat(art, "Power-Up Band battle",
                       ["img/g/powerup-1.jpg", "img/g/powerup-2.jpg", "img/g/powerup-3.jpg"],
                       POWERUP_SPOTS, "Good to know", POWERUP_TIPS)
    if day == 12:
        art = fix_beat(art, "Hiroshima okonomiyaki",
                       ["img/g/okonomiyaki-1.jpg", "img/g/okonomiyaki-2.jpg", "img/g/okonomiyaki-3.jpg"],
                       OKO_SPOTS, "Good to know", OKO_TIPS)
    art = re.sub(r'<div class="remix"><div class="box">.*?</div></div>(\s*<span class="pill")',
                 lambda mm: build_remix2(day) + mm.group(1), art, count=1, flags=re.S)
    return art

s, nc = re.subn(r'<article class="day[^"]*"[^>]*>.*?</article>', xform, s, flags=re.S)
assert nc == 13, f"articles {nc}"

open(SRC, "w", encoding="utf-8").write(s)
# report
ralt_panels = s.count('class="lnk" type="button" aria-expanded="false"><span class="txt"><b>')
print("OK. articles:", nc)
print("remix expandable options:", s.count('remix-alts') , "blocks;", s.count('<li><button class="lnk"'))
print("bytes:", len(s))
