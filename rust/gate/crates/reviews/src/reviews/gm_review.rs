//! `l7r-gate gm-review`: the GM's review after landing - `make gm-review`, `gm-question`, `gm-escalated`, `accept`, `gm-reviewed` and
//! the push's `gm-questions` row (feature 375 FR-012, plan D12; ONE DOOR, feature 432), ported from `scripts/gm_review.py` by feature
//! 449 T91 under `ask:449-T82-claims` (its Q2: the file is its own phase-3 task, and `bundle_door.py`'s write verb leaves with it).
//!
//! WHY (the GM, 2026-10-10): *"I tend to want things to land on main without needing my review"*. A feature lands with its GM's
//! review still open; this lists what waits on him - the questions escalation-check KEPT (his decisions, the one source), the ones
//! still OWED escalation-check (the session's), and the rows he may read and overturn (`listing.rs`, `explain`).
//!
//! THE ONE WRITER (`ask:449-T82-claims`, Q2): `specs/<f>/gm-review.jsonl` and the GM's box in `tasks.md` (`ensure_box`) are written
//! here alone. The round arbiter's `for_gm` (`question`), `make claims-known` (`add_row`) and these commands call it in process, where
//! the arbiter ran the Python by `python3 -c` and claims-known through `bundle_door.py`'s `gm_review_add_row` verb.
//!
//! The Python's refusals keep their text: a `ValueError` is `gm-review: refused - <why>` (exit 1), a feature with no directory
//! `gm-review: no specs/<f>* directory` (exit 1), and what it raised uncaught (a row that is no dict, a write that failed) exit 1 after
//! a `Traceback` line, as the other ports answer one. The usage text is the Python's, byte for byte.

mod listing;
mod py;

pub use self::py::{Raised, R};

use std::io::Write as _;
use std::path::{Component, Path, PathBuf};
use std::process::Command;

use fancy_regex::Regex;
use l7r_guard::shared::py_text::split;
use l7r_guard::shared::pyjson::dumps;
use serde_json::{json, Map, Value};

use self::py::{get, has, py_int, py_str, read_text, text, wrote};
use super::reply;
use crate::Reply;

const ROWS: &str = "gm-review.jsonl";
const QUESTION: &str = "question";

const USAGE: &str = "    gm_review.py list                                   the held rows, and each feature's to-review rows counted
    gm_review.py list F                                 feature F's to-review rows, one line per reason
    gm_review.py explain [F [ROW]]                      what needs the GM; with F, each of its rows (or ROW) in full
    gm_review.py accept F FINDING REASON                a finding accepted with a reason: a to-review row
    gm_review.py reviewed F [ROW G]                     the GM has reviewed F's rows (GM_WORDS= in the environment: his words)
    gm_review.py reviewed-row F ROW                     the GM has reviewed row ROW of F alone
    gm_review.py question F TEXT SOURCE                 a question for the GM, owed escalation-check (feature 432)
    gm_review.py escalated F ROW KEEP|CUT REASON [LATER] escalation-check's verdict on question ROW of F (LATER: a kept row superseded)

";

/// Where a run reads and writes: the repository (`root`, the working directory), the tree whose closing list and `impl_check.py` the
/// closing check reads (the gate's own, `L7R_GATE_TREE`) and the interpreter `impl_check.py` runs under, the GM's words (`GM_WORDS`), and the width a listing is fitted to.
struct Ctx<'a> {
    root: &'a Path,
    tree: &'a Path,
    python: &'a str,
    words: &'a str,
    columns: &'a dyn Fn(usize) -> usize,
}

/// A pattern the code itself writes (a feature's number is all it takes in), never one that fails to compile.
#[must_use]
fn re(p: &str) -> Regex {
    Regex::new(p).unwrap_or_else(|_| unreachable!("a pattern of the code's own"))
}

/// A feature's number: `int(d.name.split("-", 1)[0])`.
fn num(d: &Path) -> R<i128> {
    py_int(name(d).split('-').next().unwrap_or_default())
}

