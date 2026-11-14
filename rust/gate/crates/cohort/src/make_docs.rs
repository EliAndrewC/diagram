//! `l7r-gate make-docs [root] [--write|--check]` - the make-target reference generated from the Makefile itself, so it cannot go stale:
//! `make docs` writes `docs/make-targets.html`, and `make static`, the push's `make-docs` row and the land's first pass check it (the
//! last two in process, [`check`] and [`write`]). Ported whole from `scripts/make-docs.py` by feature 449 T135
//! (`ask:449-phase3-remainder`); it lives in `cohort` because the push and the land, which build on it, ask it in process.
//!
//! WHY (GM 2026-09-05): after two rounds of auditing targets by hand - one of which declared everything valid and was then contradicted
//! the moment the GM asked about specific targets - the durable answer is to stop hand-maintaining the list. *"our makefile can create
//! its own documentation ... the make targets and the explanation of what they do is pulled from the makefile and its comments
//! automatically."*
//!
//! THERE IS NO PYDOC FOR MAKE. The `##` help convention this Makefile used is the de facto standard ("self-documenting makefile") and
//! it is a PARSING BASE, not a generator: one flat alphabetical list with no grouping, no arguments column and no HTML. This adds the
//! three things it lacks, and nothing else.
//!
//! THE CATEGORY LIVES ON THE TARGET, DELIBERATELY. Grouping is editorial - it exists nowhere else in the code, so it cannot be derived
//! (constitution X clause 14) - so it sits where it cannot be forgotten: a `[category]` tag inside the target's own `##` line. `--check`
//! FAILS on a target with help text and no tag, caught at the gate rather than months later.
//!
//! WHAT COUNTS AS A TARGET is derived, not listed: every rule with a recipe and a `##` line. A target with no help text is REPORTED (the
//! audit that prompted this found thirteen, `quick`, `maps` and `reference` among them, invisible to `make help` for months).
//!
//! The page names this command as its generator, where it named the deleted `scripts/make-docs.py` (regenerated in T135's cut, on the
//! T87 and T91 precedent that a message naming a deleted file names the Rust).

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::checks::resolved;
use l7r_guard::shared::py_text::{strip, SPACE_CLASS};
use l7r_guard::shared::speckit::{py_path, splitlines};

use crate::Reply;

const OUT: &str = "docs/make-targets.html";

fn re(pattern: &str) -> Regex {
    Regex::new(&pattern.replace(r"\s", &format!("[{SPACE_CLASS}]")))
        .unwrap_or_else(|e| unreachable!("{e}"))
}

// Python's `re` patterns, `\s` its whitespace (`SPACE_CLASS`) and `\w` the same Unicode word class
static DOCUMENTED: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^([a-z][\w-]*):(?!=)[^\n#]*##\s*(.*)$"));
static TAG: LazyLock<Regex> = LazyLock::new(|| re(r"^\[([\w-]+)\]\s*(.*)"));
static FLAG: LazyLock<Regex> =
    LazyLock::new(|| re(r"^\{(internal|inactive)(?::\s*([^}]*))?\}\s*(.*)"));
static ARG: LazyLock<Regex> = LazyLock::new(|| re(r"\b([A-Z][A-Z0-9_]*)="));
static ARG_DOC: LazyLock<Regex> = LazyLock::new(|| re(r"^##\s+([A-Z][A-Z0-9_]*)=(.*?)\s\s+(.*)$"));
static WITH_RULE: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^([a-z][\w-]*(?:\s+[a-z][\w-]*)*):(?!=)[^\n]*\n(?:\t[^\n]*\n)+"));
static TRAILING_ARGS: LazyLock<Regex> = LazyLock::new(|| re(r"\s{2,}[A-Z][A-Z0-9_]*=.*$"));

/// The sections' order and prose. A category the Makefile uses that is missing here is an ERROR, not a silent "other" bucket - an
/// unrecognized tag is almost always a typo.
const SECTIONS: [(&str, &str, &str); 6] = [
    ("tests", "Tests", "The four tiers, cheapest first. Where a test LIVES decides when it runs, so these differ by scope rather than by filter."),
    ("maps", "Maps", "Generating and checking the pool. `maps` picks its own scope - the reference hamlet alone after a failure, the whole tier after a clean run."),
    ("diagnostics", "Diagnostics", "Read-only questions about a finished map or a generator's decisions. None of these decides what ships."),
    ("performance", "Performance", "The bookends and the three bands. A run that got slower owes records before the push."),
    ("static", "Static checks", "What the gate runs before it spends anything on a map roll."),
    ("project", "Project state", "Switches, audits and the records that make the tooling's own behavior reviewable."),
];

/// One `##  NAME=<what>  description` line under a target.
struct ArgDoc {
    name: String,
    takes: String,
    desc: String,
}

/// One documented target.
struct Row {
    name: String,
    category: String,
    help: String,
    args: String,
    flag: String,
    why: String,
    argdocs: Vec<ArgDoc>,
}

fn group<'t>(caps: &fancy_regex::Captures<'t>, i: usize) -> &'t str {
    caps.get(i).map_or("", |m| m.as_str())
}

