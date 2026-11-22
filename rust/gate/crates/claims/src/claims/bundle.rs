//! The bundle `impl-drift` reads (`scripts/record/claims.py`'s `bundle`, ported by feature 449 T82): each unit's source with the lines the
//! delta changed marked, its claims, what it calls or reads as context, the cited questions as files beside the MANIFEST, and units.json
//! with the fingerprints `claims-checked` records.

#![expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "Python's `str.endswith`, which this port keeps, is case-sensitive"
)]

use std::collections::{HashMap, HashSet};
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::checks::pages::read_page;
use l7r_shared::pyjson::{dumps, sorted};
use serde_json::{json, Map, Value};

use super::context::{Gather, Tables};
use super::grammar::{Claim, POINTER};
use super::index::{
    body_of, field, is, load_map, page_blocks, page_name, source_span, Cur, PageMemo, Row, INDEX,
    QUESTIONS,
};
use super::units::{items, splitlines};
use crate::record::repo::{fail, git, read_text, Fail};
use crate::record::units::{digest, re};

/// The questions' part's answer: the numbered blocks, the snapshots, the pages read.
type Cited = (Map<String, Value>, Map<String, Value>, PageMemo);

static HUNK_LINE: LazyLock<Regex> =
    LazyLock::new(|| re(r"\A@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@"));
static BACKTICKED: LazyLock<Regex> = LazyLock::new(|| re(r"`([A-Za-z_]\w*)"));
/// A claim whose label names a distance, gap or standoff (`claims_context.DISTANCE`).
static DISTANCE: LazyLock<Regex> = LazyLock::new(|| {
    re(r"(?i)\b(?:distance|gaps?|standoff|apart|reach|clear of|off the|ft|feet)\b")
});
/// This module's patterns, for the command's start to compile side by side ([`super::warm`], feature 449 T167).
pub(super) static WARM: [&LazyLock<Regex>; 3] = [&HUNK_LINE, &BACKTICKED, &DISTANCE];

const HEAD: [&str; 5] = [
    "# Bundle for impl-drift (feature 316)\n",
    "owed-checks: impl-drift\n",
    "Each UNIT below is a function, method, class, constant or procedure section with its CLAIMS. Judge each claim against the questions it cites (inline at the end) and report one `VERDICT <key> <IN-STEP|DRIFTED|NEEDS-RESEARCH|MISLABELED|CANNOT-TELL> - <note>` line per KEY (a DRIFTED note with `fix: claim` or `fix: code` and `effect: ...` before its `[§...]`), plus `UNCLAIMED <path>::<qualname> - <decision>` for a physical decision in a unit's code that no claim covers.\n",
    "END EVERY VERDICT NOTE with the blocks of the cited questions it rests on, as numbered in the question files: `[§3, §12]`, or `[§]` when the questions are silent on the claim. A later edit to a page re-checks a claim only when a block it rests on changes (feature 318), so name every block your verdict reads.\n",
    "LINES MARKED `+` ARE THE CHANGE being landed (against main). A DRIFTED, NEEDS-RESEARCH, MISLABELED or CANNOT-TELL verdict, or an UNCLAIMED decision, that rests on NO marked line - code the change did not touch, under a claim it did not add or reword - begins its note `[outside the change]`: it is filed as a task, not held against the change (feature 405 T36). Anything the change made or could have made untrue carries no tag. A unit with no marked line has no tag to give.\n",
];

/// path -> the lines the delta added or changed, against the merge base with `base`, the working tree included (405 T36).
pub fn changed_lines(root: &Path, base: &str) -> HashMap<String, HashSet<usize>> {
    let mb = git(root, &["merge-base", "HEAD", base]);
    let mb = l7r_shared::py_text::strip(&mb);
    let mut out: HashMap<String, HashSet<usize>> = HashMap::new();
    if mb.is_empty() {
        return out;
    }
    let mut path = String::new();
    for line in splitlines(&git(root, &["diff", "-U0", mb])) {
        if line.starts_with("+++ ") {
            path = line
                .strip_prefix("+++ b/")
                .map_or_else(String::new, |_| line.chars().skip(6).collect());
        } else if let Some(m) = (!path.is_empty())
            .then(|| HUNK_LINE.captures(&line).ok().flatten())
            .flatten()
        {
            let start: usize = m[1].parse().unwrap_or(0);
            let n: usize = m.get(2).map_or(1, |g| g.as_str().parse().unwrap_or(0));
            out.entry(path.clone())
                .or_default()
                .extend(start..start + n);
        }
    }
    out
}

