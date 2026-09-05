# The GM's request, verbatim

2026-09-05, session "Diagram html", after feature 186 (no dotted underlines on links) landed on main:

> I'm looking at file:///home/eli/l7r/diagram/.claude/skills/diagram/pool/hamlets/inashiro/inashiro.html and still see the dotted lines.  Why is the fix not there?

## What the investigation found

The mirror's HEAD carried the fix (`6bdc67d5`), but `pool/hamlets/inashiro/inashiro.html` in the mirror
was last written at 17:35:25, before the landing, and still contained three `underline dotted` rules.
render-sync had reported *"5 regenerated, 5 cached (fresh)"* and Inashiro was among the cached:
`pipeline/render_cache.engine_fingerprint()` hashes only `.py` files (line 91), and
`pipeline/gencache.engine_files()` the same (line 158), so a landing whose engine change is only
`interactive/assets/page.css` leaves every render's fingerprint unchanged and every page stale. Feature 181
closed the same gap in the GATE key; the RENDER key had it too.
