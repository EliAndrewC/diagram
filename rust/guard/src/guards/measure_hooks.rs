//! `measure-hooks` (features 146, 162, 328; ported from `scripts/hooks/measure-hooks.sh`, feature 449 T008): THE EXPENSIVE
//! MEASUREMENT IS BATCHED. A second `make test-full` (or `done FULL=1`) in a row with no engine edit and no commit between is
//! refused once; a full gate within three hours of a green one is refused once (a run after a red gate is fixing what it found); a
//! `make perf` outside a timing pair is reminded. `MEASURE_OK` with a reason stands it aside. The refusals' words are the shell's;
//! the reasons behind each rule stand in its comments, kept in git history.
//!
//! Plan T008's decisions: (a) the sanitized command and the last full gate are read in-process, and `gatecost.py`'s median, for
//! the first measurement's reminder, is asked by path; (b) the `git commit` reset reads the command as the shell's greedy `sed` did,
//! its verdict kept; (c) `status` prints the count, as it did.

use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

use serde_json::Value;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log::fire;
use crate::shared::session::Session;
use crate::shared::shape::{strip_heredocs, strip_quotes};
use crate::shared::state::{field, session_file};
use crate::shared::tool::ask;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "measure-hooks",
    events: &["PreToolUse", "status"],
    matcher: "Bash|Edit|Write|NotebookEdit",
    decide,
};

/// What one decision reads besides the event: the streak's file, its budget, the cadence, the clock and the tree's tools.
pub(crate) struct Seams {
    pub streak: PathBuf,
    pub budget: u64,
    pub cadence_s: i64,
    pub now: i64,
    pub tree: PathBuf,
    pub python: String,
}

/// An environment variable read as a number, None where unset or not one.
fn number<T: std::str::FromStr>(k: &str) -> Option<T> {
    std::env::var(k).ok()?.parse().ok()
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let env = |k: &str| std::env::var(k).ok();
    let seams = Seams {
        streak: session_file(
            &event.input,
            env("MEASURE_STATE_DIR"),
            "/tmp/claude-measure",
            "measures",
        ),
        budget: number("MEASURE_BUDGET").unwrap_or(1),
        cadence_s: number("MEASURE_CADENCE_S").unwrap_or(10_800),
        now: SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map_or(0, |d| i64::try_from(d.as_secs()).unwrap_or(0)),
        tree: env("L7R_GUARD_TREE").map_or_else(
            || std::env::current_dir().unwrap_or_default(),
            PathBuf::from,
        ),
        python: "python3".to_owned(),
    };
    judge(event, session, &seams)
}

/// The measurements in the streak since its last reset.
fn count(streak: &Path) -> u64 {
    std::fs::read_to_string(streak)
        .ok()
        .and_then(|s| s.trim().parse().ok())
        .unwrap_or(0)
}

fn reset(streak: &Path) {
    let _ = std::fs::write(streak, "");
}

