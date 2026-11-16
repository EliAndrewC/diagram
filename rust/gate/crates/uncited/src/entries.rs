//! The kept pages' registry entries (feature 312 FR-012 - FR-019, plan D9 - D14): a draft bundle's entries installed into
//! `040-uncited-works/`, an entry moved to the works cited when a footnote first cites it, two entries for one work merged, a page
//! requeued, a works-cited source no one can read retired - and where the set stands.

use std::collections::{BTreeMap, HashSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::consulted::{self, norm};
use l7r_guard::shared::pyjson::{dumps, py_str, value_repr};
use serde_json::{json, Map, Value};

use crate::lists::{drop_verdicts, field, line, read, unkeep, write};
use crate::set::{uncited_set, work};
use crate::{
    base, entries, entry_files, lines, loads, name_of, numbered_html, py, read_text, registry_keys,
    strip, text_of, today, write_text,
};
use crate::{Error, Result, KEPT, NOT_KEPT, SOURCES, UNCITED};

/// The reservation `install` makes: the new entry's path for `(key, root, url)` (`record`'s `reserve`, handed in by its dispatch, which
/// builds on this crate), or why not - a refusal is kind `Refusal`, its words the reservation's own.
pub type Reserve = dyn Fn(&str, &Path, &str) -> Result<PathBuf>;

static KEY: LazyLock<Regex> = LazyLock::new(|| py(r"^[a-z0-9][a-z0-9-]*$"));
/// A field's own label written into its text by the drafter (the pilot, 2026-10-02: "What it is: A database entry...") - the entry writes
/// the label itself, so a leading one is dropped rather than doubled.
static LABEL: LazyLock<Regex> =
    LazyLock::new(|| py(r"(?i)^(?:What it is|Why it applies, and its limits)\s*:\s*"));

/// The kept URLs that already have an uncited entry.
///
/// # Errors
/// An entry that will not read.
pub fn written(root: &Path) -> Result<HashSet<String>> {
    let mut out = HashSet::new();
    for f in l7r_gate_archive::ops::html_files(&base(root).join(UNCITED)) {
        out.extend(
            l7r_gate_archive::ops::urls_in(&read_text(&f)?)
                .iter()
                .map(|u| norm(u)),
        );
    }
    Ok(out)
}

/// One uncited entry's HTML.
#[must_use]
pub fn entry_html(key: &str, citation: &str, what: &str, why: &str, marker: &str) -> String {
    format!(
        "<h3 id=\"{key}\"><code>{key}</code></h3>\n<p><!-- WRITTEN {} from the page as saved, by feature 312's write-up pass; KEPT by \
         source-filter -->{citation}</p>\n<p><em>What it is:</em> {what}</p>\n<p><em>Why it applies, and its limits:</em> {why}</p>\n{marker}\n",
        today()
    )
}

/// What `install` counts.
#[derive(Debug, Default, PartialEq, Eq)]
pub struct Installed {
    pub written: usize,
    pub refused: usize,
    pub already: usize,
    pub dropped: usize,
}

impl Installed {
    /// As `make uncited DO=install` prints it.
    #[must_use]
    pub fn json(&self) -> Value {
        json!({"written": self.written, "refused": self.refused, "already": self.already, "dropped": self.dropped})
    }
}

/// `e[k]` of a draft's line, as the Python's subscript raised: no mapping a `TypeError`, a missing field its `KeyError`.
fn sub<'v>(e: &'v Value, k: &str) -> Result<&'v Value> {
    match e {
        Value::Object(m) => m
            .get(k)
            .ok_or_else(|| Error::new("KeyError", value_repr(&json!(k)))),
        Value::Array(_) => Err(Error::new(
            "TypeError",
            "list indices must be integers or slices, not str",
        )),
        Value::String(_) => Err(Error::new(
            "TypeError",
            "string indices must be integers, not 'str'",
        )),
        other => Err(Error::new(
            "TypeError",
            format!(
                "'{}' object is not subscriptable",
                l7r_guard::shared::blocked::type_name(other)
            ),
        )),
    }
}

