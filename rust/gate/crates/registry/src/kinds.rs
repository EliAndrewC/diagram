//! The Rust registry of the map's kinds (feature 449 T149, `ask:449-phase4-slices` Q5): the non-prose half of
//! `l7r/diagram/interactive/classes/*.py` and `compound_kinds/*.py` - each family module, its classes in definition order, each class's
//! name and `key` (the tag the engine writes on the ink and the CSS token) - with the `#` comments the Python carried above a class kept
//! as comments here, for the next developer. A kind's modal text is not here: it is the Markdown file `assets/modals/<hamlet|sheet>/<slug
//! of its key>.md` (feature 319 moved it out of the class docstrings), which [`crate::about`] reads.
//!
//! WHY A TABLE AND NOT THE PYTHON PARSED: `modals.rs` read the classes out of the `.py` sources with a Python lexer (feature 449 T87), a
//! reading that ends when S11 deletes them; the table is what the Rust readers ask from S6 on. The Python classes were deleted
//! by feature 449 T158 once nothing imported them, and with them the test that held this table equal to them: the table is the one
//! registry.
//!
//! TWO ORDERS, BOTH THE PYTHON'S: a registry lists its families in the order its `__init__.py` imports them (`_ORDER`, the spec's FR-007
//! sequence for the hamlet vocabulary), [`HAMLET`] and [`SHEET`] below; the modal checks enumerate them as `modals.rs` globbed the
//! modules, by file name ([`by_file`]).

/// One kind: its class name and its key.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Kind {
    pub class: &'static str,
    pub key: &'static str,
}

/// One family module and its kinds in definition order.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Family {
    pub module: &'static str,
    pub kinds: &'static [Kind],
}

/// A registry: where its modal files are (`assets/modals/<dir>/`) and its families.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Registry {
    pub dir: &'static str,
    pub families: &'static [Family],
}

/// The hamlet vocabulary (`classes/`), whose modals are `assets/modals/hamlet/`.
pub const HAMLET_REGISTRY: Registry = Registry {
    dir: "hamlet",
    families: &HAMLET,
};

/// The Mode A kinds (`compound_kinds/`), a registry of their own because a compound's well is written about a compound (feature 262).
pub const SHEET_REGISTRY: Registry = Registry {
    dir: "sheet",
    families: &SHEET,
};

/// Both registries, the hamlet's first (`modals.rs`'s `MODAL_DIRS` order).
pub const REGISTRIES: [Registry; 2] = [HAMLET_REGISTRY, SHEET_REGISTRY];

impl Registry {
    /// Every kind, family by family, in this registry's own order, each with its family's module name.
    #[must_use]
    pub fn kinds(&self) -> Vec<(&'static str, Kind)> {
        self.families
            .iter()
            .flat_map(|f| f.kinds.iter().map(|k| (f.module, *k)))
            .collect()
    }
}

/// Every kind of `registry` as `modals.rs` met them: the family modules by file name (`sorted(glob("*.py"))`), each in definition order.
#[must_use]
pub fn by_file(registry: &Registry) -> Vec<(&'static str, Kind)> {
    let mut families: Vec<&Family> = registry.families.iter().collect();
    families.sort_by_key(|f| f.module);
    families
        .into_iter()
        .flat_map(|f| f.kinds.iter().map(|k| (f.module, *k)))
        .collect()
}

