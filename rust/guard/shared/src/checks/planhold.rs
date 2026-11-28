//! A plan section or block is held while its review runs (feature 385 T85, from `hm_planhold.py`): a write that would change held text is refused, naming the running review, with no escape; a dead hold refuses nothing
//! (`purge` drops it at a hooked call's start, 451 T489, so 451 T496 retired the `PLAN_EDIT_OK` that passed one).
//! A hold is the tree's it was taken in (451 T123): a clone's worktrees share its check state (`state_path` reads the common dir, by
//! design), so a hold taken in the clone was written back - and refused - on the landing worktree's or a scratch worktree's own plan.

use std::collections::BTreeSet;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Map, Value};

use super::{map_mut, resolved, text};
use crate::plan_text::blocks;

/// A plan review returns in about 1-4 minutes (the evening's 42); past half an hour its hold is dead.
const HOLD_MAX_S: f64 = 1800.0;
const PENDING_S: f64 = 60.0;

fn re(pattern: &str) -> Regex {
    crate::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

/// A task's bundle is `plan-<feature>-<task>-<8 hex>`, the hex its tree's (451 T288); the bare `plan-<feature>-<task>` of a bundle
/// built before it still matches.
static BUNDLE: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(\S*/plan-(\d{3}-[a-z0-9-]+?)-(?:(T\d+[a-z]?)(?:-[0-9a-f]{8})?|blocks-[\w-]+))/MANIFEST\.md",
    )
});
static WRITE: LazyLock<Regex> = LazyLock::new(|| {
    re(r#"open\([^)]*['"][wa]['"]|write_text|\bsed\s+(?:-\S+\s+)*-i|>\s*['"]?\S*plan\.md|\btee\b"#)
});
/// A blocks bundle's key comment, `<!-- block "<the heading as plan.md holds it>" sha256 <hex> -->` (461 T70: it was JSON-escaped,
/// so a reviewer copying it into `make plan-verdict` was refused on a `\"`), read to the digest's fixed tail, never to a quote.
static BLOCK_KEY: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?m)^<!-- block "(.*)" sha256 [0-9a-f]{64} -->$"#));
static QUOTED: LazyLock<Regex> =
    LazyLock::new(|| re(r#""((?:[^"\\\n]|\\.){12,})"|'([^'\n]{12,})'"#));

/// The tree a bundle's MANIFEST says it was built from (`Built from the tree`, 451 T257), or None where it names none.
fn built_from(bundle: &str) -> Option<PathBuf> {
    let text = std::fs::read_to_string(Path::new(bundle).join("MANIFEST.md")).ok()?;
    let rest = text.split_once("Built from the tree `")?.1;
    Some(PathBuf::from(rest.split_once('`')?.0))
}

/// Record the hold a plan review's dispatch takes (at its `PreToolUse`): its tree is the one its bundle was built from - the plan
/// the review reads, and the one tree its write-back runs in (451 T123) - else `root`, the tree its call ran in. WHY the bundle's
/// (451 T295): a builder's dispatch runs with the session's clone as its cwd and its bundle is built from its worktree, so the
/// call's tree was the clone - a `make task-add` there was blamed for changing the worktree's reviewed section, and the clone's
/// text of it written back over the clone's own plan (seen 2026-11-26, T292's review).
pub fn hold(state: &mut Value, tid: &str, prompt: &str, now: f64, root: Option<&Path>) {
    let Ok(Some(m)) = BUNDLE.captures(prompt) else {
        return;
    };
    let bundle = m.get(1).map_or("", |g| g.as_str()).to_owned();
    let feature = m.get(2).map_or("", |g| g.as_str()).to_owned();
    let task = m.get(3).map(|g| g.as_str().to_owned());
    let keys: Vec<String> = if task.is_some() {
        Vec::new()
    } else {
        let text =
            std::fs::read_to_string(Path::new(&bundle).join("blocks.md")).unwrap_or_default();
        BLOCK_KEY
            .captures_iter(&text)
            .map_while(Result::ok)
            .map(|c| c[1].to_owned())
            .collect()
    };
    let mut h = json!({"feature": feature, "task": task.unwrap_or_default(), "blocks": keys, "t": now, "state": "pending"});
    if let Some(r) = built_from(&bundle).or_else(|| root.map(Path::to_path_buf)) {
        h["root"] = json!(r.to_string_lossy());
    }
    map_mut(state, "plan_holds").insert(tid.to_owned(), h);
}

/// The tree hold `h` was taken in, or None for a hold taken before 451 T123 recorded it.
fn taken_in(h: &Value) -> Option<PathBuf> {
    let r = text(h, "root");
    (!r.is_empty()).then(|| resolved(Path::new(r)))
}

/// Whether a call in `root` is written back for hold `h`: a call in the tree the hold was taken in, or in any tree for a hold that
/// recorded none (today's, until it returns). A call in another worktree of the clone changes another plan than the one reviewed:
/// written back, the hold refused that tree's own work and wrote one tree's text into the other (451 T123, measured 2026-11-21).
fn reaches(h: &Value, root: &Path) -> bool {
    taken_in(h).is_none_or(|t| t == resolved(root))
}

/// A hold's launch: its agent id.
pub fn launched(state: &mut Value, tid: &str, agent_id: &str) {
    if let Some(h) = state
        .get_mut("plan_holds")
        .and_then(Value::as_object_mut)
        .and_then(|holds| holds.get_mut(tid))
    {
        h["state"] = json!("running");
        h["aid"] = json!(agent_id);
    }
}

/// A review's return: its holds go, and the text kept for them.
pub fn returned(state: &mut Value, agent_id: &str) {
    if let Some(holds) = state.get_mut("plan_holds").and_then(Value::as_object_mut) {
        holds.retain(|_, h| h.get("aid").and_then(Value::as_str) != Some(agent_id));
    }
    prune_snaps(state);
}

/// The key a tree's held text is kept under in `plan_snaps` (451 T387), beside the call-keyed snapshots an earlier build wrote:
/// `tree:` and the tree's path, which no `tool_use_id` begins with.
fn tree_key(root: &Path) -> String {
    format!("tree:{}", resolved(root).display())
}

/// Each kept snapshot of a hold no longer open goes, and `plan_snaps` with the last of them: a stale entry kept `checks-hooks`
/// loading the state on every call's end.
fn prune_snaps(state: &mut Value) {
    let open: BTreeSet<String> = state.get("plan_holds").map_or_else(BTreeSet::new, set_of);
    if let Some(all) = state.get_mut("plan_snaps").and_then(Value::as_object_mut) {
        for s in all.values_mut().filter_map(Value::as_object_mut) {
            s.retain(|hid, _| open.contains(hid));
        }
        all.retain(|_, s| !set_of(s).is_empty());
        if all.is_empty() {
            state
                .as_object_mut()
                .and_then(|m| m.shift_remove("plan_snaps"));
        }
    }
}

fn t_of(h: &Value) -> f64 {
    h.get("t").and_then(Value::as_f64).unwrap_or(0.0)
}

fn dead(h: &Value, now: f64) -> bool {
    (text(h, "state") == "pending" && now - t_of(h) > PENDING_S) || now - t_of(h) > HOLD_MAX_S
}

/// What a write is judged against: each held block, or a held task's section joined as `task_sections` reads it - the places it
/// stands put together, which for a task whose own headings stand apart stands nowhere in the plan (451 T80 changed the write-back
/// alone; the refusal reading each place is T120).
fn held(root: &Path, h: &Value) -> Vec<String> {
    let places = held_places(root, h);
    if text(h, "task").is_empty() || places.len() < 2 {
        return places;
    }
    vec![places.concat()]
}

/// A hold whose review was launched and has not died (`hm_planhold.live`).
#[must_use]
pub fn live(h: &Value, now: f64) -> bool {
    text(h, "state") == "running" && !dead(h, now)
}

/// A dead hold goes - a pending one past `PENDING_S` never launched and never will, a running one past `HOLD_MAX_S` lost its return
/// (a session killed, a stop no hook saw) - so an empty state starts nothing; and the text kept for a hold gone. WHY the running one too
/// (451 T489): kept, it held `plan_holds` non-empty, so every Bash call of the clone paid the state's load (about 40 ms after 451 T387)
/// and its held text stayed refused without `PLAN_EDIT_OK`. Purged, it puts nothing back: `prune_snaps` drops its kept text, so a call
/// begun under it writes nothing back at its end, and its review's late return names no hold or dispatch and is booked by nothing.
pub fn purge(state: &mut Value, now: f64) {
    if let Some(holds) = state.get_mut("plan_holds").and_then(Value::as_object_mut) {
        holds.retain(|_, h| !dead(h, now));
    }
    prune_snaps(state);
}

/// Before a write: the texts each live hold holds, kept ONCE a hold and tree (451 T387), at the first call there - never retaken at a
/// later call's start. WHY: a snapshot under each call's id made every Bash call under a hold save the whole check state twice (3.0 MB,
/// 97 to 118 ms of CPU, T373's lever E); and a call begun while another's change stood took the changed text as its own, so its end
/// wrote that change back over the first call's restore (red on HEAD: `a_command_that_overwrote_held_text_is_still_written_back`).
/// A change no hooked call made (an editor, a command past its one `PostToolUse`) is written back at the next call's end, where it
/// was taken as held before.
pub fn snapshot(state: &mut Value, root: Option<&Path>, now: f64) {
    purge(state, now);
    let Some(root) = root else {
        return;
    };
    let key = tree_key(root);
    let kept = state.get("plan_snaps").and_then(|m| m.get(&key));
    let fresh: Map<String, Value> = state
        .get("plan_holds")
        .and_then(Value::as_object)
        .into_iter()
        .flatten()
        .filter(|(id, h)| {
            live(h, now) && reaches(h, root) && kept.and_then(|k| k.get(*id)).is_none()
        })
        .map(|(id, h)| (id.clone(), json!(held_places(root, h))))
        .collect();
    if !fresh.is_empty() {
        let entry = map_mut(state, "plan_snaps")
            .entry(key)
            .or_insert_with(|| json!({}));
        if let Some(m) = entry.as_object_mut() {
            m.extend(fresh);
        }
    }
}

/// The places a hold's text stands in `body`, as byte spans in document order: each place a held task's section stands
/// (`plan_text::section_places`, its own headings' spans with adjacent ones joined), or each held block.
fn places(body: &str, h: &Value) -> Vec<(usize, usize)> {
    let task = text(h, "task");
    if !task.is_empty() {
        return crate::plan_text::section_places(body, task);
    }
    let want: Vec<&str> = h
        .get("blocks")
        .and_then(Value::as_array)
        .map(|a| a.iter().filter_map(Value::as_str).collect())
        .unwrap_or_default();
    blocks(body)
        .into_iter()
        .filter(|(k, ..)| want.contains(&k.as_str()))
        .map(|(_, b, at)| (at, at + b.len()))
        .collect()
}

/// What the write-back keeps of a hold: one text a place it stands (451 T80; [`held`], the section joined, is what a write is judged
/// against, and stands nowhere in the plan for a task whose own headings stand apart).
fn held_places(root: &Path, h: &Value) -> Vec<String> {
    let plan = root.join("specs").join(text(h, "feature")).join("plan.md");
    let Ok(body) = std::fs::read_to_string(plan) else {
        return Vec::new();
    };
    places(&body, h)
        .into_iter()
        .map(|(a, b)| body[a..b].to_owned())
        .collect()
}

fn set_of(snaps: &Value) -> BTreeSet<String> {
    snaps
        .as_object()
        .into_iter()
        .flatten()
        .map(|(k, _)| k.clone())
        .collect()
}

fn describe(h: &Value) -> String {
    if text(h, "task").is_empty() {
        format!(
            "{} block(s)",
            h.get("blocks")
                .and_then(Value::as_array)
                .map_or(0, Vec::len)
        )
    } else {
        format!("{}'s section", text(h, "task"))
    }
}

/// A place's heading line, shown at most 60 characters.
fn head_of(place: &str) -> String {
    place
        .lines()
        .next()
        .unwrap_or("")
        .trim()
        .chars()
        .take(60)
        .collect()
}

/// Where each place held when the call began stands now: the same place by order where the plan holds as many, else the place its
/// heading heads - never one whose old text holds a place's heading past its own first line, since writing it back would stand text
/// twice: a held heading gone leaves the text under it in another place or outside the section (HEAD wrote the joined text over the
/// one place left and stood the far part twice, and with the first heading gone wrote its text over the place the next heading
/// heads, measured 2026-11-21 by `a_place_no_write_back_can_find_is_named` and `a_first_heading_gone_is_not_written_twice`), and a
/// snapshot taken before 451 T80 holds a split section joined.
fn paired(body: &str, now: &[(usize, usize)], before: &[String]) -> Vec<Option<usize>> {
    let heads: Vec<&str> = now
        .iter()
        .map(|(a, b)| body[*a..*b].lines().next().unwrap_or(""))
        .collect();
    let twice = |old: &str, at: usize| {
        let first = old.lines().next().unwrap_or("");
        (0..now.len()).any(|i| {
            !heads[i].is_empty()
                && (i != at || heads[i] != first)
                && old.contains(&format!("\n{}", heads[i]))
        })
    };
    if now.len() == before.len() {
        return before
            .iter()
            .enumerate()
            .map(|(i, old)| (!twice(old, i)).then_some(i))
            .collect();
    }
    let mut taken = vec![false; now.len()];
    let mut out = Vec::with_capacity(before.len());
    for old in before {
        let first = old.lines().next().unwrap_or("");
        let at = (0..now.len()).find(|i| !taken[*i] && heads[*i] == first);
        let at = at.filter(|at| !twice(old, *at));
        if let Some(i) = at {
            taken[i] = true;
        }
        out.push(at);
    }
    out
}

/// Writes back each held place a call changed, and says which it wrote back; one it could not find, or a place new since the call
/// began, it names, and a call that restored nothing says so (451 T80: the joined section was replaced, and stands nowhere whole for a
/// task whose own headings stand apart, so nothing was restored and "the held text is written back" said all the same).
fn write_back(root: &Path, h: &Value, before: &[String]) -> Option<String> {
    let feature = text(h, "feature");
    let plan = root.join("specs").join(feature).join("plan.md");
    let body = std::fs::read_to_string(&plan).ok()?;
    let now = places(&body, h);
    let pairs = paired(&body, &now, before);
    let mut changed: Vec<(usize, usize, &str)> = Vec::new();
    let mut restored = Vec::new();
    let mut missed = Vec::new();
    let whole = if text(h, "task").is_empty() {
        "the plan"
    } else {
        "the section"
    };
    for (old, at) in before.iter().zip(&pairs) {
        match at {
            Some(i) if body[now[*i].0..now[*i].1] != **old => {
                changed.push((now[*i].0, now[*i].1, old));
                restored.push(format!("`{}`", head_of(old)));
            }
            Some(_) => {}
            None => missed.push(format!("`{}` (gone from {whole})", head_of(old))),
        }
    }
    for (i, (a, b)) in now.iter().enumerate() {
        if !pairs.contains(&Some(i)) {
            missed.push(format!(
                "`{}` (new to {whole} since the call began)",
                head_of(&body[*a..*b])
            ));
        }
    }
    if !changed.is_empty() {
        let mut fixed = body.clone();
        changed.sort_by_key(|c| std::cmp::Reverse(c.0));
        for (a, b, old) in &changed {
            fixed.replace_range(*a..*b, old);
        }
        std::fs::write(&plan, fixed).ok()?;
    }
    let by_hand = format!(
        "put it back by hand (`git -C {} diff -- specs/{feature}/plan.md` shows the change) or `make plan-verdict` refuses the review's verdict as changed (451 T80)",
        root.display()
    );
    let what = if !missed.is_empty() && restored.is_empty() {
        format!(
            "NOTHING of it is written back: {}; {by_hand}",
            missed.join(", ")
        )
    } else if !missed.is_empty() {
        format!(
            "written back: {}; NOT written back: {}; {by_hand}",
            restored.join(", "),
            missed.join(", ")
        )
    } else if text(h, "task").is_empty() || now.len() < 2 {
        "the held text is written back".to_owned()
    } else {
        format!(
            "the held text is written back in {} ({} of its {} places changed)",
            restored.join(", "),
            restored.len(),
            now.len()
        )
    };
    Some(format!(
        "that call changed {} of specs/{feature}/plan.md while its plan review runs (agent {}) - {what}; wait for the review to return (feature 385 T85, hour 30's fix)",
        describe(h),
        text(h, "aid")
    ))
}

/// After the write: any held text it changed is written back and the change refused, naming the review; or "".
/// A call's own snapshot (an earlier build's, under its id) is read first, then its tree's kept text; after a write-back the tree's
/// kept text is retaken, so a place no write-back could find is named once, not at every later call (451 T387).
pub fn restore(state: &mut Value, root: Option<&Path>, tid: &str) -> String {
    let own = state
        .get_mut("plan_snaps")
        .and_then(Value::as_object_mut)
        .and_then(|m| m.shift_remove(tid));
    prune_snaps(state);
    let Some(root) = root else {
        return String::new();
    };
    let key = tree_key(root);
    let kept = state.get("plan_snaps").and_then(|m| m.get(&key)).cloned();
    let holds = state.get("plan_holds").cloned().unwrap_or(Value::Null);
    for (hid, before) in own
        .iter()
        .chain(&kept)
        .filter_map(Value::as_object)
        .flatten()
    {
        // a snapshot under a call's id is its own tree's; one under no id (a test's call) is any tree's, so the tree is asked here too
        let Some(h) = holds.get(hid).filter(|h| !h.is_null() && reaches(h, root)) else {
            continue;
        };
        let before: Vec<String> = before
            .as_array()
            .map(|a| {
                a.iter()
                    .filter_map(|v| v.as_str().map(str::to_owned))
                    .collect()
            })
            .unwrap_or_default();
        // a snapshot taken before 451 T80 holds a split section joined: the same text in fewer places is no change
        let now = held_places(root, h);
        if now == before || (now.len() != before.len() && now.concat() == before.concat()) {
            continue;
        }
        if let Some(msg) = write_back(root, h, &before) {
            let after = json!(held_places(root, h));
            if let Some(k) = state
                .get_mut("plan_snaps")
                .and_then(|m| m.get_mut(&key))
                .and_then(Value::as_object_mut)
                .filter(|k| k.contains_key(hid))
            {
                k.insert(hid.clone(), after);
            }
            return msg;
        }
    }
    String::new()
}

/// Whether held text `texts` would change under an Edit of the plan with `old`: the edit's text overlaps held text, both ends
/// exclusive (451 T77: `a <= start + t.len()` read an edit of the next section's heading as inside the held one, and an edit starting
/// before the section and ending inside it went unseen), or `old` stands in held text (a `replace_all`).
fn edit_hits(plan: &Path, texts: &[String], old: &str) -> bool {
    let current = std::fs::read_to_string(plan).unwrap_or_default();
    let at = if old.is_empty() {
        None
    } else {
        current.find(old)
    };
    texts.iter().any(|t| {
        current
            .find(t.as_str())
            .is_some_and(|start| at.is_some_and(|a| a < start + t.len() && start < a + old.len()))
    }) || texts.iter().any(|t| !old.is_empty() && t.contains(old))
}

/// The plan with each held text cut out, a NUL in its place so the text on either side never joins into a match; or None where a
/// held text does not stand in the plan whole (a task's own headings apart, joined by `task_sections`), so nothing is read as outside.
fn outside(plan: &Path, texts: &[String]) -> Option<String> {
    let mut body = std::fs::read_to_string(plan).ok()?;
    for t in texts {
        if !body.contains(t.as_str()) {
            return None;
        }
        body = body.replacen(t.as_str(), "\0", 1);
    }
    Some(body)
}

/// Whether a shell command writes the plan through held text: a held heading, a held line of 16 or more characters, or a quoted
/// string held text contains; with `rest` (the plan outside the held text), only one that `rest` does not hold too (451 T78).
fn bash_hits(cmd: &str, feature: &str, texts: &[String], rest: Option<&str>) -> bool {
    if !(cmd.contains("plan.md") && cmd.contains(feature) && WRITE.is_match(cmd).unwrap_or(false)) {
        return false;
    }
    let held_only = |s: &str| rest.is_none_or(|r| !r.contains(s));
    let lines: BTreeSet<&str> = texts
        .iter()
        .flat_map(|t| t.lines())
        .map(str::trim)
        .filter(|l| l.len() >= 16 && held_only(l))
        .collect();
    let heads: BTreeSet<&str> = texts
        .iter()
        .filter(|t| !t.trim().is_empty())
        .map(|t| t.lines().next().unwrap_or("").trim())
        .filter(|h| held_only(h))
        .collect();
    let quoted: Vec<String> = QUOTED
        .captures_iter(cmd)
        .map_while(Result::ok)
        .flat_map(|c| [c.get(1), c.get(2)])
        .flatten()
        .map(|g| g.as_str().to_owned())
        .collect();
    heads.iter().any(|h| cmd.contains(h))
        || lines.iter().any(|l| cmd.contains(l))
        || quoted
            .iter()
            .any(|q| held_only(q) && texts.iter().any(|t| t.contains(q)))
}

/// Why this write is refused while a plan review holds what it would change, or "". A dead hold is skipped, as `purge` would
/// have dropped it (451 T496).
pub fn refusal(state: &Value, root: Option<&Path>, tool: &str, ti: &Value, now: f64) -> String {
    let Some(root) = root else {
        return String::new();
    };
    for h in state
        .get("plan_holds")
        .and_then(Value::as_object)
        .map(|m| m.values().cloned().collect::<Vec<_>>())
        .unwrap_or_default()
    {
        // an Edit or Write is judged against the plan of the tree the hold was taken in, wherever the call runs: an edit of another
        // tree's plan voids no verdict, and one of the held plan by its absolute path does (451 T123)
        let tree = taken_in(&h).unwrap_or_else(|| root.to_path_buf());
        let plan = tree.join("specs").join(text(&h, "feature")).join("plan.md");
        let texts = held(&tree, &h);
        if texts.is_empty() || dead(&h, now) {
            continue;
        }
        let hit = if matches!(tool, "Edit" | "Write" | "MultiEdit")
            && resolved(Path::new(text(ti, "file_path"))) == resolved(&plan)
        {
            if tool == "Write" {
                let content = text(ti, "content");
                texts.iter().any(|t| !content.contains(t.as_str()))
            } else {
                edit_hits(&plan, &texts, text(ti, "old_string"))
            }
        } else if tool == "Bash" && reaches(&h, root) {
            // a shell write from another tree the hold judges not, as no write-back runs there either: by a relative path it writes
            // that tree's own plan (451 T123: judged against the held tree's text, a write of text every section shares to the landing
            // worktree's own plan was refused, found by T123's plan review, measured 2026-11-21); one naming the held plan by its
            // absolute path passes and is written back by nothing - accepted (451 T123's plan section: none of the transcripts' 161
            // shell commands naming a plan by its absolute path wrote one of another tree sharing the call's state), the cost a verdict
            // `make plan-verdict` refuses.
            // A live hold's foreground call is written back when it ends (`snapshot` keeps live holds alone; `restore` runs on its
            // PostToolUse or PostToolUseFailure), so for it only text standing in the held section alone names a write there: text
            // every section shares named a write to ANOTHER section, 7 of the 18 replayed refusals (451 T78). A pending hold and
            // a background call have no write-back behind them, and shared text still refuses them. A foreground call moved to
            // the background at its timeout gets its one PostToolUse at the move (measured 2026-11-21), so what it writes after
            // the move is written back by nothing, nor what a writer it detaches writes after the shell returns: accepted (451 T78's
            // plan section, priced there), the cost a verdict `make plan-verdict` refuses as changed while reviewed, the review run again
            let rest = (live(&h, now) && !crate::wait::background(ti))
                .then(|| outside(&plan, &texts))
                .flatten();
            bash_hits(
                text(ti, "command"),
                text(&h, "feature"),
                &texts,
                rest.as_deref(),
            )
        } else {
            false
        };
        if hit {
            let who = if text(&h, "aid").is_empty() {
                "a dispatch not yet launched".to_owned()
            } else {
                format!("agent {}", text(&h, "aid"))
            };
            return format!(
                "the plan review of {} in specs/{}/plan.md is running ({who}) - an edit now voids its verdict; wait for it to return (feature 385 T85)",
                describe(&h),
                text(&h, "feature")
            );
        }
    }
    String::new()
}

#[cfg(test)]
mod tests;
