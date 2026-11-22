//! The budget rules themselves (feature 443 FR-005; feature 444 FR-002, FR-005, FR-006, FR-013, FR-015, FR-022, D2; ported by feature
//! 449 T134 from `scripts/budget_change.py`): each returns "" when done, its refusal's words when not, and an error where the
//! Python raised.

use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Map, Value};

use l7r_shared::py_text::strip;
use l7r_shared::pyjson::py_str;

use super::super::work_budget_bundle::{loads, num};
use super::{
    as_float, fixed, glob, load, log, py_int_of, py_re, read, save, sizes, verdict_of, GROWTH_CAP,
    GROWTH_SLACK, HELD, ITEM_SIZES, MISSED, R, RUNS, SOUND, TABLE,
};

/// Request.md: "a sensible design needs a few thousand basic operations per house" (2,000-4,000, a GUESS).
const REFERENCE_PER_HOUSE: f64 = 4000.0;

static SPREAD: LazyLock<Regex> = LazyLock::new(|| py_re(r"^[\d,]+-[\d,]+ at \d+$"));

/// Python's truth of a stored value.
fn truthy(v: &Value) -> bool {
    match v {
        Value::Null => false,
        Value::Bool(b) => *b,
        Value::Number(n) => n.as_f64() != Some(0.0),
        Value::String(s) => !s.is_empty(),
        Value::Array(a) => !a.is_empty(),
        Value::Object(m) => !m.is_empty(),
    }
}

/// A stage's entry - or a FORM of one, `<stage>.<form>` (`field.polder`), budgeted at its own bounded n (the round arbiter's
/// ruling on ask:444-polder-sizes), unbudgeted until its first pin: the entry, or why there is none.
fn stage(table: &Map<String, Value>, phase: &str) -> R<Result<Map<String, Value>, String>> {
    let Some(Value::Object(stages)) = table.get("stages") else {
        return Err("KeyError or AttributeError: the table's stages".to_owned());
    };
    match stages.get(phase) {
        Some(Value::Object(st)) => Ok(Ok(st.clone())),
        Some(Value::Null) | None => {
            if phase
                .split_once('.')
                .is_some_and(|(head, _)| stages.contains_key(head))
            {
                let mut st = Map::new();
                st.insert("status".to_owned(), json!("unbudgeted"));
                return Ok(Ok(st));
            }
            let names: Vec<&str> = stages.keys().map(String::as_str).collect();
            Ok(Err(format!(
                "no stage `{phase}` in {TABLE} - the stages are: {}",
                names.join(", ")
            )))
        }
        Some(_) => Err("TypeError: a stage's entry is no mapping".to_owned()),
    }
}

fn status(st: &Map<String, Value>) -> R<&Value> {
    st.get("status")
        .ok_or_else(|| "KeyError: 'status'".to_owned())
}

fn is(v: &Value, word: &str) -> bool {
    v.as_str() == Some(word)
}

/// The stage's budget at `h`: per thing times its items there.
fn budget_at(st: &Map<String, Value>, h: i64) -> R<f64> {
    Ok(as_float(st.get("per_thing"))? * as_float(st.get(&format!("items_at_{h}")))?)
}

/// The stage's budget at `h` households before its first raise (`first`, recorded at the raise), else its standing budget.
fn first_budget(st: &Map<String, Value>, h: i64) -> R<f64> {
    let first = match st.get("first") {
        Some(v) if truthy(v) => match v {
            Value::Object(m) => m.get(&h.to_string()).cloned(),
            _ => return Err("AttributeError: a stage's first is no mapping".to_owned()),
        },
        _ => None,
    };
    match first {
        Some(v) if truthy(&v) => as_float(Some(&v)),
        _ => budget_at(st, h),
    }
}

/// The name a derivation's rounds run under: its file's name before `.derivation.md` (`web`, `web_greenfield`).
fn stem(derivation: &str) -> String {
    let name = Path::new(derivation)
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();
    name.strip_suffix(".derivation.md")
        .map_or_else(|| name.clone(), str::to_owned)
}

/// The derivation's two levels up (`specs/<feature>/` above its `phases/`), as `Path.parents[1]` reads it.
fn grandparent(path: &Path) -> R<&Path> {
    path.parent()
        .and_then(Path::parent)
        .ok_or_else(|| "IndexError: the derivation has no feature above it".to_owned())
}

/// Does the round arbiter's log of the derivation's feature (`specs/<feature>/arbiter.jsonl`, beside its `phases/`) hold an ACCEPT
/// at `trigger` naming `phase` - in its trigger or its instruction (feature 444 FR-013)? A greenfield derivation's rounds run under
/// its own name (`<stage>_greenfield`, feature 444 FR-015), so an accept naming that names the stage too.
fn accepted_by(root: &Path, derivation: &str, phase: &str, trigger: &str) -> R<bool> {
    let path = grandparent(&root.join(derivation))?.join("arbiter.jsonl");
    ruled_by(&[path], derivation, phase, trigger, &["accept"])
}

