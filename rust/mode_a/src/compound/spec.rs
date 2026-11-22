//! A compound program, read from its spec file (feature 449 T152, `ask:449-phase4-slices`: one Rust sheet driver with a spec file per
//! map): `pool/<tier>/<map>/<map>.compound.json`, the envelope, the reserved court spine, the gates, the buildings in feet with their
//! walls, orders, rooms, bays and doors, the parts the program owes and the knobs it records. Feet throughout, y down, the origin on the
//! compound wall's centerline at the north-west corner; pixels are the emitter's alone.
//!
//! Research: the program read - NONE: the spec's values handed on as the program states them, deciding nothing about a building

use l7r_gate_research::Error;
use serde_json::{Map, Value};

/// A box in feet: `(x0, y0, x1, y1)`.
pub type Bx = (f64, f64, f64, f64);

/// The side a face looks out of, or the wall a building backs.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Face {
    /// North (up).
    N,
    /// South (down).
    S,
    /// East (right).
    E,
    /// West (left).
    W,
}

impl Face {
    /// The face's letter read: `N`, `S`, `E` or `W`.
    ///
    /// # Errors
    /// Any other letter.
    pub fn read(s: &str) -> Result<Self, Error> {
        match s {
            "N" => Ok(Self::N),
            "S" => Ok(Self::S),
            "E" => Ok(Self::E),
            "W" => Ok(Self::W),
            _ => Err(bad(&format!("a face is N, S, E or W, not {s:?}"))),
        }
    }

    /// The face across from this one.
    #[must_use]
    pub fn opposite(self) -> Self {
        match self {
            Self::N => Self::S,
            Self::S => Self::N,
            Self::E => Self::W,
            Self::W => Self::E,
        }
    }

    /// Whether the face runs along x (a north or south face).
    #[must_use]
    pub fn along_x(self) -> bool {
        matches!(self, Self::N | Self::S)
    }
}

/// The wall a building backs: one of the compound's four, or the divider between the courts.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Wall {
    /// A compound wall.
    Side(Face),
    /// The divider wall between the courts.
    Divider,
}

/// The court a thing stands in: the inner (residence, north of the divider) or the outer (office, at the gate).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Court {
    /// The residence court behind the divider.
    Inner,
    /// The office court at the main gate.
    Outer,
}

/// A reserved open ground of the court spine (or a named yard), filed before any building.
#[derive(Clone, Debug, PartialEq)]
pub struct Zone {
    /// Its kind (`garden`, `hearing court`, `practice ground`, `outer court`, ...).
    pub kind: String,
    /// Its caption, if it carries one.
    pub caption: Option<String>,
    /// Its ground.
    pub bx: Bx,
    /// A hearing court's floor: `white gravel` or `river cobbles`.
    pub floor: Option<String>,
}

/// A hearing court's floors, the knob's forms in the record's order.
///
/// Research: sand hearing court - research/questions/0099-the-hearing-court-shirasu.drawing.html: the roofed court's floor a knob, white gravel or cobbles from the local riverbed, each plan taking one
pub const FLOORS: [&str; 2] = ["white gravel", "river cobbles"];

/// A room, bay or band of a building, as an offset in the building's own frame (feet from its north-west corner).
#[derive(Clone, Debug, PartialEq)]
pub struct Room {
    /// Its kind.
    pub kind: String,
    /// Its caption, if any.
    pub caption: Option<String>,
    /// Its offset and size.
    pub bx: Bx,
    /// How it is drawn: `room`, `passage`, `engawa`, `dais` or `seat`.
    pub style: String,
}

/// A door as the program gives it: the face it opens through and where along that face (0 west or north end, 1 the other).
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct DoorSpec {
    /// The face.
    pub face: Face,
    /// The fraction along the face.
    pub at: f64,
    /// A formal entrance (genkan): the door opens through a porch built out from the face (the formal entrance form's knob).
    pub genkan: bool,
}

