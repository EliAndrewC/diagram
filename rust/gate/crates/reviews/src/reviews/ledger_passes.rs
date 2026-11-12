//! `l7r-gate reviews ledger-owed`: every pass of every check owes its row in the review ledger (feature 371; ported from
//! `scripts/reviews/ledger_owed.py` by feature 449 T83, `ask:449-T83-scope`).
//!
//! WHY (the GM, 2026-10-10: *"a log of when our subagent checks find something that needs to be changed and when they don't, so that we
//! can see how often they are paying off"*). The log is `dev/review-ledger.md`'s measured table, and nothing made its rows get written:
//! feature 328 ran 26 glyph checks and wrote none of their rows, rebuilt by hand at a batch's close. So every check's pass is logged when
//! the agent returns (the guards' `checks::passes`, into `<git common dir>/check-passes.jsonl`, with its cost cells computed as `make
//! review-cost` computes them), and a pass is ANSWERED by a measured row carrying its check and those same cells - the table copies its
//! cost from `make review-cost`, never types it, so the cells identify the pass (two same-day rounds of one check on one subject are two
//! passes with two costs).
//!
//! ```text
//! ledger-owed [--log <jsonl>] [--ledger <md>]          list the unanswered passes, each with the row to add
//! ledger-owed --write "<where the session recorded what it did>" [--session <sid>]
//!                                                      append each unanswered pass's row, filled from the agent's own reply
//!                                                      (the page-session runner, at each session's end)
//! ledger-owed ... --refuse                             exit 1 while any is unanswered (the push)
//! ledger-owed --write-plan-reviews                     append the row of each owed plan review that recorded its verdict (385 T72)
//! ledger-passes                                        the settled passes as JSON (`feature_report.py`'s reading)
//! ```
//!
//! Escape at the push: `LEDGER_ROWS_OK="<reason>"` in sync-with-main's environment, recorded in the bypass log.

mod rows;
mod settle;
mod trace;

use std::path::{Path, PathBuf};
use std::process::Command;

use serde_json::{Map, Value};

use super::ledger::raised;
use super::reply;
use crate::record::args::{parse, Spec};
use crate::Reply;

/// One logged pass: its fields, every value a string (`{k: str(v)}`), in the order the log wrote them.
pub type Pass = Map<String, Value>;

/// The name the ledger write is recorded under in the usage log (feature 406 T03, D162): landings and `make ledger-owed` write rows
/// unasked, so each write is an automatic step whose outcome `make tool-yield` reads (the `usage_log` record of `ledger_owed._usage`).
const USAGE_LOG_TOOL: &str = "ledger-owed-write";
const LOG: &str = "check-passes.jsonl";

/// What a run reads of its process, handed in so a test runs in a scratch tree.
pub struct Env {
    /// The working directory: relative paths, and the git directory the log and the kept costs are found by.
    pub cwd: PathBuf,
    /// The gate's own tree (`L7R_GATE_TREE`), whose usage log records a write, as the Python recorded into its script's tree.
    pub tree: PathBuf,
    /// `$HOME`, for the default transcripts directory.
    pub home: String,
    /// `L7R_CACHE_OFF` set to anything but `0`: no kept costs read or written.
    pub cache_off: bool,
    /// `L7R_CLAIMS_SHEET`, unset by default.
    pub claims_sheet: Option<String>,
}

impl Env {
    /// The process's own.
    #[must_use]
    pub fn of_process() -> Self {
        let cwd = std::env::current_dir().unwrap_or_default();
        Self {
            tree: std::env::var_os("L7R_GATE_TREE").map_or_else(|| cwd.clone(), PathBuf::from),
            cwd,
            home: std::env::var("HOME").unwrap_or_default(),
            cache_off: cache_off(std::env::var("L7R_CACHE_OFF").ok().as_deref()),
            claims_sheet: std::env::var("L7R_CLAIMS_SHEET").ok(),
        }
    }

    /// A path as the process would open it: a relative one under the working directory.
    fn at(&self, path: &str) -> PathBuf {
        self.cwd.join(py_path(path))
    }

    /// `git rev-parse --git-common-dir` in the working directory, stripped; "" where git says nothing.
    fn common_dir(&self) -> String {
        Command::new("git")
            .args(["rev-parse", "--git-common-dir"])
            .current_dir(&self.cwd)
            .output()
            .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_owned())
            .unwrap_or_default()
    }

    /// `default_log`: the pass log under the common git directory (`.git` where there is none).
    fn default_log(&self) -> PathBuf {
        let out = self.common_dir();
        resolve(&self.at(if out.is_empty() { ".git" } else { &out })).join(LOG)
    }

    /// `_kept_file`: where the costed passes are kept, none with the cache off or outside a repository.
    fn kept_file(&self) -> Option<PathBuf> {
        if self.cache_off {
            return None;
        }
        let out = self.common_dir();
        (!out.is_empty()).then(|| resolve(&self.at(&out)).join(settle::SETTLED))
    }

    /// `review_cost.DEFAULT_ROOT`.
    fn default_root(&self) -> String {
        format!("{}/.claude/projects", self.home)
    }
}

