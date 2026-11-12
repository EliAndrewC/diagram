//! The landing cohort (feature 386; feature 449 T068, from `cohort_gate.py`): 48 seeds when engine work lands, and a fresh-seed rate.
//!
//! WHY. The cohort is the hamlet generator's strongest test bed and nothing asked for one: about 30 ten-seed cohorts passed on
//! 2026-10-12/13 and the next 48-seed run failed on seeds 17, 21, 40 and 45 (`specs/386-landing-cohort/`). So the gated push requires a
//! landing record rolled on exactly the engine it lands, refuses a fixed or pinned seed that regressed against main, and prints the fresh
//! block's failure rate, never refusing on it.

use std::cell::RefCell;
use std::collections::HashMap;
use std::fmt::Write as _;
use std::path::Path;
use std::process::Command;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::sha256;
use serde_json::Value;

use crate::delta;
pub use l7r_gate_core::cohort::*;

pub mod known;
pub mod room;
pub mod seeds;

/// The name its runs are recorded under in the `usage_log`.
pub const USAGE_LOG_TOOL: &str = "cohort_gate";
const LOG: &str = "dev/cohort-log";
const RUST_LOG: &str = "dev/rust-gate";
const RUST_COMMAND: &str = "make rust-gate";
const COMMAND: &str = "make cohort-landing";
const SWITCHES: &str = "dev/switches.json";
const PORT_STATES: [&str; 2] = ["rust-only", "integrated"];
/// The landing cohort's size, fixed and fresh alike: the 48 the GM's recommendation names.
const SEEDS: usize = 48;
/// The fresh blocks start here: above the fixed range, the pinned rows and every hand roll the log holds.
const FRESH_BASE: u64 = 10_000;
const FRESH_SPAN: u64 = 990_000;
const REFUSING: [&str; 3] = [" NEWLY FAILING", " WORSENED", " NO BASELINE"];

/// A scratch directory for one `ask_counters` call, removed when it is dropped (feature 449 T101). The process id alone is not
/// enough: parallel tests share a process, and one call's cleanup deleted another's files, the cause of this crate's intermittent
/// "codeid.py could not say" (2026-11-10); a `TempDir` is counted within the process too.
fn counter_dir() -> l7r_guard::shared::tempdir::TempDir {
    l7r_guard::shared::tempdir::TempDir::new("gate-counter")
}
/// The paths whose bytes unchanged mean the same engine at once.
pub const ENGINE_PATHS: [&str; 2] = ["l7r", "pool"];

/// The landing's own list of engine files (`codeid.ENGINE`, which stays in Python until phase 4).
static ENGINE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"^(l7r/.*\.py|pool/.*\.gen\.py|pool/.*\.json|rust/.*\.rs|rust/(?:.*/)?Cargo\.(?:toml|lock))$")
        .unwrap_or_else(|e| unreachable!("{e}"))
});

/// A path the landing counts as engine code (`codeid.ENGINE`): one regex for the counter-only test here and `l7r-gate land`'s engine
/// delta (feature 449 T121), so the Rust land starts no `codeid.py` to read it, as `land.py` loaded that file by path for this alone.
#[must_use]
pub fn is_landing_engine(path: &str) -> bool {
    ENGINE.is_match(path).unwrap_or(false)
}

/// Two versions of each file whose counters decide a commit pair.
type Versions = Vec<(Vec<u8>, Vec<u8>)>;

/// A repository and what it has been asked already: `baselines` asks an engine key once per record.
pub struct Repo<'a> {
    pub root: &'a Path,
    pub python: &'a str,
    keys: RefCell<HashMap<String, String>>,
    counters: RefCell<HashMap<(String, String), bool>>,
    failure: RefCell<Option<String>>,
}

fn git_bytes(root: &Path, args: &[&str]) -> Vec<u8> {
    Command::new("git")
        .arg("-C")
        .arg(root)
        .args(args)
        .output()
        .map(|o| o.stdout)
        .unwrap_or_default()
}

