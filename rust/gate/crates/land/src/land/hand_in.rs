//! `l7r-gate land --hand-in <tasks> <feature>` (feature 461 T07, plan D3): a builder's end that lands its work on WHERE WORK LANDS,
//! not on the base its tree was handed out at - so the conflicts with work landed since, and the bookkeeping the landing's first pass
//! asks (T08), are the builder's to answer in its own tree, where they cost the coordinating session a turn each before (the night of
//! 2026-11-26/27: 19 of 50 landings refused before a gate, 15 carry conflicts, spec "Why").
//!
//! In the builder's pool tree, as `make builder-done` finds it (`l7r_gate_task::builder_done::found`; `MSG` and `GUARD` from the
//! environment):
//!
//! 1. today's refusals are asked (`Found::unready`: an unfinished operation, an unmerged path, a conflict's markers, nothing to
//!    commit, a guard file with no `GUARD=`, the task's earlier done commit not yet carried
//!    and not built on by the tree's handout, 461 T09), nothing done on any;
//! 2. the base is found FIRST - `HAND_IN_BASE` (a GUESS knob, `dev/audits/hand-in-base.md`): `clone` (the default, phase 1) the
//!    clone's HEAD, `origin` (phase 2) `origin/main` after `git fetch origin` - so a fetch that fails refuses with nothing done (the
//!    plan's step 3 fetches after the scratch commit; fetching first changes nothing else and leaves no scratch commit to undo). The
//!    fetch is asked only for `origin`: in phase 1 nothing reads `origin/main`, and the clone's HEAD is in the shared object store;
//! 3. the work is committed as a SCRATCH commit on the tree's HEAD, kept at `refs/l7r/hand-in/<feature>-<task>` (one ref a task, as
//!    the done refs), the base's sha written to `<the tree's git dir>/l7r-hand-in/<feature>-<first task>.base`;
//! 4. the tree is detached at the base and the scratch commit applied with T05's no-commit carry (`carry::apply`, the carry's rules
//!    whole). Each outcome:
//!    - verified: the rules' resolved list written beside the base file (`.resolved`, one `path (rule)` line each) and on to step 5;
//!    - a conflict no rule resolves: the tree LEFT with it, every path named, those a rule resolves marked so; the builder resolves
//!      the others, `git add`s them and runs `make builder-done` again;
//!    - refused before anything was applied, or a git step past the scratch commit failing (a scratch ref refused): the tree put
//!      back - at the scratch commit's content, HEAD at its old base, the work uncommitted - and the scratch ref deleted, so
//!      nothing is done;
//!    - applied and not verified: said, the rules' resolved list written as a verified apply's is (461 T39: the resume asks the
//!      end again, and only the list tells a file a rule resolved back to the base's text from one missing), the tree left so, the
//!      next run resuming;
//! 5. (the RESUME, where the scratch ref stands) the paths still unmerged go through the carry's rules (`resolve_all`: after a
//!    conflict nothing was resolved, all or none, so a path its rule resolves is resolved here, never by hand), what they resolve is
//!    added to the `.resolved` list, and the no-commit form's end (`verified`) is asked again with that list as `kept` - the list is
//!    what tells a file a rule resolved back to the base's own text from one missing (T05). The tree's HEAD is the base: a resume
//!    never reads the clone's HEAD again, which may have moved since the stop. A scratch ref with no base file in this tree, or a
//!    tree no longer at that base, is another tree's or a stale one, refused with its `git update-ref -d`, never resumed;
//! 6. everything staged, a conflict's markers in a staged file refused; the first pass - T06's hand-in mode ([`Pass::HandIn`], D4),
//!    wired in at [`FirstPass`] by 461 T08 ([`first_pass`]): a landing rooted at the tree, asked with the tree detached at the base,
//!    HEAD the base, the work applied, the commit's subject its note - asked, a refusal printing every reason with its fixing command
//!    and committing nothing - the next run resumes at step 5. The tree's builder's kind, from its brief's line of the pool's log
//!    (`Found::kind`, 461 T44), says what the plan section owes: a build half's and a measurement's asks of it are put off
//!    ([`section_of`]), a measurement's record under `dev/measurements/` asked in their place;
//! 7. EVERYTHING staged again (`git add -A`: the verified end reads the working tree, not the index, T05; and the records a clear
//!    first pass writes into the tree go into the commit with the work, D4) and committed with the scratch
//!    commit's message (`git commit -C`), its parent the base; a base already holding every change hands nothing in, said with the
//!    release to run, the scratch ref deleted;
//! 8. the commit kept as `make builder-done` keeps one (`Found::kept`: the done ref, the `done` line with `"handed_in": true`, the
//!    tree released, the next dispatch printed and `handed in to the lane (make lane for its place)` where `make land`'s line stood,
//!    461 T08), then the scratch refs and this tree's hand-in files deleted.
//!
//! No history is rewritten: the scratch commit is never moved or amended, only left unreferenced once its work is committed again
//! on the base.

