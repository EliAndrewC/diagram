//! A Mode A stage's budget, per pool sheet (feature 449 T201): a stage whose derivation's `Sizes:` line names the pool sheets is no
//! stage of the hamlet roll and has no households, so its budget is not per thing x items at 20/40/80 but the derivation's own Totals
//! line on each sheet - per-caption cost runs 40 to 305 operations across T198's six sheets, so no single per-thing figure carries it.
//! It is kept under `sheet_stages`, beside the roll's `stages`, which every reader of the table (`make work-budget`, the program's sum,
//! the coverage exemptions, the view) reads as the roll's alone.
//!
//! What is built: the first budget (`make budget-set` on a pool-sheet derivation and its SOUND verdict), the comparison of
//! counted operations per sheet against it (`budget-change sheets`, `make budget-sheets`), and (feature 449 T243, 444 FR-022) its
//! raise, change and accept as a hamlet stage takes them, through the hamlet's own rules (`rules.rs`): the raise (`make budget-set
//! RAISE=1`) on a SOUND re-derivation naming the work its first missed, judged on the sheets together for being a raise and on each
//! sheet against its first for the caps (twice it a second SOUND, ten times it the GM's words); the change (`make budget-change`,
//! the GM's words) to the figures `TO="<sheet>=<ops> ..."` names or a re-pointed derivation's Totals; the accept (`make
//! budget-accept`) on its MODE AUDIT and each sheet's count, `COUNTS="<sheet>=<ops> ..."`. Not built: a pool-sheet stage's lowering,
//! and the counts read straight off `l7r-mode-a caption-counts` - the comparison and the accept take them as given.

use std::fmt::Write as _;
use std::path::Path;

use serde_json::{json, Map, Value};

use super::super::work_budget_bundle::{num, sheet_budget};
use super::rules::{self, Held};
use super::{
    fixed, load, log, read, save, verdict_of, Args, ITEM_FLAGS, LEEWAY, LOG, R, SOUND, TABLE,
};

/// The key of the table the pool-sheet stages are kept under.
const SHEETS: &str = "sheet_stages";

/// `set` on a pool-sheet derivation: (why not, the reply).
pub(super) fn set_cli(a: &Args) -> R<(String, String)> {
    let (root, phase) = (&a.root, &a.pos[0]);
    // the first hamlet-only argument given, which a pool-sheet stage does not take
    let hamlet = [
        ("PER_THING", !a.pos[1].is_empty()),
        ("EXPONENT", !a.pos[2].is_empty()),
    ]
    .into_iter()
    .chain(ITEM_FLAGS.iter().map(|f| (*f, a.parsed.has(f))))
    .chain(
        ["--arbiter", "--spread", "--reason", "--growth-reason"]
            .into_iter()
            .map(|f| (f, a.parsed.has(f))),
    )
    .chain(std::iter::once(("--lower", a.parsed.on("--lower"))))
    .find_map(|(name, given)| given.then_some(name));
    let raise = a.parsed.on("--raise");
    let second = a.parsed.text("--second", "");
    let why = match hamlet {
        Some(arg) => taken_not(&a.pos[3], arg),
        None if raise => raise_sheet_budget(root, phase, &a.pos[3], &a.pos[4], second)?,
        None if !second.is_empty() => {
            "SECOND= is a raise's second SOUND - give RAISE=1 with it".to_owned()
        }
        None => set_sheet_budget(root, phase, &a.pos[3], &a.pos[4])?,
    };
    let done = if why.is_empty() {
        figures_reply(root, phase, if raise { "raised" } else { "budgeted" })?
    } else {
        String::new()
    };
    Ok((why, done))
}

/// Why a hamlet-only argument is refused on a pool-sheet derivation.
fn taken_not(derivation: &str, arg: &str) -> String {
    format!("{derivation} sizes pool sheets: its budget is its Totals line on each sheet (feature 449 T201), so `{arg}` - a hamlet stage's - is not taken; give PHASE, DERIVATION and VERDICT alone, RAISE=1 [SECOND=] to raise it")
}

