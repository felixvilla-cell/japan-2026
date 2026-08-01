#!/usr/bin/env python3
"""Swap Street Kart Asakusa (needs an IDP, unobtainable now) for City Circuit
Tokyo Bay (no licence, no IDP) and move it from Day 3 to Day 4 Wed Aug 5.

Felix, 2026-08-01: the IDP is issued in the US only, so Street Kart died the
moment the trip started. City Circuit Tokyo Bay in Aomi/Odaiba needs no licence
and no permit, which makes it the one real swap. It lands on Day 4 -- the day
that lost its anchor when teamLab was cut, and the same bay area teamLab
Planets sat in.

Exact-match replacements with assertions, per the convention for this file
(the original generator for index.html is gone).
"""
import re
import sys

CLONE = "/Users/felixvilla/japan-2026-work"
MIRROR = "/Users/felixvilla/Projects/felix-assistant/reports/japan-trip"

# ---------------------------------------------------------------- the blocks
STREET_KART = (
    '<li><button class="lnk" type="button" aria-expanded="false"><span class="txt">'
    '<b>Street Kart Asakusa (real-road go-karting)</b> <span class="rblurb">Costumed '
    "go-kart tour on public streets past Senso-ji and the river; dad vs son, GoPro "
    "footage included. The single most 'I can't believe this is legal' thing he'll do."
    '</span></span><span class="go">+</span></button><div class="panel"><div class="inner">'
    '<div class="pgal"><figure><img data-src="img/r/d2-0-1.jpg" alt="" decoding="async">'
    '</figure><figure><img data-src="img/r/d2-0-2.jpg" alt="" decoding="async"></figure>'
    '</div><p class="ralt-desc">A guided go-kart tour on actual public streets, cruising '
    "past Senso-ji temple and along the Sumida River in a costume of your choice. Dad "
    "races son through real Tokyo traffic while a guide leads and GoPro footage gets "
    "captured for you. It is the single most unbelievable I-cannot-believe-this-is-legal "
    'thing on the trip.</p><div class="ptips"><h4>Quick facts</h4><ul>'
    "<li>Around 8,000-10,000 yen per person</li><li>Valid IDP driving permit required</li>"
    "<li>Book 1-2 hour tour ahead</li><li>Costumes provided free</li></ul></div></div>"
    "</div></li>"
)

CITY_CIRCUIT = (
    '<li><button class="lnk" type="button" aria-expanded="false"><span class="txt">'
    "<b>City Circuit Tokyo Bay (karting, no permit needed)</b> "
    '<span class="rblurb">A real outdoor circuit on the bay: 50km/h single-seaters, no '
    "licence and no age limit. Dad vs son, on a timed grid, with the bay behind you."
    '</span></span><span class="go">+</span></button>'
    '<div class="panel"><div class="inner"><div class="pgal">'
    '<figure><img data-src="img/r/kart-1.jpg" alt="" decoding="async"></figure>'
    '<figure><img data-src="img/r/kart-2.jpg" alt="" decoding="async"></figure></div>'
    '<p class="ralt-desc">The only kart circuit inside Tokyo&rsquo;s 23 wards, out on the '
    "Odaiba waterfront. Single-seater electric karts that top out at 50km/h on a proper "
    "outdoor track with real barriers, timing and a grid &mdash; not a fairground ride. "
    "No driving licence, no international permit and no age limit: if you clear 150cm and "
    "can reach the pedals, you drive. Helmet, gloves and suit are all provided, and there "
    "is a free shower room afterwards if you pack a towel."
    '</p><div class="ptips"><h4>Quick facts</h4><ul>'
    "<li>20 min slot 6,000 yen each &mdash; 17 min actual driving</li>"
    "<li>No licence, no IDP, no age limit &mdash; 150cm minimum</li>"
    "<li>Wednesday 12:00&ndash;20:00, last admission 19:15</li>"
    "<li>Aomi Station 3 min walk; walk-in OK, or book online</li>"
    "</ul></div></div></div></li>"
)

# ------------------------------------------------------- index.html edits
IDX_EDITS = [
    # 1. Day 4 date tag
    ('<div class="tag">Eva Store + Sunshine City &middot; Wed Aug 5</div>',
     '<div class="tag">Ikebukuro + Odaiba karting &middot; Wed Aug 5</div>'),
    # 2. Day 4 remix heading
    ("<h3>Eva Store + Sunshine City</h3>",
     "<h3>Ikebukuro + Odaiba karting</h3>"),
    # 3. Day 4 intro -- it is two districts now, and one of them has a kart track
    ("<p>One district, all day, nothing booked. The official Evangelion store, the "
     "flagship anime shop, and a whole tower of stuff stacked above them &mdash; then "
     "bail out whenever you want, because tomorrow morning is the bullet train.</p>",
     "<p>Two districts and still nothing locked down. The official Evangelion store, the "
     "flagship anime shop, and a whole tower of stuff stacked above them &mdash; then out "
     "to the bay to put him in an actual kart, because tomorrow morning is the bullet "
     "train.</p>"),
]