/// Every documented target in name order, and the names that have a recipe but no `##` line.
fn parse(text: &str) -> (Vec<Row>, Vec<String>) {
    let mut documented = Vec::new();
    for caps in DOCUMENTED.captures_iter(text).flatten() {
        let (name, mut rest) = (
            group(&caps, 1).to_owned(),
            strip(group(&caps, 2)).to_owned(),
        );
        let (mut category, mut flag, mut why) = (String::new(), String::new(), String::new());
        if let Some(tag) = TAG.captures(&rest.clone()).ok().flatten() {
            group(&tag, 1).clone_into(&mut category);
            strip(group(&tag, 2)).clone_into(&mut rest);
        }
        // {internal} - nobody types this; a recipe or a script calls it. {inactive: why} - the target exists and is kept on purpose, but
        // does nothing today. Two SEPARATE designations because they answer different questions (GM 2026-09-06): "would I ever run
        // this?" and "does running it do anything today?" - a target can be neither, either, or both
        if let Some(fl) = FLAG.captures(&rest.clone()).ok().flatten() {
            group(&fl, 1).clone_into(&mut flag);
            strip(group(&fl, 2)).clone_into(&mut why);
            strip(group(&fl, 3)).clone_into(&mut rest);
        }
        // arguments are written as WORD= in the help line; the prose is what remains
        let mut args: Vec<String> = ARG
            .captures_iter(&rest)
            .flatten()
            .map(|c| group(&c, 1).to_owned())
            .collect();
        // ...and each may be DOCUMENTED on its own `##  NAME=<what>  description` line beneath the target (GM 2026-09-06: knowing an
        // argument EXISTS is not knowing what it does). Make reads these as comments, so the recipe is unaffected. NOTE the leading
        // newlines dropped: `$` matches BEFORE the newline, so what follows the match starts with it, and an empty first line once broke
        // the loop at once and silently produced no argument docs at all
        let end = caps.get(0).map_or(0, |m| m.end());
        let mut argdocs = Vec::new();
        for line in splitlines(text[end..].trim_start_matches('\n')) {
            // the VALUE may hold spaces (`FILE=<test path>`), so it runs non-greedily up to the two-space separator; `(\S*)` broke on
            // those and, because a miss ENDS the loop, dropped every argument of four targets rather than the one line
            let Some(am) = ARG_DOC.captures(line).ok().flatten() else {
                break;
            };
            argdocs.push(ArgDoc {
                name: group(&am, 1).to_owned(),
                takes: group(&am, 2).to_owned(),
                desc: strip(group(&am, 3)).to_owned(),
            });
        }
        for a in &argdocs {
            if !args.contains(&a.name) {
                args.push(a.name.clone());
            }
        }
        let args: BTreeSet<String> = args.into_iter().collect();
        documented.push(Row {
            name,
            category,
            help: rest,
            args: args.into_iter().collect::<Vec<_>>().join(" "),
            flag,
            why,
            argdocs,
        });
    }
    let mut with_rule = BTreeSet::new();
    for caps in WITH_RULE.captures_iter(text).flatten() {
        with_rule.extend(
            l7r_guard::shared::py_text::split(group(&caps, 1))
                .into_iter()
                .map(str::to_owned),
        );
    }
    let named: BTreeSet<&str> = documented.iter().map(|r| r.name.as_str()).collect();
    let undocumented = with_rule
        .iter()
        .filter(|n| !named.contains(n.as_str()))
        .cloned()
        .collect();
    documented.sort_by(|a, b| a.name.cmp(&b.name));
    (documented, undocumented)
}