/// `src` (starting at line `first`) with each line the delta changed marked `+ `, the rest indented to match - or as it is when none is.
pub fn mark_changed(src: &str, first: usize, changed: Option<&HashSet<usize>>) -> String {
    let lines: Vec<&str> = src.split('\n').collect();
    let hit = |i: usize| changed.is_some_and(|c| c.contains(&(first + i)));
    if !(0..lines.len()).any(hit) {
        return src.to_owned();
    }
    lines
        .iter()
        .enumerate()
        .map(|(i, l)| format!("{}{l}", if hit(i) { "+ " } else { "  " }))
        .collect::<Vec<_>>()
        .join("\n")
}

/// The source of `path::qualname`, a Rust item by the item scan; any other reference is refused (a `.py` unit's source, read by
/// Python's syntax tree through the runner, left with the engine's Python, feature 449 T158).
pub fn context_source(root: &Path, reference: &str) -> Result<String, Fail> {
    let (path, qual) = reference.split_once("::").unwrap_or((reference, ""));
    if !path.ends_with(".rs") {
        return Err(format!("ValueError: `{reference}` is not a Rust item: a context reference names `<path>.rs::<item>`"));
    }
    let text = read_text(&root.join(path))?;
    items(&text, 0, "", false)
        .into_iter()
        .find(|i| i.0 == qual)
        .map(|i| i.5)
        .ok_or_else(|| format!("ValueError: no `{qual}` in {path}"))
}

fn dedupe(v: Vec<String>) -> Vec<String> {
    let mut seen = HashSet::new();
    v.into_iter().filter(|x| seen.insert(x.clone())).collect()
}

/// Every name a CANNOT-TELL verdict's note of `rows` puts in backticks: what a re-bundle chases.
fn asked(rows: &[&Row], index: &Map<String, Value>) -> Vec<String> {
    let mut asked = Vec::new();
    for r in rows {
        let row = index.get(&r.key).cloned().unwrap_or(Value::Null);
        if is(&row, "verdict", "CANNOT-TELL") {
            asked.extend(
                BACKTICKED
                    .captures_iter(field(&row, "note"))
                    .map_while(Result::ok)
                    .map(|c| c[1].to_owned()),
            );
        }
    }
    asked
}

/// Whether a claim of `rows` names a distance, gap or standoff: its context follows two calls down.
fn distance(rows: &[&Row]) -> bool {
    rows.iter()
        .any(|r| DISTANCE.is_match(&r.claim.label).unwrap_or(false))
}

fn unit_part(
    root: &Path,
    rows: &[&Row],
    index: &Map<String, Value>,
    marked: &HashMap<String, HashSet<usize>>,
    gather: &mut Gather,
    parts: &mut Vec<String>,
) -> Result<(), Fail> {
    let unit = &rows[0].unit;
    let lang = if unit.kind == "section" {
        "markdown"
    } else {
        "rust"
    };
    parts.push(format!(
        "## UNIT {} ({}, {}:{})\n",
        unit.uid(),
        unit.kind,
        unit.path,
        unit.lineno
    ));
    let inherited = if unit.inherited {
        " (inherited from the module docstring)"
    } else {
        ""
    };
    for r in rows {
        parts.push(format!("- KEY `{}`: `{}`{inherited}", r.key, r.claim.line));
    }
    let owed_lines: HashSet<&String> = rows.iter().map(|r| &r.claim.line).collect();
    for c in &unit.claims {
        if !owed_lines.contains(&c.line) {
            parts.push(format!(
                "- ALSO CLAIMED (checked already; context, no verdict owed): `{}`",
                c.line
            ));
        }
    }
    let (first, src) =
        source_span(root, unit)?.ok_or_else(|| format!("FileNotFoundError: {}", unit.path))?;
    parts.push(format!(
        "\n```{lang}\n{}\n```\n",
        mark_changed(&src, first, marked.get(&unit.path))
    ));
    if unit.kind != "section" {
        // the Python's rules on a Rust item (feature 449 T165), where it carried its own file's constants alone (feature 444 T16)
        let mut more = std::mem::take(&mut gather.refs);
        more.extend(super::context::rust_context(
            &mut gather.tables,
            root,
            unit,
            &src,
            distance(rows),
            &asked(rows, index),
        ));
        gather.refs = dedupe(more);
    }
    Ok(())
}

