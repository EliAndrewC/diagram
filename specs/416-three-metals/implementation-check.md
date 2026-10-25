# Feature 416 - implementation check

- 0295: no code implements it - consumed by gm-assistant's money skill (`l7r/diagram/interactive/record/money.py` only shows gm-assistant's own conversion table on hover and computes no rate between the metals); searched: grep -rn -i -E 'monme|kanmon|money.?changer|ryogae|zeni|copper rate' l7r pool
- 0296: no code implements it - consumed by gm-assistant's money skill (`l7r/diagram/interactive/record/money.py` computes no rate between silver and copper); searched: grep -rn -i -E 'tael|cash a tael|paper money|silver dear|copper cash' l7r pool
