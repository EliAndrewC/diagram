//! The attempts log (`scripts/record/attempts.py`, feature 312 FR-015 - FR-018; ported by feature 449 T145, phase 4's S2 under
//! `ask:449-phase4-slices`): what each source was tried for and what came of it, `research/source-attempts.jsonl`, one JSON line an
//! attempt, appended under the sources-consulted ledger's lock. In the guard's shared code because the blocked-fetch guard asks it once
//! a fetch, in process, where it ran `attempts.py seen` by path (T039 decision (c)); `l7r-gate record attempts` (`make attempts`) and the
//! gate's `source-outcome` and `source-pages` call the same functions, and the `uncited` crate's fetch and lists (feature 449 T147, S3b,
//! which deleted `attempts.py` with its last importers): this is the log's one implementation.

use std::collections::HashSet;
use std::io::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Map, Value};

use crate::shared::blocked::{blocked, domains, type_name, Fault};
use crate::shared::consulted::{self, get, norm, text};
use crate::shared::html_text::unescape;
use crate::shared::py_text::{repr, strip};
use crate::shared::pyjson::{dumps, loads, py_str, truthy};

pub const LOG: &str = "research/source-attempts.jsonl";
pub const NOT_KEPT: &str = "research/not-kept.jsonl";
pub const UNCITED: &str = "research/sources/040-uncited-works";
pub const OUTCOMES: [&str; 6] = [
    "found",
    "partial",
    "not-found",
    "not-applicable",
    "unreadable",
    "unknown",
];
pub const UNKNOWN_SOUGHT: &str = "unknown - recorded before feature 312";
pub const SEED: &str = "ledger-2026-10-02";

fn re(pattern: &str) -> Regex {
    crate::shared::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

// `$` in Python's `re` also matches before a final newline
static STEM: LazyLock<Regex> = LazyLock::new(|| re(r"^\d{4}\n?\z"));
static OLD: LazyLock<Regex> = LazyLock::new(|| re(r"^([a-z0-9-]+(?:/[a-z0-9-]+)*)/(\d{3})\n?\z"));

/// `base`: the tree whose `research/` holds the log - the clone, or `L7R_ATTEMPTS_ROOT` (the tests' seam).
#[must_use]
pub fn base(root: &Path) -> PathBuf {
    let at = consulted::var("L7R_ATTEMPTS_ROOT");
    if at.is_empty() {
        root.to_path_buf()
    } else {
        PathBuf::from(at)
    }
}

/// `today()`: the local date, as `date(1)` reads the zone (the crate reads none itself).
#[must_use]
pub fn today() -> String {
    crate::shared::tool::ask(Path::new("/"), "date", &["+%Y-%m-%d"], "").out
}

/// `read`: the log's lines (or another file of the record's, `rel`).
///
/// # Errors
/// A file that is not UTF-8.
pub fn read(root: &Path, rel: &str) -> Result<Vec<Value>, Fault> {
    consulted::read_lines(&base(root).join(rel))
}

/// `write`: append under the ledger's kind of lock, each URL checked against the blocked list (read from `record_dir`) first.
///
/// # Errors
/// A blocked URL, a line with no URL, the lock or the write.
pub fn write(root: &Path, lines: &[Value], record_dir: &Path) -> Result<(), Fault> {
    if lines.is_empty() {
        return Ok(());
    }
    for x in lines {
        let raw = match get(x, "raw")?.filter(|v| truthy(v)) {
            Some(v) => v,
            None => get(x, "url")?.ok_or_else(|| Fault::new("KeyError", "'url'".to_owned()))?,
        };
        consulted::check(&py_str(raw), "the attempts log", record_dir)?;
    }
    let path = base(root).join(LOG);
    std::fs::create_dir_all(path.parent().unwrap_or(Path::new(".")))
        .map_err(|e| Fault::new("OSError", e.to_string()))?;
    let _lock = consulted::locked(&consulted::home(root), 30.0)?;
    let text: String = lines.iter().map(|x| dumps(x, None, false) + "\n").collect();
    std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(&path)
        .and_then(|mut f| f.write_all(text.as_bytes()))
        .map_err(|e| Fault::new("OSError", e.to_string()))
}

/// The optional fields of a line.
#[derive(Default)]
pub struct More<'a> {
    pub key: &'a str,
    pub route: &'a str,
    pub feature: &'a str,
    pub date: &'a str,
}