pub(crate) fn judge(event: &Event, session: &Session, s: &Seams) -> Vec<Answer> {
    if event.name == "status" {
        return vec![Answer::Print(format!(
            "measurements_since_reset={} budget={}",
            count(&s.streak),
            s.budget
        ))];
    }
    let ti = event
        .input
        .get("tool_input")
        .cloned()
        .unwrap_or(Value::Null);
    let cmd = field(&ti, "command");
    let shown: String = cmd.chars().take(200).collect();
    let log = |kind: &str, rule: &str| fire("measure", kind, &shown, rule, &event.input, session);
    if event.tool() != "Bash" {
        // an engine edit resets the streak; a test edit does not - writing one test and re-measuring is the loop this stops
        let fp = field(&ti, "file_path");
        if !fp.contains("/tests/")
            && fp.contains("l7r/")
            && Path::new(fp).extension().is_some_and(|x| x == "py")
        {
            reset(&s.streak);
        }
        return Vec::new();
    }
    match escape_or_refuse(cmd, "MEASURE_OK") {
        Escape::Escaped(why) => {
            fire(
                "measure",
                "escaped",
                &why,
                "measure-ok",
                &event.input,
                session,
            );
            reset(&s.streak);
            return Vec::new();
        }
        Escape::Refused(text) => {
            log("blocked", "MEASURE_OK-no-reason");
            return vec![Answer::Refuse(text)];
        }
        Escape::None => {}
    }
    if greedy_command(&event.input).contains("git commit") {
        reset(&s.streak);
        return Vec::new();
    }
    let scan = Some(strip_quotes(&strip_heredocs(cmd)))
        .filter(|c| !c.is_empty())
        .unwrap_or_else(|| cmd.to_owned());
    let has = |a: &str| scan.contains(a);
    let after = |a: &str, b: &str| {
        scan.find(a)
            .is_some_and(|i| scan[i + a.len()..].contains(b))
    };
    let gate = has("make done") || has("make test-full") || after("make -C", "test-full");
    if !has("make -n") && !has("make --dry-run") && gate {
        if let Some(refused) = cadence(event, s, &log) {
            return vec![refused];
        }
    }
    let perf = has("make perf ") || scan.ends_with("make perf") || after("make -C ", " perf ");
    if perf && !after("LABEL=", "-start") && !after("LABEL=", "-end") {
        log("reminded-perf", "");
        return vec![Answer::Notice(PERF_REMINDER.to_owned())];
    }
    if has("make test-full") || after("make -C", "test-full") || has("done FULL=1") {
        return streak(event, s, &log);
    }
    Vec::new()
}

/// The command as the shell's greedy `sed` read it (T008 decision (b)): from the input's last `"command"` key to its last quote, so
/// a later field's words are read with it - the `git commit` reset's one reader, kept so its verdict is the shell's (FR-002).
fn greedy_command(input: &Value) -> String {
    let raw = input.to_string().replace('\n', " ");
    let Some(key) = raw.rfind("\"command\"") else {
        return String::new();
    };
    let tail = raw[key + "\"command\"".len()..]
        .trim_start()
        .trim_start_matches(':')
        .trim_start();
    let Some(body) = tail.strip_prefix('"') else {
        return String::new();
    };
    body.rfind('"')
        .map_or_else(String::new, |end| body[..end].to_owned())
}

/// The last full gate's end, result and record, in the tree the hook stands in.
fn last_gate(root: &Path) -> Option<(i64, String, String)> {
    let months = std::fs::read_dir(root.join("dev/run-log")).ok()?;
    let mut best: Option<(i64, String, String)> = None;
    for f in months
        .filter_map(Result::ok)
        .filter_map(|m| std::fs::read_dir(m.path()).ok())
        .flatten()
        .filter_map(Result::ok)
    {
        let p = f.path();
        let Some(r) = std::fs::read_to_string(&p)
            .ok()
            .and_then(|t| serde_json::from_str::<Value>(&t).ok())
        else {
            continue;
        };
        let target = field(&r, "target");
        let Some(start) = parse_utc(field(&r, "utc")) else {
            continue;
        };
        if p.extension().is_some_and(|x| x == "json") && (target == "done" || target == "test-full")
        {
            // the record's seconds, as a number or a numeral (the shell's `float(r.get("seconds") or 0)`)
            let secs = r
                .get("seconds")
                .and_then(|v| {
                    v.as_f64()
                        .or_else(|| v.as_str().and_then(|s| s.parse().ok()))
                })
                .unwrap_or(0.0);
            #[expect(
                clippy::cast_possible_truncation,
                reason = "a run's seconds, far below an i64's reach"
            )]
            let end = start + secs as i64;
            if best.as_ref().is_none_or(|b| end > b.0) {
                let name = p
                    .file_name()
                    .map(|n| n.to_string_lossy().into_owned())
                    .unwrap_or_default();
                best = Some((end, field(&r, "result").to_owned(), name));
            }
        }
    }
    best
}

