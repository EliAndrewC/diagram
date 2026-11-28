//! The citations a block writes in no FR, SC or D id (461 T69: 461 T65's bundle carried none of them): a task's numbered decision,
//! `T16's Decision 3`, and an entry of another of the feature's files, `data-model.md, "A repair entry"` or `data-model.md's repair
//! entry`. Measured 2026-11-27 over every `specs/*/plan.md` and `plan-done.md`: 10 task decisions so named (all 461's), 6 quoted entries
//! of `data-model.md` and 5 of its `<word> entry`; `request.md`'s 29 quotes are the GM's words, which the bundle's `request.md` carries.

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;

use super::super::super::sections::{re, task_sections};
use super::super::{paragraphs, plans_of, read, HEADING};
use super::{dir_of, not_found};

/// `[<feature> ]T<n>'s Decision <k>` or `Decisions <k> and <m>`: the feature group 1, the task 2, the numbers 3.
static TASK_DECISION: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?<![-\w])(?:(\d{3})\s+)?(T\d+[a-z]?)'s\s+Decisions?\s+(\d+(?:(?:,\s*|,?\s+(?:and|or)\s+)\d+\b)*)",
    )
});
/// A numbered decision of a task's `**Decisions**` list, `3. **...**`.
static NUMBERED: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^[ \t]*(\d+)\. \*\*"));
static NUMBER: LazyLock<Regex> = LazyLock::new(|| re(r"\d+"));
/// A file of the feature named with a quoted heading or phrase, `data-model.md, "A repair entry"` (group 1 the file, 2 the words), or
/// with its `<word> entry`, `data-model.md's repair entry` (group 1 the file, 3 the word).
static FILE_ENTRY: LazyLock<Regex> = LazyLock::new(|| {
    re(r#"(?<![\w/.-])([a-z][\w-]*\.md)(?:,\s+"([^"]+)"|'s\s+([a-z][\w-]*)\s+entry\b)"#)
});
static HEADING_LINE: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^(#{1,6}) (.*)$"));

/// The text each of `bodies`' citations in these forms names, under a line naming it, or its NOT FOUND line; each once.
pub(super) fn carried(spec_dir: &Path, own_no: &str, bodies: &[&str]) -> Vec<String> {
    let mut out: Vec<String> = Vec::new();
    // one text once, whichever form named it (`data-model.md, "A repair entry"` and `data-model.md's repair entry`)
    let mut push = |part: String| {
        let text = |p: &str| p.split_once("-->\n").map_or(p, |(_, t)| t).to_owned();
        if !out.iter().any(|o| text(o) == text(&part)) {
            out.push(part);
        }
    };
    for body in bodies {
        for c in TASK_DECISION.captures_iter(body).map_while(Result::ok) {
            let no = c.get(1).map_or(own_no, |m| m.as_str());
            for k in NUMBER.find_iter(&c[3]).map_while(Result::ok) {
                push(task_decision(spec_dir, no, &c[2], k.as_str()));
            }
        }
        for c in FILE_ENTRY.captures_iter(body).map_while(Result::ok) {
            // a template's placeholder, `"<words>"`, names no entry (461 T71)
            if &c[1] == "request.md" || c.get(2).is_some_and(|m| m.as_str().starts_with('<')) {
                continue;
            }
            let (words, entry) = (c.get(2).map(|m| m.as_str()), c.get(3).map(|m| m.as_str()));
            push(file_entry(spec_dir, &c[1], words, entry));
        }
    }
    out
}

/// Decision `k` of `task`'s `**Decisions**` list in feature `no`'s plans (to the list's next heading, so its Approach checklist's same
/// number is never read).
fn task_decision(spec_dir: &Path, no: &str, task: &str, k: &str) -> String {
    let rid = format!("{task}'s Decision {k}");
    let dir = match dir_of(spec_dir, no) {
        Ok(d) => d,
        Err(why) => return not_found(&rid, &why),
    };
    let name = dir
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();
    let Some(section) = task_sections(&plans_of(&dir)).remove(task) else {
        return not_found(
            &rid,
            &format!("specs/{name} has no {task} section in its plan.md or plan-done.md"),
        );
    };
    let list = section.find("**Decisions**").map_or("", |at| {
        let rest = &section[at..];
        let end = HEADING
            .find(rest)
            .ok()
            .flatten()
            .map_or(rest.len(), |h| h.start());
        &rest[..end]
    });
    let header = format!("<!-- feature {no} {task}, Decision {k} -->\n");
    paragraphs(list, &NUMBERED)
        .get(k)
        .and_then(|v| v.as_str())
        .map_or_else(
            || {
                not_found(
                    &rid,
                    &format!("{task}'s section in specs/{name} lists no decision {k}"),
                )
            },
            |text| header + text,
        )
}

/// The section of `file` under the heading holding `words` or `<entry> entry` (to its next heading of its level or higher), else for
/// quoted words the paragraph holding them.
fn file_entry(spec_dir: &Path, file: &str, words: Option<&str>, entry: Option<&str>) -> String {
    let name = spec_dir.file_name().unwrap_or_default().to_string_lossy();
    let (rid, sought) = match (words, entry) {
        (Some(w), _) => (format!("{file}, \"{w}\""), w.to_lowercase()),
        (None, e) => {
            let e = e.unwrap_or_default();
            (
                format!("{file}'s {e} entry"),
                format!("{e} entry").to_lowercase(),
            )
        }
    };
    let path = spec_dir.join(file);
    if !path.is_file() {
        return not_found(&rid, &format!("specs/{name} has no {file}"));
    }
    let text = read(&path);
    let header = format!("<!-- {rid} -->\n");
    if let Some(section) = heading_section(&text, &sought) {
        return header + &section;
    }
    let paragraph = words.and(
        text.split("\n\n")
            .find(|p| p.to_lowercase().contains(&sought))
            .map(|p| format!("{}\n", p.trim())),
    );
    paragraph.map_or_else(
        || {
            let what = if words.is_some() {
                "heading or paragraph with those words".to_owned()
            } else {
                format!("heading naming a {sought}")
            };
            not_found(&rid, &format!("specs/{name}/{file} holds no {what}"))
        },
        |p| header + &p,
    )
}

/// The first heading of `text` (below its title) whose words hold `sought`, ignoring case, with its body to the next heading of its
/// level or higher.
fn heading_section(text: &str, sought: &str) -> Option<String> {
    let heads: Vec<(usize, usize, bool)> = HEADING_LINE
        .captures_iter(text)
        .map_while(Result::ok)
        .map(|c| {
            let at = c.get(0).map_or(0, |g| g.start());
            (
                at,
                c[1].len(),
                c[1].len() > 1 && c[2].to_lowercase().contains(sought),
            )
        })
        .collect();
    let (i, &(at, level, _)) = heads.iter().enumerate().find(|(_, h)| h.2)?;
    let end = heads[i + 1..]
        .iter()
        .find(|h| h.1 <= level)
        .map_or(text.len(), |h| h.0);
    Some(format!("{}\n", text[at..end].trim_end()))
}