/// `html.escape(text)`: `&`, `<`, `>`, `"` and `'`.
fn escape(text: &str) -> String {
    text.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
        .replace('\'', "&#x27;")
}

/// The arguments column: each documented argument on its own line with what it DOES. An undocumented argument still shows (its bare
/// name), so the page never hides one - it just cannot say what it means until somebody writes its `##` line.
fn args_cell(r: &Row) -> String {
    if r.argdocs.is_empty() {
        let shown = escape(&r.args);
        return if shown.is_empty() {
            "&ndash;".to_owned()
        } else {
            shown
        };
    }
    let named: BTreeSet<&str> = r.argdocs.iter().map(|d| d.name.as_str()).collect();
    let mut cell = String::new();
    for d in &r.argdocs {
        let takes = if d.takes.is_empty() { "1" } else { &d.takes };
        let _ = write!(
            cell,
            "<div class=ad><span class=an>{}={}</span><span class=aw>{}</span></div>",
            escape(&d.name),
            escape(takes),
            escape(&d.desc)
        );
    }
    for a in r
        .args
        .split(' ')
        .filter(|a| !a.is_empty() && !named.contains(a))
    {
        let _ = write!(
            cell,
            "<div class=ad><span class=an>{}</span></div>",
            escape(a)
        );
    }
    cell
}

const HEAD: &str = "<!-- GENERATED BY `l7r-gate make-docs` (rust/gate/crates/cohort/src/make_docs.rs) FROM THE MAKEFILE - DO NOT EDIT.
     Edit the target's `##` line in Makefile and run `make docs`.
     `l7r-gate make-docs --check` fails the gate when this file is stale. -->
