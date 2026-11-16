//! Which translated quotations owe a `translation-check` (from `translation_owed.py`, feature 449 T87): every (translation, original) pair now against every pair at the merge base. The pairs and the glosses are read by the `research` crate's ports of `quote_verbatim` and `style_prepass`, in process since feature 449 T145 (by command before, the T065 clause), only for a notes file whose parse is not already kept; a parse is kept by the content it read in `translation-pairs.json`, as the Python kept it, measured to spare that reader on an unchanged record.

use std::collections::{HashMap, HashSet};
use std::path::Path;

use l7r_guard::shared::py_text::split;
use l7r_guard::shared::pyjson;
use l7r_guard::shared::sha1;
use serde_json::{json, Map, Value};

use super::args::{parse, Spec};
use super::delta::Delta;
use super::leaves::fragments_for;
use super::repo::{read_universal, Fail};
use super::units::{pairs_of, restored, NOTE, ORIG_STORED};
use crate::Reply;

const RECORD: &str = "research";
const GLOSS_KEY: &str = "a term's gloss";
/// Bumped where the parse changes in a way its sources below do not show (a dependency's own update), so every kept parse is redone.
const CACHE_VERSION: &str = "rust-translation-pairs-2";
/// THE PARSER'S OWN TEXT (feature 449 T145): the passages and the glosses are read in process by the `research` crate's `verbatim` and
/// `style`, so a kept parse is keyed by those modules' source as built into this binary, where it was keyed by the two `.py` files' bytes
/// read off the tree - an edit of the parser invalidates every kept parse with no constant to remember, and the tree is not read for it.
const PARSER_SOURCES: [&str; 3] = [
    include_str!("../../../research/src/verbatim.rs"),
    include_str!("../../../research/src/style.rs"),
    include_str!("../../../research/src/pyre.rs"),
];

/// (notes file, key, language, translation, original).
pub type Row = (String, String, String, String, String);
type Where = (String, String, String, String);
/// A (translation, original) pair and where it stands.
type Pairs = ((String, String), Vec<Where>);
/// A file of the record, read now or at a revision.
type Reader = dyn FnMut(&str) -> Result<String, Fail>;

fn usage(line: &str) -> Reply {
    Reply {
        stdout: String::new(),
        stderr: format!("{line}\n"),
        code: 2,
    }
}

fn notes_files(names: &[String]) -> Vec<String> {
    let mut out: Vec<String> = names
        .iter()
        .filter(|n| {
            n.starts_with(&format!("{RECORD}/"))
                && n.as_bytes().ends_with(b".notes.html")
                && !n.contains("/citations/")
        })
        .cloned()
        .collect();
    out.sort();
    out
}

fn cache_path(delta: &mut Delta) -> std::path::PathBuf {
    delta
        .git_dir()
        .join("record-checks")
        .join("translation-pairs.json")
}

fn parser_key() -> String {
    let mut bytes = CACHE_VERSION.as_bytes().to_vec();
    for source in PARSER_SOURCES {
        bytes.extend(source.as_bytes());
    }
    sha1::hex(&bytes).chars().take(12).collect()
}

fn walk_notes(dir: &Path, rel: &str, out: &mut Vec<String>) {
    for entry in std::fs::read_dir(dir).into_iter().flatten().flatten() {
        let name = entry.file_name().to_string_lossy().into_owned();
        let sub = format!("{rel}/{name}");
        let path = entry.path();
        if path.is_dir() {
            walk_notes(&path, &sub, out);
        } else if name.as_bytes().ends_with(b".notes.html") {
            out.push(sub);
        }
    }
}

/// Every file of the record's notes, with its originals and its page, at `rev` (None: the tree).
fn record_files(
    delta: &mut Delta,
    rev: Option<&str>,
) -> Result<Vec<(String, String, String, String)>, Fail> {
    let root = delta.root().to_path_buf();
    let mut read: Box<Reader>;
    let names: Vec<String> = if let Some(rev) = rev {
        let listing = delta.listing(rev, &["research/questions"]);
        let found: Vec<String> = split(&listing)
            .into_iter()
            .filter(|n| n.as_bytes().ends_with(b".html"))
            .map(str::to_owned)
            .collect();
        let texts: HashMap<String, String> = found
            .iter()
            .cloned()
            .zip(delta.texts(rev, &found))
            .collect();
        read = Box::new(move |f| Ok(texts.get(f).cloned().unwrap_or_default()));
        found
    } else {
        let mut found = Vec::new();
        walk_notes(&root.join(RECORD), RECORD, &mut found);
        read = Box::new(move |f| Ok(read_universal(&root.join(f))?.unwrap_or_default()));
        found
    };
    let mut out = Vec::new();
    for f in notes_files(&names) {
        let stem = f.strip_suffix(".notes.html").unwrap_or(&f);
        out.push((
            f.clone(),
            read(&f)?,
            read(&format!("{stem}.originals.html"))?,
            read(&format!("{stem}.html"))?,
        ));
    }
    Ok(out)
}

