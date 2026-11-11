//! The claims INDEX and what a tree owes it (`scripts/record/claims.py`'s rows and fingerprints and `claims_owed.py`, ported by feature
//! 449 T82): each claim of each unit in scope, its code and research fingerprints, the committed index (`dev/claims-index.json`), the page
//! snapshots (`dev/claims-pages.json`), and which claims a change owes a check, and why.

use std::collections::{BTreeMap, HashMap, HashSet};
use std::path::Path;
use std::rc::Rc;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::checks::pages::read_page;
use l7r_guard::shared::pyjson::{dumps, sorted};
use l7r_guard::shared::sha256;
use serde_json::{Map, Value};

use super::grammar::Claim;
use super::scope::{all_units, Reader};
use super::units::{lstripped, Unit};
use crate::record::repo::{fail, Fail};
use crate::record::units::{digest, re};

pub const INDEX: &str = "dev/claims-index.json";
pub const DEFERRED: &str = "dev/claims-deferred.json";
pub const STORE: &str = "dev/claims-pages.json";
pub const QUESTIONS: &str = "research/questions";
pub const SECTION_TRIAGE: &str = "section triage";
pub const CODE_TRIAGE: &str = "code triage";
pub const TRIAGED: [&str; 3] = ["triage", SECTION_TRIAGE, CODE_TRIAGE];

/// The index's rows, in the order they were read or written.
pub type Index = Map<String, Value>;
/// The page snapshots: a findings digest -> its blocks' digests.
pub type Store = Map<String, Value>;

/// One claim as the tree holds it now: its key, the unit, the claim, and its fingerprints.
#[derive(Clone, Debug)]
pub struct Row {
    pub key: String,
    pub unit: Rc<Unit>,
    pub claim: Claim,
    pub code: String,
    pub research: String,
}

impl Row {
    pub fn uid(&self) -> String {
        self.unit.uid()
    }
}

/// key -> Row, in the Python dict's order: a key set again keeps its place.
#[derive(Default, Debug)]
pub struct Cur {
    rows: Vec<Row>,
    at: HashMap<String, usize>,
}

impl Cur {
    pub fn insert(&mut self, row: Row) {
        if let Some(&i) = self.at.get(&row.key) {
            self.rows[i] = row;
        } else {
            self.at.insert(row.key.clone(), self.rows.len());
            self.rows.push(row);
        }
    }

    pub fn get(&self, key: &str) -> Option<&Row> {
        self.at.get(key).map(|&i| &self.rows[i])
    }

    pub fn contains(&self, key: &str) -> bool {
        self.at.contains_key(key)
    }

    pub fn iter(&self) -> impl Iterator<Item = &Row> {
        self.rows.iter()
    }

    pub fn len(&self) -> usize {
        self.rows.len()
    }

    /// The rows by key, sorted.
    pub fn sorted(&self) -> Vec<&Row> {
        let mut v: Vec<&Row> = self.rows.iter().collect();
        v.sort_by(|a, b| a.key.cmp(&b.key));
        v
    }

    /// Every unit's uid.
    pub fn uids(&self) -> HashSet<String> {
        self.rows.iter().map(Row::uid).collect()
    }
}

/// Python's truth of a JSON value.
pub fn truthy(v: Option<&Value>) -> bool {
    match v {
        None | Some(Value::Null) => false,
        Some(Value::Bool(b)) => *b,
        Some(Value::Number(n)) => n.as_f64().is_some_and(|f| f != 0.0),
        Some(Value::String(s)) => !s.is_empty(),
        Some(Value::Array(a)) => !a.is_empty(),
        Some(Value::Object(o)) => !o.is_empty(),
    }
}

/// `row.get(key) == text`.
pub fn is(row: &Value, key: &str, text: &str) -> bool {
    row.get(key).and_then(Value::as_str) == Some(text)
}

