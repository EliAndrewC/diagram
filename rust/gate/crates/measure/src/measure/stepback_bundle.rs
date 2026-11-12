//! The bundle the round arbiter steps back over at the feature's hourly checkpoint (feature 383, plan D11; feature 449 T120, from
//! `stepback_bundle.py`, under `ask:449-T83-scope`).
//!
//! WHY (the GM 2026-10-12: *"convert the hourly check that we are doing here into something that like happens automatically"*). The
//! hourly check one session ran by hand over another's log found loops, guards misfiring and slow steps the working session could not
//! see from inside. Its reading is mechanical, so this does it; the judging is the round arbiter's, from outside, on what this writes.
//!
//! It writes, under `/tmp/l7r-check/step-back-<feature>-<n>/`: `time.md` (where the hour went), `dispatches.md`, `refusals.md`,
//! `task.md`, `words.md` (`stepback_bundle/words.rs`), `fix-yield.md` (`fix_yield.rs`, in process) and `MANIFEST.md`, each in the order
//! the Python wrote them, so a raise part-way leaves the same files. The checkpoint's window and the repository's git directory come
//! from the reviews crate in process (`reviews::gitdir`, `git`, `checkpoint::state`), where the Python reached them through
//! `scripts/reviews_door.py`'s three verbs, which leave with this port (`ask:449-T89-reviews`).
//!
//! `l7r-gate measure step-back <trigger> [--root <clone>] [--transcript <jsonl>] [--since <ISO>] [--until <ISO>] [--out <dir>]`.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use l7r_gate_core::record::args::{parse_with, Spec};
use l7r_gate_reviews::reviews::{checkpoint, git as review_git, gitdir, py_path};
use l7r_guard::shared::log::civil;
use l7r_guard::shared::speckit::splitlines;
use serde_json::{Map, Value};

use super::events::{cmp_f, fixed, head, hhmm, or_text, py_str, ts, Raised, Tally};
use super::fix_yield;
use super::reply;
use super::turn_time::{ts_of, turns};
use crate::Reply;

pub mod words;

type Row = Map<String, Value>;

const OUT: &str = "/tmp/l7r-check";

/// Where a run reads the home directory's records (the transcripts, the guard log) and what time it is.
pub struct Env {
    pub home: PathBuf,
    pub now: f64,
}

/// `_lines`: a JSONL file's objects read with `errors="replace"`, none where it is no file.
///
/// # Errors
///
/// A file that cannot be read: the Python's `OSError`.
pub fn lines(path: &Path) -> Result<Vec<Row>, Raised> {
    if !path.is_file() {
        return Ok(Vec::new());
    }
    let bytes = std::fs::read(path).map_err(|e| format!("OSError: {}: {e}", path.display()))?;
    Ok(splitlines(&String::from_utf8_lossy(&bytes))
        .into_iter()
        .filter_map(|l| match serde_json::from_str(l) {
            Ok(Value::Object(m)) => Some(m),
            _ => None,
        })
        .collect())
}

/// `_iso`: `datetime.fromtimestamp(t, UTC).strftime("%Y-%m-%d %H:%M UTC")`, the microseconds rounded half to even first.
fn iso(t: f64) -> String {
    let mut whole = t.trunc();
    let us = ((t - whole) * 1e6).round_ties_even();
    if us >= 1e6 {
        whole += 1.0;
    } else if us < 0.0 {
        whole -= 1.0;
    }
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "seconds since the epoch, after it"
    )]
    let (y, mo, d, h, mi, _) = civil(whole.max(0.0) as u64);
    format!("{y:04}-{mo:02}-{d:02} {h:02}:{mi:02} UTC")
}

/// `time.strftime("%Y%m%dT%H%M%S", time.gmtime(t))`: `gmtime` floors the seconds.
fn compact(t: f64) -> String {
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "seconds since the epoch, after it"
    )]
    let (year, month, day, hour, minute, second) = civil(t.floor().max(0.0) as u64);
    format!("{year:04}{month:02}{day:02}T{hour:02}{minute:02}{second:02}")
}

/// `_ts(str(e["t"]))`.
fn t_of(e: &Row) -> Result<f64, Raised> {
    ts(&py_str(&e["t"]))
}