fn context_part(
    root: &Path,
    context: &[String],
    index: &Map<String, Value>,
    parts: &mut Vec<String>,
) -> Result<(), Fail> {
    if context.is_empty() {
        return Ok(());
    }
    parts.push("# Context (read it; it is not judged)\n\nCode the units above call or read, shown so a verdict can see it:\n".to_owned());
    for reference in context {
        parts.push(format!(
            "## CONTEXT {reference}\n\n```rust\n{}\n```\n",
            context_source(root, reference)?
        ));
        let prefix = format!("{reference}#");
        let own: Vec<String> = index
            .iter()
            .filter(|(k, v)| k.starts_with(&prefix) && !is(v, "verdict", "UNCLAIMED"))
            .map(|(k, v)| {
                let label = k.split_once('#').map_or("", |p| p.1);
                let verdict = v
                    .get("verdict")
                    .and_then(Value::as_str)
                    .unwrap_or("unjudged");
                format!("- its claim `{label}`: last judged {verdict}")
            })
            .collect();
        let any = !own.is_empty();
        parts.extend(own);
        if any {
            parts.push(String::new());
        }
    }
    Ok(())
}

fn questions_part(
    cur: &Cur,
    keys: &[String],
    cited: &[String],
    qdir: &Path,
    out: &Path,
    parts: &mut Vec<String>,
) -> Result<Cited, Fail> {
    std::fs::create_dir(out.join("questions")).map_err(fail)?;
    parts.push("# The cited questions\n\nEach is a file under `questions/` beside this MANIFEST - read each one a unit cites, once:\n".to_owned());
    let (mut numbered, mut snapshots, mut memo) = (Map::new(), Map::new(), PageMemo::default());
    for k in keys {
        let row = cur.get(k).unwrap_or_else(|| unreachable!());
        if row.unit.line_keyed() {
            snapshots.insert(
                row.unit.core.clone(),
                json!(row
                    .unit
                    .blocks
                    .iter()
                    .map(|b| digest(&[b]))
                    .collect::<Vec<_>>()),
            );
        }
    }
    for name in cited {
        let page = read_page(&read_text(&qdir.join(name))?);
        let (fp, blocks) = page_blocks(name, qdir, &mut memo)?.clone();
        snapshots.insert(
            fp,
            json!(blocks.iter().map(|(d, _)| d.clone()).collect::<Vec<_>>()),
        );
        let mut lines = Vec::new();
        for b in &page.blocks {
            if b.intro {
                lines.push(format!("[intro] {}", b.words));
                continue;
            }
            let n = numbered.len() + 1;
            numbered.insert(
                format!("§{n}"),
                json!(format!("{name}:{}", digest(&[&b.words]))),
            );
            lines.push(format!("[§{n}] {}", b.words));
        }
        let text = format!(
            "# {}\n({QUESTIONS}/{name})\n\n{}\n",
            page.heading,
            lines.join("\n\n")
        );
        std::fs::write(out.join("questions").join(format!("{name}.txt")), text).map_err(fail)?;
        parts.push(format!("- `questions/{name}.txt` - {}", page.heading));
    }
    Ok((numbered, snapshots, memo))
}

/// Every question page a claim cites: its backing's pointers, then each page its line names besides (an account's `; research/...`, a
/// `GUESS: research/...`), in order, once - feature 449 T241: `off_the_dike`'s claims cited 0027 in their accounts, and its bundle held
/// only the backings' 0019 and 0081, so its dike figures were judged without the page they cite.
pub(crate) fn cited_pages(c: &Claim) -> Vec<String> {
    let named = POINTER.find_iter(&c.line).map_while(Result::ok);
    let all = c.pointers.iter().map(|p| page_name(p).to_owned());
    dedupe(
        all.chain(named.map(|m| page_name(m.as_str()).to_owned()))
            .collect(),
    )
}

