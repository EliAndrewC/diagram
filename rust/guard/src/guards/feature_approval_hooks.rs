//! `feature-approval-hooks` (feature 377; ported from the shell of the same name and the staging half of `lib/hm_approval.py`, feature 449
//! T025): A NEW SPEC-KIT FEATURE IS FILED ONLY WITH THE GM'S APPROVAL (the GM, 2026-10-10: "spec kit features should not be filed without my
//! explicit approval"). The `spec.md` of a new feature numbered 377 or above carries `**Approved**: the GM, YYYY-MM-DD, "<his words>"`, the
//! quote three words or more and found in a message he wrote in this session. A push may not land a closed feature open, nor hide a task
//! under a closed status line, without the same. There is no escape: the GM's approval is the way through.
//!
//! Plan T025's decisions: (a) the staging check in-process; (b) the push's check in-process too, a past revision read through git; (c) the library stays for its
//! other importers until T051.

use std::collections::BTreeSet;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;

use crate::guards::conflict_marker_hooks::staged_by;
use crate::guards::finished_run_hooks::runs::realpath;
use crate::protocol::{Answer, Event, Guard};
use crate::shared::log;
use crate::shared::session::Session;
// the status line, the closing words and the task box are `make speckit-todo`'s, one copy (feature 449 T118)
use crate::shared::speckit::{BOX, CLOSING, STATUS};
use crate::shared::state::field;
use crate::shared::tool::{ask, Said};
use crate::shared::transcript::norm;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "feature-approval-hooks",
    events: &["PreToolUse"],
    matcher: "Bash",
    decide,
};

pub const FIRST: u32 = 377;
/// The approval line's form, for a refusal to print.
pub const FORM: &str = "**Approved**: the GM, YYYY-MM-DD, \"<the GM's words, verbatim>\"";
const MIN_WORDS: usize = 3;
const STANDING: &str =
    "you should treat features that I have asked to be filed as automatic approval";

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static LINE: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?m)^\*\*Approved\*\*: the GM, (\d{4}-\d{2}-\d{2}), "(.+)"[ \t]*$"#));
static SPEC: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?:^|/)specs/(\d{3,})-([a-z0-9][a-z0-9-]*)/spec\.md$"));
static FILED_FOR_GM: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^# Request: EliAndrewC/diagram#\d+"));
static GIT_ADD: LazyLock<Regex> = LazyLock::new(|| re(r"\bgit(?:\s+-[Cc]\s+\S+)*\s+add\b"));
static GIT_COMMIT_ALL: LazyLock<Regex> = LazyLock::new(|| {
    re(r"\bgit(?:\s+-[Cc]\s+\S+)*\s+commit\b[^;&|]*\s(?:-[a-zA-Z]*a[a-zA-Z]*|--all)(?=\s|$)")
});
static PUSH: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?m)(?:^|[;&|(]\s*)(?:[A-Za-z_]\w*=\S*\s+)*(?:bash\s+)?[\w./$-]*sync-with-main\.sh\s+(?:done|push)\b",
    )
});
static OPEN_BOX: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^\s*- \[ \] (.*)$"));
static TASK_ID: LazyLock<Regex> = LazyLock::new(|| re(r"^(T\d+[a-z]?)\b"));
static CD: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?:^|[;&|]\s*|\s)cd\s+(['"]?)([^\s;&|'"]+)\1"#));

fn git(repo: &str, args: &[&str]) -> Said {
    let all: Vec<&str> = ["-C", repo]
        .into_iter()
        .chain(args.iter().copied())
        .collect();
    ask(Path::new("."), "git", &all, "")
}

/// The quotes of every approval line in a spec's text.
fn quotes(text: &str) -> Vec<String> {
    LINE.captures_iter(text)
        .filter_map(Result::ok)
        .map(|c| c[2].to_owned())
        .collect()
}

fn long_enough(q: &str) -> bool {
    norm(q).split(' ').count() >= MIN_WORDS
}

/// spec-lint's check 6, the push's backstop (feature 377): nothing when the text holds a well-formed approval line, else `no-line` or
/// `short`. The transcript the commit guard also reads is not there at the push.
#[must_use]
pub fn form_problem(text: &str) -> &'static str {
    let found = quotes(text);
    if found.is_empty() {
        "no-line"
    } else if found.iter().any(|q| long_enough(q)) {
        ""
    } else {
        "short"
    }
}

/// Nothing when the spec's approval stands, else `no-line`, `short` or `not-found`.
pub(crate) fn problem(text: &str, messages: &[String]) -> &'static str {
    let found = quotes(text);
    if found.is_empty() {
        return "no-line";
    }
    if !found.iter().any(|q| long_enough(q)) {
        return "short";
    }
    if found
        .iter()
        .filter(|q| long_enough(q))
        .any(|q| messages.iter().any(|m| m.contains(&norm(q))))
    {
        ""
    } else {
        "not-found"
    }
}