pub fn seeds_of(rec: &Value) -> &[Value] {
    rec["seeds"].as_array().map_or(&[], Vec::as_slice)
}

fn is_pinned(seed: i64) -> bool {
    (901..907).contains(&seed)
}

impl<'a> Repo<'a> {
    #[must_use]
    pub fn new(root: &'a Path, python: &'a str) -> Self {
        Self {
            root,
            python,
            keys: RefCell::new(HashMap::new()),
            counters: RefCell::new(HashMap::new()),
            failure: RefCell::new(None),
        }
    }

    /// The engine key of `reference`, or of the working tree for `None`; empty for a reference that does not resolve.
    pub fn engine_key(&self, reference: Option<&str>) -> String {
        let Some(reference) = reference else {
            return delta::engine_key_worktree(self.root, self.python).unwrap_or_default();
        };
        let (_, out) = git(
            self.root,
            &[
                "rev-parse",
                "-q",
                "--verify",
                &format!("{reference}^{{commit}}"),
            ],
        );
        let sha = out.trim().to_owned();
        if sha.is_empty() {
            return String::new();
        }
        if let Some(key) = self.keys.borrow().get(&sha) {
            return key.clone();
        }
        let key = delta::engine_key(self.root, &sha, self.python).unwrap_or_default();
        self.keys.borrow_mut().insert(sha, key.clone());
        key
    }

    /// The same bytes on the engine paths, or the same engine key.
    fn same_by_key(&self, a: &str, b: &str) -> bool {
        let mut args = vec!["diff", "--quiet", a, b, "--"];
        args.extend(ENGINE_PATHS);
        if git(self.root, &args).0 {
            return true;
        }
        let first = self.engine_key(Some(a));
        !first.is_empty() && first == self.engine_key(Some(b))
    }

    /// Do the two commits carry the same engine? Identical bytes answer at once, then the keys, then a counter-only difference (feature 446).
    pub fn same_key(&self, a: &str, b: &str) -> bool {
        self.same_by_key(a, b) || self.counter_only(a, b)
    }

    /// Was `commit` rolled on main's engine?
    pub fn same_engine(&self, commit: &str) -> bool {
        self.same_key(commit, self.main_ref())
    }

