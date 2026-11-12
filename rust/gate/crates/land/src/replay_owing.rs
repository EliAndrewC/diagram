//! `l7r-gate replay-owing <rev> [<rev> ...] [--out DIR] [--triage]` (`make replay-owing`): replay recorded deltas through the OLD owing
//! and the NEW (feature 375, SC-001). Ported from `scripts/measure/replay_owing.py` by feature 449 T121 (`ask:449-T83-scope`, its OLD side
//! with its NEW by `ask:449-T77-replays` (3): `specs/375-enforced-wave-process/measurements.json`'s `sc001-replay` records `make
//! replay-owing` as its command, which `make figures` re-runs).
//!
//! SC-001: replaying feature 372's recorded deltas for waves 106, 108 and 111, the `modal-depiction` units owed in full fall by at least
//! two thirds and the `impl-drift` claims owed by at least four fifths. A delta is one commit against its parent, as the history recorded
//! it. For each:
//!
//! - OLD - the commit's own scripts and engine, in a detached worktree of the commit, with the parent's claims index: what that delta owed
//!   when it was made - owed at the commit less what was already owed at the parent (a claim owed earlier and answered in this commit
//!   belongs to the earlier delta). The commit's own scripts stay whatever language that commit had: the OLD side still runs them by
//!   `python3 -c`, the two snippets below as `replay_owing.py` held them (its `claims_door.py` branch for a commit after feature 449 T82,
//!   its own `claims.py` before).
//! - NEW - this tree's owing, run over the same worktree in process: the claims index of the parent migrated as
//!   `claims-backfill-sections` migrates it (FR-002), and the modal units split into those owed in full (their own words moved) and those
//!   owed only a triage (a page they name moved, FR-001). A triage-only unit is owed its check only if a triage names it, which is a
//!   judgment: the replay writes each delta's triage bundle beside its figures (`--triage`) so the triage can be run on it.
//!
//! One JSON line per commit, then the totals.

use std::path::{Path, PathBuf};
use std::process::Command;

use l7r_gate_core::record::args::{parse_with, Spec};
use l7r_guard::shared::py_text::strip;
use l7r_guard::shared::pyjson::dumps;
use serde_json::{json, Map, Value};

use crate::Reply;

const SPARSE: [&str; 11] = [
    "l7r",
    "scripts",
    "docs",
    "research/questions",
    "research/assets",
    "dev/claims-index.json",
    "dev/claims-pages.json",
    "dev/claims-deferred.json",
    "dev/modals.md",
    "dev/modals-particular.md",
    "pyproject.toml",
];

/// The OLD side's pop-up owing: the commit's own `scripts/record/modal_owed.py`.
const OLD_MODALS: &str = "
import sys, json; sys.path.insert(0, 'scripts/record'); import modal_owed as mo
print(json.dumps([[s, w] for s, w, _f in mo.owed(__import__('pathlib').Path('.').resolve(), sys.argv[1])]))
";

/// The OLD side's claims owing at a commit: its own door to the Rust claims after feature 449 T82, its own `claims.py` before.
const OLD_CLAIMS: &str = "
import sys, json, pathlib
scripts = sys.argv[1]
root = pathlib.Path('.').resolve()
index = json.loads(pathlib.Path(sys.argv[2]).read_text()); store = json.loads(pathlib.Path(sys.argv[3]).read_text())
if pathlib.Path(scripts, 'scripts', 'claims_door.py').is_file():  # the claims tools in Rust (feature 449 T82): their door
    sys.path.insert(0, scripts + '/scripts'); import claims_door as cd
    print(json.dumps(cd.owed(root, index, store)))
    sys.exit(0)
sys.path.insert(0, scripts + '/scripts/record'); import claims as cx  # a commit before T82: its own Python
qdir = root / cx.QUESTIONS
cur = cx.current(root)
print(json.dumps(cx.owed(cur, index, qdir, store)))
";

/// What one run reads of its process.
struct Env {
    /// This tree: where the worktrees are made from (`ROOT`, the script's own tree).
    root: PathBuf,
    /// The working directory, which a relative `--out` is read against, as the Python read it.
    cwd: PathBuf,
    python: String,
}

