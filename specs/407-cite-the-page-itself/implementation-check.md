# Feature 407: the findings no code implements

- 0275: no code implements it - a price, consumed by gm-assistant's money skill (record/money.py only presents gm-assistant's vendored conversion table and computes no price); searched: grep -rniE 'craftsman|carpenter|laborer|wage' l7r pool --include=*.py, then each hit for a price word (monme|ryo|mon|price|wage|tael|cost) within 80 characters - the only such hits are placement or compute costs and money.py's display (2026-10-26, feature 432's audit of the GM-review boxes)