/// One draft line read: its URL, key, citation, the two texts and the tags' marker; or why it is refused (the exception's words).
fn draft_line(
    raw: &str,
    ids: &Map<String, Value>,
    vocab: &l7r_gate_research::record::source_tags::Vocabulary,
) -> Result<[String; 7]> {
    let e = loads(raw)?;
    let id = sub(&e, "id")?;
    let url = match id {
        Value::Array(_) | Value::Object(_) => {
            return Err(Error::new(
                "TypeError",
                format!(
                    "cannot use '{t}' as a dict key (unhashable type: '{t}')",
                    t = l7r_guard::shared::blocked::type_name(id)
                ),
            ));
        }
        Value::String(s) => ids.get(s),
        _ => None,
    }
    .ok_or_else(|| Error::new("KeyError", value_repr(id)))?;
    let mut f: Vec<String> = Vec::new();
    for k in ["key", "citation", "what", "why"] {
        f.push(strip(&py_str(sub(&e, k)?)).to_owned());
    }
    let what = LABEL.replace(&f[2], "").into_owned();
    let why = LABEL.replace(&f[3], "").into_owned();
    let marker = format!("<!-- tags: {} -->", py_str(sub(&e, "tags")?));
    let tags = l7r_gate_research::record::source_tags::parse(&marker, &py_str(id), vocab)
        .map_err(|e| Error::new("SourceTagError", e.message))?
        .ok_or_else(|| {
            Error::new(
                "AttributeError",
                "'NoneType' object has no attribute 'marker'",
            )
        })?;
    Ok([
        py_str(id),
        py_str(url),
        f[0].clone(),
        f[1].clone(),
        what,
        why,
        tags.marker(),
    ])
}

/// A draft bundle's entries reserved and written into `040-uncited-works/`. A line is refused (and counted) when it names no known id,
/// has an empty field, a key that is not one, or tags the vocabulary refuses; a key already taken gets `-2`, `-3`... The citation must
/// carry the page's URL exactly. Each refusal is a line on `err`.
///
/// # Errors
/// The bundle's ids, the vocabulary, the registry, the kept list; a reservation refused for another reason than a key held.
pub fn install(root: &Path, d: &Path, reserve: &Reserve, err: &mut String) -> Result<Installed> {
    let ids = match loads(&read_text(&d.join("ids.json"))?)? {
        Value::Object(m) => m,
        _ => Map::new(),
    };
    let vocab =
        l7r_gate_research::record::source_tags::load_vocabulary(&base(root).join("research"))?;
    let mut taken = registry_keys(root);
    let mut done = written(root)?;
    let kept_now = crate::lists::urls_of(&read(root, KEPT)?)?;
    let mut counts = Installed::default();
    let entries_at = d.join("entries.jsonl");
    let text = if entries_at.is_file() {
        read_text(&entries_at)?
    } else {
        String::new()
    };
    let dname = name_of(d);
    for raw in lines(&text) {
        let [id, url, mut key, cite, what, why, marker] = match draft_line(raw, &ids, &vocab) {
            Ok(got) => got,
            Err(e) => {
                let _ = writeln!(
                    err,
                    "uncited: {dname}: refused - {}: {}",
                    e.message,
                    crate::first(raw, 120)
                );
                counts.refused += 1;
                continue;
            }
        };
        if !(KEY.is_match(&key).unwrap_or(false)
            && !cite.is_empty()
            && !what.is_empty()
            && !why.is_empty()
            && cite.contains(&url))
        {
            let _ = writeln!(err, "uncited: {dname}: refused {id} - a bad key, an empty field, or a citation without its URL");
            counts.refused += 1;
            continue;
        }
        if done.contains(&norm(&url)) {
            // a bundle installed twice writes nothing twice
            counts.already += 1;
            continue;
        }
        if !kept_now.contains(&norm(&url)) {
            // retired since its bundle was drafted (`dedupe`, a merge): nothing to write
            counts.dropped += 1;
            continue;
        }
        let first_key = key.clone();
        let mut n = 1;
        let path = loop {
            while taken.contains(&key) {
                n += 1;
                key = format!("{first_key}-{n}");
            }
            match reserve(&key, root, &url) {
                Ok(p) => break p,
                // a key another clone holds is taken too
                Err(e) if e.message.contains("already") => {
                    taken.insert(key.clone());
                }
                Err(e) => return Err(e),
            }
        };
        write_text(&path, &entry_html(&key, &cite, &what, &why, &marker))?;
        taken.insert(key);
        done.insert(norm(&url));
        counts.written += 1;
    }
    Ok(counts)
}

/// The placeholder `Used for:` line a cited entry gets, which the build refuses until it names a real section.
pub const USED_FOR_PLACEHOLDER: &str = "<p><em>Used for:</em> TODO (<a href=\"contents.json#SECTION\">the section it serves</a>)</p>\n";

