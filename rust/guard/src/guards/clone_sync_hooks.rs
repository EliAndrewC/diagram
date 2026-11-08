//! `clone-sync-hooks` (features 129, 168, 204, 212, 385; ported from `scripts/hooks/clone-sync-hooks.sh`, feature 449 T013): EVERY
//! SESSION WORKS IN ITS OWN CLONE, ON A CURRENT BASE. On a prompt the session's clone is synced with main (or, mid-task, only the
//! mirror refreshed); an edit into a clone is refused where the clone is not this session's, is forbidden by name, is another live
//! session's, or is behind main and could not be fast-forwarded - and a clean clone behind main is fast-forwarded first. A dirty
//! clone's make run is told it is behind main. The refusals' words are the shell's; the reasons stand in its comments, kept in git
//! history.
//!
//! Plan T013's decisions: (a) git and the tools it asks stay theirs, asked by path; (b) the session's facts are read in-process;
//! (c) `resolve` stays in the shell script, needing no binary; (d) the prompt's lines are plain stdout, as the shell printed them.

use std::path::{Path, PathBuf};
use std::sync::LazyLock;
use std::time::Duration;

use fancy_regex::Regex;
use serde_json::Value;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::log;
use crate::shared::make::targets;
use crate::shared::session::Session;
use crate::shared::state::field;
use crate::shared::tool::{ask, within, Said};

/// The guard.
/// The tools it takes: an edit, for the routing and the stale base, and a Bash call, for the behind-main notice. The shell was wired
/// for the edits alone (`.claude/settings.json` since 2026-08-25), so the notice the GM asked for on 2026-09-05 - and its suite
/// tests - never reached a session; the Bash call is added here as the defect's fix (constitution XIV, T013).
pub const GUARD: Guard = Guard {
    name: "clone-sync-hooks",
    events: &["PreToolUse", "UserPromptSubmit"],
    matcher: "Edit|Write|NotebookEdit|Bash",
    decide,
};

/// The make targets that run tests, whose clone a behind-main notice is for.
const BEHIND_TEST_TARGETS: [&str; 22] = [
    "quick",
    "test",
    "test-file",
    "test-full",
    "done",
    "verify",
    "reference",
    "maps",
    "hooks-test",
    "idle-tests",
    "cohort",
    "tripwire",
    "regressions",
    "perf",
    "perf-gate",
    "cov-file",
    "durations",
    "collect-cost",
    "parts-sweep",
    "tooling",
    "page-check",
    "soak",
];

static ENGINE_PATH: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"^(l7r/.*\.py|pool/.*\.(gen\.py|json))$").unwrap_or_else(|e| unreachable!("{e}"))
});

/// What one decision reads: the event, the session, the mirror, the tree's tools and the interpreter they run under.
pub(crate) struct Ctx<'a> {
    pub event: &'a Event,
    pub session: &'a Session,
    pub main: PathBuf,
    pub tree: PathBuf,
    /// The interpreter the tree's Python tools run under (`python3`; a test's fakes are `sh`).
    pub python: &'static str,
}

impl Ctx<'_> {
    fn input(&self, k: &str) -> &str {
        field(&self.event.input, k)
    }

    fn tool_input(&self, k: &str) -> &str {
        self.event
            .input
            .get("tool_input")
            .map_or("", |t| field(t, k))
    }

    fn mapdir(&self) -> PathBuf {
        self.main.join(".clones/.session-clones")
    }

    fn block(&self, rule: &str, detail: &Path) {
        log::fire(
            "clone-sync",
            "blocked",
            &detail.to_string_lossy(),
            rule,
            &self.event.input,
            self.session,
        );
    }

    fn permit(&self, rule: &str, detail: &Path) {
        log::fire(
            "clone-sync",
            "permitted",
            &detail.to_string_lossy(),
            rule,
            &self.event.input,
            self.session,
        );
    }

    /// A make run, or a running gate's lock, in `clone` (`own-make.sh ""` and `gate_lock.py held`).
    fn running(&self, clone: &Path) -> bool {
        if ask(
            clone,
            &self
                .tree
                .join("scripts/hooks/lib/own-make.sh")
                .to_string_lossy(),
            &[""],
            "",
        )
        .ok()
        {
            return true;
        }
        let lock = clone.join("scripts/gates/gate_lock.py");
        lock.is_file() && {
            let gitdir = git(clone, &["rev-parse", "--absolute-git-dir"]).out;
            ask(
                Path::new("/"),
                self.python,
                &[&lock.to_string_lossy(), "held", &gitdir],
                "",
            )
            .ok()
        }
    }
}

