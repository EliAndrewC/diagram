//! The check state as one hook call reads it (451 T490): every top-level key but the rows no hot call asks for. A Bash call under a
//! plan hold, its end, and an Agent call no check names parsed the whole 3.0 MB `checks-open.json` - `dispatches` 2.29 MB of it,
//! `versions` 0.51 MB - and read none of those rows, measured 2026-11-27. The rows are scanned and checked as JSON but not made
//! values; [`Part::whole`] parses them from the same text the moment a call reads them or saves, so every save writes the whole
//! state and every reader's answer is the whole parse's. A text the partial read cannot take (not JSON, not an object at the top, a
//! row that is not an object) is parsed whole at once, as `load` reads it.

use std::collections::HashMap;
use std::fmt;
use std::path::Path;

use serde::de::{DeserializeSeed, Deserializer, MapAccess, SeqAccess, Visitor};
use serde_json::{Map, Value};

use crate::checks::{falsy, parsed, text};

/// The top-level keys left unparsed until a call reads them: no `edit`, `after`, plain launch or return reads them.
const ROWS: [&str; 3] = ["dispatches", "versions", "seen"];

/// What `concerns` reads of one dispatch or hold: its agent, its state, whether its `wave` and `reply` are set (not `falsy`), and
/// its dispatch time `t` (a number, else 0), which bounds a wave row's wait (451 T505).
#[derive(Debug, Default, PartialEq)]
pub(super) struct Row {
    pub(super) aid: String,
    pub(super) state: String,
    pub(super) wave: bool,
    pub(super) reply: bool,
    pub(super) t: f64,
}

impl Row {
    /// A row read from its value, as `concerns` read it before 451 T490.
    pub(super) fn of(d: &Value) -> Self {
        Self {
            aid: text(d, "aid").to_owned(),
            state: text(d, "state").to_owned(),
            wave: !falsy(d.get("wave")),
            reply: !falsy(d.get("reply")),
            t: time_of(d.get("t")),
        }
    }
}

/// A row's `t` as `rounds::t_of` reads it: a number, else 0.
fn time_of(v: Option<&Value>) -> f64 {
    v.and_then(Value::as_f64).unwrap_or(0.0)
}

/// The state read in part.
pub(super) struct Part {
    text: String,
    value: Value,
    whole: bool,
    /// `dispatches`' rows as `concerns` reads them, where the read asked for them.
    pub(super) rows: HashMap<String, Row>,
}

#[cfg(test)]
thread_local! {
    /// Set by a test to read every state whole, the differential's other arm.
    pub(super) static WHOLE: std::cell::Cell<bool> = const { std::cell::Cell::new(false) };
}

impl Part {
    /// The state file at `path`, with `dispatches`' rows as `concerns` reads them where `rows` asks.
    pub(super) fn read(path: &Path, rows: bool) -> Self {
        Self::parse(std::fs::read_to_string(path).unwrap_or_default(), rows)
    }

    /// `text` read in part, or whole where the partial read cannot take it.
    pub(super) fn parse(text: String, rows: bool) -> Self {
        #[cfg(test)]
        let forced = WHOLE.with(std::cell::Cell::get);
        #[cfg(not(test))]
        let forced = false;
        let mut de = serde_json::Deserializer::from_str(&text);
        let light = Top { rows }
            .deserialize(&mut de)
            .and_then(|got| de.end().map(|()| got))
            .ok()
            .filter(|_| !forced);
        if let Some((value, rows)) = light {
            return Self {
                text,
                value: Value::Object(value),
                whole: false,
                rows,
            };
        }
        let value = parsed(&text);
        let rows = rows_of(&value).filter(|_| rows).unwrap_or_default();
        Self {
            text,
            value,
            whole: true,
            rows,
        }
    }

    /// The state as read: whole, or without [`ROWS`].
    pub(super) fn value(&self) -> &Value {
        &self.value
    }

    /// The state to change where the change reads no row.
    pub(super) fn value_mut(&mut self) -> &mut Value {
        &mut self.value
    }

    /// The whole state: [`ROWS`] parsed from the text now, where they were left. A call changes only the other keys before this, so
    /// the rows are the text's as they stand.
    pub(super) fn whole(&mut self) -> &mut Value {
        if !self.whole {
            self.whole = true;
            // a partial read's value is an object, and its text parsed as one (`parse` keeps it partial only then)
            let mut all = parsed(&self.text);
            let part = self
                .value
                .as_object_mut()
                .expect("a partial read's value is an object");
            for key in ROWS {
                if let Some(v) = all.get_mut(key).map(Value::take) {
                    part.insert(key.to_owned(), v);
                }
            }
        }
        &mut self.value
    }
}

/// `dispatches`' rows of a whole state, as [`Row::of`] reads each; None where it holds no object of them.
fn rows_of(value: &Value) -> Option<HashMap<String, Row>> {
    let rows = value.get("dispatches")?.as_object()?;
    Some(rows.iter().map(|(k, d)| (k.clone(), Row::of(d))).collect())
}

/// The top level: every key but [`ROWS`] as a value, and `dispatches`' rows where asked.
struct Top {
    rows: bool,
}

