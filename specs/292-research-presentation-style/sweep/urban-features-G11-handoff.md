# 292 sweep urban-features G11 - handoff (session 1: write)

## Stable yards and watering troughs

- SECTION=urban-features/stable-yards-and-watering-troughs
- RENDERING=rendering/urban-features/how-our-maps-draw-stable-yards-and-their-troughs
- OLD=research/urban-features/080-stable-yards---beaten-earth-hitching-rails-and-watering-by-relay.html research/urban-features/082-how-does-a-stable-yard-water-its-animals---troughs-beside-a-well-filled-by-relay.html research/urban-features/084-why-are-two-or-three-troughs-enough-for-several-dozen-oxen.html
- MODALS=stables
- BASE=02bd38e9d

Nothing was left out: the claims file's open line for feature 280 U1 check-a on 082 (2026-09-28) is stale, since that check landed as 309fffa09. 084's note caravanserai-enwiki-3 quoted the same passage, with the same gloss, as 082's caravanserai-enwiki-2 and is folded into it. Every other note key is cited, and the REMOVED comment names what was cut. The two old-form absence notes are converted: 080's is re-keyed `stable-yards-and-watering-troughs`, and `stable-trough-absence` keeps its key. The note qimin-yaoshu-yangma's gloss now gives 迥地 its (romaji, "meaning") form, because the style prepass required it. The towns 350 link now points at the rendering section, because it cited what the maps draw. The code comments in stable_yard.py, _yardctx.py and tests/settlement/test_civic_grounds.py now name the new titles. The Stables modal (compound_kinds/household.py) was the only modal whose Entry named the old section: its Entry names 'Stable yards and watering troughs' and adds the rendering title. The fixture has no stables entry. towns/340 and towns/350 still overlap this topic, and towns/350 is left for the towns planner to fold.
