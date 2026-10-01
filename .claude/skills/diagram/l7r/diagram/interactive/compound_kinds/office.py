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

    Why: At Takayama, the surviving intendant's office, the office block - entrance hall, great hall, office and
    examination room, rebuilt in 1816, parts this project reads as one block - was built with great formality to show the office's rank, and the room where hearings were held is one part of that block. The
    magistrate and staff need somewhere to do the daily paperwork, and the residence's private study is on
    the wrong side of the line between state and home for it, so the hall is deep, and it may be the largest
    hall in the compound, out-measuring the residence as Takayama's did, being the institution's working core
    rather than a dwelling; only a store for a wide territory's rice may be larger. A wooden hall
    could burn, and many did (the Sado magistracy was rebuilt five times, though Takayama's never burned),
    which, this project judges, is why the documents and the tax grain are kept in storehouses of their own.

    Note: The hall's form follows the record; its place in the front court, with the residence behind, is the
    Chinese yamen's order, and for the Japanese form a deliberate simplification, since at Takayama the residence
    stood beside the office, not behind it. The day office and official study behind the dais
    are this project's reading of what the block must hold, since no page read names them. That it out-sizes the
    residence follows Takayama, the one office measured building by building (about 8,100 sq ft against 6,400); no
    second office gives an area for any building, and why the papers and grain went to storehouses is this
    project's guess, as no page read says. Its size, about 80 to 150 ft long and 20 to 45 ft deep, is a guess: it
    is the plan vocabulary's working block, and it is smaller than the one office measured, Takayama's at about
    8,100 sq ft.

    Caveat: The day office and official study behind the dais are this project's reading of what the block
    must hold, since no page read names them. That it out-sizes the residence follows Takayama, the one office
    measured building by building (about 8,100 sq ft against 6,400); no second office gives an area for any
    building, and why the papers and grain went to storehouses is this project's guess, as no page read says. Its
    size, about 80 to 150 ft long and 20 to 45 ft deep, is a guess: it is the plan vocabulary's working block, and
    it is smaller than the one office measured, Takayama's at about 8,100 sq ft.

    Name: office hall
    Covers: the office hall's block, its outline and its front band
    Label: accurate
    Sources: takayama-jinya-jawiki, takayama-jinya-city, sado-bugyosho-fires
    Entry: research/buildings.html - 'The hearing court (shirasu)', "Magistrates' compounds (jin'ya and yamen)", 'The size of a compound and the rank of its buildings', 'Fire, and the fireproof storehouses (dozō)'; research/rendering/buildings.html - 'How our maps draw the hearing court (shirasu)', 'How our maps size a compound and its buildings', 'How our maps draw a magistrate's compound'
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

    Note: The raised seat over the court, and its place at the front of the office hall, follow the record.
    At Edo the clerk sat in a room between the magistrate's room and the court; these sheets set their
    seats beside the dais instead, and how large their place was is not recorded, so the size drawn is a guess.

    Caveat: At Edo the clerk sat in a room between the magistrate's room and the court; these sheets set their
    seats beside the dais instead, and how large their place was is not recorded, so the size drawn is a guess.

    Name: magistrate's dais
    Covers: the dais band on the office hall's court face, and its label
    Label: accurate
    Sources: oshirasu-jawiki, shirasu-kotobank, takayama-jinya-jawiki, takayama-jinya-city, neixiang-yamen-zhwiki
    Entry: research/buildings.html - 'The hearing court (shirasu)', "Magistrates' compounds (jin'ya and yamen)"; research/rendering/buildings.html - 'How our maps draw the hearing court (shirasu)', 'How our maps draw a magistrate's compound'
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
    the staff's houses; no page read gives the clerks a building of their own to work in. In Japan the
    paperwork was run by clerks, the tedai, chosen from the peasants and townsmen versed in rural
    administration, under officials sent by the shogunate; a Chinese county kept its clerks in six chambers
    of a few men each. Scaled to a county of this setting, that is three or four clerks, scribes by caste
    (heimen), who live in town and come in to the manor each day - and who, as permanent locals, are the
    office's memory under one magistrate after another, this project's reading of the entrenched clerks of
    China's offices.

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
    Entry: research/buildings.html - 'The office hall and its clerks (goyakusho)'; research/rendering/buildings.html - 'How our maps draw the office hall and its clerks (goyakusho)'
    """

    key = "clerks' room"


class TaxArchive(Kind):
    """
    What: A sealed storehouse (kura) of thick white-plastered earth, holding the county's
    ledgers - its tax base on paper - and serving as the strongroom for the coin and valuables the office
    holds.

    Why: Administrative halls were timber buildings and could burn - the Sado magistracy burned and was
    rebuilt five times, though Takayama's office never did - while an earthen kura was built to keep fire
    out, its walls thick with plaster. That, this project judges, is why the documents got a
    storehouse of their own instead of a room in the hall. The fire-water tubs stand at the wooden buildings
    and not here: this is the one building made not to burn.

    Note: The document storehouse follows the record, though why an office kept its papers there and not in
    the hall is this map's guess, as no page read says; it is drawn as a sealed kura of about 32 to 36 ft, the
    plan vocabulary's size, larger than the one records store measured, Takayama's of about 450 sq ft, which
    the record takes as the ceiling for a county office's; the record's proportions for it are a guess. An archive in the Chinese
    county office is not confirmed by any page read, and keeping the fire-water tubs away from it is this
    map's reasoning from its fireproofing: the pages read place tubs at the doorway and on the roof, and the
    Qing palace's vats by courtyard, but none gives a priority among buildings.

    Name: tax archive
    Covers: the plastered archive kura and its label
    Label: accurate
    Sources: sado-bugyosho-fires, dozo-jawiki, tfd-hongou-fire-history
    Entry: research/buildings.html - 'Fire, and the fireproof storehouses (dozō)', "Magistrates' compounds (jin'ya and yamen)"; research/rendering/buildings.html - 'How our maps draw a magistrate's compound', 'How our maps draw fire water and the fireproof storehouses (dozō)'; research/urban-features.html - 'Fire watch towers and firefighting gear (hinomi yagura)'
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
    so the office kura holds grain in transit plus a local reserve; and since an intendant's seat was also where the year's tax was stored, a county seat's granary stands inside
    the compound rather than in the town. Where water gives a county a way out, the grain waits in a row of storehouses at its river landing and moves on; a remote
    county, where transport costs more, keeps it in the office's own storehouse instead. The lord's kura held the paddy tax as brown rice in straw
    bales, with a corner of unhulled rice kept against famine.

    Note: The kura, its rice and its place inside the compound follow the record; that a county with water ships its grain on while a remote one keeps it in the office's storehouse is this map's reading and partly a guess: the storehouses at a county's landing are inferred from a great domain's store at the river port of Kawashiri, and no source says Takayama's rows held all of Hida's rice. The kura is drawn at about 43 to 50 by
    25 to 27 ft and set by guess, since no source gives a county office's storehouse size, between the 440 to 740 sq ft of a three-village store's storehouses and a tenth of Takayama's 11,222 sq ft; its two forms follow the record, each sheet taking one. The
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
    Entry: research/buildings.html - 'Storehouses for the tax rice'; research/rendering/buildings.html - 'How our maps draw storehouses for the tax rice'; research/towns.html - 'The magistrate's manor in a town: where it stands and which way it faces (jin'ya and yamen)'; research/rendering/towns.html - 'How our maps draw the magistrate's manor on a town map'
    """

    key = "granary"


class Cell(Kind):
    """
    What: A small cage-like holding room with barred sides, where one or two of the accused wait for their
    case to be heard and judged. It is a place of waiting, not of punishment.

    Why: Edo jails held the accused pending judgment; the sentences were exile, flogging, fines or death -
    not, in the ordinary case, time in prison - and light offenders were sent home to their villages.
    The largest jail, Edo's Tenmachō, was a walled and moated compound of its own; most others stood at
    magistrates' and daikan offices, and a magistracy that judged cases kept a temporary cell inside its own
    compound for those called before its court. So a county magistracy keeps a cell or two for remand and no
    prison block - and in Rokugan, where torture is unusual, no room built for interrogation either.

    Note: Small remand cells follow the record, though holding only one or two is a guess (and no page read
    names exile or fines as sentences, or says light offenders were sent home), and so does a temporary cell
    inside the office's own compound. Drawing no room for interrogation is this setting's own departure
    from Edo, whose jails had one. The
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
    Entry: research/buildings.html - 'Holding cells (agariya and rōya)'; research/rendering/buildings.html - 'How our maps draw holding cells (agariya and rōya)'
    """

    key = "cell"


class Gatehouse(Kind):
    """
    What: The watch's guardroom at the main gate, where the door is kept: either a small gatehouse of its own
    beside the gate, or a room of the long gate range the gate passes through - never across the opening.

    Why: The main gate is the compound's one door for visitors on business, and a guard lodged beside it
    controls it without closing the way. Both forms are attested. At the Kashiwara domain's seat the
    guardroom, with an earth floor beside it, is a room of the gate range, a long building of about 81 by 12
    ft with the gate through its middle, and at Matsue the gate range housed the gatekeepers. At Takayama the
    gate and the gatekeepers' house were both built in 1832, the house a building of its own, and Edo castle's
    gates had their guardrooms too.

    Note: Both forms follow the record, and each sheet takes one; a depth of about 12 ft is attested for
    both. The size of Takayama's gatehouse, and where it stood, were not found: the one gatehouse of its own
    measured, a temple gate's guardroom at Kita-in that now stands against the gate, is about 18 by 12 ft, and
    a gatehouse of its own drawn much longer, around 40 ft, is a guess at the gate range's scale.

    Caveat: The size of Takayama's gatehouse, and where it stood, were not found: the one gatehouse of its own
    measured, a temple gate's guardroom at Kita-in that now stands against the gate, is about 18 by 12 ft, and
    a gatehouse of its own drawn much longer, around 40 ft, is a guess at the gate range's scale.

    Name: gatehouse
    Covers: the guard post beside the main gate, or the guardroom in the gate range, and its label
    Label: accurate
    Sources: tamba-kashiwara-jinya, matsue-bukeyashiki, takayama-jinya-city, takayama-jinya-jawiki, bansho-jawiki, kitain-bansho
    Entry: research/buildings.html - 'The main gate and its gatekeepers (nagaya-mon)'; research/rendering/buildings.html - 'How our maps draw the main gate and its gatekeepers (nagaya-mon)'
    """

    key = "gatehouse"


class Barracks(Kind):
    """
    What: A plain long rowhouse divided into dwellings, where the compound's working platoon and its duty
    watch lodge - a few unmarried men sharing a unit, the lowest servants in a common room; no bunks.

    Why: Rural intendants' offices kept the huts and rowhouses of their junior officials on the grounds - Takayama's kept a rowhouse for its storehouse keepers - though for the rest of the staff the record does not
    say so; it was the great city magistrate's offices that lodged their constables in a district of their
    own, while the magistrate's own residence stood inside the office. A county posting's staff is a working platoon, mostly
    without dependents, so by default it lives on the grounds. By this map's own ordering, the barracks
    outranks the stable in size: a stable for a few horses never out-foots the watch's quarters.

    Note: On-grounds housing for the staff is a reconstruction: a small domain's jin'ya kept its retainers'
    residences inside its walls, an intendant's office kept huts and rowhouses for its junior officials, and the Takayama intendancy kept a rowhouse for its storehouse keepers, but no source read says the rest of a rural intendant's staff lived on the grounds; for a
    city magistrate's office, the separate constables' district and the magistrate's own residence inside the office are attested. That the barracks outranks the stable is
    this project's own reading, since no page read says where a stable ranked among an office's buildings; that the
    staff's rowhouse stands below the office hall and the residence is read, from Takayama's measured floor areas.
    The building's size as drawn, about 20 to 70 ft by 10 to 40 ft, is a guess taken from the plan vocabulary's
    range: the five staff rowhouses measured run about 80 to 145 ft long and 12 to 24 ft deep, longer and narrower
    than that range allows, and how many live in it follows how the posting houses its staff. A warrior's rowhouse
    divided into dwellings is read (an Edo duty rowhouse of 1860, three retainers to a unit); no page read puts a bed
    or bunk in one before modern times, and when beds first came into a Japanese barracks was not found (the army
    barracks built at Nagoya in 1873 is shown with beds today, but that date is the building's, not the beds').

    Caveat: The building's size as drawn, about 20 to 70 ft by 10 to 40 ft, is a guess taken from the plan
    vocabulary's range: the five staff rowhouses measured run about 80 to 145 ft long and 12 to 24 ft deep, longer
    and narrower than that range allows, and how many live in it follows how the posting houses its staff.

    Name: barracks
    Covers: the barracks building and its label
    Label: accurate
    Sources: hatchobori-jawiki, takayama-jinya-jawiki, jinya-jawiki
    Entry: research/buildings.html - 'Staff rowhouses and barracks (nagaya)', 'The size of a compound and the rank of its buildings'; research/rendering/buildings.html - 'How our maps draw staff rowhouses and barracks (nagaya)', 'How our maps size a compound and its buildings'
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
    at a Chinese county office's gate, carried edicts, the magistrate's own notices and bans, wanted notices
    among them, and verdicts. A magistracy's board stands at its own gate, on the
    way everyone who has business with the court must come.

    Note: The board and its roadside seat follow the record, which sets it before the gate of village
    officials' houses, though no page read puts a post town's board at its transport office; every village's board is attested, and that every town kept
    one is a reading of the sources, not their words. Notices at an office's own gate are read too, in a modern popular
    history whose dates are thin - a Chinese county office posted edicts, its own notices and bans on the splayed walls at its gate. A freestanding board at the gate,
    rather than the gate's walls, is a guess joined from the Chinese walls and the Japanese village officials' boards;
    no board at a Japanese intendant's office was found.

    Name: notice board
    Covers: the board outside the main gate and its label
    Label: guess
    Sources: kosatsu-jawiki, ogose-kosatsuba, adachi-kosatsu, kosatsu-enwiki, shoya-jawiki
    Entry: research/urban-features.html - 'Notice boards (kosatsuba)'; research/rendering/urban-features.html - 'How our maps place and draw notice boards (kosatsuba)'
    """

    key = "notice board"


class TallyOffice(Kind):
    """
    What: A small office on the route goods take through the compound, where they are counted or weighed, the
    seal is set and the tally written: the record of goods the office supervises but does not own.

    Why: The magistracy's hold on moving goods is documentary. The shogunate's tax rice went by sea on ships it hired directly, flying
    an official pennant and inspected at the ports of call, the office owning no hulls - and a charcoal store
    is drawn on our maps as a supervised, tallied depot, its goods sealed there and never owned. So the post that writes the tally
    stands where the goods pass, between the store and the way out.

    Note: That the shogunate's tax rice went by sea on hired hulls under an official pennant and port inspection is read, and that the office owned no hulls of its own, and carrying that to a county's river, are this project's own; that the
    office's hold on it was documentary is this project's reading, and drawing a charcoal store as a supervised, tallied depot is this project's decision, not a finding. No source describes the tally office as a
    building of its own; the room where the seal and the tally are made is inferred from them.

    Caveat: No source describes the tally office as a building of its own; the room where the seal and the
    tally are made is inferred from them.

    Name: tally office
    Covers: the tally office or tally shed and its label
    Label: accurate
    Sources: nishimawari-koro-jawiki, wagner-ming-iron, tonya-enwiki, economy-song-enwiki
    Entry: research/buildings.html - 'Storehouses for the tax rice'; research/rendering/buildings.html - 'How our maps draw storehouses for the tax rice'; research/urban-features.html - 'Charcoal yards and charcoal stores'; research/rendering/urban-features.html - 'How our maps draw charcoal yards and charcoal stores'
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

    Note: The weighing floor follows the record's reasoning - no source read says a charcoal dealer weighed the bales at sale - and its premise is read: the Japanese reference on the
    bale says it had no fixed standard size, even for rice, and that in one charcoal district (Hokkaido's Iburi,
    undated) a bale's weight was set by the charcoal's grade - one district's practice, not a rule shown to hold
    everywhere.

    Name: weighing floor
    Covers: the covered weighing floor, its posts and its label
    Label: accurate
    Sources: wagner-ming-iron, tonya-enwiki, fao-charcoal-safety, tawara-unit-jawiki
    Entry: research/urban-features.html - 'Charcoal yards and charcoal stores'; research/rendering/urban-features.html - 'How our maps draw charcoal yards and charcoal stores'
    """

    key = "weighing floor"


# ---- the parts of the office (feature 264: a thing drawn inside a feature is its own kind) ----------------------


class DayOffice(Kind):
    """
    What: The day office (goyoba), the room of the office hall behind the dais where the county's daily business
    is done - petitions received, orders written, accounts kept.

    Why: The dais band is the front of a deeper hall, not a stage of its own: at Takayama the office wing holds the
    entrance hall, examination room, office and great hall, which we read as one block, and so we set the day office and official study behind the court face. With no room built for interrogation, a questioning
    happens in the day office or the hearing court like any other business.

    Note: The dais as the front of the office hall follows the record; the day office behind it is our own guess
    at what the block must hold, since no page we read places it behind the court. That no room is built
    for interrogation is this project's decision for the setting, not the record: Takayama had an examination room
    (ginmisho) beside its roofed court, and its torture is reported to have been done in the jail in the town.


    Name: day office
    Covers: the day office's floor and its label
    Label: guess
    Sources: takayama-jinya-jawiki, takayama-jinya-city
    Entry: research/buildings.html - 'The office hall and its clerks (goyakusho)', 'The hearing court (shirasu)', 'Holding cells (agariya and rōya)'; research/rendering/buildings.html - 'How our maps draw the office hall and its clerks (goyakusho)', 'How our maps draw the hearing court (shirasu)', 'How our maps draw holding cells (agariya and rōya)'
    """

    key = "day office"


class OfficialStudy(Kind):
    """
    What: The official study, the magistrate's working room in the office hall, where papers are read and
    the office's daily paperwork done.

    Why: The magistrate's official work belongs on the office side of the line between state and home; the private
    study in the residence is the wrong side of that line for official business, so the office hall keeps a
    study of its own behind the dais.

    Note: The official study is this project's own guess: the Takayama office was rebuilt in 1816 in parts
    including its entrance hall, examination room, working office and great hall, which we read as one block,
    and a study behind the dais is inferred from where the office's paperwork must be done, since no page read
    places one behind the dais.

    Name: official study
    Covers: the official study's floor and its label
    Label: guess
    Sources: takayama-jinya-jawiki, takayama-jinya-city
    Entry: research/buildings.html - 'The office hall and its clerks (goyakusho)', 'The hearing court (shirasu)'; research/rendering/buildings.html - 'How our maps draw the office hall and its clerks (goyakusho)', 'How our maps draw the hearing court (shirasu)'
    """

    key = "official study"


class ClerksSeats(Kind):
    """
    What: The clerks' places in the office hall's front band, one to either side of the magistrate's seat and
    above the court, where a hearing's proceedings are written down.

    Why: A hearing is a matter of record: what the parties say and what the magistrate rules is taken down on the
    spot by the office's clerks. At the Edo town magistracy the court was a hall in tiers, and the
    clerk sat with the examining officer in the room between the magistrate's innermost room and the court;
    some magistrates' courts set a further upper room apart for the examiners and the scribes. The clerks sit in the
    hall, never on the court itself.

    Note: The clerks' place in the hall, above the court and never on it, follows the record. Setting them to
    either side of the dais, level with it, rather than in a room of their own below it, is a deliberate
    deviation for simplicity. How large that place was is not recorded, so the seats' size is a guess.

    Name: clerks' seats
    Covers: the two seats flanking the dais and their labels
    Label: deviation
    Sources: oshirasu-jawiki, shirasu-kotobank
    Entry: research/buildings.html - 'The hearing court (shirasu)'; research/rendering/buildings.html - 'How our maps draw the hearing court (shirasu)'
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
    mats is attested only at Edo; a Chinese county court at Neixiang marked only two places, kneeling stones
    for the plaintiff to the east and the defendant, so carrying the Edo arrangement to a county court is a
    guess, and the mats' size is this project's own figure.

    Caveat: The arrangement of the mats is attested only at Edo; a Chinese county court at Neixiang marked only
    two places, kneeling stones for the plaintiff to the east and the defendant, so carrying the Edo arrangement
    to a county court is a guess, and the mats' size is this project's own figure.

    Name: kneeling positions
    Covers: the straw mats on the hearing court and their label
    Label: accurate
    Sources: oshirasu-jawiki, shirasu-kotobank, shirasu-imidas, henan-neixiang, neixiang-yamen-zhwiki
    Entry: research/buildings.html - 'The hearing court (shirasu)', "Magistrates' compounds (jin'ya and yamen)"; research/rendering/buildings.html - 'How our maps draw the hearing court (shirasu)', 'How our maps draw a magistrate's compound'
    """

    key = "kneeling positions"


class GranaryStilts(Kind):
    """
    What: The posts that raise the granary's floor off the ground, drawn as small dark blocks at its foot, where
    the granary is a storehouse on posts.

    Why: The storehouse on posts, the takakura, kept its floor high to keep rats from the grain, with guards
    against them, and to let the air through against damp. Neither reason is a river's, so both hold for a
    granary away from the water as well as for one beside it.
    Such storehouses were still built in Japan on Amami Oshima, on
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
    Entry: research/buildings.html - 'Storehouses for the tax rice'; research/rendering/buildings.html - 'How our maps draw storehouses for the tax rice'; research/cities/capitals.html - 'Rice storehouses and the rice brokers in a capital (kura, fudasashi)'
    """

    key = "granary stilts"
