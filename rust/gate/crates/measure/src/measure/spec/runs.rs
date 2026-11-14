//! Three past measurements read from git and the run log (feature 449 T139, `ask:449-phase3-remainder` Q4): feature 239's
//! `change_size.py`, feature 430's `full_reasons.py` and feature 432's `triage_price.py`.

use std::fmt::Write as _;
use std::io::{BufRead as _, BufReader, Read as _, Write as _};
use std::path::Path;
use std::process::{Child, ChildStdin, ChildStdout, Command, Stdio};
use std::rc::Rc;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_core::record::bundle::today;
use l7r_gate_core::record::repo::git_out;
use l7r_guard::shared::py_text::{repr, split};
use l7r_guard::shared::pyjson::dumps;
use serde_json::{json, Map, Value};

use super::super::events::{re, read_text, Raised};
use super::{command, record, Ran};

const RECORD_239: &str = "specs/239-measurable-guards-and-derived-figures/measurements.json";

static INSERTIONS: LazyLock<Regex> = LazyLock::new(|| re(r"(\d+) insertion"));
static DELETIONS: LazyLock<Regex> = LazyLock::new(|| re(r"(\d+) deletion"));
static REASON: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r#"(a non-module file under tests/ changed: [^"\\]+|an engine file that is not Python changed: [^"\\]+)"#,
    )
});

/// The first group of `pattern` in `text` as a number, 0 where it is absent (`int((re.search(...) or [0, 0])[1] or 0)`).
fn count(pattern: &Regex, text: &str) -> u64 {
    pattern
        .captures(text)
        .ok()
        .flatten()
        .and_then(|c| c[1].parse().ok())
        .unwrap_or(0)
}

/// `git diff --shortstat a b -- paths`: insertions and deletions, both 0 where git printed nothing (a bad revision included).
fn diffstat(root: &Path, a: &str, b: &str, paths: &[&str]) -> (u64, u64) {
    let mut args = vec!["diff", "--shortstat", a, b, "--"];
    args.extend(paths);
    let out = git_out(root, &args);
    (count(&INSERTIONS, &out), count(&DELETIONS, &out))
}

/// `l7r-gate measure spec 239 change-size <from-ref> <to-ref> [--record]`: how large a change actually was, from git rather than
/// from memory (feature 239: "about 40 lines" understated feature 236's second amendment about sevenfold).
pub(super) fn change_size(args: &[String], root: &Path, out: &mut String) -> Ran {
    let (Some(a), Some(b)) = (args.first(), args.get(1)) else {
        return Err("IndexError: list index out of range".to_owned());
    };
    let (guard_ins, guard_del) = diffstat(
        root,
        a,
        b,
        &["scripts/house-style-hooks.sh", "scripts/_hm_house.py"],
    );
    let (all_ins, all_del) = diffstat(root, a, b, &["scripts/"]);
    let _ = writeln!(out, "{a}..{b}");
    let _ = writeln!(out, "  the hook and its module: +{guard_ins} -{guard_del}");
    let _ = writeln!(out, "  all of scripts/:         +{all_ins} -{all_del}");
    if args.iter().any(|x| x == "--record") {
        let (now, cmd) = (
            today(),
            command("239", "change-size", &format!(" {a} {b} --record")),
        );
        record(
            &root.join(RECORD_239),
            vec![
                (
                    "amendment-guard-lines-added",
                    json!({"value": guard_ins, "unit": "lines", "taken": now, "command": cmd, "note": "feature 236 amendment 2: the hook and its new module"}),
                ),
                (
                    "amendment-scripts-lines-added",
                    json!({"value": all_ins, "unit": "lines", "taken": now, "command": cmd, "note": "the same window, all of scripts/"}),
                ),
            ],
        )?;
        let _ = writeln!(out, "recorded 2 figures in measurements.json");
    }
    Ok(0)
}

/// `l7r-gate measure spec 430 full-reasons` (`m:full-plan-reasons`): each 2026-10-26 `make done` run planned full, by its reason's file,
/// read from the working directory's `dev/run-log/` as the Python's relative glob read it.
#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "the Python's `glob(\"20261026*.json\")` is case-sensitive"
)]
pub(super) fn full_reasons(cwd: &Path, out: &mut String) -> Ran {
    let dir = cwd.join("dev/run-log/2026-10");
    let mut names: Vec<String> = std::fs::read_dir(&dir)
        .into_iter()
        .flatten()
        .flatten()
        .filter_map(|e| e.file_name().into_string().ok())
        .filter(|n| n.starts_with("20261026") && n.ends_with(".json"))
        .collect();
    names.sort();
    let mut counts: Vec<(String, usize)> = Vec::new();
    for name in names {
        let path = dir.join(&name);
        let run: Value = serde_json::from_str(&read_text(&path)?)
            .map_err(|e| format!("JSONDecodeError: {}: {e}", path.display()))?;
        let Value::Object(fields) = &run else {
            return Err(format!("AttributeError: {name} holds no object"));
        };
        if fields.get("target") != Some(&Value::from("done")) {
            continue;
        }
        let text = dumps(&run, None, true);
        let Some(m) = REASON.captures(&text).ok().flatten() else {
            continue;
        };
        match counts.iter_mut().find(|(r, _)| *r == m[1]) {
            Some(row) => row.1 += 1,
            None => counts.push((m[1].to_owned(), 1)),
        }
    }
    counts.sort_by(|a, b| b.1.cmp(&a.1));
    for (reason, n) in counts {
        let _ = writeln!(out, "{n} {reason}");
    }
    Ok(0)
}

