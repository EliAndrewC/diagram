//! The green-gate stamps (feature 449 T063 slice 2, from `scripts/gates/gate-stamp.py`): each area's key is a hash of what its gate ran over, kept under the git directory when the gate goes green, and the
//! push refuses an area whose code changed with no matching stamp. The keys equal the Python's byte for byte, so a stamp kept before the switch still verifies.

use std::io::{Read, Write as _};
use std::path::{Path, PathBuf};
use std::process::Command;

use l7r_guard::shared::log::civil;
use l7r_guard::shared::sha256;

use crate::codeid::{self, stated, Cache};

/// A record taken under an older gate standard cannot satisfy a newer one: bump this when what the gate DEMANDS changes, never for a change in the code it runs over.
const GATE_RECIPE: &str = "2026-08-31/174-whole-tree-100-no-ratchet";

struct Area {
    name: &'static str,
    root: &'static str,
    patterns: &'static [&'static str],
    /// hashed by bytes: the one place a docstring counts as a change
    raw: bool,
    /// a skip key for a gate, never a push obligation
    skip_only: bool,
}

const AREAS: [Area; 4] = [
    Area {
        name: "browser",
        root: "",
        patterns: &[
            "l7r/diagram/interactive/*.py",
            "l7r/diagram/interactive/assets/*",
            "tests/full/interactive/page_browser/*.py",
            "research/*.html",
        ],
        raw: true,
        skip_only: true,
    },
    Area {
        name: "diagram",
        root: "",
        patterns: &["*.py", "rust/*.rs", "rust/*Cargo.toml", "rust/*Cargo.lock"],
        raw: false,
        skip_only: false,
    },
    Area {
        name: "hooks",
        root: "",
        patterns: &[
            "scripts/*.sh",
            "scripts/*.py",
            "scripts/*.txt",
            "tests/hooks/*.sh",
            "tests/hooks/*.py",
        ],
        raw: false,
        skip_only: false,
    },
    Area {
        name: "page",
        root: "l7r/diagram/interactive",
        patterns: &["assets/*", "classes/*.py"],
        raw: true,
        skip_only: false,
    },
];

/// What `diagram` excludes as declared: a subtree the coverage floor measures is hashed all the same (feature 178).
const DIAGRAM_EXCLUDED: [&str; 8] = [
    "tests/",
    "l7r/diagram/ci/",
    "scripts/",
    "specs/",
    ".claude/",
    ".specify/",
    ".clones/",
    "docs/",
];

fn prefix(area_root: &str) -> String {
    if area_root.is_empty() {
        String::new()
    } else {
        format!("{area_root}/")
    }
}

/// The repository's top level, the root every key is taken from; its absolute text is in the key, as it always was.
#[must_use]
pub fn toplevel() -> Option<PathBuf> {
    let out = git(Path::new("."), &["rev-parse", "--show-toplevel"]).ok()?;
    Some(PathBuf::from(String::from_utf8_lossy(&out).trim()))
}

/// `fnmatch` for these patterns, whose only wildcard is `*`, which crosses `/` as `git ls-files` does.
fn matches(text: &str, pattern: &str) -> bool {
    let Some((head, rest)) = pattern.split_once('*') else {
        return text == pattern;
    };
    let Some(mut left) = text.strip_prefix(head) else {
        return false;
    };
    let pieces: Vec<&str> = rest.split('*').collect();
    let (last, middle) = pieces.split_last().unwrap_or((&"", &[]));
    for piece in middle {
        let Some(at) = left.find(piece) else {
            return false;
        };
        left = &left[at + piece.len()..];
    }
    left.ends_with(last)
}

/// `[tool.coverage.run] source` as path prefixes; an unreadable config is `l7r/`, never nothing, which would restore the exclusion feature 178 closed.
fn coverage_sources(root: &Path) -> Vec<String> {
    let text = std::fs::read_to_string(root.join("pyproject.toml")).unwrap_or_default();
    let section = text.split("[tool.coverage.run]").nth(1).unwrap_or("");
    let body = section.split("\n[").next().unwrap_or("");
    let list = body
        .find("source")
        .and_then(|at| body[at..].split_once('['))
        .and_then(|(_, rest)| rest.split_once(']'))
        .map_or("", |(inner, _)| inner);
    let got: Vec<String> = list
        .split(',')
        .map(|s| s.trim().trim_matches(['"', '\'', '/']))
        .filter(|s| !s.is_empty())
        .map(|s| format!("{s}/"))
        .collect();
    if got.is_empty() {
        vec!["l7r/".to_owned()]
    } else {
        got
    }
}

