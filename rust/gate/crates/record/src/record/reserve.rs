//! Reserve the next glossary, registry-entry, question or uncited prefix under a host-wide lock (`scripts/record/reserve-prefix.py`,
//! features 265, 274, 288, 303, 305, 312; ported by feature 449 T145, phase 4's S2 under `ask:449-phase4-slices`): `l7r-gate record
//! reserve` (`make reserve`, the new-file suite), and [`reserve`] in process for `apply-edits`' glossary terms. NEXT is read under the lock:
//! 10 past the highest prefix held by the mirror's tree, every clone under `<mirror>/.clones/` and the ledger
//! `<mirror>/.specify/prefixes.jsonl`; the reservation is the file, a stub written before the lock is released. A write session's
//! registry key past its cap (`L7R_KEY_CAP`) is refused unless `KEY_CAP_OK` gives a reason, taken in process through `pages`'
//! `escape_log` where the Python ran `l7r-gate escape take`. `reserve-prefix.py` stays the implementation for `uncited.py`, its Python
//! importer, until S3b; an edit of it makes the same change here in the same commit (the ruling's Q1).

use std::fmt::Write as _;
use std::io::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_pages::escape_log::{escape, Env};
use l7r_gate_research::record::source_tags::{load_vocabulary, parse};
use l7r_gate_research::resolve;
use l7r_guard::shared::consulted;
use l7r_guard::shared::py_text::{fmt_g, repr, strip};
use l7r_guard::shared::pyjson::{dumps, py_str};
use serde_json::{json, Value};

/// Each kind's directory under the clone, in `sorted(DIRS)` order.
pub const DIRS: [(&str, &str); 4] = [
    ("glossary", "l7r/diagram/interactive/assets/glossary"),
    ("question", "research/questions"),
    ("registry", "research/sources/010-works-cited"),
    ("uncited", "research/sources/040-uncited-works"),
];
pub const LEDGER: &str = "prefixes.jsonl";
/// A registry stub's tags marker before its tags are given (feature 305 FR-011).
pub const TAGS_PLACEHOLDER: &str = "<!-- tags: period=<period>; region=<region>; kind=<kind> -->";

static NUMBERED: LazyLock<Regex> = LazyLock::new(|| l7r_gate_research::pyre::py(r"^(\d+)-"));

/// Why a reservation did not happen: the tool's own refusal (`reserve: ...`, exit 2), or what the Python raised and did not catch.
#[derive(Debug, PartialEq, Eq)]
pub enum Refused {
    Refusal(String),
    Raised(String, String),
}

fn raised(kind: &str, message: String) -> Refused {
    Refused::Raised(kind.to_owned(), message)
}

#[expect(
    clippy::needless_pass_by_value,
    reason = "a `map_err` adapter, named so each call stays one line"
)]
fn os_error(e: std::io::Error) -> Refused {
    raised("OSError", e.to_string())
}

fn from_fault(f: l7r_guard::shared::blocked::Fault) -> Refused {
    raised(f.kind, f.message)
}

fn dir_of(kind: &str) -> &'static str {
    DIRS.iter().find(|(k, _)| *k == kind).map_or("", |(_, d)| d)
}

/// `SHARED`: kinds that share one number sequence and one key space.
fn kinds(kind: &str) -> Vec<&str> {
    if matches!(kind, "registry" | "uncited") {
        vec!["registry", "uncited"]
    } else {
        vec![kind]
    }
}

/// `name_for`: the file name after the prefix.
#[must_use]
pub fn name_for(kind: &str, key: &str) -> String {
    let base = if kind == "glossary" {
        key.replace('%', "%25").replace('/', "%2F")
    } else {
        key.to_owned()
    };
    format!(
        "{base}{}",
        if kind == "glossary" { ".json" } else { ".html" }
    )
}

/// A number Python's `int()` reads from its decimal digits, any of Unicode's.
fn int_of(digits: &str) -> u64 {
    digits.chars().fold(0u64, |n, c| {
        n.saturating_mul(10)
            .saturating_add(u64::from(l7r_gate_research::digit_value(c).unwrap_or(0)))
    })
}