/// `line`: one attempt, its keys in the Python's order.
///
/// # Errors
/// An outcome not one of [`OUTCOMES`] (`ValueError`).
pub fn line(
    url: &str,
    question: &Value,
    sought: &str,
    outcome: &str,
    more: &More<'_>,
) -> Result<Value, Fault> {
    if !OUTCOMES.contains(&outcome) {
        return Err(Fault::new(
            "ValueError",
            format!(
                "outcome {} is not one of {}",
                repr(outcome),
                OUTCOMES.join(", ")
            ),
        ));
    }
    let feature = if more.feature.is_empty() {
        consulted::var("SPECIFY_FEATURE").chars().take(3).collect()
    } else {
        more.feature.to_owned()
    };
    let mut x = Map::new();
    x.insert("url".into(), json!(norm(url)));
    x.insert("raw".into(), json!(url));
    x.insert("key".into(), json!(more.key));
    x.insert(
        "question".into(),
        if truthy(question) {
            question.clone()
        } else {
            json!("unknown")
        },
    );
    x.insert("sought".into(), json!(sought));
    x.insert("outcome".into(), json!(outcome));
    x.insert(
        "date".into(),
        json!(if more.date.is_empty() {
            today()
        } else {
            more.date.to_owned()
        }),
    );
    x.insert("feature".into(), json!(feature));
    x.insert("route".into(), json!(more.route));
    Ok(Value::Object(x))
}

/// `add`: one attempt written, its feature the context's where none is given (the context is read either way, as `setdefault` did).
///
/// # Errors
/// The context, the line or the write.
pub fn add(
    root: &Path,
    url: &str,
    question: &str,
    sought: &str,
    outcome: &str,
    more: &More<'_>,
    record_dir: &Path,
) -> Result<Value, Fault> {
    let ctx = consulted::context(root)?;
    let feature = if more.feature.is_empty() {
        ctx.get("feature")
            .and_then(Value::as_str)
            .unwrap_or("")
            .to_owned()
    } else {
        more.feature.to_owned()
    };
    let x = line(
        url,
        &json!(question),
        sought,
        outcome,
        &More {
            feature: &feature,
            ..*more
        },
    )?;
    write(root, std::slice::from_ref(&x), record_dir)?;
    Ok(x)
}

/// `seen`: what the fetch guard asks, once a fetch - each URL's report when it says more than its head and the URL with every entity
/// decoded, and with `record` its attempt written (a failure to write never blocks the read).
///
/// # Errors
/// A log that cannot be read.
pub fn seen(
    root: &Path,
    urls: &[String],
    sought: &str,
    route: &str,
    record: bool,
    record_dir: &Path,
) -> Result<Vec<Value>, Fault> {
    let mut out = Vec::new();
    for url in urls {
        let got = report(root, Ask::Url(url))?;
        out.push(
            json!({"lines": if got.len() > 1 { got } else { Vec::new() }, "plain": unescape(url)}),
        );
        if record {
            let more = More {
                route,
                ..More::default()
            };
            let _ = add(root, url, "unknown", sought, "unknown", &more, record_dir);
        }
    }
    Ok(out)
}

/// `old_ids`: `moved-303.json`'s numbers, keyed as the ledger wrote them (`<page>/<NNN>`).
///
/// # Errors
/// A file that is not JSON, or not a mapping.
pub fn old_ids(root: &Path) -> Result<Map<String, Value>, Fault> {
    let path = root.join("research/moved-303.json");
    if !path.is_file() {
        return Ok(Map::new());
    }
    let raw = std::fs::read(&path).map_err(|e| Fault::new("OSError", e.to_string()))?;
    let text =
        String::from_utf8(raw).map_err(|e| Fault::new("UnicodeDecodeError", e.to_string()))?;
    let data = loads(&text).map_err(|e| Fault::new("JSONDecodeError", e.to_string()))?;
    let numbers = match &data {
        Value::Object(map) => map.get("numbers").cloned().unwrap_or_else(|| json!({})),
        other => {
            return Err(Fault::new(
                "AttributeError",
                format!("'{}' object has no attribute 'get'", type_name(other)),
            ))
        }
    };
    let Value::Object(numbers) = numbers else {
        return Err(Fault::new(
            "AttributeError",
            format!("'{}' object has no attribute 'items'", type_name(&numbers)),
        ));
    };
    Ok(numbers
        .into_iter()
        .map(|(k, v)| (k.replace(' ', "/"), v))
        .collect())
}

