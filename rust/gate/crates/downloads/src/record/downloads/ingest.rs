//! Ingest, three-way against the canonical list at the last sync (feature 313 plan D4), and sync (D5): a body the GM changed is told from one a session changed, and a
//! GM text edit is never recorded or dropped without `KEEP=` or `DROP=`.

use std::collections::{BTreeSet, HashMap, HashSet};
use std::fmt::Write as _;
use std::path::Path;

use serde_json::{json, Value};

use super::parse::{
    by_id, entries, entry_at, entry_ref, parse, render, Block, Marks, RESOLVE_STATES,
};
use super::{load_state, read, save_state, sha, Ctx, CANON, STATE};
use crate::cohort::git;
use crate::difflib::unified_diff;
use crate::measure::text_err;
use crate::record::access_tags;

/// What happened to each entry, in the copy's order.
#[derive(Debug, Default)]
pub(super) struct IngestResult {
    pub(super) recorded: Vec<String>,
    pub(super) refused: Vec<(String, String)>,
    pub(super) pending: Vec<(String, String)>,
    pub(super) kept: Vec<String>,
    pub(super) dropped: Vec<String>,
    pub(super) unknown: Vec<String>,
    pub(super) saved: Vec<(String, String)>,
}

impl IngestResult {
    fn clean(&self) -> bool {
        self.pending.is_empty() && self.unknown.is_empty() && self.refused.is_empty()
    }
}

/// Where the project lived before feature 329 moved it to the repository root: a sync recorded before the move names a commit that holds the list under this prefix.
const PRE_329: &str = ".claude/skills/diagram/";

fn at_commit(root: &Path, commit: &str) -> Result<String, String> {
    let mut named = format!("{commit}:{CANON}");
    let mut done = git(root, &["show", &named]);
    if !done.0 {
        named = format!("{commit}:{PRE_329}{CANON}");
        done = git(root, &["show", &named]);
    }
    if !done.0 {
        return Err(format!("the canonical list at {commit} cannot be read (git show failed) - is the clone synced in? scripts/sync-with-main.sh sync-in"));
    }
    Ok(universal(&done.1))
}

/// Text mode's newlines, as `subprocess.run(text=True)` reads a program's output.
pub(super) fn universal(text: &str) -> String {
    text.replace("\r\n", "\n").replace('\r', "\n")
}

/// The canonical list with the copy's marks recorded and the bodies the session was told to keep, and what happened to each entry.
pub(super) fn merge(
    texts: (&str, &str, &str),
    date: &str,
    keep: &HashSet<String>,
    drop: &HashSet<String>,
    resolve: &HashMap<String, String>,
) -> Result<(String, IngestResult), String> {
    let (canon_text, copy_text, base_text) = texts;
    let mut canon_blocks = parse(canon_text);
    let (_, canon) = by_id(&canon_blocks);
    let base_blocks = parse(base_text);
    let (_, base) = by_id(&base_blocks);
    let mut copy_blocks = parse(copy_text);
    let (copy_order, copy) = by_id(&copy_blocks);
    let mut out = IngestResult::default();
    for eid in &copy_order {
        let Some(&mine_at) = canon.get(eid) else {
            out.unknown.push(eid.clone());
            continue;
        };
        let c = entry_at(&mut copy_blocks, copy[eid]);
        if let Some(state) = resolve.get(eid) {
            if c.marks.as_ref().is_some_and(|m| !m.problem().is_empty()) {
                let marks = c.marks.as_ref().map(|m| m.resolved(state)).transpose()?;
                c.marks = marks;
            }
        }
        let c = c.clone();
        let mine = entry_at(&mut canon_blocks, mine_at);
        if let Some(marks) = c.marks.as_ref().filter(|m| Some(*m) != mine.marks.as_ref()) {
            let why = marks.problem();
            if why.is_empty() {
                mine.marks = Some(marks.clone());
                mine.recorded = Some(format!("- Marks recorded {date}"));
                out.recorded.push(eid.clone());
            } else {
                out.refused.push((eid.clone(), why.to_owned()));
            }
        }
        if let Some(saved) = c
            .marks
            .as_ref()
            .map(|m: &Marks| &m.saved)
            .filter(|s| !s.is_empty())
        {
            out.saved.push((eid.clone(), saved.clone()));
        }
        let old = base.get(eid).map(|i| entry_ref(&base_blocks, *i).whole());
        let theirs = c.whole();
        if old.as_deref() == Some(theirs.as_str()) {
            continue;
        }
        if drop.contains(eid) {
            out.dropped.push(eid.clone());
            continue;
        }
        if keep.contains(eid) {
            mine.heading.clone_from(&c.heading);
            mine.body.clone_from(&c.body);
            out.kept.push(eid.clone());
            continue;
        }
        let session_changed = old.as_ref().is_some_and(|o| mine.whole() != *o);
        let was = old.unwrap_or_default();
        let diff = unified_diff(
            &was.split('\n').collect::<Vec<_>>(),
            &theirs.split('\n').collect::<Vec<_>>(),
            "at the last sync",
            "your copy",
            1,
        )
        .join("\n");
        let lead = if session_changed {
            "CONFLICT - a session changed this entry too; the canonical text is kept unless KEEP=\n"
        } else {
            ""
        };
        out.pending.push((eid.clone(), format!("{lead}{diff}")));
    }
    Ok((render(&canon_blocks), out))
}