use std::path::{Path, PathBuf};

use l7r_gate_core::Reply;
use l7r_gate_task::builder_done::{self, Found};
use l7r_gate_task::tick::Section;
use l7r_shared::guards::conflict_marker_hooks::has_conflict;

use super::carry::apply::{apply, ended, verified, Applied};
use super::carry::{resolve_all, Form};
use super::unfinished::{git, git_dir, lines};
use super::{Land, Pass};

/// Where a hand-in's scratch commit is kept while it stands (data-model.md, "Refs").
const REFS: &str = "refs/l7r/hand-in/";
/// The directory of the tree's own git directory holding a standing hand-in's base and its rules' resolved list.
const FILES: &str = "l7r-hand-in";

/// What the first pass is asked over (D3 step 4): the tree as applied, the base it stands detached at, the feature and every task of
/// the hand-in, and the note its tick check is asked with - the commit's subject, since a hand-in takes no `NOTE=` (the tick check reads
/// a note only to refuse an empty one and, at `landed=true`, never asked here, a "landed" one).
pub(super) struct Asked<'a> {
    pub tree: &'a Path,
    pub base: &'a str,
    pub feature: &'a str,
    pub tasks: &'a [String],
    pub note: &'a str,
    /// The kind the tree's builder was briefed as (`Found::kind`, 461 T44), "" where no brief names one.
    pub kind: &'a str,
}

/// Where the record a measurement hands in stands (`builder_brief.rs`'s measurement STOP POINT).
const RECORDS: &str = "dev/measurements/";

/// WHAT A BUILDER'S KIND OWES OF ITS PLAN SECTION AT HAND-IN (461 T44): a build half's section is its closing half's to write, and a
/// measurement writes none, so both hand in with the section's asks put off ([`Section::Later`]); a fix, a closing half and a tree
/// no brief names owe it, as a landing does. The kind is read from the pool's log, written by `make builder-brief`, never named by
/// the builder.
pub(super) fn section_of(kind: &str) -> Section {
    match kind {
        "build-half" | "measurement" => Section::Later,
        _ => Section::Owed,
    }
}

/// A MEASUREMENT'S RECORD STANDS IN FOR ITS SECTION (461 T44, a decision: the algorithmically easier stand-in, a file present, its
/// content the reviewers'): a measurement's hand-in whose work, staged against `base`, holds nothing under [`RECORDS`] is refused.
fn record_refusal(asked: &Asked) -> Option<String> {
    if asked.kind != "measurement" {
        return None;
    }
    let staged = match must(
        asked.tree,
        &["diff", "--cached", "--name-only", asked.base, "--"],
    ) {
        Ok(staged) => staged,
        Err(why) => {
            return Some(format!(
                "a measurement's record could not be looked for: {why}"
            ))
        }
    };
    if staged.lines().any(|p| p.starts_with(RECORDS)) {
        return None;
    }
    Some(format!("a measurement hands in its record, which stands in for its plan section, and the work holds nothing under {RECORDS} - write the record (its commands, figures and units) at {RECORDS}<date>/<topic>/results.md in {}, then run make builder-done again", asked.tree.display()))
}

/// The first pass's seam (D3 step 4): each reason it refuses the applied tree, with its fixing command.
pub(super) type FirstPass<'a> = &'a dyn Fn(&Asked) -> Vec<String>;

/// `l7r-gate land --hand-in <tasks> <feature>`, `MSG`, `GUARD` and `HAND_IN_BASE` from the environment; the first pass T06's hand-in
/// mode (461 T08).
pub(super) fn cli(args: &[String], cwd: &Path) -> Reply {
    let var = |n: &str| std::env::var(n).unwrap_or_default();
    let (msg, guard, knob) = (var("MSG"), var("GUARD"), var("HAND_IN_BASE"));
    run(args, cwd, &msg, &guard, &knob, &first_pass)
}

