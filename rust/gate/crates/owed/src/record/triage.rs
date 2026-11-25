//! The pop-up triage (from `modal_triage.py`, feature 449 T87): a drawing or question page's edit owes a pop-up's checks only where it bears on that pop-up. `make modal-triage` writes one bundle of each moved page's changed blocks and the pop-ups naming it; `make modal-triaged` applies a triage reply, answering what the reply leaves alone and marking what it names.

use std::collections::{HashMap, HashSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::checks::pages::read_page;
use l7r_shared::pyjson;
use serde_json::{json, Map, Value};

use super::args::{parse, Parsed, Spec};
use super::modals::{self, Modal, DEPICTION_CHECK, FORM_CHECK, RESEARCH_AGENT, RESEARCH_CHECKS};
use super::owed::{self, answered as is_answered, merge_base, read_answer, write_answer};
use super::repo::{fail, git, read_text, read_universal, Fail};
use super::units::re;
use crate::Reply;
use change::Change;

pub mod change;
mod reply;

use reply::read_reply;

/// A subcommand of the triage.
type Runner = fn(&Path, &Parsed) -> Result<Reply, Fail>;

const TOUCHED: &str = "modal-triage-touched.json";

static TOUCHES: LazyLock<Regex> =
    LazyLock::new(|| re(r"^TOUCHES\s+`?(\S+?)`?(?:\s+@\s+`?(\S+?)`?)?\s+-\s+(.*)$"));

/// One clone's bundle directory, under the bundles' root (`/tmp/l7r-check`; a test's own, never the real one - feature 449 T101).
fn default_out(root: &Path) -> PathBuf {
    let name = root
        .file_name()
        .map_or_else(String::new, |n| n.to_string_lossy().into_owned());
    l7r_gate_core::record::bundle::default_root().join(format!("modal-triage-{name}"))
}

/// Whether the unit is owed only because a page it names moved.
#[must_use]
pub fn triage_only(why: &str) -> bool {
    why.starts_with("a page its ")
}

/// {slug: fingerprint} of the units a triage named.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn touched(store: &Path) -> Result<std::collections::HashMap<String, String>, Fail> {
    let Some(text) = read_universal(&store.join(TOUCHED))? else {
        return Ok(std::collections::HashMap::new());
    };
    let value: Map<String, Value> = serde_json::from_str(&text).map_err(fail)?;
    Ok(value
        .into_iter()
        .map(|(k, v)| (k, v.as_str().unwrap_or("").to_owned()))
        .collect())
}

/// (slug, why, fingerprint) of every unit owed only a triage: unanswered at its fingerprint and not named by a triage.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn pending(
    root: &Path,
    base: &str,
    store: &Path,
    owed: Option<&[(String, String, String)]>,
) -> Result<Vec<(String, String, String)>, Fail> {
    let named = touched(store)?;
    let rows = match owed {
        Some(r) => r.to_vec(),
        None => modals::owed(root, base, "")?,
    };
    Ok(rows
        .into_iter()
        .filter(|(slug, why, fp)| {
            triage_only(why) && !is_answered(store, slug, fp, "") && named.get(slug) != Some(fp)
        })
        .collect())
}

/// The page at `path` written into the clone's object store as it stands; its blob id, or "".
#[must_use]
pub fn keep(root: &Path, path: &str) -> String {
    if !root.join(path).is_file() {
        return String::new();
    }
    git(root, &["hash-object", "-w", "--", path])
        .trim()
        .to_owned()
}

fn blob_text(root: &Path, blob: &str) -> String {
    git(root, &["cat-file", "-p", blob])
}

fn kept_pages(store: &Path, slug: &str) -> Map<String, Value> {
    read_answer(store, slug)
        .get("pages")
        .and_then(Value::as_object)
        .cloned()
        .unwrap_or_default()
}

fn page_before(
    root: &Path,
    store: &Path,
    slug: &str,
    path: &str,
    base: &str,
    read: &mut modals::RevReader,
) -> String {
    let blob = kept_pages(store, slug)
        .get(path)
        .and_then(Value::as_str)
        .unwrap_or("")
        .to_owned();
    let kept = Some(blob)
        .filter(|b| !b.is_empty())
        .map(|b| blob_text(root, &b))
        .unwrap_or_default();
    let fall_back = kept.is_empty() && !base.is_empty();
    if fall_back {
        read.read(path).unwrap_or_default()
    } else {
        kept
    }
}