fn names(d: &Path) -> Vec<(PathBuf, String)> {
    std::fs::read_dir(d)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| (e.path(), e.file_name().to_string_lossy().into_owned()))
        .collect()
}

/// `holding`: the files in `d` that hold exactly this key - a prefix, a hyphen, then the key's own file name.
#[must_use]
pub fn holding(d: &Path, kind: &str, key: &str) -> Vec<PathBuf> {
    let name = name_for(kind, key);
    names(d)
        .into_iter()
        .filter(|(_, n)| {
            n.strip_suffix(&format!("-{name}")).is_some_and(|head| {
                !head.is_empty()
                    && head
                        .chars()
                        .all(|c| l7r_gate_research::digit_value(c).is_some())
            })
        })
        .map(|(p, _)| p)
        .collect()
}

fn prefixes_in(d: &Path) -> Vec<u64> {
    names(d)
        .into_iter()
        .filter_map(|(_, n)| NUMBERED.captures(&n).ok().flatten().map(|c| int_of(&c[1])))
        .collect()
}

/// The ledger's rows that parse, each a mapping (Python's `AttributeError` otherwise).
fn ledger_rows(mirror: &Path) -> Result<Vec<serde_json::Map<String, Value>>, Refused> {
    let path = mirror.join(".specify").join(LEDGER);
    let rows = consulted::read_lines(&path).map_err(from_fault)?;
    rows.into_iter()
        .map(|r| match r {
            Value::Object(m) => Ok(m),
            other => Err(raised(
                "AttributeError",
                format!(
                    "'{}' object has no attribute 'get'",
                    l7r_guard::shared::blocked::type_name(&other)
                ),
            )),
        })
        .collect()
}

/// `int(row.get("prefix", default))`.
fn prefix_of(row: &serde_json::Map<String, Value>, default: i64) -> Result<i64, Refused> {
    match row.get("prefix") {
        None => Ok(default),
        // a float truncates as `int()` truncates it; a JSON number is always one or the other
        #[expect(
            clippy::cast_possible_truncation,
            reason = "int() of a float is its truncation"
        )]
        Some(Value::Number(n)) => Ok(n
            .as_i64()
            .unwrap_or_else(|| n.as_f64().unwrap_or(0.0).trunc() as i64)),
        Some(Value::Bool(b)) => Ok(i64::from(*b)),
        Some(Value::String(s)) => strip(s).parse().map_err(|_| {
            raised(
                "ValueError",
                format!("invalid literal for int() with base 10: {}", repr(s)),
            )
        }),
        Some(other) => Err(raised(
            "TypeError",
            format!(
                "int() argument must be a string, a bytes-like object or a real number, not '{}'",
                l7r_guard::shared::blocked::type_name(other)
            ),
        )),
    }
}

/// `highest`: the highest prefix of the kind's sequence anywhere it is held.
fn highest(kind: &str, root: &Path, mirror: &Path) -> Result<i64, Refused> {
    let ks = kinds(kind);
    let mut held: Vec<i64> = Vec::new();
    for k in &ks {
        held.extend(
            prefixes_in(&mirror.join(dir_of(k)))
                .into_iter()
                .chain(prefixes_in(&root.join(dir_of(k))))
                .map(|p| i64::try_from(p).unwrap_or(i64::MAX)),
        );
    }
    for (c, _) in names(&mirror.join(".clones")) {
        for k in &ks {
            held.extend(
                prefixes_in(&c.join(dir_of(k)))
                    .into_iter()
                    .map(|p| i64::try_from(p).unwrap_or(i64::MAX)),
            );
        }
    }
    for row in ledger_rows(mirror)? {
        if row
            .get("kind")
            .and_then(Value::as_str)
            .is_some_and(|k| ks.contains(&k))
        {
            held.push(prefix_of(&row, 0)?);
        }
    }
    Ok(held.into_iter().max().unwrap_or(0))
}