/// `git -C dir args`.
fn git(dir: &Path, args: &[&str]) -> Said {
    let d = dir.to_string_lossy();
    let all: Vec<&str> = ["-C", d.as_ref()]
        .into_iter()
        .chain(args.iter().copied())
        .collect();
    ask(Path::new("/"), "git", &all, "")
}

/// The clone has uncommitted work.
fn dirty(clone: &Path) -> bool {
    let s = git(clone, &["status", "--porcelain"]);
    s.ok() && !s.out.is_empty()
}

/// A clone named after a repository, never a session's (`forbidden_clone`).
fn forbidden(path: &Path, main: &Path) -> bool {
    let name = path
        .file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default();
    name == "gm-assistant"
        || main
            .file_name()
            .is_some_and(|m| m.to_string_lossy() == name)
}

/// Whether a live process backs session `sid` (`sid_is_live`): its sessions json's file name is its pid, and that pid runs claude.
fn sid_is_live(sid: &str, sessions_dir: &Path) -> bool {
    let Ok(entries) = std::fs::read_dir(sessions_dir) else {
        return false;
    };
    let pid = entries
        .filter_map(Result::ok)
        .map(|e| e.path())
        .filter(|p| p.extension().is_some_and(|x| x == "json"))
        .find_map(|p| {
            let d: Value = serde_json::from_str(&std::fs::read_to_string(&p).ok()?).ok()?;
            let ids = ["id", "sessionId", "session_id"]
                .map(|k| d.get(k).and_then(Value::as_str).unwrap_or(""));
            ids.contains(&sid).then(|| {
                p.file_stem()
                    .map(|s| s.to_string_lossy().into_owned())
                    .unwrap_or_default()
            })
        });
    pid.filter(|p| !p.is_empty() && p.chars().all(|c| c.is_ascii_digit()))
        .and_then(|p| std::fs::read(format!("/proc/{p}/cmdline")).ok())
        .is_some_and(|c| {
            String::from_utf8_lossy(&c)
                .replace('\0', " ")
                .contains("claude")
        })
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let tree = std::env::var("L7R_GUARD_TREE").map_or_else(
        |_| std::env::current_dir().unwrap_or_default(),
        PathBuf::from,
    );
    judge(&Ctx {
        event,
        session,
        main: session.main().to_path_buf(),
        tree,
        python: "python3",
    })
}

pub(crate) fn judge(cx: &Ctx) -> Vec<Answer> {
    if cx.event.name == "UserPromptSubmit" {
        let lines = prompt(cx);
        return if lines.is_empty() {
            Vec::new()
        } else {
            vec![Answer::Print(lines.join("\n"))]
        };
    }
    pretool(cx)
}

/// One line of context for a dirty clone's test run behind main, or None (`behind_main_notice`).
fn behind_main(cx: &Ctx, clone: &Path) -> Option<String> {
    let cmd = cx.tool_input("command");
    if cx.event.tool() != "Bash"
        || cmd.is_empty()
        || !targets(cmd)
            .iter()
            .any(|t| BEHIND_TEST_TARGETS.contains(&t.as_str()))
    {
        return None;
    }
    let refd = git(&cx.main, &["rev-parse", "--verify", "-q", "origin/main"]);
    if !refd.ok()
        || refd.out.is_empty()
        || git(clone, &["merge-base", "--is-ancestor", &refd.out, "HEAD"]).ok()
    {
        return None;
    }
    let range = format!("HEAD..{}", refd.out);
    let n = Some(git(clone, &["rev-list", "--count", &range]).out)
        .filter(|n| !n.is_empty() && n != "0")
        .unwrap_or_else(|| "new".to_owned());
    let eng = git(clone, &["diff", "--name-only", &range])
        .out
        .lines()
        .filter(|l| ENGINE_PATH.is_match(l).unwrap_or(false))
        .count();
    let why = if eng > 0 {
        format!("{eng} changed file(s) are ENGINE paths, so the gate result you are building toward will be re-keyed and `make done` will have to run again anyway")
    } else {
        "no changed file is an engine path, so your gate result still stands - this is a cheap merge whenever you want it".to_owned()
    };
    Some(format!(
        "BEHIND MAIN (notice, not a block): main has {n} commit(s) this clone does not have, and {why}. Your tree is dirty, so nothing was \
merged - mid-task work is sacred and a merge mid-diagnosis would change the code under test underneath you. PULL IT IN AS SOON AS IT IS \
APPROPRIATE: when you are not reproducing or bisecting something, run `cd {} && scripts/sync-with-main.sh sync-in`, resolve any \
conflicts, and carry on. Not urgent, not ignorable.",
        clone.display()
    ))
}

