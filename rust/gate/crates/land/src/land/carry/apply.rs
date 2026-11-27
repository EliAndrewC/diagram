//! The carry's NO-COMMIT form (feature 461 T05, plan D3): a commit applied onto the tree's HEAD with the carry's rules and left
//! uncommitted - `git cherry-pick -n`, never `git rebase` - so `make builder-done`'s hand-in (461 T07) can apply a builder's scratch
//! commit onto the base, run the landing's first pass over the tree as it then stands, and commit it there itself.
//!
//! WHY ITS OWN END (D3, "the no-commit form's own verified end"): the carry's end ([`super::end`]) asks "nothing staged", which a
//! no-commit apply contradicts by design - every path it applied stands staged. Probed 2026-11-27 (method: `git cherry-pick -n` in
//! scratch repositories, git 2.x of the container): a `-n` pick writes no `CHERRY_PICK_HEAD` and no `sequencer/`, on a conflict as on a
//! clean apply, so nothing stands to `--continue` or `--skip`, and an empty pick (every change already in HEAD) exits 0 with nothing
//! staged. So this form ends verified on: nothing in progress (no pick, merge, revert, sequence or rebase standing), nothing unmerged,
//! and each non-spec file of the applied commit present in the WORKING TREE - changed there against HEAD, or already holding the
//! commit's content (a file the commit deletes is present as absent; a file a rule resolved is held whatever its text, as in the
//! carry). HEAD never moves here, so the base the check compares against is HEAD.
//!
//! What it shares with the carry: the refusal of unfinished work first ([`refusals`]), and the conflict rules whole
//! ([`super::resolve_all`]), the cleanly merged tasks.md's boxes restored from the applied commit (the carry reads it as
//! `CHERRY_PICK_HEAD`, which a `-n` pick never writes - so both forms now name the sha). What it does not: `--continue`, the empty
//! pick's `--skip`, the done ref's deletion ([`super::spent`]: nothing is carried into a commit here, and a hand-in's scratch commit is
//! under `refs/l7r/hand-in/`, a successor's earlier half under a done ref its own hand-in supersedes, D14).
//!
//! A conflict no rule resolves is LEFT IN THE TREE, its paths unmerged (nothing of it resolved), and named: the builder resolves them,
//! `git add`s them, and the hand-in resumes at its first pass, asking [`verified`] again (D3 step 3).

use std::path::Path;

use super::super::unfinished::{git, lines, refusals};
use super::{resolve_all, Form, Said, NO_DRIVER};

/// What a no-commit apply came to.
#[derive(Debug, PartialEq, Eq)]
pub(crate) enum Applied {
    /// Applied and verified: its non-spec files' count, and each file a rule resolved with the rule's name.
    Verified { files: usize, resolved: Vec<String> },
    /// Stopped on a conflict no rule resolves, the tree left with it: each path with why it stops.
    Conflict(Vec<String>),
    /// Refused before anything was applied: why (unfinished work in the tree, no such commit, a pick that did not start).
    Refused(String),
    /// Applied, but its end did not verify: what failed, and each file a rule resolved with the rule's name - kept, since a resume
    /// asks the end again and only this list tells a file a rule resolved back to the base's own text from one missing (461 T39).
    NotVerified {
        fails: Vec<String>,
        resolved: Vec<String>,
    },
}

/// The no-commit form's verified end, asked on its own too (a hand-in resumed after a hand resolution): the commit's non-spec file
/// count, or what fails - something in progress, a path unmerged, a non-spec file of `sha` the working tree does not hold.
pub(crate) fn verified(
    root: &Path,
    sha: &str,
    kept: &[String],
) -> Result<Result<usize, Vec<String>>, String> {
    // the staged paths are the apply's own: only what stands in progress, and what is unmerged, fails it - the unmerged in this
    // form's words, since the carry's say "and commit", which would move HEAD off the base the caller commits onto (the refusals'
    // words are `unfinished::refusals`' own, asserted by this form's tests)
    let mut every: Vec<String> = refusals(root)?
        .into_iter()
        .filter(|r| {
            ![
                " staged path(s) stand uncommitted in ",
                " path(s) unmerged in ",
            ]
            .iter()
            .any(|w| r.contains(w))
        })
        .collect();
    let unmerged = lines(&git(root, &["diff", "--name-only", "--diff-filter=U"])?.1);
    if !unmerged.is_empty() {
        let (tree, names) = (root.display(), unmerged.join(" "));
        every.push(format!("{} path(s) unmerged in {tree} ({names}) - resolve each and `git -C {tree} add -- {names}`, committing nothing: the no-commit form's caller commits", unmerged.len()));
    }
    let (count, lacks) = super::missing(root, sha, "HEAD", kept, Form::NoCommit)?;
    if !lacks.is_empty() {
        every.push(format!(
            "the working tree does not hold the applied commit's {}",
            lacks.join(", ")
        ));
    }
    Ok(if every.is_empty() {
        Ok(count)
    } else {
        Err(every)
    })
}

