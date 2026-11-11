//! The round arbiter's bundle (feature 449 T88, from `arbiter_bundle.py`, feature 375 FR-011, plan D11): what `round-arbiter` reads to rule on a trigger, built mechanically from the loop's own record and copied OUT of the repository. `l7r-gate arbiter bundle <trigger> [--root DIR] [--out DIR] [--missing-ok REASON] [--evidence "F F"]`, `--batch [--triggers "T T"]`, and `--check-ask WHY [--evidence ...]`.

use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::checks::arbiter as core;
use l7r_guard::shared::checks::reply;
use l7r_guard::shared::checks::rounds::subject_of_path;
use l7r_guard::shared::checks::{load, state_path};
use l7r_guard::shared::py_text::split;
use serde_json::{Map, Value};

use crate::record::args::{parse_with, Spec};
use crate::record::bundle::earlier::dispatches;
use crate::record::bundle::{
    dashed, default_root, hit, py_path, py_str, pyre, relative, remove_tree, resolve, shown, write,
    Run,
};
use crate::record::repo::{fail, read_text, tree_of, Fail};
use crate::Reply;

pub(crate) mod marks;
mod reviews;
mod sections;

use marks::{last_edits, mark_rounds, reply_of, subject_files};
use reviews::{feature_section, plan_rounds, review_verdicts, spec_rounds};
use sections::{
    capped_round_cause, claims_section, evidence_section, field, flow_sections, g, red_gate_runs,
    round_counter,
};

static PLAN_REVIEW: LazyLock<Regex> =
    LazyLock::new(|| pyre(r"(?i)\bplan(?:'s)? (?:review|round)s?\b|\bplan-delta\b"));
static TRIGGER_FEATURE: LazyLock<Regex> =
    LazyLock::new(|| pyre(r"\|(?:plan:)?(\d+-[a-z0-9][a-z0-9-]*)(?:#|@|$)"));
static MADE_UP: LazyLock<Regex> = LazyLock::new(|| pyre(r"^round-\d+@"));

/// Why a bundle cannot be built: a refusal (`ValueError`), what the loop's record lacks (`MissingRecord`), or a failure the Python raised.
pub(crate) enum Stop {
    Value(String),
    Missing(Vec<String>),
    Fail(Fail),
}

impl From<Fail> for Stop {
    fn from(why: Fail) -> Self {
        Self::Fail(why)
    }
}

/// (check, subject, files, unit) of a trigger; a reversal the EDIT wire caught names a FILE (368's ruling on 0047).
fn target(root: &Path, trigger: &str, owed: &Value) -> (String, String, Vec<String>, String) {
    let unit = owed
        .get("unit")
        .filter(|u| sections::truthy(Some(u)))
        .map_or_else(|| core::unit_of(trigger), py_str);
    let (mut check, mut subject) = unit
        .split_once('|')
        .map_or((unit.clone(), String::new()), |(c, s)| {
            (c.to_owned(), s.to_owned())
        });
    let mut files = Vec::new();
    if trigger.starts_with("reversal:") && !unit.contains('|') {
        let tgt = if unit.is_empty() {
            let rest = trigger.split_once(':').map_or("", |p| p.1);
            rest.rsplit_once('@').map_or(rest, |p| p.0).to_owned()
        } else {
            unit.clone()
        };
        check = String::new();
        if tgt.starts_with("q:") || tgt.starts_with("modal:") {
            subject = tgt;
        } else {
            let path = py_path(&tgt);
            subject = subject_of_path(&shown(&path));
            let real = std::fs::canonicalize(&path).unwrap_or_else(|_| path.clone());
            files = vec![if path.is_absolute() && real.starts_with(root) {
                relative(&real, root)
            } else {
                shown(&path)
            }];
        }
    }
    (check, subject, files, unit)
}

/// What the Rounds section found: its lines, the rounds, the rounds with no reply, the last reply.
struct Rounds {
    lines: Vec<String>,
    kept: Vec<Value>,
    missing: Vec<String>,
    last: String,
}