/// `git -C <cwd> args...`'s stdout, as `check=True` raised on a failure.
fn git(cwd: &Path, args: &[&str]) -> Result<String, String> {
    let out = Command::new("git")
        .arg("-C")
        .arg(cwd)
        .args(args)
        .output()
        .map_err(spawned)?;
    if !out.status.success() {
        return Err(format!(
            "subprocess.CalledProcessError: Command 'git {}' returned non-zero exit status {}.",
            args.join(" "),
            out.status.code().unwrap_or(-1)
        ));
    }
    String::from_utf8(out.stdout).map_err(undecodable)
}

/// What `subprocess` raised on a program it could not start.
fn spawned<E: std::fmt::Display>(e: E) -> String {
    format!("FileNotFoundError: {e}")
}

/// What `text=True` raised on output that is no UTF-8.
fn undecodable<E: std::fmt::Display>(e: E) -> String {
    format!("UnicodeDecodeError: {e}")
}

/// A path as the process opens it: a relative one under `cwd`.
fn under(cwd: &Path, path: &Path) -> PathBuf {
    cwd.join(path)
}

/// The first `n` characters of `rev`.
fn short(rev: &str, n: usize) -> String {
    rev.chars().take(n).collect()
}

impl Env {
    /// A snippet in a fresh interpreter (the old and the new engine cannot share one process), its stdout; a failure raises.
    fn py(&self, code: &str, args: &[&str], cwd: &Path) -> Result<String, String> {
        let out = Command::new(&self.python)
            .arg("-c")
            .arg(code)
            .args(args)
            .current_dir(under(&self.cwd, cwd))
            .output()
            .map_err(spawned)?;
        if !out.status.success() {
            return Err(format!(
                "subprocess.CalledProcessError: Command '{} -c ...' returned non-zero exit status {}.",
                self.python,
                out.status.code().unwrap_or(-1)
            ));
        }
        String::from_utf8(out.stdout).map_err(undecodable)
    }

    /// A sparse detached worktree of `rev` under `base`, made once.
    fn worktree(&self, rev: &str, base: &Path) -> Result<PathBuf, String> {
        let wt = base.join(short(rev, 10));
        if !under(&self.cwd, &wt).is_dir() {
            let at = wt.to_string_lossy();
            git(
                &self.root,
                &[
                    "worktree",
                    "add",
                    "-q",
                    "--no-checkout",
                    "--detach",
                    &at,
                    rev,
                ],
            )?;
            let mut sparse = vec!["sparse-checkout", "set", "--no-cone"];
            sparse.extend(SPARSE);
            git(&under(&self.cwd, &wt), &sparse)?;
            git(&under(&self.cwd, &wt), &["checkout", "-q", "--detach", rev])?;
        }
        Ok(wt)
    }

    /// The claims a tree owes, its rows read from the OLD snippet at that tree's own scripts.
    fn old_claims(
        &self,
        tree: &Path,
        idx: &Path,
        store: &Path,
    ) -> Result<Vec<(String, String)>, String> {
        let said = self.py(
            OLD_CLAIMS,
            &[
                &tree.to_string_lossy(),
                &idx.to_string_lossy(),
                &store.to_string_lossy(),
            ],
            tree,
        )?;
        rows(&said)
    }

    /// The NEW side's claims the delta owes: the parent's index migrated (`claims-backfill-sections`, FR-002) and written back, then
    /// owed at the commit less owed at the parent, in process.
    fn new_claims(
        &self,
        wp: &Path,
        at_wt: &Path,
        idx: &Path,
        store: &Path,
    ) -> Result<Rows, String> {
        let parent_at = resolved(&under(&self.cwd, wp));
        // the NEW side's files are opened from the snippet's working directory, the parent's worktree, as the Python's were
        let (idx_at, store_at) = (
            under(&under(&self.cwd, wp), idx),
            under(&under(&self.cwd, wp), store),
        );
        let (mut index, mut kept) = (object(&idx_at)?, object(&store_at)?);
        l7r_gate_claims::claims::backfill_at(&parent_at, &mut index, &mut kept)?;
        write_json(&idx_at, &index)?;
        write_json(&store_at, &kept)?;
        let (index, kept) = (object(&idx_at)?, object(&store_at)?);
        let was = l7r_gate_claims::claims::owed_at(&parent_at, &index, &kept)?;
        Ok(not_in(
            l7r_gate_claims::claims::owed_at(at_wt, &index, &kept)?,
            &was,
        ))
    }