/// Does any feature's round-arbiter log (`specs/*/arbiter.jsonl`) hold a CONTINUE or ACCEPT at `trigger` naming `phase`, as
/// `accepted_by` names it? That ruling opens an accepted stage to a raise (449 T250, the arbiter's tooling fix on
/// ask:449-T250-raise-accepted: the stage's acceptance was taken on a tree without the work the raise prices).
fn raise_opened_by(root: &Path, derivation: &str, phase: &str, trigger: &str) -> R<bool> {
    let mut logs: Vec<PathBuf> = std::fs::read_dir(root.join("specs"))
        .map(|dir| {
            dir.filter_map(Result::ok)
                .map(|e| e.path().join("arbiter.jsonl"))
                .collect()
        })
        .unwrap_or_default();
    logs.sort();
    ruled_by(&logs, derivation, phase, trigger, &["continue", "accept"])
}

/// Does one of `logs` hold a ruling of `rulings` at `trigger` naming `phase` - in its trigger or its instruction?
fn ruled_by(
    logs: &[PathBuf],
    derivation: &str,
    phase: &str,
    trigger: &str,
    rulings: &[&str],
) -> R<bool> {
    // a form (`field.polder`) answers to its own name (`polder`) too
    let mut own = vec![phase.to_owned()];
    own.extend(phase.split_once('.').map(|(_, form)| form.to_owned()));
    let mut names = own.clone();
    let stemmed = stem(derivation);
    if own.iter().any(|n| format!("{n}_greenfield") == stemmed) {
        names.push(stemmed); // its own greenfield name alone
    }
    let alternatives: Vec<String> = names
        .iter()
        .map(|n| fancy_regex::escape(n).into_owned())
        .collect();
    let naming = py_re(&format!(
        "(?<![a-z_])(?:{})(?![a-z_])",
        alternatives.join("|")
    ));
    for path in logs.iter().filter(|p| p.is_file()) {
        for line in l7r_shared::speckit::splitlines(&read(path)?) {
            let Ok(r) = loads(line) else {
                continue;
            };
            let Value::Object(r) = r else {
                return Err("AttributeError: an arbiter line is no mapping".to_owned());
            };
            let what = r.get("what").map_or_else(String::new, py_str);
            let ruling = r.get("ruling").and_then(Value::as_str).unwrap_or_default();
            if r.get("trigger").and_then(Value::as_str) == Some(trigger)
                && rulings.contains(&ruling)
                && (naming.is_match(trigger).unwrap_or(false)
                    || naming.is_match(&what).unwrap_or(false))
            {
                return Ok(true);
            }
        }
    }
    Ok(false)
}

/// The stage's counted operations at 40 households in the newest `make work-budget` run, or none when no run counts it.
fn today_at_40(root: &Path, phase: &str) -> Option<f64> {
    let newest = glob(&root.join(RUNS), "", ".json").pop()?;
    let run: Value = loads(&read(&newest).ok()?).ok()?;
    let Value::Object(per) = run
        .get("summary")?
        .get("stages")?
        .get(phase)?
        .get("per")?
        .get("40")?
    else {
        return None;
    };
    as_float(per.get("ops")).ok()
}

/// The items under the derivation's `MISSED` section - its `- ` lines up to the next heading - or none when it has none.
pub(super) fn missed_work(root: &Path, derivation: &str) -> R<Vec<String>> {
    let text = match std::fs::read_to_string(root.join(derivation)) {
        Ok(t) => l7r_gate_core::record::repo::universal(&t),
        Err(e) if e.kind() == std::io::ErrorKind::InvalidData => {
            return Err("UnicodeDecodeError: the derivation".to_owned())
        }
        Err(_) => return Ok(vec![]),
    };
    let Some((_, after)) = text.split_once(MISSED) else {
        return Ok(vec![]);
    };
    let body = after.split_once("\n## ").map_or(after, |(b, _)| b);
    Ok(l7r_shared::speckit::splitlines(body)
        .into_iter()
        .filter_map(|ln| {
            ln.strip_prefix("- ")
                .map(strip)
                .filter(|t| !t.is_empty())
                .map(str::to_owned)
        })
        .collect())
}

/// The exponent from 20 to 80 households of a figure at each (rubric S6) - or across a bounded n's sizes, `ratio` apart; 0 where
/// either is 0.
fn growth(at20: f64, at80: f64, ratio: f64) -> f64 {
    if at20 > 0.0 && at80 > 0.0 {
        (at80 / at20).ln() / ratio.ln()
    } else {
        0.0
    }
}

/// `sum()` of floats as `CPython` adds them (compensated, Neumaier's), so a total's last digit is Python's.
fn py_sum(values: &[f64]) -> f64 {
    let (mut total, mut c) = (0.0_f64, 0.0_f64);
    for x in values {
        let t = total + x;
        c += if total.abs() >= x.abs() {
            (total - t) + x
        } else {
            (x - t) + total
        };
        total = t;
    }
    if c != 0.0 && c.is_finite() {
        total += c;
    }
    total
}

