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
    official study - is the main public block, and the hearing court is one room of that block. Daily
    paperwork is most of a magistrate's job, and the residence's private study is on the wrong side of the
    line between state and home for it, so the hall is deep, and it may be the largest building in the
    compound, being the institution's working core rather than a dwelling. A wooden hall could burn, and
    many did (the Sado magistracy was rebuilt five times, though Takayama's never burned), which is why the
    documents and the tax grain are kept in storehouses of their own.

    Note: The hall's form and its place follow the record. That it may out-size the residence is a guess, the
    Takayama pages giving no floor area for any building, and no readable source ranks a compound's footprints. Its size, about 80 to 150 ft
    long and 20 to 45 ft deep, is a guess: it is the plan vocabulary's working block, with no measured
    office wing of a jin'ya behind it.

    Caveat: That it may out-size the residence is a guess, the
    Takayama pages giving no floor area for any building, and no readable source ranks a compound's footprints. Its size, about 80 to 150 ft long and 20 to 45 ft deep, is a guess: it is the
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
    magistrate's seat at its center, with the clerks' seats beside it on these sheets.

    Why: A raised hall over kneeling litigants is common to both traditions this setting draws on, Japanese
    and Chinese. At the Edo town magistracy the court was a hall in tiers: the top tier a tatami room where
    the magistrate and the other officials sat, the magistrate in its innermost room, the examining officer
    and the clerk in the room between, and a narrow board veranda at its very front; below it lay the floor
    where the parties knelt. So the dais is not a pavilion of its own but the front of a deeper office hall,
    and the magistrate hears cases in the same building where the day's paperwork is done.

    Note: The raised seat over the court, and its place at the front of the office hall, follow the record. The
    clerks sat in the tier between the magistrate's room and the court; these sheets set their seats beside the
    dais instead, and how large their place was is not recorded, so the size drawn is a guess.

    Caveat: The clerks sat in the tier between the magistrate's room and the court; these sheets set their seats
    beside the dais instead, and how large their place was is not recorded, so the size drawn is a guess.

    Name: magistrate's dais
    Covers: the dais band on the office hall's court face, and its label
    Label: accurate
    Sources: oshirasu-jawiki, shirasu-kotobank, takayama-jinya-jawiki, takayama-jinya-city, neixiang-yamen-zhwiki
    Entry: research/buildings.html - 'Who sat where at a hearing, and on what?', 'The courtroom is a room of the office hall, not a freestanding stage', 'Administrative culture is JAPAN-first for compound interiors'
    """

    key = "magistrate's dais"


class ClerksRoom(Kind):
    """
    What: The workroom of the county's few hired clerks, a room of the office hall beside the day office,
    where the tax rolls and case papers are copied and kept in order. It is a place of work, never lodging.

    Why: At the Takayama intendant's office the clerks worked in rooms of the office: the workroom of the
    officials hired from the district was partitioned off beside the room where the shogunate's own officials
    worked, and a room used only for writing, where the documents sent to the shogunate were drawn up, had a
    binding room beside it. At the Edo town magistracy, too, the duty rooms of two of its record sections
    stood in the quarter of the compound that held its court. What stood apart as buildings of their own were
    the staff's houses; no page read gives the clerks a building of their own to work in. In both traditions the paperwork was run by locally hired
    commoners under a tiny elite staff; in Japan the tedai were drawn from the peasants and townsmen who knew
    the district. Scaled to a county of this setting, that is three or four clerks, scribes by caste
    (heimen), who live in town and come in to the manor each day - and who, as permanent locals, are the
    office's memory under one magistrate after another.

    Note: The clerks' room as a room of the office hall follows the record. Their number of three or four is
    this project's scaling from a Chinese county population the record gives no source for, and the room's
    size, about 28 by 18 ft for three or four clerks, is a guess with no measured example behind it.

    Caveat: Their number of three or four is this project's scaling from a Chinese county population the
    record gives no source for, and the room's size, about 28 by 18 ft for three or four clerks, is a guess
    with no measured example behind it.

    Name: clerks' room
    Covers: the clerks' room inside the office hall, its floor and its label
    Label: accurate
    Sources: mapple-takayama-jinya, edo-ashigaru-bugyosho, jinya-kotobank, tedai-jawiki, xuli-zhwiki
    Entry: research/buildings.html - 'Where did the clerks work - in a room of the office hall, or a building of their own?', 'Clerks are few, local, and heimen'
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
    county office is not confirmed by any page read, and keeping the fire-water tubs away from it is this
    map's reasoning from its fireproofing: the pages read place tubs at the doorway and on the roof, and the
    Qing palace's vats by courtyard, but none gives a priority among buildings.

    Name: tax archive
    Covers: the plastered archive kura and its label
    Label: accurate
    Sources: sado-bugyosho-fires, dozo-jawiki, tfd-hongou-fire-history
    Entry: research/buildings.html - 'Fire discipline: halls burn, kura endure', 'Fire-water is distributed to the halls, not the kura', 'Administrative culture is JAPAN-first for compound interiors'; research/cities/fabric.html - 'How did a dense wooden city watch for fire?'
    """

    key = "tax archive"


class Granary(Kind):
    """
    What: A vented storehouse where the tax paid in grain waits on its way to the governor: rice in straw
    bales above all, with a share of other grain beside it. It takes one of two forms - a timber storehouse
    raised on posts, or an earth-walled kura set with gaps for ventilation.

    Why: Both forms are attested. The storehouse on posts, the takakura, kept its floor high against rats and
    damp; the rice storehouse of the Takayama intendancy is an earth-walled kura, its walls set with gaps for
    ventilation, and a kura guarded its grain against fire, damp and theft. Tax rice flowed from the village granaries through the magistrate's compound toward central stores,
    so the office kura holds grain in transit plus a local reserve, and a county seat's granary stands inside
    the compound rather than in the town. Where water gives a county a way out, the grain moves on; a remote
    county, where transport costs more, keeps a row of kura instead. The lord's kura held the paddy tax as brown rice in straw
    bales, with a corner of unhulled rice kept against famine.

    Note: The kura, its rice and its place inside the compound follow the record, drawn at about 43 to 50 by
    25 to 27 ft and checked against real kura sizes, and so do its two forms, each sheet taking one. The
    storehouse on posts is attested in Japan for the southern islands and the Ainu north rather than for an
    intendant's office, whose grain store on the Takayama model is the earth-walled kura. The staging - tax rice passing through the compound and
    held there in transit beside a local reserve - is this map's own reading, which no source states, and the
    famine corner of unhulled rice is a simplification: Edo kept that reserve in separate community granaries,
    and one granary is drawn instead of two. That more of the dry-field tax arrives in kind - soybeans and
    barley in bales beside the rice - than it did in Edo Japan is this setting's own economics: Rokugan is
    rich in goods and poor in coin.

    Caveat: The storehouse on posts is attested in Japan for the southern islands and the Ainu north rather
    than for an intendant's office, whose grain store on the Takayama model is the earth-walled kura. The
    staging - tax rice passing through the compound and held there in transit beside a local reserve - is
    this map's own reading, which no source states, and the famine corner of unhulled rice is a
    simplification: Edo kept that reserve in separate community granaries, and one granary is drawn instead of
    two. That more of the dry-field tax arrives in kind - soybeans and barley in bales beside the rice - than
    it did in Edo Japan is this setting's own economics: Rokugan is rich in goods and poor in coin.

    Name: granary
    Covers: the granary, on posts or earth-walled, and its label
    Label: accurate
    Sources: takayukashiki-jawiki, takayama-onkura-heritage, dozo-jawiki, takayama-jinya-city, takayama-jinya-jawiki, nishimawari-koro-jawiki, gokura-jawiki, hatakata-men-jawiki, kuramai-jawiki, kakoimai-jawiki
    Entry: research/buildings.html - 'Did a granary stand on posts, and why raise its floor away from a river?', 'The granary is a staging node, not the terminal store', 'The granary holds grain, not just rice'; research/towns.html - 'Why is the magistrate's manor drawn as a plain walled box?'
    """

    key = "granary"


class Cell(Kind):
    """
    What: A small cage-like holding room with barred sides, where one or two of the accused wait for their
    case to be heard and judged. It is a place of waiting, not of punishment.

    Why: Edo jails held the accused pending judgment; the sentences were exile, flogging, fines or death -
    not, in the ordinary case, time in prison - and light offenders were sent home to their villages.
    Purpose-built prisons were separate compounds in the great cities, while a magistracy that judged cases
    kept a temporary cell inside its own compound for those called before its court. So a county magistracy
    keeps a cell or two for remand and no prison block - and in Rokugan, where torture is unusual, no room
    built for interrogation either.

    Note: Small remand cells follow the record (though no page read names exile or fines as sentences, or
    says light offenders were sent home), and so does a temporary cell inside the office's own compound. The
    size of such a cell was not found, so the drawn size is a guess within the span of the single cell rooms
    read, from Osaka's 6-mat cell (about 12 by 9 ft) to Tenmacho's 18-mat room (about 18 by 18 ft): about 12
    by 10 ft, at the small end, because a county cell holds only a few until their hearing. That a cell may
    stand anywhere in the compound is this setting's own: Chinese regulation put the county jail on the
    south side (Neixiang's stood in its southwest), and Rokugan keeps no such rule.

    Caveat: The size of such a cell was not found, so the drawn size is a guess within the span of the single
    cell rooms read, from Osaka's 6-mat cell (about 12 by 9 ft) to Tenmacho's 18-mat room (about 18 by 18
    ft): about 12 by 10 ft, at the small end, because a county cell holds only a few until their hearing.
    That a cell may stand anywhere in the compound is this setting's own: Chinese regulation put the county
    jail on the south side (Neixiang's stood in its southwest), and Rokugan keeps no such rule.

    Name: cell
    Covers: the barred holding cell and its label
    Label: accurate
    Sources: agariya-jawiki, roya-kotobank, edo-ashigaru-bugyosho, tenmacho-jawiki, chuo-royashiki, neixiang-yamen-zhwiki, henan-neixiang, takayama-jinya-city
    Entry: research/buildings.html - 'How big was a holding cell?', 'Cells are remand, not punishment', 'No interrogation room'
    """

    key = "cell"


class Gatehouse(Kind):
    """
    What: The watch's guardroom at the main gate, where the door is kept: either a small gatehouse of its own
    just inside the gate and to one side, or a room of the long gate range the gate passes through - never
    across the opening.

    Why: The main gate is the compound's one door for visitors on business, and a guard lodged beside it
    controls it without closing the way. Both forms are attested. At the Kashiwara domain's seat the
    guardroom, with an earth floor beside it, is a room of the gate range, a long building of about 81 by 12
    ft with the gate through its middle, and at Matsue the gate range housed the gatekeepers. At Takayama the
    gate and the gatekeepers' house were both built in 1832, the house a building of its own, and Edo castle's
    gates had their guardrooms too.

    Note: Both forms follow the record, and each sheet takes one; a depth of about 12 ft is attested for
    both. The size of Takayama's gatehouse was not found: the one freestanding guardroom measured is about 18
    by 12 ft, and a freestanding gatehouse drawn much longer, around 40 ft, is a guess at the gate range's
    scale.

    Caveat: The size of Takayama's gatehouse was not found: the one freestanding guardroom measured is about
    18 by 12 ft, and a freestanding gatehouse drawn much longer, around 40 ft, is a guess at the gate range's
    scale.

    Name: gatehouse
    Covers: the guard post beside the main gate, or the guardroom in the gate range, and its label
    Label: accurate
    Sources: tamba-kashiwara-jinya, matsue-bukeyashiki, takayama-jinya-city, takayama-jinya-jawiki, bansho-jawiki, kitain-bansho
    Entry: research/buildings.html - 'Where did the gatekeepers sit - in the gate range, or a gatehouse beside it?'
    """

    key = "gatehouse"


class Barracks(Kind):
    """
    What: A plain long building divided into bunk rooms, where the compound's working platoon and its duty
    watch lodge.

    Why: Rural intendants' offices most likely housed their staff on the grounds, though the record does not
    say so; it was the great city magistrate's offices that lodged their constables in a district of their
    own, keeping only the magistrate's household inside. A county posting's staff is a working platoon, mostly
    without dependents, so by default it lives on the grounds. By this map's own ordering, the barracks
    outranks the stable in size: a stable for a few horses never out-foots the watch's quarters.

    Note: On-grounds housing for the staff is a reconstruction: a small domain's jin'ya kept its retainers'
    residences inside its walls, but no source read says a rural intendant's staff lived on the grounds; only
    the city magistrates' separate constables' district is attested. That the barracks outranks the stable is
    this project's own reading, since no readable source ranks a compound's buildings by footprint. The
    building's size, about 20 to 70 ft by 10 to 40 ft, is a guess taken from the plan vocabulary's range, and
    how many live in it follows how the posting houses its staff.

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

    Why: Every Edo town and village kept an official edict board, the kosatsuba, hung high where traffic
    was heavy: at crossroads in a town's center, at its entrances, at bridge ends, barriers and ports, and
    before the gate of the village officials' houses. That board, where the town posts the state's standing
    law, is the attested one. Laws came to be posted at the gates of courts and offices only after the boards
    were abolished, in the Meiji period, and the likely counterpart of a court's own board, the posting walls
    at a Chinese county office's gate, could not be read. A magistracy's board stands at its own gate, on the
    way everyone who has business with the court must come.

    Note: The board and its roadside seat follow the record, which sets it before the gate of village
    officials' houses, though no page read puts a post town's board at its transport office; that every town and village kept one is a reading of the
    sources, not their words. That the bench keeps a board of its own, apart from the kosatsuba where the town
    posts the state's standing law, is this project's own division; the record finds only the settlement's
    board.

    Caveat: That the bench keeps a board of its own, apart from the kosatsuba where the town posts the state's
    standing law, is this project's own division; the record finds only the settlement's board.

    Name: notice board
    Covers: the board outside the main gate and its label
    Label: accurate
    Sources: kosatsu-jawiki, ogose-kosatsuba, adachi-kosatsu, kosatsu-enwiki, shoya-jawiki
    Entry: research/buildings.html - 'Did the magistrate post notices at the office's own gate, or on the town's notice board?'; research/urban-features.html - 'The notice board (kosatsuba) - siting is a TRAFFIC decision'
    """

    key = "notice board"


class TallyOffice(Kind):
    """
    What: A small office on the route goods take through the compound, where they are counted or weighed, the
    seal is set and the tally written: the record of goods the office supervises but does not own.

    Why: The magistracy's hold on moving goods is documentary. Tax rice moved on hired commoner boats flying
    an official pennant and inspected at the ports of call, the office owning no hulls - and a charcoal store
    was a supervised, tallied depot, its goods sealed there and never owned. So the post that writes the tally
    stands where the goods pass, between the store and the way out.

    Note: That tax rice moved on hired hulls under an official pennant and port inspection is read; that the
    office's hold on it was documentary is this project's reading. No source describes the tally office as a
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

    Why: The straw bale had no standard size in the traditional Japanese system, not even for rice, and charcoal
    was packed at a weight set by its grade; a commodity with no standard bale cannot be traded by count: it must be weighed at the point of sale. That
    is what the weighing floor is for, and it is also why the office's hold on the trade is a written record
    rather than ownership.

    Note: The weighing floor follows the record's reasoning, and its premise is read: the Japanese reference on the
    bale says it had no fixed standard size, even for rice, and that in one charcoal district (Hokkaido's Iburi,
    undated) a bale's weight was set by the charcoal's grade - one district's practice, not a rule shown to hold
    everywhere.

    Name: weighing floor
    Covers: the covered weighing floor, its posts and its label
    Label: accurate
    Sources: wagner-ming-iron, tonya-enwiki, fao-charcoal-safety, tawara-unit-jawiki
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

    Note: The day office as a room of the office hall, behind the dais, follows the record. That no room is built
    for interrogation is a setting decision (GM, 2026-07), not the record: Takayama had an examination room
    (ginmisho) beside its roofed court, and its torture was done in the jail in the town.


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
    What: The clerks' places in the office hall's front band, one to either side of the magistrate's seat and
    above the court, where a hearing's proceedings are written down.

    Why: A hearing is a matter of record: what the parties say and what the magistrate rules is taken down on the
    spot by the office's clerks. At the Edo town magistracy the court was a hall in tiers, and the
    clerk sat with the examining officer in the room between the magistrate's innermost room and the court;
    some magistrates' courts set an upper tier apart for the examiners and the scribes. The clerks sit in the hall,
    never on the court itself.

    Note: The clerks' place in the hall, between the magistrate and the court and never on the court, follows
    the record. How large that place was is not recorded, so the seats' size is a guess, and the plans set the
    clerks to either side of the dais in one band rather than in a room of their own below it.

    Caveat: How large that place was is not recorded, so the seats' size is a guess, and the plans set the
    clerks to either side of the dais in one band rather than in a room of their own below it.

    Name: clerks' seats
    Covers: the two seats flanking the dais and their labels
    Label: accurate
    Sources: oshirasu-jawiki, shirasu-kotobank
    Entry: research/buildings.html - 'Who sat where at a hearing, and on what?'
    """

    key = "clerks' seats"


class KneelingPositions(Kind):
    """
    What: The straw mats on the hearing court's floor where the parties to a case kneel before the dais: the
    accused at the center, the plaintiff behind to one side, the village officials behind to the other.

    Why: A raised hall over kneeling litigants is common to both traditions this setting draws on: the magistrate
    sits above on the dais, the parties kneel below in the court. At the Edo town magistracy peasants,
    townsmen and lesser ronin knelt on straw mats spread on the court's gravel, while samurai, priests and
    monks sat on the hall's verandas; the accused sat at the center, roped, with the town officials, headmen
    and landlords behind on one side and the plaintiff behind on the other.

    Note: Commoners kneeling on straw mats below the raised hall follow the record. The arrangement of the
    mats is attested only at Edo, so carrying it to a county court is a guess, and the mats' size is this
    project's own figure.

    Caveat: The arrangement of the mats is attested only at Edo, so carrying it to a county court is a guess,
    and the mats' size is this project's own figure.

    Name: kneeling positions
    Covers: the straw mats on the hearing court and their label
    Label: accurate
    Sources: oshirasu-jawiki, shirasu-kotobank, shirasu-imidas, henan-neixiang, neixiang-yamen-zhwiki
    Entry: research/buildings.html - 'Who sat where at a hearing, and on what?', 'Administrative culture is JAPAN-first for compound interiors', 'The courtroom is a room of the office hall, not a freestanding stage'
    """

    key = "kneeling positions"


class GranaryStilts(Kind):
    """
    What: The posts that raise the granary's floor off the ground, drawn as small dark blocks at its foot, where
    the granary is a storehouse on posts.

    Why: The storehouse on posts, the takakura, kept its floor high to keep rats from the grain, with guards
    against them, and to let the air through against damp. Neither reason is a river's, so both hold for a
    granary away from the water as well as for one beside it; at the great rice stores on the river at Edo, a
    raised floor answered flood besides. Such storehouses were still built in Japan on Amami Oshima, on
    Hachijojima and among the Ainu into modern times.

    Note: The floor raised on posts follows the record as one of a granary's two forms, though it is attested for the southern islands and the Ainu north, not for an intendancy's store; the other, an
    earth-walled kura like the Takayama intendancy's rice store, is drawn with no posts. That rats and damp
    hold away from a river is this project's reading of the reasons given, and how an earth-walled kura's
    floor was raised was not found, so posts under one would be a guess.

    Caveat: That rats and damp hold away from a river is this project's reading of the reasons given, and how
    an earth-walled kura's floor was raised was not found, so posts under one would be a guess.

    Name: granary stilts
    Covers: the posts at the granary's foot
    Label: accurate
    Sources: takayukashiki-jawiki, takayama-onkura-heritage, kuramae-jawiki, wheatbaku-asakusa-okura
    Entry: research/buildings.html - 'Did a granary stand on posts, and why raise its floor away from a river?'; research/cities/capitals.html - "The sluice's lifting frame"
    """

    key = "granary stilts"