/// `row.get(key, "")` as text (a non-string as its JSON).
pub fn field<'a>(row: &'a Value, key: &str) -> &'a str {
    row.get(key).and_then(Value::as_str).unwrap_or_default()
}

/// The name a pointer names: `ptr.rsplit("/", 1)[1]`.
pub fn page_name(ptr: &str) -> &str {
    ptr.rsplit_once('/').map_or(ptr, |p| p.1)
}

/// The digest of what a claim is checked against: a question's heading and its non-intro blocks' words.
pub fn findings_of(page_text: &str) -> String {
    let page = read_page(page_text);
    let mut parts: Vec<&str> = vec![&page.heading];
    parts.extend(
        page.blocks
            .iter()
            .filter(|b| !b.intro)
            .map(|b| b.words.as_str()),
    );
    digest(&parts)
}

/// A page's findings digest and its non-intro blocks as (digest, words).
pub type Blocks = (String, Vec<(String, String)>);

/// The pages read in one run, by name, in the order first read.
#[derive(Default)]
pub struct PageMemo {
    pub order: Vec<String>,
    pub pages: HashMap<String, Blocks>,
}

impl PageMemo {
    /// The snapshots of every page read: findings digest -> its blocks' digests.
    pub fn snapshots(&self) -> Store {
        let mut out = Store::new();
        for name in &self.order {
            let (fp, blocks) = &self.pages[name];
            out.insert(
                fp.clone(),
                Value::Array(
                    blocks
                        .iter()
                        .map(|(d, _)| Value::String(d.clone()))
                        .collect(),
                ),
            );
        }
        out
    }
}

/// A cited question's findings digest and its non-intro blocks, read once a run; a missing file is `missing` with no blocks.
pub fn page_blocks<'a>(
    name: &str,
    qdir: &Path,
    memo: &'a mut PageMemo,
) -> Result<&'a Blocks, Fail> {
    if !memo.pages.contains_key(name) {
        let f = qdir.join(name);
        let got = if f.is_file() {
            let text = crate::record::repo::read_text(&f)?;
            let page = read_page(&text);
            (
                findings_of(&text),
                page.blocks
                    .iter()
                    .filter(|b| !b.intro)
                    .map(|b| (digest(&[&b.words]), b.words.clone()))
                    .collect(),
            )
        } else {
            ("missing".to_owned(), Vec::new())
        };
        memo.order.push(name.to_owned());
        memo.pages.insert(name.to_owned(), got);
    }
    Ok(&memo.pages[name])
}

/// The research fingerprint of one claim's pointers (empty for a class claim); a missing file is `missing`.
pub fn research_fp(
    pointers: &[String],
    qdir: &Path,
    memo: &mut HashMap<String, String>,
) -> Result<String, Fail> {
    if pointers.is_empty() {
        return Ok(String::new());
    }
    let mut parts = Vec::new();
    for ptr in pointers {
        let name = page_name(ptr).to_owned();
        if !memo.contains_key(&name) {
            let f = qdir.join(&name);
            let fp = if f.is_file() {
                findings_of(&crate::record::repo::read_text(&f)?)
            } else {
                "missing".to_owned()
            };
            memo.insert(name.clone(), fp);
        }
        parts.push(memo[&name].clone());
    }
    Ok(digest(
        &parts.iter().map(String::as_str).collect::<Vec<_>>(),
    ))
}

/// key -> Row for every claim of every unit in scope at `skill`, its questions under `qdir`.
pub fn current(reader: &mut Reader, skill: &Path, qdir: &Path) -> Result<Cur, Fail> {
    rows_of(all_units(reader, skill, false, true)?, qdir)
}

/// key -> Row for every claim of `pairs`, their research read under `qdir`.
pub fn rows_of(pairs: Vec<super::units::Pair>, qdir: &Path) -> Result<Cur, Fail> {
    let mut memo = HashMap::new();
    let mut out = Cur::default();
    for (unit, _errors) in pairs {
        let unit = Rc::new(unit);
        for claim in &unit.claims {
            out.insert(Row {
                key: unit.key(claim),
                unit: unit.clone(),
                claim: claim.clone(),
                code: unit.code(claim),
                research: research_fp(&claim.pointers, qdir, &mut memo)?,
            });
        }
    }
    Ok(out)
}