/// Which version of `path` a unit's triage diffs against: the blob its last answer kept, or "".
fn baseline(store: &Path, slug: &str, path: &str) -> String {
    kept_pages(store, slug)
        .get(path)
        .and_then(Value::as_str)
        .unwrap_or("")
        .to_owned()
}

/// The pages a unit's triage reads: a depiction unit's, and a form unit's (owed only by a labeled item its drawing pages gained, 451
/// T226), its `Drawing:` pages; a research unit's its `Entry:` pages.
fn pages_of(root: &Path, m: &Modal, check: &str) -> Vec<String> {
    modals::followed(
        root,
        &if check == DEPICTION_CHECK || check == FORM_CHECK {
            m.drawing_files()
        } else {
            m.entry_files()
        },
    )
}

fn clear_dir(dir: &Path) -> Result<(), Fail> {
    if dir.exists() {
        for entry in std::fs::read_dir(dir).map_err(fail)?.flatten() {
            std::fs::remove_file(entry.path()).map_err(fail)?;
        }
    }
    Ok(())
}

/// The pop-ups under one page's change, keyed `(path, baseline, the change's digest)` (sorted), each pop-up's checks sorted.
type ByPage = std::collections::BTreeMap<
    (String, String, String),
    std::collections::BTreeMap<String, std::collections::BTreeSet<String>>,
>;

/// What a page changed for its readers, keyed as [`ByPage`] is.
type Changed = std::collections::HashMap<(String, String, String), Change>;

/// A pop-up whole, as its checks read it: every tag in its file's order (feature 451 T186: never cut at 400 characters).
fn whole(m: &Modal) -> String {
    m.tags
        .iter()
        .filter(|(_, v)| !v.trim().is_empty())
        .map(|(k, v)| format!("{k}: {}", v.trim()))
        .collect::<Vec<_>>()
        .join("\n")
}

/// One change's lines in the MANIFEST: each changed block with its old self and a word diff, then the new and the removed.
fn change_lines(c: &Change, parts: &mut Vec<String>) {
    for (old, new) in &c.pairs {
        parts.push(format!(
            "Changed:\n  OLD: {old}\n  NEW: {new}\n  WORD DIFF: {}\n",
            change::word_diff(old, new)
        ));
    }
    parts.extend(c.added.iter().map(|w| format!("New:\n  NEW: {w}\n")));
    parts.extend(change::moved_edited_lines(c, "a page these pop-ups reach"));
    parts.extend(
        change::removed_unmoved(c)
            .iter()
            .map(|w| format!("Removed (no longer on the page):\n  OLD: {w}\n")),
    );
    if !c.keys_gone.is_empty() {
        parts.push(format!(
            "Note keys no longer on the page or a page it points to: {}\n",
            c.keys_gone.join(", ")
        ));
    }
}

/// The bundle's `MANIFEST.md`, part by part: each moved page's change and the pop-ups it reaches, then each pop-up whole, once.
fn manifest_parts(
    by_page: &ByPage,
    blocks: &Changed,
    modals: &[(String, Modal)],
    gained: &Gained,
) -> Vec<String> {
    let find = |uid: &str| modals.iter().find(|(u, _)| u == uid).map(|(_, m)| m);
    let mut parts = vec![
        "# Triage of pop-up checks (feature 375, FR-001; feature 451 T186)\n".to_owned(),
        "owed-checks: modal-triage\n".to_owned(),
        "For the `modal-triage` agent: rule on each pop-up below as your contract says, and reply in its form. Comment, markup, link and footnote-marker edits, and blocks a split moved verbatim, were cleared by the tool and are not shown; a block a split moved with an edit is shown as moved, with its diff.\n".to_owned(),
    ];
    let mut shown: std::collections::BTreeSet<&str> = std::collections::BTreeSet::new();
    for (key, popups) in by_page {
        let (path, base_blob, _) = key;
        let against = if base_blob.is_empty() {
            "against the merge base (no check has read it yet)"
        } else {
            "against the version these pop-ups' last check read"
        };
        parts.push(format!("## {path}\n\n({against})\n"));
        change_lines(&blocks[key], &mut parts);
        parts.push("Pop-ups reading it:\n".to_owned());
        for (uid, checks) in popups {
            let checks: Vec<&str> = checks.iter().map(String::as_str).collect();
            parts.push(format!("- UID `{uid}` ({})", checks.join(", ")));
            shown.insert(uid.as_str());
        }
        if let Some(lines) = gained.get(path) {
            parts.push("\nLabeled items new on this page that a pop-up's Guesses tab does not reference - its `modal-form` is owed for them, judged by rule (D):\n".to_owned());
            parts.extend(lines.iter().cloned());
        }
        parts.push(String::new());
    }
    parts.push("# The pop-ups, whole\n".to_owned());
    for uid in shown {
        let m = find(uid).map_or_else(Modal::default, Clone::clone);
        parts.push(format!("## UID `{uid}`\n\n{}\n", whole(&m)));
    }
    parts
}

