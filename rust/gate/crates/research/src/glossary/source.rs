//! The glossary written one word per file and assembled back (`interactive/glossary_source.py`, feature 259; ported by feature 449 T148,
//! `ask:449-phase4-slices`). The GM, 2026-09-20: each word in the glossary the name of its file in the glossary directory, so a check asks
//! a directory listing whether a word is defined and reads one definition, never the whole file.
//!
//! The prefix orders the files (assembling in file order reproduces the committed key order, which keeps `glossary.json` byte for byte);
//! it is gapped by ten and four digits at least, a fifth read, never refused, and sorted by its NUMBER (`10020-` after `1290-`). What this
//! may not do is reformat: `glossary.json` is exactly `json.dumps(obj, ensure_ascii=False, indent=1) + "\n"`.
//!
//! Every path here is under `base`, the Python's `_HERE` (`l7r/diagram/interactive`), and the messages name them as the Python did.

use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{Map, Value};

use crate::{re, Error, Result};

/// The term files, under `base`.
pub const TERMS: &str = "assets/glossary";
/// The gap between two prefixes a new file is named by.
pub const GAP: u64 = 10;
/// The prefix's minimum width.
pub const DIGITS: usize = 4;
/// Where the engine sits in the tree: the Python's `_HERE`.
pub const HERE: &str = "l7r/diagram/interactive";
static NAMED: LazyLock<Regex> = LazyLock::new(|| re(r"^(\d{4,})-(.+)\.json\n?\z"));

fn refused(message: impl Into<String>) -> Error {
    Error::new("GlossaryError", message)
}

/// A file that cannot be read or written: the Python's uncaught `OSError`, whose words no caller binds (`ask:449-usage-text`).
fn io<T>(done: std::io::Result<T>, path: &Path) -> Result<T> {
    done.map_err(|e| Error::new("OSError", format!("{e}: '{}'", path.display())))
}

/// The file read as `open(encoding="utf-8").read()`.
fn read(path: &Path) -> Result<String> {
    io(l7r_gate_core::record::read_text(path), path)
}

fn write(path: &Path, text: &str) -> Result<()> {
    io(std::fs::write(path, text), path)
}

/// `5790-towpath.json`: the term is the name, percent-encoded only where a filename cannot carry a character (`dS/m`).
#[must_use]
pub fn file_name(position: u64, term: &str) -> String {
    format!("{:0DIGITS$}-{}.json", position * GAP, encode(term))
}

fn named(name: &str) -> Option<(String, String)> {
    let c = NAMED.captures(name).ok().flatten()?;
    Some((c[1].to_owned(), c[2].to_owned()))
}

/// The term a filename claims.
///
/// # Errors
/// A name that is not `<prefix>-<term>.json`.
pub fn term_of(name: &str) -> Result<String> {
    named(name).map(|(_, t)| decode(&t)).ok_or_else(|| {
        refused(format!("{name}: not a term file. A term file is <prefix>-<term>.json, the prefix four or more digits counting by ten"))
    })
}

/// The prefix's number, read as Python's `int()` reads any decimal digits.
fn number(prefix: &str) -> u64 {
    crate::record::questions::digits_value(prefix)
}

fn order(name: &str) -> (i128, &str) {
    (
        named(name).map_or(-1, |(p, _)| i128::from(number(&p))),
        name,
    )
}

/// Only what a filename cannot carry, and reversibly: `%` first, so the mapping is one to one; a macron is left as it is.
#[must_use]
pub fn encode(term: &str) -> String {
    term.replace('%', "%25").replace('/', "%2F")
}

#[must_use]
pub fn decode(name: &str) -> String {
    name.replace("%2F", "/").replace("%25", "%")
}

/// The glossary as one entry per term, in the file's own order, each carrying its own term.
///
/// # Errors
/// Text that is not JSON, or JSON that is not an object of objects.
pub fn split(raw: &str) -> Result<Vec<Map<String, Value>>> {
    let data = crate::json(raw).map_err(|e| Error::new("JSONDecodeError", e))?;
    let Value::Object(map) = data else {
        return Err(Error::new(
            "AttributeError",
            "the glossary is an object of terms",
        ));
    };
    map.into_iter()
        .map(|(term, entry)| {
            let Value::Object(fields) = entry else {
                return Err(Error::new("TypeError", "a glossary entry is an object"));
            };
            let mut one = Map::new();
            one.insert("term".into(), Value::String(term));
            for (k, v) in fields {
                one.insert(k, v);
            }
            Ok(one)
        })
        .collect()
}

fn term_text(entry: &Map<String, Value>) -> Result<String> {
    entry
        .get("term")
        .map(l7r_shared::pyjson::py_str)
        .ok_or_else(|| Error::new("KeyError", "'term'"))
}