/// FR-014, plan D11: an uncited entry moved to the works cited when a footnote first cites it, keeping its number, with a `Used for:` line
/// placed before its tags marker. Returns where it went.
///
/// # Errors
/// No uncited entry for the key (`ValueError`), a read or a write.
pub fn cite(root: &Path, key: &str) -> Result<PathBuf> {
    let found = entry_files(&base(root).join(UNCITED), key);
    let Some(from) = found.first() else {
        return Err(Error::new(
            "ValueError",
            format!(
                "no uncited entry for {} in {UNCITED}",
                value_repr(&json!(key))
            ),
        ));
    };
    let dest = base(root)
        .join(SOURCES)
        .join("010-works-cited")
        .join(name_of(from));
    let text = read_text(from)?;
    let text = match text.rfind("<!-- tags:") {
        Some(i) => format!("{}{USED_FOR_PLACEHOLDER}{}", &text[..i], &text[i..]),
        None => text + USED_FOR_PLACEHOLDER,
    };
    write_text(&dest, &text)?;
    crate::remove_file(from)?;
    Ok(dest)
}

/// The key of the uncited entry whose citation carries this URL, if one was written.
///
/// # Errors
/// An entry that will not read.
pub fn entry_holding(root: &Path, raw: &str) -> Result<Option<String>> {
    for f in entries(&base(root).join(UNCITED)) {
        let name = name_of(&f);
        if numbered_html(&name) && read_text(&f)?.contains(raw) {
            let stem = name.strip_suffix(".html").unwrap_or(&name);
            return Ok(Some(
                stem.split_once('-')
                    .map(|(_, k)| k.to_owned())
                    .unwrap_or_default(),
            ));
        }
    }
    Ok(None)
}

/// A page whose verdict was judged from another page's text (R5, a misfiled import confirmed by reading): its kept or not-kept line and
/// its uncited entry go, so the filter judges it again from the live text. Returns the retired key.
///
/// # Errors
/// The lists' rewrite; a page with no verdict and no entry (`ValueError`).
pub fn requeue(root: &Path, raw: &str) -> Result<Option<String>> {
    let hit = drop_verdicts(root, raw)?;
    let key = entry_holding(root, raw)?.filter(|k| !k.is_empty());
    if let Some(k) = &key {
        for f in entries(&base(root).join(UNCITED)) {
            let name = name_of(&f);
            if name.as_bytes().first().is_some_and(u8::is_ascii_digit)
                && name.ends_with(&format!("-{k}.html"))
            {
                crate::remove_file(&f)?;
            }
        }
    }
    if !hit && key.is_none() {
        return Err(Error::new(
            "ValueError",
            format!("{raw} has no verdict and no entry to requeue"),
        ));
    }
    Ok(key)
}

/// Two entries for one work (a redirect and its target, a script variant): `key`'s uncited entry is retired and its page moves from the
/// kept list to the not-kept list as a duplicate of `into` - an uncited or a cited entry - which stays. Returns the retired file.
///
/// # Errors
/// Either entry missing, no kept page in the retired entry (`ValueError`); the move.
pub fn merge(root: &Path, key: &str, into: &str) -> Result<PathBuf> {
    let group = Path::new(UNCITED)
        .file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default();
    let entry = |k: &str, uncited: bool| -> Vec<PathBuf> {
        let mut out: Vec<PathBuf> = entries(&base(root).join(SOURCES))
            .into_iter()
            .filter(|d| !uncited || name_of(d) == group)
            .flat_map(|d| entry_files(&d, k))
            .collect();
        out.sort();
        out
    };
    for (k, uncited) in [(key, true), (into, false)] {
        if entry(k, uncited).is_empty() {
            return Err(Error::new(
                "ValueError",
                format!(
                    "no {}entry for {} under {SOURCES}",
                    if uncited { "uncited " } else { "" },
                    value_repr(&json!(k))
                ),
            ));
        }
    }
    let gone = entry(key, true).remove(0);
    let text = read_text(&gone)?;
    let mut mine = Vec::new();
    for x in read(root, KEPT)? {
        let raw = field(&x, "raw")?;
        if text.contains(&raw) {
            mine.push(raw);
        }
    }
    if mine.is_empty() {
        return Err(Error::new(
            "ValueError",
            format!(
                "{}: no kept page's URL appears in {}",
                value_repr(&json!(key)),
                name_of(&gone)
            ),
        ));
    }
    for raw in &mine {
        unkeep(
            root,
            raw,
            &["duplicate".to_owned()],
            "source-applicability",
            &format!("the same work as {into}"),
        )?;
    }
    crate::remove_file(&gone)?;
    Ok(gone)
}