/// Write the triage bundle (`MANIFEST.md`, `triage.json`); (its MANIFEST, how many units), or None for no unit owed one.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn bundle(root: &Path, out: &Path, base: &str) -> Result<Option<(PathBuf, usize)>, Fail> {
    Ok(bundle_in(root, out, base, &owed::store(root))?.0)
}

/// A unit's reading of its pages: each page's text now and at its baseline.
struct Reading {
    now: Vec<(String, String)>,
    before: Vec<(String, String)>,
}

impl Reading {
    fn words(texts: &[(String, String)], but: &str) -> HashSet<String> {
        texts
            .iter()
            .filter(|(p, _)| p != but)
            .flat_map(|(_, t)| change::block_words(t))
            .collect()
    }
}

/// Every question page's block words, read once a bundle and only where a removal asks (a split with no pointer).
fn record_words(root: &Path) -> Vec<(String, HashSet<String>)> {
    let dir = root.join("research/questions");
    let mut names: Vec<String> = std::fs::read_dir(&dir)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .filter(|n| {
            Path::new(n).extension().is_some_and(|e| e == "html")
                && !n.ends_with(".notes.html")
                && !n.ends_with(".originals.html")
        })
        .collect();
    names.sort();
    names
        .into_iter()
        .map(|n| {
            let text = std::fs::read_to_string(dir.join(&n)).unwrap_or_default();
            (
                format!("research/questions/{n}"),
                change::block_words(&text),
            )
        })
        .collect()
}

/// A page still owing a unit the agent: its key in the MANIFEST and its change.
type PageOwed = ((String, String, String), Change);

/// What one unit's triage reads beside its own pages: the store, the base and its reader, the record's pages (read once a bundle, only
/// where a removal asks), and the splits with no pointer it has met.
struct Unit<'a> {
    root: &'a Path,
    store: &'a Path,
    base: &'a str,
    read: &'a mut modals::RevReader,
    elsewhere: &'a mut Option<Vec<(String, HashSet<String>)>>,
    unpointed: &'a mut Vec<String>,
    /// The pages the tool may not clear for this unit: a form unit's drawing pages that gained a labeled item it is owed for (451
    /// T226). The tool's filter reads what a pop-up states, and the item is what the pop-up does not state, so only the agent's rule
    /// (D) judges it.
    held: &'a HashSet<String>,
}

/// Each page of a unit's that still owes it the agent: its key in the MANIFEST and its change, after the tool's clears and a split's
/// moves (feature 451 T185, T186).
fn unit_changes(
    u: &mut Unit<'_>,
    slug: &str,
    check: &str,
    m: &Modal,
    all: &[String],
) -> Result<Vec<PageOwed>, Fail> {
    let (root, store) = (u.root, u.store);
    let mut reading = Reading {
        now: Vec::new(),
        before: Vec::new(),
    };
    for path in all {
        reading.now.push((
            path.clone(),
            read_universal(&root.join(path))?.unwrap_or_default(),
        ));
        reading.before.push((
            path.clone(),
            page_before(root, store, slug, path, u.base, u.read),
        ));
    }
    let sources: HashSet<&str> = m.tag("Sources").split(',').map(str::trim).collect();
    let mut owed_pages: Vec<PageOwed> = Vec::new();
    for (i, path) in all.iter().enumerate() {
        if reading.before[i].1 == reading.now[i].1 {
            continue;
        }
        let (old, fresh) = (&reading.before[i].1, &reading.now[i].1);
        let reached = Reading::words(&reading.now, path);
        let (mut c, why) = judged(
            old,
            fresh,
            &reached,
            &Reading::words(&reading.before, path),
            &|k| check != DEPICTION_CHECK && sources.contains(k),
            &popup_text(m),
        );
        if !c.removed.is_empty() {
            let pages = u.elsewhere.get_or_insert_with(|| record_words(root));
            let others: Vec<(String, HashSet<String>)> = pages
                .iter()
                .filter(|(p, _)| !all.contains(p))
                .cloned()
                .collect();
            c.unpointed = change::page_change(
                &reading.before[i].1,
                &reading.now[i].1,
                &HashSet::new(),
                &HashSet::new(),
                &others,
            )
            .unpointed;
            u.unpointed
                .extend(c.unpointed.iter().map(|(_, to)| format!("{path} -> {to}")));
        }
        if why.is_none() && !u.held.contains(path) {
            continue;
        }
        let digest = super::units::digest(&[&format!(
            "{:?}",
            (
                &c.pairs,
                &c.added,
                &c.removed,
                &c.keys_gone,
                &c.moved_edited
            )
        )]);
        owed_pages.push(((path.clone(), baseline(store, slug, path), digest), c));
    }
    Ok(owed_pages)
}

