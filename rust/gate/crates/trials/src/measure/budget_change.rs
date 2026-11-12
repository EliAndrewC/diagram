//! `make budget-set`, `budget-change`, `budget-accept`, `budget-program` - the one writer of `dev/work-budget.json`, the hamlet
//! roll's work budgets (feature 443 T03, plan D6), and of its log `dev/work-budget-changes.jsonl`; ported whole from
//! `scripts/budget_change.py` by feature 449 T134 (the round arbiter's `ask:449-phase3-remainder`), its refusals, its words and its
//! files unchanged. `measure work-budget --write` writes `dev/work-budget.md` and the run files, none of these.
//!
//! THE TABLE: `{"program": {"ops_at_40": <ops>|null, "exponent": <e>|null}, "stages": {"<stage>": {...}}}`, one stage per stage of the
//! roll (named as `make work-budget` names them). A stage is `unbudgeted`; `budgeted`, with `per_thing` (basic operations per thing
//! placed), `exponent` (its growth with households), `derivation` (the path of its first-principles derivation) and `verdict` (the
//! path of its `work-budget` MODE BUDGET verdict, whose first line is the verdict word); or `accepted`, which adds `accepted` (its
//! counted operations at 40 and 80 households - T04).
//!
//! THE RULES (443 FR-005; the GM's approval of the design, 2026-10-28): a FIRST budget is set only from a SOUND verdict (`set`; LOOSE or
//! UNDERIVED refuses); every later change, and the program's whole-roll budget, needs the GM's words (`change`, `program`, WORDS
//! checked against the session's transcript by `rust/guard/src/guards/budget_change_hooks.rs`, which a make target cannot do), and is
//! logged with them. The table is a guard file: an edit other than through these targets needs `GUARD_EDIT_OK`.
//!
//! THE LEEWAY AND THE RAISE (feature 444 amendment 7, the GM 2026-11-03: "I would frankly be okay with things that are 50% higher or
//! even twice as high in terms of the number of operations than what we have budgeted ... if we end up with some kind of n squared
//! algorithm, then even in Rust that will become a problem"): a budget is an estimate, so a stage is accepted at up to `LEEWAY` times
//! it on the work-budget agent's LEEWAY, and a budget is raised without his words on a SOUND re-derivation that names the work the
//! first one missed, to at most `RAISE_CAP` times its first figure at 40; neither touches the growth caps.

use std::path::{Path, PathBuf};

use serde_json::{Map, Value};

use l7r_gate_core::record::args::{parse_with, Spec};
use l7r_guard::shared::py_text::strip;
use l7r_guard::shared::pyjson::py_float;

use super::work_budget_bundle::{dumps_py, glob, loads, nonfinite, py_re, read, sizes, R, RUNS};

mod rules;

const TABLE: &str = "dev/work-budget.json";
const LOG: &str = "dev/work-budget-changes.jsonl";
const SOUND: &str = "SOUND";
/// Feature 444 D2: a budget is per thing x the derivation's own items at each size.
const ITEM_SIZES: [i64; 3] = [20, 40, 80];
/// FR-022 rule 1: a stage accepted at up to twice its budget, on the MODE AUDIT's LEEWAY (the GM 2026-11-03: "even twice as high").
const LEEWAY: f64 = 2.0;
/// FR-022 rule 2: a raise without the GM's words reaches at most ten times the first budget at 40 ("an order of magnitude").
const RAISE_CAP: f64 = 10.0;
/// FR-022 rule 2: the section a raising re-derivation counts its missed items under.
const MISSED: &str = "## Work the first derivation missed";
/// Rubric S6: a stage's exponent from 20 to 80 households, which allows n log n and no n squared.
const GROWTH_CAP: f64 = 1.15;
/// An accepted stage's measured exponent may sit this far above its budget's: seed noise between two sizes.
const GROWTH_SLACK: f64 = 0.05;
/// The sizes an accepted stage is held to (feature 443 T04; the push's ratchet).
const HELD: [i64; 2] = [40, 80];
/// The item counts `set` takes (10: a form at a bounded n, ask:444-polder-sizes) and `change` takes (20, 40, 80).
const ITEM_FLAGS: [&str; 4] = [
    "--items-at-10",
    "--items-at-20",
    "--items-at-40",
    "--items-at-80",
];

fn load(root: &Path) -> R<Map<String, Value>> {
    let path = root.join(TABLE);
    match loads(&read(&path)?).map_err(|e| format!("{}: {e}", path.display()))? {
        Value::Object(m) => Ok(m),
        _ => Err(format!("TypeError: {TABLE} is no mapping")),
    }
}

