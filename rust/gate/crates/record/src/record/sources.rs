//! The sources-consulted ledger's and the attempts log's commands (`scripts/record/sources.py`'s and `attempts.py`'s `main`, features
//! 288 and 312; ported by feature 449 T145, phase 4's S2 under `ask:449-phase4-slices`): `l7r-gate record sources outcome | lookup |
//! mark-filled | import` (`make source-outcome`, `sources-consulted`, `record`'s fill pass, `sources-import`) and `l7r-gate record
//! attempts show | add | seed | seen` (`make attempts`). The ledger and the log are the guard's `shared::consulted` and
//! `shared::attempts`, the page cache the `research` crate's `pages`; the registry's pointer is `bundle`'s `url_of`. A page read that is
//! cited is archived by the archive crate's `urls`, in process since feature 449 T147 (where `archive_ops.py urls` ran by path).

use std::collections::{BTreeMap, HashSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pages::{cached, put, Stored};
use l7r_guard::shared::attempts::{self, Ask, More};
use l7r_guard::shared::blocked::Fault;
use l7r_guard::shared::consulted::{self, norm};
use l7r_guard::shared::html_text::unescape;
use l7r_guard::shared::py_text::repr;
use l7r_guard::shared::pyjson::{dumps, loads, py_str, truthy};
use serde_json::{json, Map, Value};

use crate::record::args::{parse_with, Spec};
use crate::record::bundle::check::url_of;
use crate::Reply;

pub const REGISTRY: &str = "research/sources/010-works-cited";
pub const SEED: &str = "reread-2026-09-29";
const PER_URL: &str = "/diagram/.clones/.tools/logs/reread-2026-09-29/per_url.json";
const SCRATCH: &str = "/tmp/l7r-check";

static ENTRY: LazyLock<Regex> =
    LazyLock::new(|| l7r_gate_research::pyre::py(r"^\d+-([\s\S]+)\.html\z"));

fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}

fn raised(said: String, f: &Fault) -> Reply {
    reply(said, format!("{}: {}\n", f.kind, f.message), 1)
}

fn fault(kind: &'static str, e: &str) -> Fault {
    Fault::new(kind, e.to_owned())
}

#[expect(
    clippy::needless_pass_by_value,
    reason = "a `map_err` adapter, named so each call stays one line"
)]
fn os_error(e: std::io::Error) -> Fault {
    fault("OSError", &e.to_string())
}

#[expect(
    clippy::needless_pass_by_value,
    reason = "a `map_err` adapter, named so each call stays one line"
)]
fn utf8_error(e: std::string::FromUtf8Error) -> Fault {
    fault("UnicodeDecodeError", &e.to_string())
}

/// A refusal raised before anything was printed.
fn early(f: Fault) -> (String, Fault) {
    (String::new(), f)
}

/// The record's blocked lists, the gate's own tree's.
fn record_dir(root: &Path) -> PathBuf {
    crate::record::repo::tree_of(root).join("research")
}

fn read_utf8(path: &Path) -> Result<String, Fault> {
    let raw = std::fs::read(path).map_err(os_error)?;
    let text = String::from_utf8(raw).map_err(utf8_error)?;
    Ok(text.replace("\r\n", "\n").replace('\r', "\n"))
}

/// The registry's entries, `sorted(glob("[0-9]*-*.html"))`: (key, text).
fn entries(root: &Path) -> Result<Vec<(Option<String>, String)>, Fault> {
    let mut found: Vec<PathBuf> = std::fs::read_dir(root.join(REGISTRY))
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter(|p| {
            // `glob("[0-9]*-*.html")`: a digit, then a hyphen somewhere before the `.html` that ends it
            let n = p
                .file_name()
                .map(|n| n.to_string_lossy().into_owned())
                .unwrap_or_default();
            n.starts_with(|c: char| c.is_ascii_digit())
                && l7r_gate_research::has_ext(&n, "html")
                && n.get(1..n.len().saturating_sub(5))
                    .is_some_and(|mid| mid.contains('-'))
        })
        .collect();
    found.sort();
    let mut out = Vec::new();
    for f in found {
        let name = f
            .file_name()
            .map(|n| n.to_string_lossy().into_owned())
            .unwrap_or_default();
        let key = ENTRY
            .captures(&name)
            .ok()
            .flatten()
            .map(|c| c[1].to_owned());
        out.push((key, read_utf8(&f)?));
    }
    Ok(out)
}

