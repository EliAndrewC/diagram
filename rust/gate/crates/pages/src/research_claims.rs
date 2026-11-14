//! The research claims sign-up sheet, claimed and asked through one tool - never opened by hand (feature 376). Ported whole from
//! `scripts/pages/research_claims.py` by feature 449 T137 (`ask:449-phase3-remainder`):
//!
//! ```text
//! l7r-gate research-claims claim <questions> --feature N [--status S] [--release OWNER --why W]   make research-claim
//! l7r-gate research-claims query <questions>                                                     make research-claims
//! l7r-gate research-claims sweep                                 release every live claim of a closed feature, one line each
//! ```
//!
//! WHY (the GM, 2026-10-10, specs/376-research-group-fixed-costs/request.md): *"any time we have a process that requires editing a
//! potentially large file, then we should use tooling to edit the file ... the same sensibility that is why we have a make target for
//! doing a task tick"*. Parallel research sessions share `/diagram/.clones/RESEARCH-CLAIMS.md`: a session says which questions it is
//! working on and checks that nobody else holds them. By 2026-10-10 the sheet was 1,138 lines (170 KB), and a check by page name (`make
//! lines KEY=<page>`) returned a median of 4,147 characters, carried on every later turn - about 16 M tokens across the research groups
//! after feature 274 (376's spec).
//!
//! A LINE keeps the sheet's own shape, `<owner> | <feature> | <item> | <status> | <date>`; a new one names its questions as
//! `Q=0060,0246`. A line names a question by any 4-digit number in its item, or by an old `<page>/<NNN>` or `<page> <NNN>` (`PAGE=<page>
//! SECTION=<NNN>` too) mapped through `research/moved-303.json`.
//!
//! A claim is LIVE while it is the latest line of its owner naming that question and that line carries none of `done`, `released`,
//! `landed`, `complete` or `withdrawn` after its owner (the spec: "an old line counts as live unless a later line for the same owner and
//! item says it is done" - old lines put the word in the item or a sixth field, so the whole line is read). A forgotten claim is released
//! by a later line: by name with a reason, or by `sweep`, which writes one release line for each live claim whose feature `make
//! speckit-todo` reads as closed (plan review of 376, which ruled an implicit retirement by the feature's state outside the spec).
//!
//! The OWNER is the clone's directory name, so a session cannot claim as another; another owner's stale claim is released only by name
//! and with a reason (`--release OWNER --why`), which the line records. A claim is read, checked and appended under `flock` on
//! `<sheet>.lock` (the lock `flock(1)` and the Python's `fcntl.flock` take, so a session on either side waits for the other). Output is
//! one line per live claim the questions touch, and one summary line.

use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::fmt::Write as _;
use std::io::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::py_text::strip;
use l7r_guard::shared::speckit::{py_name, py_parent, splitlines};
use serde_json::Value;

use crate::{py_path, raised, reply, text};
use l7r_gate_core::Reply;

/// The sheet every clone shares, unless `L7R_CLAIMS_SHEET` names another.
pub const SHEET: &str = "/diagram/.clones/RESEARCH-CLAIMS.md";

/// The sheet: `L7R_CLAIMS_SHEET` as `pathlib.Path` reads it (an empty value the directory `.`, as the Python's was), else [`SHEET`].
#[must_use]
pub fn sheet(var: Option<String>) -> PathBuf {
    py_path(&var.unwrap_or_else(|| SHEET.to_owned()))
}

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static RELEASED: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?i)\b(done|released|landed|complete|withdrawn)\b"));
// `RELEASED.match(status)`: anchored at the start, where `search` is not
static RELEASED_AT_START: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?i)^\b(done|released|landed|complete|withdrawn)\b"));
static QNUM: LazyLock<Regex> = LazyLock::new(|| re(r"(?<![\d.])(\d{4})(?![\d])"));
// an old page name and the RUN of three-digit section numbers after it - `<page> 050 110 145`, `<page>/090 080`, or the PAGE= / SECTION=
// arguments (plan review: 27 of 300 owner-question pairs sat after the first number of a run)
static OLD: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?:PAGE=)?([a-z][a-z-]*(?:/[a-z][a-z-]*)?)((?:(?:/|\s+SECTION=|\s*,?\s+(?:and\s+)?)\d{3}(?![\d]))+)",
    )
});
static THREE: LazyLock<Regex> = LazyLock::new(|| re(r"\d{3}"));
static FOUR: LazyLock<Regex> = LazyLock::new(|| re(r"\d{4}"));
static OLD_FILE: LazyLock<Regex> = LazyLock::new(|| re(r"^(.+)/(\d{3})-"));
static NEW_FILE: LazyLock<Regex> = LazyLock::new(|| re(r"questions/(\d{4})-"));

