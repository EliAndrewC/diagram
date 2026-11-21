//! THE FILTER (feature 312 FR-008): the `source-filter` agent over BUNDLES of whole pages (plan D5, plan review 2026-10-02: never a front
//! cut). A bundle closes at about 150,000 characters or 60,000 estimated tokens, whichever comes first - a CJK character is about a token
//! where a Latin one is about a quarter (research.md R3); a page over that goes alone, in parts of 20,000 estimated tokens, each a file the
//! agent reads whole. The agent writes `verdicts.jsonl` beside the bundle's `MANIFEST.md`; [`apply`] refuses a bundle whose verdicts miss
//! an id, carry an unknown reason, or give a NOT-KEPT no reason. The write-ups' drafts (FR-012, plan D9) are bundled the same way.

use std::collections::BTreeSet;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use l7r_shared::consulted;
use l7r_shared::pyjson::{dumps, py_str, truthy, value_repr};
use serde_json::{json, Map, Value};

use crate::entries::written;
use crate::lists::{field, kept, line, not_kept, read};
use crate::{
    chars, first, lines, lines_keep, loads, name_of, read_text, registry_keys, strip, text_of,
    tokens, write_text,
};
use crate::{mkdir, Error, Result, KEPT, REASONS};

pub const BUNDLE_CHARS: usize = 150_000;
pub const BUNDLE_TOKENS: usize = 60_000;
pub const PART_TOKENS: usize = 20_000;
/// The Read tool returns about 60,000 characters of a file; a part longer was read in part (feature 312, 2026-10-02).
pub const PART_CHARS: usize = 50_000;
/// A draft bundle's pages, at most.
pub const DRAFT_PAGES: usize = 15;

/// Where the bundles' contracts live: the gate's own tree (the Python's `HERE.parents[1]`), not the root it runs on.
pub struct Contracts {
    pub tree: PathBuf,
}

impl Contracts {
    /// The `source-filter` contract.
    #[must_use]
    pub fn filter(&self) -> PathBuf {
        self.tree.join(".claude/agents/source-filter.md")
    }

    /// The write-up contract.
    #[must_use]
    pub fn writeup(&self) -> PathBuf {
        self.tree
            .join("specs/312-uncited-source-catalog/writeup-contract.md")
    }

    /// The `source-filter` contract without its frontmatter, copied into every bundle as `CONTRACT.md`: a session that has not restarted
    /// since the agent file was added cannot dispatch it by name, and dispatches an ad-hoc Opus agent on the same contract instead
    /// (research.md R2) - which then reads nothing under the repository.
    ///
    /// # Errors
    /// The file will not read, or its frontmatter does not close (the Python's `IndexError`).
    pub fn body(&self) -> Result<String> {
        let text = read_text(&self.filter())?;
        if !text.starts_with("---\n") {
            return Ok(text);
        }
        let (_, rest) = text
            .split_once("\n---\n")
            .ok_or_else(|| Error::new("IndexError", "list index out of range"))?;
        Ok(rest
            .trim_start_matches(l7r_shared::py_text::is_space)
            .to_owned())
    }
}

/// A page's first non-blank line, stripped, its first 120 characters.
#[must_use]
pub fn title_of(text: &str) -> String {
    lines(text)
        .into_iter()
        .map(strip)
        .find(|x| !x.is_empty())
        .map_or_else(|| "(no text)".to_owned(), |x| first(x, 120))
}

/// A long page in parts of about `limit` estimated tokens (0: [`PART_TOKENS`]) and at most [`PART_CHARS`] characters, cut at a line where
/// one falls.
#[must_use]
pub fn split(text: &str, limit: usize) -> Vec<String> {
    let limit = if limit == 0 { PART_TOKENS } else { limit };
    let (mut parts, mut cur, mut n, mut c) = (Vec::new(), String::new(), 0, 0);
    for ln in lines_keep(text) {
        let mut ln = ln.to_owned();
        let mut t = tokens(&ln);
        if !cur.is_empty() && (n + t > limit || c + chars(&ln) > PART_CHARS) {
            parts.push(std::mem::take(&mut cur));
            (n, c) = (0, 0);
        }
        // one enormous line
        while t > limit || chars(&ln) > PART_CHARS {
            let width = (chars(&ln) * limit / t.max(1)).clamp(1, PART_CHARS);
            let at = ln.char_indices().nth(width).map_or(ln.len(), |(i, _)| i);
            parts.push(ln[..at].to_owned());
            ln = ln[at..].to_owned();
            t = tokens(&ln);
        }
        cur.push_str(&ln);
        (n, c) = (n + t, c + chars(&ln));
    }
    if !cur.is_empty() {
        parts.push(cur);
    }
    parts
}

