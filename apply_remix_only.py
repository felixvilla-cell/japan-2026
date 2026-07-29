#!/usr/bin/env python3
"""
2026-07-28 transform of the japan-2026 one-pager. Three changes Felix asked for:

  1. Swap Day 9 / Day 10  -- USJ + Super Nintendo World moves to TUE AUG 11
     (tickets bought on Klook, non-changeable); Den Den Town + Dotonbori takes
     Mon Aug 10. Day numbers and dates stay put, the content moves.
  2. Remix-only -- Felix's Remix becomes THE plan on every day. The base .beats
     lists and the fixed [The Plan | Felix's Remix] toggle come out. Hard
     logistics (flights, shinkansen, hotel moves, the USJ timed windows) are
     preserved as an always-visible "Locked in" line, because those are facts
     and not options.
  3. Cross-link index.html <-> checklist.html.

Every edit asserts. Run once against a clean checkout.
"""
import re, sys

SRC = 'index.html'
h = open(SRC, encoding='utf-8').read()
orig = h

def sub1(pattern, repl, label, flags=0, count=1):
    """Regex replace that must fire exactly `count` times."""
    global h
    new, n = re.subn(pattern, repl, h, count=count, flags=flags)
    assert n == count, f'{label}: expected {count} replacement(s), got {n}'
    h = new

def swap_str(a, b, label):
    """Exact-match single replacement."""
    global h
    assert h.count(a) == 1, f'{label}: anchor found {h.count(a)}x, need exactly 1'
    h = h.replace(a, b, 1)


# ---------------------------------------------------------------- 1. day swap
art_re = re.compile(r'<article class="day([^"]*)" id="day-(\d+)">(.*?)</article>', re.S)
arts = {m.group(2): m for m in art_re.finditer(h)}
assert '9' in arts and '10' in arts, 'day-9 / day-10 not found'

def parts(m):
    body = m.group(3)
    hero = re.search(r'<img src="([^"]+)" alt="Day \d+"', body).group(1)
    title = re.search(r'<div class="day-title"><h2>(.*?)</h2>', body).group(1)
    tag = re.search(r'<div class="tag">(.*?)</div>', body).group(1)
    label, _, date = tag.rpartition(' &middot; ')
    dbody = re.search(r'<div class="day-body">(.*)</div>\s*$', body, re.S).group(1)
    return dict(hero=hero, title=title, label=label, date=date, dbody=dbody)

p9, p10 = parts(arts['9']), parts(arts['10'])
assert 'Nintendo' in p9['label'] and 'Aug 10' in p9['date'], f"day-9 sanity: {p9['label']} / {p9['date']}"
assert 'Den Den' in p10['label'] and 'Aug 11' in p10['date'], f"day-10 sanity: {p10['label']} / {p10['date']}"

def render(num, src, date, fav):
    cls = ' fav' if fav else ''
    return (
        f'<article class="day{cls}" id="day-{num}">\n'
        f'      <div class="day-photo"><img src="{src["hero"]}" alt="Day {num}" loading="lazy" decoding="async"><div class="grad"></div>\n'
        f'        <div class="day-head"><div class="day-num"><small>Day</small><b>{num}</b></div>\n'
        f'          <div class="day-title"><h2>{src["title"]}</h2><div class="tag">{src["label"]} &middot; {date}</div></div></div>\n'
        f'      </div>\n'
        f'      <div class="day-body">{src["dbody"]}</div>\n'
        f'    </article>'
    )

# Den Den content -> Day 9 (Mon Aug 10, not the favourite).
# USJ content   -> Day 10 (Tue Aug 11, keeps the gold `fav` glow).
swap_str(arts['9'].group(0), render(9, p10, p9['date'], fav=False), 'render day-9')
swap_str(arts['10'].group(0), render(10, p9, p10['date'], fav=True), 'render day-10')

