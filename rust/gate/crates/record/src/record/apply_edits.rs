//! Apply the ready-made edits a check agent's report ends its findings with (`scripts/record/apply_edits.py`, feature 250 D15; ported by
//! feature 449 T145, phase 4's S2 under `ask:449-phase4-slices`): `l7r-gate record apply-edits` (`make apply-edits`). An EDIT block is
//! applied only where its old text occurs exactly once in a record file or a modal's file, each new text in the house style first; a
//! GLOSSARY block reserves its file under the host-wide lock ([`super::reserve`], in process). The round settles: the owed units of the
//! reply's check are fingerprinted before and after the blocks go in, and a unit whose content moved by them alone settles with its round's
//! answer (feature 335's round arbiter; features 375, 385, 399). What the Python asked through `scripts/owed_door.py` and
//! `scripts/record_door.py` (the owed tools, the modal bundle's `research_held`, `americanize`) is asked in process here.

use std::collections::{BTreeMap, HashSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::{Regex, RegexBuilder};
use l7r_gate_research::prepass::prepass_words;
use l7r_gate_research::pyre::py;
use l7r_guard::guards::house_style_hooks::americanize;
use l7r_guard::shared::py_text::{repr, strip};
use l7r_guard::shared::pyjson::{dumps, py_str};
use serde_json::{json, Value};

use super::reserve::{reserve, Ask, Refused};
use crate::record::args::{parse_with, Spec};
use crate::record::bundle::modal::research_held;
use crate::record::owed::answers::reply_text;
use crate::Reply;

const RECORD: &str = "research/";
const MODALS: &str = "l7r/diagram/interactive/classes/";
const SHEET_MODALS: &str = "l7r/diagram/interactive/compound_kinds/";
const MODAL_FILES: &str = "l7r/diagram/interactive/assets/modals/";
const ROOTS: [&str; 4] = [RECORD, MODALS, SHEET_MODALS, MODAL_FILES];
const TERMS: &str = "l7r/diagram/interactive/assets/glossary/";

static EDIT: LazyLock<Regex> = LazyLock::new(|| {
    RegexBuilder::new(
        r"(?sm)^(?P<ind>[ \t]*)EDIT[ \t]+`?(?P<path>[^\n`]+?)`?[ \t]*\n\k<ind><<<\n(?P<old>.*?)\n\k<ind>===\n(?:(?P<new>.*?)\n)??\k<ind>>>>[ \t]*$",
    )
    .backtrack_limit(10_000_000)
    .build()
    .unwrap_or_else(|e| unreachable!("{e}"))
});
static GLOSSARY: LazyLock<Regex> = LazyLock::new(|| {
    l7r_gate_core::record::units::re(
        r"(?m)^[ \t]*GLOSSARY[ \t]+(?P<term>[^|\n]+?)[ \t]*\|[ \t]*(?P<variants>[^|\n]*?)[ \t]*\|[ \t]*(?P<def>[^\n]+?)[ \t]*$",
    )
});
static QUESTION: LazyLock<Regex> =
    LazyLock::new(|| py(r"(?:^|/)research/questions/(\d{4})-[^/]*\.html$"));
static MODAL: LazyLock<Regex> = LazyLock::new(|| py(r"modals/(\w+)/([^/]+)\.md$"));

/// An EDIT block: its file, its old and new text, whether its new text is a lone empty line (a paragraph break), and the new text in
/// the house style.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Edit {
    pub n: usize,
    pub path: String,
    pub old: String,
    pub new: String,
    pub brk: bool,
    pub styled: String,
}

/// A GLOSSARY block: the term, its variants and its definition.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Term {
    pub n: usize,
    pub term: String,
    pub variants: Vec<String>,
    pub def: String,
}

/// One block of a reply, numbered from 1 in the reply's order.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Block {
    Edit(Edit),
    Glossary(Term),
}

impl Block {
    fn n(&self) -> usize {
        match self {
            Self::Edit(e) => e.n,
            Self::Glossary(t) => t.n,
        }
    }
}

#[expect(
    clippy::needless_pass_by_value,
    reason = "a `map_err` adapter, named so each call stays one line"
)]
fn os_error(e: std::io::Error) -> String {
    format!("OSError: {e}")
}

#[expect(
    clippy::needless_pass_by_value,
    reason = "a `map_err` adapter, named so each call stays one line"
)]
fn record_error(e: l7r_gate_research::Error) -> String {
    format!("{}: {}", e.kind, e.message)
}

fn dedent(text: &str, indent: &str) -> String {
    if indent.is_empty() {
        return text.to_owned();
    }
    text.split('\n')
        .map(|l| l.strip_prefix(indent).unwrap_or(l))
        .collect::<Vec<_>>()
        .join("\n")
}