/// A page and its text.
pub type Page = (String, String);

/// Pages into bundles: each closes at [`BUNDLE_CHARS`] or [`BUNDLE_TOKENS`]; a page over either goes alone.
#[must_use]
pub fn groups(pages: Vec<Page>) -> Vec<Vec<Page>> {
    let (mut out, mut cur, mut chars_in, mut toks) = (Vec::new(), Vec::new(), 0, 0);
    for (url, text) in pages {
        let (c, t) = (chars(&text), tokens(&text));
        if c > BUNDLE_CHARS || t > BUNDLE_TOKENS {
            out.push(vec![(url, text)]);
            continue;
        }
        if !cur.is_empty() && (chars_in + c > BUNDLE_CHARS || toks + t > BUNDLE_TOKENS) {
            out.push(std::mem::take(&mut cur));
            (chars_in, toks) = (0, 0);
        }
        cur.push((url, text));
        (chars_in, toks) = (chars_in + c, toks + t);
    }
    if !cur.is_empty() {
        out.push(cur);
    }
    out
}

/// `f"{n:,}"`.
#[must_use]
pub fn commas(n: usize) -> String {
    let digits = n.to_string();
    let mut out = String::new();
    for (i, d) in digits.chars().enumerate() {
        if i > 0 && (digits.len() - i) % 3 == 0 {
            out.push(',');
        }
        out.push(d);
    }
    out
}

/// A filter bundle's manifest head.
#[must_use]
pub fn manifest_head(name: &str, n: usize) -> String {
    format!(
        "# source-filter bundle {name}\n\n{n} page(s). Read EVERY file listed below, whole - a page in parts is every part - and judge each \
         page as your contract\nsays. Write `verdicts.jsonl` in THIS directory, one JSON line per id, then reply with one count line.\n\n"
    )
}

/// A draft bundle's manifest head.
#[must_use]
pub fn draft_head(name: &str, n: usize) -> String {
    format!(
        "# write-up draft bundle {name}\n\n{n} kept page(s). Read CONTRACT.md, then EVERY file listed below, whole - a page in parts is \
         every part - and draft each\npage's registry write-up as the contract says. Write `entries.jsonl` in THIS directory, one JSON line \
         per id, then reply\nwith one count line.\n\n"
    )
}

/// One page of a bundle: its id, URL and text.
pub type Item = (String, String, String);

/// A bundle written: each page's text in its own files, the MANIFEST naming them, the contract beside them.
///
/// # Errors
/// The contract, or a write.
pub fn write_bundle(d: &Path, pages: &[Item], contracts: &Contracts) -> Result<()> {
    mkdir(d)?;
    write_text(&d.join("CONTRACT.md"), &contracts.body()?)?;
    let mut body = manifest_head(&name_of(d), pages.len());
    let mut ids = Map::new();
    for (pid, url, text) in pages {
        let parts = split(text, 0);
        let names: Vec<String> = if parts.len() == 1 {
            vec![format!("{pid}.txt")]
        } else {
            (1..=parts.len())
                .map(|k| format!("{pid}.part{k}.txt"))
                .collect()
        };
        for (name, part) in names.iter().zip(&parts) {
            write_text(&d.join(name), part)?;
        }
        let _ = write!(
            body,
            "## {pid}\n\n- url: {url}\n- title: {}\n- size: {} characters, about {} tokens\n- files: {}\n\n",
            title_of(text),
            commas(chars(text)),
            commas(tokens(text)),
            names.join(", ")
        );
        ids.insert(pid.clone(), json!(url));
    }
    write_text(&d.join("MANIFEST.md"), &body)?;
    write_text(
        &d.join("ids.json"),
        &dumps(&Value::Object(ids), Some(1), false),
    )
}