/// `question_of`: (the question, what was sought) for one ledger `questions` entry.
#[must_use]
pub fn question_of(q: &str, mapped: &Map<String, Value>) -> (Value, String) {
    if STEM.is_match(q).unwrap_or(false) {
        return (json!(q), String::new());
    }
    if OLD.is_match(q).unwrap_or(false) {
        return (
            mapped
                .get(q)
                .cloned()
                .unwrap_or_else(|| json!(format!("old:{q}"))),
            String::new(),
        );
    }
    (json!("unknown"), q.to_owned())
}

/// `from_ledger`: a ledger outcome as (the attempt's outcome, its key, the rejection's reason).
#[must_use]
pub fn from_ledger(outcome: &str) -> (&'static str, String, String) {
    let (kind, why) = outcome.split_once(':').unwrap_or((outcome, ""));
    let result = match strip(kind) {
        "nothing-found" => "not-found",
        "rejected" => "not-applicable",
        "unreadable" => "unreadable",
        "cited" => "found",
        _ => "unknown",
    };
    let why = strip(why).to_owned();
    (
        result,
        if kind == "cited" {
            why.clone()
        } else {
            String::new()
        },
        if kind == "rejected" {
            why
        } else {
            String::new()
        },
    )
}

/// `last_sought`: what the latest attempt on this URL for this question sought.
///
/// # Errors
/// A log line that is not a mapping, or a hit with no `sought`.
pub fn last_sought(root: &Path, url: &str, question: &str) -> Result<String, Fault> {
    let n = json!(norm(url));
    let q = json!(if question.is_empty() {
        "unknown"
    } else {
        question
    });
    let mut last = None;
    for x in read(root, LOG)? {
        if get(&x, "url")? == Some(&n) && get(&x, "question")? == Some(&q) {
            last = Some(x);
        }
    }
    match last {
        None => Ok(UNKNOWN_SOUGHT.to_owned()),
        Some(x) => {
            let s =
                get(&x, "sought")?.ok_or_else(|| Fault::new("KeyError", "'sought'".to_owned()))?;
            Ok(text(s, "can only concatenate str")?.to_owned())
        }
    }
}

/// `outcome`: `make source-outcome`'s attempt line (FR-017), the outcome of the read with what it sought.
///
/// # Errors
/// As [`add`] and [`last_sought`].
pub fn outcome(
    root: &Path,
    url: &str,
    question: &str,
    ledger_outcome: &str,
    sought: &str,
    record_dir: &Path,
) -> Result<Value, Fault> {
    let (result, key, why) = from_ledger(ledger_outcome);
    let sought = if sought.is_empty() {
        last_sought(root, url, question)?
    } else {
        sought.to_owned()
    };
    let sought = if why.is_empty() {
        sought
    } else {
        format!("{sought} (rejected: {why})")
    };
    let more = More {
        key: &key,
        route: "source-outcome",
        ..More::default()
    };
    add(root, url, question, &sought, result, &more, record_dir)
}

/// A field's text, `r.get(name, "")` read as Python slices or tests it.
fn field_text(r: &Value, name: &str) -> Result<String, Fault> {
    Ok(get(r, name)?
        .map(|v| text(v, name).map(str::to_owned))
        .transpose()?
        .unwrap_or_default())
}

