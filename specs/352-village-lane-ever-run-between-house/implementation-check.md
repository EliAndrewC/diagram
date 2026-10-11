# Implementation check - feature 352 (feature 378)

`make impl-check F=352` lists the claims citing 0036's findings page, each with its `impl-drift` verdict. This file
records the part of the question that no claim can reach (plan D4).

- 0036, "Did a lane ever run between a farmhouse and its grove?": no page read shows one; where an account places the
  way, it runs outside the grove or through a gap in it to the house. The code keeps every lane off a household's
  reserved copse seats (`overlap/reserved.py` `Reservations.conflicts`, `homesteads/region.py` `SeatRegion.sync`,
  `homesteads/household_ways.py` `seat_walls`/`seated_parts`, `ways/web.py` `stage_web`, `rolling/gap_ways.py`,
  `rolling/passage.py` `walk_clear`) and seats them within 90 ft of the house inside its footprint
  (`homesteads/growth.py` `footprint`, `consts.py` `COPSE_HOUSE_REACH_FT`). **Implemented nowhere: a lane kept out of the
  open ground BETWEEN a house and its own seats.** Each seat's lane buffer and the house's own parts are kept clear, but
  the ground between them, out of every buffer, is open to a lane; that no lane runs there follows on our maps only from
  the seats standing close by the house, not from a rule. Searched: the FR-003 claim search
  (`(wood|woodlot|copse)s?'?[ -]seats?|seat off a lane|lane gap` over `dev/claims-index.json` and the `Research:` claim
  text), `grep -rln wood_share l7r/diagram/hamletgen/ways l7r/diagram/settlement/rolling` (only `fit.py` and `lot.py`,
  which seat and fit the share, not a way), and
  `grep -rn "between.*house.*seat|house.*and its.*seats|convex_hull"` over `hamletgen/ways`, `hamletgen/homesteads` and
  `settlement/homestead_parts` (nothing that bars a way from that ground). Not built, by the GM's scope (FR-004: the
  research and the tagging only, no map change).
