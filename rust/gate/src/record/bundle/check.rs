//! A check's BUNDLE (from `check_bundle.py`, feature 250): the files one check agent needs, copied OUT of the repository with the prepass output it is handed anyway and a MANIFEST naming each copy's origin. A defined agent that reads a file under `research/` is handed every `CLAUDE.md` above it (feature 250's slice: peak context 47,700 -> 14,500 tokens on copies).
//!
//! `l7r-gate record check-bundle Q | --key KEY | --keys "K K" | --for intro-check --qs "Q Q" [...]`, the Python's command line.

use std::collections::HashSet;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::checks::pages::read_page;
use l7r_guard::shared::html_text::unescape;
use l7r_guard::shared::py_text::collapse;
use l7r_guard::shared::pyjson;
use serde_json::Value;

use super::owed::{self as bo};
use super::{
    copy, default_root, earlier, findall, head, hit, py_path, pyre, remove_tree, rstrip, shown,
    slug, today, write, Run, MANIFEST,
};
use crate::record::args::{parse_with, Parsed, Spec};
use crate::record::leaves::fragments_for;
use crate::record::modals;
use crate::record::owed::merge_base;
use crate::record::repo::{fail, git, read_text, Fail};
use crate::record::units::{read_notes, Unit};
use crate::Reply;

const REGISTRY: &str = "research/sources/010-works-cited";
/// The uncited sources' write-ups (feature 312 FR-012), bundled for `source-applicability` as a cited work's are.
const UNCITED: &str = "research/sources/040-uncited-works";
pub(crate) const VARIANTS: &str = "research/assets/glossary-variants.txt";
const CLASSES: &str = "l7r/diagram/interactive/classes";
const COMPOUND_KINDS: &str = "l7r/diagram/interactive/compound_kinds";
/// The style guide `record-style` judges against (feature 292), handed in the bundle.
pub(crate) const STYLE: &str = "research/STYLE.md";
/// A quote-check reads notes in BATCHES of at most this many bytes (feature 292: on 2026-09-29 the median notes file was 4,838 bytes, the 90th percentile 8,599).
pub(crate) const NOTES_BUDGET: usize = 12_000;