<title>make targets</title>
<style>
:root{--bg:#fbfaf7;--fg:#1d1b17;--mut:#6b6560;--line:#ded8cf;--acc:#7a4a20;--code:#f2eee7}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#171614;--fg:#e9e5de;--mut:#a09a92;--line:#33302b;--acc:#d0a06a;--code:#22201d}}
:root[data-theme=dark]{--bg:#171614;--fg:#e9e5de;--mut:#a09a92;--line:#33302b;--acc:#d0a06a;--code:#22201d}
body{background:var(--bg);color:var(--fg);font:15px/1.55 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;margin:0;padding:2.5rem 1.25rem 5rem}
main{max-width:62rem;margin:0 auto}
h1{font-size:1.7rem;margin:0 0 .3rem}h2{font-size:1.15rem;margin:2.6rem 0 .3rem;color:var(--acc)}
p.lede{color:var(--mut);margin:.2rem 0 1.4rem}p.sec{color:var(--mut);margin:.2rem 0 .8rem;font-size:.93rem}
div.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;margin:.4rem 0 .6rem;font-size:.93rem}
th,td{text-align:left;vertical-align:top;padding:.42rem .6rem;border-bottom:1px solid var(--line)}
th{font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;color:var(--mut);font-weight:600}
td.n{white-space:nowrap;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
td.a{white-space:normal;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--mut);font-size:.86rem;min-width:15rem}
div.ad{margin:0 0 .28em}span.an{display:inline-block;color:var(--fg);font-weight:600}
span.aw{display:block;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:.92em;line-height:1.35;margin-top:.1em}
code{background:var(--code);padding:.08em .32em;border-radius:3px;font-size:.9em}
span.b{margin-left:.5em;font-size:.68rem;text-transform:uppercase;letter-spacing:.04em;padding:.1em .45em;border-radius:3px;background:var(--code);color:var(--mut);border:1px solid var(--line);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
span.b.off{color:#9a3d2a;border-color:#c8907f}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]) span.b.off{color:#e0a08c;border-color:#7a4436}}
:root[data-theme=dark] span.b.off{color:#e0a08c;border-color:#7a4436}
span.w{color:var(--mut);font-style:italic}
footer{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--line);color:var(--mut);font-size:.86rem}
</style>
<main>
<h1>make targets</h1>";

/// The page.
fn render(rows: &[Row], undocumented: &[String]) -> String {
    let mut by_cat: BTreeMap<&str, Vec<&Row>> = BTreeMap::new();
    for r in rows {
        by_cat.entry(r.category.as_str()).or_default().push(r);
    }
    let mut parts = vec![
        HEAD.to_owned(),
        format!("<p class=lede>Every target in the diagram skill's Makefile, grouped. {} documented. Generated from the Makefile - edit the target's <code>##</code> line, not this page.</p>", rows.len()),
    ];
    let mut seen = BTreeSet::new();
    for (key, title, blurb) in SECTIONS {
        let Some(group) = by_cat.get(key) else {
            continue;
        };
        seen.insert(key);
        parts.push(format!("<h2>{}</h2>", escape(title)));
        parts.push(format!("<p class=sec>{}</p>", escape(blurb)));
        parts.push("<div class=scroll><table><tr><th>target</th><th>arguments</th><th>what it is</th></tr>".to_owned());
        for r in group {
            let prose = TRAILING_ARGS.replace_all(&r.help, "");
            let badge = match r.flag.as_str() {
                "internal" => "<span class=b title='called by a recipe or a script - you would not type this'>internal</span>".to_owned(),
                "inactive" => format!(
                    "<span class='b off' title=\"{}\">inactive</span>",
                    escape(if r.why.is_empty() { "currently does nothing" } else { &r.why })
                ),
                _ => String::new(),
            };
            let note = if r.flag == "inactive" && !r.why.is_empty() {
                format!(" <span class=w>{}</span>", escape(&r.why))
            } else {
                String::new()
            };
            parts.push(format!(
                "<tr><td class=n>make {}{badge}</td><td class=a>{}</td><td>{}{note}</td></tr>",
                escape(&r.name),
                args_cell(r),
                escape(strip(&prose))
            ));
        }
        parts.push("</table></div>".to_owned());
    }
    let stray: Vec<&str> = by_cat
        .keys()
        .copied()
        .filter(|k| !k.is_empty() && !seen.contains(k))
        .collect();
    if !stray.is_empty() {
        parts.push(format!(
            "<p class=sec><b>Unrecognized categories:</b> {}</p>",
            escape(&stray.join(", "))
        ));
    }
    if !undocumented.is_empty() {
        parts.push("<h2>Undocumented</h2>".to_owned());
        parts.push("<p class=sec>These have a recipe but no <code>##</code> line, so they appear in no help output. Each is either an internal helper or an oversight.</p>".to_owned());
        parts.push("<div class=scroll><table><tr><th>target</th></tr>".to_owned());
        parts.extend(
            undocumented
                .iter()
                .map(|n| format!("<tr><td class=n>make {}</td></tr>", escape(n))),
        );
        parts.push("</table></div>".to_owned());
    }
    parts.push("<footer>Generated by <code>l7r-gate make-docs</code>. <code>make docs</code> regenerates it; the gate fails if it is stale.</footer>".to_owned());
    parts.push("</main>".to_owned());
    parts.join("\n") + "\n"
}

/// A file as `read_text(encoding="utf-8")` reads it: strictly UTF-8, its newlines universal; the error what the Python raised.
fn read_strict(path: &Path) -> Result<String, String> {
    let bytes = std::fs::read(path).map_err(|e| format!("{}: {e}", path.display()))?;
    String::from_utf8(bytes)
        .map(|t| l7r_gate_core::record::repo::universal(&t))
        .map_err(|e| format!("UnicodeDecodeError: {}: {e}", path.display()))
}

fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}

/// What the Python raised: its message after a `Traceback` line, exit 1.
fn raised(why: &str) -> Reply {
    reply(
        String::new(),
        format!("Traceback (most recent call last):\n  l7r-gate make-docs\n{why}\n"),
        1,
    )
}

/// The Makefile's rows and the page, or the reply that stops before them.
fn page(root: &Path) -> Result<(usize, usize, Vec<String>, String), Reply> {
    let mk = root.join("Makefile");
    if !mk.is_file() {
        return Err(reply(
            String::new(),
            format!("make-docs: no Makefile at {}\n", mk.display()),
            2,
        ));
    }
    let text = read_strict(&mk).map_err(|why| raised(&why))?;
    let (rows, undocumented) = parse(&text);
    let untagged = rows
        .iter()
        .filter(|r| r.category.is_empty())
        .map(|r| r.name.clone())
        .collect();
    Ok((
        rows.len(),
        undocumented.len(),
        untagged,
        render(&rows, &undocumented),
    ))
}

/// `--write`: the page regenerated under `root`.
#[must_use]
pub fn write(root: &Path) -> Reply {
    let (rows, undocumented, _, body) = match page(root) {
        Ok(p) => p,
        Err(stop) => return stop,
    };
    let out = root.join(OUT);
    let written =
        std::fs::create_dir_all(root.join("docs")).and_then(|()| std::fs::write(&out, body));
    match written {
        Ok(()) => reply(
            format!("make-docs: wrote {OUT} - {rows} targets, {undocumented} undocumented\n"),
            String::new(),
            0,
        ),
        Err(e) => raised(&format!("{}: {e}", out.display())),
    }
}

/// `--check`: exit 1, naming each problem, where the page is stale or missing or a target has no `[category]` tag.
#[must_use]
pub fn check(root: &Path) -> Reply {
    let (rows, _, untagged, body) = match page(root) {
        Ok(p) => p,
        Err(stop) => return stop,
    };
    let out = root.join(OUT);
    let mut problems = Vec::new();
    if !untagged.is_empty() {
        problems.push(format!(
            "target(s) with help text but no [category] tag: {}",
            untagged.join(", ")
        ));
    }
    if out.is_file() {
        match read_strict(&out) {
            Ok(had) if had == body => {}
            Ok(_) => problems.push(format!(
                "{OUT} is STALE - the Makefile changed since it was generated"
            )),
            Err(why) => return raised(&why),
        }
    } else {
        problems.push(format!("{OUT} does not exist"));
    }
    if problems.is_empty() {
        return reply(
            format!("make-docs: {OUT} is current ({rows} targets)\n"),
            String::new(),
            0,
        );
    }
    let listed = problems.iter().fold(String::new(), |mut all, p| {
        let _ = writeln!(all, "  - {p}");
        all
    });
    reply(
        String::new(),
        format!("\n\x1b[1mmake-docs: the target reference is out of date.\x1b[0m\n\n{listed}\n  Fix: add the [category] tag to the target's `##` line if it is missing, then\n       run `make docs`. The page is generated from the Makefile so it cannot drift;\n       that is the whole point of it being checked here.\n\n"),
        1,
    )
}

/// `l7r-gate make-docs [root] [--write|--check]` from `cwd`: the root is the first argument when it is no flag, the mode the first flag
/// (`--write`, anything else a check), as the Python read its argv.
#[must_use]
pub fn cli(args: &[String], cwd: &Path) -> Reply {
    let root = args
        .first()
        .filter(|a| !a.starts_with("--"))
        .map_or_else(|| resolved(cwd), |r| resolved(&cwd.join(py_path(r))));
    if args
        .iter()
        .find(|a| a.starts_with("--"))
        .is_some_and(|m| m == "--write")
    {
        write(&root)
    } else {
        check(&root)
    }
}

#[cfg(test)]
mod tests;
