//! A pool hamlet's spec, read from its `<name>.spec.json` (feature 444 T42, plan D5): the fields the deleted `HamletSpec` took
//! that the stages through the cut read, nothing else.
//!
//! Research:
//!     the spec - NONE: the driver's input, each value the GM's or the pool map's own

use std::collections::BTreeMap;

/// One value of the spec's flat JSON: a string, a number, null, or (for `pins`) an object of strings.
#[derive(Debug, Clone, PartialEq)]
pub enum Value {
    Str(String),
    Num(f64),
    Null,
    Obj(BTreeMap<String, String>),
}

/// The spec.
///
/// Research:
///     the spec - NONE: the record's type
#[derive(Debug, Clone, Default)]
pub struct Spec {
    pub name: String,
    pub seed: i64,
    pub households: u32,
    pub down_deg: Option<f64>,
    pub windward: Option<String>,
    pub water_sink: Option<String>,
    pub settlement_form: Option<String>,
    pub field_archetype: Option<String>,
    pub pond_layout: Option<String>,
    pub dike_crop: Option<String>,
    pub leftover: Option<String>,
    pub intake: Option<String>,
    pub brook_side: Option<i64>,
    pub pins: BTreeMap<String, String>,
}

/// Why a spec could not be read.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SpecError(pub String);

impl std::fmt::Display for SpecError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "spec: {}", self.0)
    }
}

struct Reader<'a> {
    s: &'a [u8],
    i: usize,
}

impl Reader<'_> {
    fn ws(&mut self) {
        while self.i < self.s.len() && self.s[self.i].is_ascii_whitespace() {
            self.i += 1;
        }
    }

    fn eat(&mut self, c: u8) -> Result<(), SpecError> {
        self.ws();
        if self.s.get(self.i) == Some(&c) {
            self.i += 1;
            Ok(())
        } else {
            Err(SpecError(format!(
                "expected `{}` at byte {}",
                c as char, self.i
            )))
        }
    }

    fn string(&mut self) -> Result<String, SpecError> {
        self.eat(b'"')?;
        let mut out = Vec::new();
        while let Some(&c) = self.s.get(self.i) {
            self.i += 1;
            match c {
                // the text is UTF-8 already and an escape keeps its bytes whole, so the string is too
                b'"' => return Ok(String::from_utf8_lossy(&out).into_owned()),
                b'\\' => {
                    let e = *self
                        .s
                        .get(self.i)
                        .ok_or_else(|| SpecError("an escape at the end".into()))?;
                    self.i += 1;
                    out.push(match e {
                        b'n' => b'\n',
                        b't' => b'\t',
                        other => other,
                    });
                }
                _ => out.push(c),
            }
        }
        Err(SpecError("an unterminated string".into()))
    }

    fn value(&mut self) -> Result<Value, SpecError> {
        self.ws();
        match self.s.get(self.i) {
            Some(b'"') => Ok(Value::Str(self.string()?)),
            Some(b'{') => {
                let mut m = BTreeMap::new();
                self.eat(b'{')?;
                self.ws();
                if self.s.get(self.i) == Some(&b'}') {
                    self.i += 1;
                    return Ok(Value::Obj(m));
                }
                loop {
                    let k = self.string()?;
                    self.eat(b':')?;
                    let Value::Str(v) = self.value()? else {
                        return Err(SpecError(format!("`{k}` in an object is not a string")));
                    };
                    m.insert(k, v);
                    self.ws();
                    if self.s.get(self.i) == Some(&b',') {
                        self.i += 1;
                    } else {
                        self.eat(b'}')?;
                        return Ok(Value::Obj(m));
                    }
                }
            }
            Some(b'n') if self.s[self.i..].starts_with(b"null") => {
                self.i += 4;
                Ok(Value::Null)
            }
            _ => {
                let start = self.i;
                while self.i < self.s.len()
                    && matches!(
                        self.s[self.i],
                        b'-' | b'+' | b'.' | b'e' | b'E' | b'0'..=b'9'
                    )
                {
                    self.i += 1;
                }
                std::str::from_utf8(&self.s[start..self.i])
                    .ok()
                    .and_then(|t| t.parse().ok())
                    .map(Value::Num)
                    .ok_or_else(|| SpecError(format!("not a value at byte {start}")))
            }
        }
    }
}

/// Every key of a flat JSON object and its value.
///
/// # Errors
/// When the text is not a flat object of strings, numbers, nulls and string-valued objects.
pub fn object(text: &str) -> Result<BTreeMap<String, Value>, SpecError> {
    let mut r = Reader {
        s: text.as_bytes(),
        i: 0,
    };
    let mut out = BTreeMap::new();
    r.eat(b'{')?;
    r.ws();
    if r.s.get(r.i) == Some(&b'}') {
        return Ok(out);
    }
    loop {
        let k = r.string()?;
        r.eat(b':')?;
        out.insert(k, r.value()?);
        r.ws();
        if r.s.get(r.i) == Some(&b',') {
            r.i += 1;
        } else {
            r.eat(b'}')?;
            return Ok(out);
        }
    }
}