assert re.search(r'id="day-9">.*?Den Den Town \+ Dotonbori &middot; Mon Aug 10', h, re.S), 'day-9 is not Den Den/Mon Aug 10'
assert re.search(r'class="day fav" id="day-10">.*?Super Nintendo World &middot; Tue Aug 11', h, re.S), 'day-10 is not USJ/Tue Aug 11'


# ------------------------------------------- 2. USJ day: reflect real tickets
swap_str('<span class="pill">Express Pass on sale now &mdash; buy this week</span>',
         '<span class="pill">Tickets bought &middot; SNW entry 12:30 PM</span>',
         'USJ pill')
# The park-day intro still says "on a Monday".
swap_str('Full day at Universal, on a Monday, when the park is at its calmest &mdash; which in August still means rope drop.',
         'Full day at Universal on Tuesday Aug 11. Studio Passes and Express Pass 5 are bought and in hand, '
         'so the queues are solved &mdash; the only thing that matters now is being at the Nintendo World gate at 12:30 sharp.',
         'USJ intro copy')

# Stale "buy the pass" tips inside the main SNW beat (that beat is about to be
# removed with the rest of .beats, but scrub it anyway so nothing stale survives
# in the file if the beats ever come back).
h = h.replace('Buy studio passes ahead, and strongly consider the Express Pass with timed Nintendo entry, August is peak season. On sale roughly 2 months out, so now.',
              'Studio Passes + Express Pass 5 bought for Tue Aug 11. Print all four QR codes, a phone screenshot is refused at the gate.')

# The remix alt that told him to go buy a pass is now a fact, not a to-do.
swap_str('<b>Universal Express Pass 4 or 7 (SNW timed entry)</b> <span class="rblurb">August is peak-heat and peak-crowd; the Express Pass + a Nintendo World area ticket is the difference between 3 rides and 10. Book the earliest SNW entry slot so you&#x27;re on Mario Kart before the mob.</span>'.replace('&#x27;', "'"),
         '<b>Express Pass 5 &mdash; bought, 12:30 PM Nintendo World entry</b> <span class="rblurb">Done. Mario Kart 12:30, Yoshi 1:00, and Hollywood Dream / Flying Dinosaur / Minion Mayhem are anytime that day. Mine-Cart Madness is standby, so hit it at 1:30 right after Yoshi.</span>',
         'remix alt 1 title/blurb')

swap_str("USJ's Express Pass lets you skip the standby line on a set number of headline rides, and in August those standby lines run 90 to 180 minutes. Super Nintendo World needs its own timed-entry ticket on top, so pairing an Express Pass with the earliest SNW slot is how you actually get on Mario Kart, Yoshi, and the big coasters instead of baking in queues.",
         "Bought on Klook for Tue Aug 11: two 1-Day Studio Passes plus two Universal Express Pass 5 ~Adventure Special~. That covers Mario Kart, Yoshi's Adventure, The Flying Dinosaur, Hollywood Dream and Minion Mayhem, with guaranteed Super Nintendo World entry at 12:30. Standby lines run 90 to 180 minutes in August, so this is the whole ballgame. Once you're inside Nintendo World you can stay as long as you want, but there is no re-entry if you walk out.",
         'remix alt 1 description')

swap_str('<li>Express 4 approx 10,800 yen and up</li><li>Express 7 approx 18,000 yen and up</li><li>SNW timed entry books via app, free with pass</li><li>Buy weeks ahead, peak dates sell out</li>',
         '<li>Nintendo World entry 12:30&ndash;1:30 PM</li><li>Mario Kart 12:30 &middot; Yoshi 1:00</li><li>Mine-Cart Madness is standby only</li><li>Print the QR codes, screenshots refused</li>',
         'remix alt 1 quick facts')