/// One line per subagent dispatched in the window: its kind, category, time and verdict (the event log).
///
/// # Errors
///
/// An event time `fromisoformat` cannot read.
pub fn dispatches(events: &[Row], since: f64, until: f64) -> Result<Vec<String>, Raised> {
    // a dict: a restarted id keeps its first place
    let mut started: Vec<(String, (f64, String, String))> = Vec::new();
    let mut out = Vec::new();
    for e in events {
        if !e.contains_key("t") {
            continue;
        }
        let t = t_of(e)?;
        let ev = e.get("ev").and_then(Value::as_str);
        let aid = e.get("aid").map_or_else(|| "None".to_owned(), py_str);
        let at = started.iter().position(|(k, _)| *k == aid);
        if ev == Some("SubagentStart") && since <= t && t <= until {
            let value = (
                t,
                or_text(e.get("agent").unwrap_or(&Value::Null), "?"),
                or_text(e.get("cat").unwrap_or(&Value::Null), ""),
            );
            match at {
                Some(i) => started[i].1 = value,
                None => started.push((aid, value)),
            }
        } else if let (Some("SubagentStop"), Some(i)) = (ev, at) {
            let (_, (t0, agent, cat)) = started.remove(i);
            let verdict = or_text(e.get("verdict").unwrap_or(&Value::Null), "no verdict read");
            out.push(format!(
                "- {} {agent} ({cat}): {} s, {verdict}",
                hhmm(t0),
                fixed(t - t0, 0)
            ));
        }
    }
    out.extend(
        started
            .into_iter()
            .map(|(_, (t0, agent, cat))| format!("- {} {agent} ({cat}): still running", hhmm(t0))),
    );
    Ok(out)
}

/// One line per guard refusal of these sessions in the window (the guard log: a file per firing, named by its UTC time); no session
/// named, every refusal.
#[must_use]
pub fn refusals(sids: &[String], since: f64, until: f64, log: &Path) -> Vec<String> {
    let (lo, hi) = (compact(since), compact(until + 1.0));
    let mut names: Vec<String> = std::fs::read_dir(log)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        // `glob("*.json")`: the suffix as written, case and all, a bare `.json` too
        .filter(|n| n.as_bytes().ends_with(b".json"))
        .collect();
    names.sort();
    let mut out = Vec::new();
    for name in names {
        let stamp = head(&name, 15);
        if !(lo.as_str() <= stamp && stamp <= hi.as_str()) {
            continue;
        }
        let Ok(text) = super::events::read_text(&log.join(&name)) else {
            continue;
        };
        let Ok(Value::Object(r)) = serde_json::from_str::<Value>(&text) else {
            continue;
        };
        let event = r.get("event").and_then(Value::as_str);
        let mine = |k: &str| {
            r.get(k)
                .and_then(Value::as_str)
                .is_some_and(|s| sids.iter().any(|x| x == s))
        };
        // `refused` too: the pair guard's hour refusal logs so (the round arbiter's tooling fix on hour:385-approach-checklist@10)
        if matches!(event, Some("blocked" | "refused"))
            && (sids.is_empty() || mine("session") || mine("sid"))
        {
            let part = |a: usize| name.chars().skip(a).take(2).collect::<String>();
            let detail = or_text(r.get("detail").unwrap_or(&Value::Null), "");
            out.push(format!(
                "- {}:{} {}: {} - {}",
                part(9),
                part(11),
                r.get("guard").map_or_else(|| "None".to_owned(), py_str),
                or_text(r.get("rule").unwrap_or(&Value::Null), ""),
                head(&detail, 200)
            ));
        }
    }
    out
}

/// Every session that worked the feature in the window, busiest first: the `sid`s of its events there - EVERY ONE, NOT THE BUSIEST
/// (the round arbiter's tooling fix on hour:385-approach-checklist@16).
///
/// # Errors
///
/// An event time `fromisoformat` cannot read.
pub fn sessions_of(events: &[Row], since: f64, until: f64) -> Result<Vec<String>, Raised> {
    let mut sids: Tally<String> = Tally::default();
    for e in events {
        if e.get("sid").is_some_and(super::events::truthy) && e.contains_key("t") {
            let t = t_of(e)?;
            if since <= t && t <= until {
                sids.add(&py_str(&e["sid"]), 1.0);
            }
        }
    }
    Ok(sids.most_common().into_iter().map(|(s, _)| s).collect())
}