    fn main_ref(&self) -> &'static str {
        if git(self.root, &["rev-parse", "-q", "--verify", "origin/main"]).0 {
            "origin/main"
        } else {
            "main"
        }
    }

    /// Each pair's "the same but for counter blocks", from one run of `codeid.py`, which reads the AST until phase 4
    /// (`round:spec-fidelity|plan:449-rust-codebase#T068@3`: at most one process a run, whatever the records). `None` when it could not answer.
    fn ask_counters(&self, pairs: &[&(Vec<u8>, Vec<u8>)]) -> Option<Vec<bool>> {
        let dir = counter_dir();
        let mut files = Vec::new();
        let mut written = std::fs::create_dir_all(&dir).is_ok();
        for (n, (old, new)) in pairs.iter().enumerate() {
            let (a, b) = (dir.join(format!("{n}a.py")), dir.join(format!("{n}b.py")));
            written = written && std::fs::write(&a, old).is_ok() && std::fs::write(&b, new).is_ok();
            files.extend([a, b]);
        }
        let done = Command::new(self.python)
            .arg(crate::codeid::script(self.root))
            .arg("--debug-free-equal")
            .args(&files)
            .output();
        drop(dir);
        let out = done.ok().filter(|o| written && o.status.success())?;
        let answers: Vec<bool> = String::from_utf8_lossy(&out.stdout)
            .split_whitespace()
            .map(|w| w == "1")
            .collect();
        (answers.len() == pairs.len()).then_some(answers)
    }

    /// `None`: not counter-only. Otherwise the `.py` versions that decide it (none: every differing engine file's bytes are equal).
    fn counter_pairs(&self, a: &str, b: &str) -> Option<Versions> {
        let (ok, out) = git(self.root, &["diff", "--name-status", "--no-renames", a, b]);
        let rows: Vec<(&str, &str)> = out
            .lines()
            .filter_map(|l| l.split_once('\t'))
            .filter(|(_, p)| ENGINE.is_match(p).unwrap_or(false))
            .collect();
        if !ok || rows.is_empty() || rows.iter().any(|(status, _)| *status != "M") {
            return None;
        }
        let mut pairs = Vec::new();
        for (_, path) in &rows {
            let old = git_bytes(self.root, &["show", &format!("{a}:{path}")]);
            let new = git_bytes(self.root, &["show", &format!("{b}:{path}")]);
            if old != new && !crate::checks::has_ext(path, "py") {
                return None;
            }
            pairs.extend((old != new).then_some((old, new)));
        }
        Some(pairs)
    }

    /// Answer every commit pair a run will ask, in one process.
    pub fn prime(&self, asks: &[(String, String)]) {
        let mut todo: Vec<((String, String), Versions)> = Vec::new();
        for ask in asks {
            if self.counters.borrow().contains_key(ask) || todo.iter().any(|(t, _)| t == ask) {
                continue;
            }
            match self.counter_pairs(&ask.0, &ask.1) {
                None => {
                    self.counters.borrow_mut().insert(ask.clone(), false);
                }
                Some(pairs) if pairs.is_empty() => {
                    self.counters.borrow_mut().insert(ask.clone(), true);
                }
                Some(pairs) => todo.push((ask.clone(), pairs)),
            }
        }
        if todo.is_empty() {
            return;
        }
        let flat: Vec<&(Vec<u8>, Vec<u8>)> = todo.iter().flat_map(|(_, p)| p).collect();
        let answers = self.ask_counters(&flat);
        if answers.is_none() {
            *self.failure.borrow_mut() = Some(
                "codeid.py could not say whether the engine files differ only by counter blocks"
                    .to_owned(),
            );
        }
        let mut rest = answers.unwrap_or_default().into_iter();
        for (ask, pairs) in todo {
            let taken: Vec<bool> = pairs.iter().map(|_| rest.next().unwrap_or(false)).collect();
            let same = taken.iter().all(|one| *one);
            self.counters.borrow_mut().insert(ask, same);
        }
    }

    /// Every pair the records can ask, each commit once: against main only where a record can be a baseline, against HEAD only where it
    /// can be the landing record; those the bytes and keys do not already settle. A record no question reaches is not walked.
    fn prime_records(&self, recs: &[Value]) {
        let main = self.main_ref();
        let usable: Vec<&Value> = recs
            .iter()
            .filter(|r| truthy(&r["commit"]) && !truthy(&r["engine_diff"]))
            .collect();
        let mut seen = std::collections::BTreeSet::new();
        let mut asks = Vec::new();
        for r in usable {
            let commit = text(r, "commit");
            if seen.insert((commit.clone(), main)) && !self.same_by_key(&commit, main) {
                asks.push((commit.clone(), main.to_owned()));
            }
            if landing_shaped(r, false)
                && seen.insert((commit.clone(), "HEAD"))
                && !self.same_by_key(&commit, "HEAD")
            {
                asks.push((commit, "HEAD".to_owned()));
            }
        }
        self.prime(&asks);
    }

    /// Is every engine file that differs a modification whose two versions are counter-only-equal? No engine file differing is not one.
    pub fn counter_only(&self, a: &str, b: &str) -> bool {
        let ask = (a.to_owned(), b.to_owned());
        self.prime(std::slice::from_ref(&ask));
        self.counters.borrow().get(&ask).copied().unwrap_or(false)
    }

    fn fresh_seed(&self, reference: Option<&str>) -> u64 {
        let digest = sha256::hex(self.engine_key(reference).as_bytes());
        FRESH_BASE + u64::from_str_radix(&digest[..12], 16).unwrap_or(0) % FRESH_SPAN
    }

    fn on_engine(&self, rec: &Value) -> bool {
        let commit = text(rec, "commit");
        rec.get("commit").is_some_and(truthy)
            && git(
                self.root,
                &[
                    "rev-parse",
                    "-q",
                    "--verify",
                    &format!("{commit}^{{commit}}"),
                ],
            )
            .0
            && self.same_key(&commit, "HEAD")
    }
}