pub(super) fn ingest(
    ctx: &Ctx,
    keep: &HashSet<String>,
    drop: &HashSet<String>,
    resolve: &HashMap<String, String>,
    date: &str,
) -> Result<IngestResult, String> {
    let mut state = load_state(&ctx.root)?;
    let Some(commit) = state
        .get("synced")
        .map(|s| s["commit"].as_str().unwrap_or("").to_owned())
    else {
        return Err("the GM's copy has never been synced, so it holds no mark lines to read - run `make downloads-sync` first (on the GM's word)".to_owned());
    };
    let copy_text = read(&ctx.copy)?;
    let canon_path = ctx.root.join(CANON);
    let (text, out) = merge(
        (
            &read(&canon_path)?,
            &copy_text,
            &at_commit(&ctx.root, &commit)?,
        ),
        date,
        keep,
        drop,
        resolve,
    )?;
    std::fs::write(&canon_path, text).map_err(text_err)?;
    if out.clean() {
        state["ingested"] = json!({"sha256": sha(&copy_text), "date": date});
        save_state(&ctx.root, &state)?;
    }
    Ok(out)
}

/// Write the canonical list over the GM's copy (plan D5); returns the commit recorded as the base.
pub(super) fn sync(ctx: &Ctx, date: &str) -> Result<String, String> {
    let root = &ctx.root;
    let mut state = load_state(root)?;
    let canon_text = read(&root.join(CANON))?;
    if ctx.copy.exists() {
        let text = read(&ctx.copy)?;
        let have = sha(&text);
        let known = ["imported", "synced", "ingested"]
            .iter()
            .any(|k| state[*k]["sha256"].as_str() == Some(have.as_str()));
        if !known {
            return Err(changed_message(&text, &canon_text, &state));
        }
    }
    let uncommitted = !git(root, &["diff", "--quiet", "HEAD", "--", CANON]).0
        || !git(root, &["ls-files", "--error-unmatch", CANON]).0;
    if uncommitted {
        return Err(format!("{CANON} has uncommitted changes - commit it first, so the base the next ingest compares against is a commit"));
    }
    let commit = git(root, &["rev-parse", "HEAD"]).1.trim().to_owned();
    std::fs::write(&ctx.copy, &canon_text).map_err(text_err)?;
    state["synced"] = json!({"sha256": sha(&canon_text), "date": date, "commit": commit});
    save_state(root, &state)?;
    Ok(commit)
}

