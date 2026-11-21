//! A side's outputs made comparable, and two sides compared (feature 449 T161).
//!
//! WHY A SIDE IS KEPT NORMALIZED: a kept old side is compared against a new side run in another directory on a later day, so what is
//! kept is the comparable form - the world's path replaced by `<WORLD>` at capture, each named normalization applied, the ones that
//! changed something recorded as taken. The normalizations are in both keys, so a changed normalization reruns both sides.

use std::collections::{BTreeMap, BTreeSet};

use fancy_regex::Regex;
use l7r_gate_core::difflib::unified_diff;
use l7r_shared::sha256::hex;
use serde_json::{json, Value};

use crate::cases::{Kind, Norm, Target};
use crate::run::Raw;

/// One side's comparable outputs.
#[derive(Clone, Debug, PartialEq)]
pub struct Kept {
    /// Each compared step: exit, stdout, stderr.
    pub steps: Vec<(i32, String, String)>,
    /// Each changed file or extra by its normalized name: its normalized text, `<deleted>`, or `<bytes N sha>` / `<text N sha>`.
    pub files: BTreeMap<String, String>,
    pub taken: BTreeSet<String>,
    pub took_s: f64,
}

impl Kept {
    #[must_use]
    pub fn to_json(&self) -> Value {
        json!({"steps": self.steps, "files": self.files, "taken": self.taken, "took_s": self.took_s})
    }

    /// A kept result read back; `None` when it is not one (an older or a hand-edited file: run it again).
    #[must_use]
    pub fn from_json(v: &Value) -> Option<Self> {
        Some(Self {
            steps: serde_json::from_value(v.get("steps")?.clone()).ok()?,
            files: serde_json::from_value(v.get("files")?.clone()).ok()?,
            taken: serde_json::from_value(v.get("taken")?.clone()).ok()?,
            took_s: v.get("took_s")?.as_f64()?,
        })
    }
}

fn short(bytes: &[u8]) -> String {
    hex(bytes)[..16].to_owned()
}

/// `text` with the world's path replaced and each normalization that applies to `target` (and to `file`, where one is scoped to files)
/// applied in order; those that changed something are added to `taken`.
fn apply(
    text: &str,
    target: Target,
    file: Option<&str>,
    norms: &[&Norm],
    world: &str,
    taken: &mut BTreeSet<String>,
) -> String {
    let mut t = text.to_owned();
    if !world.is_empty() && t.contains(world) {
        taken.insert("world-path".to_owned());
        t = t.replace(world, "<WORLD>");
    }
    for n in norms {
        if !n.on.contains(&target) {
            continue;
        }
        if let Some(only) = &n.only_files {
            // a normalization scoped to files applies to no step output, and to a file only where its name matches
            if !file.is_some_and(|f| only.is_match(f).unwrap_or(false)) {
                continue;
            }
        }
        let next = match &n.kind {
            Kind::Replace(re, with) => re.replace_all(&t, with.as_str()).into_owned(),
            Kind::Sort(sep) => sorted(&t, sep),
        };
        if next != t {
            taken.insert(n.name.clone());
            t = next;
        }
    }
    t
}

/// The pieces of `text` between `sep`'s matches, sorted, joined by the first separator found.
pub(crate) fn sorted(text: &str, sep: &Regex) -> String {
    let mut pieces = Vec::new();
    let (mut at, mut joint) = (0, None);
    for m in sep.find_iter(text).map_while(Result::ok) {
        if m.end() == m.start() {
            continue;
        }
        pieces.push(&text[at..m.start()]);
        joint.get_or_insert(m.as_str());
        at = m.end();
    }
    pieces.push(&text[at..]);
    pieces.sort_unstable();
    pieces.join(joint.unwrap_or(""))
}