/// `seed_lines`: an attempt line for each question of each ledger row.
///
/// # Errors
/// A row Python could not read.
pub fn seed_lines(rows: &[Value], mapped: &Map<String, Value>) -> Result<Vec<Value>, Fault> {
    let mut out = Vec::new();
    for r in rows {
        let (result, key, why) = from_ledger(&field_text(r, "outcome")?);
        let questions: Vec<Value> = match get(r, "questions")?.filter(|v| truthy(v)) {
            None => vec![json!("")],
            Some(Value::Array(items)) => items.clone(),
            Some(Value::String(s)) => s.chars().map(|c| json!(c.to_string())).collect(),
            Some(other) => {
                return Err(Fault::new(
                    "TypeError",
                    format!("'{}' object is not iterable", type_name(other)),
                ))
            }
        };
        for q in questions {
            let (question, sought) = if truthy(&q) {
                question_of(text(&q, "expected string")?, mapped)
            } else {
                (json!("unknown"), String::new())
            };
            let sought = if sought.is_empty() {
                UNKNOWN_SOUGHT.to_owned()
            } else {
                sought
            };
            let sought = if why.is_empty() {
                sought
            } else {
                format!("{sought} (rejected: {why})")
            };
            let raw = match get(r, "raw")?.filter(|v| truthy(v)) {
                Some(v) => text(v, "raw")?.to_owned(),
                None => text(
                    get(r, "url")?.ok_or_else(|| Fault::new("KeyError", "'url'".to_owned()))?,
                    "url",
                )?
                .to_owned(),
            };
            let (feature, utc) = (field_text(r, "feature")?, field_text(r, "utc")?);
            let date: String = utc.chars().take(10).collect();
            let more = More {
                key: &key,
                route: "ledger",
                feature: &feature,
                date: &date,
            };
            let mut x = line(&raw, &question, &sought, result, &more)?;
            if let Value::Object(m) = &mut x {
                m.insert("seed".into(), json!(SEED));
            }
            out.push(x);
        }
    }
    Ok(out)
}

/// A line's (url, date, feature), compared as Python's tuples are.
fn ident(x: &Value) -> Result<String, Fault> {
    let url = get(x, "url")?
        .cloned()
        .ok_or_else(|| Fault::new("KeyError", "'url'".to_owned()))?;
    let date = get(x, "date")?.cloned().unwrap_or_else(|| json!(""));
    let feature = get(x, "feature")?.cloned().unwrap_or_else(|| json!(""));
    Ok(dumps(&json!([url, date, feature]), None, false))
}

/// `seed`: every ledger row with no attempt line yet gets one, matched by URL, day and feature; (stdout, stderr, lines written).
///
/// # Errors
/// A log, a ledger or a list Python could not read, or the write.
pub fn seed(root: &Path, dir: &Path, record_dir: &Path) -> Result<(String, String, usize), Fault> {
    let mut have = HashSet::new();
    for x in read(root, LOG)? {
        have.insert(ident(&x)?);
    }
    // the list is read at the first row that asks it, as the Python's cached loader was
    let mut rules = None;
    let mut rows = Vec::new();
    for r in consulted::read(dir)? {
        let Some(url) = get(&r, "url")?.filter(|v| truthy(v)).cloned() else {
            continue;
        };
        let raw = get(&r, "raw")?
            .filter(|v| truthy(v))
            .cloned()
            .unwrap_or(url);
        if rules.is_none() {
            rules = Some(domains(record_dir)?);
        }
        if blocked(&py_str(&raw), rules.as_deref().unwrap_or_default()).is_none() {
            rows.push(r);
        }
    }
    let mut lines = Vec::new();
    for x in seed_lines(&rows, &old_ids(root)?)? {
        if !have.contains(&ident(&x)?) {
            lines.push(x);
        }
    }
    if lines.is_empty() {
        return Ok((
            String::new(),
            "attempts: every ledger row has an attempt line - nothing written\n".to_owned(),
            0,
        ));
    }
    let new: HashSet<String> = lines.iter().map(|x| py_str(&x["url"])).collect();
    let mut matched = 0;
    for r in &rows {
        if new.contains(&norm(&py_str(&r["url"]))) {
            matched += 1;
        }
    }
    write(root, &lines, record_dir)?;
    Ok((
        format!(
            "attempts: {} line(s) seeded from {matched} ledger row(s)\n",
            lines.len()
        ),
        String::new(),
        lines.len(),
    ))
}

