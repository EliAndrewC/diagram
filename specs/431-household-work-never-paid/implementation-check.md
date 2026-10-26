# Feature 431: implementation check (feature 378)

- 0315: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn 'tenement\|used cloth\|bathhouse\|bath fee\|water seller\|washing shop\|polished rice' l7r pool (only wells.py's tenement-court well and the hearth modal's tenement kamado, which draw a well and a hearth and decide no purchase or price)
- 0311: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn 'yabuiri\|days off\|rest day\|working days\|apprentice' l7r pool
- 0183: no code implements it - the change is one pointer sentence to 0315 (consumed by gm-assistant's money skill), and the only code citing 0183, l7r/diagram/overlap/registry.py and taxonomy.py, cites its drawing page, not these findings; searched: grep -rn '0183-shops-and-trades\|shops-and-trades-in-towns' l7r pool