fn exclusions(area: &Area, root: &Path) -> Vec<&'static str> {
    if area.name != "diagram" {
        return Vec::new();
    }
    let measured = coverage_sources(root);
    DIAGRAM_EXCLUDED
        .iter()
        .copied()
        .filter(|sub| !measured.iter().any(|m| sub.starts_with(m.as_str())))
        .collect()
}

fn git(root: &Path, args: &[&str]) -> Result<Vec<u8>, String> {
    let done = stated(
        Command::new("git").arg("-C").arg(root).args(args).output(),
        "cannot start git",
    )?;
    if done.status.success() {
        Ok(done.stdout)
    } else {
        Err(format!(
            "git {} failed: {}",
            args.join(" "),
            String::from_utf8_lossy(&done.stderr).trim()
        ))
    }
}

/// Tracked and untracked-but-not-ignored files of the area, its exclusions out, sorted as paths.
fn area_files(root: &Path, area: &Area) -> Result<Vec<PathBuf>, String> {
    let head = prefix(area.root);
    let specs: Vec<String> = area.patterns.iter().map(|p| format!("{head}{p}")).collect();
    let mut args = vec!["ls-files", "-coz", "--exclude-standard", "--"];
    args.extend(specs.iter().map(String::as_str));
    let excluded: Vec<String> = exclusions(area, root)
        .iter()
        .map(|sub| format!("{head}{sub}"))
        .collect();
    let out = git(root, &args)?;
    let text = String::from_utf8_lossy(&out).into_owned();
    let mut files: Vec<PathBuf> = text
        .split('\0')
        .filter(|l| !l.trim().is_empty() && !excluded.iter().any(|e| l.starts_with(e.as_str())))
        .map(|l| root.join(l))
        .collect();
    files.sort();
    files.dedup();
    Ok(files)
}

/// An area's non-file inputs: for `browser`, the installed Playwright and Chromium builds, since a browser upgrade is an input to a browser test.
fn salt(area: &Area, python: &str) -> String {
    if area.name != "browser" {
        return String::new();
    }
    let script = "import importlib.metadata as m,os,pathlib as p\ntry:\n    v=m.version('playwright')\nexcept m.PackageNotFoundError:\n    print('absent',end='');raise SystemExit\nc=p.Path(os.environ.get('PLAYWRIGHT_BROWSERS_PATH') or (p.Path.home()/'.cache'/'ms-playwright'))\nb=sorted(q.name for q in c.glob('chromium*')) if c.is_dir() else []\nprint(f\"playwright={v};chromium={','.join(b) or 'none'}\",end='')";
    Command::new(python)
        .args(["-c", script])
        .output()
        .map_or_else(
            |_| "absent".to_owned(),
            |o| String::from_utf8_lossy(&o.stdout).into_owned(),
        )
}

/// The content hash of `files`: each path with its semantic id, or the sha of its bytes in a raw area; a file gone is `<missing>`.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn hash_files(
    files: &[PathBuf],
    root: &Path,
    raw: bool,
    salt_text: &str,
    python: &str,
) -> Result<String, String> {
    let readable: Vec<(PathBuf, Vec<u8>)> = files
        .iter()
        .filter(|p| p.is_file())
        .filter_map(|p| Some((p.clone(), std::fs::read(p).ok()?)))
        .collect();
    let ids = if raw {
        readable.iter().map(|(_, d)| sha256::hex(d)).collect()
    } else {
        let script = codeid::script(root);
        codeid::content_ids(&readable, &mut Cache::at(root), python, &script)?
    };
    let mut by_path = readable.iter().map(|(p, _)| p).zip(ids);
    let mut data = format!("{GATE_RECIPE}\0{salt_text}\0").into_bytes();
    let mut next = by_path.next();
    for path in files {
        data.extend_from_slice(path.to_string_lossy().as_bytes());
        data.push(0);
        match next.as_ref().filter(|(p, _)| *p == path) {
            Some((_, id)) => {
                data.extend_from_slice(id.as_bytes());
                next = by_path.next();
            }
            None => data.extend_from_slice(b"<missing>"),
        }
        data.push(0);
    }
    Ok(sha256::hex(&data))
}

