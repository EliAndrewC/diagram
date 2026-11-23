//! Save the full visible text of named pages, for `source-reader` to grep (`scripts/record/source_pages.py`, feature 255 FR-006; ported
//! by feature 449 T145, phase 4's S2 under `ask:449-phase4-slices`). Each URL is fetched through the host's page cache
//! ([`crate::pages::CachedPages`]) and its visible text written to `<out>/<nn>-<host>.txt`, wrapped at sentence ends, a long page in
//! parts; `MANIFEST.txt` lists every pointer as `pointer | file | state`. With the ledger, each URL's earlier reads and attempts are
//! printed before it is fetched, a `pending` ledger line appended for each page saved, and an attempt for each pointer asked for.
//! `l7r-gate record source-pages` is the command (the `bundle` crate), and the check bundle's residue save calls [`save`] in process.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::attempts::{self, Ask, More};
use l7r_shared::consulted;
use serde_json::{Map, Value};

use crate::pages::{parts, wrapped, CachedPages, PART};
use crate::verbatim::fetch::urlsplit;
use crate::{re, Error, Result};

/// A page longer than this, saved for a check that names its quotes, is saved as an EXCERPT (D19).
pub const LIMIT: usize = 30_000;
/// An excerpt keeps the page's front.
pub const HEAD: usize = 6_000;
/// And this much either side of each passage the record quotes from it.
pub const WINDOW: usize = 1_500;
/// The outcomes that close a question for a page (feature 312 FR-005).
pub const CLOSED: [&str; 2] = ["not-found", "not-applicable"];
/// The refusal's compliant command (feature 312 FR-017).
pub const NEEDS_SOUGHT: &str = "source-pages: say what this read is for - every consult is recorded on the attempts log (feature 312 FR-017):\n    make source-pages OUT=<dir> URL=<u> QUESTION=<NNNN, or none> SOUGHT=\"<what you are looking for on the page>\"";

static BLOB: LazyLock<Regex> =
    LazyLock::new(|| re(r"^https?://github\.com/([^/]+)/([^/]+)/blob/([\s\S]+)$"));
static HOST_CHARS: LazyLock<Regex> = LazyLock::new(|| re(r"[^a-z0-9.-]+"));
static NUMBERED: LazyLock<Regex> = LazyLock::new(|| re(r"^(\d+)-"));

fn fault(f: l7r_shared::blocked::Fault) -> Error {
    Error::new(f.kind, f.message)
}

/// A number as Python's `f"{n:,}"` writes it.
#[must_use]
pub fn thousands(n: usize) -> String {
    let digits = n.to_string();
    let mut out = String::new();
    for (i, c) in digits.chars().enumerate() {
        if i > 0 && (digits.len() - i) % 3 == 0 {
            out.push(',');
        }
        out.push(c);
    }
    out
}

/// `judged_before`: the attempts that already closed `question` for `url`.
///
/// # Errors
/// A log Python could not read.
pub fn judged_before(root: &Path, url: &str, question: &str) -> Result<Vec<Value>> {
    let n = Value::String(consulted::norm(url));
    let mut out = Vec::new();
    for x in attempts::read(root, attempts::LOG).map_err(fault)? {
        let get = |k: &str| consulted::get(&x, k).map_err(fault);
        if get("url")? == Some(&n)
            && get("question")?.and_then(Value::as_str) == Some(question)
            && get("outcome")?
                .and_then(Value::as_str)
                .is_some_and(|o| CLOSED.contains(&o))
        {
            out.push(x.clone());
        }
    }
    Ok(out)
}

/// `reason_ok`: two words and eight characters, the project's bar for an escape's reason.
#[must_use]
pub fn reason_ok(reason: &str) -> bool {
    use l7r_shared::py_text::{split, strip};
    strip(reason).chars().count() >= 8 && split(reason).len() >= 2
}

/// `file_for`: `<nn>-<host>.txt`.
#[must_use]
pub fn file_for(index: usize, url: &str) -> String {
    let host = urlsplit(url)
        .map(|p| p[1].to_lowercase())
        .unwrap_or_default();
    let host = HOST_CHARS
        .replace_all(&host, "-")
        .trim_matches('-')
        .to_owned();
    format!(
        "{index:02}-{}.txt",
        if host.is_empty() { "page" } else { &host }
    )
}