/// Every cohort record, oldest first; a record that does not parse is skipped.
#[must_use]
pub fn records(root: &Path) -> Vec<Value> {
    let mut names: Vec<_> = std::fs::read_dir(root.join(LOG))
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter(|p| {
            let name = p
                .file_name()
                .map(|n| n.to_string_lossy().into_owned())
                .unwrap_or_default();
            name.starts_with(|c: char| c.is_ascii_digit()) && crate::checks::has_ext(&name, "json")
        })
        .collect();
    names.sort();
    names
        .iter()
        .filter_map(|p| serde_json::from_str(&std::fs::read_to_string(p).unwrap_or_default()).ok())
        .collect()
}

fn fixed(rec: &Value) -> Vec<&Value> {
    seeds_of(rec)
        .iter()
        .filter(|s| !is_pinned(int(&s["seed"])) && !truthy(&s["fresh"]))
        .collect()
}

fn fresh(rec: &Value) -> Vec<&Value> {
    seeds_of(rec)
        .iter()
        .filter(|s| truthy(&s["fresh"]))
        .collect()
}

/// 48 fixed seeds from seed 1 at the rolled sizes, no uncommitted engine diff, every seed rolled, and for the landing record its fresh block.
fn landing_shaped(rec: &Value, need_fresh: bool) -> bool {
    int(&rec["first_seed"]) == 1
        && rec["households"].is_null()
        && fixed(rec).len() >= SEEDS
        && !truthy(&rec["engine_diff"])
        && !truthy(&rec["partial"])
        && (fresh(rec).len() >= SEEDS || !need_fresh)
}

/// The records newest first, the order of equal times as they came.
#[must_use]
pub fn newest_first(recs: &[Value]) -> Vec<&Value> {
    let mut sorted: Vec<&Value> = recs.iter().collect();
    sorted.sort_by_key(|r| std::cmp::Reverse(text(r, "utc")));
    sorted
}

fn pick<'r>(repo: &Repo<'_>, recs: &'r [Value]) -> Option<&'r Value> {
    newest_first(recs)
        .into_iter()
        .find(|r| landing_shaped(r, false) && repo.on_engine(r))
}

fn rate_line(rec: &Value) -> String {
    let block = fresh(rec);
    if block.is_empty() {
        return "cohort-gate: the fresh block rolls after the push - a rate, never a refusal - the trend: make cohort-seeds".to_owned();
    }
    let bad: Vec<String> = block
        .iter()
        .filter(|s| s["verdict"] != "pass")
        .map(|s| int(&s["seed"]).to_string())
        .collect();
    let first = block.iter().map(|s| int(&s["seed"])).min().unwrap_or(0);
    let mut out = format!(
        "cohort-gate: fresh block from seed {first}: {} of {} failed ({:.0}%)",
        bad.len(),
        block.len(),
        percent(bad.len(), block.len())
    );
    if !bad.is_empty() {
        let _ = write!(out, " - seeds {}", bad.join(", "));
    }
    out + "; a rate, never a refusal - the trend: make cohort-seeds"
}