/// `blocks`: every EDIT and GLOSSARY block, in the report's order.
#[must_use]
pub fn blocks(report: &str) -> Vec<Block> {
    let mut found: Vec<(usize, Block)> = Vec::new();
    for m in EDIT.captures_iter(report).flatten() {
        let g = |k: &str| m.name(k).map_or("", |x| x.as_str());
        let ind = g("ind");
        let new = m.name("new").map(|x| x.as_str());
        found.push((
            m.get(0).map_or(0, |x| x.start()),
            Block::Edit(Edit {
                n: 0,
                path: strip(g("path")).to_owned(),
                old: dedent(g("old"), ind),
                new: dedent(new.unwrap_or(""), ind),
                brk: new == Some(""),
                styled: String::new(),
            }),
        ));
    }
    for m in GLOSSARY.captures_iter(report).flatten() {
        let g = |k: &str| m.name(k).map_or("", |x| x.as_str());
        let variants = g("variants")
            .split(',')
            .map(strip)
            .filter(|v| !v.is_empty() && *v != "-")
            .map(str::to_owned)
            .collect();
        found.push((
            m.get(0).map_or(0, |x| x.start()),
            Block::Glossary(Term {
                n: 0,
                term: strip(g("term")).to_owned(),
                variants,
                def: strip(g("def")).to_owned(),
            }),
        ));
    }
    found.sort_by_key(|f| f.0);
    found
        .into_iter()
        .enumerate()
        .map(|(i, (_, mut b))| {
            match &mut b {
                Block::Edit(e) => e.n = i + 1,
                Block::Glossary(t) => t.n = i + 1,
            }
            b
        })
        .collect()
}

/// `resolve`: the origin file, if it lies under the record or a modal's files.
fn resolve(root: &Path, path: &str) -> Option<PathBuf> {
    // an absolute path replaces the root in `join`, as `pathlib`'s `/` does
    let p = l7r_gate_research::resolve(&root.join(path));
    ROOTS
        .iter()
        .any(|r| p.starts_with(root.join(r)))
        .then_some(p)
}

fn read(p: &Path) -> Result<String, String> {
    let raw = std::fs::read(p).map_err(os_error)?;
    let text = String::from_utf8(raw).map_err(|e| format!("UnicodeDecodeError: {e}"))?;
    Ok(text.replace("\r\n", "\n").replace('\r', "\n"))
}

/// `held_dropped`: for a modal-form reply's EDIT on a pop-up, the research-fixed wording its old text holds and its new text drops.
fn held_dropped(root: &Path, path: &str, old: &str, new: &str) -> Result<String, String> {
    let Some(m) = MODAL.captures(path).ok().flatten() else {
        return Ok(String::new());
    };
    let Some(target) = resolve(root, path).filter(|t| t.is_file()) else {
        return Ok(String::new());
    };
    let held = held_of(root, &format!("{}/{}", &m[1], &m[2]), &read(&target)?);
    Ok(held
        .into_iter()
        .find(|h| old.contains(h.as_str()) && !new.contains(h.as_str()))
        .unwrap_or_default())
}

#[cfg(test)]
thread_local! {
    /// The wording a test says modal-research rounds fixed, in place of the transcripts `research_held` reads.
    static HELD: std::cell::RefCell<Option<Vec<String>>> = const { std::cell::RefCell::new(None) };
}

/// `modal_bundle.research_held`: the wording research rounds fixed on the pop-up `uid` that still stands in `text`.
fn held_of(root: &Path, uid: &str, text: &str) -> Vec<String> {
    #[cfg(test)]
    if let Some(held) = HELD.with(|h| h.borrow().clone()) {
        return held;
    }
    research_held(root, uid, text)
}

/// `replaced`: the file with the block's one occurrence replaced - a break a blank line, an emptied whole line taking its newline.
fn replaced(text: &str, old: &str, new: &str, brk: bool) -> String {
    let i = text.find(old).unwrap_or(0);
    let mut j = i + old.len();
    let whole =
        (i == 0 || text[..i].ends_with('\n')) && (j == text.len() || text[j..].starts_with('\n'));
    let new = if brk {
        if whole {
            ""
        } else {
            "\n\n"
        }
    } else if new.is_empty() && whole {
        j += usize::from(j < text.len());
        ""
    } else {
        new
    };
    format!("{}{new}{}", &text[..i], &text[j..])
}

