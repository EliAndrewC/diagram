//! Which translated quotations owe a `translation-check` (from `translation_owed.py`, feature 449 T87): every (translation, original) pair now against every pair at the merge base. The pairs and the glosses are read by Python's `quote_verbatim` and `style_prepass`, both phase 4, by command (the T065 clause), only for a notes file whose parse is not already kept; a parse is kept by the content it read in `translation-pairs.json`, as the Python kept it, measured to spare the Python start and that reader on an unchanged record.

use std::collections::{HashMap, HashSet};
use std::path::Path;

use l7r_guard::shared::py_text::split;
use l7r_guard::shared::pyjson;
use l7r_guard::shared::sha1;
use serde_json::{json, Map, Value};

use super::args::{parse, Spec};
use super::leaves::fragments_for;
use super::repo::{cat_blobs, fail, python, read_universal, tree_of, Fail};
use super::units::{pairs_of, restored, NOTE, ORIG_STORED};
use crate::Reply;

const RECORD: &str = "research";
const GLOSS_KEY: &str = "a term's gloss";
const CACHE_VERSION: &str = "rust-translation-pairs-1";

const READER: &str = r"import json, sys
sys.dont_write_bytecode = True
tree = sys.argv[1]
sys.path[:0] = [tree + '/scripts/record', tree + '/scripts/hooks/lib']
import quote_verbatim as qv, style_prepass as sp
out = []
for it in json.load(sys.stdin):
    found = []
    for key, body in it['notes']:
        for p in qv.passages(qv._strip(body)):
            if p.get('original'):
                found.append([key, p.get('language', ''), p['quote'], ' ... '.join([p['original'], *p.get('more', [])])])
    out.append([found, [list(g) for g in sp.glosses(it['page']) + sp.glosses(it['text'])]])
sys.stdout.write(json.dumps(out))";

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

/// `subprocess.run(["git", *args], cwd=root).stdout`, whatever its exit.
fn git_any(root: &Path, args: &[&str]) -> String {
    std::process::Command::new("git")
        .current_dir(root)
        .args(args)
        .output()
        .map(|o| String::from_utf8_lossy(&o.stdout).into_owned())
        .unwrap_or_default()
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

fn cache_path(root: &Path) -> std::path::PathBuf {
    let common = git_any(root, &["rev-parse", "--git-common-dir"]);
    let common = common.trim();
    let dir = if common.is_empty() {
        root.join(".git")
    } else {
        root.join(common)
    };
    dir.join("record-checks").join("translation-pairs.json")
}

fn parser_key(tree: &Path) -> Result<String, Fail> {
    let mut bytes = CACHE_VERSION.as_bytes().to_vec();
    for rel in [
        "scripts/record/quote_verbatim.py",
        "scripts/record/style_prepass.py",
    ] {
        bytes.extend(std::fs::read(tree.join(rel)).map_err(|e| format!("{rel}: {e}"))?);
    }
    Ok(sha1::hex(&bytes).chars().take(12).collect())
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
    root: &Path,
    rev: Option<&str>,
) -> Result<Vec<(String, String, String, String)>, Fail> {
    let mut read: Box<Reader>;
    let names: Vec<String> = if let Some(rev) = rev {
        let listing = git_any(
            root,
            &[
                "ls-tree",
                "-r",
                "--name-only",
                rev,
                "--",
                "research/questions",
            ],
        );
        let found: Vec<String> = split(&listing)
            .into_iter()
            .filter(|n| n.as_bytes().ends_with(b".html"))
            .map(str::to_owned)
            .collect();
        let objects: Vec<String> = found.iter().map(|n| format!("{rev}:{n}")).collect();
        let texts: HashMap<String, String> = found
            .iter()
            .cloned()
            .zip(cat_blobs(root, &objects))
            .collect();
        read = Box::new(move |f| Ok(texts.get(f).cloned().unwrap_or_default()));
        found
    } else {
        let mut found = Vec::new();
        walk_notes(&root.join(RECORD), RECORD, &mut found);
        let owned = root.to_path_buf();
        read = Box::new(move |f| Ok(read_universal(&owned.join(f))?.unwrap_or_default()));
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

fn parse_uncached(root: &Path, items: &[Value]) -> Result<Vec<Value>, Fail> {
    if items.is_empty() {
        return Ok(Vec::new());
    }
    let tree = tree_of(root);
    let said = python(
        READER,
        &[&tree.to_string_lossy()],
        &serde_json::to_string(items).map_err(fail)?,
    )?;
    serde_json::from_str(&said).map_err(fail)
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
    root: &Path,
    rev: Option<&str>,
    parser: &str,
    cache: &mut Map<String, Value>,
) -> Result<Vec<Pairs>, Fail> {
    let files = record_files(root, rev)?;
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
    let parsed = parse_uncached(
        root,
        &items.iter().map(|(_, v)| v.clone()).collect::<Vec<_>>(),
    )?;
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
    let base = git_any(root, &["merge-base", "HEAD", "origin/main"]);
    let base = base.trim();
    let parser = parser_key(&tree_of(root))?;
    let path = cache_path(root);
    let mut cache = load_cache(&path);
    let size = cache.len();
    let then: HashSet<(String, String)> = if base.is_empty() {
        HashSet::new()
    } else {
        record_pairs(root, Some(base), &parser, &mut cache)?
            .into_iter()
            .map(|(k, _)| k)
            .collect()
    };
    let now = record_pairs(root, None, &parser, &mut cache)?;
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
    let root = std::fs::canonicalize(parsed.text("--root", "."))
        .unwrap_or_else(|_| parsed.text("--root", ".").into());
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