/// Why the push refuses this engine under the Rust stage gate (feature 444 amendment 5, FR-019), or nothing.
fn rust_refusal(repo: &Repo<'_>) -> Option<String> {
    let stages = std::fs::read_dir(repo.root.join("rust/phases/src"))
        .into_iter()
        .flatten()
        .flatten();
    if !stages
        .into_iter()
        .any(|e| e.path().extension().is_some_and(|x| x == "rs"))
    {
        return None;
    }
    let key = repo.engine_key(None);
    let mut names: Vec<_> = std::fs::read_dir(repo.root.join(RUST_LOG))
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter(|p| {
            p.extension().is_some_and(|x| x == "json")
                && p.file_name().is_some_and(|n| n != "failing.json")
        })
        .collect();
    names.sort();
    let recs: Vec<Value> = names
        .iter()
        .filter_map(|p| {
            serde_json::from_str::<Value>(&std::fs::read_to_string(p).unwrap_or_default()).ok()
        })
        .filter(|r| text(r, "engine") == key)
        .collect();
    let Some(last) = recs.last() else {
        return Some(format!(
            "no Rust stage gate record on the engine being landed - run: {RUST_COMMAND}"
        ));
    };
    let failing = int(&last["failing"]);
    (failing != 0).then(|| format!("the Rust stage gate has {failing} failing seed(s) on this engine - no Rust stage may end with a failing check (FR-019): fix the Rust stage, then {RUST_COMMAND}"))
}

fn port_state(text: &str) -> Option<String> {
    let data: Value = serde_json::from_str(text).ok()?;
    if !data.is_object() {
        return None;
    }
    let got = if truthy(&data["port"]) {
        data["port"].get("state")?.as_str()?
    } else {
        "rust-only"
    };
    PORT_STATES.contains(&got).then(|| got.to_owned())
}

/// The port switch; a malformed entry closes to the last committed file's state, the state in force.
#[must_use]
pub fn port_mode(root: &Path) -> String {
    let Ok(now) = std::fs::read_to_string(root.join(SWITCHES)) else {
        return "rust-only".to_owned();
    };
    port_state(&now)
        .or_else(|| {
            let (ok, committed) = git(root, &["show", &format!("HEAD:{SWITCHES}")]);
            port_state(&committed).filter(|_| ok)
        })
        .unwrap_or_else(|| "rust-only".to_owned())
}

fn rust_landing(root: &Path) -> bool {
    let (_, base) = git(root, &["merge-base", "HEAD", "origin/main"]);
    let base = if base.trim().is_empty() {
        "origin/main"
    } else {
        base.trim()
    };
    !git(root, &["diff", "--name-only", base, "--", "rust"])
        .1
        .trim()
        .is_empty()
}

/// Feature 386's landing cohort: (refusals, notes).
fn cohort_check(repo: &Repo<'_>) -> (Vec<String>, Vec<String>) {
    let recs = records(repo.root);
    repo.prime_records(&recs);
    let Some(landing) = pick(repo, &recs) else {
        let mut why = format!("no landing cohort ({SEEDS} seeds from seed 1 and the pinned rows) was rolled on the engine being landed - run: {COMMAND}");
        let (_, status) = git(
            repo.root,
            &[
                "status",
                "--porcelain",
                "--untracked-files=all",
                "--",
                "pool",
            ],
        );
        let maps: Vec<&str> = status
            .lines()
            .filter_map(|l| l.get(3..))
            .filter(|p| crate::checks::has_ext(p, "json"))
            .collect();
        if !maps.is_empty() {
            let _ = write!(why, "; the tree has uncommitted pool maps ({}) - the gate regenerated what the change moved: read each diff, commit it, then land again", maps.join(", "));
        }
        return (vec![why], Vec::new());
    };
    let base = known::baselines(landing, &recs, &|c| repo.same_engine(c));
    let (mut refusals, mut notes) = (Vec::new(), Vec::new());
    for line in known::standing(landing, &base) {
        if REFUSING.iter().any(|w| line.contains(w)) {
            refusals.push(line);
        } else {
            notes.push(line);
        }
    }
    notes.push(rate_line(landing));
    (refusals, notes)
}

fn is_rust_gate_refusal(line: &str) -> bool {
    line.starts_with("no Rust stage gate") || line.starts_with("the Rust stage gate")
}