fn save(root: &Path, table: &Map<String, Value>) -> R<()> {
    let path = root.join(TABLE);
    super::work_budget_bundle::io(
        &path,
        std::fs::write(
            &path,
            dumps_py(&Value::Object(table.clone()), Some(1)) + "\n",
        ),
    )
}

fn log(root: &Path, row: Value) -> R<()> {
    use std::io::Write as _;
    let mut line = Map::new();
    line.insert(
        "date".to_owned(),
        Value::String(l7r_gate_core::record::bundle::today()),
    );
    if let Value::Object(m) = row {
        line.extend(m);
    }
    let path = root.join(LOG);
    let appended = std::fs::OpenOptions::new()
        .append(true)
        .create(true)
        .open(&path)
        .and_then(|mut f| f.write_all((dumps_py(&Value::Object(line), None) + "\n").as_bytes()));
    super::work_budget_bundle::io(&path, appended)
}

/// The verdict word a verdict file opens with ("" when it is unreadable or empty; a file that is no UTF-8 is the failure Python
/// raised).
fn verdict_of(path: &Path) -> R<String> {
    let text = match std::fs::read_to_string(path) {
        Ok(t) => t,
        Err(e) if e.kind() == std::io::ErrorKind::InvalidData => {
            return Err(format!("UnicodeDecodeError: {}", path.display()))
        }
        Err(_) => return Ok(String::new()),
    };
    let text = l7r_gate_core::record::repo::universal(&text);
    let first = l7r_guard::shared::speckit::splitlines(&text)
        .into_iter()
        .map(strip)
        .find(|l| !l.is_empty());
    Ok(first.map_or_else(String::new, |l| {
        let word = l7r_guard::shared::py_text::split(l)[0];
        word.trim_matches(['*', ':', '`']).to_uppercase()
    }))
}

/// `float(text)`: Python's whitespace around it, `_` between digits, `inf` and `nan` read.
fn py_float_text(text: &str) -> Option<f64> {
    underscored(strip(text))?.parse().ok()
}

/// `int(text)`: Python's whitespace around it, a sign, `_` between digits.
fn py_int_text(text: &str) -> Option<i64> {
    let t = underscored(strip(text))?;
    let digits = t.strip_prefix(['+', '-']).unwrap_or(&t);
    if digits.is_empty() || !digits.chars().all(|c| c.is_ascii_digit()) {
        return None;
    }
    t.parse().ok()
}

/// A number's text with each `_` between two digits dropped; none where an `_` stands anywhere else.
fn underscored(t: &str) -> Option<String> {
    let chars: Vec<char> = t.chars().collect();
    let mut out = String::with_capacity(t.len());
    for (i, c) in chars.iter().enumerate() {
        if *c == '_' {
            let ok = i > 0
                && chars[i - 1].is_ascii_digit()
                && chars.get(i + 1).is_some_and(char::is_ascii_digit);
            if !ok {
                return None;
            }
        } else {
            out.push(*c);
        }
    }
    Some(out)
}

/// `float(value)` of a stored figure: a number, a numeric string, a bool; the failure Python raised for anything else.
fn as_float(v: Option<&Value>) -> R<f64> {
    match v {
        Some(Value::Number(n)) => Ok(n.as_f64().unwrap_or_default()),
        Some(Value::Bool(b)) => Ok(f64::from(u8::from(*b))),
        // a non-finite figure the table holds as Python's json wrote it (`Infinity`, `NaN`)
        Some(Value::String(s)) => nonfinite(s)
            .or_else(|| py_float_text(s))
            .ok_or_else(|| format!("ValueError: could not convert string to float: {s:?}")),
        Some(other) => Err(format!(
            "TypeError: float() argument must be a string or a real number, not {other}"
        )),
        None => Err("KeyError".to_owned()),
    }
}

/// `repr(x)` of a float: Python's shortest digits, and `inf`, `-inf`, `nan`.
fn py_repr(x: f64) -> String {
    if x.is_nan() {
        "nan".to_owned()
    } else if x.is_infinite() {
        if x > 0.0 { "inf" } else { "-inf" }.to_owned()
    } else {
        py_float(x)
    }
}

