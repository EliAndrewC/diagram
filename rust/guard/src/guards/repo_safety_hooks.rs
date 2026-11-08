//! `repo-safety-hooks` (ported from the shell of the same name, feature 449 T034): THE GIT OPERATIONS THIS PROJECT SAYS MUST NEVER HAPPEN. A force
//! push, which loses somebody else's work; a history rewrite (the GM 2026-08-25, constitution VI), which throws a paid verification away; a git write
//! against `/host-l7r-repo`, the GM's own repository (file edits there are deliberately not blocked). The first two have no escape: "never" stops
//! meaning never the moment one exists. The mount guard takes `HOST_GIT_OK` with a reason, because a read-only operation misdetected as a write
//! should not strand a session. Heredoc bodies and quoted strings are payload, never commands.

use std::sync::LazyLock;

use fancy_regex::Regex;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::shape::strip_heredocs;
use crate::shared::state::field;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "repo-safety-hooks",
    events: &["PreToolUse"],
    matcher: "Bash",
    decide,
};

// Feature 178: the prefix group consumes the quoted placeholder, the only place it can legitimately stand before a command - `FOO="bar" git push
// --force` otherwise walked past the anchor.
const POS: &str =
    r"(?:^|[\n;|]|&&|\|\|)\s*(?:timeout\s+\S+\s+|env\s+|QUOTED\s+|[A-Za-z_][A-Za-z0-9_]*=\S*\s+)*";
const HOST: &str = "/host-l7r-repo";
const WRITES: &str = r"\b(?:commit|push|add|rm|mv|reset|revert|checkout|switch|restore|merge|rebase|cherry-pick|clean|stash|tag|am|apply)\b";

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

fn at_pos(tail: &str) -> Regex {
    re(&format!("{POS}{tail}"))
}

