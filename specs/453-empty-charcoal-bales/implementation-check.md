# Feature 453 - implementation check

- 0335: no code implements it - consumed by gm-assistant's money skill; searched: grep -rnIi -E 'empty bale|sumidawara|akidawara|bale.{0,40}(price|cost|sen\b|mon\b)|(price|cost).{0,40}\bbales?\b' l7r pool rust (one hit, a source key named edo-tokyo-sumidawara on the charcoal-bales modal's Sources line; nothing decides a bale's price)
- 0279: no code implements it - consumed by gm-assistant's money skill; searched: grep -rnIi -E 'empty bale|sumidawara|akidawara|bale.{0,40}(price|cost|sen\b|mon\b)|(price|cost).{0,40}\bbales?\b' l7r pool rust (one pointer line added, no finding changed)