/// `d.name` as Python's `Path` names it (a `..` is a name; a `.` is dropped when the path is made; `/` has none).
#[must_use]
pub(crate) fn name(d: &Path) -> String {
    match d.components().next_back() {
        Some(Component::Normal(n)) => n.to_string_lossy().into_owned(),
        Some(Component::ParentDir) => "..".to_owned(),
        _ => String::new(),
    }
}

/// The one GM-review box a feature carries, in the one form `l7r-gate speckit-todo --holding` honors.
fn gm_box(d: &Path) -> R<String> {
    Ok(format!(
        "- [ ] GM review (make gm-reviewed F={}) [lands-open]",
        num(d)?
    ))
}

/// The feature's rows, each line that parses; a line that does not is passed over, as the Python's `except ValueError: continue`.
fn rows(d: &Path) -> R<Vec<Value>> {
    let f = d.join(ROWS);
    if !f.is_file() {
        return Ok(Vec::new());
    }
    let t = read_text(&f)?;
    Ok(crate::record::py_lines(&t)
        .into_iter()
        .filter_map(|l| serde_json::from_str(l).ok())
        .collect())
}

/// A row as `json.dumps(row, ensure_ascii=False)` writes it, with its newline.
fn line(row: &Value) -> String {
    dumps(row, None, false) + "\n"
}

fn append(d: &Path, row: &Value) -> R<()> {
    let f = d.join(ROWS);
    let done = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(&f)
        .and_then(|mut fh| fh.write_all(line(row).as_bytes()));
    wrote(&f, done)
}

fn write_rows(d: &Path, rs: &[Value]) -> R<()> {
    let f = d.join(ROWS);
    let done = std::fs::write(&f, rs.iter().map(line).collect::<String>());
    wrote(&f, done)
}

/// Whether any row still waits on the GM (`"reviewed" not in r`).
fn any_open(rs: &[Value]) -> R<bool> {
    for r in rs {
        if !has(r, "reviewed")? {
            return Ok(true);
        }
    }
    Ok(false)
}

/// Append `row` to the feature's `gm-review.jsonl` and add the GM's review box with it: `make claims-known`'s write, called in process
/// by the claims tools (feature 449 T91; until then `bundle_door.py`'s `gm_review_add_row` verb, `ask:449-T82-claims`).
///
/// # Errors
///
/// Where the Python raised: the file cannot be written, its bytes or the feature's tasks are no UTF-8, a row is no dict, the feature's
/// name holds no number.
pub fn add_row(d: &Path, row: &Value) -> R<bool> {
    append(d, row)?;
    ensure_box(d)
}

/// Add the GM-review box to `tasks.md` when the feature has an open row and no box yet; true when added.
fn ensure_box(d: &Path) -> R<bool> {
    let tasks = d.join("tasks.md");
    if !tasks.is_file() || !any_open(&rows(d)?)? {
        return Ok(false);
    }
    let text = read_text(&tasks)?;
    let open = gm_box(d)?;
    let ticked = open.replacen("- [ ] ", "- [x] ", 1);
    // ...a new row after the GM reviewed the rest reopens his box (feature 432: a question carried into a closed feature must not
    // sit behind a ticked box)
    if text.contains(&ticked) {
        wrote(&tasks, std::fs::write(&tasks, text.replace(&ticked, &open)))?;
        return Ok(true);
    }
    if text.contains("GM review (make gm-reviewed") {
        return Ok(false);
    }
    let body = format!(
        "{}\n{open}\n      research: rendering\n      verify: the GM reviewed every row (make gm-review lists them)\n",
        text.trim_end_matches('\n')
    );
    wrote(&tasks, std::fs::write(&tasks, body))?;
    Ok(true)
}

/// `time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())`.
fn utc_now() -> String {
    crate::record::repo::utc_now()
}

fn today() -> String {
    utc_now()[..10].to_owned()
}

