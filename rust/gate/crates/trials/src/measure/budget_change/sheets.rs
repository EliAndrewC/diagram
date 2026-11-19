//! A Mode A stage's budget, per pool sheet (feature 449 T201): a stage whose derivation's `Sizes:` line names the pool sheets is no
//! stage of the hamlet roll and has no households, so its budget is not per thing x items at 20/40/80 but the derivation's own Totals
//! line on each sheet - per-caption cost runs 40 to 305 operations across T198's six sheets, so no single per-thing figure carries it.
//! It is kept under `sheet_stages`, beside the roll's `stages`, which every reader of the table (`make work-budget`, the program's sum,
//! the coverage exemptions, the view) reads as the roll's alone.
//!
//! What is built: the first budget (`make budget-set` on a pool-sheet derivation and its SOUND verdict) and the comparison of
//! counted operations per sheet against it (`budget-change sheets`, `make budget-sheets`). Not built: a pool-sheet stage's change,
//! lowering, raise or acceptance, and the counts read straight off `l7r-mode-a caption-counts` - the comparison takes them as given.

use std::fmt::Write as _;
use std::path::Path;

use serde_json::{json, Map, Value};

use super::super::work_budget_bundle::{num, sheet_budget};
use super::{fixed, load, read, save, verdict_of, Args, ITEM_FLAGS, LEEWAY, R, SOUND, TABLE};

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
        [
            "--arbiter",
            "--spread",
            "--reason",
            "--growth-reason",
            "--second",
        ]
        .into_iter()
        .map(|f| (f, a.parsed.has(f))),
    )
    .chain(
        ["--lower", "--raise"]
            .into_iter()
            .map(|f| (f, a.parsed.on(f))),
    )
    .find_map(|(name, given)| given.then_some(name));
    let why = set_sheet_budget(root, phase, &a.pos[3], &a.pos[4], hamlet)?;
    let done = if why.is_empty() {
        set_reply(root, phase)?
    } else {
        String::new()
    };
    Ok((why, done))
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
fn set_sheet_budget(
    root: &Path,
    phase: &str,
    derivation: &str,
    verdict: &str,
    hamlet: Option<&str>,
) -> R<String> {
    if let Some(arg) = hamlet {
        return Ok(format!("{derivation} sizes pool sheets: its budget is its Totals line on each sheet (feature 449 T201), so `{arg}` - a hamlet stage's - is not taken; give PHASE, DERIVATION and VERDICT alone"));
    }
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
        return Ok(format!("`{phase}` is budgeted per sheet already - a change needs the GM's words, and a pool-sheet stage's change is not built yet (feature 449 T201)"));
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

/// The per-sheet budget just set, for the reply.
fn set_reply(root: &Path, phase: &str) -> R<String> {
    let table = load(root)?;
    let st = &table[SHEETS][phase];
    let mut out = format!("`{phase}` budgeted per sheet:");
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
    let Some(Value::Object(st)) = table.get(SHEETS).and_then(|s| s.get(phase)) else {
        return Ok(Err(format!("no pool-sheet stage `{phase}` in {TABLE} - set it first: make budget-set PHASE={phase} DERIVATION=<its derivation> VERDICT=<its SOUND verdict>")));
    };
    let Some(Value::Object(sheets)) = st.get("sheets") else {
        return Err(format!("TypeError: `{phase}`'s sheets are no mapping"));
    };
    let mut given = Vec::new();
    for c in counts {
        let Some((name, n)) = c.split_once('=') else {
            return Ok(Err(format!(
                "`{c}` is no count - write `<sheet>=<counted operations>`"
            )));
        };
        let Ok(n) = n.trim().parse::<f64>() else {
            return Ok(Err(format!(
                "`{c}` is no count - write `<sheet>=<counted operations>`"
            )));
        };
        if !sheets.contains_key(name) {
            let named: Vec<&str> = sheets.keys().map(String::as_str).collect();
            return Ok(Err(format!(
                "`{name}` is no sheet of `{phase}` - its sheets are: {}",
                named.join(", ")
            )));
        }
        given.push((name.to_owned(), n));
    }
    let mut out = "| sheet | counted | budget | ratio |\n|---|---|---|---|\n".to_owned();
    let (mut counted, mut budgeted, mut past) = (0.0, 0.0, Vec::new());
    for (name, n) in &given {
        let b = sheets[name]["budget"].as_f64().unwrap_or_default();
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
        .keys()
        .filter(|k| !given.iter().any(|(g, _)| g == *k))
        .map(String::as_str)
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
