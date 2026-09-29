"""Feature 280's review measurements, read from the pool maps' drawn artifacts (run from .claude/skills/diagram).

Each figure is written to measurements.json beside this file as a record answering the verdict it verifies:
crowns centered inside a bamboo stand (the drawn `tree_crowns` against each drawn stand's outline), the bath rooms by the
wall they abut (the drawn fixture rect against its house's front wall), the fry ponds' drawn fill, and the notes' subject
paragraph."""

import json
import math
import re
import sys

POOL = "pool/hamlets"
TODAY = "2026-09-29"
SRC = "specs/280-modern-only-sweep/measure.py (run from .claude/skills/diagram)"


def inside(p, poly):
    x, y = p
    c = False
    for k in range(len(poly)):
        a, b = poly[k], poly[k - 1]
        if (a[1] > y) != (b[1] > y) and x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]:
            c = not c
    return c


def manifest(n):
    return json.load(open(f"{POOL}/{n}/{n}.json"))


def crowns_in_bamboo(n):
    m = manifest(n)
    cr = m.get("tree_crowns") or []
    crowns = [cr[k : k + 3] for k in range(0, len(cr), 3)] if cr and not isinstance(cr[0], list) else cr
    stands = m.get("bamboo_stands") or []
    return sum(1 for b in stands for c in crowns if inside((c[0], c[1]), b["poly"])), len(stands), len(crowns)


def baths_at_front_wall(n):
    """Bath rooms whose center stands in front of the house's front wall (house frame +y, `bath_room_seats`)."""
    m = manifest(n)
    houses = {(round(h["x"], 1), round(h["y"], 1)): h for h in m["houses"]}
    front = labeled_front = total = 0
    for f in m["farm_fixtures"]:
        if f["kind"] != "bath":
            continue
        total += 1
        h = houses.get((round(f["of"][0], 1), round(f["of"][1], 1)))
        if h is None:
            continue
        r = math.radians(float(h.get("rot", 0.0)))
        dx, dy = f["x"] - h["x"], f["y"] - h["y"]
        ly = -dx * math.sin(r) + dy * math.cos(r)
        at_front = ly > h["h"] / 2
        front += at_front
        labeled_front += f.get("seat") == "main_door"
    return front, labeled_front, total


def persimmons_in_bamboo(n):
    m = manifest(n)
    return sum(1 for b in m.get("bamboo_stands") or [] for p in m.get("persimmons") or [] if inside((p["x"], p["y"]), b["poly"]))


def fry_fills(n):
    svg = open(f"{POOL}/{n}/{n}.svg").read()
    return len(re.findall(r'fill="#9FA898"', svg)), sum(1 for p in manifest(n)["dikeponds"] if p.get("kind") == "fry")


def rec(key, **kw):
    kw.setdefault("measured", TODAY)
    kw.setdefault("source", SRC)
    return key, kw


def main(answers):
    out = {}
    for n in ("inashiro", "kashikawa", "mizuguchi", "sawada", "kuwabata"):
        c, s, t = crowns_in_bamboo(n)
        out.update([rec(f"f280-{n}-crowns-in-bamboo", value=c, unit="crowns centered in a bamboo stand", subject=n, stands=s, crowns=t,
                        quantity="drawn crowns (manifest tree_crowns, the drawn ink) whose center lies inside a drawn bamboo stand's outline",
                        method="point-in-polygon of every tree_crowns center against every bamboo_stands poly")])
        out.update([rec(f"f280-{n}-persimmons-in-bamboo", value=persimmons_in_bamboo(n), unit="yard persimmons centered in a bamboo stand", subject=n,
                        quantity="drawn yard persimmons (manifest persimmons, whose ink is in tree_crowns) centered inside a drawn bamboo stand",
                        method="point-in-polygon of every persimmon center against every bamboo_stands poly")])
        f, lf, tot = baths_at_front_wall(n)
        out.update([rec(f"f280-{n}-bath-front", value=lf - f, unit="baths recorded main_door but not drawn before the front wall", subject=n,
                        drawn_front=f, recorded_main_door=lf, baths=tot,
                        quantity="bath rooms whose record says main_door against those whose drawn center stands before the front wall",
                        method="each bath fixture's center in its house's frame (house rot), ly > h/2 is the front wall")])
    fr, fp = fry_fills("kuwabata")
    out.update([rec("f280-kuwabata-fry-tint", value=fr, unit="ponds drawn in the turbid fry fill #9FA898", subject="kuwabata", fry_ponds=fp,
                    quantity="drawn pond paths filled #9FA898 in kuwabata.svg against the manifest's fry ponds",
                    method="count of fill=\"#9FA898\" in the svg")])
    notes = open(f"{POOL}/inashiro/inashiro.notes.md").read().split("**Kanji triangle**")[0]
    out.update([rec("f280-inashiro-subject-burial", value=int("own_ground" in notes or "burial ground of its own" in notes), unit="stale own-ground claims",
                    subject="inashiro", quantity="the notes' subject paragraph claiming a burial ground of its own", method="text search above the kanji triangle")])
    for k, v in out.items():
        a = answers.get(v["subject"])
        if a:
            v["answers"] = a
    json.dump(out, open("../../../specs/280-modern-only-sweep/measurements.json", "w"), indent=1, ensure_ascii=False)
    for k, v in out.items():
        print(k, v["value"], {x: v[x] for x in ("stands", "drawn_front", "recorded_main_door", "baths", "fry_ponds") if x in v})


if __name__ == "__main__":
    main(json.loads(sys.argv[1]) if len(sys.argv) > 1 else {})