/// `L7R_CACHE_OFF` set to anything but "" or `0` turns the kept costs off.
fn cache_off(value: Option<&str>) -> bool {
    !matches!(value, None | Some("" | "0"))
}

/// `Path(text)` as pathlib reads it: `.` components dropped, `.` for nothing.
fn py_path(text: &str) -> PathBuf {
    super::py_path(text)
}

/// `Path.resolve()`: the longest existing prefix's real path, the rest appended, `..` folded.
fn resolve(path: &Path) -> PathBuf {
    if let Ok(real) = path.canonicalize() {
        return real;
    }
    match (path.parent(), path.file_name()) {
        (Some(parent), Some(name)) => resolve(parent).join(name),
        (Some(parent), None) => resolve(parent)
            .parent()
            .unwrap_or(Path::new("/"))
            .to_path_buf(),
        _ => path.to_path_buf(),
    }
}

/// A pass's field, none where the log wrote none.
fn field<'a>(p: &'a Pass, key: &str) -> Option<&'a str> {
    p.get(key).and_then(Value::as_str)
}

/// A pass's field, "" where it has none (`p.get(key, "")`).
fn text<'a>(p: &'a Pass, key: &str) -> &'a str {
    field(p, key).unwrap_or("")
}

/// `p[key]`, the Python's `KeyError` where it is missing.
fn required<'a>(p: &'a Pass, key: &str) -> Result<&'a str, String> {
    field(p, key).ok_or_else(|| format!("KeyError: '{key}'"))
}

/// `re.sub(r"\s+", " ", cell).strip()`.
fn norm(cell: &str) -> String {
    l7r_guard::shared::py_text::collapse(cell)
}

/// A ledger row of these cells: each normalized, its pipes turned to slashes.
fn row_of(cells: &[String]) -> String {
    let inner: Vec<String> = cells.iter().map(|c| norm(c).replace('|', "/")).collect();
    format!("| {} |", inner.join(" | "))
}

fn usage(why: &str) -> Reply {
    reply(
        String::new(),
        format!("usage: l7r-gate reviews ledger-owed [--log LOG] [--ledger LEDGER] [--refuse] [--transcripts DIR] [--write WHERE] [--session SID] [--write-plan-reviews]\nl7r-gate reviews ledger-owed: error: {why}\n"),
        2,
    )
}

/// The ledger write recorded in the gate tree's usage log as an automatic step (`_usage`).
fn record_usage(env: &Env, outcome: &str) {
    let common = Command::new("git")
        .arg("-C")
        .arg(&env.tree)
        .args(["rev-parse", "--path-format=absolute", "--git-common-dir"])
        .output()
        .ok()
        .filter(|o| o.status.success())
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_owned())
        .unwrap_or_default();
    if !common.is_empty() {
        l7r_guard::shared::checks::passes::usage(
            Path::new(&common),
            USAGE_LOG_TOOL,
            "step",
            outcome,
        );
    }
}

/// The ledger opened to append, created as `open(..., "a")` creates it.
fn open_append(ledger: &Path) -> Result<std::fs::File, String> {
    std::fs::OpenOptions::new()
        .append(true)
        .create(true)
        .open(ledger)
        .map_err(|e| format!("{}: {e}", ledger.display()))
}

/// One row appended.
fn write_row(f: &mut std::fs::File, row: &str) -> Result<(), String> {
    use std::io::Write as _;
    f.write_all(format!("{row}\n").as_bytes())
        .map_err(|e| e.to_string())
}

/// `ledger_owed.py`'s command line.
#[must_use]
pub fn cli(args: &[String], env: &Env) -> Reply {
    let specs = [
        Spec::value("--log"),
        Spec::value("--ledger"),
        Spec::flag("--refuse"),
        Spec::value("--transcripts"),
        Spec::value("--write"),
        Spec::value("--session"),
        Spec::flag("--write-plan-reviews"),
    ];
    let p = match parse(args, &specs) {
        Ok(p) => p,
        Err(why) => return usage(&why),
    };
    let default_root = env.default_root();
    let opts = Opts {
        log: p.text("--log", ""),
        ledger: p.text("--ledger", "dev/review-ledger.md"),
        refuse: p.on("--refuse"),
        transcripts: p.text("--transcripts", &default_root),
        write: p.text("--write", ""),
        session: p.text("--session", ""),
        plan_reviews: p.on("--write-plan-reviews"),
    };
    run(&opts, env).unwrap_or_else(|why| raised(String::new(), "ledger-owed", &why))
}

/// `ledger-passes`: `settled(distinct(load_passes(default_log())), kept_file=_kept_file())` as JSON, the passes `feature_report.py`
/// costs (it imported `ledger_owed` for them).
#[must_use]
pub fn passes_cli(args: &[String], env: &Env) -> Reply {
    if !args.is_empty() {
        return reply(
            String::new(),
            "usage: l7r-gate reviews ledger-passes\n".to_owned(),
            2,
        );
    }
    let passes = settle::load_passes(&env.default_log())
        .map(|ps| settle::distinct(&ps))
        .and_then(|ps| {
            settle::settled(
                &ps,
                Path::new(&env.default_root()),
                env.kept_file().as_deref(),
            )
        });
    match passes {
        Ok(ps) => reply(
            format!(
                "{}\n",
                Value::from(ps.into_iter().map(Value::Object).collect::<Vec<_>>())
            ),
            String::new(),
            0,
        ),
        Err(why) => raised(String::new(), "ledger-passes", &why),
    }
}