/// A question for the GM, written OWED escalation-check (feature 432, FR-002); its row number. The round arbiter's `for_gm` asks it
/// in process with the ruling's own time (`now`).
///
/// # Errors
///
/// A question under four words is refused; otherwise where the Python raised, as [`add_row`].
pub fn question(d: &Path, question: &str, source: &str, now: Option<&str>) -> R<usize> {
    if split(question).len() < 4 {
        return Err(Raised::Refused(
            "a question for the GM is a sentence he can answer - four words or more".to_owned(),
        ));
    }
    let row = json!({"kind": QUESTION, "status": "owed", "question": question, "source": source,
                     "utc": now.map_or_else(utc_now, str::to_owned)});
    let n = rows(d)?.len();
    append(d, &row)?;
    ensure_box(d)?;
    Ok(n)
}

/// `{**r, **extra}`: a row with keys set, a key it had keeping its place.
fn merged(r: &Value, extra: &[(&str, Value)]) -> R<Value> {
    let Value::Object(m) = r else {
        return Err(Raised::Trace(format!(
            "TypeError: 'dict' object expected, not {}",
            py_str(r)
        )));
    };
    let mut m: Map<String, Value> = m.clone();
    for (k, v) in extra {
        m.insert((*k).to_owned(), v.clone());
    }
    Ok(Value::Object(m))
}

/// `make gm-escalated`: escalation-check's verdict on an owed question. KEEP holds it for the GM; CUT closes it, the reason kept on the
/// row (feature 432, FR-002). A KEPT question the GM has not reviewed is CUT only as superseded by a later question row of the same
/// feature (`superseded_by`, the round arbiter's `ask:444-gm-review-supersede`, 2026-11-05).
fn escalated(
    d: &Path,
    row: i128,
    verdict: &str,
    reason: &str,
    now: Option<&str>,
    superseded_by: Option<i128>,
) -> R<String> {
    let mut rs = rows(d)?;
    let n = name(d);
    let count = i128::try_from(rs.len()).unwrap_or(i128::MAX);
    let at = |i: i128| usize::try_from(i).unwrap_or(usize::MAX);
    let refused = |m: String| Err(Raised::Refused(m));
    let is_question =
        |r: &Value| -> R<bool> { Ok(get(r, "kind")?.and_then(Value::as_str) == Some(QUESTION)) };
    if !(0..count).contains(&row) || !is_question(&rs[at(row)])? {
        return refused(format!(
            "ROW={row} is no question of {n} - make gm-review lists the owed ones"
        ));
    }
    let mut reason = reason.to_owned();
    if let Some(later) = superseded_by {
        if verdict != "CUT" {
            return refused("SUPERSEDED_BY closes a question: VERDICT=CUT".to_owned());
        }
        if !(row < later && later < count && is_question(&rs[at(later)])?) {
            return refused(format!(
                "SUPERSEDED_BY={later} is no later question of {n} than ROW={row}"
            ));
        }
        let kept = get(&rs[at(row)], "status")?.and_then(Value::as_str) == Some("kept");
        if !kept || py::truthy(get(&rs[at(row)], "reviewed")?) {
            return refused(format!(
                "ROW={row} of {n} is {}: SUPERSEDED_BY closes a kept question the GM has not reviewed",
                status_str(&rs[at(row)])?
            ));
        }
        reason = format!("superseded by row {later}: {reason}");
    } else if get(&rs[at(row)], "status")?.and_then(Value::as_str) != Some("owed") {
        return refused(format!(
            "ROW={row} of {n} is already {} - a kept question the record overturned is closed with SUPERSEDED_BY=<its later row>",
            status_str(&rs[at(row)])?
        ));
    }
    if !matches!(verdict, "KEEP" | "CUT") {
        return refused("VERDICT is KEEP or CUT, escalation-check's".to_owned());
    }
    if split(&reason).len() < 2 {
        return refused("REASON is escalation-check's, two words or more".to_owned());
    }
    let when = now.map_or_else(utc_now, str::to_owned);
    let r = &rs[at(row)];
    rs[at(row)] = if verdict == "KEEP" {
        merged(
            r,
            &[
                ("status", json!("kept")),
                ("kept", json!(when)),
                ("escalation", json!(reason)),
            ],
        )?
    } else {
        merged(
            r,
            &[
                ("status", json!("cut")),
                ("escalation", json!(reason)),
                ("reviewed", json!(py::head(&when, 10))),
            ],
        )?
    };
    write_rows(d, &rs)?;
    Ok(if verdict == "KEEP" {
        format!(
            "question {row} of {n} KEPT - it is the GM's decision now: name it in this turn's final message as \"{}#{row}\" with the question",
            num(d)?
        )
    } else {
        format!("question {row} of {n} CUT - closed, not the GM's: {reason}")
    })
}

