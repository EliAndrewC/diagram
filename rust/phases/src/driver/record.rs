//! The rolled hamlet's record as JSON (feature 444 T42): the plan, the rolled forms, the stages run and refused, each field's
//! outline and plots, the grain and the counted work.
//!
//! Research:
//!     the record - NONE: the driver's output, written from what the stages laid

use std::collections::BTreeMap;
use std::fmt::Write as _;

use super::Rolled;

pub(super) fn js(s: &str) -> String {
    let mut o = String::from("\"");
    for c in s.chars() {
        match c {
            '"' => o.push_str("\\\""),
            '\\' => o.push_str("\\\\"),
            '\n' => o.push_str("\\n"),
            c => o.push(c),
        }
    }
    o.push('"');
    o
}

fn ring_js(ring: &[(f64, f64)]) -> String {
    let mut o = String::from("[");
    for (i, (x, y)) in ring.iter().enumerate() {
        let _ = write!(o, "{}[{:.1},{:.1}]", if i == 0 { "" } else { "," }, x, y);
    }
    o.push(']');
    o
}

/// The hamlet's record as JSON: the plan, the rolled forms, the stages run, each field's outline and plots, and the counted work.
#[must_use]
pub fn manifest(r: &Rolled) -> String {
    let p = &r.plan;
    let mut o = String::new();
    let _ = write!(
        o,
        "{{\n \"name\": {},\n \"seed\": {},\n \"households\": {},\n \"generated_by\": \"rust/phases driver (feature 444 T42)\",\n \"stages\": [{}],\n \"down_deg\": {},\n \"water_flow\": {},\n \"windward\": {},\n \"field_archetype\": {},\n \"canvas\": [{}, {}],\n",
        js(&p.name),
        p.seed,
        p.households,
        r.stages.iter().map(|s| js(s)).collect::<Vec<_>>().join(", "),
        p.down_deg,
        p.water_flow,
        js(&p.windward),
        js(&p.archetype),
        p.w,
        p.h
    );
    let knobs: BTreeMap<&String, &String> = p.rolled.iter().chain(r.knobs.iter()).collect();
    let _ = writeln!(
        o,
        " \"knobs\": {{{}}},",
        knobs
            .iter()
            .map(|(k, v)| format!("{}: {}", js(k), js(v)))
            .collect::<Vec<_>>()
            .join(", ")
    );
    o.push_str(" \"fields\": [\n");
    for (i, (f, b)) in r.fields.iter().zip(&r.brooks).enumerate() {
        let states: Vec<String> = f
            .states
            .iter()
            .map(|s| js(&format!("{s:?}").to_lowercase()))
            .collect();
        let _ = writeln!(
            o,
            "  {{\"name\": {}, \"outline\": {}, \"brook\": {}, \"plots\": [{}], \"states\": [{}], \"channels\": [{}]}}{}",
            js(&format!("{}-paddies-{}", p.name, i + 1)),
            ring_js(&f.fan.ring),
            ring_js(b),
            f.basins.iter().map(|x| ring_js(&x.ring)).collect::<Vec<_>>().join(","),
            states.join(","),
            f.channels.iter().map(|c| format!("{{\"role\": {}, \"w\": {:.2}, \"w_tail\": {:.2}, \"pts\": {}}}", js(c.role), c.w, c.w_tail, ring_js(&c.pts))).collect::<Vec<_>>().join(","),
            if i + 1 < r.fields.len() { "," } else { "" }
        );
    }
    o.push_str(" ],\n");
    let dry: Vec<String> = r
        .dry
        .iter()
        .map(|d| {
            format!(
                "{{\"crop\": {}, \"tract\": {}, \"theta\": {:.4}, \"poly\": {}}}",
                js(d.crop),
                d.tract,
                d.theta,
                ring_js(&d.poly)
            )
        })
        .collect();
    let _ = writeln!(o, " \"dry_plots\": [{}],", dry.join(","));
    let field_grain = r.field_grain.map_or_else(
        || "null".to_owned(),
        |(drawn, need, room)| {
            format!("{{\"drawn\": {drawn:.2}, \"need\": {need:.2}, \"room\": {room:.2}}}")
        },
    );
    let hem_grain = r.grain.map_or_else(
        || "null".to_owned(),
        |(drawn, room)| format!("{{\"drawn\": {drawn:.2}, \"room\": {room:.2}}}"),
    );
    let _ = writeln!(
        o,
        " \"grain_acres\": {{\"field\": {field_grain}, \"hem\": {hem_grain}}},"
    );
    let _ = writeln!(
        o,
        " \"refusals\": [{}],",
        r.refusals
            .iter()
            .map(|s| js(s))
            .collect::<Vec<_>>()
            .join(", ")
    );
    let counts: BTreeMap<&String, &u64> = r.counts.iter().collect();
    let _ = writeln!(
        o,
        " \"counts\": {{{}}}\n}}",
        counts
            .iter()
            .map(|(k, v)| format!("{}: {}", js(k), v))
            .collect::<Vec<_>>()
            .join(", ")
    );
    o
}