fn area_named(name: &str) -> Option<&'static Area> {
    AREAS.iter().find(|a| a.name == name)
}

fn area_key(root: &Path, area: &Area, python: &str) -> Result<String, String> {
    hash_files(
        &area_files(root, area)?,
        root,
        area.raw,
        &salt(area, python),
        python,
    )
}

/// An area's key by name, for the verification state.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn area_key_named(root: &Path, name: &str, python: &str) -> Result<String, String> {
    area_key(root, area_named(name).ok_or("no such area")?, python)
}

fn stamp_path(root: &Path, area: &Area) -> Option<PathBuf> {
    codeid::common_git_dir(root).map(|d| d.join(format!("gate-green-{}", area.name)))
}

fn write_stamp(root: &Path, area: &Area, python: &str) -> Result<(), String> {
    let key = area_key(root, area, python)?;
    let path = stamp_path(root, area).ok_or("no git directory to record into")?;
    stated(std::fs::write(&path, key), &path.to_string_lossy())
}

/// Refuse an area whose gated code changed since `base` with no matching stamp; the lines to print.
fn refusals(root: &Path, base: &str, python: &str) -> Result<Vec<String>, String> {
    let diff = git(root, &["diff", "--name-only", &format!("{base}...HEAD")])?;
    let text = String::from_utf8_lossy(&diff).into_owned();
    let mut bad = Vec::new();
    for area in AREAS.iter().filter(|a| !a.skip_only) {
        let head = prefix(area.root);
        let excluded: Vec<String> = exclusions(area, root)
            .iter()
            .map(|sub| format!("{head}{sub}"))
            .collect();
        let touched = text.lines().any(|c| {
            c.strip_prefix(head.as_str()).is_some_and(|rel| {
                !excluded.iter().any(|e| c.starts_with(e.as_str()))
                    && area.patterns.iter().any(|p| matches(rel, p))
            })
        });
        if !touched {
            continue;
        }
        let gate = match area.name {
            "hooks" => "make hooks-test",
            "page" => "make page-check",
            _ => "make done",
        };
        let kept = stamp_path(root, area).and_then(|p| std::fs::read_to_string(p).ok());
        let want = area_key(root, area, python)?;
        match kept {
            None => bad.push(format!("{}: no green gate has been recorded at all ({gate} stamps it)", area.name)),
            Some(have) if have.trim() != want => bad.push(format!("{}: the last green gate ran against DIFFERENT code than you are pushing ({gate} again)", area.name)),
            Some(_) => {}
        }
    }
    Ok(bad)
}

/// The name its runs are recorded under, as `usage_log.exited` recorded the Python's.
const USAGE_LOG_TOOL: &str = "gate-stamp";

/// One line in `<git common dir>/tool-usage.jsonl`, the record every refusing check leaves (feature 406); one write of one short line in append mode, and a failure never fails the tool.
pub fn record_for(root: &Path, tool: &str, outcome: &str) {
    let Some(common) = codeid::common_git_dir(root) else {
        return;
    };
    let secs = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0, |d| d.as_secs());
    let (y, mo, d, h, mi, s) = civil(secs);
    let session = std::env::var("CLAUDE_SESSION_ID").unwrap_or_default();
    let row = format!("{{\"utc\": \"{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{s:02}Z\", \"tool\": \"{tool}\", \"kind\": \"check\", \"outcome\": \"{outcome}\", \"session\": {}}}\n", serde_json::Value::from(session));
    if let Ok(mut file) = std::fs::OpenOptions::new()
        .append(true)
        .create(true)
        .open(common.join("tool-usage.jsonl"))
    {
        let _ = file.write_all(row.as_bytes());
    }
}