/// The hamlet registry's families, in the order its registry lists them.
pub const HAMLET: [Family; 5] = [
    Family {
        module: "homestead",
        kinds: &[
            // The GM's ruling: a farmhouse's work yard and garden beds always line up with their house.
            Kind {
                class: "Farmhouse",
                key: "farmhouse",
            },
            Kind {
                class: "StorageShed",
                key: "storage shed",
            },
            Kind {
                class: "Byre",
                key: "byre",
            },
            Kind {
                class: "RetirementHouse",
                key: "retirement house",
            },
            Kind {
                class: "ThreshingYard",
                key: "threshing yard",
            },
            Kind {
                class: "Garden",
                key: "garden",
            },
            Kind {
                class: "Privy",
                key: "privy",
            },
            Kind {
                class: "WoodShed",
                key: "wood shed",
            },
            Kind {
                class: "ManureHeap",
                key: "manure heap",
            },
            Kind {
                class: "BathRoom",
                key: "bath room",
            },
            Kind {
                class: "HenCoop",
                key: "hen coop",
            },
            // The GM's ruling: the old-families pattern for household shrines (rare, notable when it appears; three to
            // eight households in a hundred), over the every-house pattern of other regions.
            Kind {
                class: "HouseholdShrine",
                key: "household shrine",
            },
            // Feature 374 wave 136: a farmstead's own grave at its plot's corner, on the hamlets whose roll keeps household graves.
            Kind {
                class: "HouseholdGrave",
                key: "household grave",
            },
            Kind {
                class: "Persimmon",
                key: "persimmon",
            },
            Kind {
                class: "BurialGround",
                key: "burial ground",
            },
        ],
    },
    Family {
        module: "greenery",
        kinds: &[
            Kind {
                class: "HomesteadBamboo",
                key: "homestead bamboo",
            },
            Kind {
                class: "SharedBambooGrove",
                key: "shared bamboo grove",
            },
            // The GM's rulings: the maps show the regional northwesterly winter wind unless a place declares its own.
            Kind {
                class: "Windbreak",
                key: "windbreak",
            },
            Kind {
                class: "HomesteadGrove",
                key: "homestead grove",
            },
            Kind {
                class: "Alder",
                key: "alder",
            },
            // The GM's correction: the copse's fruit trees and bamboo fill the gaps throughout the cluster.
            Kind {
                class: "Copse",
                key: "copse",
            },
            Kind {
                class: "WoodlandCommons",
                key: "woodland commons",
            },
            // The GM's ruling: an irrigation channel's bank keeps scrub off by the same 6 ft as a bund.
            Kind {
                class: "ScrubAndRoughGrazing",
                key: "scrub and rough grazing",
            },
            Kind {
                class: "FloodplainMeadow",
                key: "floodplain meadow",
            },
            Kind {
                class: "PaddysGrassHill",
                key: "paddy's grass hill",
            },
            Kind {
                class: "Marsh",
                key: "marsh",
            },
            // Feature 385 T08: a tail pond's planted bank (0061, the Song manual's mulberry and cudrania) - its own kind, not a planting on
            // the pond, since the bank is not drawn as a feature.
            Kind {
                class: "PondBankTree",
                key: "pond-bank tree",
            },
        ],
    },
    Family {
        module: "fields",
        kinds: &[
            Kind {
                class: "Paddy",
                key: "paddy",
            },
            Kind {
                class: "WetPaddy",
                key: "wet paddy",
            },
            Kind {
                class: "Bund",
                key: "bund",
            },
            Kind {
                class: "BundBeans",
                key: "bund beans",
            },
            Kind {
                class: "Millet",
                key: "millet",
            },
            Kind {
                class: "Buckwheat",
                key: "buckwheat",
            },
            Kind {
                class: "Barley",
                key: "barley",
            },
            Kind {
                class: "Soy",
                key: "soy",
            },
            Kind {
                class: "Fallow",
                key: "fallow",
            },
            Kind {
                class: "Holding",
                key: "farm holding",
            },
        ],
    },
    Family {
        module: "water_and_ways",
        kinds: &[
            // The GM's rulings: stream width by rank in the water hierarchy, junctions not conserving width (2026-08-16);
            // the earlier width ladder, a stream feeding a moat drawn as wide as the moat (2026-07-21).
            Kind {
                class: "Stream",
                key: "stream",
            },
            Kind {
                class: "IrrigationDitch",
                key: "irrigation ditch",
            },
            Kind {
                class: "FarmChannel",
                key: "farm channel",
            },
            Kind {
                class: "DrainageDitch",
                key: "drainage ditch",
            },
            Kind {
                class: "Weir",
                key: "weir",
            },
            // Feature 374 wave 150 (0065): a footing of steps at the water's edge where a stream or ditch passes the houses - shared on the
            // bank or one at each house's channel, the `washing_form` knob.
            Kind {
                class: "WashingPlace",
                key: "washing place",
            },
            Kind {
                class: "Pond",
                key: "pond",
            },
            Kind {
                class: "FieldPond",
                key: "field pond",
            },
            Kind {
                class: "FieldRock",
                key: "field rock",
            },
            // Feature 349 (settlement-review, Kashikawa 2026-09-28): the class covers both forms of the field grave knob - the island
            // (Chinese) and the corner (Japanese) - so it is not named for one of them.
            Kind {
                class: "FieldGrave",
                key: "field grave",
            },
            // WHY THE CLASS IS A *VILLAGE* LANE AND NOT A HAMLET LANE - the GM, 2026-08-29: "I have been
            // referring to hamlet lanes as village lanes specifically for this reason because they are presumed
            // to lead into the main village when not otherwise stated." The rule is in the `why` where a reader
            // needs it; the naming rationale is project process and stays here (settlement-review, 2026-08-29).
            Kind {
                class: "VillageLane",
                key: "village lane",
            },
            // The GM's ruling: a farm-ditch crossing is laid over water 2 ft wide or more.
            Kind {
                class: "Footbridge",
                key: "footbridge",
            },
            Kind {
                class: "Well",
                key: "well",
            },
            Kind {
                class: "NoticeBoard",
                key: "notice board",
            },
        ],
    },
    Family {
        module: "dikepond",
        kinds: &[
            // ---- the dike-pond hamlet (feature 150, Kuwabata - the first scripted mulberry_dike_fishpond) ----
            Kind {
                class: "FishPond",
                key: "fish pond",
            },
            // The GM's ruling: the mulberry crowns keep the premodern (late-Qing) spacing, about one bush per 24 sq ft.
            Kind {
                class: "MulberryDike",
                key: "mulberry dike",
            },
            Kind {
                class: "PondCanal",
                key: "pond canal",
            },
            Kind {
                class: "FruitDike",
                key: "fruit dike",
            },
            Kind {
                class: "TeaDike",
                key: "tea dike",
            },
            Kind {
                class: "PigSty",
                key: "pig sty",
            },
            Kind {
                class: "FryPond",
                key: "fry pond",
            },
            Kind {
                class: "ManurePit",
                key: "manure pit",
            },
            Kind {
                class: "SluiceGate",
                key: "sluice gate",
            },
            Kind {
                class: "PerimeterDike",
                key: "perimeter dike",
            },
        ],
    },
];