/// Whether `phase` is a pool-sheet stage of the table (feature 449 T243: its change and accept are this module's).
pub(super) fn is_sheet_stage(root: &Path, phase: &str) -> bool {
    load(root).is_ok_and(|t| t.get(SHEETS).and_then(|s| s.get(phase)).is_some())
}

/// The pool-sheet stage `phase`'s entry, or why there is none.
fn entry_of(table: &Map<String, Value>, phase: &str) -> Result<Map<String, Value>, String> {
    match table.get(SHEETS).and_then(|s| s.get(phase)) {
        Some(Value::Object(st)) => Ok(st.clone()),
        _ => Err(format!("no pool-sheet stage `{phase}` in {TABLE} - set it first: make budget-set PHASE={phase} DERIVATION=<its derivation> VERDICT=<its SOUND verdict>")),
    }
}

/// Each sheet's standing budget, in the entry's order.
fn standing(st: &Map<String, Value>, phase: &str) -> R<Vec<(String, f64)>> {
    let Some(Value::Object(sheets)) = st.get("sheets") else {
        return Err(format!("TypeError: `{phase}`'s sheets are no mapping"));
    };
    Ok(sheets
        .iter()
        .map(|(n, b)| (n.clone(), b["budget"].as_f64().unwrap_or_default()))
        .collect())
}

/// The entry written back under its phase, and the table saved.
fn put_entry(
    root: &Path,
    mut table: Map<String, Value>,
    phase: &str,
    st: Map<String, Value>,
) -> R<()> {
    // the stage was read from this table's mapping (`entry_of`), so it is one
    if let Some(Value::Object(stages)) = table.get_mut(SHEETS) {
        stages.insert(phase.to_owned(), Value::Object(st));
    }
    save(root, &table)
}

/// Figures by sheet as a JSON mapping.
fn by_sheet(figures: &[(String, f64)]) -> Value {
    Value::Object(figures.iter().map(|(n, f)| (n.clone(), num(*f))).collect())
}

/// The derivation's Totals per sheet, or why they do not read.
fn totals(
    root: &Path,
    phase: &str,
    derivation: &str,
) -> R<Result<super::super::work_budget_bundle::SheetBudget, String>> {
    Ok(sheet_budget(&read(&root.join(derivation))?).ok_or_else(|| {
        format!("{derivation}'s Totals do not read per sheet - `make work-budget-bundle MODE=budget PHASE={phase} DERIVATION={derivation}` names what is short")
    }))
}

/// A SOUND verdict at `verdict`, or why not.
fn sound_refusal(root: &Path, phase: &str, derivation: &str, verdict: &str) -> R<String> {
    let got = verdict_of(&root.join(verdict))?;
    Ok(if got == SOUND {
        String::new()
    } else {
        format!(
            "the verdict at {verdict} reads {}, not SOUND - a budget is set only from a SOUND MODE BUDGET verdict (`make work-budget-bundle MODE=budget PHASE={phase} DERIVATION={derivation}`)",
            if got.is_empty() { "nothing" } else { &got }
        )
    })
}

