//! `repo_safety_hooks`'s cases. The cases moved here from `tests/hooks/test_hooks_cases.py` (feature 449 T050), each one's history kept above it.
//!
//! TWO DIRECTIONS FOR EVERY GUARD: each table carries the cases it must FIRE on and the cases it must stay QUIET on, and the quiet half is deliberately the longer one. Every false
//! positive this project has paid for is in these tables as a regression case. **A mention is not an invocation.**

use super::{cmd, Case};

#[expect(
    clippy::too_many_lines,
    reason = "a table of cases, each with its history above it"
)]
pub(super) fn cases() -> Vec<Case> {
    vec![
        (
            "force push, long flag",
            cmd("git push --force origin main"),
            "blocked",
        ),
        ("force push, short flag", cmd("git push -f"), "blocked"),
        (
            "force push, with-lease",
            cmd("git push --force-with-lease origin HEAD:main"),
            "blocked",
        ),
        (
            "flag before the verb",
            cmd("git --force push origin main"),
            "blocked",
        ),
        (
            "an ordinary push",
            cmd("git -C /gm-assistant/.clones/x push origin HEAD:main"),
            "ok",
        ),
        (
            "the stop-work procedure",
            cmd("./scripts/sync-with-main.sh done"),
            "ok",
        ),
        // feature 321 FR-005: the remote-only backup branch, its push and its delete
        (
            "the backup push",
            cmd("git -C /diagram/.clones/x push origin HEAD:refs/heads/backup/x"),
            "ok",
        ),
        (
            "the backup delete",
            cmd("git -C /diagram/.clones/x push origin --delete backup/x"),
            "ok",
        ),
        (
            "the backup delete, refspec form",
            cmd("git -C /diagram/.clones/x push origin :refs/heads/backup/x"),
            "ok",
        ),
        // the seventh mention-versus-invocation case: a message ABOUT the rule
        (
            "a commit message quoting the rule",
            cmd("git commit -m \"never git push --force here\""),
            "ok",
        ),
        (
            "a heredoc message quoting it",
            cmd("git commit -F - <<MSG\nblocks git push --force\nMSG"),
            "ok",
        ),
        // history is never rewritten (GM 2026-08-25, constitution VI)
        ("a rebase", cmd("git rebase origin/main"), "blocked"),
        (
            "a pull with --rebase",
            cmd("git -C /diagram/.clones/x pull --rebase origin main"),
            "blocked",
        ),
        (
            "a squash merge",
            cmd("git merge --squash session/other"),
            "blocked",
        ),
        ("an amend", cmd("git commit --amend --no-edit"), "blocked"),
        (
            "an ordinary merge",
            cmd("git merge --no-edit origin/main"),
            "ok",
        ),
        (
            "the procedure's pull",
            cmd("git pull --no-rebase origin main"),
            "ok",
        ),
        (
            "a commit message mentioning rebase",
            cmd("git commit -m \"no rebase or squash here\""),
            "ok",
        ),
        (
            "git write to the GM repo",
            cmd("git -C /host-l7r-repo commit -m x"),
            "blocked",
        ),
        (
            "git add to the GM repo",
            cmd("cd /host-l7r-repo && git add setting/l7r.md"),
            "blocked",
        ),
        // read-only git there is explicitly ALLOWED by CLAUDE.md
        (
            "git log on the GM repo",
            cmd("git -C /host-l7r-repo log --oneline -5"),
            "ok",
        ),
        (
            "git diff on the GM repo",
            cmd("git -C /host-l7r-repo diff"),
            "ok",
        ),
        (
            "the documented escape",
            cmd("git -C /host-l7r-repo status  # HOST_GIT_OK: read-only"),
            "ok",
        ),
        // FEATURE 178 - A REAL BYPASS OF THIS GUARD, closed. Quoted strings are blanked because they are
        // PAYLOAD, and they were replaced by the literal word ` QUOTED `; an assignment whose value was
        // quoted therefore became `FOO= QUOTED  git push ...`, and that inserted word broke the
        // command-position anchor. The most absolute guard here - the one whose header says it has no
        // escape hatch on purpose - could be walked past by putting quotes round an environment variable.
        // Demonstrated before the fix: FOO=bar blocked, FOO="bar" ALLOWED.
        (
            "force push behind a QUOTED assignment",
            cmd("FOO=\"bar\" git push --force origin main"),
            "blocked",
        ),
        (
            "force push behind a quoted *_OK name",
            cmd("GATE_OK=\"a reason\" git push --force origin main"),
            "blocked",
        ),
        (
            "rebase behind a quoted assignment",
            cmd("FOO=\"bar\" git rebase -i main"),
            "blocked",
        ),
        (
            "host git write behind a quoted assignment",
            cmd("FOO=\"bar\" git -C /host-l7r-repo commit -am x"),
            "blocked",
        ),
        // ...and the unquoted form, which always worked, still does - the fix widened nothing else
        (
            "force push behind a plain assignment",
            cmd("FOO=bar git push --force origin main"),
            "blocked",
        ),
    ]
}