/// The newest `<projects>/*/<sid>.jsonl` by its modified time.
fn transcript_of(sid: &str, projects: &Path) -> Result<Option<PathBuf>, Raised> {
    if sid.is_empty() {
        return Ok(None);
    }
    let mut hits = Vec::new();
    for e in std::fs::read_dir(projects).into_iter().flatten().flatten() {
        let p = e.path().join(format!("{sid}.jsonl"));
        if p.symlink_metadata().is_ok() {
            let when = std::fs::metadata(&p)
                .and_then(|m| m.modified())
                .map_err(|err| format!("FileNotFoundError: {}: {err}", p.display()))?;
            hits.push((when, p));
        }
    }
    hits.sort_by_key(|h| h.0);
    Ok(hits.pop().map(|h| h.1))
}

/// (the records, merged by time, the sessions read, the sessions whose transcript was not found). A replay's `transcript` is read
/// alone (SC-008); else every session's, each record tagged `_sid` when there is more than one.
/// The records, the sessions read and the sessions not found.
type Records = (Vec<Row>, Vec<String>, Vec<String>);

fn records_of(
    sids: &[String],
    transcript: Option<&Path>,
    projects: &Path,
) -> Result<Records, Raised> {
    if let Some(t) = transcript {
        let stem = t
            .file_stem()
            .map(|s| s.to_string_lossy().into_owned())
            .unwrap_or_default();
        return Ok((lines(t)?, vec![stem], Vec::new()));
    }
    let (mut read, mut missing, mut records) = (Vec::new(), Vec::new(), Vec::new());
    for sid in sids {
        let Some(path) = transcript_of(sid, projects)? else {
            missing.push(sid.clone());
            continue;
        };
        read.push(sid.clone());
        for mut d in lines(&path)? {
            if sids.len() > 1 {
                d.insert("_sid".to_owned(), Value::String(sid.clone()));
            }
            records.push(d);
        }
    }
    let mut keyed = Vec::with_capacity(records.len());
    for d in records {
        let k = d.get("timestamp").map_or(Ok(0.0), ts_of)?;
        keyed.push((k, d));
    }
    keyed.sort_by(|a, b| cmp_f(a.0, b.0));
    Ok((keyed.into_iter().map(|(_, d)| d).collect(), read, missing))
}

/// The times of the records in the window, in order.
fn window_times(records: &[Row], since: f64, until: f64) -> Result<Vec<f64>, Raised> {
    let mut out = Vec::new();
    for d in records {
        if let Some(stamp) = d.get("timestamp") {
            let t = ts_of(stamp)?;
            if since <= t && t <= until {
                out.push(t);
            }
        }
    }
    Ok(out)
}

/// The stretches of the window, five minutes or longer, in which no record read has a timestamp (the round arbiter's tooling fix on
/// hour:395@2).
fn silent_minutes(records: &[Row], since: f64, until: f64) -> Result<Vec<String>, Raised> {
    let mut marks = window_times(records, since, until)?;
    marks.sort_by(|a, b| cmp_f(*a, *b));
    marks.insert(0, since);
    marks.push(until);
    Ok(marks
        .windows(2)
        .filter(|w| w[1] - w[0] >= 300.0)
        .map(|w| format!("{}-{}", hhmm(w[0]), hhmm(w[1])))
        .collect())
}

/// The model's seconds in the window: each reply's gap after the tool result it answers (`turn_time`'s turns).
fn model_time(records: &[Row], since: f64, until: f64) -> Result<f64, Raised> {
    let mut kept = Vec::new();
    for d in records {
        if let Some(stamp) = d.get("timestamp") {
            let t = ts_of(stamp)?;
            if since <= t && t <= until {
                kept.push(Value::Object(d.clone()));
            }
        }
    }
    Ok(turns(&kept)?.iter().fold(0.0, |s, p| s + p.1))
}

/// The bundle's `MANIFEST.md`: the four questions, the two rulings and how to record one; `{trigger}`, `{feature}`, `{since}` and
/// `{until}` filled in one pass, as `str.format` fills them.
const MANIFEST: &str = r#"# Step-back bundle - {trigger}

The feature's hourly checkpoint (feature 383): you are the round arbiter, stepping back over one hour of a session's work on
feature {feature}, {since} to {until}. Read the files beside this MANIFEST and nothing in the repository.