fn pretool(cx: &Ctx) -> Vec<Answer> {
    let sid = cx.input("session_id");
    if cx.event.input.to_string().contains("make") && cx.event.tool() == "Bash" {
        let claimed = (!sid.is_empty())
            .then(|| std::fs::read_to_string(cx.mapdir().join(sid)).ok())
            .flatten()
            .unwrap_or_default();
        let clone = PathBuf::from(&claimed);
        if !claimed.is_empty() && clone.join(".git").is_dir() && dirty(&clone) {
            return behind_main(cx, &clone)
                .map(|n| vec![Answer::Notice(n)])
                .unwrap_or_default();
        }
        return Vec::new();
    }
    let fp = cx.tool_input("file_path");
    let prefix = format!("{}/.clones/", cx.main.display());
    let Some(rest) = fp.strip_prefix(&prefix).filter(|r| {
        r.split_once('/')
            .is_some_and(|(_, after)| !after.is_empty())
    }) else {
        return Vec::new(); // not a clone file - this hook has no opinion
    };
    let clone = cx
        .main
        .join(".clones")
        .join(rest.split('/').next().unwrap_or(""));
    if !clone.join(".git").is_dir() {
        return Vec::new();
    }
    let canon = cx.session.canonical();
    let claim = || {
        if !sid.is_empty() {
            let _ = std::fs::create_dir_all(cx.mapdir());
            let _ = std::fs::write(cx.mapdir().join(sid), clone.to_string_lossy().as_bytes());
        }
    };
    if dirty(&clone) {
        claim();
        return Vec::new();
    }
    if let Some(refused) = misrouted(cx, &clone, canon.as_deref(), sid) {
        return vec![refused];
    }
    claim();
    behind(cx, &clone)
}