static CITED: LazyLock<Regex> =
    LazyLock::new(|| pyre(r#"<a href="[^"]*">\s*<code>([a-z0-9][a-z0-9-]*)</code>\s*</a>"#));
static URL: LazyLock<Regex> = LazyLock::new(|| pyre(r#"https?://[^\s<"]+"#));
/// A block ends at its close tag, or - HTML's implicit close - at the next block or the end of the fragment (water 170, feature 250 T75).
static BLOCK: LazyLock<Regex> = LazyLock::new(|| {
    pyre(r"(?s)<(p|li|blockquote|td|dd)\b[^>]*>.*?(?:</\1>|(?=<(?:p|li|blockquote|td|dd)\b)|\Z)")
});
pub(crate) static NOTE_LI: LazyLock<Regex> =
    LazyLock::new(|| pyre(r#"(?s)<li data-note="([^"]+)">.*?</li>\n?"#));
static NESTED_OPEN: LazyLock<Regex> = LazyLock::new(|| pyre(r"<(?:ul|ol)\b[^>]*>\s*\Z"));
static LI_TAG: LazyLock<Regex> = LazyLock::new(|| pyre(r"<(/?)li\b[^>]*>"));
static NESTED: LazyLock<Regex> = LazyLock::new(|| pyre(r"(?s)<(ul|ol)\b.*</\1>"));
static HEADING: LazyLock<Regex> = LazyLock::new(|| pyre(r"(?s)<h[23][^>]*>.*?</h[23]>"));
static TAG: LazyLock<Regex> = LazyLock::new(|| pyre(r"<[^>]+>"));
static FN_LINE: LazyLock<Regex> = LazyLock::new(|| pyre(r"^\s+fn-\d+ "));

/// WHAT EACH CHECK READS (feature 250 D14, research R5): `FOR=<agent>` keeps only that agent's parts.
pub(crate) fn parts(for_: &str) -> &'static [&'static str] {
    match for_ {
        "quote-check" => &["quote", "notes"],
        "record-format" => &["prepass", "variants", "notes"],
        "entry-drift" => &["kind"],
        "record-style" => &["style", "styleprepass", "variants"],
        "translation-check" => &["translations"],
        "intro-check" => &["intro"],
        _ => &["quote", "prepass", "variants", "registry", "kind", "notes"],
    }
}

const FORS: [&str; 7] = [
    "all",
    "entry-drift",
    "intro-check",
    "quote-check",
    "record-format",
    "record-style",
    "translation-check",
];

/// The registry keys a question's notes cite, in first-cited order.
fn cited_keys(notes_html: &str) -> Vec<String> {
    let mut out: Vec<String> = Vec::new();
    for k in findall(&CITED, notes_html, 1) {
        if !out.contains(&k) {
            out.push(k);
        }
    }
    out
}

/// The pointer a registry entry names: a closing parenthesis ends it unless the URL opened one; an entity is unescaped (feature 269).
pub(crate) fn url_of(entry_html: &str) -> String {
    let Some(found) = URL.find(entry_html).ok().flatten() else {
        return String::new();
    };
    let mut url = unescape(found.as_str());
    while url.ends_with(['.', ',', ';', ':'])
        || (url.ends_with(')') && url.matches(')').count() > url.matches('(').count())
    {
        url.pop();
    }
    url
}

/// The one registry file of a key: its four-digit prefix and the key, nothing between.
pub(crate) fn registry_entry(root: &Path, key: &str) -> Option<PathBuf> {
    let exact = pyre(&format!(r"^\d+-{}\.html\z", fancy_regex::escape(key)));
    let tail = format!("{key}.html");
    [REGISTRY, UNCITED].iter().find_map(|d| {
        let mut names: Vec<String> = std::fs::read_dir(root.join(d))
            .into_iter()
            .flatten()
            .flatten()
            .map(|e| e.file_name().to_string_lossy().into_owned())
            .filter(|n| n.ends_with(&tail) && hit(&exact, n))
            .collect();
        names.sort();
        names.first().map(|n| root.join(d).join(n))
    })
}

fn modal_named<'a>(found: &'a [modals::Modal], name: &str) -> Option<&'a modals::Modal> {
    let (module, cls) = name.rsplit_once('.').unwrap_or(("", name));
    found.iter().find(|m| {
        let (mod_, here) = m.cls.split_once('.').unwrap_or((m.cls.as_str(), ""));
        here == cls && (module.is_empty() || mod_ == module)
    })
}

/// (origin, docstring) of one modal class - what `entry-drift` compares with its section.
fn kind_docstring(root: &Path, name: &str) -> Result<Option<(String, String)>, Fail> {
    let found = modals::modals_now(root, false)?;
    Ok(modal_named(&found, name).map(|m| (m.origin.clone(), m.doc.clone())))
}

/// The page key of one modal class, or "".
fn kind_key(root: &Path, name: &str) -> Result<String, Fail> {
    let found = modals::modals_now(root, false)?;
    Ok(modal_named(&found, name).map_or_else(String::new, |m| m.key.clone()))
}

/// (start, end, whole, own) of each block; a list item holding a nested list is one block judged by its OWN words (feature 352).
fn blocks(html: &str) -> Vec<(usize, usize, String, String)> {
    let mut out = Vec::new();
    for c in BLOCK.captures_iter(html).flatten() {
        let (m, tag) = (
            c.get(0).unwrap_or_else(|| unreachable!()),
            c.get(1).map_or("", |g| g.as_str()),
        );
        let (whole, end) = (m.as_str(), m.end());
        if tag == "li" && !whole.ends_with("</li>") && hit(&NESTED_OPEN, whole) {
            let (mut depth, mut pos) = (1i64, end);
            for t in LI_TAG.captures_iter(&html[end..]).flatten() {
                depth += if t.get(1).is_some_and(|g| !g.as_str().is_empty()) {
                    -1
                } else {
                    1
                };
                if depth == 0 {
                    pos = end + t.get(0).map_or(0, |g| g.end());
                    break;
                }
            }
            if depth == 0 {
                let whole = &html[m.start()..pos];
                out.push((
                    m.start(),
                    pos,
                    whole.to_owned(),
                    NESTED.replace_all(whole, "").into_owned(),
                ));
                continue;
            }
        }
        out.push((m.start(), end, whole.to_owned(), whole.to_owned()));
    }
    out
}

/// Only the named notes of a question's notes file, in their order.
pub(crate) fn notes_subset(notes_html: &str, keys: &HashSet<String>) -> String {
    NOTE_LI
        .captures_iter(notes_html)
        .flatten()
        .filter(|c| c.get(1).is_some_and(|k| keys.contains(k.as_str())))
        .map(|c| c.get(0).map_or("", |g| g.as_str()).to_owned())
        .collect()
}

/// The question's heading and only the blocks carrying a mark for one of the keys; with `bare`, every unmarked block too (feature 314).
pub(crate) fn excerpt(fragment_html: &str, keys: &HashSet<String>, bare: bool) -> String {
    let heading = HEADING.find(fragment_html).ok().flatten();
    let marks: Vec<String> = keys.iter().map(|k| format!("data-note=\"{k}\"")).collect();
    let (mut kept, mut inside): (Vec<String>, Option<usize>) = (Vec::new(), None);
    for (start, end, whole, own) in blocks(fragment_html) {
        if inside.is_some_and(|i| start < i) {
            continue;
        }
        if marks.iter().any(|mk| own.contains(mk)) || (bare && !own.contains("data-note=")) {
            if !kept.contains(&whole) {
                kept.push(whole);
            }
            inside = Some(end);
        }
    }
    let what = format!(
        "only the blocks carrying the named notes{}",
        if bare {
            ", and every block carrying none"
        } else {
            ""
        }
    );
    format!(
        "{}<!-- an EXCERPT: {what} -->\n{}\n",
        heading.map_or_else(String::new, |h| format!("{}\n", h.as_str())),
        kept.join("\n")
    )
}

/// Every copy written into the MANIFEST under its origin, so a check reads ONE file in ONE turn (feature 250, recommendation 1).
fn inline(out: &Path, rows: &[(String, String, String)]) -> Result<String, Fail> {
    let mut parts = Vec::new();
    for (name, origin, _) in rows {
        let path = out.join(name);
        if !path.is_file()
            || matches!(
                name.as_str(),
                "glossary-variants.txt" | "quote-verbatim.json"
            )
            || name.starts_with("pages")
        {
            continue;
        }
        parts.push(format!(
            "## `{name}` - origin `{origin}`\n\n```\n{}\n```\n",
            rstrip(&read_text(&path)?)
        ));
    }
    Ok(parts.join("\n"))
}

/// An empty bundle directory; an existing one is cleared only if it is a bundle (its refusal the `SystemExit` the Python raised).
pub(crate) fn fresh(out: &Path) -> Result<(), Fail> {
    if out.exists() && std::fs::read_dir(out).map_err(fail)?.next().is_some() {
        if !out.join(MANIFEST).is_file() {
            return Err(format!(
                "check-bundle: {} exists and is not a bundle - choose another OUT",
                shown(out)
            ));
        }
        remove_tree(out)?;
    }
    std::fs::create_dir_all(out).map_err(fail)
}

/// The MANIFEST's head and every copy inlined.
pub(crate) fn manifest(
    out: &Path,
    title: &str,
    rows: &[(String, String, String)],
) -> Result<String, Fail> {
    let mut lines = vec![
        format!("# Check bundle - {title}"),
        String::new(),
        format!("Written {} by `make check-bundle`. Every file here is a COPY. Read these and nothing under the repository: reading a file there attaches about 28,000 tokens of instruction files meant for the main session (feature 250). A finding names the ORIGIN column, which is the file the session will edit.", today()),
        String::new(),
        "**Everything you need is in THIS file**, each copy under its origin below; read it once. The two grep".to_owned(),
        "targets that are not inlined - the glossary's variant index and a source's saved pages - are files beside it.".to_owned(),
        String::new(),
        "| file | origin | what it is for |".to_owned(),
        "|---|---|---|".to_owned(),
    ];
    lines.extend(
        rows.iter()
            .map(|(f, o, w)| format!("| `{f}` | `{o}` | {w} |")),
    );
    lines.push(String::new());
    lines.push(inline(out, rows)?);
    lines.push("Reply with your report: the counts on the first line, then only what the session must act on (your contract gives the form).".to_owned());
    lines.push(String::new());
    Ok(lines.join("\n"))
}

/// The MANIFEST's account of THE CHANGE (feature 375, FR-006): each page's blocks and notes whose words differ from the merge base.
fn changed_section(root: &Path, fragments: &[String]) -> Result<String, Fail> {
    let base = merge_base(root);
    let mut lines = Vec::new();
    for rel in fragments {
        let path = root.join(rel);
        let now = if path.is_file() {
            read_text(&path)?
        } else {
            String::new()
        };
        let was = if base.is_empty() {
            String::new()
        } else {
            git(root, &["show", &format!("{base}:{rel}")])
        };
        if rel.ends_with(".notes.html") {
            let (before, after) = (read_notes(&was, ""), read_notes(&now, ""));
            let mut keys: Vec<&String> = after.iter().map(|(k, _)| k).collect();
            keys.sort();
            lines.extend(
                keys.into_iter()
                    .filter(|k| before.get(k) != after.get(k))
                    .map(|k| format!("changed-note: {rel} | {k}")),
            );
        } else {
            let old: HashSet<String> = read_page(&was)
                .blocks
                .into_iter()
                .map(|b| b.words)
                .collect();
            lines.extend(
                read_page(&now)
                    .blocks
                    .iter()
                    .filter(|b| !old.contains(&b.words))
                    .map(|b| format!("changed-block: {rel} | {}", head(&b.words, 120))),
            );
        }
    }
    let body = if lines.is_empty() {
        "(none - every block and note predates this change: every finding is OUTSIDE THE CHANGE)"
            .to_owned()
    } else {
        lines.join("\n")
    };
    Ok(format!("\n## The change (feature 375, FR-006)\n\nThe blocks and notes this delta wrote or rewrote. A finding on anything NOT listed here is reported under a closing `OUTSIDE THE CHANGE` heading, one line each - `- <origin file> | <the block, a few words> | <the finding>` - and is filed as a row, not fixed in this change.\n\n{body}\n"))
}

/// A MANIFEST with the earlier rounds of the checks it owes (feature 393).
pub(crate) fn with_earlier(root: &Path, out: &Path, text: &str) -> Result<String, Fail> {
    Ok(format!("{text}{}", earlier::section(root, out, text)?))
}

/// A helper's output and exit: `translation-owed` is the port in this process, the rest the runner's (feature 383 D6).
pub(crate) fn run_script(
    run: &mut Run,
    name: &str,
    args: &[String],
    root: &Path,
) -> Result<(i32, String), Fail> {
    if name == "translation_owed" {
        let got = crate::record::translation::cli(args);
        return Ok((got.code, got.stdout + &got.stderr));
    }
    run.door.helper(name, args, root)
}

/// What one question bundle carries.
pub(crate) struct Entry<'a> {
    pub(crate) q: &'a str,
    pub(crate) out: PathBuf,
    pub(crate) extra: &'a [String],
    pub(crate) quotes: bool,
    pub(crate) kind: &'a str,
    pub(crate) notes: HashSet<String>,
    pub(crate) for_: &'a str,
    pub(crate) owed: String,
    pub(crate) bare: bool,
    pub(crate) images: &'a [String],
}

pub(crate) type Rows = Vec<(String, String, String)>;

/// A helper's text written to `file`, its row added; Some(exit) where it failed, its output on stderr.
pub(crate) fn helper_part(
    run: &mut Run,
    root: &Path,
    out: &Path,
    rows: &mut Rows,
    (name, args): (&str, Vec<String>),
    (file, origin, what): (&str, String, &str),
) -> Result<Option<i32>, Fail> {
    let (code, text) = run_script(run, name, &args, root)?;
    write(&out.join(file), &text)?;
    rows.push((file.to_owned(), origin, what.to_owned()));
    if code != 0 {
        run.warn(&text);
        return Ok(Some(code));
    }
    Ok(None)
}

fn copies(
    root: &Path,
    e: &Entry<'_>,
    fragments: &[String],
    rows: &mut Rows,
    keys: &mut Vec<String>,
) -> Result<(), Fail> {
    let want = parts(e.for_);
    for rel in fragments {
        let notes_file = rel.ends_with(".notes.html");
        if notes_file
            && !want.contains(&"notes")
            && (e.for_ != "record-style" || e.extra.is_empty())
        {
            continue;
        }
        let mut what = if notes_file {
            "the question's footnotes"
        } else {
            "the question, as its reader meets it"
        }
        .to_owned();
        let name = copy(&root.join(rel), &e.out, None)?;
        if !e.notes.is_empty() {
            let text = read_text(&root.join(rel))?;
            let cut = if notes_file {
                notes_subset(&text, &e.notes)
            } else {
                excerpt(&text, &e.notes, e.bare)
            };
            write(&e.out.join(&name), &cut)?;
            let mut named: Vec<&String> = e.notes.iter().collect();
            named.sort();
            let _ = write!(
                what,
                " - ONLY the notes {} and the blocks that carry them{}",
                named
                    .iter()
                    .map(|s| s.as_str())
                    .collect::<Vec<_>>()
                    .join(", "),
                if e.bare {
                    ", and every block that carries no note"
                } else {
                    ""
                }
            );
        }
        if notes_file {
            keys.extend(cited_keys(&read_text(&e.out.join(&name))?));
        }
        rows.push((name, rel.clone(), what));
    }
    Ok(())
}

/// One question's bundle (`entry_bundle`).
pub(crate) fn entry_bundle(run: &mut Run, root: &Path, e: &Entry<'_>) -> Result<i32, Fail> {
    let q = e.q;
    let fragments = fragments_for(q, root);
    if fragments.is_empty() {
        run.warn(&format!("check-bundle: Q={} names no question - name one by its number, e.g. make check-bundle Q=0041", super::py_repr(q)));
        return Ok(2);
    }
    let found_kind = if e.kind.is_empty() {
        None
    } else {
        kind_docstring(root, e.kind)?
    };
    if !e.kind.is_empty() && found_kind.is_none() {
        run.warn(&format!("check-bundle: no modal class {} under {CLASSES} or {COMPOUND_KINDS} - KIND is the modal's class name as written in its classes file, case and all (KIND=Stables, or household.Well when two modules share a name)", super::py_repr(e.kind)));
        return Ok(2);
    }
    fresh(&e.out)?;
    let (mut rows, mut keys): (Rows, Vec<String>) = (Vec::new(), Vec::new());
    if let Some((origin, doc)) = &found_kind {
        write(
            &e.out.join("kind.txt"),
            &format!("class {}  ({origin})\n\n{doc}\n", e.kind),
        )?;
        rows.push((
            "kind.txt".to_owned(),
            origin.clone(),
            format!(
                "for entry-drift: the modal `{}` - its docstring, which IS what the map says",
                e.kind
            ),
        ));
    }
    copies(root, e, &fragments, &mut rows, &mut keys)?;
    if let Some(code) = super::parts::helper_parts(run, root, e, &mut rows, &keys)? {
        return Ok(code);
    }
    let out = &e.out;
    let title = format!(
        "question {q}{}",
        if e.for_ == "all" {
            String::new()
        } else {
            format!(", for {}", e.for_)
        }
    );
    let text = manifest(out, &title, &rows)?
        + &e.owed
        + &changed_section(root, &fragments)?
        + &super::keys::images_section(out, e.images)?;
    write(&out.join(MANIFEST), &with_earlier(root, out, &text)?)?;
    run.say(&format!(
        "check-bundle: {} file(s) in {} - hand the agent {}",
        rows.len(),
        shown(out),
        shown(&out.join(MANIFEST))
    ));
    Ok(0)
}

/// `make notes`: the named notes of one question and the blocks carrying them, and nothing else (feature 250, recommendation 4).
fn print_notes(run: &mut Run, root: &Path, q: &str, keys: &HashSet<String>) -> Result<i32, Fail> {
    let found = fragments_for(q, root);
    if found.is_empty() || keys.is_empty() {
        run.warn(&format!(
            "notes: Q={q} KEYS=<key,key> - {}",
            if found.is_empty() {
                "no such question"
            } else {
                "name the keys"
            }
        ));
        return Ok(2);
    }
    for rel in found {
        let text = read_text(&root.join(&rel))?;
        let body = if rel.ends_with(".notes.html") {
            notes_subset(&text, keys)
        } else {
            excerpt(&text, keys, false)
        };
        run.say(&format!("== {rel}\n{body}"));
    }
    Ok(0)
}

/// The quote-verbatim report cut to the notes being re-checked (whitespace-collapsed both sides, feature 250 2d).
pub(crate) fn flat(text: &str) -> String {
    collapse(text)
}

/// The tag-stripped text (`re.sub(r"<[^>]+>", "", text)`).
pub(crate) fn untagged(text: &str) -> String {
    TAG.replace_all(text, "").into_owned()
}

/// The report's lines with its per-footnote lines dropped.
pub(crate) fn report_lines(full_text: &str) -> Vec<String> {
    crate::record::py_lines(full_text)
        .into_iter()
        .filter(|ln| !hit(&FN_LINE, ln))
        .map(str::to_owned)
        .collect()
}

/// A split bundle's closing word: each batch's MANIFEST, and NO top-level one (feature 374, round arbiter hour 4).
fn batched_manifests(out: &Path, nums: &[usize]) -> String {
    let _ = std::fs::remove_file(out.join(MANIFEST));
    let mut lines = vec![format!("check-bundle: {} batches - dispatch each MANIFEST below, one agent each (there is no top-level one):", nums.len())];
    lines.extend(nums.iter().map(|i| {
        format!(
            "  {}",
            shown(&out.join(format!("batch-{i}")).join(MANIFEST))
        )
    }));
    lines.join("\n")
}

/// The question's note keys in runs of at most `NOTES_BUDGET` bytes each, in note order.
fn note_batches(root: &Path, q: &str) -> Result<Vec<Vec<String>>, Fail> {
    let (mut batches, mut size): (Vec<Vec<String>>, usize) = (vec![Vec::new()], 0);
    for rel in fragments_for(q, root) {
        if !rel.ends_with(".notes.html") {
            continue;
        }
        let text = read_text(&root.join(&rel))?;
        for c in NOTE_LI.captures_iter(&text).flatten() {
            let n = c.get(0).map_or(0, |g| g.as_str().len());
            if batches.last().is_some_and(|b| !b.is_empty()) && size + n > NOTES_BUDGET {
                batches.push(Vec::new());
                size = 0;
            }
            if let Some(last) = batches.last_mut() {
                last.push(c.get(1).map_or("", |g| g.as_str()).to_owned());
            }
            size += n;
        }
    }
    Ok(batches.into_iter().filter(|b| !b.is_empty()).collect())
}

fn specs() -> [Spec; 16] {
    [
        Spec::value("--key"),
        Spec::value("--keys"),
        Spec::flag("--whole"),
        Spec::value("--question"),
        Spec::value("--out"),
        Spec::list("--extra"),
        Spec::value("--notes"),
        Spec::flag("--print-notes"),
        Spec::value("--for"),
        Spec::value("--kind"),
        Spec::flag("--no-quotes"),
        Spec::list("--images"),
        Spec::value("--root"),
        Spec::value("--qs"),
        Spec::value("--not-owed-ok"),
        Spec::value("--new"),
    ]
}

fn out_or(given: &str, default: String) -> PathBuf {
    if given.is_empty() {
        default_root().join(default)
    } else {
        py_path(given)
    }
}

/// `record check-bundle ...`.
pub(crate) fn cli(args: &[String]) -> Reply {
    let p = match parse_with(args, &specs(), 1) {
        Ok(p) if FORS.contains(&p.text("--for", "all")) => p,
        Ok(p) => {
            return super::usage(
                "check-bundle",
                &format!(
                    "argument --for: invalid choice: {}",
                    super::py_repr(p.text("--for", ""))
                ),
            )
        }
        Err(complaint) => return super::usage("check-bundle", &complaint),
    };
    let root = super::resolve(p.text("--root", "."));
    let mut run = Run::new(&root);
    let done = main(&mut run, &root, &p);
    run.reply(done)
}

/// A source's, several sources' or the intro-check bundle; None for a question's.
fn source_main(run: &mut Run, root: &Path, p: &Parsed) -> Result<Option<i32>, Fail> {
    let (q, for_, not_owed_ok, new) = (
        p.positional.first().map_or("", String::as_str),
        p.text("--for", "all"),
        p.text("--not-owed-ok", ""),
        p.text("--new", ""),
    );
    if !p.text("--keys", "").is_empty() {
        let keys: Vec<String> = p
            .text("--keys", "")
            .split_whitespace()
            .map(str::to_owned)
            .collect();
        return super::keys::keys_bundle(run, root, &keys, p.text("--out", ""), not_owed_ok)
            .map(Some);
    }
    let key = p.text("--key", "");
    if !key.is_empty() {
        let whole = p.on("--whole");
        let (rows, checks, refusal) = bo::owed_for_key(root, key, whole, not_owed_ok, new, None)?;
        if !refusal.is_empty() {
            run.warn(&format!("check-bundle: REFUSED - {refusal}"));
            return Ok(Some(3));
        }
        let out = out_or(
            p.text("--out", ""),
            format!("key-{key}{}", if whole { "-whole" } else { "" }),
        );
        let owed = bo::manifest_lines(
            &rows,
            &checks,
            if not_owed_ok.is_empty() {
                new
            } else {
                not_owed_ok
            },
        );
        let read = (whole, p.text("--question", ""));
        return super::keys::key_bundle(
            run,
            root,
            key,
            &out,
            read,
            &owed,
            &rows,
            p.list("--images"),
        )
        .map(Some);
    }
    if for_ == "intro-check" {
        let qs = if p.text("--qs", "").is_empty() {
            q
        } else {
            p.text("--qs", "")
        };
        let qs: Vec<String> = qs.split_whitespace().map(str::to_owned).collect();
        return super::keys::intro_bundle(run, root, &qs, p.text("--out", ""), not_owed_ok)
            .map(Some);
    }
    Ok(None)
}

/// One batch of a split quote-check bundle: its number, its notes, the units it can answer.
type Batch = (usize, HashSet<String>, Vec<Unit>);

/// A large question's quote-check bundles, each batch only where it owes something (feature 385 T02, plan D12).
fn batched<'a>(
    run: &mut Run,
    root: &Path,
    batches: &[Vec<String>],
    rows: &[Unit],
    (out, checks, bare): (&Path, &str, bool),
    entry: &dyn Fn(PathBuf, HashSet<String>, String, bool) -> Entry<'a>,
    not_owed_ok: &str,
) -> Result<i32, Fail> {
    run.say(&format!(
        "check-bundle: the notes are over {} bytes - {} quote-check bundles, one agent each:",
        super::thousands(NOTES_BUDGET),
        batches.len()
    ));
    let all: Vec<Batch> = batches
        .iter()
        .enumerate()
        .map(|(i, b)| {
            let set: HashSet<String> = b.iter().cloned().collect();
            let us = bo::batch_units(rows, &set, i == 0);
            (i + 1, set, us)
        })
        .collect();
    let owing: Vec<&Batch> = all.iter().filter(|(_, _, us)| !us.is_empty()).collect();
    let chosen: Vec<&Batch> = if owing.is_empty() {
        all.iter().collect()
    } else {
        owing
    };
    let mut codes = Vec::new();
    for (i, set, us) in &chosen {
        let e = entry(
            out.join(format!("batch-{i}")),
            set.clone(),
            bo::manifest_lines(us, checks, not_owed_ok),
            bare && *i == 1,
        );
        codes.push(entry_bundle(run, root, &e)?);
    }
    let nums: Vec<usize> = chosen.iter().map(|(i, _, _)| *i).collect();
    run.say(&batched_manifests(out, &nums));
    Ok(codes.into_iter().max().unwrap_or(0))
}

/// ONE modal's entry-drift units (feature 319, G4), and the refusal where none is owed and no reason is given.
fn kind_rows(
    root: &Path,
    kind: &str,
    rows: &[Unit],
    not_owed_ok: &str,
) -> Result<(Vec<Unit>, String), Fail> {
    let kept = bo::kind_units(rows, &kind_key(root, kind)?);
    let refused = kept.is_empty() && not_owed_ok.is_empty();
    let why = if refused {
        format!(
            "no entry-drift is owed on the modal {} by this delta",
            super::py_repr(kind)
        )
    } else {
        String::new()
    };
    Ok((kept, why))
}

fn main(run: &mut Run, root: &Path, p: &Parsed) -> Result<i32, Fail> {
    if let Some(code) = source_main(run, root, p)? {
        return Ok(code);
    }
    let (q, for_, not_owed_ok) = (
        p.positional.first().map_or("", String::as_str),
        p.text("--for", "all"),
        p.text("--not-owed-ok", ""),
    );
    if q.is_empty() {
        run.err.push_str("usage: l7r-gate record check-bundle\ncheck-bundle: error: Q (a question's number), or --key\n");
        return Ok(2);
    }
    let mut wanted: HashSet<String> = p
        .text("--notes", "")
        .split(',')
        .map(|k| {
            k.trim_matches(l7r_guard::shared::py_text::is_space)
                .to_owned()
        })
        .filter(|k| !k.is_empty())
        .collect();
    if p.on("--print-notes") {
        return print_notes(run, root, q, &wanted);
    }
    if fragments_for(q, root).is_empty() {
        run.warn(&format!("check-bundle: Q={} names no question - name one by its number, e.g. make check-bundle Q=0041", super::py_repr(q)));
        return Ok(2);
    }
    let (mut rows, checks, mut refusal) = bo::owed_for_question(root, q, for_, not_owed_ok, None)?;
    let kind = p.text("--kind", "");
    if refusal.is_empty() && for_ == "entry-drift" && !kind.is_empty() {
        (rows, refusal) = kind_rows(root, kind, &rows, not_owed_ok)?;
    }
    if !refusal.is_empty() {
        run.warn(&format!("check-bundle: REFUSED - {refusal}"));
        return Ok(3);
    }
    if for_ == "quote-check" && wanted.is_empty() && not_owed_ok.is_empty() {
        wanted = bo::owed_notes(&rows);
    }
    let owed = bo::manifest_lines(&rows, &checks, not_owed_ok);
    let out = out_or(
        p.text("--out", ""),
        format!(
            "q-{}{}",
            slug(q),
            if for_ == "all" {
                String::new()
            } else {
                format!("-{for_}")
            }
        ),
    );
    let batches = if wanted.is_empty() && for_ == "quote-check" {
        note_batches(root, q)?
    } else {
        Vec::new()
    };
    let bare = for_ == "quote-check" && bo::unfootnoted_owed(&rows);
    let entry = |out: PathBuf, notes: HashSet<String>, owed: String, bare: bool| Entry {
        q,
        out,
        extra: p.list("--extra"),
        quotes: !p.on("--no-quotes"),
        kind,
        notes,
        for_,
        owed,
        bare,
        images: p.list("--images"),
    };
    if batches.len() > 1 {
        return batched(
            run,
            root,
            &batches,
            &rows,
            (&out, &checks, bare),
            &entry,
            not_owed_ok,
        );
    }
    entry_bundle(run, root, &entry(out, wanted, owed, bare))
}

/// A quotation report as JSON: `json.dumps(data, ensure_ascii=False, indent=1) + "\n"`.
pub(crate) fn dumps(data: &Value) -> String {
    pyjson::dumps(data, Some(1), false) + "\n"
}

#[cfg(test)]
mod tests;