/// The terms back into the bytes the engine reads.
///
/// # Errors
/// A term two files define, or an entry with no term.
pub fn assemble(terms: &[Map<String, Value>]) -> Result<String> {
    let mut out = Map::new();
    for entry in terms {
        let term = term_text(entry)?;
        if out.contains_key(&term) {
            return Err(refused(format!(
                "`{term}` is defined by two term files - a term has one home"
            )));
        }
        let fields: Map<String, Value> = entry
            .iter()
            .filter(|(k, _)| k.as_str() != "term")
            .map(|(k, v)| (k.clone(), v.clone()))
            .collect();
        out.insert(term, Value::Object(fields));
    }
    Ok(l7r_shared::pyjson::dumps(&Value::Object(out), Some(1), false) + "\n")
}

/// The one-time split: `glossary.json` into one file per term; refuses to leave a split that does not assemble back to the same bytes.
///
/// # Errors
/// The source unreadable or not a glossary, a file it cannot write, or a split that does not assemble back.
pub fn write_term_files(base: &Path) -> Result<Vec<String>> {
    let raw = read(&source_of(base))?;
    let here = base.join(TERMS);
    io(std::fs::create_dir_all(&here), &here)?;
    let mut written = Vec::new();
    for (position, entry) in (1..).zip(split(&raw)?) {
        let name = file_name(position, &term_text(&entry)?);
        let text = l7r_shared::pyjson::dumps(&Value::Object(entry), Some(1), false) + "\n";
        write(&here.join(&name), &text)?;
        written.push(format!("{TERMS}/{name}"));
    }
    let rebuilt = assemble(&term_files(base)?)?;
    if rebuilt != raw {
        return Err(refused(format!(
            "the split does not assemble back to the same bytes ({}) - the term files in {TERMS}/ are wrong and must not be committed",
            first_difference(&raw, &rebuilt)
        )));
    }
    Ok(written)
}

/// Every term file, in prefix order, every refusal checked: a file it does not recognize is a refusal, never a skip.
///
/// # Errors
/// No term directory, a stray file, two files on one prefix, a file whose name and content disagree, or one that is not JSON.
pub fn term_files(base: &Path) -> Result<Vec<Map<String, Value>>> {
    let here = base.join(TERMS);
    if !here.is_dir() {
        return Err(refused(format!(
            "{TERMS}/: no term files - run `make glossary SPLIT=1`"
        )));
    }
    let mut names: Vec<String> = io(std::fs::read_dir(&here), &here)?
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .collect();
    names.sort_by(|a, b| order(a).cmp(&order(b)));
    let mut seen: Vec<(u64, String)> = Vec::new();
    let mut out = Vec::new();
    for name in names {
        term_of(&name)?;
        let at = named(&name).map_or(0, |(p, _)| number(&p));
        if let Some((_, first)) = seen.iter().find(|(p, _)| *p == at) {
            return Err(refused(format!("{TERMS}/: {first} and {name} both claim prefix {at:0DIGITS$} - the assembly will not choose between them")));
        }
        seen.push((at, name.clone()));
        let path = here.join(&name);
        let entry = crate::json(&read(&path)?).map_err(|e| Error::new("JSONDecodeError", e))?;
        let Value::Object(entry) = entry else {
            return Err(Error::new(
                "AttributeError",
                format!(
                    "'{}' object has no attribute 'get'",
                    l7r_shared::blocked::type_name(&entry)
                ),
            ));
        };
        // COMPARED IN THE ENCODE DIRECTION (the plan review of feature 259): decoding a filename is not injective once a term holds a `%`
        let said = entry
            .get("term")
            .map_or_else(|| "None".to_owned(), l7r_shared::pyjson::py_str);
        if name != format!("{at:0DIGITS$}-{}.json", encode(&said)) {
            return Err(refused(format!("{TERMS}/{name}: its filename says `{}` and its content says `{said}` - one of the two is wrong", term_of(&name)?)));
        }
        out.push(entry);
    }
    Ok(out)
}

/// The committed files that differ from what the term files assemble; none before the split has landed.
///
/// # Errors
/// [`term_files`]'s, or the committed glossary unreadable.
pub fn check(base: &Path) -> Result<Vec<String>> {
    if !base.join(TERMS).is_dir() {
        return Ok(Vec::new());
    }
    let committed = read(&source_of(base))?;
    let terms = term_files(base)?;
    let mut stale = Vec::new();
    if committed != assemble(&terms)? {
        stale.push("assets/glossary.json".to_owned());
    }
    let index = index_path(base);
    if read(&index).ok() != Some(variant_index(&terms)?) {
        stale.push(relpath(&index, base));
    }
    Ok(stale)
}

