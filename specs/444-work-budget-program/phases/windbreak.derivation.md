# Derivation - windbreak (feature 444)

## Contract

- Reads: the placed homesteads and the cluster's oriented footprint; each farm's homestead wood, rolled in the register's range (`homestead_wood_ft2`); the belt and the groves already planted by the hinterland; the registry; the water courses (each farm's bank).
- Writes: the copse among the homes (`village_groves`, role `copse`): its clumps on a grid in the gaps between the houses, each clump's crowns; `meta.copse_clumps`.
- Keeps: over the cluster's own oriented footprint, in the gaps between the houses (0036, 0071); a clump within 90 ft of a house (`COPSE_HOUSE_REACH_FT`, a dooryard's reach, 0036); on its house's own bank (0035, a GUESS recorded there); sized by the homestead woods, each farm's share of 6,000 to 28,000 sq ft, the copse filled to what the belt and groves leave (0036); no copse without a belt or a reserved seat; seated after the woods and the ground cover, so the copse and the belt read as two stands; each clump asked before it is drawn (S4).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the cluster's extent 477 by 721 ft and 750 by 1,085 ft (x1.57 and x1.5: 750 by 1,085 ft at 20, 1,178 by 1,628 ft at 40, 1,849 by 2,442 ft at 80); a clump 11 ft in radius on a grid of pitch 11 x root 2, 15.6 ft (the clumps' median nearest neighbor 15.5 ft at 10 and 20); the clumps 223 and 462 (x2.07: 462 at 20, 957 at 40, 1,980 at 80) and their crowns 296 and 624 (x2.11: 624 at 20, 1,317 at 40, 2,779 at 80); the houses' density at most 2.9e-5 a sq ft, so at most 3 houses in 3 by 3 cells of 90 ft; at most 29 things in a 64 ft cell; 1 ft a pixel at the hamlet scale.

## The algorithm

    the sites: the clump grid of pitch 15.6 ft over the cluster's footprint grown by the 90 ft reach
    each site: its houses within 90 ft from its 3 by 3 cells of a 90 ft house index; on its house's bank (1); its clump's
        box against the registry's things in its cells (S4); the farm's wood not yet filled (1); admitted: the clump drawn and
        filed, its crowns written, the farm's share counted down

## Indexes

- house index: cells of 90 ft (the copse's reach), so a site's houses within reach lie in its 3 by 3 cells; densest the houses' density x 9 x 90 squared, 3, from a smallest side of 90 ft
- registry: cells of 64 ft; densest 29 things a cell (measured at 10 and 20, the ceiling taken), from a smallest side of 64 ft against a clump's 22 ft box, in at most 2 by 2 cells

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 4,920 at 20, 10,296 at 40, 22,139 at 80 | the grid's sites, (the cluster's width + 180) / 15.6 by (its length + 180) / 15.6, each rounded up | 80 households |
| the site test (house index and registry cells examined) | per item | 134 | its 9 cells of 90 ft (9) and their at most 3 houses (3), its bank (1), its clump's 2 by 2 cells of 64 ft with their 29 things and the cell (120), its farm's share (1) | every site tested |
| slack | per item | 1 | every factor is a ceiling at its worst case | not applicable |
| the clumps (registry cells written) | over the run | 462 x 5 at 20, 957 x 5 at 40, 1,980 x 5 at 80 | each clump drawn, recorded (1) and filed in at most 4 cells (4) | 80 households |
| the house index (cells written) | once | 20 at 20, 40 at 40, 80 at 80 | each house filed once in its 90 ft cell | 80 households |
| the crowns (written) | over the run | 624 at 20, 1,317 at 40, 2,779 at 80 | each crown written once | 80 households |

So: the sites x 134 x 1, plus the clumps x 5, the house index and the crowns.

## Totals

- at 20: 4920 x 134 x 1 + 462 x 5 + 624 + 20 = 662234
- at 40: 10296 x 134 x 1 + 957 x 5 + 1317 + 40 = 1385806
- at 80: 22139 x 134 x 1 + 1980 x 5 + 2779 + 80 = 2979385

## Cheaper algorithms considered

- sweep: used - the grid's sites are taken in rows over the footprint, once each
- grid or spatial index: used - the house index for the reach and the registry for each clump
- priority queue: not used - the sites are taken in grid order; the farms' shares bound the fill
- incremental update: used - each clump is filed as it is drawn, and its farm's share counted down
- memoizing what a scan does not change: used - the houses and the belt stand through the stage; the 90 ft house index is built once, each house filed
