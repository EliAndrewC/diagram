//! The verbs' command lines of `l7r-gate arbiter` - `ruled`, `ruled-batch`, `ask`, `fix` and `nit` - each a ruling or an ask read,
//! recorded through the parent's rules and said (moved from `arbiter.rs` past the 1,000-line bar by 461 T84, unchanged but
//! `ruled`'s part B, which a red gate's landing now owes in its own feature).

use super::*;

fn feature_label(root: &Rooted) -> String {
    core::feature_dir_in(root, "", root.reader()).map_or_else(
        || "none".to_owned(),
        |d| {
            d.file_name()
                .map_or_else(String::new, |n| n.to_string_lossy().into_owned())
        },
    )
}

pub(super) fn ruled_cli(root: &Rooted, trigger: &str, file: &str, who: &str) -> Reply {
    let (row, d) =
        match load_ruling(file).and_then(|r| ruling_at(root, trigger, &r, who, None, false)) {
            Ok(r) => r,
            Err(stop) => return stop.reply("arbiter-ruled"),
        };
    let t = text(&row, "trigger");
    let mut out = format!("arbiter-ruled: {t} - {} (binding; recorded in {}'s arbiter.jsonl; a for_gm question goes to escalation-check: make gm-review)\n", text(&row, "ruling"), home::name_of(&d));
    let owed = crate::plan::approach_ruled_for(root, t, &d, &landing_tasks(&row));
    out.push_str(&plan_accept(&d, &row));
    let claims_review = text(&row, "review");
    if let Some(keys) = claims_review
        .strip_prefix("claims:")
        .filter(|_| text(&row, "ruling") == "accept")
    {
        out.push_str(&claims_accept(root, keys, t));
    }
    out.push_str(&owed_line(owed));
    ok(out)
}

/// A plan review's accept or process-fault applied as its verdict (feature 385 T16, feature 409), a line, or nothing: the blocks and the
/// tasks its question names (feature 451 T92), each block's heading listed - a bare count hid 28 blocks recorded CLEAR for one task's
/// question (`ask:451-T79-third-plan-round`, measured 2026-11-21) - applied in `d`, the feature the ruling was filed in, never one
/// resolved again (feature 451 T179).
fn plan_accept(d: &Path, row: &Value) -> String {
    let t = text(row, "trigger");
    let plan_review = t.starts_with("round:spec-fidelity|plan:") || text(row, "review") == "plan";
    if !plan_review || !matches!(text(row, "ruling"), "accept" | "process-fault") {
        return String::new();
    }
    accepted_line(&crate::plan::arbiter_accept_listed(d, t))
}

/// What [`plan_accept`] says the accept recorded: its scope, each heading, the task verdict.
fn accepted_line(got: &crate::plan::Accepted) -> String {
    let heads: Vec<String> = got
        .blocks
        .iter()
        .map(|k| k.chars().take(60).collect())
        .collect();
    let listed = if heads.is_empty() {
        String::new()
    } else {
        format!(": {}", heads.join("; "))
    };
    let n = got.blocks.len();
    if got.whole {
        return format!("arbiter-ruled: {n} plan block(s) recorded CLEAR, the question the whole plan's{listed} - the accept is the plan's verdict\n");
    }
    if got.tasks.is_empty() && !got.unwritten.is_empty() {
        let blank = got.unwritten.join(" and ");
        return format!("arbiter-ruled: no verdict recorded - {blank}'s section is still the `make task-add` template, which decides nothing; it owes its first plan review once written (451 T462)\n");
    }
    if got.tasks.is_empty() {
        return "arbiter-ruled: 0 plan block(s) recorded CLEAR - the task the question names has no section in plan.md (archived to plan-done.md, or not this feature's), so nothing is the accept's to record\n".to_owned();
    }
    let tasks = got.tasks.join(" and ");
    format!("arbiter-ruled: {n} plan block(s) of {tasks}'s section recorded CLEAR{listed}; and {tasks}'s task verdict CLEAR, declared round-arbiter - the accept is {tasks}'s plan-review verdict, the one the tick, the push and `plan decided` read\n")
}