/// `{rs[row].get('status')}` in a message: `None` where the row has none.
fn status_str(r: &Value) -> R<String> {
    Ok(get(r, "status")?.map_or_else(|| "None".to_owned(), py_str))
}

/// A finding accepted with a reason - the work goes on, and the GM may overturn it after landing (FR-012).
fn accept(d: &Path, finding: &str, reason: &str) -> R<Value> {
    if split(reason).len() < 2 {
        return Err(Raised::Refused(
            "REASON needs two words or more - the GM reads it".to_owned(),
        ));
    }
    let row = json!({"kind": "accepted", "finding": finding, "why": reason, "utc": utc_now()});
    append(d, &row)?;
    ensure_box(d)?;
    Ok(row)
}

/// The words check every review shares: the GM's own, two words or more.
fn check_words(words: &str) -> R<()> {
    if !words.is_empty() && split(words).len() < 2 {
        return Err(Raised::Refused(
            "WORDS are the GM's own, two words or more".to_owned(),
        ));
    }
    Ok(())
}

/// The first truthy of a row's values, `""` where none is (`a or b or ""`).
fn first_truthy(r: &Value, keys: &[&str]) -> R<Value> {
    for k in keys {
        let v = get(r, k)?;
        if py::truthy(v) {
            return Ok(v.cloned().unwrap_or_default());
        }
    }
    Ok(json!(""))
}

/// `" - ".join(x for x in parts if x)`, each part a string (a truthy part of another type raised `TypeError`).
fn joined(parts: &[Value]) -> R<String> {
    let mut out = Vec::new();
    for p in parts.iter().filter(|p| py::truthy(Some(p))) {
        out.push(
            p.as_str()
                .ok_or_else(|| {
                    Raised::Trace("TypeError: sequence item: expected str instance".to_owned())
                })?
                .to_owned(),
        );
    }
    Ok(out.join(" - "))
}