/// The edit's clone refused where it is forbidden, another session's by name, or another live session's claim.
fn misrouted(cx: &Ctx, clone: &Path, canon: Option<&Path>, sid: &str) -> Option<Answer> {
    let base = |p: &Path| {
        p.file_name()
            .map(|n| n.to_string_lossy().into_owned())
            .unwrap_or_default()
    };
    if let Some(c) = canon.filter(|c| forbidden(c, &cx.main)) {
        cx.block("forbidden-name-unnamed", clone);
        return Some(Answer::Refuse(format!(
            "BLOCKED: this session has no distinct name - it resolves to the FORBIDDEN '.clones/{}' (a repository's name, not a session \
workspace). Ask the GM to /rename this session to something distinct, then work in .clones/<that-name>.   (CLAUDE.md 'Session clones' - \
forbidden clone names)",
            base(c)
        )));
    }
    if forbidden(clone, &cx.main) {
        cx.block("forbidden-name", clone);
        let resolves = canon
            .map(|c| format!(" (this session resolves to {})", c.display()))
            .unwrap_or_default();
        return Some(Answer::Refuse(format!(
            "BLOCKED: '.clones/{}' is a FORBIDDEN clone name (a repository's name, not a session). Work in .clones/<your-session-name>{resolves}. \
  (CLAUDE.md 'Session clones' - forbidden clone names)",
            base(clone)
        )));
    }
    if let Some(c) = canon.filter(|c| *c != clone) {
        cx.block("name-routing", clone);
        let (m, c) = (cx.main.display(), c.display());
        return Some(Answer::Refuse(format!(
            "BLOCKED: this session's clone is {c} (resolved from its session name); the edit targets {}. Two sessions must never share a \
working tree (the 2026-07-22 collision). Work in {c} - if it does not exist: git clone {m} {c} && cd {c} && git config user.name \
\"$(git -C {m} config user.name)\" && git config user.email \"$(git -C {m} config user.email)\" && scripts/sync-with-main.sh sync-in   \
(CLAUDE.md 'Session clones' - name-routing guard)",
            clone.display()
        )));
    }
    let dispatcher = std::env::var("L7R_DISPATCHER").unwrap_or_default();
    let entries = (!sid.is_empty())
        .then(|| std::fs::read_dir(cx.mapdir()).ok())
        .flatten()?;
    let other = entries
        .filter_map(Result::ok)
        .map(|e| e.path())
        .filter(|p| p.is_file())
        .find(|m| {
            let other = base(m);
            !other.starts_with('.')
                && other != sid
                && (dispatcher.is_empty() || other != dispatcher)
                && std::fs::read_to_string(m).ok().as_deref()
                    == Some(clone.to_string_lossy().as_ref())
                && sid_is_live(&other, &cx.session.sessions_dir)
        })?;
    cx.block("live-claim", clone);
    Some(Answer::Refuse(format!(
        "BLOCKED: {} is already occupied by another live session ({}) - two sessions must not share a working tree. Ask the GM to /rename \
one session distinctly and use its own clone.   (CLAUDE.md 'Session clones' - claim backstop)",
        clone.display(),
        base(&other)
    )))
}

/// A clean clone behind main: refused where the mirror carries a stray commit, told where a make runs, fast-forwarded where it can be.
fn behind(cx: &Ctx, clone: &Path) -> Vec<Answer> {
    let head = git(&cx.main, &["rev-parse", "HEAD"]).out;
    if head.is_empty() || git(clone, &["merge-base", "--is-ancestor", &head, "HEAD"]).ok() {
        return Vec::new();
    }
    let m = cx.main.display();
    if git(&cx.main, &["rev-parse", "--verify", "-q", "origin/main"]).ok()
        && !git(
            &cx.main,
            &["merge-base", "--is-ancestor", &head, "origin/main"],
        )
        .ok()
    {
        cx.block("stray-mirror-commit", &cx.main);
        let last = git(&cx.main, &["log", "-1", "--format=%h %s"]).out;
        return vec![Answer::Refuse(format!(
            "BLOCKED: the mirror {m} is carrying a commit GitHub main does not have ({last}), so this clone cannot be judged against it - and \
`sync-in` will NOT fix it: it fetches GitHub, finds nothing new, and reports success.\n\
That is a STRAY COMMIT in main's tree, almost always a bare `cd /diagram` that leaked into the next command (docs/session-clones.md, \
'Name the tree in the command'). Main is an integration point, never a workspace, so no session may build on it.\n\
It belongs to whoever made it. Do NOT reset it unless it is yours - the mirror's working tree may be the only copy. Find that session \
(ListAgents / SendMessage); the recovery that loses nothing is: format-patch or copy the content into THAT session's clone and commit it \
there, check `git -C {m} status --porcelain` for untracked files a reset would destroy, then `git -C {m} reset --hard origin/main`."
        ))];
    }
    let c = clone.display();
    if cx.running(clone) {
        cx.permit("behind-under-a-make", clone);
        return vec![Answer::Notice(format!(
            "clone-sync: {c} is behind main, but a make runs in it - nothing is merged under a running gate or roll (feature 385 T30); the merge \
waits until it ends. Write nothing to the tree meanwhile."
        ))];
    }
    let sync = clone.join("scripts/sync-with-main.sh");
    if sync.is_file()
        && within(
            clone,
            "scripts/sync-with-main.sh",
            &["sync-in"],
            Duration::from_secs(25),
        )
        && git(clone, &["merge-base", "--is-ancestor", &head, "HEAD"]).ok()
    {
        cx.permit("synced-in", clone);
        let _ = ask(
            Path::new("/"),
            &cx.tree
                .join("scripts/reviews/layout_carry.sh")
                .to_string_lossy(),
            &[&clone.to_string_lossy()],
            "",
        );
        return vec![Answer::Notice(format!(
            "clone-sync: {c} was a clean clone BEHIND main (main moved during this turn), so main was merged in - a fast-forward - before this \
edit; it proceeds on the current base. If this edit fails as stale, the merge changed the file: re-read it and retry. (feature 212; \
CLAUDE.md, Session clones / sync-in rule)"
        ))];
    }
    cx.block("stale-head", clone);
    vec![Answer::Refuse(format!(
        "BLOCKED: {c} has a clean tree (a new work unit) but its HEAD is behind main - new work must not build on a stale base, and the \
automatic sync-in could not fast-forward it (a diverged clone, or the merge failed). Run: cd {c} && scripts/sync-with-main.sh sync-in   \
(CLAUDE.md 'Session clones' / sync-in rule)"
    ))]
}