/// The program's sum at 40 households per household, against the design's reference - printed at every pin (ask:444-budget-standard).
pub(super) fn per_house(root: &Path) -> R<String> {
    // read after a pin, which needed its stages a mapping
    let table = load(root)?;
    let stages = table
        .get("stages")
        .and_then(Value::as_object)
        .cloned()
        .unwrap_or_default();
    let (mut at40, mut open) = (Vec::new(), 0);
    for st in stages.values() {
        let Value::Object(st) = st else {
            return Err("AttributeError: a stage's entry is no mapping".to_owned());
        };
        // a form at a bounded n holds no 40
        if !st.get("status").is_some_and(|s| is(s, "unbudgeted"))
            && st.get("items_at_40").is_some_and(|v| !v.is_null())
        {
            at40.push(budget_at(st, 40)?);
        }
        open += usize::from(st.get("status").is_some_and(|s| is(s, "unbudgeted")));
    }
    let total = py_sum(&at40);
    let tail = if open > 0 {
        format!("; {open} stage(s) not yet budgeted")
    } else {
        String::new()
    };
    Ok(format!(
        "the program at 40 households: {} operations, {} a household against the design's few thousand ({} at most, request.md){tail}",
        fixed(total, 0, true),
        fixed(total / 40.0, 0, true),
        fixed(REFERENCE_PER_HOUSE, 0, true)
    ))
}

/// A first budget's pin, as `make budget-set` gives it.
pub(super) struct Pin<'a> {
    pub phase: &'a str,
    pub per_thing: f64,
    pub exponent: f64,
    pub derivation: &'a str,
    pub verdict: &'a str,
    pub items: &'a [(i64, i64)],
    pub arbiter: &'a str,
    pub spread: &'a str,
    pub reason: &'a str,
    pub lower: bool,
    pub growth_reason: &'a str,
    pub raise: bool,
    pub second: &'a str,
}

/// Figures by size as a JSON mapping (`{"20": ...}`, as `json.dumps` writes an int key).
fn by_size(sz: &[i64], f: impl Fn(i64) -> R<f64>) -> R<Value> {
    let mut m = Map::new();
    for h in sz {
        m.insert(h.to_string(), num(f(*h)?));
    }
    Ok(Value::Object(m))
}

/// The checks a raise (`RAISE=1`) owes before it pins: at its top size, past its standing budget, within ten times its first, and
/// past twice it only on a second, independent SOUND.
fn raise_refusal(
    root: &Path,
    pin: &Pin,
    st: &Map<String, Value>,
    sz: &[i64],
    new: &dyn Fn(i64) -> f64,
) -> R<String> {
    // ...AT THE DERIVATION'S TOP SIZE: 40 households, or a form's bounded n (`waterward.polder` at 10-20, feature 444 T29)
    let top = if sz.contains(&40) {
        40
    } else {
        sz[sz.len() - 1]
    };
    let at = format!("at {top}");
    if let Some(why) = no_raise(pin.phase, &at, new(top), budget_at(st, top)?) {
        return Ok(why);
    }
    past_first(
        root,
        pin.phase,
        &at,
        new(top),
        first_budget(st, top)?,
        (pin.verdict, pin.second),
        "TO=<per thing>",
    )
}