/// One round's lines: its verdict, what owed it, its reply beside the MANIFEST, its findings marked.
fn round_lines(
    out: &Path,
    i: usize,
    v: &Value,
    r: &str,
    marked: &[(String, String)],
    missing: &mut Vec<String>,
) -> Result<Vec<String>, Fail> {
    let c = field(v, "check", "None");
    let verdict = l7r_guard::guards::event_log_hooks::verdict_of(r);
    let shown_verdict = if verdict.is_empty() {
        "no reply kept"
    } else {
        &verdict
    };
    let mut parts = vec![format!(
        "### Round {i}: {c} ({}; verdict: {shown_verdict})\n",
        field(v, "state", "None")
    )];
    let owed: Vec<String> = v
        .get("owed")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .map(|o| format!("Owed by: {}", py_str(o)))
        .collect();
    if owed.is_empty() {
        parts.push(
            "Owed by: (not recorded - a dispatch before feature 374 kept no occasion)".to_owned(),
        );
    } else {
        parts.extend(owed);
    }
    if r.is_empty() {
        let bundle = v
            .get("manifest")
            .filter(|m| sections::truthy(Some(m)))
            .map_or_else(|| "?".to_owned(), py_str);
        missing.push(format!("round {i} ({c}, bundle {bundle})"));
    } else {
        write(&out.join(format!("round-{i}-{c}.md")), r)?;
        parts.push(format!(
            "The whole reply: `round-{i}-{c}.md` beside this file."
        ));
    }
    if marked.is_empty() {
        let none = if r.is_empty() {
            "- (no reply kept for this round)"
        } else {
            "- (no findings it numbers or bullets - read the whole reply)"
        };
        parts.push(none.to_owned());
    } else {
        parts.extend(marked.iter().map(|(m, f)| format!("- {m}: {f}")));
    }
    parts.push(String::new());
    Ok(parts)
}

/// The Rounds section (`rounds_section`): each dispatch of the check (or of every check, for a reversal) on the subject.
fn rounds_section(
    root: &Path,
    out: &Path,
    check: &str,
    subject: &str,
    trigger: &str,
) -> Result<Rounds, Fail> {
    let state =
        load(&state_path(&root.to_string_lossy()).unwrap_or_else(|| PathBuf::from("/nonexistent")));
    let on = |v: &&Value| {
        v.get("subjects")
            .and_then(Value::as_array)
            .is_some_and(|s| s.iter().any(|x| x.as_str() == Some(subject)))
    };
    let every: Vec<Value> = dispatches(&state).into_iter().filter(on).cloned().collect();
    let of = |v: &Value| v.get("check").and_then(Value::as_str).map(str::to_owned);
    let rounds: Vec<Value> = every
        .iter()
        .filter(|v| check.is_empty() || of(v).as_deref() == Some(check))
        .cloned()
        .collect();
    let others: Vec<(String, String)> = every
        .iter()
        .filter(|v| !check.is_empty() && of(v).as_deref() != Some(check))
        .flat_map(|v| {
            reply::blocks(&reply_of(v))
                .into_iter()
                .map(|(_, o, n)| (o, n))
        })
        .collect();
    let replies: Vec<String> = rounds.iter().map(reply_of).collect();
    let n = if trigger.starts_with("round:") {
        trigger.rsplit_once('@').map_or("", |p| p.1)
    } else {
        ""
    };
    let mut lines = vec![format!(
        "## Rounds - {} on {subject}\n",
        if check.is_empty() {
            "every check"
        } else {
            check
        }
    )];
    if !n.is_empty() {
        lines.push(format!("The owed round is the counter's round {n}: it counts the dispatches let through on this unit in this feature, a first reading of new notes not counted, so the list below - every dispatch kept - may run longer.\n"));
    }
    let mut missing = Vec::new();
    for (i, (v, marked)) in rounds
        .iter()
        .zip(mark_rounds(&replies, &others))
        .enumerate()
    {
        lines.extend(round_lines(
            out,
            i + 1,
            v,
            &replies[i],
            &marked,
            &mut missing,
        )?);
    }
    let last = replies
        .iter()
        .rev()
        .find(|r| !r.is_empty())
        .cloned()
        .unwrap_or_default();
    Ok(Rounds {
        lines,
        kept: rounds,
        missing,
        last,
    })
}