/// Python's `==` over what `json.loads` made: `1 == 1.0 == True`, a dict equal whatever its keys' order.
fn py_eq(a: &Value, b: &Value) -> bool {
    let number = |v: &Value| match v {
        Value::Bool(x) => Some(f64::from(u8::from(*x))),
        Value::Number(n) => n.as_f64(),
        _ => None,
    };
    match (a, b) {
        (Value::Array(x), Value::Array(y)) => {
            x.len() == y.len() && x.iter().zip(y).all(|(p, q)| py_eq(p, q))
        }
        (Value::Object(x), Value::Object(y)) => {
            x.len() == y.len() && x.iter().all(|(k, p)| y.get(k).is_some_and(|q| py_eq(p, q)))
        }
        _ => match (number(a), number(b)) {
            (Some(x), Some(y)) => x == y,
            _ => a == b,
        },
    }
}

/// `value in {"DRIFTED", "MISLABELED"}`: a list or a dict is unhashable, the Python's `TypeError`.
fn finding(v: &Value) -> Result<bool, Raised> {
    match v {
        Value::Array(_) | Value::Object(_) => Err("TypeError: unhashable type".to_owned()),
        Value::String(s) => Ok(s == "DRIFTED" || s == "MISLABELED"),
        _ => Ok(false),
    }
}

/// `x.get(key)`, `None` where absent; anything but a dict the Python's `AttributeError`.
fn get<'a>(v: &'a Value, key: &str) -> Result<&'a Value, Raised> {
    static NULL: Value = Value::Null;
    match v {
        Value::Object(m) => Ok(m.get(key).unwrap_or(&NULL)),
        _ => Err("AttributeError: no .get on a value that is no dict".to_owned()),
    }
}

/// The claims index at each revision: the blob names through one `git cat-file --batch-check`, each blob through one `git cat-file
/// --batch` kept open, the last three parsed kept (a pair is looked up parent first, and the next commit's own blob is usually this
/// one's parent's). The Python's two `git show` processes a commit (1,116 over the window) and its parse of every blob twice cost 48.8 s
/// (observed 2026-11-13, method: `time python3 specs/432-gm-review-signal/measure/triage_price.py`). A missing file, or text that is no
/// JSON, is `{}`, as the Python's `at()` read it.
struct Index {
    cat: Option<(ChildStdin, BufReader<ChildStdout>, Child)>,
    kept: Vec<(String, Rc<Value>)>,
}

impl Index {
    fn new(root: &Path) -> Self {
        let cat = Command::new("git")
            .arg("-C")
            .arg(root)
            .args(["cat-file", "--batch"])
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::null())
            .spawn()
            .ok()
            .and_then(|mut child| {
                let (stdin, stdout) = (child.stdin.take()?, child.stdout.take()?);
                Some((stdin, BufReader::new(stdout), child))
            });
        Self {
            cat,
            kept: Vec::new(),
        }
    }

    /// One blob's text through the open `--batch`: its header line, then its size in bytes and a newline.
    fn text(&mut self, blob: &str) -> std::io::Result<String> {
        let Some((stdin, stdout, _)) = self.cat.as_mut() else {
            return Ok(String::new());
        };
        stdin.write_all(format!("{blob}\n").as_bytes())?;
        stdin.flush()?;
        let mut head = String::new();
        stdout.read_line(&mut head)?;
        let Some(size) = head
            .split_whitespace()
            .nth(2)
            .and_then(|n| n.parse::<usize>().ok())
        else {
            return Ok(String::new()); // `<name> missing`: no body follows
        };
        let mut body = vec![0; size + 1];
        stdout.read_exact(&mut body)?;
        body.truncate(size);
        Ok(String::from_utf8_lossy(&body).into_owned())
    }

    fn at(&mut self, blob: &str) -> Rc<Value> {
        if let Some((_, v)) = self.kept.iter().find(|(b, _)| b == blob) {
            return Rc::clone(v);
        }
        let text = if blob.is_empty() {
            String::new()
        } else {
            self.text(blob).unwrap_or_default()
        };
        let v = Rc::new(serde_json::from_str(&text).unwrap_or_else(|_| Value::Object(Map::new())));
        self.kept.push((blob.to_owned(), Rc::clone(&v)));
        if self.kept.len() > 3 {
            self.kept.remove(0);
        }
        v
    }
}