/// A first budget, from a SOUND verdict or the round arbiter's accept of the derivation (feature 444 FR-013, the GM 2026-10-28):
/// "" when set, else why not. `lower` re-pins a budgeted stage at no more than its standing budget at any size (no GM words: a
/// lowering asks nothing of him, ask:444-budget-standard). A pin above the stage's counted operations at 40 in the newest `make
/// work-budget` run is refused unless `reason` names why: a budget the stage already meets is no target (the GM 2026-10-28: "I
/// thought the idea was to REDUCE the number of operations"); the count is read here, outside the bundle, so it anchors no
/// derivation.
#[expect(
    clippy::too_many_lines,
    reason = "the rules in the order the Python checked them, each refusal's words beside its check"
)]
pub(super) fn set_budget(root: &Path, pin: &Pin) -> R<String> {
    let (phase, derivation, verdict) = (pin.phase, pin.derivation, pin.verdict);
    let mut table = load(root)?;
    let st = match stage(&table, phase)? {
        Ok(st) => st,
        Err(why) => return Ok(why),
    };
    if pin.raise && pin.lower {
        return Ok("RAISE=1 and LOWER=1 together - a re-pin is one or the other".to_owned());
    }
    // AN ACCEPTED STAGE OPENED TO A RAISE (449 T250, the round arbiter's tooling fix on ask:449-T250-raise-accepted): RAISE=1 with
    // ARBITER= naming a continue or accept ruling on this stage re-pins it, its acceptance and audit dropped as LOWER=1 drops them,
    // its verdict still the raise's own SOUND; without that ruling an accepted stage's raise stays refused
    let opened = pin.raise && !pin.arbiter.is_empty() && is(status(&st)?, "accepted");
    // one raise a ruling (its words: "bound to this stage and these figures", "never a second raise on this ruling")
    if opened && st.get("raised_on").and_then(Value::as_str) == Some(pin.arbiter) {
        return Ok(format!("`{phase}` was raised on {} already - a ruling opens one raise; another owes a new ask (449 T250)", pin.arbiter));
    }
    if opened && !raise_opened_by(root, derivation, phase, pin.arbiter)? {
        return Ok(format!(
            "the round arbiters' logs hold no continue or accept at {} naming `{phase}` - an accepted stage is raised only on a ruling on that stage (449 T250)",
            pin.arbiter
        ));
    }
    if pin.raise {
        let why = raise_ready(root, phase, status(&st)?, derivation, opened)?;
        if !why.is_empty() && is(status(&st)?, "accepted") {
            return Ok(format!("{why}; an accepted stage is raised on the round arbiter's continue or accept ruling naming it: ARBITER=<trigger> (449 T250)"));
        }
        if !why.is_empty() {
            return Ok(why);
        }
    }
    if !(is(status(&st)?, "unbudgeted") || pin.lower || pin.raise) {
        return Ok(format!(
            "`{phase}` is {} already - a change needs the GM's words: make budget-change PHASE={phase} TO=<per thing> WORDS=\"<the GM's words>\"; a lowering re-pins with LOWER=1",
            py_str(status(&st)?)
        ));
    }
    if pin.lower && is(status(&st)?, "unbudgeted") {
        return Ok(format!(
            "`{phase}` has no budget to lower - a first one is set without LOWER"
        ));
    }
    if !root.join(derivation).is_file() {
        return Ok(format!("no derivation at {derivation}"));
    }
    let got = if pin.arbiter.is_empty() || opened {
        verdict_of(&root.join(verdict))?
    } else {
        if !accepted_by(root, derivation, phase, pin.arbiter)? {
            return Ok(format!(
                "the round arbiter's log holds no accept at {} naming `{phase}` - an accept pins a first budget only as the arbiter gave it (feature 444 FR-013)",
                pin.arbiter
            ));
        }
        if !SPREAD.is_match(strip(pin.spread)).unwrap_or(false) {
            return Ok("an accept-pinned budget records its totals' spread across the rounds, for the program target: SPREAD=\"<low>-<high> at <households>\" (feature 444 FR-013)".to_owned());
        }
        SOUND.to_owned()
    };
    if got != SOUND {
        return Ok(format!(
            "the verdict at {verdict} reads {}, not SOUND - a first budget is set only from a SOUND MODE BUDGET verdict (`make work-budget-bundle MODE=budget PHASE={phase} DERIVATION={derivation}`)",
            if got.is_empty() { "nothing" } else { &got }
        ));
    }
    let sz = sizes(&read(&root.join(derivation))?);
    let item = |h: i64| {
        pin.items
            .iter()
            .rev()
            .find(|(s, _)| *s == h)
            .map(|(_, n)| *n)
    };
    let missing: Vec<String> = sz
        .iter()
        .filter(|h| item(**h).is_none())
        .map(i64::to_string)
        .collect();
    if !missing.is_empty() {
        let flags: Vec<String> = sz.iter().map(|h| format!("ITEMS_AT_{h}=")).collect();
        return Ok(format!(
            "no items at {} households - a budget is per thing x the derivation's own items at each size: {} (feature 444 D2)",
            missing.join(", "),
            flags.join(" ")
        ));
    }
    #[expect(
        clippy::cast_precision_loss,
        reason = "an item count, as Python's float times int"
    )]
    let new = |h: i64| pin.per_thing * item(h).unwrap_or(0) as f64;
    if pin.raise {
        let why = raise_refusal(root, pin, &st, &sz, &new)?;
        if !why.is_empty() {
            return Ok(why);
        }
    }
    if pin.lower {
        let mut raised = Vec::new();
        for h in &sz {
            if new(*h) > budget_at(&st, *h)? {
                raised.push(*h);
            }
        }
        if !raised.is_empty() {
            let sizes_said: Vec<String> = raised.iter().map(i64::to_string).collect();
            let mut against = Vec::new();
            for h in &raised {
                against.push(format!(
                    "{} against {}",
                    fixed(new(*h), 0, true),
                    fixed(budget_at(&st, *h)?, 0, true)
                ));
            }
            return Ok(format!(
                "`{phase}` would rise at {} households ({}) - a raise needs the GM's words: make budget-change PHASE={phase} TO=<per thing> WORDS=\"<the GM's words>\"",
                sizes_said.join(", "),
                against.join(", ")
            ));
        }
    }
    // THE GROWTH CAP, HELD BY THE TOOL (the GM 2026-10-29: "if we allow polynomial growth but with a high exponent like n cubed on an
    // n which grows considerably with map size ... that is really going to not work in the long run"): S6's 1.15 was the work-budget
    // agent's judgment alone; a pin growing past it from 20 to 80 households names its reason, such as a bounded n
    let (lo, hi) = (sz[0], sz[sz.len() - 1]);
    #[expect(clippy::cast_precision_loss, reason = "household sizes")]
    let g = growth(new(lo), new(hi), hi as f64 / lo as f64);
    if g > GROWTH_CAP && strip(pin.growth_reason).is_empty() {
        return Ok(format!(
            "`{phase}`'s budget grows at an exponent of {} from 20 to 80 households, past rubric S6's {GROWTH_CAP} (n log n at most) - re-derive it, or name why its n is bounded: GROWTH_REASON=\"<why>\"",
            fixed(g, 2, false)
        ));
    }
    let today = if sz.contains(&40) {
        today_at_40(root, phase)
    } else {
        None
    };
    if let Some(today) =
        today.filter(|t| new(40) > *t && strip(pin.reason).is_empty() && !pin.raise)
    {
        return Ok(format!(
            "`{phase}`'s budget at 40 households, {}, is above what the stage counts today, {} (the newest `make work-budget` run) - a budget the stage already meets is no target (ask:444-budget-standard). Re-derive at the typical case, or name why: REASON=\"<why this stage needs more than it does today>\"",
            fixed(new(40), 0, true),
            fixed(today, 0, true)
        ));
    }
    let mut entry = Map::new();
    entry.insert("status".to_owned(), json!("budgeted"));
    entry.insert("per_thing".to_owned(), num(pin.per_thing));
    entry.insert("exponent".to_owned(), num(pin.exponent));
    entry.insert("derivation".to_owned(), json!(derivation));
    entry.insert(
        "verdict".to_owned(),
        json!(if pin.arbiter.is_empty() || opened {
            verdict
        } else {
            pin.arbiter
        }),
    );
    for h in &sz {
        entry.insert(format!("items_at_{h}"), json!(item(*h)));
    }
    if sz != ITEM_SIZES {
        entry.insert("sizes".to_owned(), json!(sz));
    }
    if opened {
        entry.insert("raised_on".to_owned(), json!(pin.arbiter));
    }
    if !pin.arbiter.is_empty() && !opened {
        entry.insert("pinned_on".to_owned(), json!("accept"));
        // read once more after its `is_file()`, as the Python's `read_bytes()` did
        let bytes = std::fs::read(root.join(derivation)).unwrap_or_default();
        entry.insert(
            "derivation_sha".to_owned(),
            json!(l7r_shared::sha256::hex(&bytes)),
        );
        // its recorded work-budget verdicts
        let dir = root.join(derivation);
        let rounds = glob(
            dir.parent().unwrap_or(root),
            &format!("{}.verdict-", stem(derivation)),
            ".txt",
        )
        .len();
        entry.insert("rounds".to_owned(), json!(rounds));
        entry.insert("spread".to_owned(), json!(strip(pin.spread)));
    }
    if !strip(pin.reason).is_empty() {
        entry.insert("reason".to_owned(), json!(strip(pin.reason)));
    }
    if !strip(pin.growth_reason).is_empty() {
        entry.insert("growth_reason".to_owned(), json!(strip(pin.growth_reason)));
    }
    if pin.raise {
        entry.insert("first".to_owned(), by_size(&sz, |h| first_budget(&st, h))?);
        if !pin.second.is_empty() {
            entry.insert("second".to_owned(), json!(pin.second));
        }
    }
    if let Some(Value::Object(stages)) = table.get_mut("stages") {
        stages.insert(phase.to_owned(), Value::Object(entry));
    }
    save(root, &table)?;
    // the log's figures are read after the save, where the Python read them: a stage that cannot give them is saved unlogged
    let to = by_size(&sz, |h| Ok(new(h)))?;
    let from = if pin.raise || pin.lower {
        by_size(&sz, |h| budget_at(&st, h))?
    } else {
        Value::Null
    };
    if pin.raise {
        let mut row = json!({"what": "raised", "phase": phase, "from": from, "to": to, "verdict": verdict, "missed": missed_work(root, derivation)?});
        if opened {
            row["arbiter"] = json!(pin.arbiter);
        }
        log(root, row)?;
    }
    if pin.lower {
        let row = json!({"what": "lowered", "phase": phase, "from": from, "to": to, "verdict": if pin.arbiter.is_empty() { verdict } else { pin.arbiter }});
        log(root, row)?;
    }
    Ok(String::new())
}