/// Every match of `rx` in `text`, its group `g`.
fn all(rx: &Regex, text: &str, g: usize) -> Vec<String> {
    rx.captures_iter(text)
        .filter_map(Result::ok)
        .filter_map(|c| c.get(g).map(|m| m.as_str().to_owned()))
        .collect()
}

/// One line of the sheet: its owner, feature, item, status, date and the line itself.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Row {
    pub owner: String,
    pub feature: String,
    pub item: String,
    pub status: String,
    pub date: String,
    pub line: String,
}

/// The repository's top (`git rev-parse --show-toplevel` in `cwd`), else `.`.
fn root(cwd: &Path) -> PathBuf {
    let top = l7r_gate_core::record::repo::git(cwd, &["rev-parse", "--show-toplevel"]);
    py_path(strip(&top))
}

/// The mirror a clone belongs to (`<mirror>/.clones/<name>`), else the tree itself.
fn mirror(top: &Path) -> PathBuf {
    let up = py_parent(top);
    if py_name(&up) == ".clones" {
        py_parent(&up)
    } else {
        top.to_path_buf()
    }
}

/// (old page, old section number) -> the question's number, from feature 303's move record; nothing where it cannot be read.
fn old_map(top: &Path) -> HashMap<(String, u32), String> {
    let read = std::fs::read(top.join("research/moved-303.json"))
        .ok()
        .and_then(|b| String::from_utf8(b).ok())
        .and_then(|t| serde_json::from_str::<Value>(&t).ok());
    let mut out = HashMap::new();
    let Some(files) = read
        .as_ref()
        .and_then(|v| v.get("files"))
        .and_then(Value::as_object)
    else {
        return out;
    };
    for (old, new) in files {
        let new = new.as_str().unwrap_or("");
        let m = OLD_FILE.captures(old).ok().flatten();
        let n = NEW_FILE.captures(new).ok().flatten();
        if let (Some(m), Some(n)) = (m, n) {
            if let Ok(section) = m[2].parse() {
                out.insert((m[1].to_owned(), section), n[1].to_owned());
            }
        }
    }
    out
}

fn questions_of(item: &str, olds: &HashMap<(String, u32), String>) -> BTreeSet<String> {
    let mut found: BTreeSet<String> = all(&QNUM, item, 1).into_iter().collect();
    for caps in OLD.captures_iter(item).filter_map(Result::ok) {
        let page = caps.get(1).map_or("", |m| m.as_str());
        let run = caps.get(2).map_or("", |m| m.as_str());
        for num in all(&THREE, run, 0) {
            if let Some(q) = num
                .parse()
                .ok()
                .and_then(|n: u32| olds.get(&(page.to_owned(), n)))
            {
                found.insert(q.clone());
            }
        }
    }
    found
}

/// A line of the sheet, or None for a comment or a line of fewer than three cells.
#[must_use]
pub fn parse(line: &str) -> Option<Row> {
    let parts: Vec<&str> = line.split('|').map(strip).collect();
    if parts.len() < 3 || strip_start(line).starts_with('#') {
        return None;
    }
    let at = |i: usize| parts.get(i).map_or_else(String::new, |p| (*p).to_owned());
    Some(Row {
        owner: at(0),
        feature: at(1),
        item: at(2),
        status: at(3),
        date: at(4),
        line: line.trim_end_matches('\n').to_owned(),
    })
}

fn strip_start(text: &str) -> &str {
    text.trim_start_matches(l7r_guard::shared::py_text::is_space)
}