/// FR-019 (plan D14): a works-cited source no one can read, its footnotes gone, leaves the works cited - its entry removed, a not-kept line
/// (`unreadable`, its access state) and the access state recorded by hand with the reason, through the access tags in process (feature 449
/// T147, where it ran `l7r-gate record access-tags set`). Refused while any question still cites it: its footnotes are removed or
/// re-sourced first. Returns the removed file.
///
/// # Errors
/// No entry, a question still citing it (`ValueError`); the line, the access tags' refusal (`ValueError`, their words).
pub fn retire_cited(root: &Path, key: &str, access: &str, note: &str) -> Result<PathBuf> {
    let found = entry_files(&base(root).join(SOURCES).join("010-works-cited"), key);
    let Some(entry) = found.first() else {
        return Err(Error::new(
            "ValueError",
            format!("no works-cited entry for {}", value_repr(&json!(key))),
        ));
    };
    let mut citing = Vec::new();
    for f in l7r_gate_archive::ops::html_files(&base(root).join("research/questions")) {
        if read_text(&f)?.contains(&format!("<code>{key}</code>")) {
            citing.push(name_of(&f));
        }
    }
    if !citing.is_empty() {
        citing.sort();
        return Err(Error::new(
            "ValueError",
            format!(
                "{key} is still cited in {} - remove or re-source those footnotes first (FR-019)",
                citing.join(", ")
            ),
        ));
    }
    let urls = l7r_gate_archive::ops::urls_in(&read_text(entry)?);
    let raw = urls
        .first()
        .ok_or_else(|| Error::new("IndexError", "list index out of range"))?
        .trim_end_matches(|c| ").,;:".contains(c))
        .to_owned();
    write(
        root,
        &[line(
            &raw,
            &["unreadable".to_owned()],
            "fr-019",
            &format!("{key}: {note}"),
            access,
        )?],
        NOT_KEPT,
    )?;
    let args: Vec<String> = ["set", key, access, &today(), note]
        .iter()
        .map(|a| (*a).to_owned())
        .collect();
    let done = l7r_gate_downloads::record::access_tags::cli(&args, root);
    if done.code != 0 {
        return Err(Error::new("ValueError", strip(&done.stderr).to_owned()));
    }
    crate::remove_file(entry)?;
    Ok(entry.clone())
}

/// Where the set stands, as `make uncited DO=report` prints it.
///
/// # Errors
/// The lists, the set, the cache, an entry.
pub fn report(root: &Path) -> Result<String> {
    let nk = read(root, NOT_KEPT)?;
    let mut reasons: BTreeMap<String, usize> = BTreeMap::new();
    for x in &nk {
        let rs =
            crate::lists::get(x, "reasons")?.ok_or_else(|| Error::new("KeyError", "'reasons'"))?;
        for r in rs.as_array().into_iter().flatten() {
            *reasons.entry(py_str(r)).or_default() += 1;
        }
    }
    let left = uncited_set(root)?;
    let home = consulted::home(root);
    let mut readable = 0;
    for u in &left {
        if text_of(&home, u)?.is_some() {
            readable += 1;
        }
    }
    let kept_lines = read(root, KEPT)?;
    let kept: HashSet<String> = crate::lists::urls_of(&kept_lines)?
        .iter()
        .map(|u| work(u))
        .collect();
    let mut entry_urls: Vec<HashSet<String>> = Vec::new();
    for f in entries(&base(root).join(UNCITED)) {
        if numbered_html(&name_of(&f)) {
            let text = read_text(&f)?;
            entry_urls.push(
                l7r_gate_archive::ops::urls_in(&text)
                    .iter()
                    .map(|u| work(&norm(u.trim_end_matches(|c| ").,;:".contains(c)))))
                    .collect(),
            );
        }
    }
    let orphans = entry_urls.iter().filter(|us| us.is_disjoint(&kept)).count();
    let all: HashSet<&String> = entry_urls.iter().flatten().collect();
    let unwritten = kept.iter().filter(|u| !all.contains(u)).count();
    let shown: Vec<String> = reasons.iter().map(|(k, v)| format!("{k} {v}")).collect();
    Ok(format!(
        "uncited: {} page(s) not yet judged ({readable} with saved text); {} kept, {} not kept ({}); {} written up, {unwritten} kept with no \
         entry, {orphans} entr(ies) whose URL is no kept page's (a citation a check corrected)",
        left.len(),
        kept_lines.len(),
        nk.len(),
        shown.join(", "),
        entry_urls.len()
    ))
}

/// The JSON a count is printed as (`json.dumps`, its separators).
#[must_use]
pub fn shown(v: &Value) -> String {
    dumps(v, None, true)
}

#[cfg(test)]
mod tests;