/// `apply_edit`: one EDIT block applied, skipped as already applied, or refused with why.
fn apply_edit(root: &Path, b: &Edit, dry: bool, form: bool) -> Result<String, String> {
    let Edit {
        path,
        old,
        new,
        brk,
        styled,
        ..
    } = b;
    if form {
        let h = held_dropped(root, path, old, new)?;
        if !h.is_empty() {
            return Ok(format!("REFUSED - a modal-form EDIT drops wording a research round fixed ({}); reword around it, or put the fact to modal-research", repr(&h.chars().take(80).collect::<String>())));
        }
    }
    let Some(target) = resolve(root, path) else {
        return Ok(format!(
            "REFUSED - {path} is not under {RECORD}, {MODAL_FILES}, {MODALS} or {SHEET_MODALS}"
        ));
    };
    if !target.is_file() {
        return Ok(format!("REFUSED - no file {path}"));
    }
    let name = target
        .file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default();
    let text = read(&target)?;
    let count = text.matches(old.as_str()).count();
    if !old.is_empty()
        && new.contains(old.as_str())
        && text.contains(new.as_str())
        && text.matches(new.as_str()).count() >= count
    {
        return Ok(format!("already applied to {name}"));
    }
    if count != 1 {
        return Ok(format!(
            "REFUSED - the old text occurs {count} times in {name}, not once"
        ));
    }
    if !dry {
        std::fs::write(&target, replaced(&text, old, styled, *brk)).map_err(os_error)?;
    }
    Ok(format!("applied to {name}"))
}

/// `apply_term`: a GLOSSARY block's file reserved under the host-wide lock, or skipped where the term is on file.
fn apply_term(root: &Path, b: &Term, dry: bool) -> Result<String, String> {
    let Term {
        term,
        variants,
        def,
        ..
    } = b;
    let mut have = HashSet::new();
    for e in std::fs::read_dir(root.join(TERMS))
        .into_iter()
        .flatten()
        .flatten()
    {
        if e.path().extension().is_some_and(|x| x == "json") {
            let data: Value = l7r_guard::shared::pyjson::loads(&read(&e.path())?)
                .map_err(|e| format!("JSONDecodeError: {e}"))?;
            let t = data.get("term").map_or_else(String::new, |v| {
                v.as_str().map(str::to_lowercase).unwrap_or_default()
            });
            have.insert(t);
        }
    }
    if have.contains(&term.to_lowercase()) {
        return Ok(format!("skipped - '{term}' is already a glossary term"));
    }
    let mut all = vec![term.clone()];
    all.extend(variants.iter().filter(|v| *v != term).cloned());
    let entry = json!({"term": term, "def": def, "variants": all});
    if dry {
        return Ok(format!("would add a file for {}", repr(term)));
    }
    let ask = Ask {
        kind: "glossary",
        key: term,
        root,
        mirror: None,
        stub: Some(dumps(&entry, Some(1), false) + "\n"),
        timeout: 30.0,
        url: "",
        tags: "",
        command: std::env::args().collect::<Vec<_>>().join(" "),
        var: &l7r_guard::shared::consulted::var,
    };
    match reserve(&ask) {
        Ok(path) => Ok(format!(
            "added {}",
            path.file_name()
                .map(|n| n.to_string_lossy().into_owned())
                .unwrap_or_default()
        )),
        Err(Refused::Refusal(why)) => Ok(format!("REFUSED - {why}")),
        Err(Refused::Raised(kind, why)) => Err(format!("{kind}: {why}")),
    }
}

/// `touched_questions`: the question numbers whose files the report's EDIT blocks name.
fn touched_questions(found: &[Block]) -> Vec<String> {
    let mut out: Vec<String> = found
        .iter()
        .filter_map(|b| match b {
            Block::Edit(e) => QUESTION
                .captures(&e.path)
                .ok()
                .flatten()
                .map(|c| c[1].to_owned()),
            Block::Glossary(_) => None,
        })
        .collect();
    out.sort();
    out.dedup();
    out
}

/// `is_repo`: `root` is a clone's top level.
fn is_repo(root: &Path) -> bool {
    let (ok, top) = l7r_gate_core::cohort::git(root, &["rev-parse", "--show-toplevel"]);
    ok && l7r_gate_research::resolve(Path::new(strip(&top))) == l7r_gate_research::resolve(root)
}

mod round;

fn usage(e: &str) -> Reply {
    Reply {
        stdout: String::new(),
        stderr: format!("apply_edits.py: error: {e}\n"),
        code: 2,
    }
}