/// `int(value)` of a stored size: a number (a float truncated), a numeric string, a bool.
fn py_int_of(v: &Value) -> R<i64> {
    match v {
        #[expect(
            clippy::cast_possible_truncation,
            reason = "int() of a float truncates, as Python's does"
        )]
        Value::Number(n) => Ok(n
            .as_i64()
            .unwrap_or_else(|| n.as_f64().map_or(0, |f| f.trunc() as i64))),
        Value::Bool(b) => Ok(i64::from(*b)),
        Value::String(s) => {
            py_int_text(s).ok_or_else(|| format!("ValueError: invalid literal for int(): {s:?}"))
        }
        other => Err(format!(
            "TypeError: int() argument must be a string or a real number, not {other}"
        )),
    }
}

/// `f"{x:.<prec>f}"`, with thousands commas when `commas`.
fn fixed(x: f64, prec: usize, commas: bool) -> String {
    if x.is_nan() {
        return "nan".to_owned();
    }
    let s = format!("{x:.prec$}");
    if !commas || x.is_infinite() {
        return s;
    }
    let (sign, rest) = s.strip_prefix('-').map_or(("", s.as_str()), |r| ("-", r));
    let (whole, frac) = rest
        .split_once('.')
        .map_or((rest, None), |(w, f)| (w, Some(f)));
    let mut grouped = String::new();
    for (i, c) in whole.chars().enumerate() {
        if i > 0 && (whole.len() - i) % 3 == 0 {
            grouped.push(',');
        }
        grouped.push(c);
    }
    format!(
        "{sign}{grouped}{}",
        frac.map_or_else(String::new, |f| format!(".{f}"))
    )
}

/// What a command line read: the verb's own words, and where it fails, argparse's exit 2.
struct Args {
    root: PathBuf,
    cmd: String,
    pos: Vec<String>,
    parsed: l7r_gate_core::record::args::Parsed,
}

fn usage(why: &str) -> crate::Reply {
    crate::Reply {
        stdout: String::new(),
        stderr: format!(
            "usage: budget_change.py [--root ROOT] {{set,change,program,accept}} ...: {why}\n"
        ),
        code: 2,
    }
}