/// The first pass at hand-in as the process asks it: a landing rooted at the builder's tree - never at `cwd`, since the registry
/// finds the tree and `make builder-done` may be run from the clone - its tools where a landing's are.
pub(super) fn first_pass(asked: &Asked) -> Vec<String> {
    pass(
        &Land::new(asked.tree, &super::scripts_of(asked.tree)),
        asked,
    )
}

/// T06's hand-in mode ([`Pass::HandIn`], D4) asked of `land` over the applied tree: each reason with its fixing command. A pass that
/// cannot be asked - no spec directory for the feature in the tree, or a raise - is a reason too, never a clear. No `deferred` list: an
/// owed claim with a round in flight is quiet, the landing's to wait on (phase 1 has no lane to hand it to).
pub(super) fn pass(land: &Land, asked: &Asked) -> Vec<String> {
    let found = l7r_gate_task::tick::spec_dir(asked.tree, asked.feature)
        .filter(|d| d.join("tasks.md").is_file());
    let Some(d) = found else {
        return vec![format!("no single specs/{}* directory with a tasks.md in {} - the first pass cannot be asked; name the feature as F= names it (make builder-done T={} F=<feature>)", asked.feature, asked.tree.display(), asked.tasks.join(","))];
    };
    let at = Pass::HandIn {
        base: asked.base.to_owned(),
        section: section_of(asked.kind),
    };
    let mut reasons = land
        .cheap_refusals(&d, asked.tasks, asked.note, &at, None)
        .unwrap_or_else(|why| vec![format!("the first pass could not be asked: {why}")]);
    reasons.extend(record_refusal(asked));
    reasons
}

/// No first pass: nothing refused (the tests' clear pass).
#[cfg(test)]
pub(super) fn none(_: &Asked) -> Vec<String> {
    Vec::new()
}

/// A file step's error as the hand-in says it, mapped here once.
pub(super) fn io<T>(r: std::io::Result<T>) -> Result<T, String> {
    r.map_err(|e| e.to_string())
}

fn said(stderr: String, code: i32) -> Reply {
    Reply {
        stdout: String::new(),
        stderr,
        code,
    }
}

/// `git -C tree args`, a step that fails only where something is badly wrong: its stdout trimmed, or what it said.
pub(super) fn must(tree: &Path, args: &[&str]) -> Result<String, String> {
    let (rc, out) = git(tree, args)?;
    if rc != 0 {
        return Err(format!(
            "git {} failed in {}: {}",
            args.join(" "),
            tree.display(),
            out.trim()
        ));
    }
    Ok(out.trim().to_owned())
}

/// A hand-in under way: the tree found, its scratch commit and its base, and where its files are.
struct Hand<'a> {
    f: &'a Found,
    tree: PathBuf,
    files: PathBuf,
    key: String,
    sha: String,
    base: String,
}

impl Hand<'_> {
    fn file(&self, ext: &str) -> PathBuf {
        self.files.join(format!("{}.{ext}", self.key))
    }

    fn short(sha: &str) -> &str {
        sha.get(..10).unwrap_or(sha)
    }

    /// The rules' resolved list written beside the base file, one `path (rule)` line each, for a resume's end to read.
    fn ruled(&self, resolved: &[String]) -> Result<(), String> {
        let list = resolved.join("\n") + "\n";
        io(std::fs::write(self.file("resolved"), list))
    }

    /// The hand-in undone where nothing of it is to resume: the tree back at the scratch commit's content, HEAD at its old base,
    /// the work uncommitted, the scratch refs and files deleted.
    fn undo(&self) -> Result<(), String> {
        must(&self.tree, &["checkout", "-q", "-f", "--detach", &self.sha])?;
        must(&self.tree, &["reset", "-q", &format!("{}^", self.sha)])?;
        self.spent()
    }

    /// The scratch refs and this tree's hand-in files deleted (step 8, and wherever the hand-in ends with nothing to resume).
    fn spent(&self) -> Result<(), String> {
        for task in self.f.tasks() {
            git(
                &self.tree,
                &[
                    "update-ref",
                    "-d",
                    &format!("{REFS}{}-{task}", self.f.feature()),
                ],
            )?;
        }
        let _ = std::fs::remove_dir_all(&self.files);
        Ok(())
    }
}