/// `registry`: each entry's key to the pointer it names.
///
/// # Errors
/// An entry that cannot be read.
pub fn registry(root: &Path) -> Result<Vec<(String, String)>, Fault> {
    Ok(entries(root)?
        .into_iter()
        .filter_map(|(key, text)| {
            let url = url_of(&text);
            key.filter(|_| !url.is_empty()).map(|k| (k, url))
        })
        .collect())
}

/// `registry_urls`: normalized URL to the key of the entry that cites it - its own pointer first, then any other URL in it.
fn registry_urls(root: &Path) -> Result<BTreeMap<String, String>, Fault> {
    let (mut primary, mut other) = (BTreeMap::new(), BTreeMap::new());
    for (key, text) in entries(root)? {
        let Some(key) = key else {
            continue;
        };
        let own = url_of(&text);
        if !own.is_empty() {
            primary.entry(norm(&own)).or_insert_with(|| key.clone());
        }
        for u in consulted::URL
            .find_iter(&text)
            .map_while(std::result::Result::ok)
        {
            other
                .entry(norm(&unescape(u.as_str())))
                .or_insert_with(|| key.clone());
        }
    }
    other.extend(primary);
    Ok(other)
}

/// `mark_filled`: a `cited:<key>` line for every filled registry entry whose URL the ledger does not already mark so.
///
/// # Errors
/// The ledger, the context, a blocked URL or the write.
pub fn mark_filled(root: &Path, home: &Path) -> Result<Vec<Value>, Fault> {
    let mut have = HashSet::new();
    for r in consulted::read(home)? {
        let pair = (
            consulted::get(&r, "url")?.cloned(),
            consulted::get(&r, "outcome")?.cloned(),
        );
        have.insert(dumps(&json!([pair.0, pair.1]), None, false));
    }
    let ctx = consulted::context(root)?;
    let rows: Vec<Value> = registry(root)?
        .into_iter()
        .filter(|(key, url)| {
            !have.contains(&dumps(
                &json!([norm(url), format!("cited:{key}")]),
                None,
                false,
            ))
        })
        .map(|(key, url)| consulted::line(&ctx, &url, &format!("cited:{key}"), &[]))
        .collect();
    consulted::append(home, &rows, &record_dir(root))?;
    Ok(rows)
}

/// The browser and the working copy a cited read is archived with: the archive's own (production) wiring, which a test of this crate
/// never starts - its launcher is the real tree's when `l7r-gate.sh` runs the tests - so a test meets a browser that will not start.
#[cfg(not(test))]
fn reads_browser(
    root: &Path,
) -> l7r_gate_archive::Result<Box<dyn l7r_gate_archive::fetch::Client>> {
    l7r_gate_archive::cli::start_browser(root)
}

#[cfg(test)]
fn reads_browser(_: &Path) -> l7r_gate_archive::Result<Box<dyn l7r_gate_archive::fetch::Client>> {
    Err(l7r_gate_archive::Error::new(
        "Error",
        "BrowserType.launch: no browser in a test",
    ))
}

#[cfg(not(test))]
fn reads_store(root: &Path) -> l7r_gate_archive::store::Archive {
    l7r_gate_archive::cli::production_store(root)
}

#[cfg(test)]
fn reads_store(root: &Path) -> l7r_gate_archive::store::Archive {
    l7r_gate_archive::store::Archive::new(&consulted::home(root), None)
}