/// A pool-sheet stage raised on a SOUND re-derivation (444 FR-022, feature 449 T243): "" when raised, else why not. It owes what a
/// hamlet raise owes (`rules::raise_ready`, `no_raise`, `past_first`): judged a raise on the sheets together, capped on each sheet
/// against its first figure, which the first raise records and every later one keeps.
fn raise_sheet_budget(
    root: &Path,
    phase: &str,
    derivation: &str,
    verdict: &str,
    second: &str,
) -> R<String> {
    let table = load(root)?;
    let mut st = match entry_of(&table, phase) {
        Ok(st) => st,
        Err(why) => return Ok(why),
    };
    let why = rules::raise_ready(
        root,
        phase,
        st.get("status").unwrap_or(&Value::Null),
        derivation,
        false,
    )?;
    if !why.is_empty() {
        return Ok(why);
    }
    let why = sound_refusal(root, phase, derivation, verdict)?;
    if !why.is_empty() {
        return Ok(why);
    }
    let budget = match totals(root, phase, derivation)? {
        Ok(b) => b,
        Err(why) => return Ok(why),
    };
    let was = standing(&st, phase)?;
    if let Some((name, _)) = was
        .iter()
        .find(|(n, _)| !budget.sheets.iter().any(|(s, _, _)| s == n))
    {
        return Ok(format!("{derivation} names no budget for {name}, a sheet `{phase}` holds - a raise re-derives every sheet"));
    }
    let all_was = st
        .get("all_sheets")
        .and_then(Value::as_f64)
        .unwrap_or_default();
    if let Some(why) = rules::no_raise(phase, "on all sheets", budget.all, all_was) {
        return Ok(why);
    }
    let mut first = if let Some(Value::Object(f)) = st.get("first") {
        f.clone()
    } else {
        let mut f: Map<String, Value> = was.iter().map(|(n, b)| (n.clone(), num(*b))).collect();
        f.insert("all sheets".to_owned(), num(all_was));
        f
    };
    for (name, ops, _) in &budget.sheets {
        // a sheet new to the stage has no first figure: its own is its first
        let at_first = first.get(name).and_then(Value::as_f64).unwrap_or(*ops);
        let why = rules::past_first(
            root,
            phase,
            &format!("on {name}"),
            *ops,
            at_first,
            (verdict, second),
            "TO=\"<sheet>=<ops> ...\"",
        )?;
        if !why.is_empty() {
            return Ok(why);
        }
        first.entry(name.clone()).or_insert_with(|| num(*ops));
    }
    let mut sheets = Map::new();
    for (name, ops, items) in &budget.sheets {
        sheets.insert(
            name.clone(),
            json!({"budget": num(*ops), "items": num(*items)}),
        );
    }
    let to: Vec<(String, f64)> = budget
        .sheets
        .iter()
        .map(|(n, o, _)| (n.clone(), *o))
        .collect();
    st.insert("derivation".to_owned(), json!(derivation));
    st.insert("verdict".to_owned(), json!(verdict));
    st.insert("sheets".to_owned(), Value::Object(sheets));
    st.insert("all_sheets".to_owned(), num(budget.all));
    st.insert("first".to_owned(), Value::Object(first));
    if !second.is_empty() {
        st.insert("second".to_owned(), json!(second));
    }
    put_entry(root, table, phase, st)?;
    let row = json!({"what": "raised", "phase": phase, "from": by_sheet(&was), "to": by_sheet(&to), "verdict": verdict, "missed": rules::missed_work(root, derivation)?});
    log(root, row)?;
    Ok(String::new())
}

/// `<sheet>=<figure>` pairs read against the stage's sheets: each pair, or why not (`noun`: what a figure is, `count` or `figure`).
fn pairs(
    phase: &str,
    sheets: &[(String, f64)],
    given: &[String],
    noun: &str,
) -> Result<Vec<(String, f64)>, String> {
    let mut out = Vec::new();
    for c in given {
        let read = c
            .split_once('=')
            .and_then(|(name, n)| Some((name, n.trim().parse::<f64>().ok()?)));
        let Some((name, n)) = read else {
            return Err(format!("`{c}` is no {noun} - write `<sheet>=<operations>`"));
        };
        if !sheets.iter().any(|(s, _)| s == name) {
            let named: Vec<&str> = sheets.iter().map(|(s, _)| s.as_str()).collect();
            return Err(format!(
                "`{name}` is no sheet of `{phase}` - its sheets are: {}",
                named.join(", ")
            ));
        }
        out.push((name.to_owned(), n));
    }
    Ok(out)
}