/// `urlsplit(url).netloc`, or its `ValueError`.
fn netloc(url: &str) -> Result<String> {
    l7r_gate_research::verbatim::fetch::urlsplit(url)
        .map(|p| p[1].clone())
        .map_err(|e| Error::new("ValueError", e))
}

/// The set's pages with saved text as filter bundles under `out`, numbered from `start`, the pages by host; returns each bundle's directory.
///
/// # Errors
/// The cache, a URL that will not split, a bundle's write.
pub fn bundle(
    root: &Path,
    urls: &[String],
    out: &Path,
    start: i64,
    contracts: &Contracts,
) -> Result<Vec<PathBuf>> {
    let home = consulted::home(root);
    let mut pages = Vec::new();
    for u in urls {
        if let Some(t) = text_of(&home, u)?.filter(|t| !strip(t).is_empty()) {
            pages.push((netloc(u)?, u.clone(), t));
        }
    }
    pages.sort_by(|a, b| (&a.0, &a.1).cmp(&(&b.0, &b.1)));
    let (mut dirs, mut n) = (Vec::new(), 0);
    for (k, group) in (start..).zip(groups(pages.into_iter().map(|(_, u, t)| (u, t)).collect())) {
        let d = out.join(format!("312-filter-{}", padded(k, 4)));
        let items: Vec<Item> = group
            .into_iter()
            .map(|(url, text)| {
                n += 1;
                (format!("p{}", padded(n, 5)), url, text)
            })
            .collect();
        write_bundle(&d, &items, contracts)?;
        dirs.push(d);
    }
    Ok(dirs)
}

/// `f"{k:0{w}d}"`: a number zero-padded to `w` digits, its sign first.
#[must_use]
pub fn padded(k: i64, w: usize) -> String {
    if k < 0 {
        format!(
            "-{:0>width$}",
            k.unsigned_abs(),
            width = w.saturating_sub(1)
        )
    } else {
        format!("{k:0w$}")
    }
}

/// The bundle's verdicts by id, and every problem with them (FR-008's shape).
pub type Verdicts = (Vec<(String, Value)>, Vec<String>);

fn ids_of(d: &Path) -> Result<Map<String, Value>> {
    match loads(&read_text(&d.join("ids.json"))?)? {
        Value::Object(m) => Ok(m),
        other => Err(Error::new(
            "TypeError",
            format!(
                "argument of type '{}' is not a container or iterable",
                l7r_shared::blocked::type_name(&other)
            ),
        )),
    }
}

/// The bundle's verdicts by id (a later line for an id replacing an earlier), and every problem with them (FR-008's shape).
///
/// # Errors
/// The ids, a line that is no mapping, a reason list that is not one.
pub fn read_verdicts(d: &Path) -> Result<Verdicts> {
    let ids = ids_of(d)?;
    let path = d.join("verdicts.jsonl");
    let text = if path.is_file() {
        read_text(&path)?
    } else {
        String::new()
    };
    let mut got: Vec<(String, Value)> = Vec::new();
    let mut problems = Vec::new();
    for raw in lines(&text) {
        if strip(raw).is_empty() {
            continue;
        }
        let Ok(v) = loads(raw) else {
            problems.push(format!("not JSON: {}", first(raw, 80)));
            continue;
        };
        let pid = crate::lists::get(&v, "id")?
            .cloned()
            .unwrap_or_else(|| json!(""));
        let verdict = v.get("verdict");
        let reasons = v.get("reasons");
        let key = match &pid {
            Value::String(s) if ids.contains_key(s) => s.clone(),
            Value::Array(_) | Value::Object(_) => {
                return Err(Error::new(
                    "TypeError",
                    format!(
                        "cannot use '{t}' as a dict key (unhashable type: '{t}')",
                        t = l7r_shared::blocked::type_name(&pid)
                    ),
                ));
            }
            _ => {
                problems.push(format!("{} is not an id of this bundle", value_repr(&pid)));
                continue;
            }
        };
        if !matches!(verdict.and_then(Value::as_str), Some("KEEP" | "NOT-KEPT")) {
            problems.push(format!(
                "{key}: verdict {}",
                verdict.map_or_else(|| "None".to_owned(), value_repr)
            ));
            continue;
        }
        if verdict.and_then(Value::as_str) == Some("NOT-KEPT") && !reasons_ok(reasons)? {
            problems.push(format!(
                "{key}: NOT-KEPT needs reasons from {} - got {}",
                REASONS.join(", "),
                reasons.map_or_else(|| "None".to_owned(), value_repr)
            ));
            continue;
        }
        match got.iter_mut().find(|(k, _)| *k == key) {
            Some((_, old)) => *old = v,
            None => got.push((key, v)),
        }
    }
    for pid in ids.keys() {
        if !got.iter().any(|(k, _)| k == pid) {
            problems.push(format!("{pid}: no verdict"));
        }
    }
    Ok((got, problems))
}