    /// The parent's claims records copied beside the figures (`{}` where the parent has none): the index and the store both sides
    /// read.
    fn copy_records(&self, wp: &Path, idx: &Path, store: &Path) -> Result<(), String> {
        for (src, dst) in [
            ("dev/claims-index.json", idx),
            ("dev/claims-pages.json", store),
        ] {
            let (from, to) = (under(&self.cwd, &wp.join(src)), under(&self.cwd, dst));
            let done = if from.is_file() {
                std::fs::copy(&from, &to).map(|_| ())
            } else {
                std::fs::write(&to, "{}")
            };
            done.map_err(spawned)?;
        }
        Ok(())
    }

    /// One commit replayed: its row.
    fn replay(&self, rev: &str, base: &Path, triage: bool) -> Result<Map<String, Value>, String> {
        let parent = strip(&git(&self.root, &["rev-parse", &format!("{rev}^")])?).to_owned();
        let (wt, wp) = (self.worktree(rev, base)?, self.worktree(&parent, base)?);
        let old_modals: Value = loads(&self.py(OLD_MODALS, &[&parent], &wt)?)?;
        let at_wt = resolved(&under(&self.cwd, &wt));
        let new_modals = with_triage(l7r_gate_owed::record::modals::owed(&at_wt, &parent, "")?);
        let (idx, store) = (
            base.join(format!("{}.index.json", short(rev, 10))),
            base.join(format!("{}.store.json", short(rev, 10))),
        );
        self.copy_records(&wp, &idx, &store)?;
        // what the DELTA owes: owed at the commit, less what was already owed at its parent (both against the parent's index) - a claim
        // owed earlier and answered in this very commit is the earlier delta's, not this one's
        let old_was = self.old_claims(&wp, &idx, &store)?;
        let old_claims = not_in(self.old_claims(&wt, &idx, &store)?, &old_was);
        let new_claims = self.new_claims(&wp, &at_wt, &idx, &store)?;
        triage_bundle(
            wants_triage(triage, &new_modals),
            rev,
            base,
            &parent,
            &at_wt,
        )?;
        let subject = strip(&git(&self.root, &["log", "-1", "--format=%s", rev])?)
            .chars()
            .take(90)
            .collect::<String>();
        let mut row = Map::new();
        row.insert("rev".into(), json!(short(rev, 10)));
        row.insert("subject".into(), json!(subject));
        row.insert("modal_depiction_old".into(), json!(depicted(&old_modals)));
        row.insert(
            "modal_depiction_new_full".into(),
            json!(counted(&new_modals, false)),
        );
        row.insert(
            "modal_depiction_new_triage".into(),
            json!(counted(&new_modals, true)),
        );
        row.insert("impl_drift_old".into(), json!(full(&old_claims)));
        row.insert("impl_drift_new_full".into(), json!(full(&new_claims)));
        row.insert(
            "impl_drift_new_triage".into(),
            json!(new_claims.len() - full(&new_claims)),
        );
        Ok(row)
    }
}

/// `(key, why)` rows of what a tree owes.
type Rows = Vec<(String, String)>;

const DEPICTION: &str = "modal-depiction:";

/// The rows whose key `was` does not hold.
fn not_in(rows: Rows, was: &Rows) -> Rows {
    rows.into_iter()
        .filter(|(k, _)| !was.iter().any(|(w, _)| w == k))
        .collect()
}

/// The claims owed a full check: every row but those owed only a triage.
fn full(rows: &Rows) -> usize {
    rows.iter()
        .filter(|(_, why)| why != "triage" && why != "section triage")
        .count()
}