static QUOTED: LazyLock<Regex> = LazyLock::new(|| re(r#"'[^']*'|"[^"]*""#));
static FORCE: LazyLock<[Regex; 2]> = LazyLock::new(|| {
    [
        at_pos(r"git\b[^\n;|&]*\bpush\b[^\n;|&]*(?:--force(?:-with-lease)?|(?<![\w-])-f(?![\w-]))"),
        at_pos(r"git\b[^\n;|&]*(?:--force(?:-with-lease)?)[^\n;|&]*\bpush\b"),
    ]
});
static REWRITE: LazyLock<[Regex; 4]> = LazyLock::new(|| {
    [
        at_pos(r"git\b(?:\s+-C\s+\S+|\s+-\S+)*\s+rebase\b"),
        at_pos(r"git\b[^\n;|&]*\bpull\b[^\n;|&]*(?<![\w-])--rebase\b"),
        at_pos(r"git\b[^\n;|&]*\bmerge\b[^\n;|&]*--squash"),
        at_pos(r"git\b[^\n;|&]*\bcommit\b[^\n;|&]*--amend"),
    ]
});
static MOUNT: LazyLock<[Regex; 2]> = LazyLock::new(|| {
    [
        at_pos(&format!(r"git\b[^\n;|&]*-C\s+{HOST}\S*[^\n;|&]*{WRITES}")),
        re(&format!(r"cd\s+{HOST}\S*[^\n]*?\bgit\b[^\n;|&]*{WRITES}")),
    ]
});

/// The command with its payload blanked: heredoc bodies, then quoted strings.
fn sanitized(cmd: &str) -> String {
    let body = strip_heredocs(cmd);
    let (mut out, mut from) = (String::new(), 0);
    for m in QUOTED.find_iter(&body).flatten() {
        out.push_str(&body[from..m.start()]);
        out.push_str(" QUOTED ");
        from = m.end();
    }
    out + &body[from..]
}

fn any(patterns: &[Regex], text: &str) -> bool {
    patterns.iter().any(|r| r.is_match(text).unwrap_or(false))
}

/// The rule the command breaks, or None; the mount rule only where the escape has not spoken.
pub(crate) fn verdict(cmd: &str, escaped: bool) -> Option<&'static str> {
    let c = sanitized(cmd);
    if any(&*FORCE, &c) {
        return Some("force-push");
    }
    if any(&*REWRITE, &c) {
        return Some("history-rewrite");
    }
    (!escaped && any(&*MOUNT, &c)).then_some("host-git-write")
}

const FORCE_PUSH: &str = "BLOCKED: git push --force.

CLAUDE.md calls this \"the one thing that overwrites other sessions' work\", and that is literal. The
GM runs several sessions at once, each in its own clone, all pushing to one main. A force push does
not lose YOUR work - it loses SOMEBODY ELSE'S, silently, and the person who discovers it is not the
person who did it.

There is no legitimate force push in this workflow. What you want instead:

  scripts/sync-with-main.sh done     locked pull-then-push, then render-sync
  git pull origin main               if the push was rejected, MERGE and push again

If a push is being refused and merging looks wrong, that is worth raising with the GM rather than
overwriting. There is deliberately no escape hatch here: \"never\" stops meaning never the moment one
exists.

(rust/guard/src/guards/repo_safety_hooks.rs; CLAUDE.md session-clone workflow)";

const HISTORY: &str =
    "BLOCKED: a history rewrite (rebase, pull --rebase, merge --squash, or commit --amend).

This project never rewrites history (GM 2026-08-25, constitution VI): every landing is a real merge
commit with its parents intact. The history is the record of decisions, and the verified-tree
records, the perf-review records and the performance bookends are keyed by the commits and content
that were actually tested - a rewrite would throw a paid verification away without saying so.

What to do instead:
  - to bring main in:   scripts/sync-with-main.sh sync-in   (a merge, never a rebase)
  - to fix a commit:    make another commit that fixes it
  - to combine work:    a merge commit (git merge --no-edit <ref>)

No escape hatch: \"never\" stops meaning never the moment one exists.";

const HOST_WRITE: &str = "BLOCKED: a git write against /host-l7r-repo.

That is the GM's own repo, bind-mounted from their laptop. CLAUDE.md: \"From inside the container,
never run `git commit` or `git push` against the mount.\" They do their own git there - a commit made
from here appears on their machine as work they did not do.

What IS allowed, and is not blocked:

  - EDITING files there. The Note Intake Workflow exists to append to setting/l7r.md.
  - READ-ONLY git: `git -C /host-l7r-repo log`, `diff`, `show`, `status`.

If a read-only command was misread as a write, put HOST_GIT_OK in it with a note - and say what it
false-positived on, because that is a bug in this hook.

(rust/guard/src/guards/repo_safety_hooks.rs; CLAUDE.md \"Session clones\")";

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let cmd = event
        .input
        .get("tool_input")
        .map_or("", |t| field(t, "command"));
    let shown: String = cmd.chars().take(200).collect();
    let escaped = match escape_or_refuse(cmd, "HOST_GIT_OK") {
        Escape::Escaped(why) => {
            log::fire(
                "repo-safety",
                "escaped",
                &why,
                "host-git-ok",
                &event.input,
                session,
            );
            true
        }
        Escape::Refused(text) => {
            log::fire(
                "repo-safety",
                "blocked",
                &shown,
                "HOST_GIT_OK-no-reason",
                &event.input,
                session,
            );
            return vec![Answer::Refuse(text)];
        }
        Escape::None => false,
    };
    let Some(rule) = verdict(cmd, escaped) else {
        return Vec::new();
    };
    log::fire(
        "repo-safety",
        "blocked",
        &shown,
        rule,
        &event.input,
        session,
    );
    let text = match rule {
        "force-push" => FORCE_PUSH,
        "history-rewrite" => HISTORY,
        _ => HOST_WRITE,
    };
    vec![Answer::Refuse(text.to_owned())]
}

#[cfg(test)]
mod tests;