/// `sha` applied onto `root`'s HEAD without committing, with the carry's rules, and its end verified.
pub(crate) fn apply(root: &Path, sha: &str) -> Result<Applied, String> {
    let stops = refusals(root)?;
    if !stops.is_empty() {
        return Ok(Applied::Refused(format!(
            "{} holds unfinished work: {}",
            root.display(),
            stops.join("; ")
        )));
    }
    let (rc, out) = git(
        root,
        &["rev-parse", "-q", "--verify", &format!("{sha}^{{commit}}")],
    )?;
    if rc != 0 {
        return Ok(Applied::Refused(format!(
            "{} holds no commit {sha}",
            root.display()
        )));
    }
    let sha = out.trim().to_owned();
    let (rc, out) = git(root, &["-c", NO_DRIVER, "cherry-pick", "-n", &sha])?;
    let mut kept = Vec::new();
    if rc != 0 {
        let unmerged = lines(&git(root, &["diff", "--name-only", "--diff-filter=U"])?.1);
        if unmerged.is_empty() {
            return Ok(Applied::Refused(format!(
                "git cherry-pick -n said: {}",
                lines(&out).join(" | ")
            )));
        }
        match resolve_all(root, &unmerged, &sha, Form::NoCommit)? {
            Err(stops) => return Ok(Applied::Conflict(left(&unmerged, &stops))),
            Ok(paths) => kept = paths,
        }
    }
    Ok(ended(verified(root, &sha, &kept)?, kept))
}

/// Every path a stopped apply leaves unmerged, each with why: the rules resolve all of a pick's conflicts or none, so a path its rule
/// would resolve is left with the rest, and said so.
fn left(unmerged: &[String], stops: &[String]) -> Vec<String> {
    let why = |path: &String| {
        let own = stops.iter().find(|s| s.starts_with(&format!("{path} (")));
        own.cloned()
            .unwrap_or_else(|| format!("{path} (its rule would resolve it; left with the rest)"))
    };
    unmerged.iter().map(why).collect()
}

/// An apply's verified end as what it came to.
pub(crate) fn ended(end: Result<usize, Vec<String>>, resolved: Vec<String>) -> Applied {
    match end {
        Ok(files) => Applied::Verified { files, resolved },
        Err(fails) => Applied::NotVerified { fails, resolved },
    }
}

/// `l7r-gate land --carry --no-commit <tree> [<commit>]`: `commit` of `from` applied onto `root` and said; its exit.
pub(super) fn cli(root: &Path, from: &Path, commit: &str, said: &mut Said) -> Result<i32, String> {
    let Some(sha) = super::located(root, from, commit, said)? else {
        return Ok(2);
    };
    let applied = apply(root, &sha)?;
    Ok(told(root, &sha, &applied, said))
}

/// The words for what [`apply`] came to, and its exit: 0 applied and verified, 2 refused or stopped (a stop leaves the conflict in
/// the tree), 1 the end's verification failed - the carry's exits.
pub(super) fn told(root: &Path, commit: &str, applied: &Applied, said: &mut Said) -> i32 {
    let tree = root.display();
    let short: String = commit.chars().take(10).collect();
    match applied {
        Applied::Verified { files, resolved } => {
            let both = if resolved.is_empty() {
                String::new()
            } else {
                format!("; resolved {}", resolved.join(", "))
            };
            said.say(&format!("carry: {short} applied onto {tree}'s HEAD, uncommitted (the no-commit form) - verified: nothing in progress, nothing unmerged, its {files} non-spec file(s) in the working tree{both}\n"));
            0
        }
        Applied::Conflict(stops) => {
            said.warn(&format!("carry: STOPPED - {short} is applied onto {tree} uncommitted, with a conflict this command does not resolve - nothing was resolved, every path left unmerged: {} - resolve each, `git -C {tree} add -- <path>`, and nothing to continue or commit (the no-commit form's caller commits)\n", stops.join(", ")));
            2
        }
        Applied::Refused(why) => {
            said.warn(&format!("carry: refused - nothing applied: {why}\n"));
            2
        }
        Applied::NotVerified { fails, .. } => {
            said.warn(&format!(
                "carry: NOT VERIFIED - {short} applied onto {tree} uncommitted:\n  {}\n",
                fails.join("\n  ")
            ));
            1
        }
    }
}