/// `held_elsewhere`: where another clone already holds this key, else "".
fn held_elsewhere(kind: &str, key: &str, root: &Path, mirror: &Path) -> Result<String, Refused> {
    let ks = kinds(kind);
    let me = resolve(root);
    let cwd = std::env::current_dir().unwrap_or_default();
    for row in ledger_rows(mirror)? {
        let mine = row
            .get("kind")
            .and_then(Value::as_str)
            .is_some_and(|k| ks.contains(&k));
        let clone = row.get("clone").map(py_str).unwrap_or_default();
        if mine
            && row.get("key").and_then(Value::as_str) == Some(key)
            && resolve(&cwd.join(&clone)) != me
        {
            let f = |k: &str| row.get(k).map_or_else(|| "None".to_owned(), py_str);
            return Ok(format!(
                "{} (reserved {}, {})",
                f("clone"),
                f("prefix"),
                f("utc")
            ));
        }
    }
    let mut clones: Vec<PathBuf> = names(&mirror.join(".clones"))
        .into_iter()
        .map(|(p, _)| p)
        .collect();
    clones.sort();
    for c in clones {
        if resolve(&c) != me
            && ks
                .iter()
                .any(|k| !holding(&c.join(dir_of(k)), k, key).is_empty())
        {
            return Ok(c.to_string_lossy().into_owned());
        }
    }
    Ok(String::new())
}

/// `check_key_cap`: a write session's registry key past its cap refused, unless `KEY_CAP_OK` gives a reason (feature 274 D4).
fn check_key_cap(kind: &str, key: &str, mirror: &Path, ask: &Ask<'_>) -> Result<(), Refused> {
    let var = ask.var;
    let (session, cap) = (var("L7R_PAGE_SESSION"), var("L7R_KEY_CAP"));
    if kind != "registry"
        || session.is_empty()
        || cap.is_empty()
        || !cap.chars().all(|c| c.is_ascii_digit())
    {
        return Ok(());
    }
    let mut n = 0;
    for row in ledger_rows(mirror)? {
        n += usize::from(
            row.get("kind").and_then(Value::as_str) == Some("registry")
                && row.get("session").and_then(Value::as_str) == Some(session.as_str()),
        );
    }
    if n < cap.parse().unwrap_or(usize::MAX) {
        return Ok(());
    }
    let context = json!({"key": key, "session": session, "reserved": n});
    let lookup = |k: &str| Some(var(k)).filter(|v| !v.is_empty());
    let env = Env {
        var: &lookup,
        cwd: std::env::current_dir().unwrap_or_default(),
        command: ask.command.clone(),
    };
    match escape("KEY_CAP_OK", "reserve", "key-cap", Some(&context), &env) {
        Ok(true) => return Ok(()),
        Ok(false) => {}
        Err(why) => return Err(Refused::Refusal(why)),
    }
    let cont = Some(var("L7R_CONTINUE"))
        .filter(|c| !c.is_empty())
        .unwrap_or_else(|| "$L7R_CONTINUE".to_owned());
    Err(Refused::Refusal(format!(
        "this write session has reserved {n} new registry keys, its cap (feature 274: a write session takes at most {cap}; its cost grows with its length). Do not reserve {}. Finish the question in hand with the keys you have; then write the items you have not reached to {cont} as a brief of the same shape - the same header, a `## Your items` list of just those items, the same handoff path - commit, and stop. The runner starts that brief next, in a fresh session. For a deliberate larger load: KEY_CAP_OK='<reason>'",
        repr(key)
    )))
}

/// `tags_marker`: the marker for `TAGS=`, checked against the clone's `source-tags.json`.
fn tags_marker(tags: &str, root: &Path) -> Result<String, Refused> {
    let checked = load_vocabulary(&root.join("research"))
        .and_then(|v| parse(&format!("<!-- tags: {tags} -->"), "TAGS", &v));
    match checked {
        // the marker is the one this builds, so a parse always finds it
        Ok(t) => Ok(t.map(|t| t.marker()).unwrap_or_default()),
        // the Python's `except st.SourceTagError` turns that into the refusal; anything else (a vocabulary that is not UTF-8) it raised
        Err(e) => Err(if e.kind == "SourceTagError" {
            Refused::Refusal(e.message)
        } else {
            raised(e.kind, e.message)
        }),
    }
}