/// What a ruling owes the active task's part B, a line, or nothing (`if owed: print(owed)`).
/// The tasks a red gate's ruling names as its landing's (461 T84), or none.
fn landing_tasks(row: &Value) -> Vec<String> {
    row.get("tasks")
        .and_then(Value::as_array)
        .map(|a| {
            a.iter()
                .filter_map(Value::as_str)
                .map(str::to_owned)
                .collect()
        })
        .unwrap_or_default()
}

pub(super) fn owed_line(owed: Option<String>) -> String {
    owed.filter(|o| !o.is_empty())
        .map_or_else(String::new, |o| o + "\n")
}

/// `make claims-accept`'s command, in process (`l7r-gate claims accept`, feature 449 T82): its stdout then its stderr.
fn claims_accept(root: &Path, keys: &str, trigger: &str) -> String {
    let args = [
        "--root",
        &root.to_string_lossy(),
        "accept",
        "--keys",
        keys,
        "--trigger",
        trigger,
    ]
    .map(str::to_owned);
    let done = crate::claims::cli(&args);
    format!("{}\n", (done.stdout + &done.stderr).trim())
}

pub(super) fn ruled_batch_cli(root: &Rooted, file: &str, who: &str) -> Reply {
    let rows = match load_ruling(file).and_then(|r| batch_at(root, &r, who, None)) {
        Ok(r) => r,
        Err(stop) => return stop.reply("arbiter-ruled"),
    };
    let mut out = String::new();
    for (row, d) in &rows {
        let t = text(row, "trigger");
        let _ = writeln!(out, "arbiter-ruled: {t} - {}", text(row, "ruling"));
        // a batch's plan-review accept is that review's verdict as a single ruling's is (feature 451 T92: it was recorded, never applied)
        out.push_str(&plan_accept(d, row));
        out.push_str(&owed_line(crate::plan::approach_ruled_for(
            root,
            t,
            d,
            &landing_tasks(row),
        )));
    }
    let _ = writeln!(out, "arbiter-ruled: the batch's {} triggers recorded (binding; each in arbiter.jsonl; a for_gm question goes to escalation-check: make gm-review)", rows.len());
    ok(out)
}

pub(super) fn ask_cli(root: &Rooted, args: &[String]) -> Reply {
    let (subject, why) = (args[0].trim(), args[1].trim());
    let review = args.get(2).map_or("", |r| r.trim());
    if !ASK_SUBJECT.is_match(subject).unwrap_or(false)
        || why.split_whitespace().count() < 2
        || why.chars().count() < 8
    {
        return fail("arbiter-ask: SUBJECT is one short id (letters, digits, . _ -) and WHY the question, two words or more\n".to_owned(), 2);
    }
    if !review.is_empty()
        && !REVIEWS.contains(&review)
        && (!review.starts_with("claims:") || review.len() <= "claims:".len())
    {
        return fail(format!("arbiter-ask: REVIEW= is spec, plan or claims:<key>;<key> (the review whose verdict the ruling stands as), or left out - not {}\n", py_repr(review)), 2);
    }
    let trigger = format!("ask:{subject}");
    // an ask is filed in the feature it names, or the active one, or refused - never feature "" (feature 451 T179)
    let named = match home::named(root, &trigger, review) {
        Ok(d) => d,
        Err(why) => return fail(format!("arbiter-ask: refused - {why}\n"), 2),
    };
    let Some(d) = named.or_else(|| core::feature_dir_in(root, &trigger, root.reader())) else {
        return fail(format!("arbiter-ask: refused - no feature to file {trigger} under: none is active (.specify/feature.json) and its SUBJECT names none (`<NNN>-...`)\n"), 2);
    };
    if home::ruled_in(&d).contains_key(&trigger) {
        return fail(format!("arbiter-ask: {trigger} is already ruled - one ruling per trigger, binding; ask a new SUBJECT for a new question\n"), 1);
    }
    let stands = if review.is_empty() {
        String::new()
    } else {
        format!("(REVIEW={review}: an accept stands as the {review} review's verdict)")
    };
    let detail = format!("{why} {stands}");
    if let Err(why) = core::try_trip_in(
        root,
        &trigger,
        "ask",
        "",
        detail.trim(),
        &Value::Null,
        review,
        root.reader(),
    ) {
        return fail(format!("arbiter-ask: {trigger} was not filed - {why}\n"), 1);
    }
    let mut out = format!("arbiter-ask: {trigger} recorded - the round arbiter rules on it, not the GM (its ruling reaches him only as a kept for_gm question, feature 432); dispatch `round-arbiter` with the MANIFEST below\n");
    if !stands.is_empty() {
        let _ = writeln!(out, "arbiter-ask: {stands}");
    } else if ASK_HINT.is_match(subject).unwrap_or(false)
        || ASK_WORDS.is_match(why).unwrap_or(false)
    {
        out.push_str("arbiter-ask: hint - if this asks about a spec or plan review, ask it with REVIEW=spec or REVIEW=plan, so an accept stands as its verdict (feature 409)\n");
    }
    ok(out)
}