/// `change PHASE "<sheet>=<ops> ..." --words W [--derivation D --verdict V]` on a pool-sheet stage (feature 449 T243): the figures
/// changed with the GM's words, as a hamlet stage's are (`rules::NO_WORDS`, `rules::repoint_refusal`), and logged.
pub(super) fn change_cli(a: &Args) -> R<(String, String)> {
    let (root, phase) = (&a.root, &a.pos[0]);
    let text = |f: &str| a.parsed.text(f, "").to_owned();
    let (words, derivation, verdict) = (text("--words"), text("--derivation"), text("--verdict"));
    let hamlet = std::iter::once(("EXPONENT", a.parsed.has("--exponent")))
        .chain(ITEM_FLAGS[1..].iter().map(|f| (*f, a.parsed.has(f))))
        .find_map(|(name, given)| given.then_some(name));
    let refused = |why: String| Ok((why, String::new()));
    if let Some(arg) = hamlet {
        return refused(format!("`{phase}` is budgeted per sheet (feature 449 T201), so `{arg}` - a hamlet stage's - is not taken; give TO=\"<sheet>=<ops> ...\", or DERIVATION= and VERDICT=, with WORDS"));
    }
    if l7r_shared::py_text::strip(&words).is_empty() {
        return refused(rules::NO_WORDS.to_owned());
    }
    let table = load(root)?;
    let mut st = entry_of(&table, phase)?;
    let why = rules::repoint_refusal(root, &derivation, &verdict)?;
    if !why.is_empty() {
        return refused(why);
    }
    let given: Vec<String> = a.pos[1].split_whitespace().map(str::to_owned).collect();
    if given.is_empty() && derivation.is_empty() {
        return refused(format!("a pool-sheet stage's change names its figures: TO=\"<sheet>=<ops> ...\", or DERIVATION= VERDICT= to take its Totals (`{phase}`'s sheets: {})", standing(&st, phase)?.iter().map(|(n, _)| n.as_str()).collect::<Vec<_>>().join(", ")));
    }
    let was = standing(&st, phase)?;
    if !derivation.is_empty() {
        let budget = match totals(root, phase, &derivation)? {
            Ok(b) => b,
            Err(why) => return refused(why),
        };
        let mut sheets = Map::new();
        for (name, ops, items) in &budget.sheets {
            sheets.insert(
                name.clone(),
                json!({"budget": num(*ops), "items": num(*items)}),
            );
        }
        st.insert("sheets".to_owned(), Value::Object(sheets));
        st.insert("derivation".to_owned(), json!(derivation));
        st.insert("verdict".to_owned(), json!(verdict));
    }
    let moved = match pairs(phase, &standing(&st, phase)?, &given, "figure") {
        Ok(m) => m,
        Err(why) => return refused(why),
    };
    for (name, n) in &moved {
        if let Some(Value::Object(b)) = st.get_mut("sheets").and_then(|s| s.get_mut(name)) {
            b.insert("budget".to_owned(), num(*n));
        }
    }
    let to = standing(&st, phase)?;
    st.insert(
        "all_sheets".to_owned(),
        num(to.iter().map(|(_, b)| b).sum()),
    );
    put_entry(root, table, phase, st)?;
    log(
        root,
        json!({"what": "sheets", "phase": phase, "from": by_sheet(&was), "to": by_sheet(&to), "words": words}),
    )?;
    let done = figures_reply(root, phase, "changed")?;
    Ok((
        String::new(),
        format!("{done}, logged in {LOG} with the GM's words"),
    ))
}