/// One page's change for one pop-up reading `popup`, after the tool's clears and a split's moves, its note keys kept where `cited`,
/// and why it still owes the pop-up its triage, or None: the one judgment the bundle and the landing's replay share (feature 451 T194).
fn judged(
    old: &str,
    fresh: &str,
    reached_now: &HashSet<String>,
    reached_before: &HashSet<String>,
    cited: &dyn Fn(&str) -> bool,
    popup: &str,
) -> (Change, Option<String>) {
    let mut c = change::page_change(old, fresh, reached_now, reached_before, &[]);
    c.keys_gone.retain(|k| cited(k));
    if c.is_clear() && c.keys_gone.is_empty() {
        return (c, None);
    }
    let page_now: Vec<String> = read_page(fresh)
        .blocks
        .into_iter()
        .map(|b| b.words)
        .collect();
    let why = change::fires(&c, &page_now, reached_now, popup, &[]);
    (c, why)
}

/// Answer a unit the tool cleared, keeping the pages it read so its next triage diffs against them.
fn answer_cleared(store: &Path, slug: &str, fp: &str, read: Option<&Value>) -> Result<(), Fail> {
    let mut kept = read_answer(store, slug)
        .get("pages")
        .and_then(Value::as_object)
        .cloned()
        .unwrap_or_default();
    for (k, v) in read.and_then(Value::as_object).into_iter().flatten() {
        kept.insert(k.clone(), v.clone());
    }
    write_answer(
        store,
        slug,
        fp,
        "triage: cleared by the tool (no claim-bearing change)",
        Some(&Value::Object(kept)),
    )
}

/// What a pop-up states, as the echo rule reads it: every tag but its references and its name.
fn popup_text(m: &Modal) -> String {
    m.tags
        .iter()
        .filter(|(k, _)| {
            !matches!(
                k.as_str(),
                "Sources" | "Entry" | "Drawing" | "Covers" | "Name"
            )
        })
        .map(|(_, v)| v.as_str())
        .collect::<Vec<_>>()
        .join("\n")
}