/// `registry_stub`: a registry entry's opening, naming its pointer, its tags marker last.
#[must_use]
pub fn registry_stub(key: &str, url: &str, marker: &str) -> String {
    let pointer = if url.is_empty() {
        String::new()
    } else {
        format!("<p>({url})</p>\n")
    };
    format!("<h3 id=\"{key}\"><code>{key}</code></h3>\n{pointer}{marker}\n")
}

/// `question_stub`: a new question's page, its tags marker the build refuses until it is filled.
#[must_use]
pub fn question_stub(key: &str) -> String {
    format!("<h2 id=\"{key}\">TITLE</h2>\n<!-- tags: subject=<subject>; setting=<setting>; level=<level> -->\n<p></p>\n")
}

/// A reservation's request.
pub struct Ask<'a> {
    pub kind: &'a str,
    pub key: &'a str,
    pub root: &'a Path,
    pub mirror: Option<&'a Path>,
    pub stub: Option<String>,
    pub timeout: f64,
    pub url: &'a str,
    pub tags: &'a str,
    /// The caller's command line, for the key cap's escape entry.
    pub command: String,
    /// The environment the key cap reads (`L7R_PAGE_SESSION`, `L7R_KEY_CAP`, `L7R_CONTINUE`, `KEY_CAP_OK`): the process's, or a test's.
    pub var: &'a dyn Fn(&str) -> String,
}

/// `reserve`: the new file's path, its prefix reserved and a stub written before the lock is released.
///
/// # Errors
/// A refusal (`Refused::Refusal`), or what the Python raised.
pub fn reserve(ask: &Ask<'_>) -> Result<PathBuf, Refused> {
    let (kind, key, root) = (ask.kind, ask.key, ask.root);
    if !DIRS.iter().any(|(k, _)| *k == kind) {
        return Err(Refused::Refusal(
            "KIND must be one of ['glossary', 'question', 'registry', 'uncited']".to_owned(),
        ));
    }
    let entry = matches!(kind, "registry" | "uncited");
    if !ask.url.is_empty() && !entry {
        return Err(Refused::Refusal(
            "URL= names a registry entry's source - it is for KIND=registry or KIND=uncited only"
                .to_owned(),
        ));
    }
    if !ask.tags.is_empty() && !entry {
        return Err(Refused::Refusal("TAGS= are a registry entry's source tags - they are for KIND=registry or KIND=uncited only".to_owned()));
    }
    let mut stub = ask.stub.clone();
    if entry && stub.is_none() {
        let marker = if ask.tags.is_empty() {
            TAGS_PLACEHOLDER.to_owned()
        } else {
            tags_marker(ask.tags, root)?
        };
        stub = Some(registry_stub(key, ask.url, &marker));
    }
    if strip(key).is_empty() {
        return Err(Refused::Refusal(
            "KEY is required - the glossary term, the registry key, or the question's heading id"
                .to_owned(),
        ));
    }
    let mirror = ask.mirror.map_or_else(
        || l7r_gate_core::record::repo::mirror_of(root),
        Path::to_path_buf,
    );
    let existing: Vec<PathBuf> = kinds(kind)
        .iter()
        .flat_map(|k| holding(&root.join(dir_of(k)), k, key))
        .collect();
    if let Some(first) = existing.first() {
        let shown = first
            .strip_prefix(root)
            .unwrap_or(first)
            .to_string_lossy()
            .into_owned();
        return Err(Refused::Refusal(format!(
            "{shown} already holds {} - edit it rather than reserving another",
            repr(key)
        )));
    }
    let lock = mirror.join(".specify").join("prefixes.lock");
    let held = l7r_guard::shared::tool::flock_within(&lock, ask.timeout).map_err(os_error)?;
    let Some(held) = held else {
        let at = lock.display();
        return Err(Refused::Refusal(format!(
            "could not take the prefix lock within {}s: {at} is held (fuser {at})",
            fmt_g(ask.timeout)
        )));
    };
    let elsewhere = held_elsewhere(kind, key, root, &mirror)?;
    if !elsewhere.is_empty() {
        return Err(Refused::Refusal(format!("{} is already being defined in {elsewhere} - one home per {kind} key; pull that work in and edit it there", repr(key))));
    }
    check_key_cap(kind, key, &mirror, ask)?;
    let step = if kind == "question" { 1 } else { 10 };
    let prefix = (highest(kind, root, &mirror)?.div_euclid(step) + 1) * step;
    let d = root.join(dir_of(kind));
    let path = d.join(format!("{prefix:04}-{}", name_for(kind, key)));
    let stub = stub.unwrap_or_else(|| match kind {
        "question" => question_stub(key),
        _ => {
            dumps(
                &json!({"term": key, "def": "", "variants": [key]}),
                Some(1),
                false,
            ) + "\n"
        }
    });
    std::fs::create_dir_all(&d).map_err(os_error)?;
    std::fs::write(&path, stub).map_err(os_error)?;
    let row = json!({"kind": kind, "key": key, "prefix": prefix, "clone": root.to_string_lossy(), "session": (ask.var)("L7R_PAGE_SESSION"), "utc": consulted::now()});
    std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(mirror.join(".specify").join(LEDGER))
        .and_then(|mut f| f.write_all((dumps(&row, None, false) + "\n").as_bytes()))
        .map_err(os_error)?;
    drop(held);
    if !ask.url.is_empty() && kind == "registry" {
        let ctx = consulted::context(root).map_err(from_fault)?;
        let line = consulted::line(&ctx, ask.url, &format!("cited:{key}"), &[]);
        let record_dir = l7r_gate_core::record::repo::tree_of(root).join("research");
        consulted::append(&consulted::home(root), &[line], &record_dir).map_err(from_fault)?;
    }
    Ok(path)
}