/// A building of the program.
#[derive(Clone, Debug, PartialEq)]
pub struct Building {
    /// Its name in the program.
    pub name: String,
    /// Its kind (`data-kind`).
    pub kind: String,
    /// Its caption.
    pub caption: String,
    /// Its palette role (`lord`, `service`, `plain`, `kura`, `takakura`, `shrine`, `cell`, `dark`).
    pub role: String,
    /// Its extent along x and along y.
    pub w: f64,
    /// Its extent along y.
    pub h: f64,
    /// Its court.
    pub court: Court,
    /// The wall it backs.
    pub wall: Wall,
    /// Its order in its tier (higher first).
    pub order: i64,
    /// Its rank: 1 against the wall, 2 behind the wall's rank-1 row (stores only).
    pub rank: u8,
    /// How far it stands in off its wall's band, past the clear ground every building keeps.
    pub inset: f64,
    /// The building it is an ell of.
    pub joins: Option<String>,
    /// The end of its host it joins, where the program names one.
    pub end: Option<Face>,
    /// Seated beside the main gate, nearest it first.
    pub beside_gate: bool,
    /// Where along its wall its search starts, nearest that point both ways (the program's start knob), where the program names one.
    pub near: Option<f64>,
    /// Its rooms.
    pub rooms: Vec<Room>,
    /// Its dwelling walls, as offsets along its long axis.
    pub bays: Vec<f64>,
    /// Its doors; empty takes the default.
    pub doors: Vec<DoorSpec>,
    /// A drawn interior by rule: `stables` or `cell`.
    pub interior: Option<String>,
}

/// A gate in the compound wall: its wall, the middle of its opening along the wall, its passage.
#[derive(Clone, Debug, PartialEq)]
pub struct Gate {
    /// `main gate` or `side gate`.
    pub kind: String,
    /// The wall it opens in.
    pub wall: Face,
    /// The middle of its opening along the wall (feet).
    pub at: f64,
    /// Its passage (feet).
    pub width: f64,
}

/// A knob the program records: its key, its attested forms and the form the sheet takes, re-rolled from the seed and held to it.
#[derive(Clone, Debug, PartialEq)]
pub struct Knob {
    /// The roll's key, after the sheet's name.
    pub key: String,
    /// The forms, in the record's order.
    pub options: Vec<String>,
    /// The form the program takes.
    pub value: String,
}

/// The parts the program owes, each seated by its rule against its anchor.
#[derive(Clone, Debug, PartialEq, Default)]
pub struct Parts {
    /// The bath's size (feet), seated on the kitchen's service side.
    pub bath: Option<(f64, f64)>,
    /// The wells by use: `kitchen`, `garden`, `stables`.
    pub wells: Vec<String>,
    /// The buildings an outer privy stands by, each against a service wall.
    pub privies: Vec<String>,
    /// The building the practice ground's weapon rack faces.
    pub rack_by: Option<String>,
    /// The striking posts.
    pub posts: usize,
    /// The no-genkan approach: a roji from the middle gate to the reception's shoe stone.
    pub roji: bool,
    /// The notice board outside the main gate.
    pub board: bool,
    /// The landform the water depth follows, where the notes record one.
    pub landform: Option<String>,
}

/// A whole compound program.
#[derive(Clone, Debug, PartialEq)]
pub struct Program {
    /// The sheet's name: its seed for every roll.
    pub name: String,
    /// The title and subtitle.
    pub title: String,
    /// The subtitle.
    pub subtitle: String,
    /// The envelope's width and depth and the divider's line (feet).
    pub w: f64,
    /// Its depth.
    pub h: f64,
    /// The divider's line.
    pub divider: f64,
    /// The gates in the compound wall, the main gate first.
    pub gates: Vec<Gate>,
    /// The middle gate's passage.
    pub middle_gate: f64,
    /// The spine and the named yards.
    pub zones: Vec<Zone>,
    /// The buildings.
    pub buildings: Vec<Building>,
    /// The parts.
    pub parts: Parts,
    /// The knobs recorded.
    pub knobs: Vec<Knob>,
}

fn bad(message: &str) -> Error {
    Error::new("ValueError", message.to_owned())
}