/// `not v.get("reasons") or any(r not in REASONS for r in v["reasons"])`, inverted: a list (or a text, read a character at a time, as
/// Python iterates one) of known reasons, at least one.
fn reasons_ok(reasons: Option<&Value>) -> Result<bool> {
    match reasons {
        None | Some(Value::String(_)) => Ok(false),
        Some(r) if !truthy(r) => Ok(false),
        Some(Value::Array(a)) => Ok(a
            .iter()
            .all(|r| r.as_str().is_some_and(|s| REASONS.contains(&s)))),
        Some(Value::Object(m)) => Ok(m.keys().all(|k| REASONS.contains(&k.as_str()))),
        Some(other) => Err(Error::new(
            "TypeError",
            format!(
                "'{}' object is not iterable",
                l7r_shared::blocked::type_name(other)
            ),
        )),
    }
}

fn refused(d: &Path, problems: &[String]) -> Error {
    Error::new(
        "ValueError",
        format!(
            "{}: verdicts refused -\n  {}",
            d.display(),
            problems.join("\n  ")
        ),
    )
}

/// A bundle's verdicts written: the not-kept lines and the kept pages; each domain the agent proposes blocking said on `out`, for the GM
/// (only the GM adds a domain, FR-001). Returns the counts `make uncited DO=apply` prints.
///
/// # Errors
/// A problem with the verdicts (`ValueError`, every one), the ids, the lists.
pub fn apply(root: &Path, d: &Path, out: &mut String) -> Result<Value> {
    let (got, problems) = read_verdicts(d)?;
    if !problems.is_empty() {
        return Err(refused(d, &problems));
    }
    let ids = ids_of(d)?;
    let mut nk = Vec::new();
    let mut keep = Vec::new();
    for (p, v) in &got {
        let url = py_str(&ids[p]);
        if v.get("verdict").and_then(Value::as_str) == Some("NOT-KEPT") {
            let reasons: Vec<String> = v
                .get("reasons")
                .and_then(Value::as_array)
                .into_iter()
                .flatten()
                .map(py_str)
                .collect();
            let note = v
                .get("note")
                .filter(|n| truthy(n))
                .map(py_str)
                .unwrap_or_default();
            nk.push(line(
                &url,
                &reasons,
                "source-filter",
                &first(&note, 200),
                "",
            )?);
        } else {
            keep.push(url);
        }
    }
    not_kept(root, &nk)?;
    kept(root, &keep, "source-filter")?;
    let proposed: BTreeSet<String> = got
        .iter()
        .filter_map(|(_, v)| v.get("propose_block").filter(|b| truthy(b)).map(py_str))
        .collect();
    for dom in &proposed {
        let _ = writeln!(
            out,
            "uncited: {} proposes blocking {dom} - for the GM; only the GM adds a domain (FR-001)",
            name_of(d)
        );
    }
    Ok(json!({"kept": keep.len(), "not-kept": nk.len(), "proposed": proposed.len()}))
}