/// The whole filter replayed over a landing (feature 451 T186's replay): each pop-up at its parent that reads a question or drawing
/// page the landing changed, and whether that page's change still owes it its triage; `<uid>\tfires|cleared\t<page>\t<why>`.
///
/// # Errors
///
/// Where the parent's pop-ups cannot be read.
pub fn replay_landing(root: &Path, commit: &str) -> Result<String, Fail> {
    let parent = format!("{commit}^");
    let changed: Vec<String> = git(
        root,
        &[
            "diff",
            "--name-only",
            &format!("{parent}..{commit}"),
            "--",
            "research/questions",
        ],
    )
    .lines()
    .filter(|f| {
        Path::new(f).extension().is_some_and(|e| e == "html")
            && !f.ends_with(".notes.html")
            && !f.ends_with(".originals.html")
    })
    .map(str::to_owned)
    .collect();
    let mut texts: HashMap<(bool, String), String> = HashMap::new();
    let mut text = |at_commit: bool, page: &str| -> String {
        texts
            .entry((at_commit, page.to_owned()))
            .or_insert_with(|| {
                let rev = if at_commit { commit } else { parent.as_str() };
                git(root, &["show", &format!("{rev}:{page}")])
            })
            .clone()
    };
    let mut out = String::new();
    for (uid, m) in modals::modals_at(root, &parent, false)?.iter() {
        let reads: Vec<String> = m
            .entry_files()
            .into_iter()
            .chain(m.drawing_files())
            .collect();
        // the pages the pop-up reaches at each side: its own and their pointers' targets, as the bundle's `followed` reads them
        let mut reach = |at_commit: bool| -> Vec<(String, String)> {
            let mut pages: Vec<(String, String)> = reads
                .iter()
                .map(|p| (p.clone(), text(at_commit, p)))
                .collect();
            let targets: Vec<String> = pages
                .iter()
                .flat_map(|(_, t)| change::pointer_targets(t))
                .collect();
            for t in targets {
                if !pages.iter().any(|(p, _)| *p == t) {
                    let body = text(at_commit, &t);
                    pages.push((t, body));
                }
            }
            pages
        };
        let (now, before) = (reach(true), reach(false));
        let sources: HashSet<&str> = m.tag("Sources").split(',').map(str::trim).collect();
        for (page, new) in now.iter().filter(|(p, _)| changed.contains(p)) {
            let old = before
                .iter()
                .find(|(p, _)| p == page)
                .map_or_else(|| text(false, page), |(_, t)| t.clone());
            let (_, why) = judged(
                &old,
                new,
                &Reading::words(&now, page),
                &Reading::words(&before, page),
                &|k| sources.contains(k),
                &popup_text(m),
            );
            let _ = writeln!(
                out,
                "{uid}\t{}\t{page}\t{}",
                if why.is_some() { "fires" } else { "cleared" },
                why.unwrap_or_default()
            );
        }
    }
    Ok(out)
}

/// [`bundle`] reading the answer records `store` (feature 451 T38: a landing's replay names its own store here, where it set
/// `RECORD_CHECKS_DIR` in the process's environment around the call); also how many units the tool cleared with no agent (feature
/// 451 T186), each answered as `triage: cleared by the tool`.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn bundle_in(
    root: &Path,
    out: &Path,
    base: &str,
    store: &Path,
) -> Result<(Option<(PathBuf, usize)>, usize), Fail> {
    let base = if base.is_empty() {
        merge_base(root)
    } else {
        base.to_owned()
    };
    let units = pending(root, &base, store, None)?;
    if units.is_empty() {
        return Ok((None, 0));
    }
    let modals_now: Vec<(String, Modal)> = modals::modals_now(root, false)?
        .into_iter()
        .map(|m| (m.uid(), m))
        .collect();
    let find = |uid: &str| modals_now.iter().find(|(u, _)| u == uid).map(|(_, m)| m);
    let mut read = modals::read_at(root, &base);
    let mut by_page: ByPage = ByPage::new();
    let mut blocks = Changed::new();
    let (mut reads, mut blobs) = (Map::new(), Map::new());
    let mut kept_ids: HashMap<String, String> = HashMap::new();
    let mut elsewhere: Option<Vec<(String, HashSet<String>)>> = None;
    let (mut sent, mut cleared) = (Vec::new(), 0usize);
    let mut unpointed: Vec<String> = Vec::new();
    let mut gained = Gained::new();
    for (slug, _why, fp) in &units {
        let (check, uid) = slug.split_once(':').unwrap_or((slug, ""));
        let m = find(uid).cloned().unwrap_or_default();
        let all = pages_of(root, &m, check);
        let held = held_pages(root, &base, check, &m, &mut gained)?;
        let owed_pages = unit_changes(
            &mut Unit {
                root,
                store,
                base: &base,
                read: &mut read,
                elsewhere: &mut elsewhere,
                unpointed: &mut unpointed,
                held: &held,
            },
            slug,
            check,
            &m,
            &all,
        )?;
        let mut row = Map::new();
        for path in &all {
            let id = kept_ids
                .entry(path.clone())
                .or_insert_with(|| keep(root, path));
            row.insert(path.clone(), json!(id));
        }
        blobs.insert(slug.clone(), Value::Object(row));
        if owed_pages.is_empty() {
            answer_cleared(store, slug, fp, blobs.get(slug))?;
            cleared += 1;
            continue;
        }
        sent.push((slug.clone(), fp.clone()));
        reads.insert(slug.clone(), json!(all));
        for (key, c) in owed_pages {
            blocks.entry(key.clone()).or_insert(c);
            by_page
                .entry(key)
                .or_default()
                .entry(uid.to_owned())
                .or_default()
                .insert(check.to_owned());
        }
    }
    clear_dir(out)?;
    unpointed.sort();
    unpointed.dedup();
    if sent.is_empty() {
        return Ok((None, cleared));
    }
    std::fs::create_dir_all(out).map_err(fail)?;
    let mut parts = manifest_parts(&by_page, &blocks, &modals_now, &gained);
    if !unpointed.is_empty() {
        parts.push(format!(
            "(for the session, not the agent) blocks removed that stand verbatim on a page these pop-ups do not reach: {}. A split owes nothing when the source page points to where the text now lives: `<a class=\"moved\" href=\"NNNN-<slug>.html\">...</a>` (feature 451 T185).\n",
            unpointed.join("; ")
        ));
    }
    let manifest = out.join("MANIFEST.md");
    std::fs::write(&manifest, parts.join("\n") + "\n").map_err(fail)?;
    let units_map: Map<String, Value> = sent.iter().map(|(s, fp)| (s.clone(), json!(fp))).collect();
    blobs.retain(|k, _| units_map.contains_key(k));
    let data = json!({"units": units_map, "pages": reads, "blobs": blobs});
    std::fs::write(
        out.join("triage.json"),
        pyjson::dumps(&pyjson::sorted(&data), Some(1), true) + "\n",
    )
    .map_err(fail)?;
    Ok((Some((manifest, sent.len())), cleared))
}