/// `archive_reads`: each cited URL with no archive row yet captured by the archive's `urls` (`archive_ops.py urls`, in process since
/// feature 449 T147 where it ran the Python by path), its report on stderr; a failure never blocks the read. `L7R_ARCHIVE_READS=0`
/// switches it off.
fn archive_reads(root: &Path, urls: &[&str], err: &mut String, var: &dyn Fn(&str) -> String) {
    if urls.is_empty() || var("L7R_ARCHIVE_READS") == "0" {
        return;
    }
    let urls: Vec<String> = urls.iter().map(|u| (*u).to_owned()).collect();
    if let Err(e) =
        l7r_gate_archive::ops::archive_urls(root, &urls, &reads_browser, &reads_store, err)
    {
        // the exception's one line where the Python's traceback ended (`ask:449-usage-text`), and the exit it gave
        let _ = writeln!(err, "{e}");
        let _ = writeln!(err, "archive: archiving the pages read failed (exit 1) - `make archive URL=<u>` retries one");
    }
}

fn outcome(args: &[String], root: &Path, home: &Path) -> Reply {
    let p =
        match parse_with(
            args,
            &[Spec::value("--question"), Spec::value("--sought")],
            2,
        ) {
            Ok(p) if p.positional.len() == 2 => p,
            Ok(_) => return reply(
                String::new(),
                "sources.py outcome: error: the following arguments are required: url, outcome\n"
                    .to_owned(),
                2,
            ),
            Err(e) => {
                return reply(
                    String::new(),
                    format!("sources.py outcome: error: {e}\n"),
                    2,
                )
            }
        };
    let (url, said) = (&p.positional[0], &p.positional[1]);
    if !consulted::valid_outcome(said) {
        return reply(
            String::new(),
            format!(
                "source-outcome: OUTCOME={} is not one of: {}\n",
                repr(said),
                consulted::OUTCOMES
            ),
            2,
        );
    }
    let (question, sought) = (p.text("--question", ""), p.text("--sought", ""));
    let said = l7r_guard::shared::py_text::strip(said);
    let run = || -> Result<(String, String), (String, Fault)> {
        let ctx = consulted::context(root).map_err(early)?;
        let questions: Vec<String> = if question.is_empty() {
            Vec::new()
        } else {
            vec![question.to_owned()]
        };
        let row = consulted::line(&ctx, url, said, &questions);
        consulted::append(home, std::slice::from_ref(&row), &record_dir(root)).map_err(early)?;
        let out = format!(
            "source-outcome: recorded{}\n",
            consulted::show(&row).map_err(early)?
        );
        if let Err(f) = attempts::outcome(root, url, question, said, sought, &record_dir(root)) {
            return Err((out, f));
        }
        let mut err = String::new();
        if said.starts_with("cited:") {
            archive_reads(root, &[url], &mut err, &consulted::var);
        }
        Ok((out, err))
    };
    match run() {
        Ok((out, err)) => reply(out, err, 0),
        Err((out, f)) => raised(out, &f),
    }
}

fn entries_word(n: usize) -> &'static str {
    if n == 1 {
        "y"
    } else {
        "ies"
    }
}

fn lookup(args: &[String], root: &Path, home: &Path) -> Reply {
    let p = match parse_with(args, &[Spec::value("--url"), Spec::value("--key")], 0) {
        Ok(p) => p,
        Err(e) => return reply(String::new(), format!("sources.py lookup: error: {e}\n"), 2),
    };
    let (url, key) = (p.text("--url", ""), p.text("--key", ""));
    if url.is_empty() && key.is_empty() {
        return reply(
            String::new(),
            "sources-consulted: URL=<u> or KEY=<regex> is required\n".to_owned(),
            2,
        );
    }
    let run = || -> Result<String, Fault> {
        let filled = mark_filled(root, home)?;
        let rows = if url.is_empty() {
            consulted::by_key(home, key)?
        } else {
            consulted::earlier(home, url)?
        };
        let what = if url.is_empty() {
            format!("keys matching {}", repr(key))
        } else {
            norm(url)
        };
        let note = if filled.is_empty() {
            String::new()
        } else {
            format!(
                " ({} newly filled registry entr{} marked cited first)",
                filled.len(),
                entries_word(filled.len())
            )
        };
        let mut out = format!(
            "sources-consulted: {} line(s) for {what}{note}\n",
            rows.len()
        );
        for r in &rows {
            if !key.is_empty() {
                let u = consulted::get(r, "url")?.ok_or_else(|| fault("KeyError", "'url'"))?;
                let _ = write!(out, "  {}\n  ", py_str(u));
            }
            out.push_str(&(consulted::show(r)? + "\n"));
        }
        Ok(out)
    };
    match run() {
        Ok(out) => reply(out, String::new(), 0),
        Err(f) => raised(String::new(), &f),
    }
}