# --------------------------------------------------- 3. remix becomes THE plan
# Always-visible "Locked in" strip for the days whose only hard facts lived in
# the base beats. Authored from facts/trips.json, not scraped from the beats.
LOCKED = {
    '1':  'UA2373 ORD 6:00 AM &rarr; LAX, then UA32 LAX 10:55 AM &rarr; Narita, landing Sun Aug 2 at 2:10 PM. Hotel Gracery Shinjuku, four nights.',
    '5':  'Shinkansen Tokyo &rarr; Kyoto on Thu Aug 6. Solaria Nishitetsu Kyoto Premier, three nights.',
    '8':  'Train Kyoto &rarr; Osaka on Sun Aug 9. Fairfield by Marriott Namba, four nights.',
    '10': 'Studio Pass + Express Pass 5, both bought. Nintendo World entry 12:30 PM, Mario Kart 12:30, Yoshi 1:00. Print the QR codes.',
    '12': 'UA34 KIX 4:55 PM &rarr; SFO, then UA2250 SFO 1:54 PM &rarr; ORD 8:26 PM, same Thursday. Leave the castle by 1:30 PM.',
}

removed_beats = 0
removed_why = 0
added_locked = 0

def strip_balanced_ul(s, opener='<ul class="beats">'):
    """Remove `opener` .. its MATCHING </ul>. The beats panels contain nested
    <ul> lists (.ptips), so a non-greedy regex stops at the wrong </ul> and
    leaves orphaned markup behind. Walk the tags and track depth instead."""
    i = s.find(opener)
    if i == -1:
        return s, 0
    depth = 0
    for m in re.finditer(r'<ul\b|</ul>', s[i:]):
        depth += 1 if m.group(0).startswith('<ul') else -1
        if depth == 0:
            end = i + m.end()
            rest = s[end:]
            stripped = rest[:len(rest) - len(rest.lstrip())]
            return s[:i] + rest[len(stripped):], 1
    raise AssertionError('unbalanced <ul class="beats">')

def transform_day(m):
    global removed_beats, removed_why, added_locked
    cls, num, body = m.group(1), m.group(2), m.group(3)

    body, n = strip_balanced_ul(body)
    removed_beats += n
    assert '<ul class="beats">' not in body, f'day-{num}: more than one beats list'

    body, n2 = re.subn(r'<p class="remix-why">.*?</p>', '', body, flags=re.S)
    removed_why += n2

    if num in LOCKED:
        strip = (f'<div class="locked"><span class="lk">Locked in</span>'
                 f'<span>{LOCKED[num]}</span></div>')
        body, n3 = re.subn(r'(<div class="remix">)', strip + r'\1', body, count=1)
        assert n3 == 1, f'day-{num}: could not place Locked in strip'
        added_locked += 1

    return f'<article class="day{cls}" id="day-{num}">{body}</article>'

h = art_re.sub(transform_day, h)
assert removed_beats == 12, f'expected to strip 12 beats lists, stripped {removed_beats}'
assert removed_why == 12, f'expected to strip 12 remix-why paras, stripped {removed_why}'
assert added_locked == 5, f'expected 5 Locked in strips, added {added_locked}'
assert '<ul class="beats">' not in h, 'a beats list survived'
assert 'class="remix-why"' not in h, 'a remix-why survived'

# .remix always visible now (was collapsed, revealed by body.remix-on).
swap_str('''  .remix{margin-top:18px;overflow:hidden;max-height:0;opacity:0;
    transition:max-height .5s cubic-bezier(.2,.7,.2,1),opacity .35s ease,margin .3s ease;}
  body.remix-on .remix{max-height:1600px;opacity:1;margin-top:20px;}''',
'''  .remix{margin-top:20px;}
  .locked{display:flex;gap:11px;align-items:flex-start;margin-top:16px;padding:11px 14px;border-radius:11px;
    background:rgba(212,175,55,.07);border:1px solid rgba(212,175,55,.32);}
  .locked .lk{flex:0 0 auto;font-size:10.5px;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;
    color:var(--gold);padding-top:2px;}
  .locked span:last-child{font-size:13.5px;line-height:1.5;color:#e4dcc4;}''',
         'remix CSS -> always visible + .locked')