impl<'de> DeserializeSeed<'de> for Top {
    type Value = (Map<String, Value>, HashMap<String, Row>);
    fn deserialize<D: Deserializer<'de>>(self, d: D) -> Result<Self::Value, D::Error> {
        d.deserialize_map(self)
    }
}

impl<'de> Visitor<'de> for Top {
    type Value = (Map<String, Value>, HashMap<String, Row>);
    fn expecting(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.write_str("the check state")
    }
    fn visit_map<A: MapAccess<'de>>(self, mut m: A) -> Result<Self::Value, A::Error> {
        let (mut kept, mut rows) = (Map::new(), HashMap::new());
        while let Some(k) = m.next_key::<String>()? {
            if k == "dispatches" && self.rows {
                rows = m.next_value_seed(Rows)?;
            } else if ROWS.contains(&k.as_str()) {
                m.next_value_seed(Skip)?;
            } else {
                kept.insert(k, m.next_value()?);
            }
        }
        Ok((kept, rows))
    }
}

/// `dispatches`, each row read as [`Row`]; a later row of the same key replaces an earlier, as the whole parse keeps the last.
struct Rows;

impl<'de> DeserializeSeed<'de> for Rows {
    type Value = HashMap<String, Row>;
    fn deserialize<D: Deserializer<'de>>(self, d: D) -> Result<Self::Value, D::Error> {
        d.deserialize_map(self)
    }
}

impl<'de> Visitor<'de> for Rows {
    type Value = HashMap<String, Row>;
    fn expecting(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.write_str("the dispatches")
    }
    fn visit_map<A: MapAccess<'de>>(self, mut m: A) -> Result<Self::Value, A::Error> {
        let mut rows = HashMap::new();
        while let Some(k) = m.next_key::<String>()? {
            rows.insert(k, m.next_value_seed(OneRow)?);
        }
        Ok(rows)
    }
}

/// One dispatch: `aid`, `state` and `t` as values, `wave` and `reply` as their truth, every other field scanned.
struct OneRow;

impl<'de> DeserializeSeed<'de> for OneRow {
    type Value = Row;
    fn deserialize<D: Deserializer<'de>>(self, d: D) -> Result<Row, D::Error> {
        d.deserialize_map(self)
    }
}

impl<'de> Visitor<'de> for OneRow {
    type Value = Row;
    fn expecting(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.write_str("a dispatch")
    }
    fn visit_map<A: MapAccess<'de>>(self, mut m: A) -> Result<Row, A::Error> {
        let mut row = Row::default();
        while let Some(k) = m.next_key::<String>()? {
            match k.as_str() {
                "aid" => row.aid = text_of(m.next_value()?),
                "state" => row.state = text_of(m.next_value()?),
                "wave" => row.wave = m.next_value_seed(Skip)?,
                "reply" => row.reply = m.next_value_seed(Skip)?,
                "t" => row.t = time_of(Some(&m.next_value()?)),
                _ => {
                    m.next_value_seed(Skip)?;
                }
            }
        }
        Ok(row)
    }
}

/// A field as `text` reads it: its string, or "".
fn text_of(v: Value) -> String {
    match v {
        Value::String(s) => s,
        _ => String::new(),
    }
}

/// Any value scanned through `deserialize_any`, never made one, answering whether it is set (not `falsy`). Not `IgnoredAny`'s own
/// scan, which takes a number past f64 the whole parse refuses (451 T493's `1e400`): this one parses every token as `Value` does,
/// so a text it takes is one the whole parse takes. `IgnoredAny` in its place was measured and left (451 T506): -2.1 to 1.2 ms a
/// hook, inside the noise, on a copy of the clone's 2.6 MB state, 2026-11-27.
struct Skip;

impl<'de> DeserializeSeed<'de> for Skip {
    type Value = bool;
    fn deserialize<D: Deserializer<'de>>(self, d: D) -> Result<bool, D::Error> {
        d.deserialize_any(self)
    }
}

impl<'de> Visitor<'de> for Skip {
    type Value = bool;
    fn expecting(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.write_str("any JSON value")
    }
    fn visit_bool<E>(self, v: bool) -> Result<bool, E> {
        Ok(v)
    }
    fn visit_i64<E>(self, v: i64) -> Result<bool, E> {
        Ok(v != 0)
    }
    fn visit_u64<E>(self, v: u64) -> Result<bool, E> {
        Ok(v != 0)
    }
    fn visit_f64<E>(self, v: f64) -> Result<bool, E> {
        Ok(v != 0.0)
    }
    fn visit_str<E>(self, v: &str) -> Result<bool, E> {
        Ok(!v.is_empty())
    }
    fn visit_unit<E>(self) -> Result<bool, E> {
        Ok(false)
    }
    fn visit_seq<A: SeqAccess<'de>>(self, mut s: A) -> Result<bool, A::Error> {
        let mut set = false;
        while s.next_element_seed(Skip)?.is_some() {
            set = true;
        }
        Ok(set)
    }
    fn visit_map<A: MapAccess<'de>>(self, mut m: A) -> Result<bool, A::Error> {
        let mut set = false;
        while m.next_key_seed(Skip)?.is_some() {
            m.next_value_seed(Skip)?;
            set = true;
        }
        Ok(set)
    }
}

#[cfg(test)]
mod tests;