/// `seed`: one ledger line per URL, feature and session of the 2026-09-29 measurement's reads; none once the ledger holds the seed.
fn seed(per_url: &Path, root: &Path, home: &Path) -> Result<usize, Fault> {
    for r in consulted::read(home)? {
        if consulted::get(&r, "seed")?.and_then(Value::as_str) == Some(SEED) {
            return Ok(0);
        }
    }
    let cited = registry_urls(root)?;
    let data = loads(&read_utf8(per_url)?).map_err(|e| fault("JSONDecodeError", &e.to_string()))?;
    let Value::Object(data) = data else {
        return Err(fault("AttributeError", "object has no attribute 'items'"));
    };
    let mut rows = Vec::new();
    for (url, events) in data {
        let mut events: Vec<Value> = match events {
            Value::Array(list) => list,
            Value::String(s) if s.is_empty() => Vec::new(),
            Value::Object(m) if m.is_empty() => Vec::new(),
            _ => return Err(fault("AttributeError", "an event that is not a mapping")),
        };
        events.sort_by_key(|e| e.get("ts").map(py_str).unwrap_or_default());
        let mut groups: Vec<((String, String), Vec<Value>)> = Vec::new();
        for e in events {
            let feature = e
                .get("feature")
                .filter(|v| truthy(v))
                .map(py_str)
                .unwrap_or_default();
            let session = e.get("session").map(py_str).unwrap_or_default();
            match groups
                .iter_mut()
                .find(|(k, _)| *k == (feature.clone(), session.clone()))
            {
                Some((_, evs)) => evs.push(e),
                None => groups.push(((feature, session), vec![e])),
            }
        }
        for ((feature, session), evs) in groups {
            let mut whys: Vec<String> = Vec::new();
            for e in evs.iter().filter(|e| e.get("why").is_some_and(truthy)) {
                let w: String = l7r_guard::shared::py_text::collapse(&py_str(&e["why"]))
                    .chars()
                    .take(200)
                    .collect();
                if !whys.contains(&w) {
                    whys.push(w);
                }
            }
            whys.truncate(3);
            let ts: String = evs[0]
                .get("ts")
                .map(py_str)
                .unwrap_or_default()
                .chars()
                .take(19)
                .collect();
            let outcome = cited
                .get(&url)
                .map_or_else(|| "unknown-outcome".to_owned(), |k| format!("cited:{k}"));
            rows.push(json!({"url": url, "raw": url, "utc": format!("{ts}+00:00"), "feature": feature, "clone": "", "session": session,
                             "questions": whys, "outcome": outcome, "reads": evs.len(), "seed": SEED}));
        }
    }
    consulted::append(home, &rows, &record_dir(root))?;
    Ok(rows.len())
}

/// Every file named `MANIFEST.txt` under `dir`, sorted.
fn manifests(dir: &Path, out: &mut Vec<PathBuf>) {
    for e in std::fs::read_dir(dir).into_iter().flatten().flatten() {
        let p = e.path();
        if p.is_dir() {
            manifests(&p, out);
        } else if p.file_name().is_some_and(|n| n == "MANIFEST.txt") {
            out.push(p);
        }
    }
}