/// The GM has reviewed `d`'s rows: each marked reviewed; an overturned one becomes an open row of the feature `to`; the GM-review box
/// is ticked - through the closing check, since it may close the feature (FR-009). `words`, when a session marks the review on the
/// GM's behalf after discussing it with him, are his words, kept on each row it marks.
fn reviewed(ctx: &Ctx, d: &Path, overturn: Option<(i128, &Path)>) -> R<Vec<String>> {
    check_words(ctx.words)?;
    let mut rs = rows(d)?;
    let mut msgs = Vec::new();
    let today = today();
    if let Some((o, to)) = overturn {
        let count = i128::try_from(rs.len()).unwrap_or(i128::MAX);
        if !(0..count).contains(&o) {
            return Err(Raised::Refused(
                "OVERTURN=<row number> needs TO=<an open feature>".to_owned(),
            ));
        }
        let at = usize::try_from(o).unwrap_or(usize::MAX);
        let r = &rs[at];
        let finding = format!(
            "overturned by the GM: {}",
            joined(&[
                first_truthy(r, &["why", "tooling_fix"])?,
                get(r, "note")?.cloned().unwrap_or(json!(""))
            ])?
        );
        let block = first_truthy(r, &["trigger"])?;
        let block = if py::truthy(Some(&block)) {
            block
        } else {
            get(r, "finding")?.cloned().unwrap_or(Value::Null)
        };
        let found = json!({"check": "gm-review", "file": name(d), "block": block, "finding": finding, "status": "open"});
        let f = to.join("found.jsonl");
        let done = std::fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(&f)
            .and_then(|mut fh| fh.write_all(line(&found).as_bytes()));
        wrote(&f, done)?;
        msgs.push(format!("row {o} overturned - an open row of {}", name(to)));
        // the overturned row ALONE is reviewed: the rest of the feature's rows still wait on the GM (2026-10-12, overturning 343's two
        // declined fixes would have marked its 83 other rows reviewed by the GM)
        rs[at] = merged(
            r,
            &[
                ("reviewed", json!(today)),
                ("overturned_to", json!(name(to))),
            ],
        )?;
        write_rows(d, &rs)?;
        if any_open(&rs)? {
            return Ok(msgs);
        }
    }
    let tasks = d.join("tasks.md");
    let text = if tasks.is_file() {
        read_text(&tasks)?
    } else {
        String::new()
    };
    let f = num(d)?;
    let last_box = re(&format!(
        r"(?m)^- \[ \] GM review \(make gm-reviewed F={f}\)"
    ));
    if last_box.is_match(&text).unwrap_or(false) && text.matches("- [ ] ").count() == 1 {
        let why = close_reasons(ctx, d)?;
        if !why.is_empty() {
            return Err(Raised::Refused(format!(
                "the GM's box closes the feature, and: {}",
                why.join("; ")
            )));
        }
    }
    let mut out = Vec::with_capacity(rs.len());
    for r in &rs {
        let r = merged(r, &[])?; // `{**r, ...}`: a row that is no dict raised first
        let mut extra = vec![(
            "reviewed",
            get(&r, "reviewed")?
                .cloned()
                .unwrap_or_else(|| json!(today)),
        )];
        if !ctx.words.is_empty() && !has(&r, "reviewed")? {
            extra.push(("gm_words", json!(ctx.words)));
        }
        out.push(merged(&r, &extra)?);
    }
    write_rows(d, &out)?;
    // ...THE BOX AS WRITTEN, with or without its `[lands-open]` (feature 432: 415's box was written without it, so this marked its rows
    // reviewed, said so, and left the box open)
    let open_box = re(&format!(
        r"(?m)^- \[ \] (GM review \(make gm-reviewed F={f}\).*)$"
    ));
    if open_box.is_match(&text).unwrap_or(false) {
        let ticked = open_box.replacen(&text, 1, "- [x] $1").into_owned();
        wrote(&tasks, std::fs::write(&tasks, ticked))?;
    }
    msgs.push(format!("{} row(s) of {} reviewed", rs.len(), name(d)));
    Ok(msgs)
}

/// `close_check.reasons(d, root / "specs")`, in process since feature 449 T127 ported the closing check here (`super::closing`), where
/// T91 ran `close_check.py --reasons-json` by path; what the Python raised is a trace, as its raise was.
fn close_reasons(ctx: &Ctx, d: &Path) -> R<Vec<String>> {
    let tools = super::closing::Tools {
        tree: ctx.tree,
        python: ctx.python,
    };
    // what impl_check printed on a passing run is dropped, as the by-path run of T91 kept it to itself (the coordinator's ruling on
    // T127); a failure still carries it inside the trace
    super::closing::reasons(&tools, &ctx.root.join("specs"), &[d.to_path_buf()])
        .map(|mut found| found.each.pop().unwrap_or_default())
        .map_err(|e| Raised::Trace(format!("close_check.reasons raised:\n{e}")))
}

/// Row `row` of `d` alone is reviewed; the feature's other rows still wait on the GM, and its box stays open while they do.
fn reviewed_row(ctx: &Ctx, d: &Path, row: i128) -> R<String> {
    check_words(ctx.words)?;
    let mut rs = rows(d)?;
    let count = i128::try_from(rs.len()).unwrap_or(i128::MAX);
    if !(0..count).contains(&row) {
        return Err(Raised::Refused(format!(
            "ROW={row}: {} has rows 0-{}",
            name(d),
            count - 1
        )));
    }
    let at = usize::try_from(row).unwrap_or(usize::MAX);
    let mut extra = vec![("reviewed", json!(today()))];
    if !ctx.words.is_empty() {
        extra.push(("gm_words", json!(ctx.words)));
    }
    rs[at] = merged(&rs[at], &extra)?;
    write_rows(d, &rs)?;
    let mut waiting = 0;
    for r in &rs {
        waiting += usize::from(!has(r, "reviewed")?);
    }
    Ok(format!(
        "row {row} of {} reviewed; {waiting} still wait on the GM",
        name(d)
    ))
}

