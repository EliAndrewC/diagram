"""The office and its works - the hall and the bench, the clerks, the stores, the cell, the watch, the tally.

Each class's DOCSTRING is its explanation - `What:`, `Why:`, `Note:`, optional `Caveat:`, then the data tags -
parsed by `..classes._base.parse_explanation` (feature 189). Every kind is written FROM the existing record
(feature 262, FR-005): the sections its `Entry:` names, and the `buildings/types.json` program item folded into
it where there is one - the item's class and why are carried here, not re-decided: a size band the item calls a
guess is the kind's caveat (office hall, barracks), and a presence-only item's class is the kind's label (clerks'
room, gatehouse). The measurement behind each label is `specs/262-interactive-magistracy-pages/coverage.md`.
"""

from __future__ import annotations

from ..classes import Kind


class OfficeHall(Kind):
    """
    What: The working heart of the compound: a long hall backing onto the internal wall, its front band the
    magistrate's dais over the hearing court, and behind a screen its working rooms - the day office and the
    official study, each its own feature.

    Why: At Takayama, the surviving intendant's office, the office wing - reception rooms, day office and
    official study - is the dominant public building, and the hearing court is one room of that block. Daily
    paperwork is most of a magistrate's job, and the residence's private study is on the wrong side of the
    line between state and home for it, so the hall is deep, and it may be the largest building in the
    compound, being the institution's working core rather than a dwelling. A wooden hall could burn, and
    many did (the Sado magistracy was rebuilt five times, though Takayama's never burned), which is why the
    documents and the tax grain are kept in storehouses of their own.

    Note: The hall's form and its place follow the record; that it may out-size the residence is this
    project's reading, since no readable source ranks a compound's footprints. Its size, about 80 to 150 ft
    long and 20 to 45 ft deep, is a guess: it is the plan vocabulary's working block, with no measured
    office wing of a jin'ya behind it.

    Caveat: That it may out-size the residence is this project's reading, since no readable source ranks a
    compound's footprints. Its size, about 80 to 150 ft long and 20 to 45 ft deep, is a guess: it is the
    plan vocabulary's working block, with no measured office wing of a jin'ya behind it.

    Name: office hall
    Covers: the office hall's block, its outline and its front band
    Label: accurate
    Sources: takayama-jinya-jawiki, takayama-jinya-city, sado-bugyosho-fires
    Entry: research/buildings.html - 'The courtroom is a room of the office hall, not a freestanding stage', 'Administrative culture is JAPAN-first for compound interiors', 'The compound has a size HIERARCHY, not just individual sizes', 'Fire discipline: halls burn, kura endure'
    """

    key = "office hall"


class MagistratesDais(Kind):
    """
    What: The raised tatami band along the office hall's front, overlooking the hearing court: the
    magistrate's seat at its center, between the clerks' seats.

    Why: A raised hall over kneeling litigants is common to both traditions this setting draws on, Japanese
    and Chinese. The dais is not a pavilion of its own but the front of a deeper office hall, so the
    magistrate hears cases in the same building where the day's paperwork is done.

    Note: The raised seat over the court, and its place at the front of the office hall, follow the record.

    Name: magistrate's dais
    Covers: the dais band on the office hall's court face, and its label
    Label: accurate
    Sources: takayama-jinya-jawiki, takayama-jinya-city, neixiang-yamen-zhwiki
    Entry: research/buildings.html - 'The courtroom is a room of the office hall, not a freestanding stage', 'Administrative culture is JAPAN-first for compound interiors'
    """

    key = "magistrate's dais"


class ClerksRoom(Kind):
    """
    What: The workroom of the county's few hired clerks, where the tax rolls and case papers are copied and
    kept in order: a room of the office hall on some plans, a small building of its own beside it on others.
    It is a place of work, never lodging.

    Why: In both traditions the paperwork was run by locally hired commoners under a tiny elite staff; in
    Japan the tedai were drawn from the peasants and townsmen who knew the district. Scaled to a county of
    this setting, that is three or four clerks, scribes by caste (heimen), who live in town and come in to
    the manor each day - and who, as permanent locals, are the office's memory under one magistrate after
    another.

    Note: the record finds the clerks but says nothing of their room, and the program's workroom of about 28
    by 18 ft for three or four clerks is a guess with no measured example behind it, whether it is drawn as a
    room of the office hall or as a building of its own.

    Name: clerks' room
    Covers: the clerks' room inside the office hall, its floor and its label, or the clerks' own small building beside it
    Label: guess
    Sources: tedai-jawiki, xuli-zhwiki
    Entry: research/buildings.html - 'Clerks are few, local, and heimen'
    """

    key = "clerks' room"


