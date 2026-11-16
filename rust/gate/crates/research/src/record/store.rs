//! The record on disk, read for a reader (`record/store.py`, features 258, 303; ported by feature 449 T144). The QUESTIONS are one stem each
//! in `questions/`, a question page shown with its cross-link and its *Not to be confused with:* list written in (`page_html`) and with its
//! own notes (`page_notes`); the REGISTRY is a page of fragments - `sources/`, its front matter, its groups and their entries - assembled
//! as feature 258 assembled every page. Nothing here guesses: a file it does not recognize is a refusal, never skipped.
//!
//! The Python's `MEMO` (feature 383: a per-file memo the push's record check hands in) is not ported: its one caller, `memo_check.py`, is
//! S5's, and keeps or drops a cache on its own measurement (`ask:449-T81-slices`).

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};

use crate::record::fragments as frag;
use crate::record::notes::{notes_of, Notes};
use crate::record::questions::{self as qs, Page as QPage, Record};
use crate::record::split::{heading_id, Entry, Page, Section};
use crate::record::{absence, assemble, confusables, originals, passages, xref};
use crate::{re, Error, Result};

/// The registry is the one page whose sections hold entries of their own.
pub const REGISTRY: &str = "SOURCES.html";
pub const REGISTRY_DIR: &str = "sources";
pub const ENTRY_LEVEL: usize = 3;
static NOTE_BODY: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?s)(<li data-note="[^"]+">)(.*?)(</li>)"#));

fn refused(message: impl Into<String>) -> Error {
    Error::new("RecordError", message)
}

/// Which heading level is an ENTRY on this page, if any: only the registry has them.
#[must_use]
pub fn entry_level(page_rel: &str) -> Option<usize> {
    (page_rel == REGISTRY).then_some(ENTRY_LEVEL)
}

/// Every question, tagged and homed; a refusal as a `RecordError` naming every file at fault.
///
/// # Errors
/// The questions' or the contents' refusals, as one `RecordError`.
pub fn load(record_dir: &Path) -> Result<Record> {
    qs::load(record_dir).map_err(|e| match e.kind {
        "QuestionError" | "ContentsError" => refused(e.message),
        _ => e,
    })
}

fn read(path: &Path) -> String {
    crate::read(path).unwrap_or_default()
}

/// The names of a directory, in the order the file system lists them, as `os.listdir`.
fn listdir(dir: &Path) -> Vec<String> {
    std::fs::read_dir(dir)
        .map(|d| {
            d.flatten()
                .map(|e| e.file_name().to_string_lossy().into_owned())
                .collect()
        })
        .unwrap_or_default()
}

/// The `Page` the registry's directory of fragments holds, in prefix order, with every refusal checked.
///
/// # Errors
/// No directory, its front or tail missing, a name that is not a fragment's, two fragments on one prefix, an entry whose file and heading
/// disagree, or an entry with no heading id (`ValueError`, the splitter's).
pub fn read_fragments(page_rel: &str, record_dir: &Path) -> Result<Page> {
    let place = frag::page_dir(page_rel);
    let root = record_dir.join(&place);
    if !root.is_dir() {
        return Err(refused(format!(
            "{place}/: no fragment directory for {page_rel}"
        )));
    }
    let names = listdir(&root);
    let missing: Vec<&str> = [frag::FRONT, frag::TAIL]
        .into_iter()
        .filter(|n| !names.iter().any(|x| x == n))
        .collect();
    if !missing.is_empty() {
        return Err(refused(format!(
            "{place}/: {} missing - a page's front matter and its closing are fragments like any other, and the assembly will not invent them",
            missing.join(" and ")
        )));
    }
    let (front, tail) = (read(&root.join(frag::FRONT)), read(&root.join(frag::TAIL)));
    let mut sections = Vec::new();
    for name in ordered_sections(&place, &root, &names)? {
        sections.push(Section {
            id: id_of(&name),
            text: read(&root.join(&name)),
            entries: entries(&place, &root, &name)?,
        });
    }
    Ok(Page {
        front,
        sections,
        tail,
    })
}

/// The registry as one page.
///
/// # Errors
/// [`read_fragments`]'s.
pub fn registry_html(record_dir: &Path) -> Result<String> {
    Ok(assemble(&read_fragments(REGISTRY, record_dir)?))
}

fn ordered_sections(place: &str, root: &Path, names: &[String]) -> Result<Vec<String>> {
    let ordered = frag::ordered(names);
    for name in names {
        if name == frag::FRONT
            || name == frag::TAIL
            || ordered.contains(name)
            || root.join(name).is_dir()
        {
            continue;
        }
        return Err(refused(format!(
            "{place}/{name}: not a fragment name. A page directory holds {}, {} and <prefix>-<heading id>.html, and nothing else",
            frag::FRONT,
            frag::TAIL
        )));
    }
    let mut seen: Vec<(u128, &String)> = Vec::new();
    for name in &ordered {
        let at = frag::position_of(name)?;
        if let Some((_, first)) = seen.iter().find(|(p, _)| *p == at) {
            return Err(refused(format!(
                "{place}/: {first} and {name} both claim prefix {at:0w$} - the assembly will not choose between them",
                w = frag::SECTION_DIGITS
            )));
        }
        seen.push((at, name));
    }
    Ok(ordered)
}