/// The content key of one notes file's parse.
fn parse_key(parser: &str, notes: &str, originals: &str, page: &str) -> String {
    sha1::hex([parser, notes, originals, page].join("\x00").as_bytes())
}

/// Each notes file's translated passages and its page's and notes' glosses, `[[key, language, translation, original], ...]` then
/// `[[characters, reading, meaning], ...]` (what `translation_owed.py`'s reader printed by command until feature 449 T145).
fn parse_uncached(items: &[Value]) -> Vec<Value> {
    use l7r_gate_research::{
        style::glosses,
        verbatim::{passages, strip_markup},
    };
    items
        .iter()
        .map(|it| {
            let mut found = Vec::new();
            for pair in it["notes"].as_array().into_iter().flatten() {
                let (key, body) = (text_field(pair, 0), text_field(pair, 1));
                for p in passages(&strip_markup(&body)) {
                    if !p.original.is_empty() {
                        let mut original = vec![p.original.clone()];
                        original.extend(p.more.clone().unwrap_or_default());
                        found.push(json!([key, p.language, p.quote, original.join(" ... ")]));
                    }
                }
            }
            let text = |k: &str| it[k].as_str().unwrap_or("").to_owned();
            let gl: Vec<Value> = glosses(&text("page"))
                .into_iter()
                .chain(glosses(&text("text")))
                .map(|(c, r, m)| json!([c, r, m]))
                .collect();
            json!([found, gl])
        })
        .collect()
}

fn load_cache(path: &Path) -> Map<String, Value> {
    std::fs::read_to_string(path)
        .ok()
        .and_then(|t| serde_json::from_str::<Value>(&t).ok())
        .and_then(|v| v.as_object().cloned())
        .unwrap_or_default()
}

fn save_cache(path: &Path, cache: &Map<String, Value>) {
    if let Some(dir) = path.parent() {
        let _ = std::fs::create_dir_all(dir);
    }
    let _ = std::fs::write(
        path,
        pyjson::dumps(&Value::Object(cache.clone()), None, false),
    );
}

fn text_field(v: &Value, i: usize) -> String {
    v.get(i).and_then(Value::as_str).unwrap_or("").to_owned()
}

/// {(translation, original): [(notes file, key, language, translation)]} across the record at `rev` (None: the tree), in insertion order.
fn record_pairs(
    delta: &mut Delta,
    rev: Option<&str>,
    parser: &str,
    cache: &mut Map<String, Value>,
) -> Result<Vec<Pairs>, Fail> {
    let files = record_files(delta, rev)?;
    let (mut keys, mut missing, mut items) =
        (Vec::with_capacity(files.len()), HashSet::new(), Vec::new());
    for (_, notes, originals, page) in &files {
        let key = parse_key(parser, notes, originals, page);
        if !cache.contains_key(&key) && missing.insert(key.clone()) {
            let table: HashMap<String, String> =
                pairs_of(&ORIG_STORED, originals).into_iter().collect();
            let bodies: Vec<(String, String)> = pairs_of(&NOTE, &restored(notes, &table));
            items.push((
                key.clone(),
                json!({"notes": bodies, "page": page, "text": notes}),
            ));
        }
        keys.push(key);
    }
    let parsed = parse_uncached(&items.iter().map(|(_, v)| v.clone()).collect::<Vec<_>>());
    for ((key, _), value) in items.into_iter().zip(parsed) {
        cache.insert(key, value);
    }
    let mut order: Vec<(String, String)> = Vec::new();
    let mut out: HashMap<(String, String), Vec<Where>> = HashMap::new();
    let mut push = |key: (String, String), row: Where| {
        out.entry(key.clone())
            .or_insert_with(|| {
                order.push(key);
                Vec::new()
            })
            .push(row);
    };
    for ((f, ..), key) in files.iter().zip(&keys) {
        let entry = cache.get(key).cloned().unwrap_or(Value::Null);
        for row in entry.get(0).and_then(Value::as_array).into_iter().flatten() {
            let (k, lang, quote, original) = (
                text_field(row, 0),
                text_field(row, 1),
                text_field(row, 2),
                text_field(row, 3),
            );
            push((quote.clone(), original), (f.clone(), k, lang, quote));
        }
        for g in entry.get(1).and_then(Value::as_array).into_iter().flatten() {
            let (chars, reading, meaning) = (text_field(g, 0), text_field(g, 1), text_field(g, 2));
            push(
                (format!("{meaning} (read {reading})"), chars),
                (f.clone(), GLOSS_KEY.to_owned(), String::new(), meaning),
            );
        }
    }
    Ok(order
        .into_iter()
        .map(|k| {
            let v = out.remove(&k).unwrap_or_default();
            (k, v)
        })
        .collect())
}