/// Name what the copy holds that is not in the canonical list, and how to bring it in.
fn changed_message(copy_text: &str, canon_text: &str, state: &Value) -> String {
    let canon_blocks = parse(canon_text);
    let (_, canon) = by_id(&canon_blocks);
    let copy_blocks: Vec<Block> = parse(copy_text);
    let mut names = Vec::new();
    for e in entries(&copy_blocks) {
        match canon.get(&e.id).map(|i| entry_ref(&canon_blocks, *i)) {
            None => names.push(format!("{} (not in the canonical list - add it with `make download-add FILE=<draft>`, or by hand at the end if it keeps its number)", e.id)),
            Some(mine) => {
                if (e.marks.is_some() && e.marks != mine.marks)
                    || e.body_text() != mine.body_text()
                    || e.heading != mine.heading
                {
                    names.push(e.id.clone());
                }
            }
        }
    }
    let first = state.get("synced").is_none();
    let lead = if first {
        "the GM's copy changed since the import, before any sync"
    } else {
        "the GM's copy holds changes not yet ingested"
    };
    let fix = if first {
        "bring each named entry into the canonical list (an added one with `make download-add`, a changed one by hand), then sync"
    } else {
        "run `make downloads-ingest` first (KEEP=/DROP= for text edits), then sync"
    };
    let shown = if names.is_empty() {
        "text outside any entry".to_owned()
    } else {
        names.join(", ")
    };
    format!("{lead}: {shown} - {fix}")
}

/// The access tag of every source an entry whose marks were recorded names (plan D4), one line each.
fn changed_tags(root: &Path, ids: &[String]) -> Result<Vec<String>, String> {
    if ids.is_empty() {
        return Ok(Vec::new());
    }
    let world = access_tags::load(root)?;
    let mut keys: BTreeSet<String> = BTreeSet::new();
    for eid in ids {
        let own = format!("download:{eid}");
        match world.entry_keys.get(&own).filter(|named| !named.is_empty()) {
            Some(named) => keys.extend(named.iter().cloned()),
            None => {
                keys.insert(own);
            }
        }
    }
    Ok(keys
        .iter()
        .map(|k| format!("{k}: {}", access_tags::tag(&world, k).line()))
        .collect())
}

/// entry id -> the file its saved-as line names, for the files present in the inbox (plan D7): the GM's naming matches a download to its entry without a question.
pub(super) fn inbox_matches(saved: &[(String, String)], inbox: &Path) -> Vec<(String, String)> {
    saved
        .iter()
        .filter(|(_, name)| !name.contains('/') && inbox.join(name).exists())
        .cloned()
        .collect()
}

/// The ingest report and its exit code.
pub(super) fn report(out: &IngestResult, root: &Path) -> Result<(String, i32), String> {
    let mut text = String::new();
    let listed = if out.recorded.is_empty() {
        String::new()
    } else {
        format!(" ({})", out.recorded.join(", "))
    };
    let _ = writeln!(
        text,
        "downloads: ingest - marks recorded on {} entries{listed}",
        out.recorded.len()
    );
    for (eid, why) in &out.refused {
        let _ = writeln!(
            text,
            "  NOT RECORDED {eid}: {why} - ask the GM which they meant, then MARK={eid}=<{}>",
            RESOLVE_STATES.join("|")
        );
    }
    for eid in &out.unknown {
        let _ = writeln!(text, "  NOT IN THE LIST {eid}: the GM's copy has an entry the canonical list lacks - bring it in by hand at the end");
    }
    for (eid, diff) in &out.pending {
        let _ = writeln!(
            text,
            "  TEXT EDIT {eid} - pending; KEEP={eid} records it, DROP={eid} discards it:\n{diff}"
        );
    }
    if !out.kept.is_empty() || !out.dropped.is_empty() {
        let or_dash = |v: &[String]| {
            if v.is_empty() {
                "-".to_owned()
            } else {
                v.join(", ")
            }
        };
        let _ = writeln!(
            text,
            "  text kept: {}; dropped: {}",
            or_dash(&out.kept),
            or_dash(&out.dropped)
        );
    }
    if !out.saved.is_empty() {
        let named: Vec<String> = out.saved.iter().map(|(k, v)| format!("{k}={v}")).collect();
        let _ = writeln!(text, "  saved-as files named: {}", named.join(", "));
    }
    for line in changed_tags(root, &out.recorded)? {
        let _ = writeln!(text, "  access {line}");
    }
    let after = if out.clean() {
        ""
    } else {
        "; sync stays refused until nothing is pending"
    };
    let _ = writeln!(text, "  commit {CANON} and {STATE}{after}");
    Ok((text, i32::from(!out.clean())))
}