fn text(v: Option<&Value>) -> Option<String> {
    match v {
        Some(Value::Str(s)) => Some(s.clone()),
        _ => None,
    }
}

#[expect(
    clippy::cast_possible_truncation,
    reason = "a spec's integers are small: a seed, a household count, a flank"
)]
fn int(v: Option<&Value>) -> Option<i64> {
    match v {
        Some(Value::Num(n)) if n.fract() == 0.0 => Some(*n as i64),
        _ => None,
    }
}

/// The spec from its JSON text.
///
/// # Errors
/// When the text is not an object, or `name` or `seed` is missing, or `households` lies outside 10-20.
///
/// Research:
///     households at a hamlet's size - GUESS: the hamlet tier's ten to twenty households, the deleted `HamletSpec`'s bounds, 15 unless the spec says; no page sets the tier's bounds
pub fn parse(text_in: &str) -> Result<Spec, SpecError> {
    let o = object(text_in)?;
    let name = text(o.get("name")).ok_or_else(|| SpecError("`name` is required".into()))?;
    let seed =
        int(o.get("seed")).ok_or_else(|| SpecError("`seed` is required, an integer".into()))?;
    let households = u32::try_from(int(o.get("households")).unwrap_or(15))
        .map_err(|_| SpecError("`households` is negative".into()))?;
    if !(10..=20).contains(&households) {
        return Err(SpecError(format!(
            "`households` {households} is outside a hamlet's 10 to 20"
        )));
    }
    let down_deg = match o.get("down_deg") {
        Some(Value::Num(n)) => Some(*n),
        _ => None,
    };
    let pins = match o.get("pins") {
        Some(Value::Obj(m)) => m.clone(),
        _ => BTreeMap::new(),
    };
    Ok(Spec {
        name,
        seed,
        households,
        down_deg,
        windward: text(o.get("windward")),
        water_sink: text(o.get("water_sink")),
        settlement_form: text(o.get("settlement_form")),
        field_archetype: text(o.get("field_archetype")),
        pond_layout: text(o.get("pond_layout")),
        dike_crop: text(o.get("dike_crop")),
        leftover: text(o.get("leftover")),
        intake: text(o.get("intake")),
        brook_side: int(o.get("brook_side")),
        pins,
    })
}

#[cfg(test)]
mod tests {
    use super::{object, parse, Value};

    #[test]
    fn a_pool_spec_is_read_with_its_defaults() {
        let s = parse(r#"{"name": "Sawada", "seed": 24, "households": 19, "down_deg": 225, "water_sink": "offmap", "intake": "open", "pins": {"paddy_rest": "unsettled", "weir_form": "crib"}, "brook_side": -1}"#).unwrap();
        assert_eq!(
            (s.name.as_str(), s.seed, s.households, s.down_deg),
            ("Sawada", 24, 19, Some(225.0))
        );
        assert_eq!(
            s.pins.get("paddy_rest").map(String::as_str),
            Some("unsettled")
        );
        assert_eq!(
            (s.intake.as_deref(), s.brook_side, s.windward),
            (Some("open"), Some(-1), None)
        );
        let d = parse(r#"{"name": "x\"y", "seed": 4, "down_deg": null, "pins": {}}"#).unwrap();
        assert_eq!(
            (d.name.as_str(), d.households, d.down_deg),
            ("x\"y", 15, None)
        );
    }

    #[test]
    fn a_bad_spec_is_refused_naming_why() {
        for (t, why) in [
            (r#"{"seed": 4}"#, "name"),
            (r#"{"name": "a"}"#, "seed"),
            (r#"{"name": "a", "seed": 4, "households": 30}"#, "outside"),
            (
                r#"{"name": "a", "seed": 4, "pins": {"k": 3}}"#,
                "not a string",
            ),
            (r#"["a"]"#, "expected"),
            (r#"{"name": "a"#, "unterminated"),
            (r#"{"name": "a", "seed": x}"#, "not a value"),
        ] {
            let e = parse(t).unwrap_err().to_string();
            assert!(e.contains(why), "{t}: {e}");
        }
        assert_eq!(object("{}").unwrap().len(), 0);
        assert_eq!(
            object(r#"{"a": "\n\t\\"}"#).unwrap().get("a"),
            Some(&Value::Str("\n\t\\".into()))
        );
        assert!(object(r#"{"a": "\"#).is_err());
        assert!(parse(r#"{"name": "a", "seed": 4, "households": -3}"#).is_err());
    }
}
