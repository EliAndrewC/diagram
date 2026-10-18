# T06 - a scattered hamlet's seating: measured 2026-10-18

The ranking row (328, E3 kept): `stages.py::_seat_households#a scattered hamlet's seating` - "seat a scattered hamlet's farms in
single file hugged to the field edge, no front-row cap, brick ranks or cloud". 0031's drawing page: "the whole line is hugged to
the field edge in single file ... Draw a scattered settlement on a roomier field, or declare fewer households; do not squeeze the
homesteads to make them fit. This is a rule about fitting the drawing, not a finding about how far apart scattered farms stood."
0031's question page: "A scattered hamlet's farms each stand in the middle of their own fields."

## The pool

No pool hamlet is dispersed today (inashiro, kuwabata, sawada nucleated; kashikawa, mizuguchi linear) - the change reaches no
shipped map. The landing cohort (dev/cohort-log/20261018T105752Z-diagram-backlog-2570331.json): 29 dispersed seeds, all pass.

## HEAD (make hamlet, --no-render)

| seed | households | front row seated | rank rounds |
|---|---|---|---|
| 1 | 17 | 7 | 3 |
| 14 | 20 | 2 | 5 |
| 5 | 12 | 4 | 3 |

## The literal fix, tried (patch saved: t06-single-file-experiment.patch in the session scratchpad)

Every household in the front row, offered along the margin chain at the farmstead's own width (grove included), no ranks, no
exhaustive pass, the rest to the next margin (as a row village):

| seed | farmstead pitch | seats the margin offers | seated | result |
|---|---|---|---|---|
| 1 | 205 ft | 6 | 5 of 17 | SiteRefused |
| 14 | 273 ft | 3 | 1 of 20 | SiteRefused |
| 5 | 273 ft | 4 | 4 of 12 | SiteRefused |

## The room

| seed | margin chains | field's whole outline | single file needs (households x ~240 ft) |
|---|---|---|---|
| 1 | 1,147 ft | 4,619 ft | 4,080 ft |
| 14 | 585 ft | 4,786 ft | 4,800 ft |
| 5 | 1,019 ft | 3,615 ft | 2,880 ft |