/// Each page's lines naming the labeled items a form unit is owed for (451 T226), one a pop-up and item.
type Gained = std::collections::BTreeMap<String, Vec<String>>;

/// A form unit's drawing pages that gained a labeled item its Guesses tab does not reference, each item's line added to `gained`; none
/// for another check.
fn held_pages(
    root: &Path,
    base: &str,
    check: &str,
    m: &Modal,
    gained: &mut Gained,
) -> Result<HashSet<String>, Fail> {
    if check != FORM_CHECK {
        return Ok(HashSet::new());
    }
    let items = modals::labeled::of_modal(root, base, m)?;
    for (page, i) in &items {
        let says = Some(&i.guess).filter(|g| !g.is_empty()).unwrap_or(&i.block);
        gained.entry(page.clone()).or_default().push(format!(
            "- UID `{}`: `{}` {} - {says}",
            m.uid(),
            i.id,
            i.label
        ));
    }
    Ok(items.into_iter().map(|(page, _)| page).collect())
}

fn name_of(p: &str) -> String {
    Path::new(p)
        .file_name()
        .map_or_else(String::new, |n| n.to_string_lossy().into_owned())
}

/// Does a unit whose checks read `unit_pages` read the page a reply line named?
fn reads_page(page: &str, unit_pages: &[String]) -> bool {
    let name = name_of(page);
    unit_pages.iter().any(|p| {
        let n = name_of(p);
        n == name || n == format!("{name}.html")
    })
}

fn as_pages(v: Option<&Value>) -> Vec<String> {
    v.and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter_map(|s| s.as_str().map(str::to_owned))
        .collect()
}