/// The feature directory a round trigger names, if it exists (round:spec-fidelity|413-money-tooltip-on-the-record#1@6).
fn trigger_feature_dir(root: &Path, trigger: &str) -> Option<PathBuf> {
    let c = TRIGGER_FEATURE.captures(trigger).ok().flatten()?;
    let d = root.join("specs").join(&c[1]);
    d.is_dir().then_some(d)
}

/// The room table's questions, in this binary (feature 449 T068), run in the scripts' tree as the Python ran them.
fn cohort(tree: &Path, args: &[&str]) -> Reply {
    let args: Vec<String> = args.iter().map(|a| (*a).to_owned()).collect();
    crate::cohort::cli(&args, tree, "python3")
}

/// What the plan review's rounds add, and the plan as the bundle's file.
fn with_plan(root: &Path, d: &Path, parts: &mut Vec<String>, files: &mut Vec<String>) {
    let (plan_parts, plan) = plan_rounds(d);
    parts.extend(plan_parts);
    if files.is_empty() && plan.is_file() {
        files.push(relative(&plan, root));
    }
}

fn ask_parts(
    run: &mut Run,
    root: &Path,
    out: &Path,
    owed: &Value,
    evidence: &[String],
    parts: &mut Vec<String>,
) -> Result<(), Fail> {
    let detail = field(owed, "detail", "");
    parts.push(format!("## The question\n\n{detail}\n\nA process question the session would have put to the GM. `continue`: go on as the question proposes; `accept`: it stands as it is (a waiver); `process-fault`: the process is wrong - name the fix as `tooling_fix`. Say in `what` exactly what the session does next.\n"));
    parts.extend(evidence_section(out, evidence)?);
    let tree = tree_of(root);
    if cohort(&tree, &["names-fit", &detail]).code == 0 {
        parts.push(cohort(&tree, &["room-table"]).stdout);
    }
    let mut texts = vec![detail];
    for f in evidence {
        let p = py_path(f);
        if p.is_file() {
            texts.push(read_text(&p)?);
        }
    }
    parts.extend(claims_section(run, root, &texts)?);
    Ok(())
}

/// The spec review's and the ask's own sections, with the plan as a file where they read one.
fn review_parts(
    run: &mut Run,
    root: &Path,
    out: &Path,
    (trigger, owed, d): (&str, &Value, Option<&Path>),
    (check, subject): (&str, &str),
    evidence: &[String],
    (parts, files): (&mut Vec<String>, &mut Vec<String>),
) -> Result<(), Fail> {
    if check == "spec-fidelity" && trigger.contains("|plan:") && d.is_some() {
        with_plan(root, d.unwrap_or(root), parts, files);
    } else if check == "spec-fidelity" {
        parts.push(format!("## Rounds - the spec review of {subject}\n\nIts rounds are `spec.md`'s Review history (beside this file): each round's verdict and what was applied. Rule as for any round cap: `accept` lets the spec stand as the last round left it (the review gate takes the ruling as its verdict).\n"));
        parts.extend(spec_rounds(out, subject)?);
    }
    if trigger.starts_with("ask:") {
        ask_parts(run, root, out, owed, evidence, parts)?;
        if let Some(d) = d.filter(|_| hit(&PLAN_REVIEW, &field(owed, "detail", ""))) {
            with_plan(root, d, parts, files);
        }
    }
    Ok(())
}