fn num(o: &Map<String, Value>, key: &str) -> Result<f64, Error> {
    o.get(key)
        .and_then(Value::as_f64)
        .ok_or_else(|| bad(&format!("the spec's {key:?} is no number")))
}

fn num_or(o: &Map<String, Value>, key: &str, or: f64) -> Result<f64, Error> {
    if o.contains_key(key) {
        num(o, key)
    } else {
        Ok(or)
    }
}

fn text(o: &Map<String, Value>, key: &str) -> Result<String, Error> {
    o.get(key)
        .and_then(Value::as_str)
        .map(str::to_owned)
        .ok_or_else(|| bad(&format!("the spec's {key:?} is no string")))
}

fn opt_text(o: &Map<String, Value>, key: &str) -> Option<String> {
    o.get(key).and_then(Value::as_str).map(str::to_owned)
}

fn obj<'v>(v: &'v Value, what: &str) -> Result<&'v Map<String, Value>, Error> {
    v.as_object()
        .ok_or_else(|| bad(&format!("the spec's {what} is no object")))
}

fn list<'v>(o: &'v Map<String, Value>, key: &str) -> &'v [Value] {
    o.get(key)
        .and_then(Value::as_array)
        .map_or(&[], Vec::as_slice)
}

fn bx(o: &Map<String, Value>) -> Result<Bx, Error> {
    let (x, y) = (num(o, "x")?, num(o, "y")?);
    Ok((x, y, x + num(o, "w")?, y + num(o, "h")?))
}

fn court(s: &str) -> Result<Court, Error> {
    match s {
        "inner" => Ok(Court::Inner),
        "outer" => Ok(Court::Outer),
        _ => Err(bad(&format!("a court is inner or outer, not {s:?}"))),
    }
}

fn wall(s: &str) -> Result<Wall, Error> {
    if s == "divider" {
        Ok(Wall::Divider)
    } else {
        Face::read(s).map(Wall::Side)
    }
}

fn room(v: &Value) -> Result<Room, Error> {
    let o = obj(v, "room")?;
    Ok(Room {
        kind: text(o, "kind")?,
        caption: opt_text(o, "caption"),
        bx: bx(o)?,
        style: opt_text(o, "style").unwrap_or_else(|| "room".to_owned()),
    })
}

fn building(v: &Value) -> Result<Building, Error> {
    let o = obj(v, "building")?;
    let name = text(o, "name")?;
    let doors = list(o, "doors")
        .iter()
        .map(|d| {
            let d = obj(d, "door")?;
            Ok(DoorSpec {
                face: Face::read(&text(d, "face")?)?,
                at: num(d, "at")?,
                genkan: d.get("genkan").and_then(Value::as_bool).unwrap_or(false),
            })
        })
        .collect::<Result<Vec<_>, Error>>()?;
    let bays = list(o, "bays")
        .iter()
        .map(|b| b.as_f64().ok_or_else(|| bad("a bay is a number")))
        .collect::<Result<Vec<_>, Error>>()?;
    Ok(Building {
        kind: text(o, "kind")?,
        caption: opt_text(o, "caption").unwrap_or_else(|| name.clone()),
        role: text(o, "role")?,
        w: num(o, "w")?,
        h: num(o, "h")?,
        court: court(&text(o, "court")?)?,
        wall: wall(&text(o, "wall")?)?,
        order: o.get("order").and_then(Value::as_i64).unwrap_or(0),
        rank: if o.get("rank").and_then(Value::as_u64) == Some(2) {
            2
        } else {
            1
        },
        inset: num_or(o, "inset", 0.0)?,
        joins: opt_text(o, "joins"),
        end: opt_text(o, "end").map(|e| Face::read(&e)).transpose()?,
        beside_gate: o.get("beside").and_then(Value::as_str) == Some("main gate"),
        near: o.get("near").and_then(Value::as_f64),
        rooms: list(o, "rooms")
            .iter()
            .map(room)
            .collect::<Result<_, _>>()?,
        bays,
        doors,
        interior: opt_text(o, "interior"),
        name,
    })
}