class TaxArchive(Kind):
    """
    What: A sealed storehouse (kura) of thick white-plastered earth, holding the county's
    ledgers - its tax base on paper - and serving as the strongroom for the coin and valuables the office
    holds.

    Why: Administrative halls were ordinary wooden buildings and burned again and again - the Sado magistracy
    burned and was rebuilt five times - while only thick-walled earthen kura were fireproof, their walls often
    a foot or more thick. That is why the documents got a storehouse of their own instead of a room in the
    hall. The fire-water tubs stand at the wooden buildings and not here: this is the one building made not
    to burn.

    Note: The fireproof document store follows the record, drawn as a sealed kura of about 32 to 36 ft, the
    plan vocabulary's size for a records store that doubles as the strongroom. An archive in the Chinese
    county office is not confirmed by any page read.

    Name: tax archive
    Covers: the plastered archive kura and its label
    Label: accurate
    Sources: sado-bugyosho-fires, dozo-jawiki, tfd-hongou-fire-history
    Entry: research/buildings.html - 'Fire discipline: halls burn, kura endure', 'Fire-water is distributed to the halls, not the kura', 'Administrative culture is JAPAN-first for compound interiors'; research/cities/fabric.html - 'How did a dense wooden city watch for fire?'
    """

    key = "tax archive"


class Granary(Kind):
    """
    What: A raised storehouse with slatted vents, where the tax paid in grain waits
    on its way to the governor: rice in straw bales above all, with a share of other grain beside it.

    Why: Tax rice flowed from the village granaries through the magistrate's compound toward central stores,
    so the office kura holds grain in transit plus a local reserve, and a county seat's granary stands inside
    the compound rather than in the town. Where water gives a county a way out, the grain moves on; a remote
    county, where transport costs more, keeps a row of kura instead. The lord's kura held the paddy tax as brown rice in straw
    bales, with a corner of unhulled rice kept against famine.

    Note: The kura, its rice and its place inside the compound follow the record, but the famine corner of
    unhulled rice is a simplification: Edo kept that reserve in separate community granaries, and one granary
    is drawn instead of two. The staging - tax rice passing through the compound and held there in transit beside a local reserve - is this map's own reading, which no source states; drawn at about
    43 to 50 by 25 to 27 ft and checked against real kura sizes. That more of the dry-field tax arrives in
    kind - soybeans and barley in bales beside the rice - than it did in Edo Japan is this setting's own
    economics: Rokugan is rich in goods and poor in coin.

    Caveat: The staging - tax rice held in the compound in transit beside a local reserve - is this map's own
    reading, which no source states, and the famine corner of unhulled rice stands in for Edo's separate
    community granaries. That more of the dry-field tax arrives in kind - soybeans and barley in bales beside the rice -
    than it did in Edo Japan is this setting's own economics: Rokugan is rich in goods and poor in coin.

    Name: granary
    Covers: the vented granary kura and its label
    Label: accurate
    Sources: takayama-jinya-city, takayama-jinya-jawiki, nishimawari-koro-jawiki, gokura-jawiki, hatakata-men-jawiki, kuramai-jawiki, kakoimai-jawiki
    Entry: research/buildings.html - 'The granary is a staging node, not the terminal store', 'The granary holds grain, not just rice'; research/towns.html - 'Why is the magistrate's manor drawn as a plain walled box?'
    """

    key = "granary"


class Cell(Kind):
    """
    What: A small cage-like holding room with barred sides, where one or two of the accused wait for their
    case to be heard and judged. It is a place of waiting, not of punishment.

    Why: Edo jails held the accused pending judgment; the sentences were exile, flogging, fines or death -
    not, in the ordinary case, time in prison - and light offenders were sent home to their villages.
    Purpose-built prisons were separate compounds in the great cities. So a county magistracy keeps a cell or
    two for remand and no prison block - and in Rokugan, where torture is unusual, no room built for
    interrogation either.

    Note: Small remand cells follow the record, a real remand cage running about 10 by 12 ft. That a cell may
    stand anywhere in the compound is this setting's own: Chinese regulation put the county jail in the
    southwest corner, and Rokugan keeps no such rule.

    Caveat: That a cell may stand anywhere in the compound is this setting's own: Chinese regulation put the
    county jail in the southwest corner, and Rokugan keeps no such rule.

    Name: cell
    Covers: the barred holding cell and its label
    Label: accurate
    Sources: tenmacho-jawiki, chuo-royashiki, neixiang-yamen-zhwiki, henan-neixiang, takayama-jinya-city
    Entry: research/buildings.html - 'Cells are remand, not punishment', 'No interrogation room'
    """

    key = "cell"