# Drop the toggle: CSS block, markup, and its JS handler.
swap_str('''  /* fixed remix toggle */
  .remix-toggle{position:fixed;bottom:18px;left:50%;transform:translateX(-50%);z-index:46;display:flex;gap:4px;
    background:rgba(11,15,28,.9);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);
    border:1px solid rgba(255,255,255,.16);border-radius:999px;padding:5px;box-shadow:0 12px 34px rgba(0,0,0,.55);}
  .remix-toggle button{border:0;background:none;color:#aab4c8;font:inherit;font-weight:800;font-size:13.5px;letter-spacing:.5px;
    padding:9px 18px;border-radius:999px;cursor:pointer;transition:background .25s,color .25s;}
  .remix-toggle button.on{background:var(--crimson);color:#fff;}
  body.remix-on .remix-toggle button.plan{background:none;color:#aab4c8;}
  body.remix-on .remix-toggle button.remix{background:linear-gradient(90deg,var(--neon),#7ee);color:#061018;box-shadow:0 0 16px rgba(63,224,224,.5);}
  body.remix-on .remix-toggle button.remix.on{background:linear-gradient(90deg,var(--neon),#7ee);color:#061018;}
''', '', 'toggle CSS')

sub1(r'<div class="remix-toggle" role="group".*?</div>\n', '', 'toggle markup', flags=re.S)
sub1(r'  document\.querySelectorAll\(\'\.remix-toggle button\'\).*?\n  \}\);\n', '', 'toggle JS', flags=re.S)
assert 'remix-toggle' not in h, 'remix-toggle references survive'
sub1(r'\s*body\.remix-on \.remix\{max-height:9000px;\}', '', 'leftover remix-on rule')
assert 'remix-on' not in h, 'remix-on references survive'


# ----------------------------------------------------- 4. Book These Now block
swap_str('<p>Two things sell out in August. Everything else can be decided on the ground &mdash; these can\'t. (The Nintendo Museum was the third &mdash; August is already gone; watching for cancellations.)</p>',
         '<p>Universal is bought &mdash; Studio Passes and Express Pass 5 for Tue Aug 11, Nintendo World entry at 12:30. One thing left. '
         '(The Nintendo Museum was the third &mdash; August is already gone; watching for cancellations.)</p>',
         'Book These Now intro')

sub1(r'<a href="https://www\.usj\.co\.jp/web/en/us"[^>]*><b>Universal Express Pass</b>.*?</a>\s*',
     '', 'remove USJ from Book These Now', flags=re.S)
assert 'Universal Express Pass</b>' not in h, 'USJ book-now card survived'


# ------------------------------------------------------------ 5. cross-links
swap_str('Nothing locked, everything changeable &middot; also as tap-through decks: '
         '<a href="tokyo-week-one.html" style="color:var(--crimson);font-weight:700;">Week One</a> &middot; '
         '<a href="kyoto-osaka-week-two.html" style="color:var(--crimson);font-weight:700;">Week Two</a>',
         'Tap-through decks: '
         '<a href="tokyo-week-one.html" style="color:var(--crimson);font-weight:700;">Week One</a> &middot; '
         '<a href="kyoto-osaka-week-two.html" style="color:var(--crimson);font-weight:700;">Week Two</a>'
         '<br><a href="checklist.html" style="display:inline-block;margin-top:14px;padding:9px 18px;border-radius:999px;'
         'background:rgba(212,175,55,.14);border:1px solid rgba(212,175,55,.4);color:var(--gold);'
         'font-weight:800;font-size:13px;letter-spacing:.5px;text-decoration:none;">Prep Checklist &#8599;</a>',
         'footer checklist link')

open(SRC, 'w', encoding='utf-8').write(h)
print(f'index.html: {len(orig)} -> {len(h)} bytes')
print(f'  beats removed: {removed_beats} | remix-why removed: {removed_why} | locked strips: {added_locked}')