/// `YYYY-mm-ddTHH:MM:SSZ` as seconds since the epoch.
pub(crate) fn parse_utc(stamp: &str) -> Option<i64> {
    let b = stamp.as_bytes();
    if b.len() != 20
        || b[4] != b'-'
        || b[7] != b'-'
        || b[10] != b'T'
        || b[13] != b':'
        || b[16] != b':'
        || b[19] != b'Z'
    {
        return None;
    }
    let num = |r: std::ops::Range<usize>| stamp[r].parse::<i64>().ok();
    let (year, month, day) = (num(0..4)?, num(5..7)?, num(8..10)?);
    let clock = num(11..13)? * 3600 + num(14..16)? * 60 + num(17..19)?;
    // days from the civil date (Howard Hinnant's algorithm), the inverse of `log::civil`
    let year = if month <= 2 { year - 1 } else { year };
    let era = year.div_euclid(400);
    let year_of_era = year - era * 400;
    let day_of_year = (153 * (if month > 2 { month - 3 } else { month + 9 }) + 2) / 5 + day - 1;
    let day_of_era = year_of_era * 365 + year_of_era / 4 - year_of_era / 100 + day_of_year;
    Some((era * 146_097 + day_of_era - 719_468) * 86_400 + clock)
}

/// The work tree `cwd` stands in, and its git directory.
fn tree_of(cwd: &Path) -> (PathBuf, PathBuf) {
    let Some(root) = cwd
        .ancestors()
        .find(|d| d.join(".git").exists())
        .map(Path::to_path_buf)
    else {
        return (cwd.to_path_buf(), cwd.join(".git"));
    };
    let dot = root.join(".git");
    // a worktree's `.git` is a file naming its git directory
    let git = std::fs::read_to_string(&dot)
        .ok()
        .and_then(|t| t.strip_prefix("gitdir: ").map(|g| PathBuf::from(g.trim())))
        .map_or(dot, |g| if g.is_absolute() { g } else { root.join(g) });
    (root, git)
}

/// A full gate within the cadence of a green one, refused once a green run (feature 328, the GM 2026-10-08).
fn cadence(event: &Event, s: &Seams, log: &dyn Fn(&str, &str)) -> Option<Answer> {
    let cwd = Some(field(&event.input, "cwd"))
        .filter(|c| !c.is_empty())
        .map_or_else(
            || std::env::current_dir().unwrap_or_default(),
            PathBuf::from,
        );
    let (root, git) = tree_of(&cwd);
    let (end, result, id) = last_gate(&root)?;
    let age = s.now - end;
    let red = std::fs::metadata(git.join("gate-preflight-red"))
        .and_then(|m| m.modified())
        .ok()
        .and_then(|t| t.duration_since(UNIX_EPOCH).ok())
        .map_or(0, |d| i64::try_from(d.as_secs()).unwrap_or(0));
    let marker = s.streak.with_extension("measures.cadence");
    if result != "green"
        || age >= s.cadence_s
        || red > end
        || std::fs::read_to_string(&marker).ok().as_deref() == Some(id.as_str())
    {
        return None;
    }
    let _ = std::fs::write(&marker, &id); // once per green run: re-issuing goes through
    log("blocked-cadence", "");
    Some(Answer::Refuse(format!(
        "BLOCKED (once): this tree's last full gate was GREEN {} min ago. Batch the expensive measurement; do not re-run it\n\
         after every small round of changes (GM 2026-10-08).\n\n\
         Do this instead, until the batch is done:\n \
         - after each fix: `make quick` (or `make test-file FILE=<the test files your change reaches>`) - seconds, never blocked\n \
         - after a map-changing fix: regenerate the maps it touches (`make map GEN=...`) and `make notes-census`\n \
         - claims: `make claims-owed` / `make claims-bundle` / impl-drift as you go - they are not the gate\n \
         - then ONE `make done` for the whole batch (feature 328: once per 4-5 waves, or before anything lands)\n\n\
         A run after a RED gate is not refused (that is fixing what it found). Re-issuing this command goes through.\n\
         (Escape: MEASURE_OK=\"<why>\" in the command - a batch close, or a measurement a record needs.)\n",
        age / 60
    )))
}