fn gate(v: &Value) -> Result<Gate, Error> {
    let o = obj(v, "gate")?;
    Ok(Gate {
        kind: text(o, "kind")?,
        wall: Face::read(&text(o, "wall")?)?,
        at: num(o, "at")?,
        width: num(o, "width")?,
    })
}

fn strings(o: &Map<String, Value>, key: &str) -> Vec<String> {
    list(o, key)
        .iter()
        .filter_map(Value::as_str)
        .map(str::to_owned)
        .collect()
}

fn parts(v: Option<&Value>) -> Result<Parts, Error> {
    let Some(v) = v else {
        return Ok(Parts::default());
    };
    let o = obj(v, "parts")?;
    let bath = match o.get("bath") {
        Some(b) => {
            let b = obj(b, "bath")?;
            Some((num(b, "w")?, num(b, "h")?))
        }
        None => None,
    };
    Ok(Parts {
        bath,
        wells: strings(o, "wells"),
        privies: strings(o, "privies"),
        rack_by: opt_text(o, "rack_by"),
        posts: o
            .get("posts")
            .and_then(Value::as_u64)
            .and_then(|n| usize::try_from(n).ok())
            .unwrap_or(0),
        roji: o.get("roji").and_then(Value::as_bool).unwrap_or(false),
        board: o.get("board").and_then(Value::as_bool).unwrap_or(false),
        landform: opt_text(o, "landform"),
    })
}

fn knob(v: &Value) -> Result<Knob, Error> {
    let o = obj(v, "knob")?;
    Ok(Knob {
        key: text(o, "key")?,
        options: strings(o, "options"),
        value: text(o, "value")?,
    })
}

/// A program read from its spec's text.
///
/// # Errors
/// Text that is not JSON, or a field of the wrong form (`ValueError`, naming it).
///
/// Research:
///     the program read - NONE: the spec's values handed on as the program states them
///     divider gate width - GUESS: searched, the record silent (feature 417 T36 pass P4, 2026-10-25); the middle gate's passage 6 ft where the program names none, as docs/building-programs.md draws a household door
pub fn read(src: &str) -> Result<Program, Error> {
    let v: Value = serde_json::from_str(src)
        .map_err(|e| Error::new("json.decoder.JSONDecodeError", e.to_string()))?;
    let o = obj(&v, "program")?;
    let env = obj(o.get("envelope").unwrap_or(&Value::Null), "envelope")?;
    let zones = list(o, "zones")
        .iter()
        .map(|z| {
            let z = obj(z, "zone")?;
            let kind = text(z, "kind")?;
            let floor = opt_text(z, "floor");
            if kind == "hearing court" && !floor.as_deref().is_some_and(|f| FLOORS.contains(&f)) {
                return Err(bad("a hearing court's floor is a knob each plan takes: white gravel or river cobbles"));
            }
            Ok(Zone {
                kind,
                caption: opt_text(z, "caption"),
                bx: bx(z)?,
                floor,
            })
        })
        .collect::<Result<Vec<_>, Error>>()?;
    let gates = list(o, "gates")
        .iter()
        .map(gate)
        .collect::<Result<Vec<_>, _>>()?;
    if gates.first().is_none_or(|g| g.kind != "main gate") {
        return Err(bad("the spec's first gate is the main gate"));
    }
    Ok(Program {
        name: text(o, "name")?,
        title: text(o, "title")?,
        subtitle: opt_text(o, "subtitle").unwrap_or_default(),
        w: num(env, "w")?,
        h: num(env, "h")?,
        divider: num(env, "divider")?,
        gates,
        middle_gate: num_or(o, "middle_gate", 6.0)?,
        zones,
        buildings: list(o, "buildings")
            .iter()
            .map(building)
            .collect::<Result<_, _>>()?,
        parts: parts(o.get("parts"))?,
        knobs: list(o, "knobs")
            .iter()
            .map(knob)
            .collect::<Result<_, _>>()?,
    })
}