/// Apply a triage reply; the messages `make modal-triaged` prints.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn record(
    store: &Path,
    units: &Map<String, Value>,
    reply: &str,
    pages: Option<&Value>,
    blobs: Option<&Value>,
) -> Result<Vec<String>, Fail> {
    let mut slugs: Vec<&String> = units.keys().collect();
    slugs.sort();
    let uids: HashSet<&str> = slugs
        .iter()
        .map(|s| s.split_once(':').map_or("", |p| p.1))
        .collect();
    let named = read_reply(reply, &uids)?;
    let mut msgs: Vec<String> = Vec::new();
    let mut mark = touched(store)?;
    let known: Vec<String> = pages
        .and_then(Value::as_object)
        .into_iter()
        .flatten()
        .flat_map(|(_, v)| as_pages(Some(v)))
        .collect();
    for slug in slugs {
        let fp = units[slug].as_str().unwrap_or("");
        let uid = slug.split_once(':').map_or("", |p| p.1);
        let lines = named
            .iter()
            .find(|(u, _)| u == uid)
            .map_or(&[][..], |(_, v)| v.as_slice());
        let unit_pages = pages.and_then(|p| p.get(slug));
        // rule (D) - a labeled item new on a drawing page, on the pop-up's own subject, that its Guesses tab does not hold - owes its
        // form check alone, and (A)-(C) every other check (451 T226)
        let by_d = slug.starts_with(&format!("{FORM_CHECK}:"));
        let hit: Vec<&str> = lines
            .iter()
            .filter(|(_, why)| why.trim_start().starts_with("D:") == by_d)
            .filter(|(page, _)| {
                page.is_empty()
                    || pages.is_none()
                    || unit_pages.is_none()
                    || !reads_page(page, &known)
                    || reads_page(page, &as_pages(unit_pages))
            })
            .map(|(_, why)| why.as_str())
            .collect();
        if let Some(first) = hit.first() {
            mark.insert(slug.clone(), fp.to_owned());
            msgs.push(format!("touched: {slug} - {first}"));
        } else {
            let mut kept = read_answer(store, slug)
                .get("pages")
                .and_then(Value::as_object)
                .cloned()
                .unwrap_or_default();
            for (k, v) in blobs
                .and_then(|b| b.get(slug))
                .and_then(Value::as_object)
                .into_iter()
                .flatten()
            {
                kept.insert(k.clone(), v.clone());
            }
            let pages_value = Value::Object(kept);
            write_answer(store, slug, fp, "triage: untouched", Some(&pages_value))?;
        }
    }
    std::fs::create_dir_all(store).map_err(fail)?;
    let body = Value::Object(mark.into_iter().map(|(k, v)| (k, json!(v))).collect());
    std::fs::write(
        store.join(TOUCHED),
        pyjson::dumps(&pyjson::sorted(&body), Some(1), true) + "\n",
    )
    .map_err(fail)?;
    Ok(msgs)
}

/// Why `make modal-bundle` may not bundle `check` on `m` yet: a unit of it owed only a triage that has not named it.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn refusal(
    root: &Path,
    m: &Modal,
    check: &str,
    owed: Option<&[(String, String, String)]>,
) -> Result<String, Fail> {
    refusal_in(root, &owed::store(root), m, check, owed)
}

/// [`refusal`] reading the answer records `store` (feature 451 T38: `make modal-bundle` names the store its root's environment
/// gives, so a dependent's test never reads a session's exported one).
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn refusal_in(
    root: &Path,
    store: &Path,
    m: &Modal,
    check: &str,
    owed: Option<&[(String, String, String)]>,
) -> Result<String, Fail> {
    let base = merge_base(root);
    let slugs: HashSet<String> = if check == RESEARCH_AGENT {
        RESEARCH_CHECKS
            .iter()
            .map(|c| format!("{c}:{}", m.uid()))
            .collect()
    } else {
        HashSet::from([format!("{check}:{}", m.uid())])
    };
    let mut waiting: Vec<String> = pending(root, &base, store, owed)?
        .into_iter()
        .map(|p| p.0)
        .filter(|s| slugs.contains(s))
        .collect();
    if waiting.is_empty() {
        return Ok(String::new());
    }
    waiting.sort();
    Ok(format!("{} owe(s) only a TRIAGE (a page it names moved, its own words did not) - `make modal-triage` first; it sends on only the pop-ups a change bears on", waiting.join(", ")))
}

fn usage(line: &str) -> Reply {
    Reply {
        stdout: String::new(),
        stderr: format!("{line}\n"),
        code: 2,
    }
}

fn run_bundle(root: &Path, parsed: &Parsed) -> Result<Reply, Fail> {
    let out_arg = parsed.text("--out", "");
    let out = if out_arg.is_empty() {
        default_out(root)
    } else {
        PathBuf::from(out_arg)
    };
    let store = owed::store(root);
    let triaged = bundle_in(root, &out, "", &store)?;
    let linked = modals::split_links::apply(root, &store)?;
    let said: String = linked
        .iter()
        .flat_map(|l| ["modal-triage: ", l.as_str(), "\n"])
        .collect();
    let tail = match triaged {
            (None, 0) => "modal-triage: no pop-up is owed a triage\n".to_owned(),
            (None, c) => format!("modal-triage: {c} unit(s) cleared by the tool (no claim-bearing change); no agent is owed\n"),
            (Some((manifest, n)), c) => format!(
                "{}\nmodal-triage: {c} unit(s) cleared by the tool; {n} unit(s) left; dispatch the `modal-triage` agent on the MANIFEST (a session started before 2026-10-17's amendment 6 landed: restart to load it), save its reply, then `make modal-triaged BUNDLE=<dir> REPLY=<file>`\n",
                manifest.display()
            ),
        };
    Ok(Reply {
        stdout: said + &tail,
        stderr: String::new(),
        code: 0,
    })
}

