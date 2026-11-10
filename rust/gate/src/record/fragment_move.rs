//! Move a question of the record and every pointer to it, in one change (features 301 FR-015, 303 FR-019; feature 449 T79, from `fragment_move.py`).
//!
//! The GM, 2026-10-01: a pointer names *"the source which is fed into and used to generate that HTML page"* - the fragment. Since feature 303 a question
//! is one STEM, `NNNN-<slug>`, whose slug is its research page's heading id (its drawing page's, for a question that has none), so retitling a question
//! renames its stem and a renumbering moves it to a free number. This does the move with everything that names it: every file of the stem (`git mv`, so
//! history follows them), the heading's `id`, every link inside the record, the `about:` markers, the `confusables.json` entries, every pointer in the
//! repository's tracked files and the migration mapping (`research/moved-303.json`), so a late pointer is told the current name.
//!
//! It refuses rather than guesses: a source that is not a question's page, a target name that is not `NNNN-<slug>.html` (or `.drawing.html` for a
//! drawing-only question), a number already another question's. `l7r-gate check research-pointers` (gate and push) catches a move made by hand.

use std::collections::BTreeSet;
use std::io::ErrorKind;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::{escape, Captures, NoExpand, Regex};
use serde_json::{json, Value};

use super::{py_lines, reply};
use crate::cohort::git;
use crate::logs::py_dumps;
use crate::Reply;

const RECORD: &str = "research";
const QUESTIONS: &str = "questions";
const SUFFIXES: [&str; 6] = [
    "",
    ".notes",
    ".originals",
    ".drawing",
    ".drawing.notes",
    ".drawing.originals",
];
const USAGE: &str = "usage: make fragment-move FROM=research/questions/NNNN-<slug>.html TO=research/questions/NNNN-<new slug>.html\n";