/// A calibration run against its labels (`answers`: id -> KEEP | NOT-KEPT): per leg, agreed of total.
///
/// # Errors
/// A problem with the verdicts (`ValueError`), a label that is neither, an id with no verdict (`KeyError`).
pub fn score(d: &Path, answers: &Value) -> Result<Value> {
    let (got, problems) = read_verdicts(d)?;
    if !problems.is_empty() {
        return Err(refused(d, &problems));
    }
    let mut legs = [("KEEP", 0, 0), ("NOT-KEPT", 0, 0)];
    let answers = answers.as_object().ok_or_else(|| {
        Error::new(
            "AttributeError",
            format!(
                "'{}' object has no attribute 'items'",
                l7r_shared::blocked::type_name(answers)
            ),
        )
    })?;
    for (pid, want) in answers {
        let want_s = py_str(want);
        let leg = legs
            .iter_mut()
            .find(|(w, _, _)| *w == want_s)
            .ok_or_else(|| Error::new("KeyError", value_repr(want)))?;
        leg.2 += 1;
        let v = got
            .iter()
            .find(|(k, _)| k == pid)
            .ok_or_else(|| Error::new("KeyError", value_repr(&json!(pid))))?;
        if v.1.get("verdict").and_then(Value::as_str) == Some(leg.0) {
            leg.1 += 1;
        }
    }
    Ok(
        json!({"KEEP": {"agreed": legs[0].1, "total": legs[0].2}, "NOT-KEPT": {"agreed": legs[1].1, "total": legs[1].2}}),
    )
}

/// Every tag value with its explanation, from the record's own vocabulary (the source-applicability contract's form).
///
/// # Errors
/// The vocabulary will not load.
pub fn vocabulary_block(root: &Path) -> Result<String> {
    let vocab = l7r_gate_research::record::source_tags::load_vocabulary(
        &crate::base(root).join("research"),
    )?;
    Ok(l7r_gate_research::record::source_tags::contract_block(
        &vocab,
    ))
}

/// The kept pages with no entry yet as draft bundles under `out`, [`DRAFT_PAGES`] a bundle (within the token budget), each with the
/// drafting contract and the keys already taken.
///
/// # Errors
/// The lists, the cache, the contracts, the vocabulary, a write.
pub fn draft_bundles(
    root: &Path,
    out: &Path,
    start: i64,
    contracts: &Contracts,
) -> Result<Vec<PathBuf>> {
    let home = consulted::home(root);
    let done = written(root)?;
    let mut todo = Vec::new();
    for x in read(root, KEPT)? {
        if !done.contains(&field(&x, "url")?) {
            let raw = field(&x, "raw")?;
            if let Some(t) = text_of(&home, &raw)?.filter(|t| !t.is_empty()) {
                todo.push((raw, t));
            }
        }
    }
    let contract = read_text(&contracts.writeup())? + &vocabulary_block(root)? + "\n";
    let taken: Vec<String> = registry_keys(root).into_iter().collect();
    let (mut dirs, mut n, mut k) = (Vec::new(), 0, start);
    for group in groups(todo) {
        for chunk in group.chunks(DRAFT_PAGES) {
            let d = out.join(format!("312-draft-{}", padded(k, 4)));
            let items: Vec<Item> = chunk
                .iter()
                .map(|(url, text)| {
                    n += 1;
                    (format!("p{}", padded(n, 5)), url.clone(), text.clone())
                })
                .collect();
            write_bundle(&d, &items, contracts)?;
            write_text(&d.join("CONTRACT.md"), &contract)?;
            let head = manifest_head(&name_of(&d), items.len());
            let manifest = read_text(&d.join("MANIFEST.md"))?;
            let mut text = draft_head(&name_of(&d), items.len())
                + manifest.get(head.len()..).unwrap_or_default();
            let _ = writeln!(
                text,
                "## Keys already taken - choose none of these\n\n{}",
                taken.join(" ")
            );
            write_text(&d.join("MANIFEST.md"), &text)?;
            dirs.push(d);
            k += 1;
        }
    }
    Ok(dirs)
}

#[cfg(test)]
mod tests;
