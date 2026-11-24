//! The texts a triage shows a claim's removed blocks from (feature 375 T04; a procedure section's, feature 451 T210, T215): each page a
//! recorded snapshot was taken of kept as a git blob in the clone (git's history holds a page's), each section's words in the
//! repository ([`SECTION_WORDS`]), and the words of a block that no longer stands found in the kept text, then the history.

use std::collections::{BTreeMap, HashSet};
use std::path::Path;

use l7r_shared::checks::pages::read_page;
use l7r_shared::pyjson::{dumps, sorted};
use serde_json::{json, Map, Value};

use super::super::index::{field, findings_of, Cur, Index, Store};
use super::super::units::doc_units;
use super::BLOBS;
use crate::record::repo::{fail, git, Fail};
use crate::record::units::digest;

fn blob_map(qdir: &Path) -> Option<std::path::PathBuf> {
    let common = git(
        qdir,
        &["rev-parse", "--path-format=absolute", "--git-common-dir"],
    );
    let common = l7r_shared::py_text::strip(&common);
    (!common.is_empty()).then(|| Path::new(common).join(BLOBS))
}

/// Each page a recorded snapshot was taken of kept as a git blob, while the page still stands at it (feature 375 T04).
pub fn keep_texts(qdir: &Path, units: &Map<String, Value>) -> Result<usize, Fail> {
    let mut pages: BTreeMap<String, String> = BTreeMap::new();
    for u in units.values() {
        for (name, fp) in u
            .get("pages")
            .and_then(Value::as_object)
            .into_iter()
            .flatten()
        {
            pages.insert(name.clone(), fp.as_str().unwrap_or_default().to_owned());
        }
    }
    keep_blobs(qdir, &mut |blobs| {
        let mut texts = Vec::new();
        for (name, fp) in &pages {
            let f = qdir.join(name);
            if blobs.contains_key(fp) || !f.is_file() {
                continue;
            }
            let text = crate::record::repo::read_text(&f)?;
            if findings_of(&text) == *fp {
                texts.push((fp.clone(), text));
            }
        }
        Ok(texts)
    })
}

/// What [`keep_blobs`] is told to keep, given the blob map as it stands: (key, text) pairs.
type Pick<'a> = dyn FnMut(&Map<String, Value>) -> Result<Vec<(String, String)>, Fail> + 'a;

/// Each text `pick` names, from the clone's blob map as it stands, written as a git blob and recorded under its key; how many.
fn keep_blobs(at: &Path, pick: &mut Pick) -> Result<usize, Fail> {
    let Some(path) = blob_map(at) else {
        return Ok(0);
    };
    let mut blobs = super::super::index::load_map(&path)?;
    let mut kept = 0;
    for (key, text) in pick(&blobs)? {
        let sha = crate::claims::stdin_git(at, &["hash-object", "-w", "--stdin"], &text);
        if let Some(sha) = sha {
            blobs.insert(key, json!(l7r_shared::py_text::strip(&sha)));
            kept += 1;
        }
    }
    if kept > 0 {
        std::fs::write(
            &path,
            dumps(&sorted(&Value::Object(blobs)), Some(0), true) + "\n",
        )
        .map_err(fail)?;
    }
    Ok(kept)
}

/// The key a bundle's procedure-section words are written under (feature 451 T210): `{section core: [its blocks]}`, beside its snapshots.
pub const SECTION_TEXTS: &str = "section_texts";

/// The words of every procedure section `keys`' claims sit in, as a bundle reads them: `{its core: [its blocks]}` ([`SECTION_TEXTS`]).
pub fn section_texts(cur: &Cur, keys: &[String]) -> Map<String, Value> {
    let mut out = Map::new();
    for k in keys {
        let unit = &cur.get(k).unwrap_or_else(|| unreachable!()).unit;
        if unit.line_keyed() {
            out.insert(unit.core.clone(), json!(unit.blocks));
        }
    }
    out
}

/// The repository's record of the procedure sections' kept words (feature 451 T215): one line a block, `{"block": its digest, "words":
/// its words}`, sorted by digest, holding every block of every section snapshot the index names. In the repository, not the clone's
/// `.git` (T210 kept them there): they can be the only copy of what was judged - a snapshot of words that never reached a commit - so
/// another clone, or a fresh one, found none and forced the section's claims. One line a block: a regenerated row adds its new block's
/// line and drops its old one, and two clones' lines never conflict (`merge=union` in `.gitattributes`; a line is its block's alone).
pub const SECTION_WORDS: &str = "dev/claims-section-words.jsonl";