/// `reserved`: whether the ledger holds this prefix for this kind - and, given a key, for this key.
///
/// # Errors
/// A ledger row Python could not read.
pub fn reserved(
    kind: &str,
    prefix: i64,
    mirror: &Path,
    key: Option<&str>,
) -> Result<bool, Refused> {
    if !mirror.join(".specify").join(LEDGER).is_file() {
        return Ok(false);
    }
    for row in ledger_rows(mirror)? {
        if row.get("kind").and_then(Value::as_str) == Some(kind)
            && prefix_of(&row, -1)? == prefix
            && key.is_none_or(|k| row.get("key").and_then(Value::as_str) == Some(k))
        {
            return Ok(true);
        }
    }
    Ok(false)
}

/// A record tool still Python (`archive.py` until S3a, `archive_ops.py` until S3b) run by path from the gate's tree in `root`, its
/// stdout and stderr both to the caller's stderr as the Python routed them; its exit, 1 where it could not start.
pub fn python_tool(root: &Path, tool: &str, args: &[&str], err: &mut String) -> i32 {
    let at = l7r_gate_core::record::repo::tree_of(root)
        .join("scripts/record")
        .join(tool);
    match std::process::Command::new("python3")
        .arg(&at)
        .args(args)
        .current_dir(root)
        .output()
    {
        Ok(o) => {
            err.push_str(&String::from_utf8_lossy(&o.stdout));
            err.push_str(&String::from_utf8_lossy(&o.stderr));
            o.status.code().unwrap_or(1)
        }
        Err(e) => {
            let _ = writeln!(err, "{e}");
            1
        }
    }
}