fn record(root: &Path, outcome: &str) {
    record_for(root, USAGE_LOG_TOOL, outcome);
}

/// Prove the hash still bites, since a checker never seen failing is not a checker; the failure, if it does not.
fn selftest(root: &Path, python: &str) -> Result<(), String> {
    let dir = std::env::temp_dir().join(format!("l7r-gate-selftest-{}", std::process::id()));
    let result = selftest_in(&dir, root, python);
    let _ = std::fs::remove_dir_all(&dir);
    result
}

/// (file, its new text or gone, what the hash must do against the last baseline, what it means if it does not).
const SELFTEST: [(&str, Option<&str>, Rule, &str); 9] = [
    ("a.py", Some("x = 1\n"), Rule::Baseline, ""),
    ("b.py", Some("y = 2\n"), Rule::Baseline, ""),
    ("a.py", Some("x = 2\n"), Rule::Moves, "a changed .py did NOT change the hash"),
    ("a.py", None, Rule::Moves, "a deleted .py did NOT change the hash"),
    ("a.py", Some("def f(x):\n    return x + 1\n"), Rule::Baseline, ""),
    ("a.py", Some("\"\"\"module doc\"\"\"\n\n# a comment\n\ndef f(x):\n    \"\"\"f doc\"\"\"\n    return  x+1  # trailing\n"), Rule::Stays, "a comment/docstring/format-only edit CHANGED the hash"),
    ("a.py", Some("def f(x):\n    return x + 2\n"), Rule::Moves, "a one-token code change did NOT change the hash"),
    ("c.json", Some("{}\n"), Rule::Baseline, ""),
    ("c.json", Some("{} \n"), Rule::Moves, "a non-.py file is hashed by its bytes and must move on any edit"),
];

#[derive(PartialEq, Clone, Copy)]
enum Rule {
    Baseline,
    Moves,
    Stays,
}

fn selftest_in(dir: &Path, root: &Path, python: &str) -> Result<(), String> {
    stated(std::fs::create_dir_all(dir), "the self-test's directory")?;
    let files = [dir.join("a.py"), dir.join("b.py"), dir.join("c.json")];
    let mut base = String::new();
    for (name, text, rule, why) in SELFTEST {
        let path = dir.join(name);
        match text {
            Some(text) => stated(std::fs::write(&path, text), name)?,
            None => stated(std::fs::remove_file(&path), name)?,
        }
        let now = hash_files(&files, root, false, "", python)?;
        if rule == Rule::Baseline {
            base = now;
        } else if (now == base) == (rule == Rule::Moves) {
            return Err(why.to_owned());
        }
    }
    Ok(())
}

/// Repository-relative paths, one a line: what a caller asks for once a process rather than once a file.
fn listing(files: &[PathBuf], root: &Path) -> String {
    files
        .iter()
        .filter_map(|f| f.strip_prefix(root).ok())
        .map(|f| {
            f.to_string_lossy().into_owned()
                + "
"
        })
        .collect()
}

/// Is `path` in a byte-hashed area, by pattern (so a file not yet on disk answers too)? Ported unchanged from `gate-stamp._matches`, including that an area on the repository root takes `diagram`'s exclusions
/// (`_area_exclusions` named the first area with that root): `ask:T063-browser-raw` holds what that leaves.
#[must_use]
pub fn in_raw_area(root: &Path, path: &str) -> bool {
    AREAS.iter().filter(|a| a.raw).any(|area| {
        let owner = if area.root.is_empty() {
            area_named("diagram").unwrap_or(area)
        } else {
            area
        };
        let head = prefix(area.root);
        let excluded = exclusions(owner, root)
            .iter()
            .any(|sub| path.starts_with(&format!("{head}{sub}")));
        !excluded
            && path
                .strip_prefix(head.as_str())
                .is_some_and(|rel| area.patterns.iter().any(|p| matches(rel, p)))
    })
}

/// Those of the newline-separated `paths` that are in a byte-hashed area, a whole batch in one process.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn raw_matches(root: &Path, paths: &mut dyn Read) -> Result<String, String> {
    let mut text = String::new();
    stated(paths.read_to_string(&mut text), "reading the paths")?;
    Ok(text
        .lines()
        .filter(|p| in_raw_area(root, p))
        .flat_map(|p| [p, "\n"])
        .collect())
}