/// Every feature number `make speckit-todo` reads as closed in the mirror's specs/ (and this clone's), in process (the guard's
/// `shared::speckit`, which `l7r-gate speckit-todo --each-state` serves, where the Python asked that command once). The top's vocabulary
/// read once: a broken one retires nothing, as the command's raise did; a directory that cannot be read is skipped, as its `error:` line
/// was. A top with no gate of its own retires nothing, as the Python's run of its missing `scripts/gates/l7r-gate.sh` did.
fn settled_features(top: &Path) -> BTreeSet<String> {
    use l7r_guard::shared::speckit::{state_given_vocabulary, vocabulary};
    let mut roots: Vec<PathBuf> = vec![mirror(top).join("specs"), top.join("specs")];
    roots.dedup();
    let dirs: Vec<PathBuf> = roots
        .iter()
        .filter_map(|specs| std::fs::read_dir(specs).ok())
        .flatten()
        .filter_map(Result::ok)
        .map(|e| e.path())
        .filter(|d| {
            let n = py_name(d);
            n.len() >= 4
                && n.as_bytes()[..3].iter().all(u8::is_ascii_digit)
                && n.as_bytes()[3] == b'-'
        })
        .collect();
    if dirs.is_empty()
        || !runnable(&top.join("scripts/gates/l7r-gate.sh"))
        || vocabulary(top).is_err()
    {
        return BTreeSet::new();
    }
    dirs.iter()
        .filter(|d| {
            state_given_vocabulary(d)
                .is_ok_and(|s| s == "closed" || s == "done - GM review pending")
        })
        .map(|d| py_name(d).split('-').next().unwrap_or("").to_owned())
        .collect()
}

/// Whether a file is there to run (a file with an execute bit), as the Python's `subprocess.run` of it found it.
fn runnable(path: &Path) -> bool {
    use std::os::unix::fs::PermissionsExt as _;
    std::fs::metadata(path).is_ok_and(|m| m.is_file() && m.permissions().mode() & 0o111 != 0)
}

/// question -> the live claims on it (the latest line of each owner naming it, carrying no released word), in the order the Python's
/// dicts kept: an owner's question by its first line, its row the last.
fn live(lines: &[&str], top: &Path) -> BTreeMap<String, Vec<Row>> {
    let olds = old_map(top);
    let mut order: Vec<(String, String)> = Vec::new();
    let mut latest: HashMap<(String, String), Row> = HashMap::new();
    for line in lines {
        let Some(row) = parse(line) else {
            continue;
        };
        for q in questions_of(&row.item, &olds) {
            let key = (row.owner.clone(), q);
            if !latest.contains_key(&key) {
                order.push(key.clone());
            }
            latest.insert(key, row.clone());
        }
    }
    let mut out: BTreeMap<String, Vec<Row>> = BTreeMap::new();
    for key in order {
        let row = &latest[&key];
        let after_owner = row
            .line
            .split_once('|')
            .map_or(row.line.as_str(), |(_, r)| r);
        if RELEASED.is_match(after_owner).unwrap_or(false) {
            continue;
        }
        out.entry(key.1).or_default().push(row.clone());
    }
    out
}

/// The rows of `held` on the questions `qs` that `keep` keeps, one per line (the first line's place, its last row), as the Python's
/// `{r["line"]: r for ...}` kept them.
fn distinct(
    held: &BTreeMap<String, Vec<Row>>,
    qs: &[String],
    keep: &dyn Fn(&Row) -> bool,
) -> Vec<Row> {
    let mut out: Vec<Row> = Vec::new();
    for r in qs
        .iter()
        .filter_map(|q| held.get(q))
        .flatten()
        .filter(|r| keep(r))
    {
        if let Some(at) = out.iter_mut().find(|o| o.line == r.line) {
            *at = r.clone();
        } else {
            out.push(r.clone());
        }
    }
    out
}

/// The sheet's lines, none where it is no file.
fn read_lines(sheet: &Path) -> String {
    if sheet.is_file() {
        l7r_guard::shared::speckit::read_text(sheet).unwrap_or_default()
    } else {
        String::new()
    }
}

/// The sheet's lock held: `<sheet>.lock` opened (its directory made) and `flock`ed exclusively, until the file is dropped. Its failures
/// are what the Python's `mkdir`, `open` or `fcntl.flock` raised.
fn locked(sheet: &Path) -> Result<std::fs::File, String> {
    let lock = PathBuf::from(format!("{}.lock", text(sheet)));
    let fail = |e: std::io::Error| format!("{}: {e}", lock.display());
    std::fs::create_dir_all(py_parent(sheet)).map_err(fail)?;
    let file = std::fs::OpenOptions::new()
        .read(true)
        .append(true)
        .create(true)
        .open(&lock)
        .map_err(fail)?;
    let refused = format!("{}: flock failed", lock.display());
    l7r_guard::shared::tool::flock(&file, "-x")
        .then_some(file)
        .ok_or(refused)
}