/// `accept PHASE AUDIT --counts "<sheet>=<ops> ..." [--arbiter A]` on a pool-sheet stage (feature 449 T243): its audit and each
/// sheet's count held as a hamlet stage's sizes are (`rules::audit_refusal`, `rules::over_refusal`), recorded as `accepted`.
pub(super) fn accept_cli(a: &Args) -> R<(String, String)> {
    let (root, phase) = (&a.root, &a.pos[0]);
    let (arbiter, counts) = (
        a.parsed.text("--arbiter", ""),
        a.parsed.text("--counts", ""),
    );
    let refused = |why: String| Ok((why, String::new()));
    let table = load(root)?;
    let mut st = entry_of(&table, phase)?;
    let status = st.get("status").and_then(Value::as_str);
    if status != Some("budgeted") && status != Some("accepted") {
        return refused(format!("`{phase}` has no budget to be accepted against"));
    }
    let derivation = st
        .get("derivation")
        .and_then(Value::as_str)
        .unwrap_or_default()
        .to_owned();
    let Some(audit) = rules::in_repo(root, &a.pos[1]) else {
        return refused(rules::outside(root, &a.pos[1], phase, &derivation));
    };
    let why = rules::audit_refusal(root, phase, &audit, arbiter, &derivation)?;
    if !why.is_empty() {
        return refused(why);
    }
    let given: Vec<String> = counts.split_whitespace().map(str::to_owned).collect();
    if given.is_empty() {
        return refused(format!("`{phase}` is budgeted per sheet: its accept takes each sheet's counted operations, COUNTS=\"<sheet>=<ops> ...\" (`make budget-sheets` compares them first)"));
    }
    let sheets = standing(&st, phase)?;
    let given = match pairs(phase, &sheets, &given, "count") {
        Ok(g) => g,
        Err(why) => return refused(why),
    };
    let first = st.get("first").cloned().unwrap_or(Value::Null);
    let second = st
        .get("second")
        .is_some_and(|v| v.as_str().is_some_and(|s| !s.is_empty()));
    let mut got = Map::new();
    let mut names = Vec::new();
    for (name, budget) in sheets {
        let Some(ops) = given
            .iter()
            .rev()
            .find(|(n, _)| *n == name)
            .map(|(_, o)| *o)
            .filter(|o| *o > 0.0)
        else {
            return refused(format!("no count on {name} for `{phase}` - an accept counts every sheet, and a stage is never accepted at 0 operations, a count its counters missed"));
        };
        let held = Held {
            phase,
            at: &format!("on {name}"),
            budget,
            first: first.get(&name).and_then(Value::as_f64),
            second,
        };
        let why = rules::over_refusal(root, &held, ops, &audit, arbiter)?;
        if !why.is_empty() {
            return refused(why);
        }
        got.insert(name.clone(), num(ops));
        names.push(name);
    }
    st.insert("status".to_owned(), json!("accepted"));
    st.insert("accepted".to_owned(), Value::Object(got.clone()));
    st.insert("audit".to_owned(), json!(audit));
    if !arbiter.is_empty() {
        st.insert("accept".to_owned(), json!(arbiter));
    }
    put_entry(root, table, phase, st)?;
    let mut row = json!({"what": "accepted", "phase": phase, "accepted": got, "audit": audit, "counts": "given"});
    if !arbiter.is_empty() {
        row["accept"] = json!(arbiter);
    }
    log(root, row)?;
    let said = rules::and_said(&names);
    Ok((
        String::new(),
        format!("`{phase}` accepted at its counted operations on {said}, logged in {LOG}"),
    ))
}

/// `sheets PHASE "<sheet>=<ops> ..."`: (why not, the table).
pub(super) fn compare_cli(a: &Args) -> R<(String, String)> {
    let counts: Vec<String> = a.pos[1].split_whitespace().map(str::to_owned).collect();
    Ok(match compare(&a.root, &a.pos[0], &counts)? {
        Ok(table) => (String::new(), table.trim_end().to_owned()),
        Err(why) => (why, String::new()),
    })
}

/// A first per-sheet budget from a SOUND verdict: "" when set, else why not. `hamlet` names the first hamlet-only argument given.
fn set_sheet_budget(root: &Path, phase: &str, derivation: &str, verdict: &str) -> R<String> {
    let mut table = load(root)?;
    // a stage of the roll, or a form of one (`<stage>.<form>`, as `stage` reads it)
    let head = phase.split_once('.').map_or(phase, |(h, _)| h);
    if [phase, head]
        .iter()
        .any(|p| table.get("stages").and_then(|s| s.get(*p)).is_some())
    {
        return Ok(format!(
            "`{phase}` is a hamlet stage of {TABLE}, sized by households - its derivation cannot size pool sheets"
        ));
    }
    if table.get(SHEETS).and_then(|s| s.get(phase)).is_some() {
        return Ok(format!("`{phase}` is budgeted per sheet already - a change needs the GM's words: make budget-change PHASE={phase} TO=\"<sheet>=<ops> ...\" WORDS=\"<the GM's words>\"; a raise on a SOUND re-derivation naming the work its first missed takes RAISE=1 (feature 449 T243)"));
    }
    let got = verdict_of(&root.join(verdict))?;
    if got != SOUND {
        return Ok(format!(
            "the verdict at {verdict} reads {}, not SOUND - a first budget is set only from a SOUND MODE BUDGET verdict (`make work-budget-bundle MODE=budget PHASE={phase} DERIVATION={derivation}`)",
            if got.is_empty() { "nothing" } else { &got }
        ));
    }
    let Some(budget) = sheet_budget(&read(&root.join(derivation))?) else {
        return Ok(format!("{derivation}'s Totals do not read per sheet - `make work-budget-bundle MODE=budget PHASE={phase} DERIVATION={derivation}` names what is short"));
    };
    let mut sheets = Map::new();
    for (name, ops, items) in &budget.sheets {
        sheets.insert(
            name.clone(),
            json!({"budget": num(*ops), "items": num(*items)}),
        );
    }
    let entry = json!({"status": "budgeted", "derivation": derivation, "verdict": verdict, "sheets": sheets, "all_sheets": num(budget.all)});
    match table.entry(SHEETS).or_insert_with(|| json!({})) {
        Value::Object(stages) => {
            stages.insert(phase.to_owned(), entry);
        }
        _ => return Err(format!("TypeError: {TABLE}'s {SHEETS} is no mapping")),
    }
    save(root, &table)?;
    Ok(String::new())
}