fn read_args(args: &[String], root: &Path) -> Result<Args, crate::Reply> {
    let (mut root, mut i) = (root.to_owned(), 0);
    while let Some(a) = args.get(i).filter(|a| a.starts_with("--") && a.len() > 2) {
        let (word, inline) = a
            .split_once('=')
            .map_or((a.as_str(), None), |(w, v)| (w, Some(v)));
        if !"--root".starts_with(word) {
            return Err(usage(&format!("unrecognized arguments: {a}")));
        }
        match inline
            .map(str::to_owned)
            .or_else(|| args.get(i + 1).cloned())
        {
            Some(v) => root = PathBuf::from(v),
            None => return Err(usage("argument --root: expected one argument")),
        }
        i += if inline.is_some() { 1 } else { 2 };
    }
    let Some(cmd) = args.get(i).cloned() else {
        return Err(usage("the following arguments are required: cmd"));
    };
    let items = |flags: &[&'static str]| flags.iter().map(|f| Spec::value(f)).collect::<Vec<_>>();
    let (specs, need): (Vec<Spec>, usize) = match cmd.as_str() {
        "set" => {
            let mut s = vec![
                Spec::value("--arbiter"),
                Spec::value("--spread"),
                Spec::value("--reason"),
                Spec::flag("--lower"),
                Spec::value("--second"),
                Spec::flag("--raise"),
                Spec::value("--growth-reason"),
            ];
            s.extend(items(&ITEM_FLAGS));
            (s, 5)
        }
        "change" => {
            let mut s = vec![
                Spec::value("--exponent"),
                Spec::value("--words"),
                Spec::value("--derivation"),
                Spec::value("--verdict"),
            ];
            s.extend(items(&ITEM_FLAGS[1..]));
            (s, 2)
        }
        "program" => (vec![Spec::value("--words")], 2),
        "accept" => (vec![Spec::value("--arbiter")], 2),
        other => return Err(usage(&format!("argument cmd: invalid choice: '{other}'"))),
    };
    let parsed = parse_with(&args[i + 1..], &specs, need).map_err(|why| usage(&why))?;
    if parsed.positional.len() < need {
        return Err(usage("the following arguments are required"));
    }
    Ok(Args {
        root,
        cmd,
        pos: parsed.positional.clone(),
        parsed,
    })
}

/// A `type=float` argument: argparse's exit 2 where it does not read. A non-finite one (`inf`, `nan`, `1e999`) is taken, as
/// Python's `float()` takes it, and written as its `json` wrote it (feature 449 T134, the coordinator's ruling).
fn float_arg(text: &str) -> Result<f64, crate::Reply> {
    py_float_text(text).ok_or_else(|| usage(&format!("invalid float value: '{text}'")))
}

fn int_arg(text: &str) -> Result<i64, crate::Reply> {
    py_int_text(text).ok_or_else(|| usage(&format!("invalid int value: '{text}'")))
}

/// The `--items-at-<h>` given, in the sizes' order.
fn items_of(a: &Args, sizes: &[i64]) -> Result<Vec<(i64, i64)>, crate::Reply> {
    let mut out = Vec::new();
    for h in sizes {
        let flag = format!("--items-at-{h}");
        if a.parsed.has(&flag) {
            out.push((*h, int_arg(a.parsed.text(&flag, ""))?));
        }
    }
    Ok(out)
}

fn run(a: &Args) -> Result<R<(String, String)>, crate::Reply> {
    let root = &a.root;
    let text = |name: &str| a.parsed.text(name, "").to_owned();
    Ok(match a.cmd.as_str() {
        "set" => {
            let items = items_of(a, &[10, 20, 40, 80])?;
            let (phase, per_thing, exponent) = (&a.pos[0], &a.pos[1], &a.pos[2]);
            let lower = a.parsed.on("--lower");
            let raise = a.parsed.on("--raise");
            (|| {
                let figure = |t: &str| {
                    py_float_text(t).ok_or_else(|| {
                        format!("ValueError: could not convert string to float: '{t}'")
                    })
                };
                let (per, exp) = (figure(per_thing)?, figure(exponent)?);
                let pin = rules::Pin {
                    phase,
                    per_thing: per,
                    exponent: exp,
                    derivation: &a.pos[3],
                    verdict: &a.pos[4],
                    items: &items,
                    arbiter: &text("--arbiter"),
                    spread: &text("--spread"),
                    reason: &text("--reason"),
                    lower,
                    growth_reason: &text("--growth-reason"),
                    raise,
                    second: &text("--second"),
                };
                let why = rules::set_budget(root, &pin)?;
                let done = if why.is_empty() {
                    let verb = if lower {
                        "lowered to"
                    } else if raise {
                        "raised to"
                    } else {
                        "budgeted at"
                    };
                    format!("`{phase}` {verb} {per_thing} per thing, exponent {exponent}\nbudget-set: {}", rules::per_house(root)?)
                } else {
                    String::new()
                };
                Ok((why, done))
            })()
        }
        "change" => {
            let to = float_arg(&a.pos[1])?;
            let exponent = if a.parsed.has("--exponent") {
                Some(float_arg(&text("--exponent"))?)
            } else {
                None
            };
            let items = items_of(a, &ITEM_SIZES)?;
            let phase = &a.pos[0];
            rules::change_budget(
                root,
                phase,
                to,
                exponent,
                &text("--words"),
                &items,
                &text("--derivation"),
                &text("--verdict"),
            )
            .map(|why| {
                (
                    why,
                    format!(
                        "`{phase}` changed to {} per thing, logged in {LOG} with the GM's words",
                        py_repr(to)
                    ),
                )
            })
        }
        "accept" => {
            let phase = &a.pos[0];
            rules::accept_stage(root, phase, &a.pos[1], &text("--arbiter"))
                .map(|why| (why, format!("`{phase}` accepted at its counted operations at 40 and 80 households, logged in {LOG}")))
        }
        _ => {
            let ops = int_arg(&a.pos[0])?;
            let exponent = float_arg(&a.pos[1])?;
            rules::set_program(root, ops, exponent, &text("--words")).map(|why| {
                (why, format!("the program's budget set to {ops} operations at 40 households, exponent {}, logged in {LOG}", py_repr(exponent)))
            })
        }
    })
}

/// `l7r-gate budget-change [--root R] set|change|program|accept ...`.
#[must_use]
pub fn cli(args: &[String], root: &Path) -> crate::Reply {
    let a = match read_args(args, root) {
        Ok(a) => a,
        Err(reply) => return reply,
    };
    match run(&a) {
        Err(reply) => reply,
        Ok(Err(why)) => crate::Reply {
            stdout: String::new(),
            stderr: format!("budget-{}: {why}\n", a.cmd),
            code: 1,
        },
        Ok(Ok((why, _))) if !why.is_empty() => crate::Reply {
            stdout: String::new(),
            stderr: format!("budget-{}: {why}\n", a.cmd),
            code: 1,
        },
        Ok(Ok((_, done))) => crate::Reply {
            stdout: format!("budget-{}: {done}\n", a.cmd),
            stderr: String::new(),
            code: 0,
        },
    }
}

#[cfg(test)]
mod tests;