/// Every variant and the term that owns it, one tab-separated line each in the variant's order: the one small derived file that answers
/// "is this word already defined, and by which term?" (22,564 bytes against 30,820 as `indent=1` JSON).
///
/// # Errors
/// An entry with no variants or term, or a variant that is not text.
pub fn variant_index(terms: &[Map<String, Value>]) -> Result<String> {
    let mut out: Map<String, Value> = Map::new();
    for entry in terms {
        let Some(Value::Array(variants)) = entry.get("variants") else {
            return Err(Error::new("KeyError", "'variants'"));
        };
        let term = term_text(entry)?;
        for v in variants {
            let v = v
                .as_str()
                .ok_or_else(|| Error::new("AttributeError", "a glossary variant is text"))?;
            out.insert(v.to_lowercase(), Value::String(term.clone()));
        }
    }
    let mut rows: Vec<(&String, &Value)> = out.iter().collect();
    rows.sort_by(|a, b| a.0.cmp(b.0));
    Ok(rows
        .into_iter()
        .map(|(v, t)| format!("{v}\t{}\n", t.as_str().unwrap_or_default()))
        .collect::<Vec<String>>()
        .concat())
}

/// Beside the derived script the record's pages load: `research/assets/glossary-variants.txt`, three levels above `base`.
#[must_use]
pub fn index_path(base: &Path) -> PathBuf {
    normpath(&base.join("../../../research/assets/glossary-variants.txt"))
}

/// Write the variant index; 1 if it changed, 0 if it was already right.
///
/// # Errors
/// [`term_files`]'s, or a file it cannot write.
pub fn write_index(base: &Path) -> Result<u8> {
    let want = variant_index(&term_files(base)?)?;
    let path = index_path(base);
    if read(&path).ok().as_ref() == Some(&want) {
        return Ok(0);
    }
    write(&path, &want)?;
    Ok(1)
}

/// Write `glossary.json` from the term files; 1 if it changed, 0 if it was already right.
///
/// # Errors
/// [`term_files`]'s, the committed file unreadable, or a file it cannot write.
pub fn write_source(base: &Path) -> Result<u8> {
    let want = assemble(&term_files(base)?)?;
    let path = source_of(base);
    if read(&path)? == want {
        return Ok(0);
    }
    write(&path, &want)?;
    Ok(1)
}

fn source_of(base: &Path) -> PathBuf {
    base.join("assets/glossary.json")
}

/// `os.path.normpath` of an absolute or relative path: `.` dropped, `..` taken back over the part before it.
fn normpath(p: &Path) -> PathBuf {
    let mut out: Vec<std::path::Component> = Vec::new();
    for c in p.components() {
        match c {
            std::path::Component::CurDir => {}
            std::path::Component::ParentDir
                if matches!(out.last(), Some(std::path::Component::Normal(_))) =>
            {
                out.pop();
            }
            std::path::Component::ParentDir
                if matches!(out.last(), Some(std::path::Component::RootDir)) => {}
            other => out.push(other),
        }
    }
    out.iter().collect()
}

/// `os.path.relpath(path, start)` of two paths under one root.
fn relpath(path: &Path, start: &Path) -> String {
    let (a, b) = (normpath(&absolute(path)), normpath(&absolute(start)));
    let (pa, pb): (Vec<_>, Vec<_>) = (a.components().collect(), b.components().collect());
    let common = pa.iter().zip(&pb).take_while(|(x, y)| x == y).count();
    let mut parts: Vec<String> = vec!["..".to_owned(); pb.len() - common];
    parts.extend(
        pa[common..]
            .iter()
            .map(|c| c.as_os_str().to_string_lossy().into_owned()),
    );
    if parts.is_empty() {
        ".".to_owned()
    } else {
        parts.join("/")
    }
}

fn absolute(p: &Path) -> PathBuf {
    if p.is_absolute() {
        p.to_path_buf()
    } else {
        std::env::current_dir().unwrap_or_default().join(p)
    }
}

fn first_difference(want: &str, got: &str) -> String {
    let (w, g): (Vec<char>, Vec<char>) = (want.chars().collect(), got.chars().collect());
    for (at, (a, b)) in w.iter().zip(&g).enumerate() {
        if a != b {
            let cut = |s: &[char]| -> String { s[at..(at + 40).min(s.len())].iter().collect() };
            return format!(
                "first difference at character {at}: {} against {}",
                l7r_shared::py_text::repr(&cut(&w)),
                l7r_shared::py_text::repr(&cut(&g))
            );
        }
    }
    format!("one is {} characters and the other {}", w.len(), g.len())
}

#[cfg(test)]
mod tests;