/// `open(sheet, "a")` and `lines` written to it.
fn append(sheet: &Path, lines: &[String]) -> Result<(), String> {
    let fail = |e: std::io::Error| format!("{}: {e}", sheet.display());
    let body: String = lines.iter().flat_map(|l| [l.as_str(), "\n"]).collect();
    std::fs::OpenOptions::new()
        .append(true)
        .create(true)
        .open(sheet)
        .and_then(|mut fh| fh.write_all(body.as_bytes()))
        .map_err(fail)
}

/// One release line for each live claim whose feature `make speckit-todo` reads as closed - the later line the spec asks for, written
/// once, not a rule applied silently on every read.
///
/// # Errors
///
/// What the lock or the write raised.
pub fn sweep(top: &Path, sheet: &Path, today: &str) -> Result<String, String> {
    let done = settled_features(top);
    let _lock = locked(sheet)?;
    let text = read_lines(sheet);
    let held = live(&splitlines(&text), top);
    let mut by_owner: BTreeMap<(String, String), BTreeSet<String>> = BTreeMap::new();
    for (q, rows) in &held {
        for r in rows {
            let feat = feature_number(&r.feature);
            if !feat.is_empty() && done.contains(&feat) {
                by_owner
                    .entry((r.owner.clone(), feat))
                    .or_default()
                    .insert(q.clone());
            }
        }
    }
    let name = py_name(top);
    let lines: Vec<String> = by_owner
        .iter()
        .map(|((o, f), qs)| {
            let qs: Vec<&str> = qs.iter().map(String::as_str).collect();
            format!(
                "{o} | {f} | Q={} | released by {name}: feature {f} is closed (make speckit-todo) | {today}",
                qs.join(",")
            )
        })
        .collect();
    append(sheet, &lines)?;
    let claims: usize = by_owner.values().map(BTreeSet::len).sum();
    Ok(format!(
        "research-claims sweep: {} release line(s) for {claims} claim(s) of closed features",
        lines.len()
    ))
}

/// The first three digits of a feature cell (`re.search(r"\d{3}", ...)`), "" where there are none.
fn feature_number(feature: &str) -> String {
    THREE
        .find(feature)
        .ok()
        .flatten()
        .map_or_else(String::new, |m| m.as_str().to_owned())
}

/// The questions a `Q=` names, sorted and distinct.
///
/// # Errors
///
/// It names none: the Python's `SystemExit` message.
pub fn asked(spec: &str) -> Result<Vec<String>, String> {
    let qs: BTreeSet<String> = all(&FOUR, spec, 0).into_iter().collect();
    if qs.is_empty() {
        return Err(
            "research-claims: Q= names no question - give their numbers, e.g. Q=\"0060 0246\""
                .to_owned(),
        );
    }
    Ok(qs.into_iter().collect())
}

fn show(row: &Row) -> String {
    format!(
        "  {} | {} | {} | {} | {}",
        row.owner, row.feature, row.item, row.status, row.date
    )
}

/// The live claims on `qs`: (1 when there are some, else 0; what is printed).
#[must_use]
pub fn query(qs: &[String], top: &Path, sheet: &Path) -> (i32, String) {
    let text = read_lines(sheet);
    let held = live(&splitlines(&text), top);
    let rows = distinct(&held, qs, &|_| true);
    if rows.is_empty() {
        return (
            0,
            format!("research-claims: no live claim on {}", qs.join(" ")),
        );
    }
    let mut out = format!(
        "research-claims: {} live claim(s) on {}:",
        rows.len(),
        qs.join(" ")
    );
    for r in &rows {
        let _ = write!(out, "\n{}", show(r));
    }
    (1, out)
}

/// What a claim asks: its questions, feature and status, and the owner it releases with why.
pub struct Ask<'a> {
    pub qs: &'a [String],
    pub feature: &'a str,
    pub status: &'a str,
    pub release: &'a str,
    pub why: &'a str,
}