/// The second expensive measurement of a streak refused once; the first reminded, with the last runs' median.
fn streak(_event: &Event, s: &Seams, log: &dyn Fn(&str, &str)) -> Vec<Answer> {
    let n = count(&s.streak) + 1;
    if n > s.budget {
        reset(&s.streak); // block ONCE - re-issuing goes straight through, so this cannot deadlock
        log("blocked", "");
        return vec![Answer::Refuse(STREAK_REFUSAL.to_owned())];
    }
    let _ = std::fs::write(&s.streak, n.to_string());
    if n != 1 {
        return Vec::new();
    }
    log("reminded", "");
    let cost = ask(
        &s.tree,
        &s.python,
        &[
            &s.tree.join("scripts/measure/gatecost.py").to_string_lossy(),
            "done",
            "full",
        ],
        "",
    );
    let line = if cost.ok() && !cost.out.is_empty() {
        format!(
            "The last runs of this measurement recorded a median of {} s. ",
            cost.out
        )
    } else {
        String::new()
    };
    vec![Answer::Notice(format!(
        "REMINDER (measure-hooks, once per batch of work): this is the expensive measurement. {line}The NEXT one in this streak is \
refused unless an engine edit or a git commit comes between - a test edit deliberately does not reset it, because writing one test \
and re-measuring is the loop this guard exists to stop (measured on feature 146: about an hour of re-deriving a coverage worklist \
the session already had). Work from the list instead: write the whole batch, run `make quick` or `make test-file FILE=...` between \
edits, and ask `make cov-file FILE=... MOD=...` which lines one test file actually reaches - it is the only command here that \
answers that, and the commonest wrong answer is that the test covered the guard ABOVE the branch it was aimed at."
    ))]
}

const PERF_REMINDER: &str = "REMINDER (measure-hooks): `make perf` outside a timing pair. If the question is whether a change refuses a \
larger hamlet, `make cohort N=4 SEED=4 HOUSEHOLDS=40` (and HOUSEHOLDS=20) rolls those sizes without the snapshot's timing; the perf \
snapshot belongs to the batch's one pair (LABEL=<feature>-start / -end, feature 328 FR-005).";

const STREAK_REFUSAL: &str = "BLOCKED: that is the second EXPENSIVE measurement in a row with no engine change and no commit between.

This is the expensive one; `make quick`, `make test-file` and `make cov-file` are the cheap loop and are
never blocked, however often they run. Measured on feature 146: 20 test-full runs, about an hour, almost all
of it re-deriving a coverage worklist the session already had written down.
(GUARD_EDIT_OK: feature 162 - the durations that used to be quoted here are gone rather than restated. A
number typed into a guard message in August is wrong in September and nothing tells anybody; `make audit`
and `scripts/measure/gatecost.py` answer from the run log instead.)

Do this instead:
 - ASKING WHICH LINES A TEST REACHES? That is what the third run is usually for, and this is the slowest way
   to be told. `make cov-file FILE=tests/... MOD=l7r/diagram/...` answers it in seconds, for one test file,
   and it is the only command here that answers it at all. It catches the commonest mistake this guard sees:
   a test that covers the guard ABOVE the branch it was aimed at (measured twice on feature 146, at ten
   minutes an answer).
 - You already know what the measurement will say. Work from the LIST, not from the run: write the whole
   batch of tests or fixes in one go.
 - Between edits run `make quick` (or `make test-file FILE=...`) - free, and it catches a broken test at once.
 - Measure ONCE when the batch is done. `CLAUDE.md`: \"Iterate on ONE artifact; run the full test bed exactly
   once, at the end.\"

(Escape: put MEASURE_OK in the command with a reason - a re-run after fixing a red the measurement itself
found, or a deliberate before/after pair for a record. An engine edit or a git commit resets this too.)
";

#[cfg(test)]
mod tests;