/// `fix done|declined <ids> <note> [<test>] [--landing <task> --files "<paths>" [--feature <f>]]`: the test and the landing's flags
/// (451 T182) after the note, or None for an argument it does not take.
fn fix_args(rest: &[String]) -> Option<(&str, Option<Landing>)> {
    let mut test = "";
    let (mut task, mut feature, mut files) = (None, String::new(), Vec::new());
    let mut it = rest.iter();
    while let Some(a) = it.next() {
        match a.as_str() {
            "--landing" => task = Some(it.next()?.clone()),
            "--feature" => it.next()?.clone_into(&mut feature),
            "--files" => files = it.next()?.split_whitespace().map(str::to_owned).collect(),
            t if test.is_empty() && !t.starts_with("--") => test = t,
            _ => return None,
        }
    }
    Some((
        test,
        task.map(|task| Landing {
            task,
            feature,
            files,
        }),
    ))
}

pub(super) fn fix_cli(root: &Rooted, args: &[String]) -> Reply {
    let status = args[0].as_str();
    let ids: Vec<&str> = args[1].split_whitespace().collect();
    let note = &args[2];
    let Some((test, landing)) = fix_args(&args[3..]) else {
        return fail(format!("usage: fix {status} <trigger(s)> <note> [<test>] [--landing <task> --files \"<the fix's files>\" [--feature <f>]]\n"), 2);
    };
    let label = format!("arbiter-fix-{status}");
    let unknown: Vec<&str> = ids
        .iter()
        .copied()
        .filter(|i| fix_home(root, i).is_none())
        .collect();
    if !unknown.is_empty() || ids.is_empty() {
        let found: Vec<String> = core::spec_dirs(root, "")
            .iter()
            .flat_map(|f| open_fixes(f).into_iter().map(|(t, _)| t))
            .collect();
        let open_now = if found.is_empty() {
            "none".to_owned()
        } else {
            found.join(", ")
        };
        let wanted = if unknown.is_empty() {
            "(no ID)".to_owned()
        } else {
            unknown.join(", ")
        };
        return fail(format!("{label}: refused - no open tooling fix: {wanted}; searched the active feature ({}), the feature an hour trigger names, and every feature; open now: {open_now}\n", feature_label(root)), 1);
    }
    let mut last = Value::Null;
    for id in &ids {
        match settle_fix(root, id, status, note, test, landing.as_ref()) {
            Ok(row) => last = row,
            Err(Stop::Declined(why) | Stop::Refused(why)) => {
                return fail(format!("{label}: refused - {why}\n"), 1)
            }
        }
    }
    if let Some(l) = &landing {
        return ok(format!(
            "{label}: {} fix(es) pending - {}: each settles as `make land F={} T={}` pushes, its done row in that landing's tick commit\n",
            ids.len(),
            ids.join(", "),
            text(&last, "feature"),
            l.task
        ));
    }
    let tail = if status == "declined" {
        " - each a question owed escalation-check (make gm-review)"
    } else {
        ""
    };
    ok(format!(
        "{label}: {} fix(es) settled - {}{tail}\n",
        ids.len(),
        ids.join(", ")
    ))
}

pub(super) fn nit_cli(root: &Rooted, args: &[String]) -> Reply {
    match nit_answers(root, &args[0], &args[1], &args[2]) {
        Err(Stop::Declined(why) | Stop::Refused(why)) => {
            fail(format!("arbiter-nit: refused - {why}\n"), 1)
        }
        Ok(done) => {
            let listed = if done.is_empty() {
                "none owed".to_owned()
            } else {
                done.join(", ")
            };
            ok(format!(
                "arbiter-nit: {} unit(s) answered at today's words - {listed}\n",
                done.len()
            ))
        }
    }
}