| file | what it is |
|---|---|
| `time.md` | where the hour went: model, tools by command, the rest |
| `dispatches.md` | the subagents dispatched, their time and verdicts |
| `refusals.md` | the guards that refused the session |
| `task.md` | the feature's open tasks |
| `words.md` | the session's own words: replies, commands, edits (no tool output), the newest kept |
| `fix-yield.md` | each tooling fix of the feature: what its tools did since it was made - uses, interventions, likely misfires - and its reading |

Answer four questions:
1. Is the session going in circles, or oscillating between approaches (the same edit made and unmade, a route tried again)?
2. Is it packing features against a number nobody researched - an UNRESEARCHED, GUESS, CONVENTION or convenience size, spacing,
   reach or band - where more room would settle it while the map stays within the research ("Room before packing")? Name the
   number.
3. Is a step slow, or a guard misfiring, enough to be worth a tooling fix? Name the tool and the change. And in `fix-yield.md`,
   does a made fix read "doing nothing"? Then retire it (remove or simplify) as this hour's `tooling_fix`, or keep it with the
   reason in `what`.
4. Is anything too big for the session, which the GM should see?

Rule `continue` (nothing to change) or `change-route` (binding: `what` names the loop or the number, and the route to take -
more room first). Add `tooling_fix` for question 3 (it opens an item the session makes, with its test, or declines as an
overhaul) and `for_gm` for question 4. Only `for_gm` reaches the GM - as a question owed escalation-check, kept only if it is truly his (feature 432).

Record it: write the JSON `{"ruling": ..., "why": ..., "what": ..., "tooling_fix": ..., "fix_minutes": ..., "for_gm": ...}` to a
file (a `tooling_fix` carries `fix_minutes`, the cost it measured) and run
`make arbiter-ruled TRIGGER={trigger} FILE=<that file> AS=round-arbiter`.
"#;

fn write(path: &Path, text: &str) -> Result<(), Raised> {
    std::fs::write(path, text).map_err(|e| format!("OSError: {}: {e}", path.display()))
}

/// `time.md`: the window, the model's time, the tools' by command and the rest.
fn time_md(records: &[Row], read: usize, since: f64, until: f64) -> Result<String, Raised> {
    let tools = words::tool_time(records, since, until)?;
    let model = model_time(records, since, until)?;
    let wall = until - since;
    let mut rows = Vec::new();
    for (k, spent) in tools.spent.most_common().into_iter().take(15) {
        let (long, cmd) = tools
            .longest
            .get(&k)
            .ok_or_else(|| format!("KeyError: {}", l7r_guard::shared::py_text::repr(&k)))?;
        let count = tools.count.get(&k).copied().unwrap_or(0);
        rows.push(format!(
            "- {:5.1} min x{count:<3} {k} (longest {} s: `{cmd}`)",
            spent / 60.0,
            fixed(*long, 0)
        ));
    }
    let rest = wall - model - tools.total;
    let rest = if 0.0 > rest { 0.0 } else { rest };
    Ok(format!(
        "# Where the hour went ({} to {})\n\n{}wall {} min; the model {} min; tools {} min; the rest (waiting on background work, subagents or the GM) {} min\n\n## Tools by command\n\n{}\n",
        iso(since),
        iso(until),
        if read > 1 {
            format!("summed over {read} sessions, which may run side by side and so sum past the hour\n\n")
        } else {
            String::new()
        },
        fixed(wall / 60.0, 0),
        fixed(model / 60.0, 1),
        fixed(tools.total / 60.0, 1),
        fixed(rest / 60.0, 1),
        if rows.is_empty() { "(no tool call in the window)".to_owned() } else { rows.join("\n") }
    ))
}

fn or_none(lines: &[String]) -> String {
    if lines.is_empty() {
        "(none)".to_owned()
    } else {
        lines.join("\n")
    }
}