/// Is this `specs/NNN-slug/spec.md` a new feature, rather than one HEAD holds, at this path or renumbered?
pub(crate) fn is_new(top: &str, rel: &str, slug: &str) -> bool {
    if git(top, &["cat-file", "-e", &format!("HEAD:{rel}")]).ok()
        || git(top, &["cat-file", "-e", &format!("MERGE_HEAD:{rel}")]).ok()
    {
        return false; // the merge's other side holds a feature filed and approved where it was written
    }
    let renames = git(top, &["diff", "--cached", "-M", "--name-status"]).out;
    if renames
        .lines()
        .any(|l| l.starts_with('R') && l.rsplit('\t').next() == Some(rel))
    {
        return false;
    }
    // a renumber not yet staged: HEAD's spec of the same slug has LEFT; one beside a spec still there is a copy, and new
    let held = git(top, &["ls-tree", "--name-only", "HEAD", "specs/"]).out;
    let gone = git(top, &["diff", "--cached", "--name-only", "--diff-filter=D"]).out;
    let same_slug = re(&format!(r"^specs/\d{{3,}}-{}$", fancy_regex::escape(slug)));
    !held.split_whitespace().any(|d| {
        let old = format!("{d}/spec.md");
        old != rel
            && same_slug.is_match(d).unwrap_or(false)
            && (!Path::new(top).join(&old).exists() || gone.split_whitespace().any(|g| g == old))
    })
}

/// The file as the command would commit it: the working tree's for `add` and `commit -a`, else the index's.
fn text_of(top: &str, rel: &str, worktree: bool) -> String {
    let on_disk = worktree
        .then(|| std::fs::read(Path::new(top).join(rel)).ok())
        .flatten();
    on_disk.map_or_else(
        || git(top, &["show", &format!(":{rel}")]).out,
        |b| String::from_utf8_lossy(&b).into_owned(),
    )
}

/// Does a spec of an issue gm-assistant filed for the GM quote his standing approval (2026-10-18)?
pub(crate) fn standing(spec: &str, request: &str) -> bool {
    FILED_FOR_GM.is_match(request).unwrap_or(false)
        && request.contains("**[gm-assistant]**")
        && quotes(spec).iter().any(|q| norm(q).contains(STANDING))
}

/// (problem, path) for every new feature's spec this command would stage without an approval.
pub(crate) fn judge_staging(cmd: &str, base: &str, messages: &[String]) -> Vec<(String, String)> {
    let worktree =
        GIT_ADD.is_match(cmd).unwrap_or(false) || GIT_COMMIT_ALL.is_match(cmd).unwrap_or(false);
    let mut out = Vec::new();
    for path in staged_by(cmd, base) {
        let Ok(Some(found)) = SPEC.captures(&path) else {
            continue;
        };
        if found[1].parse::<u32>().unwrap_or(0) < FIRST {
            continue;
        }
        let parent = Path::new(&path)
            .parent()
            .filter(|p| p.is_dir())
            .map_or(base.to_owned(), |p| p.to_string_lossy().into_owned());
        let top = git(&parent, &["rev-parse", "--show-toplevel"]).out;
        let full = realpath(Path::new(&path));
        let rel = full
            .strip_prefix(&top)
            .map_or(path.clone(), |r| r.to_string_lossy().into_owned());
        if top.is_empty() || !is_new(&top, &rel, &found[2]) {
            continue;
        }
        let text = text_of(&top, &rel, worktree);
        let bad = problem(&text, messages);
        let request = Path::new(&rel).with_file_name("request.md");
        let waived = bad == "not-found"
            && standing(&text, &text_of(&top, &request.to_string_lossy(), worktree));
        if !bad.is_empty() && !waived {
            out.push((bad.to_owned(), rel));
        }
    }
    out
}

/// The repository a `sync-with-main.sh done|push` runs in: the last `cd` before it, else the cwd.
fn push_repo(cmd: &str, at: usize, base: &str) -> String {
    let last = CD
        .captures_iter(&cmd[..at])
        .filter_map(Result::ok)
        .last()
        .map(|c| c[2].to_owned());
    let dest = last.map_or_else(
        || base.to_owned(),
        |w| Path::new(base).join(w).to_string_lossy().into_owned(),
    );
    git(&dest, &["rev-parse", "--show-toplevel"]).out
}