pub(super) fn run(
    args: &[String],
    cwd: &Path,
    msg: &str,
    guard: &str,
    knob: &str,
    first: FirstPass,
) -> Reply {
    let origin = match knob {
        "" | "clone" => false,
        "origin" => true,
        _ => return said(format!("hand-in: refused - nothing done: HAND_IN_BASE is clone (the clone's HEAD, phase 1) or origin (origin/main after a fetch, phase 2), not {knob:?}\n"), 2),
    };
    let f = match builder_done::found(args, cwd, msg, guard) {
        Ok(f) => f,
        Err(refusal) => return refusal,
    };
    let done = handed(&f, origin, first);
    done.unwrap_or_else(|why| said(format!("hand-in: {why}\n"), 2))
}

fn handed(f: &Found, origin: bool, first: FirstPass) -> Result<Reply, String> {
    let tree = f.tree().to_path_buf();
    let key = format!("{}-{}", f.feature(), f.tasks()[0]);
    let files = git_dir(&tree)?.join(FILES);
    let scratch = format!("{REFS}{key}");
    let (rc, standing) = git(&tree, &["rev-parse", "-q", "--verify", &scratch])?;
    let mut hand = Hand {
        f,
        tree,
        files,
        key,
        sha: standing.trim().to_owned(),
        base: String::new(),
    };
    if rc == 0 {
        return resume(&mut hand, &scratch, first);
    }
    if let Some(why) = f.unready() {
        return Ok(said(why, 2));
    }
    hand.base = if origin {
        let (rc, out) = git(&hand.tree, &["fetch", "-q", "origin"])?;
        if rc != 0 {
            return Ok(said(
                format!(
                    "hand-in: refused - nothing done: git fetch origin failed in {}: {}\n",
                    hand.tree.display(),
                    out.trim()
                ),
                2,
            ));
        }
        must(&hand.tree, &["rev-parse", "origin/main"])?
    } else {
        f.clone_head().to_owned()
    };
    f.sweep();
    io(std::fs::create_dir_all(&hand.files))?;
    let message = hand.file("message");
    io(std::fs::write(&message, f.message()))?;
    must(&hand.tree, &["add", "-A"])?;
    let (rc, out) = git(
        &hand.tree,
        &["commit", "-q", "-F", &message.to_string_lossy()],
    )?;
    if rc != 0 {
        must(&hand.tree, &["reset", "-q"])?;
        let _ = std::fs::remove_dir_all(&hand.files);
        return Ok(said(format!("hand-in: git commit failed in {} - nothing committed, nothing left staged, the tree still held:\n{}\n", hand.tree.display(), out.trim()), 1));
    }
    hand.sha = must(&hand.tree, &["rev-parse", "HEAD"])?;
    // a step that fails past the scratch commit undoes it: left on HEAD with no ref, the next run found nothing to commit (a
    // reference-transaction hook vetoing the ref, probed 2026-11-27 on git 2.53.0)
    match placed(&hand) {
        Ok(applied) => outcome(&hand, applied, first),
        Err(why) => {
            hand.undo()?;
            Err(format!(
                "{why} - the work is back in the tree uncommitted, on its old base"
            ))
        }
    }
}

/// The scratch refs written, the base file, the tree detached at the base and the scratch commit applied there.
fn placed(hand: &Hand) -> Result<Applied, String> {
    for task in hand.f.tasks() {
        let name = format!("{REFS}{}-{task}", hand.f.feature());
        must(&hand.tree, &["update-ref", &name, &hand.sha])?;
    }
    io(std::fs::write(hand.file("base"), &hand.base))?;
    must(&hand.tree, &["checkout", "-q", "--detach", &hand.base])?;
    apply(&hand.tree, &hand.sha)
}

/// Step 5: a standing hand-in resumed in the tree that left it.
fn resume(hand: &mut Hand, scratch: &str, first: FirstPass) -> Result<Reply, String> {
    let base = std::fs::read_to_string(hand.file("base")).unwrap_or_default();
    let head = must(&hand.tree, &["rev-parse", "HEAD"])?;
    if base.is_empty() || head != base {
        return Ok(said(format!("hand-in: refused - nothing done: {scratch} stands (a hand-in's scratch commit, {}), but this tree did not leave it or is no longer on its base - its work is kept there: take what you need of it (`git show {scratch}`), then `git update-ref -d {scratch}` and run this again\n", Hand::short(&hand.sha)), 2));
    }
    hand.base = base;
    let unmerged = lines(&git(&hand.tree, &["diff", "--name-only", "--diff-filter=U"])?.1);
    let mut kept = lines(&std::fs::read_to_string(hand.file("resolved")).unwrap_or_default());
    if !unmerged.is_empty() {
        match resolve_all(&hand.tree, &unmerged, &hand.sha, Form::NoCommit)? {
            Err(stops) => return outcome(hand, Applied::Conflict(stops), first),
            Ok(paths) => kept.extend(paths),
        }
    }
    let end = verified(&hand.tree, &hand.sha, &kept)?;
    outcome(hand, ended(end, kept), first)
}