fn compiled(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

/// A question's page: Python's `$` also stands before one final newline.
static NAME: LazyLock<Regex> =
    LazyLock::new(|| compiled(r"^(\d{4})-([^./\s]+)(\.drawing)?\.html\n?$"));

/// `Path.read_text(encoding="utf-8")`: strict UTF-8, and universal newlines, so a file this rewrites comes out with Python's line ends.
fn read_text(path: &Path) -> std::io::Result<String> {
    let text = String::from_utf8(std::fs::read(path)?).map_err(|_| ErrorKind::InvalidData)?;
    Ok(text.replace("\r\n", "\n").replace('\r', "\n"))
}

fn read(path: &Path) -> Result<String, String> {
    read_text(path).map_err(|e| format!("{}: {e}", path.display()))
}

fn save(path: &Path, text: &str) -> Result<(), String> {
    std::fs::write(path, text).map_err(|e| format!("{}: {e}", path.display()))
}

fn git_ok(root: &Path, args: &[&str]) -> Result<String, String> {
    let (ok, out) = git(root, args);
    if ok {
        Ok(out)
    } else {
        Err(format!("git {} failed", args.join(" ")))
    }
}

fn name(path: &str) -> &str {
    path.rsplit('/').next().unwrap_or(path)
}

/// What a move renames: the old and new stem, the old and new heading id.
struct Move {
    old: String,
    new: String,
    old_id: String,
    new_id: String,
}

/// The move, or a refusal with what to do instead.
fn plan(root: &Path, src: &str, dst: &str) -> Result<Move, String> {
    let qdir = root.join(RECORD).join(QUESTIONS);
    let (old, new) = (name(src), name(dst));
    let (old_m, new_m) = (
        NAME.captures(old).ok().flatten(),
        NAME.captures(new).ok().flatten(),
    );
    let Some(old_m) = old_m.filter(|_| qdir.join(old).is_file()) else {
        return Err(format!(
            "FROM={src}: not a question's page in research/questions/ - name its `NNNN-<slug>.html`"
        ));
    };
    let Some(new_m) = new_m.filter(|m| m.get(3).is_some() == old_m.get(3).is_some()) else {
        return Err(format!("TO={dst}: a question is named `NNNN-<slug>.html` (`.drawing.html` for a drawing-only question), as FROM is"));
    };
    let old_stem = format!("{}-{}", &old_m[1], &old_m[2]);
    if old_m.get(3).is_some() && qdir.join(format!("{old_stem}.html")).is_file() {
        return Err(format!(
            "FROM={src}: a drawing page beside its research page moves with it - name the research page"
        ));
    }
    let new_stem = format!("{}-{}", &new_m[1], &new_m[2]);
    if old_stem == new_stem {
        return Err(format!("TO={dst}: the same name as FROM"));
    }
    let (number, own) = (format!("{}-", &new_m[1]), format!("{old_stem}."));
    let taken = std::fs::read_dir(&qdir)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .find(|n| n.starts_with(&number) && !n.starts_with(&own));
    if let Some(taken) = taken {
        return Err(format!(
            "TO={dst}: number {} is already {taken} - take a free one from `make reserve KIND=question`",
            &new_m[1]
        ));
    }
    Ok(Move {
        old: old_stem,
        new: new_stem,
        old_id: old_m[2].to_owned(),
        new_id: new_m[2].to_owned(),
    })
}

/// Do the move; the files it changed, repository-relative, sorted.
fn relocate(root: &Path, src: &str, dst: &str) -> Result<Vec<String>, String> {
    let m = plan(root, src, dst)?;
    let qdir = root.join(RECORD).join(QUESTIONS);
    let mut changed = BTreeSet::new();
    for suffix in SUFFIXES {
        let (from, to) = (
            format!("{RECORD}/{QUESTIONS}/{}{suffix}.html", m.old),
            format!("{RECORD}/{QUESTIONS}/{}{suffix}.html", m.new),
        );
        if root.join(&from).is_file() {
            git_ok(root, &["mv", &from, &to])?;
            changed.insert(to);
        }
    }
    let owner = if qdir.join(format!("{}.html", m.new)).is_file() {
        format!("{}.html", m.new)
    } else {
        format!("{}.drawing.html", m.new)
    };
    if m.old_id != m.new_id {
        let path = qdir.join(&owner);
        let text = read(&path)?;
        let heading = compiled(&format!(r#"(<h[23] id="){}(")"#, escape(&m.old_id)));
        let moved = heading.replace(&text, |c: &Captures| {
            format!("{}{}{}", &c[1], m.new_id, &c[2])
        });
        save(&path, &moved)?;
    }
    changed.extend(repoint_record(root, &m, &owner)?);
    changed.extend(repoint_tracked(root, &m.old, &m.new)?);
    Ok(changed.into_iter().collect())
}

/// Every link inside the record that reached the question, re-aimed; its `about:` markers; the confusables; the mapping.
fn repoint_record(root: &Path, m: &Move, owner: &str) -> Result<Vec<String>, String> {
    let record = root.join(RECORD);
    let qdir = record.join(QUESTIONS);
    let link = compiled(&format!(
        r#"(href="){}((?:\.drawing)?\.html)(#[^"]*)?(")"#,
        escape(&m.old)
    ));
    let (own_anchor, new_anchor) = (format!("#{}", m.old_id), format!("#{}", m.new_id));
    let mut changed = Vec::new();
    let mut names: Vec<String> = std::fs::read_dir(&qdir)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .filter(|n| n.strip_suffix(".html").is_some())
        .collect();
    names.sort();
    for file in names {
        let path = qdir.join(&file);
        let text = read(&path)?;
        let linked = link.replace_all(&text, |c: &Captures| {
            let anchor = c.get(3).map_or("", |a| a.as_str());
            let renamed =
                anchor == own_anchor && (&c[2] == ".html" || owner.ends_with(".drawing.html"));
            let shown = if renamed { new_anchor.as_str() } else { anchor };
            format!("{}{}{}{shown}{}", &c[1], m.new, &c[2], &c[4])
        });
        let mut fresh = linked.replace(
            &format!("<!-- about: {} -->", m.old),
            &format!("<!-- about: {} -->", m.new),
        );
        if file == owner {
            fresh = fresh.replace(
                &format!("href=\"#{}\"", m.old_id),
                &format!("href=\"#{}\"", m.new_id),
            );
        }
        if fresh != text {
            save(&path, &fresh)?;
            changed.push(format!("{RECORD}/{QUESTIONS}/{file}"));
        }
    }
    let data = record.join("confusables.json");
    if data.is_file() && repoint_confusables(&data, m, owner)? {
        changed.push(format!("{RECORD}/confusables.json"));
    }
    let mapping = record.join("moved-303.json");
    if mapping.is_file() {
        let text = read(&mapping)?;
        let at = compiled(&format!(r#"\bquestions/{}(?=[."])"#, escape(&m.old)));
        let aimed = format!("questions/{}", m.new);
        let fresh = at.replace_all(&text, NoExpand(&aimed));
        if fresh != text {
            save(&mapping, &fresh)?;
            changed.push(format!("{RECORD}/moved-303.json"));
        }
    }
    Ok(changed)
}

/// The `confusables.json` entries naming the question, re-aimed; whether any was. An entry with no anchor comes out with an empty one, as it always has.
fn repoint_confusables(data: &Path, m: &Move, owner: &str) -> Result<bool, String> {
    let shape = || format!("{}: not a list of a/b pairs", data.display());
    let mut pairs: Value =
        serde_json::from_str(&read(data)?).map_err(|e| format!("{}: {e}", data.display()))?;
    let whole = compiled(&format!(r"^{}((?:\.drawing)?\.html)$", escape(&m.old)));
    let mut moved = false;
    for pair in pairs.as_array_mut().ok_or_else(shape)? {
        for side in ["a", "b"] {
            let value = pair[side].as_str().ok_or_else(shape)?.to_owned();
            let (file, anchor) = value.split_once('#').unwrap_or((&value, ""));
            if let Some(c) = whole.captures(file).ok().flatten() {
                let page = format!("{}{}", m.new, &c[1]);
                let kept = if anchor == m.old_id && page == owner {
                    m.new_id.as_str()
                } else {
                    anchor
                };
                pair[side] = json!(format!("{page}#{kept}"));
                moved = true;
            }
        }
    }
    if moved {
        save(data, &(py_dumps(&pairs, 1, false) + "\n"))?;
    }
    Ok(moved)
}

/// Every tracked file outside the record naming the stem - any of its pages, notes or originals.
fn repoint_tracked(root: &Path, old: &str, new: &str) -> Result<Vec<String>, String> {
    let stem = compiled(&format!(
        r"\b{RECORD}/{QUESTIONS}/{}(?=(?:\.drawing)?(?:\.notes|\.originals)?\.html)",
        escape(old)
    ));
    let aimed = format!("{RECORD}/{QUESTIONS}/{new}");
    let mut changed = Vec::new();
    let listing = git_ok(root, &["ls-files"])?;
    for path in py_lines(&listing) {
        if path.starts_with("research/") {
            continue;
        }
        let file = root.join(path);
        let text = match read_text(&file) {
            Ok(text) => text,
            // a binary file holds no pointer; a file deleted but not yet staged, or a submodule, has none
            Err(e)
                if matches!(
                    e.kind(),
                    ErrorKind::InvalidData | ErrorKind::NotFound | ErrorKind::IsADirectory
                ) =>
            {
                continue
            }
            Err(e) => return Err(format!("{path}: {e}")),
        };
        if !text.contains(old) {
            continue;
        }
        let fresh = stem.replace_all(&text, NoExpand(&aimed));
        if fresh != text {
            save(&file, &fresh)?;
            changed.push(path.to_owned());
        }
    }
    Ok(changed)
}

fn holds(path: &Path, needle: &str) -> bool {
    read_text(path).is_ok_and(|t| t.contains(needle))
}

fn ensure(ok: bool, what: &str) -> Result<(), String> {
    if ok {
        Ok(())
    } else {
        Err(format!("selftest failed: {what}"))
    }
}

fn refuses(got: Result<Vec<String>, String>, why: &str) -> bool {
    got.is_err_and(|e| e.contains(why))
}

fn put(root: &Path, rel: &str, text: &str) -> Result<(), String> {
    save(&root.join(rel), text)
}

const Q0120: &str = "research/questions/0120-ponds.html";
const Q0125: &str = "research/questions/0125-reservoir-ponds.html";

/// The move on a scratch repository: every refusal, then a move with all it carries, then a drawing-only question.
fn selftest_in(root: &Path) -> Result<(), String> {
    seed(root)?;
    refusals(root)?;
    carried(root)
}

fn seed(root: &Path) -> Result<(), String> {
    let q = root.join(RECORD).join(QUESTIONS);
    std::fs::create_dir_all(&q).map_err(|e| e.to_string())?;
    put(root, Q0120, "<h2 id=\"ponds\">Ponds</h2><p>see <a href=\"#ponds\">here</a> <a href=\"0120-ponds.drawing.html\">drawn</a></p>")?;
    put(
        root,
        "research/questions/0120-ponds.notes.html",
        "<li data-note=\"k\">n</li>",
    )?;
    put(
        root,
        "research/questions/0120-ponds.drawing.html",
        "<h2 id=\"drawn-ponds\">Drawn</h2><a href=\"0120-ponds.html#ponds\">p</a>",
    )?;
    put(
        root,
        "research/questions/0121-more.drawing.html",
        "<h2 id=\"more\">M</h2>\n<!-- about: 0120-ponds -->",
    )?;
    put(root, "research/questions/0130-x.html", "<h2 id=\"x\">X</h2><a href=\"0120-ponds.html#ponds\">ponds</a> <a href=\"0120-ponds.html#other\">o</a>")?;
    put(
        root,
        "research/questions/0140-alone.drawing.html",
        "<h2 id=\"alone\">A</h2>",
    )?;
    put(
        root,
        "research/confusables.json",
        r#"[{"a": "0120-ponds.html#ponds", "b": "0130-x.html#x"}]"#,
    )?;
    put(
        root,
        "research/moved-303.json",
        r#"{"files": {"water/120-ponds.html": "questions/0120-ponds.html"}}"#,
    )?;
    put(root, "code.py", "# research/questions/0120-ponds.html says so; notes at research/questions/0120-ponds.notes.html\n")?;
    git_ok(root, &["init", "-q"])?;
    git_ok(root, &["add", "-A"])?;
    Ok(())
}

fn refusals(root: &Path) -> Result<(), String> {
    let cases = [
        (
            "research/questions/0999-gone.html",
            "research/questions/0998-x.html",
            "not a question's page",
        ),
        (Q0120, "research/questions/ponds.html", "is named"),
        (
            Q0120,
            "research/questions/0130-ponds.html",
            "already 0130-x.html",
        ),
        (
            "research/questions/0120-ponds.drawing.html",
            "research/questions/0120-p.drawing.html",
            "moves with it",
        ),
        (Q0120, Q0120, "the same name"),
    ];
    for (from, to, why) in cases {
        ensure(refuses(relocate(root, from, to), why), why)?;
    }
    Ok(())
}

fn carried(root: &Path) -> Result<(), String> {
    let q = root.join(RECORD).join(QUESTIONS);
    let changed = relocate(root, Q0120, Q0125)?;
    for file in [
        "0125-reservoir-ponds.html",
        "0125-reservoir-ponds.notes.html",
        "0125-reservoir-ponds.drawing.html",
    ] {
        ensure(q.join(file).is_file(), file)?;
    }
    let page = q.join("0125-reservoir-ponds.html");
    ensure(holds(&page, "<h2 id=\"reservoir-ponds\">"), "the heading")?;
    ensure(
        holds(&page, "href=\"#reservoir-ponds\""),
        "the page's own link",
    )?;
    ensure(
        holds(&page, "href=\"0125-reservoir-ponds.drawing.html\""),
        "the link to its drawing",
    )?;
    ensure(
        holds(
            &q.join("0125-reservoir-ponds.drawing.html"),
            "href=\"0125-reservoir-ponds.html#reservoir-ponds\"",
        ),
        "the drawing's link",
    )?;
    ensure(
        holds(
            &q.join("0121-more.drawing.html"),
            "<!-- about: 0125-reservoir-ponds -->",
        ),
        "the about marker",
    )?;
    let x = q.join("0130-x.html");
    ensure(
        holds(&x, "href=\"0125-reservoir-ponds.html#reservoir-ponds\""),
        "another page's link",
    )?;
    ensure(
        holds(&x, "href=\"0125-reservoir-ponds.html#other\""),
        "an anchor that is not the heading",
    )?;
    ensure(
        holds(
            &root.join("research/confusables.json"),
            "0125-reservoir-ponds.html#reservoir-ponds",
        ),
        "the confusables",
    )?;
    ensure(
        holds(
            &root.join("research/moved-303.json"),
            "questions/0125-reservoir-ponds.html",
        ),
        "the mapping",
    )?;
    let code = root.join("code.py");
    ensure(
        holds(&code, "research/questions/0125-reservoir-ponds.html"),
        "the tracked pointer",
    )?;
    ensure(
        holds(&code, "research/questions/0125-reservoir-ponds.notes.html"),
        "the tracked notes pointer",
    )?;
    ensure(changed.iter().any(|c| c == "code.py"), "code.py reported")?;
    relocate(
        root,
        "research/questions/0140-alone.drawing.html",
        "research/questions/0140-on-its-own.drawing.html",
    )?;
    ensure(
        holds(
            &q.join("0140-on-its-own.drawing.html"),
            "<h2 id=\"on-its-own\">",
        ),
        "a drawing-only question's slug is its heading",
    )
}

fn selftest_reply(got: Result<(), String>) -> Reply {
    match got {
        Ok(()) => reply("fragment-move selftest ok\n".to_owned(), String::new(), 0),
        Err(why) => reply(String::new(), format!("fragment-move: {why}\n"), 1),
    }
}

fn selftest() -> Reply {
    let dir = crate::checks::scratch("fragment-move-selftest");
    let got = selftest_in(&dir);
    let _ = std::fs::remove_dir_all(&dir);
    selftest_reply(got)
}

/// `record fragment-move FROM TO [--root DIR] | --selftest`.
pub(crate) fn cli(args: &[String]) -> Reply {
    if args.first().is_some_and(|a| a == "--selftest") {
        return selftest();
    }
    let mut plain: Vec<&str> = args
        .iter()
        .map(String::as_str)
        .filter(|a| !a.starts_with("--"))
        .collect();
    let mut given = ".";
    if let Some(at) = args.iter().position(|a| a == "--root") {
        let Some(value) = args.get(at + 1) else {
            return reply(String::new(), USAGE.to_owned(), 2);
        };
        given = value;
        if let Some(found) = plain.iter().position(|a| a == value) {
            plain.remove(found);
        }
    }
    let [from, to] = plain[..] else {
        return reply(String::new(), USAGE.to_owned(), 2);
    };
    let root = std::fs::canonicalize(given).unwrap_or_else(|_| PathBuf::from(given));
    match relocate(&root, from, to) {
        Ok(changed) => {
            let list: Vec<String> = changed.iter().map(|c| format!("  {c}")).collect();
            reply(
                format!(
                    "fragment-move: {from} -> {to}; {} file(s) changed:\n{}\nthen `make record` at the repository root, and commit\n",
                    changed.len(),
                    list.join("\n")
                ),
                String::new(),
                0,
            )
        }
        Err(why) => reply(String::new(), format!("fragment-move: {why}\n"), 1),
    }
}

#[cfg(test)]
mod tests;