/// `l7r-gate stamp --write <area> | --fresh <area> | --check <base> | --selftest | --key <area> | --list <area> | --raw-match` (the paths on stdin): the first four answer and record as `gate-stamp.py` did, the other three are what a
/// Python caller asks once a process until it is ported.
pub fn cli(
    args: &[String],
    top: Option<&Path>,
    python: &str,
    stdin: &mut dyn Read,
) -> crate::Reply {
    let reply = answer(args, top, python, stdin);
    if let (Some(root), Some("--write" | "--fresh" | "--check" | "--selftest")) =
        (top, args.first().map(String::as_str))
    {
        record(root, if reply.code == 0 { "passed" } else { "refused" });
    }
    reply
}

fn answer(args: &[String], top: Option<&Path>, python: &str, stdin: &mut dyn Read) -> crate::Reply {
    // not a git checkout: the guard is a no-op rather than an obstacle, and nothing can be fresh
    let Some(root) = top else {
        return crate::Reply {
            stdout: String::new(),
            stderr: String::new(),
            code: i32::from(args.first().is_some_and(|f| f == "--fresh")),
        };
    };
    let say = |stdout: String, stderr: String, code: i32| crate::Reply {
        stdout,
        stderr,
        code,
    };
    let area = args.get(1).and_then(|n| area_named(n));
    match (args.first().map(String::as_str), area) {
        (Some("--write"), Some(area)) => match write_stamp(root, area, python) {
            Ok(()) => say(String::new(), String::new(), 0),
            Err(why) => say(String::new(), format!("gate-stamp: {why}\n"), 1),
        },
        (Some("--fresh"), Some(area)) => {
            let kept = stamp_path(root, area).and_then(|p| std::fs::read_to_string(p).ok());
            let same = kept.is_some_and(|k| area_key(root, area, python).is_ok_and(|want| k.trim() == want));
            say(String::new(), String::new(), i32::from(!same))
        }
        (Some("--selftest"), _) => match selftest(root, python) {
            Ok(()) => say(String::new(), String::new(), 0),
            Err(why) => say(String::new(), format!("gate-stamp selftest: {why}\n"), 1),
        },
        (Some("--list"), Some(area)) => match area_files(root, area) {
            Ok(files) => say(listing(&files, root), String::new(), 0),
            Err(why) => say(String::new(), format!("gate-stamp: {why}\n"), 1),
        },
        (Some("--raw-match"), _) => match raw_matches(root, stdin) {
            Ok(found) => say(found, String::new(), 0),
            Err(why) => say(String::new(), format!("gate-stamp: {why}\n"), 1),
        },
        (Some("--key"), Some(area)) => match area_key(root, area, python) {
            Ok(key) => say(format!("{key}\n"), String::new(), 0),
            Err(why) => say(String::new(), format!("gate-stamp: {why}\n"), 1),
        },
        (Some("--check"), _) => match refusals(root, args.get(1).map_or("origin/main", String::as_str), python) {
            Err(why) => say(String::new(), format!("gate-stamp: {why}\n"), 1),
            Ok(bad) if bad.is_empty() => say(String::new(), String::new(), 0),
            Ok(bad) => {
                let lines: Vec<String> = bad.iter().map(|l| format!("  {l}\n")).collect();
                say(String::new(), format!("gate-stamp: refusing to push code that no green gate has seen (constitution Principle XIII):\n{}gate-stamp: run the named gate at the repository root and push again - it stamps on success.\ngate-stamp: a cohort/sweep regression is NOT covered here; check it separately.\ngate-stamp: escape hatch, with a reason: GATE_STAMP_OK='<why this push is safe>'\n", lines.concat()), 1)
            }
        },
        _ => say(String::new(), "usage: l7r-gate stamp --write <area> | --fresh <area> | --check <base> | --selftest | --key <area> | --list <area> | --raw-match\n".to_owned(), 2),
    }
}

#[cfg(test)]
mod tests;