# ------------------------------------------------- tokyo-week-one.html edits
DECK_EDITS = [
    ('<div class="tag">Eva Store + Sunshine City</div>',
     '<div class="tag">Ikebukuro + Odaiba karting</div>'),
    ("<p>One district, all day, nothing booked &mdash; the loose day before the bullet "
     "train south.</p>",
     "<p>Ikebukuro all morning, then a real kart circuit out on the bay &mdash; the loose "
     "day before the bullet train south.</p>"),
]

ANCHOR_BAIL = "<li><button class=\"lnk\" type=\"button\" aria-expanded=\"false\"><span class=\"txt\"><b>Bail out early"


def day_slice(h, start_text, end_text):
    i = h.find(start_text)
    j = h.find(end_text, i)
    assert i > 0 and j > i, f"could not slice {start_text!r}"
    return i, j


def apply_index(path):
    h = open(path, encoding="utf-8").read()
    orig = h

    # --- pre-flight assertions -------------------------------------------
    i3, j3 = day_slice(h, "Old Tokyo, Then Arcade Heaven", "Ikebukuro, Off the Clock")
    i4, j4 = day_slice(h, "Ikebukuro, Off the Clock", "South on the Bullet Train")
    n3, n4 = h[i3:j3].count('class="lnk"'), h[i4:j4].count('class="lnk"')
    assert (n3, n4) == (9, 5), f"expected 9 lnk on day3 / 5 on day4, got {n3}/{n4}"
    assert h.count(STREET_KART) == 1, f"Street Kart block not found verbatim"
    assert h.count(CITY_CIRCUIT) == 0, "City Circuit already present"
    assert h.count(ANCHOR_BAIL) == 1, "bail-out anchor not unique"

    # --- 1. remove Street Kart from Day 3 --------------------------------
    h = h.replace(STREET_KART, "", 1)

    # --- 2. insert City Circuit into Day 4, ahead of the bail-out option --
    k = h.find(ANCHOR_BAIL)
    assert k > 0
    h = h[:k] + CITY_CIRCUIT + h[k:]

    # --- 3. copy edits ----------------------------------------------------
    for old, new in IDX_EDITS:
        assert h.count(old) == 1, f"index: expected 1 match for {old[:60]!r}, got {h.count(old)}"
        h = h.replace(old, new, 1)

    # --- post-flight assertions ------------------------------------------
    assert "Street Kart" not in h, "Street Kart still present"
    assert "Valid IDP driving permit required" not in h, "IDP line survived"
    assert h.count(CITY_CIRCUIT) == 1, "City Circuit not inserted exactly once"
    i3, j3 = day_slice(h, "Old Tokyo, Then Arcade Heaven", "Ikebukuro, Off the Clock")
    i4, j4 = day_slice(h, "Ikebukuro, Off the Clock", "South on the Bullet Train")
    n3, n4 = h[i3:j3].count('class="lnk"'), h[i4:j4].count('class="lnk"')
    assert (n3, n4) == (8, 6), f"after: expected 8/6 lnk, got {n3}/{n4}"
    # the new option must sit inside Day 4, not leak into Day 3 or Day 5
    assert CITY_CIRCUIT in h[i4:j4], "City Circuit landed outside Day 4"
    for tag in ("li", "ul", "div", "figure", "button"):
        a, b = orig.count(f"<{tag}"), h.count(f"<{tag}")
        ca, cb = orig.count(f"</{tag}>"), h.count(f"</{tag}>")
        assert b - cb == a - ca, f"{tag} balance drifted: {a}/{ca} -> {b}/{cb}"
    for img in ("img/r/kart-1.jpg", "img/r/kart-2.jpg"):
        assert img in h, f"missing {img}"
    assert "img/r/d2-0-1.jpg" not in h and "img/r/d2-0-2.jpg" not in h, "old kart imgs linger"

    open(path, "w", encoding="utf-8").write(h)
    return len(orig), len(h)


def apply_deck(path):
    h = open(path, encoding="utf-8").read()
    orig = h
    for old, new in DECK_EDITS:
        assert h.count(old) == 1, f"deck: expected 1 match for {old[:60]!r}, got {h.count(old)}"
        h = h.replace(old, new, 1)
    open(path, "w", encoding="utf-8").write(h)
    return len(orig), len(h)


if __name__ == "__main__":
    for tree in (CLONE, MIRROR):
        a, b = apply_index(f"{tree}/index.html")
        print(f"  index.html        {a} -> {b}  ({tree})")
        a, b = apply_deck(f"{tree}/tokyo-week-one.html")
        print(f"  tokyo-week-one    {a} -> {b}")
    print("all assertions passed")