/// A feature's state at a revision: `make speckit-todo`'s reading of its status line and tasks, and what the guard compares; also
/// `hm_approval._state_at` for the glyph clock's reopening walk (`l7r-gate reviews`, feature 449 T89, `ask:449-T89-reviews`).
pub struct AtRev {
    /// `closed`, `done - GM review pending` or `open`.
    pub state: &'static str,
    /// The spec's text at the revision.
    pub spec: String,
    /// Its unticked tasks, by id where they have one.
    pub open: BTreeSet<String>,
    /// Whether its status line closes it.
    pub status_closed: bool,
}

/// `specs/<dir>` at `rev` in the repository `top`, or None where it did not exist.
#[must_use]
pub fn at_rev(top: &str, rev: &str, dir: &str) -> Option<AtRev> {
    let prefix = format!("specs/{dir}");
    if git(top, &["ls-tree", "-r", "--name-only", rev, "--", &prefix])
        .out
        .is_empty()
    {
        return None;
    }
    let show = |name: &str| git(top, &["show", &format!("{rev}:{prefix}/{name}")]).out;
    let (spec, tasks, rows) = (show("spec.md"), show("tasks.md"), show("gm-review.jsonl"));
    let status = STATUS
        .captures(&spec)
        .ok()
        .flatten()
        .map_or(String::new(), |c| {
            c.get(1)
                .or_else(|| c.get(2))
                .map_or(String::new(), |m| m.as_str().trim().to_lowercase())
        });
    let status_closed = CLOSING.iter().any(|w| status.starts_with(w));
    let boxes: Vec<String> = BOX
        .captures_iter(&tasks)
        .filter_map(Result::ok)
        .map(|c| c[1].to_owned())
        .collect();
    let (total, ticked) = (boxes.len(), boxes.iter().filter(|b| *b != " ").count());
    let open_rows = rows
        .lines()
        .filter(|l| !l.trim().is_empty() && !l.contains("\"reviewed\""))
        .count();
    let state = if status_closed || (total > 0 && ticked == total) {
        "closed"
    } else if total > 0 && ticked + 1 == total && open_rows > 0 {
        "done - GM review pending"
    } else {
        "open"
    };
    let open = OPEN_BOX
        .captures_iter(&tasks)
        .filter_map(Result::ok)
        .map(|c| {
            let line = norm(&c[1]);
            TASK_ID
                .captures(&line)
                .ok()
                .flatten()
                .map_or_else(|| line.clone(), |id| id[1].to_owned())
        })
        .collect();
    Some(AtRev {
        state,
        spec,
        open,
        status_closed,
    })
}

/// Every feature CLOSED at the push's base and OPEN at HEAD, or with a task hidden under a status that still says closed, unless HEAD's
/// spec adds an approval the GM wrote in this session (the GM, 2026-10-10). Reopened, worked and closed again within the delta passes.
fn reopened(top: &str, messages: &[String]) -> Vec<(String, String)> {
    let base = git(top, &["merge-base", "HEAD", "origin/main"]).out;
    if base.is_empty() {
        return Vec::new();
    }
    let changed = git(top, &["diff", "--name-only", &base, "HEAD", "--", "specs/"]).out;
    let dirs: BTreeSet<&str> = changed
        .lines()
        .filter(|n| n.matches('/').count() >= 2)
        .filter_map(|n| n.split('/').nth(1))
        .collect();
    let mut out = Vec::new();
    for dir in dirs {
        let was = at_rev(top, &base, dir);
        let Some(now) = at_rev(top, "HEAD", dir) else {
            continue;
        };
        let reopen = was.as_ref().is_some_and(|w| w.state != "open") && now.state == "open";
        let before = was.as_ref().map_or(BTreeSet::new(), |w| w.open.clone());
        let hidden = now.status_closed
            && now
                .open
                .difference(&before)
                .any(|t| !t.starts_with("GM review (make gm-reviewed F="));
        if !(reopen || hidden) {
            continue;
        }
        let earlier = quotes(was.as_ref().map_or("", |w| w.spec.as_str()));
        let added: Vec<String> = quotes(&now.spec)
            .into_iter()
            .filter(|q| !earlier.contains(q) && long_enough(q))
            .collect();
        if !added
            .iter()
            .any(|q| messages.iter().any(|m| m.contains(&norm(q))))
        {
            let kind = if reopen { "reopened" } else { "hidden-open" };
            out.push((
                if added.is_empty() {
                    kind.to_owned()
                } else {
                    format!("{kind}-not-found")
                },
                format!("specs/{dir}/spec.md"),
            ));
        }
    }
    out
}