/// `root / "specs" / f` as `pathlib` makes it: a `.` part and a trailing slash dropped, an absolute `f` replacing the base.
fn py_join(base: &Path, f: &str) -> PathBuf {
    let mut out = base.to_path_buf();
    for c in Path::new(f).components() {
        match c {
            Component::CurDir => {}
            Component::RootDir => out = PathBuf::from("/"),
            other => out.push(other.as_os_str()),
        }
    }
    out
}

/// A feature directory by number (`NNN-*`, the first in order) or by name; `SystemExit` where there is none.
fn feature(root: &Path, f: &str) -> R<PathBuf> {
    let specs = root.join("specs");
    // `f.isdigit()`: a non-ASCII digit such as `²` takes the number's road too, where `int()` refuses it
    let hit = if !f.is_empty()
        && f.chars()
            .all(|c| c.is_ascii_digit() || (c.is_numeric() && !c.is_ascii()))
    {
        let prefix = format!("{:03}-", py_int(f)?);
        let mut hits: Vec<PathBuf> = std::fs::read_dir(&specs)
            .into_iter()
            .flatten()
            .flatten()
            .filter(|e| e.file_name().to_string_lossy().starts_with(&prefix))
            .map(|e| e.path())
            .collect();
        hits.sort();
        hits.into_iter().next()
    } else {
        Some(py_join(&specs, f))
    };
    hit.filter(|d| d.is_dir())
        .ok_or_else(|| Raised::Exit(format!("gm-review: no specs/{f}* directory")))
}

/// The questions still owed escalation-check in the features this push changes (`specs/<f>/gm-review.jsonl` in the delta against
/// `origin/main`, committed or not): a feature does not land with one unjudged (feature 432, FR-002).
fn owed_in_delta(root: &Path) -> R<Vec<String>> {
    let git = |args: &[&str]| {
        Command::new("git")
            .arg("-C")
            .arg(root)
            .args(args)
            .output()
            .ok()
            .filter(|o| o.status.success())
            .map(|o| String::from_utf8_lossy(&o.stdout).into_owned())
    };
    let base = git(&["merge-base", "HEAD", "origin/main"]).unwrap_or_default();
    let base = base.trim();
    let mut paths: Vec<String> = Vec::new();
    if !base.is_empty() {
        paths.extend(
            git(&["diff", "--name-only", base])
                .iter()
                .flat_map(|o| split(o))
                .map(str::to_owned),
        );
    }
    let others = git(&["ls-files", "--others", "--exclude-standard"]).unwrap_or_default();
    paths.extend(split(&others).into_iter().map(str::to_owned));
    let mut feats: Vec<String> = paths
        .iter()
        .filter(|p| p.starts_with("specs/") && p.ends_with(&format!("/{ROWS}")))
        .map(|p| p.split('/').nth(1).unwrap_or_default().to_owned())
        .collect();
    feats.sort();
    feats.dedup();
    let mut out = Vec::new();
    for f in feats {
        let d = root.join("specs").join(&f);
        for (i, r) in rows(&d)?.iter().enumerate() {
            if get(r, "kind")?.and_then(Value::as_str) == Some(QUESTION)
                && get(r, "status")?.and_then(Value::as_str) == Some("owed")
                && !has(r, "reviewed")?
            {
                out.push(format!("{}#{i}: {}", num(&d)?, text(r, "question")?));
            }
        }
    }
    Ok(out)
}

/// Each of `items` on its own line after `prefix`.
fn lines(prefix: &str, items: &[String]) -> String {
    let mut out = String::new();
    for item in items {
        out.push_str(prefix);
        out.push_str(item);
        out.push('\n');
    }
    out
}