/// Every event of every feature's log in the clone, or this feature's where there is no log directory.
fn clone_events(g: Option<&Path>, events: &[Row]) -> Result<Vec<Row>, Raised> {
    // EVERY SESSION OF THE CLONE IN THE WINDOW (the round arbiter's tooling fix on hour:395-shrine-building-costs@2): sessions come
    // from every feature's log in the clone
    match g {
        Some(g) if g.join("l7r-events").is_dir() => {
            let mut logs =
                l7r_gate_core::measure::tool_inventory::ending(&g.join("l7r-events"), ".jsonl");
            logs.sort();
            let mut all = Vec::new();
            for p in logs {
                all.extend(lines(&p)?);
            }
            Ok(all)
        }
        _ => Ok(events.to_vec()),
    }
}

/// The feature's first 30 open tasks.
fn open_tasks(tasks: &Path) -> Result<Vec<String>, Raised> {
    if !tasks.is_file() {
        return Ok(Vec::new());
    }
    let text = super::events::read_text(tasks)?;
    Ok(splitlines(&text)
        .into_iter()
        .filter(|l| l.starts_with("- [ ]"))
        .take(30)
        .map(str::to_owned)
        .collect())
}

/// `words.md`'s head line and its words: the sessions read and left out, the cut, the silent stretches.
fn words_md(
    records: &[Row],
    read: &[String],
    missing: &[String],
    window: (f64, f64),
) -> Result<(String, String), Raised> {
    let (since, until) = window;
    let said = words::words(records, since, until, words::WORDS_CAP)?;
    let short = |s: &String| head(s, 8).to_owned();
    let names: Vec<String> = read.iter().map(short).collect();
    let mut top = format!(
        "sessions read: {}",
        if names.is_empty() {
            "none".to_owned()
        } else {
            names.join(", ")
        }
    );
    if !missing.is_empty() {
        let _ = write!(
            top,
            "; left out (no transcript found): {}",
            missing.iter().map(short).collect::<Vec<_>>().join(", ")
        );
    }
    if said.starts_with("[... the hour's earlier words cut") {
        top += "; cut to the cap: the hour's earliest words";
    }
    let gaps = silent_minutes(records, since, until)?;
    if !gaps.is_empty() {
        let _ = write!(
            top,
            "; NO WORDS FOUND for {} of the window - judge those minutes as unseen, not as idle",
            gaps.join(", ")
        );
    }
    Ok((
        top,
        if said.is_empty() {
            "(no transcript found)".to_owned()
        } else {
            said
        },
    ))
}

/// Writes the bundle; returns its `MANIFEST.md`.
///
/// # Errors
///
/// Any raise of the readers, or a file that cannot be written: the files written before it stay, as the Python's did.
pub fn build(
    trigger: &str,
    root: &Path,
    out: &Path,
    window: (f64, f64),
    transcript: Option<&Path>,
    env: &Env,
) -> Result<PathBuf, Raised> {
    let (since, until) = window;
    let feature = trigger.split_once(':').map_or(trigger, |(_, f)| f);
    let feature = feature.rsplit_once('@').map_or(feature, |(f, _)| f);
    let g = gitdir(root);
    let events = match &g {
        Some(g) => lines(&g.join("l7r-events").join(format!("{feature}.jsonl")))?,
        None => Vec::new(),
    };
    let clone_events = clone_events(g.as_deref(), &events)?;
    let sids = sessions_of(&clone_events, since, until)?;
    let projects = env.home.join(".claude/projects");
    let (records, read, missing) = records_of(&sids, transcript, &projects)?;
    std::fs::create_dir_all(out).map_err(|e| format!("OSError: {}: {e}", out.display()))?;
    write(
        &out.join("time.md"),
        &time_md(&records, read.len(), since, until)?,
    )?;
    write(
        &out.join("dispatches.md"),
        &format!(
            "# Subagents dispatched\n\n{}\n",
            or_none(&dispatches(&events, since, until)?)
        ),
    )?;
    let guard_log = env.home.join(".claude/guard-log");
    write(
        &out.join("refusals.md"),
        &format!(
            "# Guard refusals\n\n{}\n",
            or_none(&refusals(&sids, since, until, &guard_log))
        ),
    )?;
    let open = open_tasks(&root.join("specs").join(feature).join("tasks.md"))?;
    write(
        &out.join("task.md"),
        &format!("# Open tasks of {feature}\n\n{}\n", or_none(&open)),
    )?;
    let (top, said) = words_md(&records, &read, &missing, (since, until))?;
    write(
        &out.join("words.md"),
        &format!("# The sessions' own words\n\n{top}\n\n{said}\n"),
    )?;
    // EACH FIX'S YIELD (feature 385 T119, D141; the GM's change 3 of 2026-10-19): a fix that does nothing is retired
    let yields = fix_yield::report(root, &root.join("specs").join(feature), env.now, &guard_log)?;
    write(
        &out.join("fix-yield.md"),
        &format!("# Each tooling fix's yield\n\n{yields}"),
    )?;
    let (from, to) = (iso(since), iso(until));
    let manifest = super::events::re(r"\{(trigger|feature|since|until)\}").replace_all(
        MANIFEST,
        |c: &fancy_regex::Captures| {
            match &c[1] {
                "trigger" => trigger,
                "feature" => feature,
                "since" => from.as_str(),
                _ => to.as_str(),
            }
            .to_owned()
        },
    );
    write(&out.join("MANIFEST.md"), &manifest)?;
    Ok(out.join("MANIFEST.md"))
}