/// A budgeted stage's figure changed with the GM's words, and logged: "" when done, else why not. With `derivation` and `verdict`,
/// the stage is re-pointed at the derivation the raise comes from (feature 444 FR-015: a greenfield figure above its standing pin,
/// raised on the GM's words, stands on its own derivation and SOUND verdict, no longer the one it replaces).
#[expect(
    clippy::too_many_arguments,
    reason = "the command's own arguments, as the Python took them"
)]
pub(super) fn change_budget(
    root: &Path,
    phase: &str,
    to: f64,
    exponent: Option<f64>,
    words: &str,
    items: &[(i64, i64)],
    derivation: &str,
    verdict: &str,
) -> R<String> {
    if strip(words).is_empty() {
        return Ok(NO_WORDS.to_owned());
    }
    let mut table = load(root)?;
    let mut st = match stage(&table, phase)? {
        Ok(st) => st,
        Err(why) => return Ok(why),
    };
    if is(status(&st)?, "unbudgeted") {
        return Ok(format!("`{phase}` has no budget yet - a first one is set from a SOUND verdict: make budget-set PHASE={phase} PER_THING= EXPONENT= DERIVATION= VERDICT="));
    }
    let why = repoint_refusal(root, derivation, verdict)?;
    if !why.is_empty() {
        return Ok(why);
    }
    // A CHANGE MOVES ITEMS AT ITS STAGE'S OWN SIZES (449 T253): a form at its bounded n (`waterward.polder`, 10 and 20) at those, a
    // stage at 20, 40 and 80 - an item count at another size would sit in the table beside figures nothing reads
    let own = form_sizes(phase, &st)?.unwrap_or_else(|| ITEM_SIZES.to_vec());
    if let Some((h, _)) = items.iter().find(|(h, _)| !own.contains(h)) {
        let flags: Vec<String> = own.iter().map(|s| format!("ITEMS_AT_{s}=")).collect();
        return Ok(format!(
            "`{phase}` has no items at {h} households - its sizes are {}: {}",
            households_said(&own),
            flags.join(" ")
        ));
    }
    // ...and the item counts it moves, each named: a raise by items alone logged only the unchanged per-thing figure (444#3)
    // one count a size, in the sizes' order (`items_of`)
    let moved: Vec<(String, i64)> = items
        .iter()
        .map(|(h, n)| (format!("items_at_{h}"), *n))
        .collect();
    let mut before = Map::new();
    for key in ["per_thing", "exponent"] {
        before.insert(
            key.to_owned(),
            st.get(key)
                .cloned()
                .ok_or_else(|| format!("KeyError: '{key}'"))?,
        );
    }
    for (k, _) in &moved {
        before.insert(k.clone(), st.get(k).cloned().unwrap_or(Value::Null));
    }
    st.insert("per_thing".to_owned(), num(to));
    if let Some(e) = exponent {
        st.insert("exponent".to_owned(), num(e));
    }
    for (k, n) in &moved {
        st.insert(k.clone(), json!(n));
    }
    if !derivation.is_empty() {
        st.insert("derivation".to_owned(), json!(derivation));
        st.insert("verdict".to_owned(), json!(verdict));
        for k in ["pinned_on", "derivation_sha", "rounds", "spread"] {
            st.shift_remove(k);
        }
    }
    let mut after = Map::new();
    after.insert("per_thing".to_owned(), st["per_thing"].clone());
    after.insert("exponent".to_owned(), st["exponent"].clone());
    for (k, _) in &moved {
        after.insert(k.clone(), st[k].clone());
    }
    if let Some(Value::Object(stages)) = table.get_mut("stages") {
        stages.insert(phase.to_owned(), Value::Object(st));
    }
    save(root, &table)?;
    let row = json!({"what": "stage", "phase": phase, "from": before, "to": after, "words": words});
    log(root, row)?;
    Ok(String::new())
}