/// The kept words of each block [`SECTION_WORDS`] holds, by digest; a line that does not parse, or whose words do not hash to its
/// digest (a hand edit), is not read, so its words are sought in the history.
fn section_blocks(root: &Path) -> BTreeMap<String, String> {
    let text = std::fs::read_to_string(root.join(SECTION_WORDS)).unwrap_or_default();
    text.lines()
        .filter_map(|line| serde_json::from_str::<Value>(line).ok())
        .filter_map(|v| {
            let words = v.get("words")?.as_str()?.to_owned();
            (v.get("block")?.as_str()? == digest(&[&words])).then(|| (digest(&[&words]), words))
        })
        .collect()
}

/// Each procedure section a recorded snapshot was taken of kept by its words, as the bundle read them, in [`SECTION_WORDS`] (feature
/// 451 T210, T215: a snapshot of words that never reached a commit - a generated row edited by hand, then regenerated - left the triage
/// no removed block to show, and it forced every claim of the section); `data` a bundle's `blocks.json` or `triage.json`, `index` and
/// `store` the rows and snapshots as recorded, whose named section snapshots the file is pruned to. How many blocks it holds.
pub fn keep_sections(
    root: &Path,
    data: &Value,
    index: &Index,
    store: &Store,
) -> Result<usize, Fail> {
    let mut blocks = section_blocks(root);
    for words in data
        .get(SECTION_TEXTS)
        .and_then(Value::as_object)
        .into_iter()
        .flat_map(|m| m.values())
        .filter_map(Value::as_array)
        .flatten()
        .filter_map(Value::as_str)
    {
        blocks.insert(digest(&[words]), words.to_owned());
    }
    let named: HashSet<&str> = index
        .values()
        .filter_map(|r| r.get("section").and_then(Value::as_str))
        .filter_map(|core| store.get(core).and_then(Value::as_array))
        .flatten()
        .filter_map(Value::as_str)
        .collect();
    blocks.retain(|d, _| named.contains(d.as_str()));
    let text: String = blocks
        .iter()
        .map(|(d, w)| dumps(&json!({"block": d, "words": w}), None, false) + "\n")
        .collect();
    let path = root.join(SECTION_WORDS);
    if std::fs::read_to_string(&path).ok().as_deref() != Some(text.as_str()) {
        std::fs::write(&path, text).map_err(fail)?;
    }
    Ok(blocks.len())
}

/// The text of the page snapshot `fp`, from the clone's kept blobs, or "".
pub fn kept_text(qdir: &Path, fp: &str) -> Result<String, Fail> {
    let blob = match blob_map(qdir) {
        Some(p) if p.is_file() => {
            field(&Value::Object(super::super::index::load_map(&p)?), fp).to_owned()
        }
        _ => String::new(),
    };
    Ok(if blob.is_empty() {
        String::new()
    } else {
        git(qdir, &["cat-file", "-p", &blob])
    })
}

/// The words of the blocks `digests` of the question `name` that no longer stand: the snapshot's kept text, then the page's history.
pub fn removed_words(
    qdir: &Path,
    name: &str,
    digests: &HashSet<String>,
    snapshot: &str,
) -> Result<BTreeMap<String, String>, Fail> {
    let mut found = BTreeMap::new();
    let mut texts = Vec::new();
    if !snapshot.is_empty() {
        texts.push(kept_text(qdir, snapshot)?);
    }
    for sha in git(qdir, &["log", "--format=%H", "-60", "--", name]).split_whitespace() {
        texts.push(git(qdir, &["show", &format!("{sha}:./{name}")]));
    }
    for text in texts {
        for b in read_page(&text).blocks {
            let d = digest(&[&b.words]);
            if digests.contains(&d) && !b.intro {
                found.entry(d).or_insert(b.words);
            }
        }
        if found.len() == digests.len() {
            break;
        }
    }
    Ok(found)
}

/// The words of the blocks `digests` of the procedure section `title` of `path` that no longer stand: the repository's kept words
/// ([`SECTION_WORDS`], feature 451 T210, T215), then its history.
pub fn section_words(
    root: &Path,
    path: &str,
    title: &str,
    digests: &HashSet<String>,
) -> BTreeMap<String, String> {
    let mut found: BTreeMap<String, String> = section_blocks(root)
        .into_iter()
        .filter(|(d, _)| digests.contains(d))
        .collect();
    if found.len() == digests.len() {
        return found;
    }
    for sha in git(root, &["log", "--format=%H", "-60", "--", path]).split_whitespace() {
        let text = git(root, &["show", &format!("{sha}:{path}")]);
        let units = doc_units(&text, path, None);
        for unit in units.iter().filter(|u| u.qualname == title) {
            for b in &unit.blocks {
                let d = digest(&[b]);
                if digests.contains(&d) {
                    found.entry(d).or_insert_with(|| b.clone());
                }
            }
        }
        if found.len() == digests.len() {
            break;
        }
    }
    found
}