fn mtime(p: &Path) -> f64 {
    std::fs::metadata(p)
        .and_then(|m| m.modified())
        .ok()
        .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
        .map_or(0.0, |d| d.as_secs_f64())
}

/// One manifest row's saved files, or why it is skipped (an excerpt, or a part missing).
fn saved_files(dir: &Path, file: &str) -> Result<Vec<PathBuf>, &'static str> {
    let first = file.split(' ').next().unwrap_or("");
    let stem = first.strip_suffix(".txt").unwrap_or(first);
    let stem = stem.strip_suffix(".p1").unwrap_or(stem);
    let mut parts: Vec<(u64, PathBuf)> = std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .filter_map(|e| {
            let n = e.file_name().to_string_lossy().into_owned();
            let k = n
                .strip_prefix(&format!("{stem}.p"))?
                .strip_suffix(".txt")?
                .parse()
                .ok()?;
            Some((k, e.path()))
        })
        .collect();
    parts.sort();
    let files: Vec<PathBuf> = if parts.is_empty() {
        vec![dir.join(format!("{stem}.txt"))]
    } else {
        parts.into_iter().map(|p| p.1).collect()
    };
    if !files.iter().all(|f| f.is_file()) {
        return Err("missing");
    }
    let head = String::from_utf8_lossy(&std::fs::read(&files[0]).unwrap_or_default()).into_owned();
    if head.starts_with("[EXCERPT") {
        return Err("excerpts");
    }
    Ok(files)
}

/// `import_saves`: each distinct page saved under `scratch` into the cache once, the newest whole save of each normalized URL.
fn import_saves(
    scratch: &Path,
    home: &Path,
    record_dir: &Path,
) -> Result<Map<String, Value>, Fault> {
    let mut found = Vec::new();
    manifests(scratch, &mut found);
    found.sort();
    let mut counts: BTreeMap<&str, usize> = [
        ("manifests", 0),
        ("rows", 0),
        ("excerpts", 0),
        ("missing", 0),
    ]
    .into();
    let mut best: BTreeMap<String, (f64, String, PathBuf, Vec<PathBuf>)> = BTreeMap::new();
    for manifest in found {
        *counts.entry("manifests").or_default() += 1;
        let text = String::from_utf8_lossy(&std::fs::read(&manifest).unwrap_or_default())
            .replace("\r\n", "\n");
        let dir = manifest.parent().unwrap_or(scratch).to_path_buf();
        for row in l7r_guard::shared::checks::reply::py_lines(&text)
            .into_iter()
            .skip(1)
        {
            let mut cells = row.splitn(3, " | ");
            let (pointer, file, state) = (
                cells.next().unwrap_or(""),
                cells.next().unwrap_or(""),
                cells.next().unwrap_or(""),
            );
            if !state.starts_with("FETCHED")
                || file.is_empty()
                || file == "-"
                || !pointer.starts_with("http")
            {
                continue;
            }
            *counts.entry("rows").or_default() += 1;
            if state.contains("excerpt") {
                *counts.entry("excerpts").or_default() += 1;
                continue;
            }
            let files = match saved_files(&dir, file) {
                Ok(f) => f,
                Err(why) => {
                    *counts.entry(why).or_default() += 1;
                    continue;
                }
            };
            let newest = files.iter().map(|f| mtime(f)).fold(f64::MIN, f64::max);
            let key = norm(pointer);
            if best.get(&key).is_none_or(|b| newest > b.0) {
                best.insert(key, (newest, pointer.to_owned(), dir.clone(), files));
            }
        }
    }
    let (mut imported, mut kept) = (0, 0);
    for (newest, pointer, dir, files) in best.values() {
        if cached(home, pointer, 10_000.0, false)
            .map_err(|e| Fault::new("ValueError", e.message))?
            .is_some()
        {
            kept += 1;
            continue;
        }
        let text: String = files
            .iter()
            .map(|f| {
                String::from_utf8_lossy(&std::fs::read(f).unwrap_or_default())
                    .replace("\r\n", "\n")
                    .replace('\r', "\n")
            })
            .collect();
        #[expect(
            clippy::cast_possible_truncation,
            clippy::cast_sign_loss,
            reason = "a file's modified time in whole seconds"
        )]
        let (y, mo, d, h, mi, s) = l7r_guard::shared::log::civil(*newest as u64);
        let fetched = format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{s:02}+00:00");
        let origin = format!("import:{}", dir.display());
        let how = Stored {
            fetched: Some(&fetched),
            exact: false,
            origin: &origin,
        };
        put(home, pointer, &text, &how, record_dir).map_err(|e| Fault::new(e.kind, e.message))?;
        imported += 1;
    }
    let mut out = Map::new();
    for (k, v) in counts {
        out.insert(k.to_owned(), json!(v));
    }
    let mut ordered = Map::new();
    for k in ["manifests", "rows", "excerpts", "missing"] {
        ordered.insert(k.to_owned(), out[k].clone());
    }
    ordered.insert("distinct".into(), json!(best.len()));
    ordered.insert("imported".into(), json!(imported));
    ordered.insert("already".into(), json!(kept));
    Ok(ordered)
}