/// A rebuilt phase accepted (feature 444 FR-005, checklist boxes 6-8): its MODE AUDIT verdict WITHIN, and its counted operations at
/// its sizes (`sizes`, a form's bounded n; else 40 and 80 households) in the newest `make work-budget` run at most its budget,
/// recorded as `accepted` - the figures the push's ratchet then holds it to. The sizes accepted at when done, else why not.
///
/// THE RUN IS THE NEWEST BY THE STAMP ITS NAME OPENS WITH, whatever its name's form (`<stamp>-<code id>[-spec].json`, the Python
/// roll's; `<stamp>-rust-<engine>.json`, the Rust driver's), and it counts a stage or a form under the phase's own name (feature
/// 449 T226: on 2026-11-20 the accept read a Python-era `-spec` run, which held the stage's name at 0 operations, past the newest
/// run that held the form's counts). A size it has no count at - none, or 0 operations, a count its counters missed - is refused,
/// never recorded as 0; and the audit is a file of the repository, kept beside the stage's derivation, recorded relative to it.
///
/// ...OR THE ROUND ARBITER'S ACCEPT IN ITS PLACE (`arbiter`, a trigger naming the phase in its log): feature 444 T16's sixth MODE AUDIT
/// was made final for box 7, came back UNCOUNTED, and the arbiter accepted the cheaper rebuild that followed rather than owe a
/// seventh (ask:444-T16-field-after-audit-6) - so `audit` is then the last audit, and every budget check below still holds.
pub(super) fn accept_stage(
    root: &Path,
    phase: &str,
    audit: &str,
    arbiter: &str,
) -> R<Result<Vec<i64>, String>> {
    let mut table = load(root)?;
    let mut st = match stage(&table, phase)? {
        Ok(st) => st,
        Err(why) => return Ok(Err(why)),
    };
    if !st
        .get("status")
        .is_some_and(|s| is(s, "budgeted") || is(s, "accepted"))
    {
        return Ok(Err(format!(
            "`{phase}` has no budget to be accepted against"
        )));
    }
    let derivation = st
        .get("derivation")
        .filter(|v| truthy(v))
        .map_or_else(String::new, py_str);
    let Some(audit) = in_repo(root, audit) else {
        return Ok(Err(outside(root, audit, phase, &derivation)));
    };
    accept_checked(
        root,
        &mut table,
        &mut st,
        phase,
        &audit,
        arbiter,
        &derivation,
    )
}