/// A replay's time: `Z` appended where it names no zone (`--since`, `--until`).
fn replay_time(text: &str) -> Result<f64, Raised> {
    if text.ends_with('Z') || text.contains('+') {
        ts(text)
    } else {
        ts(&format!("{text}Z"))
    }
}

/// `l7r-gate measure step-back <trigger> [--root R] [--transcript T] [--since S] [--until U] [--out O]`.
#[must_use]
pub fn cli(args: &[String], env: &Env) -> Reply {
    let specs = ["--root", "--transcript", "--since", "--until", "--out"].map(Spec::value);
    let p = match parse_with(args, &specs, 1) {
        Ok(p) if !p.positional.is_empty() => p,
        Ok(_) => return usage("the following arguments are required: trigger"),
        Err(why) => return usage(&why),
    };
    let trigger = p.positional[0].as_str();
    if !trigger.starts_with("hour:") || !trigger.contains('@') {
        return reply(
            String::new(),
            "stepback-bundle: the trigger is hour:<feature>@<n>\n".to_owned(),
            2,
        );
    }
    match run(trigger, &p, env) {
        Ok(manifest) => reply(
            format!(
                "step-back: {trigger} - dispatch `round-arbiter` on {}\n",
                manifest.display()
            ),
            String::new(),
            0,
        ),
        Err(why) => reply(
            String::new(),
            format!("Traceback (most recent call last):\n  l7r-gate measure step-back\n{why}\n"),
            1,
        ),
    }
}

/// `float(checkpoint_state(root).get("since") or time.time() - 3600)`: the open checkpoint's start, else the last hour.
fn checkpoint_since(state: &Map<String, Value>, now: f64) -> f64 {
    match state.get("since") {
        Some(v) if super::events::truthy(v) => v.as_f64().unwrap_or(0.0),
        _ => now - 3600.0,
    }
}

fn run(
    trigger: &str,
    p: &l7r_gate_core::record::args::Parsed,
    env: &Env,
) -> Result<PathBuf, Raised> {
    let given = p.text("--root", ".");
    let root = review_git(&py_path(given), &["rev-parse", "--show-toplevel"])
        .filter(|t| !t.is_empty())
        .map_or_else(|| py_path(given), PathBuf::from);
    let since = match p.text("--since", "") {
        "" => checkpoint_since(&checkpoint::state(&root, None), env.now),
        s => replay_time(s)?,
    };
    let until = match p.text("--until", "") {
        "" => env.now,
        u => replay_time(u)?,
    };
    let name = trigger
        .split_once(':')
        .map_or("", |(_, n)| n)
        .replace('@', "-");
    let out = match p.text("--out", "") {
        "" => Path::new(OUT).join(format!("step-back-{name}")),
        o => py_path(o),
    };
    let transcript = match p.text("--transcript", "") {
        "" => None,
        t => Some(py_path(t)),
    };
    build(
        trigger,
        &root,
        &out,
        (since, until),
        transcript.as_deref(),
        env,
    )
}

fn usage(why: &str) -> Reply {
    reply(
        String::new(),
        format!("usage: l7r-gate measure step-back [--root ROOT] [--transcript TRANSCRIPT] [--since SINCE] [--until UNTIL] [--out OUT] trigger\nl7r-gate measure step-back: error: {why}\n"),
        2,
    )
}

#[cfg(test)]
mod tests;