/// `replay --edits F`: the tool's half of the triage over recorded edits (feature 451 T186).
fn run_replay(root: &Path, parsed: &Parsed) -> Result<Reply, Fail> {
    let landing = parsed.text("--landing", "");
    let stdout = if landing.is_empty() {
        change::replay(&read_text(Path::new(parsed.text("--edits", "")))?)?
    } else {
        replay_landing(root, landing)?
    };
    Ok(Reply {
        stdout,
        stderr: String::new(),
        code: 0,
    })
}

fn run_record(root: &Path, parsed: &Parsed) -> Result<Reply, Fail> {
    let (dir, reply_file) = (parsed.text("--bundle", ""), parsed.text("--reply", ""));
    let text = read_text(&Path::new(dir).join("triage.json"))?;
    let data: Value = serde_json::from_str(&text).map_err(fail)?;
    let units = data
        .get("units")
        .and_then(Value::as_object)
        .cloned()
        .ok_or_else(|| "triage.json: no units".to_owned())?;
    let reply = owed_reply(root, reply_file)?;
    let msgs = record(
        &owed::store(root),
        &units,
        &reply,
        data.get("pages"),
        data.get("blobs"),
    )?;
    let mut out = String::new();
    for msg in &msgs {
        let _ = writeln!(out, "modal-triaged: {msg}");
    }
    let n = msgs.iter().filter(|m| m.starts_with("touched")).count();
    let _ = writeln!(out, "modal-triaged: {n} of {} unit(s) sent on to their checks; the rest answered `triage: untouched`", units.len());
    Ok(Reply {
        stdout: out,
        stderr: String::new(),
        code: 0,
    })
}

fn owed_reply(root: &Path, path: &str) -> Result<String, Fail> {
    super::owed::reply_of(root, path)
}

/// `record modal-triage [--root DIR] bundle [--out DIR] | record --bundle DIR --reply F`.
pub fn cli(args: &[String]) -> Reply {
    let main = [Spec::value("--root")];
    let mut i = 0;
    while i < args.len() && args[i].starts_with('-') {
        i += if args[i].contains('=') { 1 } else { 2 };
    }
    let split_at = i.min(args.len());
    let parsed_main = match parse(&args[..split_at], &main) {
        Ok(p) => p,
        Err(complaint) => {
            return usage(&format!("usage: l7r-gate record modal-triage: {complaint}"))
        }
    };
    let root = std::fs::canonicalize(parsed_main.text("--root", "."))
        .unwrap_or_else(|_| parsed_main.text("--root", ".").into());
    let (verb, rest) = (
        args.get(split_at).map_or("", String::as_str),
        args.get(split_at + 1..).unwrap_or(&[]),
    );
    let (specs, runner): (&[Spec], Runner) = match verb {
        "bundle" => (&[Spec::value("--out")], run_bundle),
        "record" => (
            &[Spec::value("--bundle"), Spec::value("--reply")],
            run_record,
        ),
        "replay" => (
            &[Spec::value("--edits"), Spec::value("--landing")],
            run_replay,
        ),
        _ => {
            return usage("usage: l7r-gate record modal-triage bundle | record | replay --edits F")
        }
    };
    let parsed = match parse(rest, specs) {
        Ok(p) if verb != "record" || (!p.text("--bundle", "").is_empty() && !p.text("--reply", "").is_empty()) => p,
        Ok(_) => return usage("usage: l7r-gate record modal-triage record: the arguments --bundle and --reply are required"),
        Err(complaint) => return usage(&format!("usage: l7r-gate record modal-triage {verb}: {complaint}")),
    };
    runner(&root, &parsed).unwrap_or_else(|why| Reply {
        stdout: String::new(),
        stderr: why + "\n",
        code: 1,
    })
}

#[cfg(test)]
mod tests;