/// What an apply (or a resume's end) came to, said; a verified one on to the commit.
fn outcome(hand: &Hand, applied: Applied, first: FirstPass) -> Result<Reply, String> {
    let (tree, base) = (hand.tree.display(), Hand::short(&hand.base));
    let again = hand.f.command();
    match applied {
        Applied::Verified { resolved, .. } => {
            hand.ruled(&resolved)?;
            committed(hand, first)
        }
        Applied::Conflict(stops) => Ok(said(format!("hand-in: STOPPED - nothing committed: the work is applied onto {tree}'s base {base} uncommitted, with a conflict no rule resolves: {} - resolve by hand each path not marked \"its rule would resolve it\" and `git -C {tree} add -- <path>` it (those marked are resolved by their rule when this runs again); the work is kept at {REFS}{}; then run it again: {again}\n", stops.join(", "), hand.key), 2)),
        Applied::Refused(why) => {
            hand.undo()?;
            Ok(said(format!("hand-in: refused - nothing applied: {why}; the work is back in the tree uncommitted, on its old base\n"), 2))
        }
        Applied::NotVerified { fails, resolved } => {
            // kept for the resume as a verified apply's is (461 T39): its end is asked again with this list
            hand.ruled(&resolved)?;
            Ok(said(format!("hand-in: NOT VERIFIED - nothing committed: the work is applied onto {tree}'s base {base} uncommitted, but:\n  {}\nmend it in the tree, then run it again: {again}\n", fails.join("\n  ")), 1))
        }
    }
}

/// Steps 6 to 8: the markers and the first pass asked, everything staged and committed on the base, the commit kept.
fn committed(hand: &Hand, first: FirstPass) -> Result<Reply, String> {
    let (tree, base) = (hand.tree.display(), Hand::short(&hand.base));
    let again = hand.f.command();
    must(&hand.tree, &["add", "-A"])?;
    let staged = lines(&must(
        &hand.tree,
        &["diff", "--cached", "--name-only", "HEAD"],
    )?);
    let marked = |path: &&String| {
        std::fs::read_to_string(hand.tree.join(path)).is_ok_and(|t| has_conflict(&t))
    };
    if let Some(path) = staged.iter().find(marked) {
        return Ok(said(format!("hand-in: refused - nothing committed: a conflict's markers stand in {path} of {tree}; resolve them, then run it again: {again}\n"), 2));
    }
    let (message, kind) = (hand.f.message(), hand.f.kind().unwrap_or_default());
    let reasons = first(&Asked {
        tree: &hand.tree,
        base: &hand.base,
        feature: hand.f.feature(),
        tasks: hand.f.tasks(),
        note: message.lines().next().unwrap_or_default(),
        kind: &kind,
    });
    if !reasons.is_empty() {
        return Ok(said(format!("hand-in: refused by the first pass - nothing committed, the work applied onto {tree}'s base {base} uncommitted; answer each, then run it again ({again}):\n  {}\n", reasons.join("\n  ")), 2));
    }
    // the records a clear first pass wrote into the tree go into the commit with the work (D4)
    must(&hand.tree, &["add", "-A"])?;
    let staged = lines(&must(
        &hand.tree,
        &["diff", "--cached", "--name-only", "HEAD"],
    )?);
    if staged.is_empty() {
        hand.spent()?;
        return Ok(said(format!("hand-in: nothing to hand in - the base {base} already holds every change of the work (its scratch commit {}); make builder-tree-release T={} F={} frees the tree\n", Hand::short(&hand.sha), hand.f.tasks().join(","), hand.f.feature()), 2));
    }
    let (rc, out) = git(&hand.tree, &["commit", "-q", "-C", &hand.sha])?;
    if rc != 0 {
        return Ok(said(format!("hand-in: git commit failed in {tree} - nothing committed; the work stands applied, uncommitted; run it again: {again}\n{}\n", out.trim()), 1));
    }
    let sha = must(&hand.tree, &["rev-parse", "HEAD"])?;
    let mut kept = hand.f.kept(&sha, true);
    hand.spent()?;
    kept.stdout = format!(
        "hand-in: the work applied onto {tree}'s base {base}, verified, and committed there\n{}",
        kept.stdout
    );
    Ok(kept)
}

#[cfg(test)]
mod tests;