/// The NEW side's pop-up rows, each `(subject, owed only a triage)`.
fn with_triage(rows: Vec<(String, String, String)>) -> Vec<(String, bool)> {
    rows.into_iter()
        .map(|(s, w, _f)| {
            let t = l7r_gate_owed::record::triage::triage_only(&w);
            (s, t)
        })
        .collect()
}

/// The OLD side's `modal-depiction` units.
fn depicted(old: &Value) -> usize {
    old.as_array()
        .into_iter()
        .flatten()
        .filter(|r| r[0].as_str().is_some_and(|s| s.starts_with(DEPICTION)))
        .count()
}

/// The NEW side's `modal-depiction` units owed in full (`triage` false) or only a triage.
fn counted(rows: &[(String, bool)], triage: bool) -> usize {
    rows.iter()
        .filter(|(s, t)| s.starts_with(DEPICTION) && *t == triage)
        .count()
}

/// `--triage` and a depiction unit owed only a triage: the bundle is written.
fn wants_triage(triage: bool, rows: &[(String, bool)]) -> bool {
    triage && rows.iter().any(|(s, t)| *t && s.starts_with(DEPICTION))
}

/// The commit's pop-up triage bundle written under `base/triage-<rev>`, its checks' store `base/store-<rev>` (`RECORD_CHECKS_DIR`,
/// set for the bundle alone as the Python set it for that one child): the NEW side's `modal_triage.bundle`, in process.
fn triage_bundle(
    want: bool,
    rev: &str,
    base: &Path,
    parent: &str,
    at_wt: &Path,
) -> Result<(), String> {
    if !want {
        return Ok(());
    }
    let store = base.join(format!("store-{}", short(rev, 10)));
    let out = base.join(format!("triage-{}", short(rev, 10)));
    let was = std::env::var_os("RECORD_CHECKS_DIR");
    // a relative `--out` names it from the worktree, the door's working directory in the Python
    std::env::set_var("RECORD_CHECKS_DIR", under(at_wt, &store));
    let done = l7r_gate_owed::record::triage::bundle(at_wt, &under(at_wt, &out), parent);
    restore("RECORD_CHECKS_DIR", was);
    done.map(|_| ())
}

/// A variable put back as it was before a call set it.
fn restore(key: &str, was: Option<std::ffi::OsString>) {
    match was {
        Some(v) => std::env::set_var(key, v),
        None => std::env::remove_var(key),
    }
}

/// `json.loads` of what a snippet printed.
fn loads(text: &str) -> Result<Value, String> {
    serde_json::from_str(text).map_err(|e| format!("json.decoder.JSONDecodeError: {e}"))
}

/// `Path.resolve()` of an existing directory.
fn resolved(path: &Path) -> PathBuf {
    path.canonicalize().unwrap_or(path.to_path_buf())
}

/// A JSON file's object, as the snippet's `json.loads` read it; anything but an object fails where the door's `dict(index)` did.
fn object(path: &Path) -> Result<Map<String, Value>, String> {
    let text = std::fs::read_to_string(path).map_err(|e| format!("{}: {e}", path.display()))?;
    match serde_json::from_str(&text).map_err(|e| format!("json.decoder.JSONDecodeError: {e}"))? {
        Value::Object(m) => Ok(m),
        other => Err(format!(
            "ValueError: dictionary update sequence element: {other}"
        )),
    }
}

/// `write_text(json.dumps(value))`.
fn write_json(path: &Path, value: &Map<String, Value>) -> Result<(), String> {
    std::fs::write(path, dumps(&Value::Object(value.clone()), None, true))
        .map_err(|e| format!("{}: {e}", path.display()))
}

/// The `[key, why]` rows a snippet printed.
fn rows(said: &str) -> Result<Vec<(String, String)>, String> {
    let v: Value =
        serde_json::from_str(said).map_err(|e| format!("json.decoder.JSONDecodeError: {e}"))?;
    Ok(v.as_array()
        .into_iter()
        .flatten()
        .map(|r| {
            let text = |i: usize| r[i].as_str().unwrap_or_default().to_owned();
            (text(0), text(1))
        })
        .collect())
}