class Gatehouse(Kind):
    """
    What: A small guard post just inside the main gate and beside it - never across the opening - where the
    watch keeps the door.

    Why: The main gate is the compound's one door for visitors on business, and a guard lodged beside it
    controls it without closing the way; standing inside the wall and to one side, the post leaves the
    passage clear into the forecourt.

    Note: The program classes the gatehouse as accurate, a gate guard's post beside the opening of about 40 by
    14 ft; the record holds no entry on a compound's gatehouse, and the size is the program's own.

    Caveat: the record holds no entry on a compound's gatehouse, and the size is the program's own.

    Name: gatehouse
    Covers: the guard post beside the main gate and its label
    Label: accurate
    Sources: not recorded
    Entry: research/buildings.html (no dedicated entry - recorded as silent)
    """

    key = "gatehouse"


class Barracks(Kind):
    """
    What: A plain long building divided into bunk rooms, where the compound's working platoon and its duty
    watch lodge.

    Why: Rural intendants' offices housed their staff on the grounds; it was
    the great city magistrate's offices that lodged their constables in a district of their own, keeping only the
    magistrate's household inside. A county posting's staff is a working platoon, mostly without dependents,
    so by default it lives on the grounds. The barracks outranks the stable in size: a stable for a few
    horses never out-foots the watch's quarters.

    Note: On-grounds housing for the staff follows the record. The building's size, about 20 to 70 ft by 10
    to 40 ft, is a guess taken from the plan vocabulary's range, and how many live in it follows how the
    posting houses its staff.

    Caveat: The building's size, about 20 to 70 ft by 10 to 40 ft, is a guess taken from the plan vocabulary's
    range, and how many live in it follows how the posting houses its staff.

    Name: barracks
    Covers: the barracks building and its label
    Label: accurate
    Sources: hatchobori-jawiki, takayama-jinya-jawiki, jinya-jawiki
    Entry: research/buildings.html - 'Staff housing spans a real spectrum', 'The compound has a size HIERARCHY, not just individual sizes'
    """

    key = "barracks"


class BenchNoticeBoard(Kind):
    """
    What: The bench's own board, just outside the main gate, where the court posts what it produces -
    verdicts, edicts and bounties - for those who come to it.

    Why: Every Edo town and village kept an official edict board, the kosatsuba, and set it where traffic
    passed: at checkpoints and bridgeheads, at the entrance or center of a settlement, and before the gate of
    the village officials' houses. A magistracy's board stands at its own gate, on the way everyone who has
    business with the court must come.

    Note: The board and its roadside seat follow the record, which sets it before the gate of village
    officials' houses but at no government office; that every town and village kept one is a reading of the
    sources, not their words. That the bench keeps a board of its own, apart from the kosatsuba where the town
    posts the state's standing law, is this project's own division; the record finds only the settlement's
    board.

    Caveat: That the bench keeps a board of its own, apart from the kosatsuba where the town posts the state's
    standing law, is this project's own division; the record finds only the settlement's board.

    Name: notice board
    Covers: the board outside the main gate and its label
    Label: accurate
    Sources: ogose-kosatsuba, kosatsu-jawiki, adachi-kosatsu, kosatsu-enwiki, shoya-jawiki
    Entry: research/urban-features.html - 'The notice board (kosatsuba) - siting is a TRAFFIC decision'
    """

    key = "notice board"


class TallyOffice(Kind):
    """
    What: A small office on the route goods take through the compound, where they are counted or weighed, the
    seal is set and the tally written: the record of goods the office supervises but does not own.

    Why: The magistracy's hold on moving goods is documentary. Tax rice moved on hired commoner boats under the
    office's seals - the office owned no hulls - and a charcoal store was a supervised, tallied depot, its
    goods sealed there and never owned. So the post that writes the tally stands where the goods pass,
    between the store and the way out.

    Note: The documentary control it performs follows the record. No source describes the tally office as a
    building of its own; the room where the seal and the tally are made is inferred from them.

    Caveat: No source describes the tally office as a building of its own; the room where the seal and the
    tally are made is inferred from them.

    Name: tally office
    Covers: the tally office or tally shed and its label
    Label: accurate
    Sources: nishimawari-koro-jawiki, wagner-ming-iron, tonya-enwiki, economy-song-enwiki
    Entry: research/buildings.html - 'The granary is a staging node, not the terminal store'; research/urban-features.html - 'Charcoal yards: a tallied depot, a cooling ground, and a weighing floor'
    """

    key = "tally office"


class WeighingFloor(Kind):
    """
    What: An open, roofed work floor beside the tally office where bales are weighed before the tally is written;
    its balance and the bales on it are each their own feature.

    Why: The charcoal bale had no standard weight in the traditional Japanese system, unlike rice, and a
    commodity with no standard bale cannot be traded by count: it must be weighed at the point of sale. That
    is what the weighing floor is for, and it is also why the office's hold on the trade is a written record
    rather than ownership.

    Note: The weighing floor follows the record's reasoning, but its premise - that the charcoal bale had no standard weight - rests on no source read: the page it had been cited to says nothing about charcoal, and no other was found.

    Name: weighing floor
    Covers: the covered weighing floor, its posts and its label
    Label: accurate
    Sources: wagner-ming-iron, tonya-enwiki, fao-charcoal-safety
    Entry: research/urban-features.html - 'Charcoal yards: a tallied depot, a cooling ground, and a weighing floor'
    """

    key = "weighing floor"