/// The command line, read.
struct Opts<'a> {
    log: &'a str,
    ledger: &'a str,
    refuse: bool,
    transcripts: &'a str,
    write: &'a str,
    session: &'a str,
    plan_reviews: bool,
}

/// `main` after its arguments.
fn run(o: &Opts, env: &Env) -> Result<Reply, String> {
    let ledger = env.at(o.ledger);
    let log = if o.log.is_empty() {
        env.default_log()
    } else {
        env.at(o.log)
    };
    // the transcripts' directory as given, not joined to the working directory: the kept costs record each transcript's path under it
    // (`str(path)`), relative where it was
    let transcripts = py_path(o.transcripts);
    let passes = settle::distinct(&settle::settled(
        &settle::load_passes(&log)?,
        &transcripts,
        env.kept_file().as_deref(),
    )?);
    let text = if ledger.is_file() {
        std::fs::read_to_string(&ledger).map_err(|e| format!("{}: {e}", ledger.display()))?
    } else {
        String::new()
    };
    let owed = settle::unanswered(&passes, &text)?;
    let repo = resolve(&ledger)
        .parent()
        .and_then(Path::parent)
        .map(Path::to_path_buf)
        .unwrap_or_default();
    if o.plan_reviews {
        let made = rows::plan_review_rows(&owed, &transcripts, &repo)?;
        if !made.is_empty() {
            let mut f = open_append(&ledger)?;
            for row in &made {
                write_row(&mut f, row)?;
            }
        }
        record_usage(env, outcome(made.is_empty()));
        return Ok(reply(
            format!("ledger-owed: {} plan review row(s) written\n", made.len()),
            String::new(),
            0,
        ));
    }
    if !o.write.is_empty() {
        return write_owed(o, env, &owed, (&ledger, &repo, &transcripts));
    }
    if owed.is_empty() {
        return Ok(reply(String::new(), String::new(), 0));
    }
    let mut said = format!("ledger-owed: {} check pass(es) have no row in dev/review-ledger.md's measured table - write them from each agent's reply: make ledger-owed WRITE=\"<where you recorded what you did>\" (feature 385 FR-019); or add each by hand, filling the ?s:\n", owed.len());
    for p in &owed {
        said.push_str("  ");
        said.push_str(&rows::row_for(p));
        said.push('\n');
    }
    said += "  (a row answers a pass by its check and its cost cells, which are the pass's own `make review-cost` - feature 371; the push refuses until each has its row, or LEDGER_ROWS_OK=\"<reason>\")\n";
    Ok(if o.refuse {
        reply(String::new(), said, 1)
    } else {
        reply(said, String::new(), 0)
    })
}

/// The usage log's outcome of a write: `unchanged` where it wrote nothing.
fn outcome(nothing: bool) -> &'static str {
    if nothing {
        "unchanged"
    } else {
        "changed"
    }
}

/// `--write`: each owed pass of the session (or, for a feature's specs directory, each traced to that feature) appended as a row
/// filled from its agent's reply; `at` is the ledger, its repository and the transcripts' directory.
fn write_owed(
    o: &Opts,
    env: &Env,
    owed: &[Pass],
    at: (&Path, &Path, &Path),
) -> Result<Reply, String> {
    let (ledger, repo, transcripts) = at;
    let mut mine = Vec::new();
    for p in owed {
        if o.session.is_empty() || rows::session_of(p, transcripts) == o.session {
            mine.push(p.clone());
        }
    }
    let feat = trace::feature_of(o.write);
    if let Some(num) = feat.as_deref().filter(|_| o.session.is_empty()) {
        // a page session's own passes are its feature's already
        let questions = trace::feature_questions(num, repo, env)?;
        let mut kept = Vec::new();
        for p in mine {
            if trace::belongs(&p, num, &questions, repo, transcripts)? {
                kept.push(p);
            }
        }
        mine = kept;
    }
    // the ledger is opened first and each row written as it is made, so a row that raises leaves the ones before it, as the
    // Python's `writelines` over a generator did
    let mut f = open_append(ledger)?;
    for p in &mine {
        write_row(&mut f, &rows::filled_row(p, o.write, transcripts)?)?;
    }
    let left = owed.len() - mine.len();
    record_usage(env, outcome(mine.is_empty()));
    let whom = if o.session.is_empty() {
        feat.map_or_else(|| "every session".to_owned(), |n| format!("feature {n}"))
    } else {
        o.session.to_owned()
    };
    let tail = if left > 0 {
        format!("; {left} pass(es) not traced to it stay owed for the feature that ran them")
    } else {
        String::new()
    };
    Ok(reply(
        format!(
            "ledger-owed: {} row(s) written for {whom}{tail}\n",
            mine.len()
        ),
        String::new(),
        0,
    ))
}

#[cfg(test)]
mod tests;