/// (notes file, key, language, translation, original) for each pair now that the merge base does not hold.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn owed(root: &Path) -> Result<Vec<Row>, Fail> {
    owed_in(&mut Delta::new(root))
}

/// [`owed`], on one computation's reads.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn owed_in(delta: &mut Delta) -> Result<Vec<Row>, Fail> {
    let base = delta.translation_base();
    let parser = parser_key();
    let path = cache_path(delta);
    let mut cache = load_cache(&path);
    let size = cache.len();
    let then: HashSet<(String, String)> = if base.is_empty() {
        HashSet::new()
    } else {
        record_pairs(delta, Some(&base), &parser, &mut cache)?
            .into_iter()
            .map(|(k, _)| k)
            .collect()
    };
    let now = record_pairs(delta, None, &parser, &mut cache)?;
    if cache.len() != size {
        save_cache(&path, &cache);
    }
    let mut rows: Vec<Row> = now
        .into_iter()
        .filter(|(k, _)| !then.contains(k))
        .map(|((q, o), w)| (w[0].0.clone(), w[0].1.clone(), w[0].2.clone(), q, o))
        .collect();
    rows.sort();
    Ok(rows)
}

/// FAILURE PARITY ON A ROOT THAT IS NO DIRECTORY (feature 449 T145, the coordinator's ruling on the T145 report): the Python's first
/// `git` ran with `cwd=root`, so `subprocess` raised before anything was read - `FileNotFoundError` where nothing is there,
/// `NotADirectoryError` on a file - exit 1, nothing on stdout. Its last line is kept; the traceback's text is not bound
/// (`ask:449-usage-text`).
fn no_directory(root: &Path) -> Option<String> {
    let shown = l7r_guard::shared::py_text::repr(&root.to_string_lossy());
    match std::fs::metadata(root) {
        Ok(m) if m.is_dir() => None,
        Ok(_) => Some(format!(
            "NotADirectoryError: [Errno 20] Not a directory: PosixPath({shown})\n"
        )),
        Err(_) => Some(format!(
            "FileNotFoundError: [Errno 2] No such file or directory: PosixPath({shown})\n"
        )),
    }
}

fn report(rows: &[Row]) -> String {
    let mut lines = vec![format!("translation-owed: {} translated quotation(s) new or changed since the merge base - each owes a translation-check", rows.len())];
    for (f, key, lang, quote, original) in rows {
        lines.push(format!("== {f} - `{key}` ({lang})"));
        lines.push(format!("  TRANSLATION: {quote}"));
        lines.push(format!("  ORIGINAL:    {original}"));
    }
    lines.join("\n") + "\n"
}

/// `record translation-owed [--root DIR] [--q QUESTIONS]`.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let flags = [Spec::value("--root"), Spec::value("--q")];
    let parsed = match parse(args, &flags) {
        Ok(p) => p,
        Err(complaint) => {
            return usage(&format!(
                "usage: l7r-gate record translation-owed: {complaint}"
            ))
        }
    };
    let root = l7r_gate_research::resolve(Path::new(parsed.text("--root", ".")));
    if let Some(why) = no_directory(&root) {
        return Reply {
            stdout: String::new(),
            stderr: why,
            code: 1,
        };
    }
    let mut rows = match owed(&root) {
        Ok(rows) => rows,
        Err(why) => {
            return Reply {
                stdout: String::new(),
                stderr: why + "\n",
                code: 1,
            }
        }
    };
    let q = parsed.text("--q", "");
    if !q.is_empty() {
        let mine: HashSet<String> = fragments_for(q, &root)
            .into_iter()
            .filter(|r| r.as_bytes().ends_with(b".notes.html"))
            .collect();
        rows.retain(|r| mine.contains(&r.0));
    }
    Reply {
        stdout: report(&rows),
        stderr: String::new(),
        code: 0,
    }
}

#[cfg(test)]
mod tests;