/// What the loop's record lacks for a ruling, each a line the refusal prints.
fn gaps_of(
    root: &Path,
    out: &Path,
    (trigger, check, subject, unit): (&str, &str, &str, &str),
    (rounds, missing, files, diff): (&[Value], &[String], &[String], &str),
    parts: &mut Vec<String>,
) -> Result<Vec<String>, Fail> {
    let mut gaps: Vec<String> = missing
        .iter()
        .map(|m| format!("no reply kept for {m}"))
        .collect();
    if trigger.starts_with("reversal:")
        && rounds.is_empty()
        && l7r_guard::shared::py_text::strip(diff).is_empty()
    {
        let what = if !subject.is_empty() {
            subject
        } else if !unit.is_empty() {
            unit
        } else {
            "?"
        };
        let history = if files.is_empty() {
            "?".to_owned()
        } else {
            files.join(", ")
        };
        gaps.push(format!(
            "a reversal with no check rounds on {what} and no history of {history}"
        ));
    }
    if trigger.starts_with("round:") && check != "spec-fidelity" && rounds.is_empty() {
        let earlier = review_verdicts(root, out, subject)?;
        if earlier.is_empty() {
            let (c, s) = (
                if check.is_empty() { "?" } else { check },
                if subject.is_empty() { "?" } else { subject },
            );
            gaps.push(format!("no dispatch of {c} on {s} in the check state - a round trigger with no rounds to rule on"));
        } else {
            parts.extend(earlier);
        }
    }
    Ok(gaps)
}

/// The edits between rounds: the last 20 commits touching `files`, then the working tree, as `edits.diff`.
fn edits_part(
    root: &Path,
    out: &Path,
    files: &[String],
    parts: &mut Vec<String>,
) -> Result<String, Fail> {
    if files.is_empty() {
        return Ok(String::new());
    }
    let mut log = vec![
        "log",
        "-p",
        "--format=--- %h %ad %s",
        "--date=iso",
        "-20",
        "--",
    ];
    log.extend(files.iter().map(String::as_str));
    let mut wt = vec!["diff", "--"];
    wt.extend(files.iter().map(String::as_str));
    let diff = g(root, &log) + &g(root, &wt);
    write(
        &out.join("edits.diff"),
        if diff.is_empty() {
            "(no edits)\n"
        } else {
            &diff
        },
    )?;
    parts.push(format!("## Edits between rounds\n\n`edits.diff` beside this file: the last 20 commits touching {}, then the working tree.\n", files.join(", ")));
    Ok(diff)
}

/// A subject's rounds, the last round's EDITs against the files now, and what owes a capped round; `files` is the subject's where none was given.
fn subject_parts(
    root: &Path,
    out: &Path,
    (trigger, check, subject): (&str, &str, &str),
    files: &mut Vec<String>,
    parts: &mut Vec<String>,
) -> Result<Rounds, Fail> {
    let mut found = rounds_section(root, out, check, subject, trigger)?;
    parts.append(&mut found.lines);
    if files.is_empty() {
        *files = subject_files(root, subject);
    }
    if !found.last.is_empty() {
        let edits = last_edits(root, &found.last, files);
        let edits = if edits.is_empty() {
            "- (it proposed none)".to_owned()
        } else {
            edits.join("\n")
        };
        parts.push(format!(
            "## The last answered round's EDITs, against the files now\n\n{edits}\n"
        ));
    }
    if trigger.starts_with("round:") && !found.kept.is_empty() {
        let since = found
            .kept
            .last()
            .and_then(|v| v.get("t"))
            .and_then(Value::as_f64)
            .unwrap_or(0.0);
        parts.extend(capped_round_cause(
            root,
            out,
            (check, subject),
            files,
            since,
            &found.kept,
        )?);
    }
    Ok(found)
}