fn usage(why: &str) -> Reply {
    Reply {
        stdout: String::new(),
        stderr: format!("usage: l7r-gate replay-owing [-h] [--out OUT] [--triage] revs [revs ...]\nl7r-gate replay-owing: error: {why}\n"),
        code: 2,
    }
}

/// argparse's `nargs="+"` positional: one run of revisions, an argument past the run refused as unrecognized.
fn revs_of(args: &[String], specs: &[Spec]) -> Result<(Vec<String>, String, bool), String> {
    let p = parse_with(args, specs, usize::MAX)?;
    let mut run_ended = false;
    let mut extra: Vec<&str> = Vec::new();
    let mut started = false;
    let mut i = 0;
    while i < args.len() {
        let a = &args[i];
        i += 1;
        if a.starts_with("--") && a.len() > 2 {
            if started {
                run_ended = true;
            }
            if !a.contains('=') && "--out".starts_with(a.as_str()) {
                i += 1;
            }
            continue;
        }
        if run_ended {
            extra.push(a);
        }
        started = true;
    }
    if !extra.is_empty() {
        return Err(format!("unrecognized arguments: {}", extra.join(" ")));
    }
    if p.positional.is_empty() {
        return Err("the following arguments are required: revs".to_owned());
    }
    Ok((
        p.positional.clone(),
        p.text("--out", "/tmp/l7r-replay").to_owned(),
        p.on("--triage"),
    ))
}

/// `l7r-gate replay-owing`: each commit's row as it is replayed, then the totals; the worktrees removed on every way out.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let cwd = std::env::current_dir().unwrap_or_default();
    let root = std::env::var_os("L7R_GATE_TREE").map_or_else(|| cwd.clone(), PathBuf::from);
    let env = Env {
        root,
        cwd,
        python: "python3".to_owned(),
    };
    run(args, &env, &mut print_line)
}

/// A line on stdout, as `print` wrote it.
fn print_line(line: &str) {
    println!("{line}");
}

fn run(args: &[String], env: &Env, say: &mut dyn FnMut(&str)) -> Reply {
    let specs = [Spec::value("--out"), Spec::flag("--triage")];
    let (revs, out, triage) = match revs_of(args, &specs) {
        Ok(t) => t,
        Err(why) => return usage(&why),
    };
    let base = PathBuf::from(&out);
    if let Err(e) = std::fs::create_dir_all(under(&env.cwd, &base)) {
        return raised(&format!("{}: {e}", base.display()));
    }
    let mut totals: Map<String, Value> = Map::new();
    let done = (|| -> Result<(), String> {
        for rev in &revs {
            let sha = strip(&git(&env.root, &["rev-parse", rev])?).to_owned();
            let row = env.replay(&sha, &base, triage)?;
            say(&dumps(&Value::Object(row.clone()), None, true));
            for (k, v) in &row {
                if let Some(n) = v.as_u64() {
                    let had = totals.get(k).and_then(Value::as_u64).unwrap_or(0);
                    totals.insert(k.clone(), json!(had + n));
                }
            }
        }
        Ok(())
    })();
    for entry in std::fs::read_dir(under(&env.cwd, &base))
        .into_iter()
        .flatten()
        .flatten()
    {
        let wt = entry.path();
        if wt.is_dir() && wt.join(".git").is_file() {
            let _ = Command::new("git")
                .arg("-C")
                .arg(&env.root)
                .args(["worktree", "remove", "--force"])
                .arg(&wt)
                .output();
        }
    }
    if let Err(why) = done {
        return raised(&why);
    }
    say(&dumps(&json!({"totals": totals}), None, true));
    Reply {
        stdout: String::new(),
        stderr: String::new(),
        code: 0,
    }
}

fn raised(why: &str) -> Reply {
    Reply {
        stdout: String::new(),
        stderr: format!("Traceback (most recent call last):\n  l7r-gate replay-owing\n{why}\n"),
        code: 1,
    }
}

#[cfg(test)]
mod tests;
