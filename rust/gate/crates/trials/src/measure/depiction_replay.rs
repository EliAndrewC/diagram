//! The depiction replay (feature 449 T88, from `depiction_replay.py`, feature 375 amendment 6, onto the Rust `modal_owed` with no door, `ask:449-T77-replays`): how many existing pop-up edits since a date owed `modal-depiction` under amendment 1's rule (FR-015) and under amendment 6's, and how many of the About-only edits that once owed one owe none now.
//!
//! `l7r-gate measure depiction-replay [--since 2026-10-05] [--until <commit>] [--record <measurements.json> --key <key>]`.

use std::path::Path;

use l7r_shared::pyjson;
use serde_json::{json, Map, Value};

use crate::record::args::{parse, Spec};
use crate::record::modals::{choice_modal, depiction_owed_by, Modal, MODALS};
use crate::record::repo::{cat_blobs, git_out, read_text, tree_of, universal};

/// Amendment 1's rule (FR-015), as `modal_owed.owed` held it until amendment 6.
fn old_rule(was: &Modal, m: &Modal) -> bool {
    depiction_owed_by(Some(was), m) || was.tag("About") != m.tag("About")
}

fn same_tags(a: &Modal, b: &Modal) -> bool {
    let sorted = |m: &Modal| {
        let mut t = m.tags.clone();
        t.sort();
        t
    };
    sorted(a) == sorted(b)
}

#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "the pop-up files' names, as `str.endswith` read them"
)]
/// (before, after) of every pop-up file a non-merge commit changed, present on both sides, its tags moved. The commits and the files
/// each changed come from one `git log --name-only` and every version from one `git cat-file --batch` (feature 449 T167), where a
/// `git diff-tree` a commit and a `git show` a version were 111 processes for the test's three commits and seven runs, 205 ms against
/// FR-008's tenth of a second. The log's diff is a commit's against its one parent, renames not followed, as the `diff-tree` of
/// `<commit>^` and `<commit>` read it; a commit with no parent had no `<commit>^` to read and has none here.
fn edits(root: &Path, since: &str, until: &str) -> Vec<(Modal, Modal)> {
    let listed = git_out(
        root,
        &[
            "log",
            "--no-merges",
            "--no-renames",
            &format!("--since={since}"),
            "--format=%x00%H %P",
            "--name-only",
            until,
            "--",
            MODALS,
        ],
    );
    // (the commit, a pop-up file it changed), each commit's block `\0<commit> <parent>`, a blank line and its files
    let changed: Vec<(&str, &str)> = listed
        .split('\0')
        .filter_map(|block| {
            let mut lines = block.lines();
            let (c, parent) = lines.next()?.split_once(' ')?;
            (!parent.is_empty()).then(|| lines.filter(|f| f.ends_with(".md")).map(move |f| (c, f)))
        })
        .flatten()
        .collect();
    let versions: Vec<String> = changed
        .iter()
        .flat_map(|(c, f)| [format!("{c}^:{f}"), format!("{c}:{f}")])
        .collect();
    let mut read = cat_blobs(root, &versions)
        .into_iter()
        .map(|t| universal(&t));
    let mut out = Vec::new();
    for (_, f) in changed {
        let (before, after) = (
            read.next().unwrap_or_default(),
            read.next().unwrap_or_default(),
        );
        if let (Some(was), Some(m)) = (
            choice_modal(f, &before, false),
            choice_modal(f, &after, false),
        ) {
            if !same_tags(&was, &m) {
                out.push((was, m));
            }
        }
    }
    out
}

fn replay(rows: &[(Modal, Modal)]) -> Map<String, Value> {
    let old: Vec<&(Modal, Modal)> = rows.iter().filter(|(w, m)| old_rule(w, m)).collect();
    let new = rows
        .iter()
        .filter(|(w, m)| depiction_owed_by(Some(w), m))
        .count();
    let about_only: Vec<&&(Modal, Modal)> = old
        .iter()
        .filter(|(w, m)| !depiction_owed_by(Some(w), m))
        .collect();
    let owed_now = about_only
        .iter()
        .filter(|(w, m)| depiction_owed_by(Some(w), m))
        .count();
    let mut out = Map::new();
    out.insert("edits to existing pop-ups".to_owned(), json!(rows.len()));
    out.insert(
        "owed modal-depiction, amendment 1".to_owned(),
        json!(old.len()),
    );
    out.insert("owed modal-depiction, amendment 6".to_owned(), json!(new));
    out.insert(
        "About-only edits (owed before, not now)".to_owned(),
        json!(about_only.len()),
    );
    out.insert(
        "owed now among the About-only edits".to_owned(),
        json!(owed_now),
    );
    out
}

/// `measure depiction-replay ...`.
#[must_use]
pub fn cli(args: &[String], root: &Path) -> crate::Reply {
    let p = match parse(
        args,
        &[
            Spec::value("--since"),
            Spec::value("--until"),
            Spec::value("--record"),
            Spec::value("--key"),
        ],
    ) {
        Ok(p) => p,
        Err(complaint) => {
            return super::reply(
                String::new(),
                format!("usage: l7r-gate measure depiction-replay: {complaint}\n"),
                2,
            )
        }
    };
    let tree = tree_of(root);
    let (since, until) = (p.text("--since", "2026-10-05"), p.text("--until", "HEAD"));
    let mut s = Map::new();
    s.insert("since".to_owned(), json!(since));
    s.insert(
        "until".to_owned(),
        json!(l7r_shared::py_text::strip(&git_out(
            &tree,
            &["rev-parse", "--short", until]
        ))),
    );
    s.extend(replay(&edits(&tree, since, until)));
    let s = Value::Object(s);
    let record = p.text("--record", "");
    if !record.is_empty() {
        let key = p.text("--key", "");
        if key.is_empty() {
            return super::reply(
                String::new(),
                "depiction_replay: --record needs --key\n".to_owned(),
                2,
            );
        }
        let path = Path::new(record);
        let written = read_text(path)
            .and_then(|t| serde_json::from_str::<Value>(&t).map_err(|e| e.to_string()))
            .and_then(|mut data| {
                let entry = data
                    .as_object_mut()
                    .ok_or_else(|| "AttributeError: the record is no JSON object".to_owned())?
                    .entry(key.to_owned())
                    .or_insert_with(|| json!({}));
                entry
                    .as_object_mut()
                    .ok_or_else(|| format!("TypeError: {key} is no JSON object"))?
                    .insert("value".to_owned(), s.clone());
                std::fs::write(path, pyjson::dumps(&data, Some(1), false) + "\n")
                    .map_err(|e| e.to_string())
            });
        if let Err(why) = written {
            return super::reply(String::new(), why + "\n", 1);
        }
    }
    super::reply(pyjson::dumps(&s, Some(1), true) + "\n", String::new(), 0)
}

#[cfg(test)]
mod tests;