/// The sheet registry's families, in the order its registry lists them.
pub const SHEET: [Family; 5] = [
    Family {
        module: "grounds",
        kinds: &[
            Kind {
                class: "OuterCourt",
                key: "outer court",
            },
            Kind {
                class: "InnerCourt",
                key: "inner court",
            },
            Kind {
                class: "BorderCourt",
                key: "border court",
            },
            Kind {
                class: "HearingCourt",
                key: "hearing court",
            },
            Kind {
                class: "PracticeGround",
                key: "practice ground",
            },
            Kind {
                class: "CompoundGarden",
                key: "garden",
            },
            Kind {
                class: "RearYard",
                key: "rear yard",
            },
            Kind {
                class: "VegetableGarden",
                key: "vegetable garden",
            },
            Kind {
                class: "ShrineGrove",
                key: "shrine grove",
            },
            // The GM's ruling: the compound wall is drawn 3 ft thick, the heavier of the two real forms.
            Kind {
                class: "CompoundWall",
                key: "compound wall",
            },
            Kind {
                class: "MainGate",
                key: "main gate",
            },
            Kind {
                class: "SideGate",
                key: "side gate",
            },
            Kind {
                class: "CourtDivider",
                key: "court divider",
            },
            Kind {
                class: "ApproachRoad",
                key: "road",
            },
            Kind {
                class: "CartYard",
                key: "cart yard",
            },
            // ---- the parts of the grounds (feature 264: a thing drawn inside a feature is its own kind) --------------------
            Kind {
                class: "GardenPond",
                key: "garden pond",
            },
            Kind {
                class: "StoneLantern",
                key: "stone lantern",
            },
            Kind {
                class: "GardenPines",
                key: "garden pines",
            },
            Kind {
                class: "StrikingPosts",
                key: "striking posts",
            },
            Kind {
                class: "WeaponRack",
                key: "weapon rack",
            },
            Kind {
                class: "Nakamon",
                key: "nakamon",
            },
            Kind {
                class: "Door",
                key: "door",
            },
        ],
    },
    Family {
        module: "office",
        kinds: &[
            Kind {
                class: "OfficeHall",
                key: "office hall",
            },
            Kind {
                class: "MagistratesDais",
                key: "magistrate's dais",
            },
            Kind {
                class: "ClerksRoom",
                key: "clerks' room",
            },
            Kind {
                class: "TaxArchive",
                key: "tax archive",
            },
            Kind {
                class: "Granary",
                key: "granary",
            },
            Kind {
                class: "Cell",
                key: "cell",
            },
            Kind {
                class: "Gatehouse",
                key: "gatehouse",
            },
            Kind {
                class: "Barracks",
                key: "barracks",
            },
            Kind {
                class: "BenchNoticeBoard",
                key: "notice board",
            },
            Kind {
                class: "TallyOffice",
                key: "tally office",
            },
            Kind {
                class: "WeighingFloor",
                key: "weighing floor",
            },
            // ---- the parts of the office (feature 264: a thing drawn inside a feature is its own kind) ----------------------
            Kind {
                class: "Armory",
                key: "armory",
            },
            Kind {
                class: "DayOffice",
                key: "day office",
            },
            Kind {
                class: "OfficialStudy",
                key: "official study",
            },
            Kind {
                class: "ClerksSeats",
                key: "clerks' seats",
            },
            Kind {
                class: "KneelingPositions",
                key: "kneeling positions",
            },
            Kind {
                class: "GranaryStilts",
                key: "granary stilts",
            },
        ],
    },
    Family {
        module: "household",
        kinds: &[
            Kind {
                class: "Residence",
                key: "residence",
            },
            Kind {
                class: "AncestralAlcove",
                key: "ancestral alcove",
            },
            Kind {
                class: "KarosHouse",
                key: "karo's house",
            },
            Kind {
                class: "RetainersQuarters",
                key: "retainers' quarters",
            },
            Kind {
                class: "ServantsQuarters",
                key: "servants' quarters",
            },
            Kind {
                class: "GuestQuarters",
                key: "guest quarters",
            },
            Kind {
                class: "Kitchen",
                key: "kitchen",
            },
            Kind {
                class: "Bath",
                key: "bath",
            },
            Kind {
                class: "Well",
                key: "well",
            },
            Kind {
                class: "Latrine",
                key: "latrine",
            },
            Kind {
                class: "Stables",
                key: "stables",
            },
            Kind {
                class: "Kennel",
                key: "kennel",
            },
            Kind {
                class: "Storehouse",
                key: "storehouse",
            },
            Kind {
                class: "FireWaterTubs",
                key: "fire-water tubs",
            },
            Kind {
                class: "CompoundShrine",
                key: "compound shrine",
            },
            Kind {
                class: "WritingPavilion",
                key: "writing pavilion",
            },
            // ---- the parts of the household's buildings (feature 264: a thing drawn inside a feature is its own kind) -------
            Kind {
                class: "Hearth",
                key: "hearth",
            },
            Kind {
                class: "Genkan",
                key: "genkan",
            },
            Kind {
                class: "Engawa",
                key: "engawa",
            },
            Kind {
                class: "ResidenceCorridor",
                key: "residence corridor",
            },
            Kind {
                class: "LordsQuarters",
                key: "lord's quarters",
            },
            Kind {
                class: "FamilyQuarters",
                key: "family quarters",
            },
            Kind {
                class: "InnerRooms",
                key: "inner rooms",
            },
            Kind {
                class: "ReceptionRoom",
                key: "reception room",
            },
            Kind {
                class: "ShutteredWing",
                key: "shuttered wing",
            },
            Kind {
                class: "ShrineAltar",
                key: "shrine altar",
            },
            // The GM's ruling of 2026-09-27: a village shrine's innermost arch stands 12 ft from its hall where there is room.
            Kind {
                class: "Torii",
                key: "torii",
            },
        ],
    },
    Family {
        module: "particulars",
        kinds: &[
            // The GM's rulings: a flanking pair of stones, one each side of the road, where canon sets one; and Ochiba's pair
            // drawn larger than canon's two-fist stones (about 3.3 by 4.7 ft), because Ochiba makes and paints them.
            Kind {
                class: "ThresholdStones",
                key: "threshold stones",
            },
            Kind {
                class: "CinnabarWorkshop",
                key: "cinnabar workshop",
            },
            Kind {
                class: "River",
                key: "river",
            },
            Kind {
                class: "RiverLanding",
                key: "river landing",
            },
            Kind {
                class: "FoxBorder",
                key: "fox border",
            },
            // The GM's ruling: the door which receives the Kitsune is the border, so the parley room is built across it.
            Kind {
                class: "ParleyRoom",
                key: "parley room",
            },
            Kind {
                class: "BoundaryStones",
                key: "boundary stones",
            },
            Kind {
                class: "CharcoalStore",
                key: "charcoal store",
            },
            Kind {
                class: "WoodKamiAltar",
                key: "wood-kami altar",
            },
            // ---- the parts of the particulars (feature 264: a thing drawn inside a feature is its own kind) ----------------
            Kind {
                class: "Revetment",
                key: "revetment",
            },
            Kind {
                class: "Dock",
                key: "dock",
            },
            Kind {
                class: "TaxBarge",
                key: "tax barge",
            },
            Kind {
                class: "BoatmensAltar",
                key: "boatmen's altar",
            },
            Kind {
                class: "RiverWatch",
                key: "river watch",
            },
            Kind {
                class: "Steelyard",
                key: "steelyard",
            },
            Kind {
                class: "CharcoalBales",
                key: "charcoal bales",
            },
            Kind {
                class: "ParleyMats",
                key: "parley mats",
            },
            Kind {
                class: "DryingStonesAndBowls",
                key: "drying stones and bowls",
            },
        ],
    },
    Family {
        module: "shrine",
        kinds: &[
            // The GM's ruling: one roof over the hall and the dwelling is the setting's form for its country shrines.
            Kind {
                class: "HallAndDwelling",
                key: "hall and dwelling",
            },
            Kind {
                class: "Sanctuary",
                key: "sanctuary",
            },
            Kind {
                class: "MonksRooms",
                key: "the monk's rooms",
            },
            Kind {
                class: "WritingRoom",
                key: "writing room",
            },
            // The GM's rulings: the number of arches along the approach and their pitch.
            Kind {
                class: "ShrineApproach",
                key: "approach",
            },
            Kind {
                class: "ShrineBasin",
                key: "basin",
            },
            Kind {
                class: "SacredTree",
                key: "sacred tree",
            },
            Kind {
                class: "SweptClearing",
                key: "precinct clearing",
            },
            Kind {
                class: "Footpath",
                key: "footpath",
            },
            Kind {
                class: "GuardianFigures",
                key: "guardian figures",
            },
            Kind {
                class: "StoneLanterns",
                key: "lanterns",
            },
            Kind {
                class: "StrengthStones",
                key: "strength stones",
            },
            Kind {
                class: "FarmersStage",
                key: "stage",
            },
            Kind {
                class: "SumoRing",
                key: "sumo ring",
            },
            Kind {
                class: "BellTower",
                key: "bell tower",
            },
            Kind {
                class: "ShrineBurialGround",
                key: "burial ground",
            },
        ],
    },
];

#[cfg(test)]
mod tests;
