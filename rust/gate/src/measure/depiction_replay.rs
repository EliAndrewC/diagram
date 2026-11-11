//! The depiction replay (feature 449 T88, from `depiction_replay.py`, feature 375 amendment 6, onto the Rust `modal_owed` with no door, `ask:449-T77-replays`): how many existing pop-up edits since a date owed `modal-depiction` under amendment 1's rule (FR-015) and under amendment 6's, and how many of the About-only edits that once owed one owe none now.
//!
//! `l7r-gate measure depiction-replay [--since 2026-10-05] [--until <commit>] [--record <measurements.json> --key <key>]`.

use std::path::Path;

use l7r_guard::shared::pyjson;
use serde_json::{json, Map, Value};

use crate::record::args::{parse, Spec};
use crate::record::modals::{choice_modal, depiction_owed_by, Modal, MODALS};
use crate::record::repo::{git_out, read_text, tree_of};

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
/// (before, after) of every pop-up file a non-merge commit changed, present on both sides, its tags moved.
fn edits(root: &Path, since: &str, until: &str) -> Vec<(Modal, Modal)> {
    let mut out = Vec::new();
    for c in git_out(
        root,
        &[
            "log",
            "--no-merges",
            &format!("--since={since}"),
            "--format=%H",
            until,
            "--",
            MODALS,
        ],
    )
    .split_whitespace()
    {
        let parent = format!("{c}^");
        for f in git_out(
            root,
            &[
                "diff-tree",
                "--no-commit-id",
                "-r",
                "--name-only",
                &parent,
                c,
                "--",
                MODALS,
            ],
        )
        .split_whitespace()
        {
            if !f.ends_with(".md") {
                continue;
            }
            let before = git_out(root, &["show", &format!("{parent}:{f}")]);
            let after = git_out(root, &["show", &format!("{c}:{f}")]);
            if let (Some(was), Some(m)) = (
                choice_modal(f, &before, false),
                choice_modal(f, &after, false),
            ) {
                if !same_tags(&was, &m) {
                    out.push((was, m));
                }
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
pub(crate) fn cli(args: &[String], root: &Path) -> crate::Reply {
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
        json!(l7r_guard::shared::py_text::strip(&git_out(
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