/// A tool's output with the lines `sync-with-main.sh` marks as worth reading kept.
fn notes(out: &str) -> Vec<String> {
    out.lines()
        .filter(|l| {
            l.starts_with("sync-with-main: NOTE") || l.starts_with("sync-with-main: WARNING")
        })
        .map(str::to_owned)
        .collect()
}

/// The last `n` lines of `out`, as `tail -n` gives them.
fn tail(out: &str, n: usize) -> String {
    let lines: Vec<&str> = out.lines().collect();
    lines[lines.len().saturating_sub(n)..].join("\n")
}

/// The lines the prompt mode says: the unnamed-session notice, the tracked-pointer notice, and the sync's outcome.
fn prompt(cx: &Ctx) -> Vec<String> {
    let sid = cx.input("session_id");
    if sid.is_empty() {
        return Vec::new();
    }
    let map = cx.mapdir().join(sid);
    let Ok(claimed) = std::fs::read_to_string(&map) else {
        return unnamed(cx, sid);
    };
    let clone = PathBuf::from(claimed);
    if !clone.join(".git").is_dir() {
        return Vec::new();
    }
    let mut lines = Vec::new();
    let _ = ask(
        Path::new("/"),
        cx.python,
        &[
            &cx.tree
                .join("scripts/hooks/lib/clone_local_settings.py")
                .to_string_lossy(),
            &clone.to_string_lossy(),
        ],
        "",
    );
    let notice = cx.mapdir().join(format!("{sid}.feature-json-notice"));
    if git(
        &clone,
        &["ls-files", "--error-unmatch", ".specify/feature.json"],
    )
    .ok()
        && !notice.exists()
    {
        let _ = std::fs::write(&notice, "");
        lines.push(format!(
            "clone-sync: .specify/feature.json is TRACKED again in {c} - it must stay gitignored. It OUTRANKS SPECIFY_FEATURE when spec-kit \
resolves FEATURE_DIR, so a peer session's copy silently redirects your spec-kit writes into THEIR specs/NNN-*/. Fix: cd {c} && git rm \
--cached .specify/feature.json && git commit -m 'chore: untrack spec-kit active-feature pointer'   (docs/session-clones.md 'Concurrent \
sessions')",
            c = clone.display()
        ));
    }
    if ask(
        Path::new("/"),
        cx.python,
        &[&cx.tree.join("scripts/hooks/lib/solo.py").to_string_lossy()],
        "",
    )
    .ok()
    {
        return lines;
    }
    lines.extend(sync(cx, &clone));
    lines
}