/// A JSON file's object, or an empty one where there is no file.
pub fn load_map(path: &Path) -> Result<Map<String, Value>, Fail> {
    if !path.is_file() {
        return Ok(Map::new());
    }
    let text = std::fs::read_to_string(path).map_err(fail)?;
    match serde_json::from_str::<Value>(&text)
        .map_err(|e| format!("json.decoder.JSONDecodeError: {e}"))?
    {
        Value::Object(m) => Ok(m),
        other => Err(format!("{}: not an object: {other}", path.display())),
    }
}

fn write(path: &Path, text: &str) -> Result<(), Fail> {
    std::fs::create_dir_all(path.parent().unwrap_or(Path::new("."))).map_err(fail)?;
    std::fs::write(path, text).map_err(fail)
}

/// The index, sorted, as `json.dumps(indent=1, sort_keys=True, ensure_ascii=False)` writes it.
pub fn save_index(path: &Path, rows: &Index) -> Result<(), Fail> {
    write(
        path,
        &(dumps(&sorted(&Value::Object(rows.clone())), Some(1), false) + "\n"),
    )
}

/// The snapshots, as `json.dumps(indent=0, sort_keys=True)` writes them.
pub fn save_store(path: &Path, store: &Store) -> Result<(), Fail> {
    write(
        path,
        &(dumps(&sorted(&Value::Object(store.clone())), Some(0), true) + "\n"),
    )
}

/// The index rows that still speak of something: a claim in scope, or an UNCLAIMED row whose unit still exists.
pub fn live_rows(cur: &Cur, index: &Index) -> Index {
    let uids = cur.uids();
    index
        .iter()
        .filter(|(k, v)| {
            cur.contains(k)
                || (is(v, "verdict", "UNCLAIMED")
                    && uids.contains(k.rsplit_once('#').map_or(k.as_str(), |p| p.0)))
        })
        .map(|(k, v)| (k.clone(), v.clone()))
        .collect()
}

/// {new key: old key} for every claim of a unit moved to another file with its code intact (405 T53, T58).
pub fn moved(cur: &Cur, index: &Index) -> BTreeMap<String, String> {
    let mut gone: HashMap<&str, Vec<&String>> = HashMap::new();
    for k in index.keys() {
        if !cur.contains(k) {
            if let Some((_, tail)) = k.split_once("::") {
                gone.entry(tail).or_default().push(k);
            }
        }
    }
    let mut out = BTreeMap::new();
    for row in cur.iter() {
        if index.contains_key(&row.key) {
            continue;
        }
        let Some((_, tail)) = row.key.split_once("::") else {
            continue;
        };
        let olds: Vec<&&String> = gone
            .get(tail)
            .into_iter()
            .flatten()
            .filter(|k| is(&index[k.as_str()], "code", &row.code))
            .collect();
        if olds.len() == 1 {
            out.insert(row.key.clone(), (*olds[0]).clone());
        }
    }
    out
}

/// Each moved claim's row carried to its new key and the old one dropped; how many moved.
pub fn rekey(cur: &Cur, index: &mut Index) -> usize {
    let moves = moved(cur, index);
    for (new, old) in &moves {
        let row = index[old].clone();
        index.insert(new.clone(), row);
    }
    for old in moves.values().collect::<HashSet<_>>() {
        index.shift_remove(old);
    }
    moves.len()
}

/// The owed keys `impl-drift` must judge: every owed key but those owed only a triage.
pub fn judged(due: &[(String, String)]) -> Vec<String> {
    due.iter()
        .filter(|(_, why)| !TRIAGED.contains(&why.as_str()))
        .map(|(k, _)| k.clone())
        .collect()
}