/// `archive_at_cite`: a source cited from now on archived as it is cited (feature 309 FR-006) - `archive.py url` on the new entry's
/// URL, its report on stderr, its failure never blocking the reservation.
pub fn archive_at_cite(root: &Path, url: &str, key: &str, err: &mut String) -> i32 {
    let code = python_tool(root, "archive.py", &["url", url, "--key", key], err);
    if code != 0 {
        let _ = writeln!(err, "reserve: archiving {url} failed (exit {code}) - `make archive URL='{url}' KEY={key}` retries it");
    }
    code
}

/// `int(re.match(r"(\d+)-", name).group(1))` of a path's name.
#[must_use]
pub fn prefix_of_name(name: &str) -> Option<i64> {
    NUMBERED
        .captures(name)
        .ok()
        .flatten()
        .map(|c| i64::try_from(int_of(&c[1])).unwrap_or(i64::MAX))
}

/// `l7r-gate record reserve <kind> <key> [--root R] [--mirror M] [--url U] [--tags T] [--check PATH]` (`make reserve`): the new file's
/// path on stdout; with `--check`, exit 0 where the path's prefix is reserved in the ledger and 1 where it is not.
#[must_use]
pub fn cli(args: &[String], cwd: &Path) -> crate::Reply {
    use crate::record::args::{parse_with, Spec};
    let reply = |stdout: String, stderr: String, code: i32| crate::Reply {
        stdout,
        stderr,
        code,
    };
    let specs = [
        Spec::value("--root"),
        Spec::value("--mirror"),
        Spec::value("--url"),
        Spec::value("--tags"),
        Spec::value("--check"),
    ];
    let p = match parse_with(args, &specs, 2) {
        Ok(p) if p.positional.len() == 2 => p,
        Ok(_) => {
            return reply(
                String::new(),
                "reserve-prefix.py: error: the following arguments are required: kind, key
"
                .to_owned(),
                2,
            )
        }
        Err(e) => {
            return reply(
                String::new(),
                format!(
                    "reserve-prefix.py: error: {e}
"
                ),
                2,
            )
        }
    };
    let (kind, key) = (p.positional[0].as_str(), p.positional[1].as_str());
    if !DIRS.iter().any(|(k, _)| *k == kind) {
        return reply(
            String::new(),
            format!(
                "reserve-prefix.py: error: argument kind: invalid choice: {}
",
                repr(kind)
            ),
            2,
        );
    }
    let root = match p.text("--root", "") {
        "" => consulted::repo_root(Some(cwd)),
        r => resolve(&cwd.join(r)),
    };
    let mirror = match p.text("--mirror", "") {
        "" => l7r_gate_core::record::repo::mirror_of(&root),
        m => resolve(&cwd.join(m)),
    };
    let check = p.text("--check", "");
    if !check.is_empty() {
        let name = Path::new(check)
            .file_name()
            .map(|n| n.to_string_lossy().into_owned())
            .unwrap_or_default();
        let held = prefix_of_name(&name)
            .map(|n| reserved(kind, n, &mirror, Some(key).filter(|k| !k.is_empty())));
        return match held {
            Some(Err(Refused::Raised(k, m))) => reply(String::new(), format!("{k}: {m}\n"), 1),
            Some(Ok(true)) => reply(String::new(), String::new(), 0),
            _ => reply(String::new(), String::new(), 1),
        };
    }
    let (url, tags) = (p.text("--url", ""), p.text("--tags", ""));
    let command = std::env::args().collect::<Vec<_>>().join(" ");
    let ask = Ask {
        kind,
        key,
        root: &root,
        mirror: Some(&mirror),
        stub: None,
        timeout: 30.0,
        url,
        tags,
        command,
        var: &consulted::var,
    };
    match reserve(&ask) {
        Ok(path) => {
            let mut err = String::new();
            if !url.is_empty() && kind == "registry" {
                archive_at_cite(&root, url, key, &mut err);
            }
            reply(format!("{}\n", path.display()), err, 0)
        }
        Err(Refused::Refusal(why)) => reply(String::new(), format!("reserve: {why}\n"), 2),
        Err(Refused::Raised(kind, why)) => reply(String::new(), format!("{kind}: {why}\n"), 1),
    }
}

#[cfg(test)]
mod tests;