/// `audit` as a path of the repository at `root`, relative to it - `.` and `..` resolved by their names, as the file need not
/// exist yet - or none when it lies outside.
pub(super) fn in_repo(root: &Path, audit: &str) -> Option<String> {
    use std::path::Component;
    let lexical = |p: &Path| {
        let mut out = std::path::PathBuf::new();
        for c in p.components() {
            if c == Component::ParentDir {
                out.pop();
            } else {
                out.push(c);
            }
        }
        out
    };
    let base = lexical(&std::path::absolute(root).ok()?);
    let path = lexical(&base.join(audit));
    Some(
        path.strip_prefix(&base)
            .ok()?
            .to_string_lossy()
            .into_owned(),
    )
}

/// Why an audit outside the repository is refused, and where it belongs: beside the stage's derivation, under the name the
/// existing audits take (`<phase, its dot an underscore>.audit-<n>.txt`, the next `n`).
pub(super) fn outside(root: &Path, audit: &str, phase: &str, derivation: &str) -> String {
    let said = format!("{audit} is outside the repository - an audit verdict belongs beside the stage's derivation, as specs/444-work-budget-program/phases/waterward.audit-4.txt is");
    if derivation.is_empty() {
        return said;
    }
    let dir = Path::new(derivation).parent().unwrap_or(Path::new(""));
    let name = format!("{}.audit-", phase.replace('.', "_"));
    let next = glob(&root.join(dir), &name, ".txt")
        .iter()
        .filter_map(|p| {
            let file = p.file_name()?.to_string_lossy().into_owned();
            file[name.len()..file.len() - ".txt".len()]
                .parse::<i64>()
                .ok()
        })
        .max()
        .unwrap_or(0)
        + 1;
    format!(
        "{said}: save it as {} and pass that",
        dir.join(format!("{name}{next}.txt")).display()
    )
}

/// Sizes as a sentence names them: `10 and 20`, `20, 40 and 80`.
pub(super) fn households_said(sizes: &[i64]) -> String {
    and_said(&sizes.iter().map(i64::to_string).collect::<Vec<_>>())
}

/// Names as a sentence lists them: `alpha-sheet and beta-sheet`, `a, b and c`.
pub(super) fn and_said(parts: &[String]) -> String {
    let all = parts.join(", ");
    all.rsplit_once(", ")
        .map_or_else(|| all.clone(), |(rest, last)| format!("{rest} and {last}"))
}

/// The stamp a run's name opens with (`20261120T053709Z`, the name up to its first `-`), the runs' order.
fn stamp_of(run: &Path) -> String {
    let name = run.file_name().unwrap_or_default().to_string_lossy();
    name.split('-').next().unwrap_or_default().to_owned()
}

/// A form's own sizes, its bounded n (`waterward.polder`'s 10 and 20, feature 444 T29), or none for a stage, which an accept holds
/// at 40 and 80 and a change sizes at 20, 40 and 80.
fn form_sizes(phase: &str, st: &Map<String, Value>) -> R<Option<Vec<i64>>> {
    let form = phase.contains('.');
    match st.get("sizes") {
        Some(Value::Array(list)) if form && !list.is_empty() => {
            Ok(Some(list.iter().map(py_int_of).collect::<R<_>>()?))
        }
        Some(other) if form && truthy(other) => {
            Err("TypeError: a form's sizes are no list".to_owned())
        }
        _ => Ok(None),
    }
}