/// The notice for a session whose name gives no clone, said once a session.
fn unnamed(cx: &Ctx, sid: &str) -> Vec<String> {
    let notice = cx.mapdir().join(format!("{sid}.name-notice"));
    if notice.exists() {
        return Vec::new();
    }
    let _ = std::fs::create_dir_all(cx.mapdir());
    let _ = std::fs::write(&notice, "");
    match cx.session.canonical() {
        None => vec![format!(
            "clone-sync: this session's name does not resolve (no /rename record in its transcript and no entry for it under {}), so it has NO \
valid clone name. Read-only work is fine. If you are going to modify this repo, ask the GM to /rename the session NOW - before the recon, \
not after it.",
            cx.session.sessions_dir.display()
        )],
        Some(c) if forbidden(&c, &cx.main) => vec![format!(
            "clone-sync: this session resolves to the FORBIDDEN '.clones/{}' (unnamed, auto-derived, or named after a repository). Read-only \
work is fine. If you are going to modify this repo, ask the GM to /rename the session NOW - before the recon, not after it.",
            c.file_name().map(|n| n.to_string_lossy().into_owned()).unwrap_or_default()
        )],
        Some(_) => Vec::new(),
    }
}

/// The prompt's sync: mid-task only the mirror is refreshed; else the clone is synced with main.
fn sync(cx: &Ctx, clone: &Path) -> Vec<String> {
    let c = clone.display();
    let midtask = if dirty(clone) {
        "has uncommitted work (mid-task)"
    } else if ask(
        clone,
        &cx.tree
            .join("scripts/hooks/lib/own-make.sh")
            .to_string_lossy(),
        &[""],
        "",
    )
    .ok()
    {
        "has a make run going (a gate or a roll)"
    } else if cx.running(clone) {
        "holds a running gate's lock"
    } else {
        ""
    };
    let script = "scripts/sync-with-main.sh";
    if !midtask.is_empty() {
        return refresh_mirror(cx, clone, midtask);
    }
    let out = ask(clone, script, &["sync-in", "--background-render"], "");
    let text = both(&out);
    if !out.ok() {
        return vec![format!(
            "clone-sync: auto sync-in FAILED in {c} - resolve before modifying the repo: {}",
            tail(&text, 2)
        )];
    }
    let mut lines = vec![format!("clone-sync: auto-synced {c} with main (git)")];
    let root = clone.to_string_lossy();
    let usage = cx.tree.join("scripts/hooks/lib/usage_log.py");
    let _ = ask(
        Path::new("/"),
        cx.python,
        &[
            &usage.to_string_lossy(),
            "record",
            "--root",
            &root,
            "--tool",
            "clone-sync-merge",
            "--kind",
            "step",
            "--outcome",
            "changed",
        ],
        "",
    );
    let carried = ask(
        Path::new("/"),
        &cx.tree
            .join("scripts/reviews/layout_carry.sh")
            .to_string_lossy(),
        &[&root],
        "",
    );
    lines.extend(
        [carried.out, carried.err]
            .into_iter()
            .filter(|s| !s.is_empty()),
    );
    lines.extend(notes(&text));
    lines
}

/// A tool's stdout and stderr together, as `2>&1` caught them.
fn both(out: &Said) -> String {
    [out.out.as_str(), out.err.as_str()]
        .iter()
        .filter(|s| !s.is_empty())
        .copied()
        .collect::<Vec<_>>()
        .join("\n")
}

/// Mid-task: the clone is left alone and only the mirror refreshed.
fn refresh_mirror(cx: &Ctx, clone: &Path, midtask: &str) -> Vec<String> {
    let c = clone.display();
    let out = ask(
        clone,
        "scripts/sync-with-main.sh",
        &["sync-in", "--mirror-only", "--background-render"],
        "",
    );
    let text = both(&out);
    if !out.ok() {
        return vec![format!(
            "clone-sync: {c} {midtask} - clone merge skipped; mirror refresh FAILED: {}",
            tail(&text, 1)
        )];
    }
    let mut lines = vec![format!("clone-sync: {c} {midtask} - clone merge skipped; mirror refreshed from GitHub main. Finish and run sync-with-main.sh done")];
    if git(
        clone,
        &[
            "ls-files",
            "--error-unmatch",
            ".claude/skills/diagram/Makefile",
        ],
    )
    .ok()
        && cx.tree.join("scripts/l7r/diagram/__init__.py").is_file()
    {
        lines.push("clone-sync: main moved the project to the repository root (feature 329) - this clone is still on the old layout. Commit, then sync in: the merge carries your edits to the new paths.".to_owned());
    }
    lines.extend(notes(&text));
    lines
}

#[cfg(test)]
mod tests;