/// The MANIFEST for `trigger`; `Missing` where a round kept no reply or a reversal has no record, unless `allow_missing` gives the reason.
pub(crate) fn bundle(
    run: &mut Run,
    root: &Path,
    trigger: &str,
    out: &Path,
    allow_missing: &str,
    evidence: &[String],
) -> Result<PathBuf, Stop> {
    let owed = core::owed(root)
        .get(trigger)
        .cloned()
        .unwrap_or_else(|| Value::Object(Map::new()));
    let d = trigger_feature_dir(root, trigger).or_else(|| core::feature_dir(root, trigger));
    if out.exists() {
        remove_tree(out)?;
    }
    std::fs::create_dir_all(out).map_err(fail)?;
    let kind = owed.get("kind").map_or_else(
        || trigger.split(':').next().unwrap_or("").to_owned(),
        py_str,
    );
    let fired = field(
        &owed,
        "detail",
        "(not in arbiter-owed.json) - the unit read from the trigger",
    );
    let mut parts = vec![
        format!("# Round arbiter bundle (feature 375, FR-011)\n\ntrigger: {trigger}\n"),
        format!("Kind: {kind}. Fired: {fired}.\n"),
        format!("Clone root (for `make arbiter-ruled`): {}\n", shown(root)),
    ];
    let (check, subject, mut files, unit) = target(root, trigger, &owed);
    review_parts(
        run,
        root,
        out,
        (trigger, &owed, d.as_deref()),
        (&check, &subject),
        evidence,
        (&mut parts, &mut files),
    )?;
    let mut found = Rounds {
        lines: Vec::new(),
        kept: Vec::new(),
        missing: Vec::new(),
        last: String::new(),
    };
    if !subject.is_empty() && check != "spec-fidelity" {
        found = subject_parts(
            root,
            out,
            (trigger, &check, &subject),
            &mut files,
            &mut parts,
        )?;
    }
    if trigger.starts_with("round:") && !unit.is_empty() {
        parts.extend(round_counter(root, &unit));
    }
    if trigger.starts_with("red-gate@") {
        parts.extend(red_gate_runs(root));
    }
    let diff = edits_part(root, out, &files, &mut parts)?;
    let gaps = gaps_of(
        root,
        out,
        (trigger, &check, &subject, &unit),
        (&found.kept, &found.missing, &files, &diff),
        &mut parts,
    )?;
    if !gaps.is_empty() && allow_missing.is_empty() {
        remove_tree(out)?;
        return Err(Stop::Missing(gaps));
    }
    if !gaps.is_empty() {
        let listed: Vec<String> = gaps.iter().map(|g| format!("- {g}")).collect();
        parts.push(format!(
            "## Missing from the record (bundled anyway: {allow_missing})\n\n{}\n",
            listed.join("\n")
        ));
    }
    parts.extend(flow_sections(
        root,
        out,
        d.as_deref(),
        if subject.is_empty() { &[] } else { &files },
    )?);
    parts.push(feature_section(root, out, d.as_deref(), trigger)?);
    let manifest = out.join("MANIFEST.md");
    write(&manifest, &(parts.join("\n") + "\n"))?;
    Ok(manifest)
}

/// A batch member's subdirectory: the tail of the trigger's slug, never starting with "-" (374 batch 4).
fn batch_dir(trigger: &str) -> String {
    let s = dashed(&trigger.to_lowercase());
    let tail = &s[s.len().saturating_sub(60)..];
    tail.trim_start_matches('-').to_owned()
}

/// The rounds the dispatch counter holds for `unit` in the active feature; 0 where it holds none.
fn counted(root: &Path, unit: &str) -> u64 {
    let state =
        load(&state_path(&root.to_string_lossy()).unwrap_or_else(|| PathBuf::from("/nonexistent")));
    let Some(d) = core::feature_dir(root, "") else {
        return 0;
    };
    if state.get("feature").and_then(Value::as_str)
        != Some(&*d.file_name().unwrap_or_default().to_string_lossy())
    {
        return 0;
    }
    state
        .get("rounds")
        .and_then(|r| r.get(unit))
        .and_then(Value::as_u64)
        .unwrap_or(0)
}

/// Each round trigger the session NAMED whose `@N` is not the unit's next round, with the one to ask about (352's check session).
fn misnumbered(root: &Path, triggers: &[String]) -> Vec<String> {
    let fired = core::owed(root);
    let mut out = Vec::new();
    for t in triggers {
        let unit = core::unit_of(t);
        if unit.is_empty() || fired.contains_key(t) || t.starts_with("round:spec-fidelity|") {
            continue;
        }
        let n = counted(root, &unit);
        let want = format!("round:{unit}@{}", n + 1);
        if *t != want {
            out.push(format!(
                "{t} - the counter holds {n} round(s) of {unit}: ask about `{want}`"
            ));
        }
    }
    out
}