fn import(args: &[String], root: &Path, home: &Path) -> Reply {
    let p = match parse_with(
        args,
        &[Spec::value("--per-url"), Spec::value("--scratch")],
        0,
    ) {
        Ok(p) => p,
        Err(e) => return reply(String::new(), format!("sources.py import: error: {e}\n"), 2),
    };
    let (per_url, scratch) = (
        PathBuf::from(p.text("--per-url", PER_URL)),
        PathBuf::from(p.text("--scratch", SCRATCH)),
    );
    let seeded = if per_url.is_file() {
        match seed(&per_url, root, home) {
            Ok(n) => n,
            Err(f) => return raised(String::new(), &f),
        }
    } else {
        0
    };
    let got = if scratch.is_dir() {
        match import_saves(&scratch, home, &record_dir(root)) {
            Ok(g) => g,
            Err(f) => return raised(String::new(), &f),
        }
    } else {
        Map::new()
    };
    let out = format!(
        "sources-import: seeded {seeded} ledger line(s) from {} (0: already seeded, or no file)\nsources-import: page cache {}\n",
        per_url.display(),
        dumps(&Value::Object(got), None, true)
    );
    reply(out, String::new(), 0)
}

/// `l7r-gate record sources <outcome|lookup|mark-filled|import>`.
#[must_use]
pub fn cli(args: &[String], cwd: &Path) -> Reply {
    let root = consulted::repo_root(Some(cwd));
    let home = consulted::home(&root);
    let rest = args.get(1..).unwrap_or(&[]);
    match args.first().map(String::as_str) {
        Some("outcome") => outcome(rest, &root, &home),
        Some("lookup") => lookup(rest, &root, &home),
        Some("mark-filled") => match mark_filled(&root, &home) {
            Ok(rows) => reply(
                format!(
                    "sources-consulted: {} filled registry entr{} marked cited\n",
                    rows.len(),
                    entries_word(rows.len())
                ),
                String::new(),
                0,
            ),
            Err(f) => raised(String::new(), &f),
        },
        Some("import") => import(rest, &root, &home),
        _ => reply(
            String::new(),
            "sources.py: error: argument cmd: invalid choice\n".to_owned(),
            2,
        ),
    }
}