/// A claim (or a release) appended under the lock: (0 recorded, 1 refused - another session holds one, 2 a release with no why; what is
/// printed).
///
/// # Errors
///
/// What the lock or the write raised.
pub fn claim(ask: &Ask, top: &Path, sheet: &Path, today: &str) -> Result<(i32, String), String> {
    let owner = py_name(top);
    let qs = ask.qs.join(",");
    let _lock = locked(sheet)?;
    let text = read_lines(sheet);
    let held = live(&splitlines(&text), top);
    let line = if ask.release.is_empty() {
        let others = distinct(&held, ask.qs, &|r| r.owner != owner);
        if !others.is_empty() && !RELEASED_AT_START.is_match(ask.status).unwrap_or(false) {
            let mut out = format!(
                "research-claim: REFUSED - another session holds {} of these:",
                others.len()
            );
            for r in &others {
                let _ = write!(out, "\n{}", show(r));
            }
            out += "\n  if a claim is stale (its session gone), release it: make research-claim Q=<n> FEATURE=<f> RELEASE=<owner> WHY=\"<why>\"";
            return Ok((1, out));
        }
        format!(
            "{owner} | {} | Q={qs} | {} | {today}",
            ask.feature, ask.status
        )
    } else {
        if ask.why.is_empty() {
            return Ok((
                2,
                "research-claim: RELEASE=<owner> needs WHY=\"<why the claim is stale>\" - it is written on the line".to_owned(),
            ));
        }
        format!(
            "{} | {} | Q={qs} | released by {owner}: {} | {today}",
            ask.release, ask.feature, ask.why
        )
    };
    append(sheet, std::slice::from_ref(&line))?;
    Ok((0, format!("research-claim: recorded - {line}")))
}

const USAGE: &str = "usage: l7r-gate research-claims [-h] [--feature FEATURE] [--status STATUS] [--release RELEASE] [--why WHY] {claim,query,sweep} [questions]\n";

/// What the command reads of its process.
pub struct Env {
    /// The working directory, whose repository's top is the owner.
    pub cwd: PathBuf,
    /// `L7R_CLAIMS_SHEET`, else [`SHEET`].
    pub sheet: PathBuf,
    /// The local date, `datetime.date.today().isoformat()`, asked only by a write.
    pub today: fn() -> String,
}

/// `l7r-gate research-claims claim|query|sweep ...`: the Python's exits - a query 0, a claim 0, 1 refused or 2 for a release with no why
/// or no feature, `Q=` naming nothing 1 (its `SystemExit`), argparse's 2 on a command line it cannot read.
#[must_use]
pub fn cli(args: &[String], env: &Env) -> Reply {
    use l7r_gate_core::record::args::{parse_with, Spec};
    let usage = |why: &str| {
        reply(
            String::new(),
            format!("{USAGE}l7r-gate research-claims: error: {why}\n"),
            2,
        )
    };
    let specs = [
        Spec::value("--feature"),
        Spec::value("--status"),
        Spec::value("--release"),
        Spec::value("--why"),
    ];
    let p = match parse_with(args, &specs, 2) {
        Ok(p) => p,
        Err(why) => return usage(&why),
    };
    let op = p.positional.first().map_or("", String::as_str);
    if op.is_empty() {
        return usage("the following arguments are required: op");
    }
    if !["claim", "query", "sweep"].contains(&op) {
        return usage(&format!(
            "argument op: invalid choice: '{op}' (choose from claim, query, sweep)"
        ));
    }
    if op == "sweep" {
        return match sweep(&root(&env.cwd), &env.sheet, &(env.today)()) {
            Ok(said) => reply(format!("{said}\n"), String::new(), 0),
            Err(why) => raised("research-claims", String::new(), &why),
        };
    }
    let qs = match asked(p.positional.get(1).map_or("", String::as_str)) {
        Ok(qs) => qs,
        Err(why) => return reply(String::new(), format!("{why}\n"), 1),
    };
    let top = root(&env.cwd);
    if op == "query" {
        return reply(
            format!("{}\n", query(&qs, &top, &env.sheet).1),
            String::new(),
            0,
        );
    }
    let feature = p.text("--feature", "");
    if !THREE.is_match(feature).unwrap_or(false) {
        return reply(
            String::new(),
            "research-claim: FEATURE=<number> is required - the feature the work belongs to\n"
                .to_owned(),
            2,
        );
    }
    let ask = Ask {
        qs: &qs,
        feature,
        status: p.text("--status", "in progress"),
        release: p.text("--release", ""),
        why: p.text("--why", ""),
    };
    match claim(&ask, &top, &env.sheet, &(env.today)()) {
        Ok((0, said)) => reply(format!("{said}\n"), String::new(), 0),
        Ok((code, said)) => reply(String::new(), format!("{said}\n"), code),
        Err(why) => raised("research-claims", String::new(), &why),
    }
}

#[cfg(test)]
mod tests;