fn entries(place: &str, root: &Path, section_name: &str) -> Result<Vec<Entry>> {
    let sub = section_name.strip_suffix(".html").unwrap_or(section_name);
    let path = root.join(sub);
    if !path.is_dir() {
        return Ok(Vec::new());
    }
    let mut out = Vec::new();
    for name in ordered_sections(&format!("{place}/{sub}"), &path, &listdir(&path))? {
        let text = read(&path.join(&name));
        let heading = heading_id(&text, 0)?;
        let named = id_of(&name);
        if frag::key_of(&heading) != frag::key_of(&named) {
            return Err(refused(format!(
                "{place}/{sub}/{name}: its filename says `{}` and its heading registers `{}` - one of the two is wrong",
                frag::key_of(&named),
                frag::key_of(&heading)
            )));
        }
        out.push(Entry { id: heading, text });
    }
    Ok(out)
}

/// The heading id a fragment's name carries: `010-how-deep.html` is `how-deep`.
fn id_of(name: &str) -> String {
    let rest = name.split_once('-').map_or("", |s| s.1);
    rest.strip_suffix(".html").unwrap_or(rest).to_owned()
}

/// A page file's name less its `.html`, as `file[: -len(".html")]`.
fn base(file: &str) -> String {
    let n = file.chars().count().saturating_sub(5);
    file.chars().take(n).collect()
}

/// key to body of one page's notes, as its reader sees them: originals put back, a note of several passages as a list, an absence note's
/// words (feature 292). A page with no notes file has none.
///
/// # Errors
/// A placeholder with no original, or no originals file for one; a malformed or repeated note key.
pub fn page_notes(file: &str, record_dir: &Path) -> Result<Notes> {
    let root = record_dir.join(qs::QUESTIONS);
    let b = base(file);
    let (notes_name, orig_name) = (format!("{b}{}", qs::NOTES), format!("{b}{}", qs::ORIGINALS));
    let Some(mut text) = crate::read(&root.join(&notes_name)) else {
        return Ok(Notes::new());
    };
    let place = format!("{}/{notes_name}", qs::QUESTIONS);
    match crate::read(&root.join(&orig_name)) {
        Some(stored) => {
            text = originals::restore(&text, &stored, true)
                .map_err(|e| refused(format!("{place}: {}", e.message)))?;
        }
        None if originals::has_placeholder(&text) => {
            return Err(refused(format!(
                "{place}: a note holds an original's placeholder and {orig_name} is missing"
            )));
        }
        None => {}
    }
    let text = passages::bulleted_notes(&text);
    let text = NOTE_BODY
        .replace_all(&text, |m: &Captures| {
            format!("{}{}{}", &m[1], absence::render(&m[2]), &m[3])
        })
        .into_owned();
    // `merge` of one file is that file's notes: `notes_of` has already refused a key defined twice in it
    notes_of(&text, &place).map_err(|e| refused(e.message))
}

/// What every question page's `page_html` reads of the whole record - the cross-link pairs and the confusables - read and checked once.
///
/// # Errors
/// The confusables' file broken, or a pair naming a section that does not exist.
pub fn shared(
    record: &Record,
    record_dir: &Path,
) -> Result<(Vec<xref::Pair>, Vec<confusables::Pair>)> {
    let pairs = confusables::load(record_dir)?;
    let bad = confusables::unresolved(&pairs, record);
    if !bad.is_empty() {
        return Err(refused(format!(
            "{} names a section that does not exist:\n  {}",
            confusables::DATA,
            bad.join("\n  ")
        )));
    }
    Ok((xref::pairs(record), pairs))
}

/// A question page as its reader sees it before its links are written for a site page: the cross-link to its other half and its *Not to
/// be confused with:* list written in. `tables` is [`shared`]'s, read once by a caller writing many pages.
///
/// # Errors
/// [`shared`]'s, where no tables are handed in; the cross-link's.
pub fn page_html(
    record: &Record,
    page: &QPage,
    record_dir: &Path,
    tables: Option<&(Vec<xref::Pair>, Vec<confusables::Pair>)>,
) -> Result<String> {
    let owned;
    let (xpairs, pairs) = if let Some(t) = tables {
        t
    } else {
        owned = shared(record, record_dir)?;
        &owned
    };
    let linked = xref::link(&page.text, page, xpairs)?;
    Ok(confusables::write(&linked, &page.file, pairs, record))
}

/// Move every original still written inline in a page's notes into its `.originals.html`; the notes files that had one. With `write` false
/// it only reports - the check.
///
/// # Errors
/// [`originals::split`]'s, or a file it cannot write.
pub fn split_originals(record_dir: &Path, write: bool) -> Result<Vec<String>> {
    let root = record_dir.join(qs::QUESTIONS);
    let mut names: Vec<String> = if root.is_dir() {
        listdir(&root)
    } else {
        Vec::new()
    };
    names.sort();
    let mut moved = Vec::new();
    for name in names.iter().filter(|n| n.ends_with(qs::NOTES)) {
        let notes_path = root.join(name);
        let orig_path = root.join(format!(
            "{}{}",
            name.strip_suffix(qs::NOTES).unwrap_or(name),
            qs::ORIGINALS
        ));
        let (text, stored) = (read(&notes_path), read(&orig_path));
        let (new_text, new_stored) = originals::split(&text, &stored)?;
        if new_text == text {
            continue;
        }
        moved.push(format!("{}/{name}", qs::QUESTIONS));
        if write {
            for (path, body) in [(&notes_path, &new_text), (&orig_path, &new_stored)] {
                std::fs::write(path, body).map_err(|e| Error::new("OSError", e.to_string()))?;
            }
        }
    }
    Ok(moved)
}

#[cfg(test)]
mod tests;