/// `verdict`: the filter's word on a URL - not kept (its reasons), kept (its uncited entry), or nothing yet.
///
/// # Errors
/// A list line or an entry Python could not read.
pub fn verdict(root: &Path, url: &str) -> Result<String, Fault> {
    let n = json!(norm(url));
    for x in read(root, NOT_KEPT)?.iter().rev() {
        if get(x, "url")? == Some(&n) {
            let note = match get(x, "note")?.filter(|v| truthy(v)) {
                Some(v) => format!(" - {}", py_str(v)),
                None => String::new(),
            };
            let mut reasons = Vec::new();
            match get(x, "reasons")? {
                None => {}
                Some(Value::Array(items)) => {
                    for (i, r) in items.iter().enumerate() {
                        reasons.push(text(r, &format!("sequence item {i}"))?.to_owned());
                    }
                }
                Some(Value::String(s)) => reasons.extend(s.chars().map(String::from)),
                Some(_) => {
                    return Err(Fault::new(
                        "TypeError",
                        "can only join an iterable".to_owned(),
                    ))
                }
            }
            let date = get(x, "date")?.map(py_str).unwrap_or_default();
            return Ok(format!("NOT KEPT {date} ({}{note})", reasons.join(", ")));
        }
    }
    let d = base(root).join(UNCITED);
    let mut pages: Vec<PathBuf> = std::fs::read_dir(&d)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter(|p| p.extension().is_some_and(|x| x == "html"))
        .collect();
    pages.sort();
    let n = py_str(&n);
    for p in pages {
        let raw = std::fs::read(&p).map_err(|e| Fault::new("OSError", e.to_string()))?;
        let body =
            String::from_utf8(raw).map_err(|e| Fault::new("UnicodeDecodeError", e.to_string()))?;
        let body = body.replace("\r\n", "\n").replace('\r', "\n");
        if consulted::URL
            .find_iter(&body)
            .map_while(Result::ok)
            .any(|m| norm(m.as_str()) == n)
        {
            let name = p
                .file_name()
                .map(|s| s.to_string_lossy().into_owned())
                .unwrap_or_default();
            return Ok(format!("KEPT, uncited: {name}"));
        }
    }
    Ok(String::new())
}

/// `show`: one attempt as a line.
#[must_use]
pub fn show(x: &Value) -> String {
    let f = |k: &str| x.get(k).map(py_str).unwrap_or_default();
    format!(
        "  {} Q {}: {} - {}",
        f("date"),
        f("question"),
        f("outcome"),
        f("sought")
    )
}

/// What a report is asked for.
#[derive(Clone, Copy)]
pub enum Ask<'a> {
    Url(&'a str),
    Key(&'a str),
    Question(&'a str),
}

/// `report`: the attempts on a URL (with the filter's verdict), a registry key, or a question.
///
/// # Errors
/// A log line that is not a mapping, or the verdict's reading.
pub fn report(root: &Path, ask: Ask<'_>) -> Result<Vec<String>, Fault> {
    let lines = read(root, LOG)?;
    let pick = |name: &str, want: &Value| -> Result<Vec<Value>, Fault> {
        let mut hits = Vec::new();
        for x in &lines {
            if get(x, name)? == Some(want) {
                hits.push(x.clone());
            }
        }
        Ok(hits)
    };
    match ask {
        Ask::Url(url) => {
            let hits = pick("url", &json!(norm(url)))?;
            let mut head = vec![format!(
                "attempts: {url} - {}",
                if hits.is_empty() {
                    "no earlier attempt".to_owned()
                } else {
                    format!("{} earlier attempt(s):", hits.len())
                }
            )];
            let v = verdict(root, url)?;
            if !v.is_empty() {
                head.push(format!("  filter verdict: {v}"));
            }
            head.extend(hits.iter().map(show));
            Ok(head)
        }
        Ask::Key(key) => {
            let hits = pick("key", &json!(key))?;
            let mut head = vec![format!("attempts: key {key} - {} attempt(s)", hits.len())];
            head.extend(hits.iter().map(show));
            Ok(head)
        }
        Ask::Question(q) => {
            let hits = pick("question", &json!(q))?;
            let mut head = vec![format!(
                "attempts: question {q} - {} attempt(s)",
                hits.len()
            )];
            for x in &hits {
                let raw = match x.get("raw").filter(|v| truthy(v)) {
                    Some(v) => py_str(v),
                    None => py_str(
                        x.get("url")
                            .ok_or_else(|| Fault::new("KeyError", "'url'".to_owned()))?,
                    ),
                };
                head.push(format!("  {raw}\n  {}", strip(&show(x))));
            }
            Ok(head)
        }
    }
}

#[cfg(test)]
mod tests;