/// ONE bundle for every owed round trigger (FR-017; the GM 2026-10-11), each trigger's own bundle beneath it.
fn batch(
    run: &mut Run,
    root: &Path,
    out: &Path,
    allow_missing: &str,
    extra: &[String],
) -> Result<PathBuf, Stop> {
    let wrong = misnumbered(root, extra);
    if !wrong.is_empty() {
        return Err(Stop::Value(format!(
            "a named round is not its unit's next: {}",
            wrong.join("; ")
        )));
    }
    let triggers = core::batch_triggers(root, extra);
    if triggers.is_empty() {
        return Err(Stop::Value(
            "no round trigger is owed a ruling - nothing to batch".to_owned(),
        ));
    }
    if out.exists() {
        remove_tree(out)?;
    }
    std::fs::create_dir_all(out).map_err(fail)?;
    let (mut gaps, mut rows) = (Vec::new(), Vec::new());
    for t in &triggers {
        let sub = batch_dir(t);
        match bundle(run, root, t, &out.join(&sub), allow_missing, &[]) {
            Ok(_) => rows.push(format!("- `{t}` - its bundle: `{sub}/MANIFEST.md`")),
            Err(Stop::Missing(g)) => gaps.extend(g.iter().map(|g| format!("{t}: {g}"))),
            Err(other) => return Err(other),
        }
    }
    if !gaps.is_empty() {
        return Err(Stop::Missing(gaps));
    }
    let aside = core::aside(root);
    let mut parts = vec![
        format!("# Round arbiter BATCH bundle (feature 375, FR-017)\n\n{} round triggers reached the cap together. Read each unit's own bundle below; they are likely related (one round of the same checks on related pop-ups or pages).\n", triggers.len()),
        format!("Clone root (for `make arbiter-ruled`): {}\n", shown(root)),
        "## The triggers\n".to_owned(),
    ];
    parts.extend(rows);
    if !aside.is_empty() {
        parts.push(
            "\nLeft out - owed in another feature, ruled or rulable there, not in this batch:\n"
                .to_owned(),
        );
        parts.extend(aside.iter().map(|a| format!("- {a}")));
    }
    parts.push("\n## Reply\n\nONE JSON object: the batch's ruling, and an exception for each unit you rule differently:\n\n    {\"ruling\": \"continue|accept|process-fault\", \"why\": \"...\", \"what\": \"...\", \"tooling_fix\": \"<or omit>\",\n     \"triggers\": [<every trigger above>], \"exceptions\": {\"<trigger>\": {\"ruling\": \"...\", \"why\": \"...\", \"what\": \"...\"}}}\n\nRecord it with `make arbiter-ruled BATCH=1 FILE=<that file> AS=round-arbiter`: each trigger is recorded under the batch's ruling or its exception, so each unit's hold, closure and GM-review row work as they do alone.\n".to_owned());
    let manifest = out.join("MANIFEST.md");
    write(&manifest, &(parts.join("\n") + "\n"))?;
    Ok(manifest)
}

fn specs() -> [Spec; 7] {
    [
        Spec::flag("--batch"),
        Spec::value("--triggers"),
        Spec::value("--root"),
        Spec::value("--out"),
        Spec::value("--missing-ok"),
        Spec::value("--evidence"),
        Spec::value("--check-ask"),
    ]
}

fn reply_of_run(out: String, err: String, code: i32) -> Reply {
    Reply {
        stdout: out,
        stderr: err,
        code,
    }
}