/// `excerpt`: a long page cut to its front and a window around each quoted passage found in it; a short page whole.
#[must_use]
pub fn excerpt(text: &str, quotes: &[String]) -> String {
    let words = |t: &str| l7r_shared::py_text::collapse(t);
    let flat: Vec<char> = words(text).chars().collect();
    if flat.len() <= LIMIT {
        return text.to_owned();
    }
    let find = |probe: &[char]| -> Option<usize> {
        (0..=flat.len().checked_sub(probe.len())?).find(|&i| flat[i..i + probe.len()] == *probe)
    };
    let mut spans = vec![(0, HEAD.min(flat.len()))];
    for q in quotes {
        let w: Vec<char> = words(q).chars().collect();
        let mid = w.len() / 2;
        // `words[mid - 15 : mid + 15]`, a negative start counted from the end as Python's slice counts it
        let low = if mid >= 15 {
            mid - 15
        } else {
            (w.len() + mid).saturating_sub(15)
        };
        let high = (mid + 15).min(w.len());
        let probes: [&[char]; 3] = [
            &w[..40.min(w.len())],
            if low < high { &w[low..high] } else { &[] },
            &w[w.len().saturating_sub(30)..],
        ];
        let at = probes
            .iter()
            .filter(|p| p.len() >= 12)
            .find_map(|p| find(p));
        if let Some(at) = at {
            spans.push((
                at.saturating_sub(WINDOW),
                flat.len().min(at + q.chars().count() + WINDOW),
            ));
        }
    }
    let found = spans.len() - 1;
    spans.sort_unstable();
    let mut merged: Vec<(usize, usize)> = Vec::new();
    for (a, b) in spans {
        match merged.last_mut() {
            Some(last) if a <= last.1 => last.1 = last.1.max(b),
            _ => merged.push((a, b)),
        }
    }
    let mut pieces = String::new();
    let mut last = 0;
    for (a, b) in merged {
        if a > last {
            let _ = writeln!(
                pieces,
                "\n[... {} characters not copied ...]",
                thousands(a - last)
            );
        }
        pieces.push_str(&wrapped(&flat[a..b].iter().collect::<String>()));
        last = b;
    }
    if last < flat.len() {
        let _ = writeln!(
            pieces,
            "\n[... {} characters not copied ...]",
            thousands(flat.len() - last)
        );
    }
    format!(
        "[EXCERPT of a {}-character page: its first {} characters and {} either side of the {found} of {} quoted passage(s) found in it]\n{pieces}",
        thousands(flat.len()),
        thousands(HEAD),
        thousands(WINDOW),
        quotes.len()
    )
}

/// `fetch_url`: a github.com blob page fetched as its raw file.
#[must_use]
pub fn fetch_url(url: &str) -> String {
    BLOB.captures(url).ok().flatten().map_or_else(
        || url.to_owned(),
        |m| {
            format!(
                "https://raw.githubusercontent.com/{}/{}/{}",
                &m[1], &m[2], &m[3]
            )
        },
    )
}

/// One row of a manifest.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Row {
    pub pointer: String,
    pub file: String,
    pub state: String,
    pub why: String,
}

/// `saved_rows`: the rows an earlier save into `out` listed.
///
/// # Errors
/// A manifest that is not UTF-8.
pub fn saved_rows(out: &Path) -> Result<Vec<Row>> {
    let manifest = out.join("MANIFEST.txt");
    if !manifest.is_file() {
        return Ok(Vec::new());
    }
    let raw = std::fs::read(&manifest).map_err(|e| Error::new("OSError", e.to_string()))?;
    let text =
        String::from_utf8(raw).map_err(|e| Error::new("UnicodeDecodeError", e.to_string()))?;
    let text = text.replace("\r\n", "\n").replace('\r', "\n");
    Ok(l7r_shared::checks::reply::py_lines(&text)
        .into_iter()
        .skip(1)
        .map(|line| {
            let mut cells = line.splitn(3, " | ").map(str::to_owned);
            let (pointer, file, state) = (
                cells.next().unwrap_or_default(),
                cells.next().unwrap_or_default(),
                cells.next().unwrap_or_default(),
            );
            let (state, why) = state.split_once(" - ").unwrap_or((&state, ""));
            Row {
                pointer,
                file,
                state: state.to_owned(),
                why: why.to_owned(),
            }
        })
        .collect())
}

/// `next_number`: one past the highest number a page file in `out` already carries.
///
/// # Errors
/// A directory that cannot be listed.
pub fn next_number(out: &Path) -> Result<usize> {
    let mut top = 0;
    for e in std::fs::read_dir(out)
        .map_err(|e| Error::new("OSError", e.to_string()))?
        .flatten()
    {
        let name = e.file_name().to_string_lossy().into_owned();
        if let Some(n) = NUMBERED
            .captures(&name)
            .ok()
            .flatten()
            .and_then(|c| c[1].parse::<usize>().ok())
        {
            top = top.max(n);
        }
    }
    Ok(top + 1)
}

/// The ledger of a save (feature 288 FR-003, feature 312 FR-017).
pub struct Ledger {
    pub home: PathBuf,
    pub ctx: Map<String, Value>,
    pub questions: Vec<String>,
    pub root: PathBuf,
    pub sought: String,
}

fn write(path: &Path, text: &str) -> Result<()> {
    std::fs::write(path, text).map_err(|e| Error::new("OSError", e.to_string()))
}