/// The per-sheet budget just written, for the reply: `verb` says how (`budgeted`, `raised`, `changed`).
fn figures_reply(root: &Path, phase: &str, verb: &str) -> R<String> {
    let table = load(root)?;
    let st = &table[SHEETS][phase];
    let mut out = format!("`{phase}` {verb} per sheet:");
    for (name, b) in st["sheets"].as_object().into_iter().flatten() {
        let _ = write!(
            out,
            " {name} {};",
            fixed(b["budget"].as_f64().unwrap_or_default(), 0, true)
        );
    }
    let _ = write!(
        out,
        " all sheets {}",
        fixed(st["all_sheets"].as_f64().unwrap_or_default(), 0, true)
    );
    Ok(out)
}

/// Counted operations per sheet (`<sheet>=<ops>`) against a pool-sheet stage's budget: a table, each sheet's ratio and the sheets
/// together, and the sheets past twice their budget (the audit's leeway, 444 FR-022) - or why it cannot compare.
fn compare(root: &Path, phase: &str, counts: &[String]) -> R<Result<String, String>> {
    let table = load(root)?;
    let st = match entry_of(&table, phase) {
        Ok(st) => st,
        Err(why) => return Ok(Err(why)),
    };
    let sheets = standing(&st, phase)?;
    let given = match pairs(phase, &sheets, counts, "count") {
        Ok(g) => g,
        Err(why) => return Ok(Err(why)),
    };
    let mut out = "| sheet | counted | budget | ratio |\n|---|---|---|---|\n".to_owned();
    let (mut counted, mut budgeted, mut past) = (0.0, 0.0, Vec::new());
    for (name, n) in &given {
        let b = sheets
            .iter()
            .find(|(s, _)| s == name)
            .map_or(0.0, |(_, b)| *b);
        counted += n;
        budgeted += b;
        let _ = writeln!(
            out,
            "| {name} | {} | {} | {} |",
            fixed(*n, 0, true),
            fixed(b, 0, true),
            ratio(*n, b)
        );
        if *n > LEEWAY * b {
            past.push(name.as_str());
        }
    }
    let _ = writeln!(
        out,
        "| **the sheets given** | {} | {} | {} |",
        fixed(counted, 0, true),
        fixed(budgeted, 0, true),
        ratio(counted, budgeted)
    );
    let missing: Vec<&str> = sheets
        .iter()
        .filter(|(k, _)| !given.iter().any(|(g, _)| g == k))
        .map(|(k, _)| k.as_str())
        .collect();
    if !missing.is_empty() {
        let _ = writeln!(out, "not counted: {}", missing.join(", "));
    }
    if !past.is_empty() {
        let _ = writeln!(
            out,
            "past twice the budget (the audit's leeway, 444 FR-022): {}",
            past.join(", ")
        );
    }
    Ok(Ok(out))
}

fn ratio(n: f64, b: f64) -> String {
    if b > 0.0 {
        format!("{}x", fixed(n / b, 1, false))
    } else {
        "-".to_owned()
    }
}

#[cfg(test)]
mod tests;
