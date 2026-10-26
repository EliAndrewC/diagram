# Feature 431: implementation check (feature 378)

- 0312: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn -i -E 'yonabe|araihari|household.?work|unpaid|man-day|night work' l7r pool
- 0313: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn -i -E 'spinning|weaving|tan of cloth|bolt of cloth|ramie|reel' l7r pool
- 0314: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn -i -E 'warp-weighted|weaving speed|hand-spun' l7r pool
- 0209: no code implements it - only a pointer to 0313 was added, and no code claim cites 0209; searched: grep -rn -i -E 'spinning|weaving' l7r pool
- 0306: no code implements it - only a pointer to 0313 was added; searched: grep -rn -i -E 'spinning|weaving' l7r pool
- 0315: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn 'tenement\|used cloth\|bathhouse\|bath fee\|water seller\|washing shop\|polished rice' l7r pool (only wells.py's tenement-court well and the hearth modal's tenement kamado, which draw a well and a hearth and decide no purchase or price)
- 0311: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn 'yabuiri\|days off\|rest day\|working days\|apprentice' l7r pool
- 0183: no code implements it - the change is one pointer sentence to 0315 (consumed by gm-assistant's money skill), and the only code citing 0183, l7r/diagram/overlap/registry.py and taxonomy.py, cites its drawing page, not these findings; searched: grep -rn '0183-shops-and-trades\|shops-and-trades-in-towns' l7r pool
- 0316: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn -i 'proverb\|unrecorded\|onna daigaku\|0316-why' l7r pool (only the Onna daigaku glossary term's files and binary caches; no code)
- 0317: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn -i 'proverb\|rise before dawn\|early rising\|0317-is-there' l7r pool (only binary caches; no code)