/// Every check of an accept after its stage and its audit's place, and the write: the sizes accepted at, else why not.
#[expect(
    clippy::too_many_lines,
    reason = "the rules in the order the Python checked them, each refusal's words beside its check"
)]
fn accept_checked(
    root: &Path,
    table: &mut Map<String, Value>,
    st: &mut Map<String, Value>,
    phase: &str,
    audit: &str,
    arbiter: &str,
    derivation: &str,
) -> R<Result<Vec<i64>, String>> {
    let why = audit_refusal(root, phase, audit, arbiter, derivation)?;
    if !why.is_empty() {
        return Ok(Err(why));
    }
    // A FORM AT ITS BOUNDED N (`waterward.polder`, feature 444 T29) is accepted at its own sizes, a stage at the held 40 and 80
    let form = phase.contains('.');
    let sizes = form_sizes(phase, st)?.unwrap_or_else(|| HELD.to_vec());
    let said = households_said(&sizes);
    // the newest run, by its name's stamp, holds the counts: a form's under its own name (the Rust driver's `hamlet --budget
    // polder`), never its stage's, which rolls another form
    let newest = glob(&root.join(RUNS), "", ".json")
        .into_iter()
        .max_by_key(|r| stamp_of(r));
    let per = newest.as_ref().and_then(|r| {
        let run: Value = loads(&read(r).ok()?).ok()?;
        run.get("summary")?
            .get("stages")?
            .get(phase)?
            .get("per")
            .cloned()
    });
    let Some(per) = per else {
        return Ok(Err(format!("no `make work-budget` run counts `{phase}` - run `make work-budget`, which counts it at {said} households, first")));
    };
    let Value::Object(per) = per else {
        return Err("AttributeError: the run's per is no mapping".to_owned());
    };
    let run = newest
        .as_ref()
        .and_then(|r| r.file_name())
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();
    let mut got = Map::new();
    for h in &sizes {
        let ops = match per.get(&h.to_string()).filter(|r| truthy(r)) {
            Some(Value::Object(row)) if row.get("ops").is_some_and(truthy) => {
                as_float(row.get("ops"))?
            }
            Some(Value::Object(_)) | None => {
                return Ok(Err(format!("the newest run, {run}, has no count at {h} households for `{phase}` - run `make work-budget`, which counts it at {said} households; a stage is never accepted at 0 operations, a count its counters missed")));
            }
            Some(_) => return Err("AttributeError: a roll is no mapping".to_owned()),
        };
        let first = if st.get("first").is_some_and(truthy) {
            Some(first_budget(st, *h)?)
        } else {
            None
        };
        let held = Held {
            phase,
            at: &format!("at {h} households"),
            budget: budget_at(st, *h)?,
            first,
            second: st.get("second").is_some_and(truthy),
        };
        let why = over_refusal(root, &held, ops, audit, arbiter)?;
        if !why.is_empty() {
            return Ok(Err(why));
        }
        got.insert(h.to_string(), num(ops));
    }
    let (lo, hi) = if form {
        (sizes[0], sizes[sizes.len() - 1])
    } else {
        (20, 80)
    };
    let at_lo = match per.get(&lo.to_string()).filter(|r| truthy(r)) {
        Some(Value::Object(row)) => match row.get("ops") {
            Some(v) => as_float(Some(v))?,
            None => 0.0,
        },
        Some(_) => return Err("AttributeError: a roll is no mapping".to_owned()),
        None => 0.0,
    };
    let at_hi = as_float(got.get(&hi.to_string()))?;
    #[expect(clippy::cast_precision_loss, reason = "household sizes")]
    let ratio = hi as f64 / lo as f64;
    let g = growth(at_lo, at_hi, ratio);
    let b = growth(budget_at(st, lo)?, budget_at(st, hi)?, ratio);
    if g > b + GROWTH_SLACK {
        return Ok(Err(format!(
            "`{phase}` grows at an exponent of {} from {lo} to {hi} households, past its budget's {} (rubric S6, FR-005) - rebuild it again, or raise the budget with the GM's words",
            fixed(g, 2, false),
            fixed(b, 2, false)
        )));
    }
    st.insert("status".to_owned(), json!("accepted"));
    st.insert("accepted".to_owned(), Value::Object(got.clone()));
    st.insert("audit".to_owned(), json!(audit));
    if !arbiter.is_empty() {
        st.insert("accept".to_owned(), json!(arbiter));
    }
    if let Some(Value::Object(stages)) = table.get_mut("stages") {
        stages.insert(phase.to_owned(), Value::Object(st.clone()));
    }
    save(root, table)?;
    let mut row =
        json!({"what": "accepted", "phase": phase, "accepted": got, "audit": audit, "run": run});
    if !arbiter.is_empty() {
        row["accept"] = json!(arbiter);
    }
    log(root, row)?;
    Ok(Ok(sizes))
}

/// The whole roll's budget (444 FR-002), set with the GM's words and logged: "" when done, else why not.
pub(super) fn set_program(root: &Path, ops_at_40: i64, exponent: f64, words: &str) -> R<String> {
    if strip(words).is_empty() {
        return Ok(
            "no WORDS - the program's budget is set only with the GM's own words".to_owned(),
        );
    }
    let mut table = load(root)?;
    let before = match table.get("program") {
        Some(Value::Object(m)) => Value::Object(m.clone()),
        _ => return Err("KeyError or TypeError: the table's program".to_owned()),
    };
    let program = json!({"ops_at_40": ops_at_40, "exponent": num(exponent)});
    table.insert("program".to_owned(), program.clone());
    save(root, &table)?;
    let row = json!({"what": "program", "from": before, "to": program, "words": words});
    log(root, row)?;
    Ok(String::new())
}

mod shared;
pub(super) use shared::{
    audit_refusal, no_raise, over_refusal, past_first, raise_ready, repoint_refusal, Held, NO_WORDS,
};

#[cfg(test)]
mod tests;