/// The command line, as `gm_review.py`'s `main` read it.
fn run(args: &[String], ctx: &Ctx) -> R<Reply> {
    let a: Vec<&str> = args.iter().map(String::as_str).collect();
    let said = |s: String| Ok(reply(s, String::new(), 0));
    match (a.first().copied(), a.len()) {
        (Some("list"), 1 | 2) => said(listing::listing(ctx, a.get(1).copied().unwrap_or(""))?),
        (Some("explain"), 1..=3) => said(listing::explain(
            ctx,
            a.get(1).copied().unwrap_or(""),
            a.get(2).copied().unwrap_or(""),
        )?),
        (Some("accept"), 4) => {
            accept(&feature(ctx.root, a[1])?, a[2], a[3])?;
            said(
                "accept: recorded - a row the GM may read and overturn (make gm-review)\n"
                    .to_owned(),
            )
        }
        (Some("reviewed"), 2 | 4) => {
            let over = if a.len() == 4 {
                Some((py_int(a[2])?, feature(ctx.root, a[3])?))
            } else {
                None
            };
            let d = feature(ctx.root, a[1])?;
            let msgs = reviewed(ctx, &d, over.as_ref().map(|(o, to)| (*o, to.as_path())))?;
            said(lines("gm-reviewed: ", &msgs))
        }
        (Some("question"), 4) => {
            let d = feature(ctx.root, a[1])?;
            let n = question(&d, a[2], a[3], None)?;
            said(format!(
                "gm-question: row {n} of {} - owed escalation-check before it reaches the GM (make gm-escalated F={} ROW={n})\n",
                name(&d),
                num(&d)?
            ))
        }
        (Some("owed-check"), 1) => {
            let owed = owed_in_delta(ctx.root)?;
            if owed.is_empty() {
                return said(String::new());
            }
            let mut err = lines("gm-review: owed escalation-check - ", &owed);
            err += "gm-review: dispatch escalation-check on each, then make gm-escalated F=<n> ROW=<n> VERDICT=KEEP|CUT REASON=\"...\"\n";
            Ok(reply(String::new(), err, 1))
        }
        (Some("escalated"), 5 | 6) => {
            let later = match a.get(5) {
                Some(l) if !l.is_empty() => Some(py_int(l)?),
                _ => None,
            };
            let d = feature(ctx.root, a[1])?;
            let row = py_int(a[2])?;
            said(format!(
                "gm-escalated: {}\n",
                escalated(&d, row, a[3], a[4], None, later)?
            ))
        }
        (Some("reviewed-row"), 3) => {
            let d = feature(ctx.root, a[1])?;
            let row = py_int(a[2])?;
            said(format!("gm-reviewed: {}\n", reviewed_row(ctx, &d, row)?))
        }
        _ => Ok(reply(String::new(), USAGE.to_owned(), 2)),
    }
}

/// `l7r-gate gm-review <verb> ...` in `ctx`.
#[must_use]
fn cli_in(args: &[String], ctx: &Ctx) -> Reply {
    match run(args, ctx) {
        Ok(r) => r,
        Err(Raised::Refused(m)) => reply(String::new(), format!("gm-review: refused - {m}\n"), 1),
        Err(Raised::Exit(m)) => reply(String::new(), format!("{m}\n"), 1),
        Err(Raised::Trace(m)) => reply(
            String::new(),
            format!("Traceback (most recent call last):\n  l7r-gate gm-review\n{m}\n"),
            1,
        ),
    }
}

/// `l7r-gate gm-review <verb> ...` in the working directory, with this process's environment.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let root = std::env::current_dir().unwrap_or_default();
    let tree = std::env::var_os("L7R_GATE_TREE").map_or_else(|| root.clone(), PathBuf::from);
    let words = std::env::var("GM_WORDS").unwrap_or_default();
    let ctx = Ctx {
        root: &root,
        tree: &tree,
        python: "python3",
        words: l7r_guard::shared::py_text::strip(&words),
        columns: &py::columns,
    };
    cli_in(args, &ctx)
}

#[cfg(test)]
mod tests;