impl Drop for Index {
    fn drop(&mut self) {
        if let Some((stdin, _, child)) = &mut self.cat {
            let _ = stdin.flush();
            let _ = child.kill();
            let _ = child.wait();
        }
    }
}

/// `git cat-file --batch-check` fed `input`, written beside the read so neither pipe fills.
fn batch_check(root: &Path, input: &str) -> std::io::Result<String> {
    let mut child = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["cat-file", "--batch-check=%(objectname) %(objecttype)"])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .spawn()?;
    let (pipe, body) = (child.stdin.take(), input.to_owned());
    let writer = std::thread::spawn(move || pipe.map(|mut p| p.write_all(body.as_bytes())));
    let done = child.wait_with_output()?;
    let _ = writer.join();
    Ok(String::from_utf8_lossy(&done.stdout).into_owned())
}

/// Each `<rev>:dev/claims-index.json`'s blob name, "" where the revision holds no such file.
fn blobs(root: &Path, revs: &[String]) -> Vec<String> {
    let input = revs.iter().fold(String::new(), |mut acc, r| {
        let _ = writeln!(acc, "{r}:dev/claims-index.json");
        acc
    });
    let text = batch_check(root, &input).unwrap_or_default();
    let mut lines = text.lines();
    revs.iter()
        .map(|_| {
            lines
                .next()
                .and_then(|l| l.strip_suffix(" blob"))
                .unwrap_or_default()
                .to_owned()
        })
        .collect()
}

/// `l7r-gate measure spec 432 triage-price` (`m:triage-price`, feature 432 T05, D7): what clearing a page-edit's triage-owed claims
/// mechanically would have let through, replayed over every commit that changed `dev/claims-index.json` from 2026-10-04 to 2026-10-26
/// against its first parent.
pub(super) fn triage_price(root: &Path, out: &mut String) -> Ran {
    let log = git_out(
        root,
        &[
            "log",
            "--since=2026-10-04",
            "--until=2026-10-26T23:59:59",
            "--format=%h %p",
            "--",
            "dev/claims-index.json",
        ],
    );
    // `git log --format=%h %p` prints no empty line, so the Python's unpacking never raised; a root commit has no parent and is skipped
    let commits: Vec<Vec<&str>> = log.lines().map(split).collect();
    let revs: Vec<String> = commits
        .iter()
        .filter(|c| c.len() > 1)
        .flat_map(|c| [c[1].to_owned(), c[0].to_owned()])
        .collect();
    let named = blobs(root, &revs);
    let mut index = Index::new(root);
    let (mut tally, mut found): (Vec<(String, usize)>, Vec<String>) = (Vec::new(), Vec::new());
    for (pair, commit) in named.chunks(2).zip(commits.iter().filter(|c| c.len() > 1)) {
        let (a, b) = (index.at(&pair[0]), index.at(&pair[1]));
        let Value::Object(rows) = &*b else {
            return Err("AttributeError: the claims index holds no dict".to_owned());
        };
        for (k, row) in rows {
            let was = get(&a, k)?;
            if !super::super::events::truthy(was) || !py_eq(get(row, "code")?, get(was, "code")?) {
                continue;
            }
            if py_eq(get(row, "pages")?, get(was, "pages")?) {
                continue;
            }
            let same_rests = py_eq(get(row, "rests")?, get(was, "rests")?);
            let (new, old) = (get(row, "verdict")?, get(was, "verdict")?);
            let route = if same_rests { "triage" } else { "rests" };
            let what = if finding(new)? && !finding(old)? {
                if same_rests {
                    found.push(format!(
                        "  {} {:10} {k}",
                        commit[0],
                        new.as_str().unwrap_or_default()
                    ));
                }
                "new finding"
            } else if py_eq(new, old) {
                "re-judged, same verdict"
            } else {
                continue;
            };
            let key = format!("{route}: {what}");
            match tally.iter_mut().find(|(r, _)| *r == key) {
                Some(row) => row.1 += 1,
                None => tally.push((key, 1)),
            }
        }
    }
    let shown: Vec<String> = tally
        .iter()
        .map(|(k, n)| format!("{}: {n}", repr(k)))
        .collect();
    let _ = writeln!(out, "{{{}}}", shown.join(", "));
    for line in found {
        let _ = writeln!(out, "{line}");
    }
    Ok(0)
}

#[cfg(test)]
mod tests;