/// A raw side made comparable.
#[must_use]
pub fn kept(raw: &Raw, norms: &[&Norm], max_text: usize) -> Kept {
    let world = raw.world.display().to_string();
    let mut taken = BTreeSet::new();
    let steps = raw
        .steps
        .iter()
        .map(|s| {
            (
                s.exit,
                apply(&s.stdout, Target::Stdout, None, norms, &world, &mut taken),
                apply(&s.stderr, Target::Stderr, None, norms, &world, &mut taken),
            )
        })
        .collect();
    // names that meet after normalization (two captures of one URL whose directories differ only by their stamp) are told apart by
    // their order among the raw names, as T146's capture ranks were
    let mut named: BTreeMap<String, Vec<&String>> = BTreeMap::new();
    for raw_name in raw.delta.keys() {
        named
            .entry(apply(
                raw_name,
                Target::Names,
                Some(raw_name),
                norms,
                &world,
                &mut taken,
            ))
            .or_default()
            .push(raw_name);
    }
    let mut files = BTreeMap::new();
    for (name, raws) in named {
        if raws.len() > 1 {
            taken.insert("name-rank".to_owned());
        }
        for (i, raw_name) in raws.into_iter().enumerate() {
            let label = if i == 0 {
                name.clone()
            } else {
                format!("{name} #{}", i + 1)
            };
            let text = match &raw.delta[raw_name] {
                None => "<deleted>".to_owned(),
                Some(bytes) => match std::str::from_utf8(bytes) {
                    Err(_) => format!("<bytes {} {}>", bytes.len(), short(bytes)),
                    Ok(text) => {
                        let t = apply(
                            text,
                            Target::Files,
                            Some(raw_name),
                            norms,
                            &world,
                            &mut taken,
                        );
                        if t.len() > max_text {
                            format!("<text {} {}>", bytes.len(), short(t.as_bytes()))
                        } else {
                            t
                        }
                    }
                },
            };
            files.insert(label, text);
        }
    }
    Kept {
        steps,
        files,
        taken,
        took_s: (raw.took_s * 100.0).round() / 100.0,
    }
}

fn clip(text: &str, n: usize) -> String {
    let start = text.len().saturating_sub(n);
    let start = (start..=text.len())
        .find(|i| text.is_char_boundary(*i))
        .unwrap_or(text.len());
    text[start..].to_owned()
}

fn udiff(a: &str, b: &str, la: &str, lb: &str) -> String {
    let (a, b): (Vec<&str>, Vec<&str>) = (a.lines().collect(), b.lines().collect());
    unified_diff(&a, &b, la, lb, 1)
        .iter()
        .take(80)
        .map(|l| l.chars().take(400).collect::<String>())
        .collect::<Vec<_>>()
        .join("\n")
}

/// What differs between two sides' kept outputs, one entry a difference; empty when they are the same.
#[must_use]
pub fn compare(a: &Kept, b: &Kept, la: &str, lb: &str) -> Vec<String> {
    let mut diffs = Vec::new();
    if a.steps.len() != b.steps.len() {
        diffs.push(format!(
            "compared steps {} != {}",
            a.steps.len(),
            b.steps.len()
        ));
    }
    for (i, ((ac, ao, ae), (bc, bo, be))) in a.steps.iter().zip(&b.steps).enumerate() {
        if ac != bc {
            diffs.push(format!("step {i} exit {ac} != {bc}"));
        }
        for (what, x, y) in [("stdout", ao, bo), ("stderr", ae, be)] {
            if x != y {
                diffs.push(format!(
                    "step {i} {what}\n--{la}--\n{}\n--{lb}--\n{}",
                    clip(x, 3000),
                    clip(y, 3000)
                ));
            }
        }
    }
    let names: BTreeSet<&String> = a.files.keys().chain(b.files.keys()).collect();
    for name in names {
        let (x, y) = (a.files.get(name), b.files.get(name));
        if x != y {
            let (x, y) = (
                x.map_or("<absent>", String::as_str),
                y.map_or("<absent>", String::as_str),
            );
            diffs.push(format!("file {name}\n{}", udiff(x, y, la, lb)));
        }
    }
    diffs
}