/// The bundle's reply: its MANIFEST, or the refusal the Python printed.
fn answer(mut run: Run, done: Result<PathBuf, Stop>) -> Reply {
    match done {
        Ok(manifest) => {
            run.say(&shown(&manifest));
            run.say("arbiter-bundle: dispatch `round-arbiter` on that MANIFEST; it records its own ruling (make arbiter-ruled)");
            run.reply(Ok(0))
        }
        Err(Stop::Value(why)) => {
            run.warn(&format!("arbiter-bundle: {why}"));
            run.reply(Ok(2))
        }
        Err(Stop::Missing(gaps)) => {
            run.warn(&format!("arbiter-bundle: the record lacks what the arbiter rules on - {} (neither the hook's kept reply nor the agent's transcript has it). Bundle anyway, so the arbiter weighs the gap: `make arbiter-bundle TRIGGER=... MISSING_OK=\"<why it is gone>\"`", gaps.join("; ")));
            run.reply(Ok(2))
        }
        Err(Stop::Fail(why)) => run.reply(Err(why)),
    }
}

/// `arbiter bundle ...`.
pub(crate) fn cli(args: &[String]) -> Reply {
    let p = match parse_with(args, &specs(), 1) {
        Ok(p) => p,
        Err(complaint) => {
            return reply_of_run(
                String::new(),
                format!("usage: l7r-gate arbiter bundle: {complaint}\n"),
                2,
            )
        }
    };
    let trigger = p.positional.first().cloned().unwrap_or_default();
    let evidence: Vec<String> = split(p.text("--evidence", ""))
        .into_iter()
        .map(str::to_owned)
        .collect();
    if hit(&MADE_UP, &trigger) {
        return reply_of_run(String::new(), format!("arbiter-bundle: {} is no trigger - a plan review's round is `round:spec-fidelity|plan:<feature dir>#<task>@<n>`, and a guard's refusal names it. For a process question: make arbiter-ask SUBJECT=<slug> WHY=<what>\n", crate::record::bundle::py_repr(&trigger)), 2);
    }
    let check_ask = p.text("--check-ask", "");
    if !check_ask.is_empty() {
        let gaps = sections::pool_unstated(check_ask, &evidence);
        if gaps.is_empty() {
            return reply_of_run(String::new(), String::new(), 0);
        }
        return reply_of_run(String::new(), format!("arbiter-ask: {}. Roll the pool under every route the question offers (`make maps SCOPE=all`) and cite it - in WHY or a FILES= summary - before asking: `make arbiter-ask SUBJECT=... WHY=\"...\" FILES=\"<the summaries>\"`\n", gaps.join("; ")), 2);
    }
    let root = resolve(p.text("--root", "."));
    let slug = {
        let s = dashed(&trigger.to_lowercase());
        s[s.len().saturating_sub(60)..].to_owned()
    };
    let missing_ok = l7r_guard::shared::py_text::strip(p.text("--missing-ok", "")).to_owned();
    if !missing_ok.is_empty() && split(p.text("--missing-ok", "")).len() < 2 {
        return reply_of_run(String::new(), "arbiter-bundle: MISSING_OK needs a reason of two words or more - MISSING_OK=\"<why the reply is gone>\"\n".to_owned(), 2);
    }
    if !p.on("--batch") && trigger.is_empty() {
        return reply_of_run(String::new(), "arbiter-bundle: name the TRIGGER the refusal named, or BATCH=1 for every owed round trigger at once\n".to_owned(), 2);
    }
    let out_arg = p.text("--out", "");
    let mut run = Run::new(&root);
    let done = if p.on("--batch") {
        let extra: Vec<String> = split(p.text("--triggers", ""))
            .into_iter()
            .map(str::to_owned)
            .collect();
        let out = if out_arg.is_empty() {
            default_root().join("arbiter-batch")
        } else {
            py_path(out_arg)
        };
        batch(&mut run, &root, &out, &missing_ok, &extra)
    } else {
        let wrong = misnumbered(&root, std::slice::from_ref(&trigger));
        if wrong.is_empty() {
            let out = if out_arg.is_empty() {
                default_root().join(format!("arbiter-{slug}"))
            } else {
                py_path(out_arg)
            };
            bundle(&mut run, &root, &trigger, &out, &missing_ok, &evidence)
        } else {
            Err(Stop::Value(format!(
                "a named round is not its unit's next: {}",
                wrong.join("; ")
            )))
        }
    };
    answer(run, done)
}

#[cfg(test)]
mod tests;