/// `l7r-gate record apply-edits <report> [--root R] [--skip 2,5] [--dry-run]`.
#[must_use]
pub fn cli(args: &[String], cwd: &Path) -> Reply {
    let specs = [
        Spec::value("--root"),
        Spec::value("--skip"),
        Spec::flag("--dry-run"),
    ];
    let p = match parse_with(args, &specs, 1) {
        Ok(p) if !p.positional.is_empty() => p,
        Ok(_) => return usage("the following arguments are required: report"),
        Err(e) => return usage(&e),
    };
    let root = l7r_gate_research::resolve(&cwd.join(p.text("--root", ".")));
    let report = match reply_text(&cwd.join(&p.positional[0])) {
        Ok(r) => r,
        Err(e) => {
            return Reply {
                stdout: String::new(),
                stderr: e + "\n",
                code: 1,
            }
        }
    };
    let mut found = blocks(&report);
    let form = l7r_guard::shared::checks::reply::py_lines(&report)
        .into_iter()
        .map(strip)
        .find(|l| !l.is_empty())
        .unwrap_or("")
        .starts_with("modal-form:");
    if found.is_empty() {
        return Reply { stdout: String::new(), stderr: "apply-edits: the report carries no EDIT or GLOSSARY block - apply its findings by hand\n".to_owned(), code: 2 };
    }
    let mut skip = HashSet::new();
    for s in p
        .text("--skip", "")
        .split(',')
        .filter(|s| !strip(s).is_empty())
    {
        match strip(s).parse::<i64>() {
            Ok(n) => {
                skip.insert(usize::try_from(n).unwrap_or(usize::MAX));
            }
            Err(_) => {
                return Reply {
                    stdout: String::new(),
                    stderr: format!(
                        "ValueError: invalid literal for int() with base 10: {}\n",
                        repr(s)
                    ),
                    code: 1,
                }
            }
        }
    }
    let dry = p.on("--dry-run");
    if !dry {
        for b in &mut found {
            if let Block::Edit(e) = b {
                if !skip.contains(&e.n) {
                    e.styled = americanize(&e.new);
                }
            }
        }
    }
    round::run(&root, &report, &found, &skip, dry, form)
}

#[cfg(test)]
mod tests;

/// What `apply` tallied over the blocks.
#[derive(Default)]
struct Tally {
    refused: usize,
    terms: usize,
    edited: usize,
}

/// `apply`: every block not skipped, each said on its own line.
fn apply(
    root: &Path,
    found: &[Block],
    skip: &HashSet<usize>,
    dry: bool,
    form: bool,
    said: &mut String,
) -> Result<Tally, String> {
    let mut t = Tally::default();
    for b in found {
        if skip.contains(&b.n()) {
            let _ = writeln!(said, "  {}. skipped (--skip)", b.n());
            continue;
        }
        let (word, what) = match b {
            Block::Edit(e) => (apply_edit(root, e, dry, form)?, e.path.clone()),
            Block::Glossary(t) => (apply_term(root, t, dry)?, format!("GLOSSARY {}", t.term)),
        };
        t.refused += usize::from(word.starts_with("REFUSED"));
        t.terms += usize::from(word.starts_with("added"));
        t.edited += usize::from(word.starts_with("applied"));
        let _ = writeln!(said, "  {}. {word}   ({what})", b.n());
    }
    Ok(t)
}

/// An EDIT already applied by hand is put back to its old text, so the settling sees the round's own blocks move the unit (385 T21).
fn unapply_by_hand(
    root: &Path,
    found: &[Block],
    skip: &HashSet<usize>,
    said: &mut String,
) -> Result<(), String> {
    for b in found.iter().filter_map(|b| {
        if let Block::Edit(e) = b {
            Some(e)
        } else {
            None
        }
    }) {
        let Edit {
            n, path, old, new, ..
        } = b;
        if skip.contains(n) || old.is_empty() || new.contains(old.as_str()) {
            continue;
        }
        let Some(target) = resolve(root, path).filter(|t| t.is_file()) else {
            continue;
        };
        let text = read(&target)?;
        if !text.is_empty()
            && !text.contains(old.as_str())
            && text.matches(new.as_str()).count() == 1
        {
            std::fs::write(&target, text.replacen(new.as_str(), old, 1)).map_err(os_error)?;
            let _ = writeln!(
                said,
                "  {n}. found applied by hand - settled through its reply   ({path})"
            );
        }
    }
    Ok(())
}

/// The words of each question's prepass, for a record-format round.
fn words_of(
    root: &Path,
    questions: &[String],
) -> Result<BTreeMap<String, HashSet<String>>, String> {
    questions
        .iter()
        .map(|q| {
            prepass_words(root, q)
                .map(|w| (q.clone(), w))
                .map_err(record_error)
        })
        .collect()
}

/// A JSON value's text, `str()`.
fn text(v: Option<&Value>, default: &str) -> String {
    v.map_or_else(|| default.to_owned(), py_str)
}
