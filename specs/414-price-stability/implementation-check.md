# Feature 414 - implementation check (research/CLAUDE.md, "A finding is checked against the code")

- 0290: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn -i -E 'price.?stab|volatil|price level|inflation' l7r pool (only l7r/diagram/interactive/record/money.py, whose docstring says the borrowing rule waits on diagram#15 and checks none)
- 0291: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn -i -E 'price.?stab|volatil|price level|inflation|fiat|cpi' l7r pool (the same single docstring mention)