/// What the ledger and the attempts log already hold of `url`, printed before it is read.
fn earlier_reads(l: &Ledger, url: &str, said: &mut String) -> Result<()> {
    let seen = consulted::earlier(&l.home, url).map_err(fault)?;
    let _ = writeln!(
        said,
        "sources-consulted: {url} - {}",
        if seen.is_empty() {
            "no earlier read on the ledger".to_owned()
        } else {
            format!("read {} time(s) before:", seen.len())
        }
    );
    for r in &seen {
        said.push_str(&(consulted::show(r).map_err(fault)? + "\n"));
    }
    if !l.sought.is_empty() {
        said.push_str(
            &(attempts::report(&l.root, Ask::Url(url))
                .map_err(fault)?
                .join("\n")
                + "\n"),
        );
    }
    Ok(())
}

/// `save`: each pointer's page saved into `out`; what it printed, and the manifest's rows.
///
/// # Errors
/// What a write, the ledger, the attempts log or the cache refused.
pub fn save(
    urls: &[String],
    out: &Path,
    pages: &mut CachedPages,
    quotes: Option<&[String]>,
    ledger: Option<&Ledger>,
    said: &mut String,
) -> Result<Vec<Row>> {
    std::fs::create_dir_all(out).map_err(|e| Error::new("OSError", e.to_string()))?;
    let rows = saved_rows(out)?;
    let start = (rows.len() + 1).max(next_number(out)?);
    let have: Vec<String> = rows
        .iter()
        .filter(|r| r.state == "FETCHED")
        .map(|r| r.pointer.clone())
        .collect();
    let mut rows: Vec<Row> = rows
        .into_iter()
        .filter(|r| have.contains(&r.pointer) || !urls.contains(&r.pointer))
        .collect();
    let mut todo: Vec<&String> = Vec::new();
    for u in urls {
        if !todo.contains(&u) && !have.contains(u) {
            todo.push(u);
        }
    }
    let record_dir = pages.record_dir.clone();
    for (index, url) in (start..).zip(todo) {
        if let Some(l) = ledger {
            earlier_reads(l, url, said)?;
        }
        let got = pages.get(&fetch_url(url))?;
        if let Some(l) = ledger.filter(|l| !l.sought.is_empty() && !got.blocked) {
            let q = l.questions.first().map_or("unknown", String::as_str);
            let more = More {
                route: "source-pages",
                ..More::default()
            };
            attempts::add(&l.root, url, q, &l.sought, "unknown", &more, &record_dir)
                .map_err(fault)?;
        }
        let mut row = Row {
            pointer: url.clone(),
            file: "-".to_owned(),
            state: got.state.clone(),
            why: got.why.clone(),
        };
        if got.state == "FETCHED" {
            let name = file_for(index, url);
            let text = match quotes {
                None => wrapped(&got.text),
                Some(q) => excerpt(&wrapped(&got.text), q),
            };
            let pieces = parts(&text, PART);
            let stem = &name[..name.len() - 4];
            if pieces.len() == 1 {
                write(&out.join(&name), &pieces[0])?;
                row.file.clone_from(&name);
            } else {
                for (k, piece) in pieces.iter().enumerate() {
                    write(&out.join(format!("{stem}.p{}.txt", k + 1)), piece)?;
                }
                row.file = format!("{stem}.p1.txt ... .p{n}.txt ({n} parts - grep them all, read the part a hit is in)", n = pieces.len());
            }
            let (chars, saved) = (got.text.chars().count(), text.chars().count());
            row.why = format!("{chars} chars");
            if quotes.is_some() && saved < chars {
                let _ = write!(row.why, ", saved as an excerpt of {}", thousands(saved));
            }
            if let Some(at) = &got.cached {
                let day: String = at.chars().take(10).collect();
                let _ = write!(
                    row.why,
                    ", from the page cache (fetched {day}; REFRESH=1 fetches it again)"
                );
            }
            if let Some(day) = got.archived.as_ref().filter(|d| !d.is_empty()) {
                // the link answered with no page (a bot check, 449 T345): what is saved is the archive's capture, said so
                let _ = write!(row.why, ", from the archive's capture of {day}");
            }
            if let Some(l) = ledger {
                let line = consulted::line(&l.ctx, url, "pending", &l.questions);
                consulted::append(&l.home, &[line], &record_dir).map_err(fault)?;
            }
        }
        rows.push(row);
    }
    let manifest = rows.iter().fold(String::new(), |mut m, r| {
        let why = if r.why.is_empty() {
            String::new()
        } else {
            format!(" - {}", r.why)
        };
        let _ = writeln!(m, "{} | {} | {}{why}", r.pointer, r.file, r.state);
        m
    });
    write(
        &out.join("MANIFEST.txt"),
        &format!("pointer | file | state\n{manifest}"),
    )?;
    Ok(rows)
}

#[cfg(test)]
mod tests;