/// (refusals, notes): a landing that changes a Rust stage, or any landing at rust-only, is judged by the Rust stage gate alone (FR-019, FR-023),
/// and at rust-only that gate retired with the Python driver that ran it (feature 444 T39).
fn check(repo: &Repo<'_>) -> (Vec<String>, Vec<String>) {
    let (mut refusals, mut notes) = cohort_check(repo);
    refusals.extend(rust_refusal(repo));
    let rust_only = port_mode(repo.root) == "rust-only";
    if rust_only || rust_landing(repo.root) {
        let (rust, others): (Vec<String>, Vec<String>) =
            refusals.into_iter().partition(|r| is_rust_gate_refusal(r));
        notes.extend(
            others
                .into_iter()
                .map(|r| format!("(a Rust-stage landing, a rate - FR-019) {r}")),
        );
        refusals = rust;
    }
    if rust_only {
        notes.extend(refusals.drain(..).map(|r| format!("(the Rust stage gate retired with the Python driver, feature 444 T39 - not a refusal) {r}")));
    }
    (refusals, notes)
}

fn needs_baseline(repo: &Repo<'_>) -> bool {
    repo.prime_records(&records(repo.root));
    !records(repo.root).iter().any(|r| {
        truthy(&r["commit"]) && landing_shaped(r, false) && repo.same_engine(&text(r, "commit"))
    })
}

fn counter_only_delta(repo: &Repo<'_>) -> bool {
    let (_, base) = git(repo.root, &["merge-base", "HEAD", "origin/main"]);
    !base.trim().is_empty() && repo.counter_only(base.trim(), "HEAD")
}

fn reply(stdout: String, stderr: String, code: i32) -> crate::Reply {
    crate::Reply {
        stdout,
        stderr,
        code,
    }
}

fn exit_of(yes: bool) -> crate::Reply {
    reply(String::new(), String::new(), i32::from(!yes))
}

fn gate_check(repo: &Repo<'_>) -> crate::Reply {
    let (refusals, notes) = check(repo);
    let mut out: String = notes.iter().flat_map(|n| [n.as_str(), "\n"]).collect();
    for line in &refusals {
        let _ = writeln!(out, "cohort-gate: REFUSED {line}");
    }
    crate::stamp::record_for(
        repo.root,
        USAGE_LOG_TOOL,
        if refusals.is_empty() {
            "passed"
        } else {
            "refused"
        },
    );
    reply(out, String::new(), i32::from(!refusals.is_empty()))
}

/// `l7r-gate cohort ...`.
pub fn cli(args: &[String], root: &Path, python: &str) -> crate::Reply {
    let words: Vec<&str> = args.iter().map(String::as_str).collect();
    let repo = Repo::new(root, python);
    let reply_of = answer(&words, &repo, root);
    match repo.failure.take() {
        Some(why) => reply(String::new(), format!("cohort: {why}\n"), 2),
        None => reply_of,
    }
}

fn answer(words: &[&str], repo: &Repo<'_>, root: &Path) -> crate::Reply {
    match words {
        [] | ["check"] => gate_check(repo),
        ["fresh-seed"] => reply(format!("{}\n", repo.fresh_seed(None)), String::new(), 0),
        ["fresh-seed", reference] => reply(format!("{}\n", repo.fresh_seed(Some(reference))), String::new(), 0),
        ["engine-key", reference] => reply(format!("{}\n", repo.engine_key(Some(reference))), String::new(), 0),
        ["port"] => reply(format!("{}\n", port_mode(root)), String::new(), 0),
        ["counter-only"] => exit_of(counter_only_delta(repo)),
        ["needs-baseline"] => exit_of(needs_baseline(repo)),
        ["rust-owed"] => exit_of(rust_refusal(repo).is_some() && port_mode(root) != "rust-only"),
        ["known", rest @ ..] => known::cli(rest, repo),
        ["seeds", rest @ ..] => seeds::cli(rest, root),
        ["room-table"] => room::render(root),
        ["names-fit", text] => exit_of(room::names_fit(text)),
        _ => reply(String::new(), format!("cohort: unknown command {words:?} (fresh-seed | check | needs-baseline | counter-only | rust-owed | engine-key | port | known | seeds | room-table | names-fit)\n"), 2),
    }
}

#[cfg(test)]
mod tests;
