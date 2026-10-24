# Feature 412: the findings no code implements

- 0250: no code implements it - consumed by gm-assistant's money skill; searched: grep -rniE 'unskilled|day wage|hiyatoi|日雇' l7r pool
- 0265: no code implements it - consumed by gm-assistant's money skill; searched: grep -rniE 'tenement|back-alley|tanachin|rent a room' l7r pool (hits only the street-width and well claims of 0136 and a well docstring, none a rent)
- 0273: no code implements it - consumed by gm-assistant's money skill; searched: grep -rniE 'salt price|price of salt|monme a koku|kg of salt' l7r pool
- 0279: no code implements it - consumed by gm-assistant's money skill; searched: grep -rniE 'firewood|charcoal price|price of charcoal|10 kan' l7r pool (hits only the wood shed's placement claims of 0043, none a price)
- 0286: no code implements it - consumed by gm-assistant's money skill (record/money.py only presents gm-assistant's vendored conversion table and computes no price); searched: grep -rn -i -E 'chogin|basket|mugi|Kumon|Iwahashi|Kimura|monme.*koku' l7r pool
- 0287: no code implements it - consumed by gm-assistant's money skill (record/money.py converts only by gm-assistant's vendored table); searched: grep -rn -i -E 'chogin|koban|fineness|pure silver|grams of silver|nanryo|ichibu' l7r pool
- 0288: no code implements it - consumed by gm-assistant's money skill (record/money.py only presents gm-assistant's vendored conversion table and computes no price); searched: grep -rn -i -E 'tael|copper cash|basket|Songjiang|Canton|picul|catty' l7r pool
- 0289: no code implements it - consumed by gm-assistant's money skill (record/money.py converts only by gm-assistant's vendored table); searched: grep -rn -i -E 'tael|tiao|jingqian|kuping|cash a tael|grams of silver' l7r pool