static RESEARCH_BLOCK: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?ms)^[ \t]*(?:"""|''')?Research:.*?(?="""|'''|^[ \t]*$)"#));

/// A file's text split on `\n`; None where it cannot be opened (Python's `OSError`), the failure where it is not UTF-8.
fn lines_of(root: &Path, path: &str) -> Result<Option<Vec<String>>, Fail> {
    match std::fs::read(root.join(path)) {
        Err(_) => Ok(None),
        Ok(bytes) => {
            let text = String::from_utf8(bytes).map_err(|e| format!("UnicodeDecodeError: {e}"))?;
            Ok(Some(
                crate::record::repo::universal(&text)
                    .split('\n')
                    .map(str::to_owned)
                    .collect(),
            ))
        }
    }
}

fn at(lines: &[String], i: usize) -> Result<&str, Fail> {
    lines
        .get(i)
        .map(String::as_str)
        .ok_or_else(|| "IndexError: list index out of range".to_owned())
}

fn indent(line: &str) -> usize {
    line.chars().count() - lstripped(line).chars().count()
}

/// (the 1-based line the unit's text starts at, the text): its lines, with the comment block directly above it.
pub fn source_span(root: &Path, unit: &Unit) -> Result<Option<(usize, String)>, Fail> {
    let Some(lines) = lines_of(root, &unit.path)? else {
        return Ok(None);
    };
    let mut start = unit.lineno.saturating_sub(1);
    while start > 0 && lstripped(at(&lines, start - 1)?).starts_with(['#', '@']) {
        start -= 1;
    }
    let mut end = unit.end_lineno;
    if unit.kind == "class" {
        let own = indent(at(&lines, unit.lineno.saturating_sub(1))?);
        for k in unit.lineno..unit.end_lineno {
            let line = at(&lines, k)?;
            let st = lstripped(line);
            if ["def ", "async def ", "class ", "@"]
                .iter()
                .any(|p| st.starts_with(p))
                && indent(line) > own
            {
                end = k;
                break;
            }
        }
    }
    if unit.kind == "constant"
        && end < lines.len()
        && lstripped(&lines[end]).starts_with(['"', '\''])
    {
        while end < lines.len() && !l7r_guard::shared::py_text::strip(&lines[end]).is_empty() {
            end += 1;
        }
    }
    let stop = end.min(lines.len());
    let start_at = start.min(stop);
    Ok(Some((start + 1, lines[start_at..stop].join("\n"))))
}

/// A unit's source with its `Research:` section taken out, fingerprinted; "" where its file cannot be opened.
pub fn body_of(root: &Path, unit: &Unit) -> Result<String, Fail> {
    let Some((_, text)) = source_span(root, unit)? else {
        return Ok(String::new());
    };
    Ok(sha256::hex(RESEARCH_BLOCK.replace_all(&text, "").as_bytes())[..16].to_owned())
}

/// Is a claim whose code fingerprint moved changed in its `Research:` lines alone (the body as last judged)?
pub fn relabeled_only(was: &Value, row: &Row, root: &Path) -> Result<bool, Fail> {
    if !truthy(was.get("body"))
        || was.get("body").and_then(Value::as_str) != Some(&body_of(root, &row.unit)?)
    {
        return Ok(false);
    }
    Ok(is(was, "claim", &row.claim.normalized()) || is(was, "verdict", "MISLABELED"))
}

/// `was.get("claim") not in (None, text)`.
pub fn claim_rewritten(was: &Value, text: &str) -> bool {
    was.get("claim")
        .is_some_and(|c| !c.is_null() && c.as_str() != Some(text))
}

/// A MISLABELED verdict answered by the relabel it prescribed (385 T23, plan D45).
pub fn relabel_answered(was: &Value, row: &Row, root: &Path) -> Result<bool, Fail> {
    Ok(is(was, "verdict", "MISLABELED")
        && claim_rewritten(was, &row.claim.normalized())
        && relabeled_only(was, row, root)?)
}

/// `page:digest` for every block now standing on the questions `pointers` cite.
pub fn standing(
    pointers: &[String],
    qdir: &Path,
    memo: &mut PageMemo,
) -> Result<HashSet<String>, Fail> {
    let mut out = HashSet::new();
    for ptr in pointers {
        let name = page_name(ptr);
        for (d, _) in &page_blocks(name, qdir, memo)?.1 {
            out.insert(format!("{name}:{d}"));
        }
    }
    Ok(out)
}

/// Why a claim whose cited research moved is owed: in full where a block it rested on is gone, its row predates the snapshots or it cites a page its check never read; else the triage.
pub fn research_why(
    row: &Row,
    was: &Value,
    qdir: &Path,
    store: &Store,
    memo: &mut PageMemo,
) -> Result<String, Fail> {
    let Some(pages) = was.get("pages").and_then(Value::as_object) else {
        return Ok("research changed".to_owned());
    };
    let unsnapped = pages
        .values()
        .any(|d| d.as_str().is_none_or(|d| !store.contains_key(d)));
    let unread = row
        .claim
        .pointers
        .iter()
        .any(|p| !pages.contains_key(page_name(p)));
    if unsnapped || unread {
        return Ok("research changed".to_owned());
    }
    if let Some(rests) = was.get("rests").and_then(Value::as_array) {
        let now = standing(&row.claim.pointers, qdir, memo)?;
        if !rests
            .iter()
            .all(|r| r.as_str().is_some_and(|r| now.contains(r)))
        {
            return Ok("rests changed".to_owned());
        }
    }
    Ok("triage".to_owned())
}

/// (key, why) for every claim with no row, whose code moved, or whose research moved.
pub fn owed(
    cur: &Cur,
    index: &Index,
    qdir: Option<&Path>,
    store: Option<&Store>,
) -> Result<Vec<(String, String)>, Fail> {
    let mut out = Vec::new();
    let mut memo = PageMemo::default();
    let moves = moved(cur, index);
    let empty = Store::new();
    for row in cur.sorted() {
        let own = index.get(&row.key);
        let was = if truthy(own) {
            own
        } else {
            index.get(moves.get(&row.key).map_or("", String::as_str))
        };
        let Some(was) = was else {
            out.push((row.key.clone(), "new".to_owned()));
            continue;
        };
        let why = owed_one(row, was, qdir, store.unwrap_or(&empty), &mut memo)?;
        if let Some(why) = why {
            out.push((row.key.clone(), why));
        }
    }
    Ok(out)
}

fn owed_one(
    row: &Row,
    was: &Value,
    qdir: Option<&Path>,
    store: &Store,
    memo: &mut PageMemo,
) -> Result<Option<String>, Fail> {
    let relabeled = |q: &Path| -> Result<bool, Fail> {
        let root = q.parent().and_then(Path::parent).unwrap_or(Path::new(""));
        relabeled_only(was, row, root)
    };
    if !is(was, "code", &row.code) && !qdir.map(relabeled).transpose()?.unwrap_or(false) {
        let text = row.claim.normalized();
        let full =
            is(was, "triage", "touched") || row.unit.line_keyed() || claim_rewritten(was, &text);
        return Ok(Some(
            if full { "code changed" } else { CODE_TRIAGE }.to_owned(),
        ));
    }
    if is(was, "triage", "touched") {
        return Ok(Some("triage touched".to_owned()));
    }
    if row.unit.line_keyed()
        && was.get("section").is_some()
        && was.get("section").and_then(Value::as_str) != Some(&row.unit.core)
    {
        return Ok(Some(SECTION_TRIAGE.to_owned()));
    }
    if was.get("research").and_then(Value::as_str) != Some(&row.research) {
        return Ok(Some(match qdir {
            Some(q) => research_why(row, was, q, store, memo)?,
            None => "research changed".to_owned(),
        }));
    }
    Ok(None)
}

#[cfg(test)]
mod tests;