fn why(kind: &str, path: &str) -> String {
    let reason = match kind {
        "no-line" => "no approval line".to_owned(),
        "short" => "the approval quote is under three words - a bare \"yes\" approves nothing".to_owned(),
        "not-found" => "the quoted words are in no message the GM wrote in this session".to_owned(),
        "reopened" => "closed before, and this push lands it OPEN - finish its work and close it again, or add the GM's approval".to_owned(),
        "reopened-not-found" => "reopened and left open; the approval line it adds quotes words the GM did not write in this session".to_owned(),
        "hidden-open" => "an unticked task added under a status line that still says closed - speckit-todo would never show it".to_owned(),
        "hidden-open-not-found" => "a task added under a closed status; the approval line it adds quotes words the GM did not write in this session".to_owned(),
        other => other.to_owned(),
    };
    format!("  {path}: {reason}")
}

fn refusal(bad: &[(String, String)], input: &str, today: &str) -> String {
    let kinds = bad
        .iter()
        .map(|(k, _)| k.as_str())
        .collect::<Vec<_>>()
        .join(" ");
    let listed = bad
        .iter()
        .map(|(k, p)| why(k, p))
        .collect::<Vec<_>>()
        .join("\n");
    let mut text = format!("\n\u{1b}[1mBLOCKED: this would add a feature with open work the GM has not approved.\u{1b}[0m\n{listed}\n");
    if kinds.contains("reopened") {
        text += "\nReopening a feature to do its work yourself needs no approval: finish the work and close the feature\nagain (status Done, or every task ticked), THEN push. Until then the work stays committed in your clone,\nbacked up by every refused push. Only a feature you mean to land OPEN needs the GM's approval below.\n";
    }
    if kinds.contains("hidden-open") {
        text += "\nAdding a task under a closed status to do it yourself needs no approval: do the work and tick the task,\nTHEN push. Until then it stays committed in your clone, backed up by every refused push. Only work you mean\nto land undone needs the GM's approval below - and then its status line should say it is open.\n";
    }
    if input.contains("spec.md") {
        text += "\nThis command itself touches a spec.md, but the guard judged the file as it stands NOW, before the command\nruns: an approval line the command would write is not seen. Write and commit the approval line in its own\ncommand first, then run the git add / commit / sync-with-main.sh step on its own.\n";
    }
    if kinds.contains("not-found") {
        text += "\nAn issue gm-assistant filed for the GM (request.md opens \"# Request: EliAndrewC/diagram#N\") is approved by\nhis standing words (2026-10-18) - quote them on the line:\n  **Approved**: the GM, 2026-10-18, \"you should treat features that I have asked to be filed as automatic approval\"\n";
    }
    text + &format!(
        "\nA feature is filed only when the GM says to (the GM, 2026-10-10). Ask the GM in this session, in your\n\
final message rather than mid-stream, and prefer extending and reopening the feature the work came from.\n\
Once the GM approves, put their words on a line of its own in the spec.md, verbatim:\n  \
**Approved**: the GM, {today}, \"<the GM's words, verbatim>\"\n\
This guard reads the GM's own messages in this transcript (a picked AskUserQuestion answer is quoted\n\
with its question). There is no escape variable.\n"
    )
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let here = std::env::current_dir().unwrap_or_default();
    judge(event, session, &here.to_string_lossy())
}

pub(crate) fn judge(event: &Event, session: &Session, base: &str) -> Vec<Answer> {
    let input = event.input.to_string();
    let wanted = input.contains("sync-with-main.sh")
        || (input.contains("git") && (input.contains("add") || input.contains("commit")));
    let cmd = event
        .input
        .get("tool_input")
        .map_or("", |t| field(t, "command"));
    if !wanted || cmd.is_empty() {
        return Vec::new();
    }
    let mut bad = judge_staging(cmd, base, session.gm_messages());
    if let Ok(Some(push)) = PUSH.find(cmd) {
        let top = push_repo(cmd, push.start(), base);
        if !top.is_empty() {
            bad.extend(reopened(&top, session.gm_messages()));
        }
    }
    if bad.is_empty() {
        return Vec::new();
    }
    let mut kinds: Vec<&str> = bad.iter().map(|(k, _)| k.as_str()).collect();
    kinds.sort_unstable();
    kinds.dedup();
    log::fire(
        "feature-approval",
        "blocked",
        &format!("{} ", kinds.join(" ")),
        "unapproved-feature",
        &event.input,
        session,
    );
    let today = ask(Path::new("/"), "date", &["+%F"], "").out;
    vec![Answer::Refuse(refusal(&bad, &input, &today))]
}

#[cfg(test)]
mod tests;