/// `l7r-gate record attempts <show|add|seed|seen>`.
#[must_use]
#[expect(
    clippy::too_many_lines,
    reason = "attempts.py's argparse: four subcommands' flags and refusals, read in its order"
)]
pub fn attempts_cli(args: &[String], cwd: &Path) -> Reply {
    let rest = args.get(1..).unwrap_or(&[]);
    let usage = |e: &str| reply(String::new(), format!("attempts.py: error: {e}\n"), 2);
    match args.first().map(String::as_str) {
        Some("seen") => {
            let specs = [
                Spec::value("--root"),
                Spec::value("--sought"),
                Spec::value("--route"),
                Spec::flag("--record"),
            ];
            // after `--` every argument is a URL, as argparse reads it
            let cut = rest.iter().position(|a| a == "--").unwrap_or(rest.len());
            let mut p = match parse_with(&rest[..cut], &specs, usize::MAX) {
                Ok(p) => p,
                Err(e) => return usage(&e),
            };
            p.positional.extend(rest.iter().skip(cut + 1).cloned());
            if p.positional.is_empty()
                || !p.has("--root")
                || !p.has("--sought")
                || !p.has("--route")
            {
                return usage(
                    "the following arguments are required: --root, --sought, --route, urls",
                );
            }
            let root = cwd.join(p.text("--root", ""));
            let urls = p.positional.clone();
            match attempts::seen(
                &root,
                &urls,
                p.text("--sought", ""),
                p.text("--route", ""),
                p.on("--record"),
                &record_dir(&root),
            ) {
                Ok(got) => reply(dumps(&json!(got), None, false) + "\n", String::new(), 0),
                Err(f) => raised(String::new(), &f),
            }
        }
        Some("show") => {
            let p = match parse_with(
                rest,
                &[
                    Spec::value("--url"),
                    Spec::value("--key"),
                    Spec::value("--q"),
                ],
                0,
            ) {
                Ok(p) => p,
                Err(e) => return usage(&e),
            };
            let given: Vec<&str> = ["--url", "--key", "--q"]
                .into_iter()
                .filter(|f| p.has(f))
                .collect();
            if given.len() != 1 {
                return usage("one of the arguments --url --key --q is required");
            }
            let root = consulted::repo_root(Some(cwd));
            let ask = match (p.text("--url", ""), p.text("--key", ""), p.text("--q", "")) {
                (u, _, _) if !u.is_empty() => Ask::Url(u),
                (_, k, _) if !k.is_empty() => Ask::Key(k),
                (_, _, q) => Ask::Question(q),
            };
            match attempts::report(&root, ask) {
                Ok(lines) => reply(lines.join("\n") + "\n", String::new(), 0),
                Err(f) => raised(String::new(), &f),
            }
        }
        Some("add") => {
            let specs = [
                Spec::value("--url"),
                Spec::value("--q"),
                Spec::value("--sought"),
                Spec::value("--outcome"),
                Spec::value("--route"),
                // the door's `--root` and `--print` (T145, for `attempts.add`'s forwarder) left with its last importer, `uncited.py` (T147)
                Spec::value("--key"),
            ];
            let p = match parse_with(rest, &specs, 0) {
                Ok(p) => p,
                Err(e) => return usage(&e),
            };
            if !p.has("--url") || !p.has("--sought") {
                return usage("the following arguments are required: --url, --sought");
            }
            let outcome = p.text("--outcome", "unknown");
            if !attempts::OUTCOMES.contains(&outcome) {
                return usage(&format!(
                    "argument --outcome: invalid choice: {}",
                    repr(outcome)
                ));
            }
            let root = consulted::repo_root(Some(cwd));
            let more = More {
                key: p.text("--key", ""),
                route: p.text("--route", ""),
                ..More::default()
            };
            match attempts::add(
                &root,
                p.text("--url", ""),
                p.text("--q", "unknown"),
                p.text("--sought", ""),
                outcome,
                &more,
                &record_dir(&root),
            ) {
                Ok(_) => reply(String::new(), String::new(), 0),
                Err(f) => raised(String::new(), &f),
            }
        }
        Some("seed") => {
            let root = consulted::repo_root(Some(cwd));
            match attempts::seed(&root, &consulted::home(&root), &record_dir(&root)) {
                Ok((out, err, _)) => reply(out, err, 0),
                Err(f) => raised(String::new(), &f),
            }
        }
        _ => usage("argument cmd: invalid choice"),
    }
}

#[cfg(test)]
mod tests;