/// Writes the bundle for `keys` (rows of `cur`) under `out`; the MANIFEST's path.
pub fn bundle(
    root: &Path,
    cur: &Cur,
    keys: &[String],
    out: &Path,
    with: &[String],
    pages: &[String],
) -> Result<PathBuf, Fail> {
    if out.exists() {
        std::fs::remove_dir_all(out).map_err(fail)?;
    }
    std::fs::create_dir_all(out).map_err(fail)?;
    let mut by_uid: Vec<(String, Vec<&Row>)> = Vec::new();
    for k in keys {
        let row = cur.get(k).ok_or_else(|| format!("KeyError: '{k}'"))?;
        match by_uid.iter_mut().find(|(u, _)| *u == row.uid()) {
            Some((_, rows)) => rows.push(row),
            None => by_uid.push((row.uid(), vec![row])),
        }
    }
    let qdir = root.join(QUESTIONS);
    let index = load_map(&root.join(INDEX))?;
    let mut cited: Vec<String> = Vec::new();
    let mut parts: Vec<String> = HEAD.iter().map(|s| (*s).to_owned()).collect();
    let marked = changed_lines(root, "origin/main");
    let mut gather = Gather {
        refs: with.to_vec(),
        tables: Tables::default(),
    };
    for (_, rows) in &by_uid {
        unit_part(root, rows, &index, &marked, &mut gather, &mut parts)?;
        for c in &rows[0].unit.claims {
            for name in cited_pages(c) {
                if !qdir.join(&name).is_file() {
                    return Err(format!(
                        "ValueError: {}'s claim `{}` cites {QUESTIONS}/{name}, no question file under {} - fix the citation or restore the page",
                        rows[0].uid(),
                        c.label,
                        qdir.display()
                    ));
                }
                if !cited.contains(&name) {
                    cited.push(name);
                }
            }
        }
    }
    context_part(root, &gather.refs, &index, &mut parts)?;
    for p in pages {
        let p = page_name(p).to_owned();
        if !qdir.join(&p).is_file() {
            return Err(format!(
                "ValueError: PAGES: no question file {p} under {}",
                qdir.display()
            ));
        }
        if !cited.contains(&p) {
            cited.push(p);
        }
    }
    let (numbered, snapshots, mut memo) =
        questions_part(cur, keys, &cited, &qdir, out, &mut parts)?;
    std::fs::write(out.join("MANIFEST.md"), parts.join("\n") + "\n").map_err(fail)?;
    let mut units = Map::new();
    for k in keys {
        let row = cur.get(k).unwrap_or_else(|| unreachable!());
        let mut pages = Map::new();
        // every page the claim cites, not its backing's alone: `claims-checked` drops a reply's rests on a page not here (449 T241)
        for name in cited_pages(&row.claim) {
            let fp = json!(page_blocks(&name, &qdir, &mut memo)?.0);
            pages.insert(name, fp);
        }
        let mut u = json!({
            "code": row.code, "core": row.unit.core, "body": body_of(root, &row.unit)?, "claim": row.claim.normalized(),
            "research": row.research, "uid": row.uid(), "pages": pages,
        });
        if row.unit.line_keyed() {
            u["section"] = json!(row.unit.core);
        }
        // the constants a Rust unit read at its check, recorded on its row (feature 449 T166)
        if !row.unit.reads.is_empty() {
            u["reads"] = json!(row.unit.reads);
        }
        units.insert(k.clone(), u);
    }
    std::fs::write(
        out.join("units.json"),
        dumps(&sorted(&Value::Object(units)), Some(1), true) + "\n",
    )
    .map_err(fail)?;
    let blocks = json!({"numbered": numbered, "snapshots": snapshots});
    std::fs::write(
        out.join("blocks.json"),
        dumps(&sorted(&blocks), Some(1), true) + "\n",
    )
    .map_err(fail)?;
    Ok(out.join("MANIFEST.md"))
}

#[cfg(test)]
mod tests;