# ---- the parts of the office (feature 264: a thing drawn inside a feature is its own kind) ----------------------


class DayOffice(Kind):
    """
    What: The day office (goyoba), the room of the office hall behind the dais where the county's daily business
    is done - petitions received, orders written, accounts kept.

    Why: The dais band is the front of a deeper hall, not a stage of its own: at Takayama the office wing holds the
    day office and the official study behind the court face. With no room built for interrogation, a questioning
    happens in the day office or the hearing court like any other business.

    Note: The day office as a room of the office hall, behind the dais, follows the record.

    Name: day office
    Covers: the day office's floor and its label
    Label: accurate
    Sources: takayama-jinya-jawiki, takayama-jinya-city
    Entry: research/buildings.html - 'The courtroom is a room of the office hall, not a freestanding stage', 'No interrogation room'
    """

    key = "day office"


class OfficialStudy(Kind):
    """
    What: The official study, the magistrate's working room in the office hall, where papers are read and
    judgments drafted.

    Why: The magistrate's official work belongs on the office side of the line between state and home; the private
    study in the residence is the wrong side of that line for official business, so the office hall keeps a
    study of its own behind the dais.

    Note: The official study as a room of the office hall follows the record.

    Name: official study
    Covers: the official study's floor and its label
    Label: accurate
    Sources: takayama-jinya-jawiki, takayama-jinya-city
    Entry: research/buildings.html - 'The courtroom is a room of the office hall, not a freestanding stage'
    """

    key = "official study"


class ClerksSeats(Kind):
    """
    What: The clerks' places on the dais band, one to either side of the magistrate's seat, where a hearing's
    proceedings would be written down.

    Why: A hearing is a matter of record: what the parties say and what the magistrate rules is taken down on the
    spot by the few clerks the office keeps.

    Note: the research record covers the clerks themselves, a few local commoners, but has no entry on who sat
    beside the magistrate at a hearing or where, so the two seats flanking the dais, and their size, are a guess.

    Name: clerks' seats
    Covers: the two seats flanking the dais and their labels
    Label: guess
    Sources: not recorded
    Entry: research/buildings.html (no dedicated entry - recorded as silent)
    """

    key = "clerks' seats"


class KneelingPositions(Kind):
    """
    What: The marked places on the hearing court's sand where the parties to a case kneel before the dais -
    witnesses, petitioners, the accused - each about the size of half a tatami mat.

    Why: A raised hall over kneeling litigants is common to both traditions this setting draws on: the magistrate
    sits above on the dais, the parties kneel below in the court, and the examination room and the court were
    one paired feature of the office block.

    Note: Kneeling litigants below the raised hall follow the record. The marks' size is this project's own
    figure; and at Takayama the court they kneel in was paved with stone and roofed, where these plans draw open
    sand.

    Caveat: The marks' size is this project's own figure; and at Takayama the court they kneel in was paved with
    stone and roofed, where these plans draw open sand.

    Name: kneeling positions
    Covers: the kneeling marks on the hearing court and their label
    Label: accurate
    Sources: henan-neixiang, neixiang-yamen-zhwiki, takayama-jinya-jawiki, takayama-jinya-city
    Entry: research/buildings.html - 'Administrative culture is JAPAN-first for compound interiors', 'The courtroom is a room of the office hall, not a freestanding stage'
    """

    key = "kneeling positions"


class GranaryStilts(Kind):
    """
    What: The posts that raise the granary's floor off the ground, drawn as small dark blocks at its foot.

    Why: A grain storehouse keeps its floor raised: at the great rice stores on the river at Edo, the answer to
    flood was the storehouse's own raised floor and a stone revetment, not distance from the water.

    Note: A storehouse's raised floor follows the record. How the floor was raised - on posts, as drawn, or on a
    stone base - is not in the record, and the one reason it gives, flood at a river quay, fits only a granary by
    the water; why one away from a river keeps its floor raised is not recorded.

    Caveat: How the floor was raised - on posts, as drawn, or on a stone base - is not in the record, and the one
    reason it gives, flood at a river quay, fits only a granary by the water; why one away from a river keeps its
    floor raised is not recorded.

    Name: granary stilts
    Covers: the posts at the granary's foot
    Label: accurate
    Sources: kuramae-jawiki, wheatbaku-asakusa-okura
    Entry: research/cities/capitals.html - "The sluice's lifting frame"
    """

    key = "granary stilts"
