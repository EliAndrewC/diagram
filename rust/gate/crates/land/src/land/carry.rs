//! `l7r-gate land --carry <tree> [<commit>]` (`make carry FROM=<tree> [COMMIT=<sha>]`, feature 451 T292): a builder worktree's commit
//! reaches the current tree by ONE command that carries it and verifies it, in place of a hand `git cherry-pick`. WHY: three landings
//! ran over a hand cherry-pick left unfinished on a conflict (451 T235, T262, T270 - [`super::unfinished`] has T270's), and every
//! carry-over of the parallel trials conflicted in the same two files, each time resolved by hand the same way.
//!
//! The commit carried is the tree's HEAD, or the one named; it is cherry-picked, never merged (the worktree's branch is not the
//! clone's). With no tree and a commit named (`make carry COMMIT=<sha>`, 451 T397) the commit is looked for where the carry runs:
//! a linked worktree's commit is in the clone's own objects, and one `make builder-done` kept under `refs/l7r/done/` stays there
//! after its tree's next handout, so no tree need be named for it. A conflict is resolved here only where keeping both sides is provably what a hand would do:
//!
//! - `specs/*/tasks.md`, where every conflicting hunk is one both sides only ADDED to (nothing of the base between them) and every
//!   added line is a list line, its continuation or blank - an Occasions line, a task's line appended: ours, then theirs' lines ours
//!   lacks. Two tasks' Occasions lines added after the same line is the conflict of every parallel carry-over (2026-11-26: 20347702fc
//!   against be3f3a248b's parent).
//!   A task `make task-add` filed in each tree is the same conflict, each box with its research line: theirs is kept by BLOCK - a
//!   list line with its continuation lines - never line by line (451 T289: the second box's research line, the same words as the
//!   first's, was dropped), and a bare open box is given back the lines a side holds under it ([`boxes`], 451 T300).
//! - `specs/*/plan.md`, by SECTION from its three whole sides ([`sections`], 451 T300), each keyed by its whole heading line (451
//!   T419): the builder's filled stub taken, the stub it removed dropped, the clone's sections kept, the builder's new ones placed
//!   after its task's last, then each task's sections put together in their order; one section both sides changed stops.
//! - `specs/*/request.md`, where every conflicting hunk is one both sides only added to and each side's addition opens with a
//!   `## ` heading - a dated section of the GM's words, one written in each tree: ours, a blank line, then theirs' sections ours
//!   lacks; one heading over different words on the two sides stops (451 T300).
//! - `specs/*/plan-review.json`, merged three-way by the record's own merge (`plan merge-record`, 451 T256), always in process: the
//!   pick runs with the record's git driver failing, so the merge is given the merged plan.md and keeps the verdict on the text
//!   there (451 T495).
//!
//! And outside a feature's spec files (451 T300, part 2 - the four carries of 2026-11-26 that still stopped after the rules above):
//!
//! - `docs/make-targets.html`, GENERATED from the Makefile: never merged - once every other conflict is resolved it is
//!   regenerated (`make docs`' own code, `l7r_gate_cohort::make_docs::write`) and staged. Where that fails the carry stops with
//!   the other files resolved and staged and says what to run.
//! - a hunk of PROSE with base lines - a `.md` line, a Makefile comment or ` ## ` help line, a `.rs` comment line - merged by
//!   words against the merge base ([`words`]): both sides' changes made where they do not overlap, stopped where they do.
//! - a hunk with no base lines, both sides having added whole lines at one place ([`added`]): two Makefile target blocks or two
//!   Markdown bullets, kept both, the clone's first.
//! - a `.jsonl`, by record ([`records`], 451 T399): each side's appended records kept, what either pruned dropped.
//!
//! Any other conflict - another file, code, or words both sides changed - stops: nothing is resolved, the files and the next command are
//! printed, the pick is left standing, and `make land` refuses until it is finished. The carry ENDS by verifying: nothing in
//! progress, nothing unmerged, nothing staged, and each non-spec file of the carried commit in HEAD - changed by the carry (HEAD
//! against the commit before it names the path), already holding the carried commit's content, or holding its change among others
//! (its lines counted, 461 T73). Its last line says so, and names
//! each file it resolved with the rule that resolved it.
//!
//! A commit whose changes HEAD already holds - carried before under another sha, or its lines kept from both sides equal to ours -
//! makes an EMPTY pick: it is skipped, verified the same way, and said to change nothing (exit 0, nothing left in progress; T304).
//! At that verified end, empty or not, the ref `make builder-done` kept the commit under is deleted ([`spent`], 451 T397) - where
//! the carry ran in the clone's main worktree; a carry in a linked worktree keeps it, said, the clone still waiting (451 T404).
//!
//! Exit: 0 carried and verified (or already in HEAD's history), 2 refused or stopped (the stop leaves the pick in progress), 1 the
//! end's verification failed.
//!
//! `--no-commit` (461 T05) is the NO-COMMIT form, [`apply`]: the same rules, the commit applied onto HEAD and left uncommitted, with
//! its own verified end - the hand-in's apply (461 D3).

use std::collections::HashMap;
use std::path::Path;

use l7r_gate_core::Reply;
use l7r_gate_task::builder_done::REFS as DONE_REFS;
use l7r_shared::speckit::marks;

use super::unfinished::{git, git_dir, lines, refusals};

mod added;
pub(super) mod apply;
mod boxes;
mod records;
mod sections;
mod words;

const USAGE: &str =
    "usage: l7r-gate land --carry [--no-commit] <tree> [<commit>]   (make carry FROM=<builder's worktree> [COMMIT=<sha>]; COMMIT=<sha> alone for a commit this clone's objects hold, as make builder-done keeps one; --no-commit applies it onto HEAD uncommitted)";
/// The pick's own continue, its editor answered.
const CONTINUE: &str = "-c core.editor=true cherry-pick --continue";

/// The carry's two forms: the pick committed (`make carry`), or applied and left uncommitted ([`apply`], 461 T05).
#[derive(Clone, Copy, PartialEq, Eq)]
pub(super) enum Form {
    Commit,
    NoCommit,
}

impl Form {
    /// What finishes a pick whose other conflicts are resolved and staged, once its generated page is regenerated by hand.
    fn then(self) -> String {
        match self {
            Self::Commit => format!("`git {CONTINUE}`"),
            Self::NoCommit => "nothing to continue (the no-commit form commits nothing)".to_owned(),
        }
    }
}

/// What the carry printed, and its exit.
struct Said {
    out: String,
    err: String,
}

impl Said {
    /// Text on stdout, as written.
    fn say(&mut self, text: &str) {
        self.out.push_str(text);
    }

    /// Text on stderr, as written.
    fn warn(&mut self, text: &str) {
        self.err.push_str(text);
    }

    fn reply(self, code: i32) -> Reply {
        Reply {
            stdout: self.out,
            stderr: self.err,
            code,
        }
    }
}

/// Is `path` `specs/<feature>/<name>`?
fn spec_file(path: &str, name: &str) -> bool {
    let parts: Vec<&str> = path.split('/').collect();
    parts.len() == 3 && parts[0] == "specs" && parts[2] == name
}

/// A line both sides may add at one place of a tasks.md and keep: a list line (an Occasions line, a task's line), its continuation,
/// or a blank.
fn listed(line: &str) -> bool {
    line.starts_with("- ") || line.starts_with([' ', '\t']) || line.trim().is_empty()
}

/// The file whose conflict is kept both: what each side may add at one place, and what of theirs ours already holds.
#[derive(Clone, Copy, PartialEq, Eq)]
enum Kind {
    /// `specs/*/tasks.md`: list lines, each with its continuation lines - an Occasions line, a task's box with its research line.
    Tasks,
    /// `specs/*/request.md`: whole `## ` sections - a dated section of the GM's words (451 T300).
    Request,
}

/// One side's added lines as its blocks: in a tasks.md a list line with its continuation lines (a blank its own block), in a
/// request.md a `## ` heading with the lines under it.
fn blocks(lines: &[&str], kind: Kind) -> Vec<String> {
    let mut out: Vec<String> = Vec::new();
    for line in lines {
        let opens = match kind {
            Kind::Tasks => line.starts_with("- ") || line.trim().is_empty(),
            Kind::Request => line.starts_with("## "),
        };
        match out.last_mut() {
            Some(last) if !opens => last.push_str(line),
            _ => out.push((*line).to_owned()),
        }
    }
    out
}

/// A block's first line.
fn head(block: &str) -> &str {
    block.split_inclusive('\n').next().unwrap_or("")
}

/// One conflicting hunk both sides only added to, kept both: ours, then the blocks of theirs ours lacks - or why it is left to a hand.
///
/// BY BLOCK, NEVER BY LINE (451 T289, measured 2026-11-26 on two worktrees' `make task-add`): theirs' lines were dropped one by one
/// where ours held the same line, so the second of two filed boxes lost its `      research: rendering` line - the first box has the
/// same one. A block of theirs is dropped where ours has it whole - in a tasks.md also where theirs is the bare list
/// line of a block ours has (ours' continuation kept) - and one list line with different lines under it on each side stops, as one
/// heading of a request over different words does: either is a choice between the sides, not an addition. A request's sections
/// stand a blank line apart.
fn both(ours: &[&str], theirs: &[&str], kind: Kind) -> Result<String, String> {
    for side in [ours, theirs] {
        let odd = match kind {
            Kind::Tasks => side
                .iter()
                .find(|l| !listed(l))
                .map(|l| ("line", "list line", l)),
            // a side opens with a section's heading, so what it added is whole sections and nothing of another's
            Kind::Request => side
                .iter()
                .find(|l| !l.trim().is_empty())
                .filter(|l| !l.starts_with("## "))
                .map(|l| ("block", "`## ` section", l)),
        };
        if let Some((what, wanted, line)) = odd {
            return Err(format!(
                "an added {what} that is no {wanted}: {}",
                line.trim_end()
            ));
        }
    }
    let held = blocks(ours, kind);
    let mut out: String = ours.concat();
    for block in blocks(theirs, kind) {
        let same_line = held.iter().any(|h| head(h) == head(&block));
        // ours has it whole, or has the list line theirs adds bare
        if held.contains(&block) || (kind == Kind::Tasks && same_line && block == head(&block)) {
            continue;
        }
        // one list line with different lines under it on each side, or one heading over different words, is a choice between them
        if same_line && !head(&block).trim().is_empty() {
            return Err(match kind {
                Kind::Tasks => format!(
                    "both sides added one list line with different lines under it: {}",
                    head(&block).trim_end()
                ),
                Kind::Request => format!(
                    "both sides added one section, differently: {}",
                    head(&block).trim_end()
                ),
            });
        }
        if kind == Kind::Request && !block.trim().is_empty() && !out.ends_with("\n\n") {
            out.push('\n');
        }
        out += &block;
    }
    Ok(out)
}

/// A diff3 merge (`git merge-file -p --diff3`) with every conflict resolved by keeping both sides ([`both`]) - or why not: a hunk
/// with base lines between its sides (both changed something), or a side that added what `kind` does not keep.
fn keep_both(merged: &str, kind: Kind) -> Result<String, String> {
    let mut out = String::new();
    // 0 outside a conflict, 1 in ours, 2 in the base, 3 in theirs
    let mut part = 0;
    let (mut ours, mut theirs): (Vec<&str>, Vec<&str>) = (Vec::new(), Vec::new());
    for line in merged.split_inclusive('\n') {
        match (part, line.get(..7)) {
            (0, Some("<<<<<<<")) => part = 1,
            (1, Some("|||||||")) => part = 2,
            (2, Some("=======")) => part = 3,
            (3, Some(">>>>>>>")) => {
                part = 0;
                out += &both(&ours, &theirs, kind)?;
                ours.clear();
                theirs.clear();
            }
            (0, _) => out += line,
            (1, _) => ours.push(line),
            (2, _) => return Err("a hunk both sides changed, not only added to".to_owned()),
            (_, _) => theirs.push(line),
        }
    }
    Ok(out)
}

/// `git merge-file -p --diff3` of three files, ours first: the merge with its conflicts marked.
fn merge_file(root: &Path, files: &[String]) -> Result<String, String> {
    let args = [
        "merge-file",
        "-p",
        "--diff3",
        &files[1],
        &files[0],
        &files[2],
    ];
    Ok(git(root, &args)?.1)
}

/// The page `make docs` generates from the Makefile: regenerated after a conflict, never merged.
const PAGE: &str = "docs/make-targets.html";
/// A feature's plan review record, merged beside its plan (451 T495).
const RECORD: &str = "plan-review.json";
/// The pick's record driver, failing: a record both sides changed stops unmerged and is merged in process, beside the merged plan.md
/// git's driver is never given (451 T495; mid-merge the work tree holds ours' plan, probed 2026-11-27).
const NO_DRIVER: &str = "merge.plan-review.driver=false";

/// The merged plan.md beside the record at `path`: the one this pass resolved where it was unmerged, else the one the pick wrote.
fn merged_plan(
    root: &Path,
    path: &str,
    merged: &[&String],
    texts: &[Option<Result<(String, &'static str), String>>],
) -> Option<String> {
    let plan = format!("{}plan.md", path.strip_suffix(RECORD)?);
    match merged.iter().position(|p| **p == plan) {
        Some(i) => texts[i].as_ref()?.as_ref().ok().map(|(t, _)| t.clone()),
        None => std::fs::read_to_string(root.join(&plan)).ok(),
    }
}

/// One unmerged path resolved by its file's rule: its merged text and the rule's name, or why it is left to a hand. Its three
/// stages are written under `scratch` and merged there.
fn resolved(
    root: &Path,
    scratch: &Path,
    path: &str,
    plan: Option<&str>,
) -> Result<(String, &'static str), String> {
    let spec = |name: &str| spec_file(path, name);
    let named = ["tasks.md", "plan.md", "request.md", "plan-review.json"]
        .iter()
        .any(|name| spec(name));
    let prose = words::kind(path);
    let records = Path::new(path)
        .extension()
        .is_some_and(|ext| ext == "jsonl");
    if !named && !records && prose.is_none() {
        return Err("a file the carry has no rule for".to_owned());
    }
    let mut files = Vec::new();
    let mut sides = Vec::new();
    for stage in ["1", "2", "3"] {
        let (rc, text) = git(root, &["show", &format!(":{stage}:{path}")])?;
        if rc != 0 {
            return Err("added or deleted by one side".to_owned());
        }
        let file = scratch.join(stage);
        std::fs::write(&file, &text).map_err(super::io)?;
        files.push(file.to_string_lossy().into_owned());
        sides.push(text);
    }
    if spec("plan.md") {
        return Ok((
            sections::merged(&sides[0], &sides[1], &sides[2])?,
            "by section",
        ));
    }
    if spec("request.md") {
        let merged = merge_file(root, &files)?;
        return Ok((
            keep_both(&merged, Kind::Request)?,
            "both sides' dated sections",
        ));
    }
    if spec("tasks.md") {
        let kept = keep_both(&merge_file(root, &files)?, Kind::Tasks)?;
        return Ok((
            boxes::restored(&kept, [&sides[1], &sides[2]]),
            "both sides' list lines",
        ));
    }
    if records {
        let text = records::merged(&sides[0], &sides[1], &sides[2])?;
        return Ok((text, "both sides' records"));
    }
    if let Some(kind) = prose {
        return added::merged(&merge_file(root, &files)?, kind);
    }
    let said = l7r_gate_plan::plan::merge_files(
        Path::new(&files[0]),
        Path::new(&files[1]),
        Path::new(&files[2]),
        plan,
    );
    if said.code != 0 {
        return Err("a side is not JSON".to_owned());
    }
    let text = std::fs::read_to_string(&files[1]).map_err(super::io)?;
    Ok((text, "the record's merge"))
}

/// The stopped pick's conflicts resolved where each has a rule that resolves it - all of them, or none: each path resolved with its
/// rule's name, or each path with why it stops. `sha` is the commit picked: the side a cleanly merged tasks.md's boxes are restored
/// from, named by its sha because a no-commit pick writes no `CHERRY_PICK_HEAD` (461 T05).
pub(super) fn resolve_all(
    root: &Path,
    unmerged: &[String],
    sha: &str,
    form: Form,
) -> Result<Result<Vec<String>, Vec<String>>, String> {
    let scratch = git_dir(root)?.join("l7r-carry");
    std::fs::create_dir_all(&scratch).map_err(super::io)?;
    let merged: Vec<&String> = unmerged.iter().filter(|p| *p != PAGE).collect();
    // each record after the rest, beside its feature's merged plan.md: the one resolved here, else the one the pick wrote (451 T495)
    let mut texts: Vec<Option<Result<(String, &'static str), String>>> = merged
        .iter()
        .map(|p| (!spec_file(p, RECORD)).then(|| resolved(root, &scratch, p, None)))
        .collect();
    for i in 0..merged.len() {
        if texts[i].is_none() {
            let plan = merged_plan(root, merged[i], &merged, &texts);
            texts[i] = Some(resolved(root, &scratch, merged[i], plan.as_deref()));
        }
    }
    let texts: Vec<Result<(String, &'static str), String>> = texts.into_iter().flatten().collect();
    let _ = std::fs::remove_dir_all(&scratch);
    let stops: Vec<String> = merged
        .iter()
        .zip(&texts)
        .filter_map(|(p, t)| t.as_ref().err().map(|why| format!("{p} ({why})")))
        .collect();
    if !stops.is_empty() {
        return Ok(Err(stops));
    }
    let mut done = Vec::new();
    for (path, text) in merged.iter().zip(texts) {
        let (text, rule) = text.unwrap_or_default();
        std::fs::write(root.join(path), text).map_err(super::io)?;
        git(root, &["add", "--", path])?;
        done.push(format!("{path} ({rule})"));
    }
    // the generated page last, from the Makefile as the pick and the rules above left it
    if merged.len() < unmerged.len() {
        let said = l7r_gate_cohort::make_docs::write(root);
        if said.code != 0 {
            return Err(format!("{PAGE} was not regenerated, the pick's other conflicts resolved and staged - {} - regenerate it (`make docs`), `git add` it and {}", said.stderr.trim(), form.then()));
        }
        git(root, &["add", "--", PAGE])?;
        done.push(format!("{PAGE} (regenerated)"));
    }
    // a tasks.md git merged cleanly keeps its boxes' lines too
    for path in lines(&git(root, &["diff", "--cached", "--name-only"])?.1) {
        let side = |rev: &str| git(root, &["show", &format!("{rev}:{path}")]).map(|said| said.1);
        if !spec_file(&path, "tasks.md") || unmerged.contains(&path) {
            continue;
        }
        let text = std::fs::read_to_string(root.join(&path)).map_err(super::io)?;
        let whole = boxes::restored(&text, [&side("HEAD")?, &side(sha)?]);
        if whole != text {
            std::fs::write(root.join(&path), whole).map_err(super::io)?;
            git(root, &["add", "--", &path])?;
            done.push(format!("{path} (a bare box's lines restored)"));
        }
    }
    Ok(Ok(done))
}

/// The carried commit's files outside `specs/` that HEAD does not hold: neither changed since `before`, nor at the commit's content,
/// nor holding the commit's change among others ([`holds_change`], 461 T73: a ledger whose rows the base already held).
///
/// A file a RULE resolved is held whatever its text: the rule's result can be the clone's own (a page regenerated to what the clone
/// had, records the clone already held), which the pick's commit then does not touch.
///
/// In the no-commit form (461 T05) HEAD never moves: the file is held where the WORKING TREE holds it - changed there against `before`
/// (HEAD), or at the commit's content (a file the commit deletes held where the working tree lacks it too).
fn missing(
    root: &Path,
    sha: &str,
    before: &str,
    kept: &[String],
    form: Form,
) -> Result<(usize, Vec<String>), String> {
    let names = lines(
        &git(
            root,
            &["diff-tree", "--no-commit-id", "--name-only", "-r", sha],
        )?
        .1,
    );
    let to: &[&str] = match form {
        Form::Commit => &["HEAD"],
        Form::NoCommit => &[],
    };
    let moved = lines(&git(root, &[&["diff", "--name-only", before], to].concat())?.1);
    let own: Vec<String> = names
        .into_iter()
        .filter(|n| !n.starts_with("specs/"))
        .collect();
    let mut lacks = Vec::new();
    for path in &own {
        let blob = |rev: &str| {
            git(
                root,
                &["rev-parse", "-q", "--verify", &format!("{rev}:{path}")],
            )
        };
        // the working tree's blob, as `rev-parse` answers a commit's: absent is `(1, "")`
        let held = match form {
            Form::Commit => blob("HEAD")?,
            Form::NoCommit if root.join(path).exists() => git(root, &["hash-object", "--", path])?,
            Form::NoCommit => (1, String::new()),
        };
        let ruled = kept.iter().any(|k| k.starts_with(&format!("{path} (")));
        if !ruled
            && !moved.contains(path)
            && held != blob(sha)?
            && !change_held(root, sha, path, form)?
        {
            lacks.push(path.clone());
        }
    }
    Ok((own.len(), lacks))
}

/// `path` as `rev` holds it, absent read as empty.
fn text_at(root: &Path, rev: &str, path: &str) -> Result<String, String> {
    let (rc, out) = git(root, &["show", &format!("{rev}:{path}")])?;
    Ok(if rc == 0 { out } else { String::new() })
}

/// Whether HEAD (the working tree in the no-commit form) already holds the commit's change to `path` among other changes (461 T73):
/// [`holds_change`] over the commit's parent, the commit and HEAD's text.
fn change_held(root: &Path, sha: &str, path: &str, form: Form) -> Result<bool, String> {
    let held = match form {
        Form::Commit => text_at(root, "HEAD", path)?,
        Form::NoCommit => {
            String::from_utf8_lossy(&std::fs::read(root.join(path)).unwrap_or_default())
                .into_owned()
        }
    };
    let parent = text_at(root, &format!("{sha}^"), path)?;
    Ok(holds_change(&parent, &text_at(root, sha, path)?, &held))
}

/// THE CHANGE ALREADY HELD (461 T73), by its lines counted: every line the commit made more frequent than its parent had it is in
/// `held` at least as often as in the commit, every line it made less frequent at most as often, and at least one line's count
/// changed (a commit that only reorders lines is held by no count). WHY COUNTS, NOT THE PATCH REVERSED: a review ledger whose added
/// rows the base holds with another row after them (`merge=union`, the pick merging to HEAD's own text) is held, though the
/// patch's context no longer matches - measured 2026-11-28, `git apply -R --check` of 1136054db4's `dev/review-ledger.md` hunk
/// failed against af774303de and origin/main both, the stop of the lane's batch 462-1. WHY COUNTS, NOT MEMBERSHIP: a commit adding a
/// common line (`}`, a blank) is held only where HEAD has as many of it as the commit's file. Label: the easier route.
fn holds_change(parent: &str, commit: &str, held: &str) -> bool {
    fn counts(text: &str) -> HashMap<&str, usize> {
        let mut m = HashMap::new();
        for l in text.lines() {
            *m.entry(l).or_default() += 1;
        }
        m
    }
    let (was, is, has) = (counts(parent), counts(commit), counts(held));
    let n = |m: &HashMap<&str, usize>, l: &str| m.get(l).copied().unwrap_or(0);
    let mut changed = false;
    for l in is.keys().chain(was.keys()) {
        let (before, after, now) = (n(&was, l), n(&is, l), n(&has, l));
        changed |= before != after;
        if (after > before && now < after) || (after < before && now > after) {
            return false;
        }
    }
    changed
}

/// A pick that came out EMPTY - `CHERRY_PICK_HEAD` standing, nothing unmerged, nothing staged: every change of the commit is already
/// in HEAD - is skipped (`git cherry-pick --skip`), so nothing is left in progress; whether it was one. WHY (451 T304): a commit
/// carried a second time is in HEAD's history only where its first pick reproduced its sha - the same parent, author, message AND
/// committer second - so a second `make carry` of a carried commit, in a real clone always under another sha, stopped at exit 2
/// with a pick standing that `make land` then refused; the test of it passed only while the builder's commit and its pick fell in one
/// wall second (3 red of 100 loops alone, 2026-11-26). A pick that refused to start leaves no marker and is no empty pick.
fn skipped_empty(root: &Path) -> Result<bool, String> {
    let empty = git_dir(root)?.join("CHERRY_PICK_HEAD").exists()
        && git(root, &["diff", "--cached", "--quiet"])?.0 == 0;
    Ok(empty && git(root, &["cherry-pick", "--skip"])?.0 == 0)
}

/// The refs `make builder-done` kept `sha` under (`refs/l7r/done/<feature>-<task>`), deleted, and the words that say so; nothing
/// where it is under none. A done ref says "this commit waits on its carry", and this is the carry's verified end - carried, in
/// HEAD's history already, or an EMPTY pick skipped because HEAD holds its changes by another route. WHY HERE (451 T397, the plan
/// review of T394, 2026-11-27): `make builder-trees` and `make builder-tree` tell a carried commit by its author's time and
/// subject in HEAD, which an empty pick never leaves there, so its ref stayed and the task was refused its next tree though
/// its work was in HEAD.
///
/// ONLY IN THE CLONE (451 T404): refs are shared by every worktree of a clone, so a carry run in a linked worktree - a pool tree, a
/// builder's scratch - would delete the ref of a done commit the clone's HEAD still lacks, and `make builder-trees` would list it no
/// more. A carry that ran anywhere but the clone's main worktree keeps the ref and says so. The main worktree, not "the clone's
/// HEAD holds a commit of its author's time and subject" (`builder_done`'s test): an empty pick leaves no such commit, and its
/// ref is spent in the clone all the same (451 T397).
fn spent(root: &Path, sha: &str) -> Result<String, String> {
    let listed = git(
        root,
        &[
            "for-each-ref",
            "--format=%(refname)",
            "--points-at",
            sha,
            DONE_REFS,
        ],
    )?;
    let refs = lines(&listed.1);
    if refs.is_empty() {
        return Ok(String::new());
    }
    let clone = marks::places(root).map(|(common, _)| marks::main_top(&common));
    if let Some(clone) = clone.filter(|c| !marks::same_tree(c, root)) {
        return Ok(format!(
            "; still waiting on its carry into {}, which this tree is not: {} kept",
            clone.display(),
            refs.join(", ")
        ));
    }
    for name in &refs {
        git(root, &["update-ref", "-d", name])?;
    }
    Ok(format!(
        "; no longer waiting on its carry: {}",
        refs.join(", ")
    ))
}

/// `commit` of `from` as a sha `root`'s objects hold - fetched from `from` where they do not - or None with the refusal said.
fn located(
    root: &Path,
    from: &Path,
    commit: &str,
    said: &mut Said,
) -> Result<Option<String>, String> {
    let (rc, out) = git(
        from,
        &[
            "rev-parse",
            "-q",
            "--verify",
            &format!("{commit}^{{commit}}"),
        ],
    )?;
    if rc != 0 {
        said.warn(&format!(
            "carry: refused - nothing carried: {} holds no commit {commit}\n{USAGE}\n",
            from.display()
        ));
        return Ok(None);
    }
    let sha = out.trim().to_owned();
    let short: String = sha.chars().take(10).collect();
    let known = |root: &Path| git(root, &["cat-file", "-e", &format!("{sha}^{{commit}}")]);
    // a linked worktree shares the clone's objects; another clone's commit is fetched from it
    if known(root)?.0 != 0 {
        git(root, &["fetch", "-q", &from.to_string_lossy(), "HEAD"])?;
        if known(root)?.0 != 0 {
            said.warn(&format!("carry: refused - nothing carried: {short} is not HEAD of {} nor in its history, so it cannot be fetched from there\n", from.display()));
            return Ok(None);
        }
    }
    Ok(Some(sha))
}

/// The carry, after its arguments: what it printed and its exit code.
fn carry(root: &Path, from: &Path, commit: &str, said: &mut Said) -> Result<i32, String> {
    let tree = root.display();
    let stops = refusals(root)?;
    if !stops.is_empty() {
        said.warn(&format!(
            "carry: refused - nothing carried; {tree} holds unfinished work:\n  {}\n",
            stops.join("\n  ")
        ));
        return Ok(2);
    }
    let Some(sha) = located(root, from, commit, said)? else {
        return Ok(2);
    };
    let short: String = sha.chars().take(10).collect();
    if git(root, &["merge-base", "--is-ancestor", &sha, "HEAD"])?.0 == 0 {
        let spent = spent(root, &sha)?;
        said.say(&format!(
            "carry: {short} is already in {tree}'s history - nothing to carry{spent}\n"
        ));
        return Ok(0);
    }
    let before = git(root, &["rev-parse", "HEAD"])?.1.trim().to_owned();
    let (rc, out) = git(
        root,
        &[
            "-c",
            "core.editor=true",
            "-c",
            NO_DRIVER,
            "cherry-pick",
            &sha,
        ],
    )?;
    let mut kept = Vec::new();
    if rc != 0 {
        let unmerged = lines(&git(root, &["diff", "--name-only", "--diff-filter=U"])?.1);
        let stopped = |said: &mut Said, what: &str| -> Result<i32, String> {
            said.warn(&format!(
                "carry: STOPPED - {short} is NOT carried into {tree}: {what}\n  {}\n",
                refusals(root)?.join("\n  ")
            ));
            Ok(2)
        };
        if unmerged.is_empty() {
            if skipped_empty(root)? {
                return end(root, &sha, &before, &kept, said);
            }
            // nothing to resolve and nothing standing: the pick refused to start (a local edit in its way)
            let why = lines(&out).join(" | ");
            return stopped(said, &format!("git cherry-pick said: {why}"));
        }
        match resolve_all(root, &unmerged, &sha, Form::Commit)? {
            Err(stops) => {
                return stopped(
                    said,
                    &format!(
                        "a conflict this command does not resolve, in {} - nothing was resolved",
                        stops.join(", ")
                    ),
                )
            }
            Ok(paths) => kept = paths,
        }
        let (rc, out) = git(root, &CONTINUE.split(' ').collect::<Vec<_>>())?;
        if rc != 0 && !skipped_empty(root)? {
            let why = lines(&out).join(" | ");
            return stopped(said, &format!("its continue failed: {why}"));
        }
    }
    end(root, &sha, &before, &kept, said)
}

/// THE END, verified, never assumed: nothing in progress, unmerged or staged, and the carried commit's non-spec files in HEAD.
fn end(
    root: &Path,
    sha: &str,
    before: &str,
    kept: &[String],
    said: &mut Said,
) -> Result<i32, String> {
    let tree = root.display();
    let short: String = sha.chars().take(10).collect();
    let mut every = refusals(root)?;
    let (count, lacks) = missing(root, sha, before, kept, Form::Commit)?;
    if !lacks.is_empty() {
        every.push(format!(
            "HEAD does not hold the carried commit's {}",
            lacks.join(", ")
        ));
    }
    if !every.is_empty() {
        said.warn(&format!(
            "carry: NOT VERIFIED - {short} into {tree}:\n  {}\n",
            every.join("\n  ")
        ));
        return Ok(1);
    }
    let head: String = git(root, &["rev-parse", "HEAD"])?
        .1
        .trim()
        .chars()
        .take(10)
        .collect();
    let both = if kept.is_empty() {
        String::new()
    } else {
        format!("; resolved {}", kept.join(", "))
    };
    // HEAD where the carry found it: the pick came out empty and was skipped
    let how = if before.starts_with(&head) {
        format!("changes nothing in {tree}, whose HEAD {head} already holds its changes - nothing to carry")
    } else {
        format!("carried into {tree} as {head}")
    };
    let spent = spent(root, sha)?;
    said.say(&format!("carry: {short} {how} - verified: nothing in progress, nothing unmerged, nothing staged, its {count} non-spec file(s) in HEAD{both}{spent}\n"));
    Ok(0)
}

/// `l7r-gate land --carry [--no-commit] <tree> [<commit>]`, run in `root`.
pub(super) fn cli(args: &[String], root: &Path) -> Reply {
    let mut said = Said {
        out: String::new(),
        err: String::new(),
    };
    // the no-commit form (461 T05): applied onto HEAD and left uncommitted, its own verified end
    let no_commit = args.first().is_some_and(|a| a == "--no-commit");
    let args = &args[usize::from(no_commit)..];
    // no tree named and a commit given: a commit the clone's own objects hold, as `make builder-done` keeps one (451 T397)
    let first = args.first().map_or("", String::as_str);
    let named = args.get(1).filter(|c| !c.is_empty());
    if args.len() > 2 || (first.is_empty() && named.is_none()) {
        said.err = format!("{USAGE}\n");
        return said.reply(2);
    }
    let from = if first.is_empty() {
        root
    } else {
        Path::new(first)
    };
    let commit = named.map_or("HEAD", String::as_str);
    let run = if no_commit {
        apply::cli(root, from, commit, &mut said)
    } else {
        carry(root, from, commit, &mut said)
    };
    match run {
        Ok(code) => said.reply(code),
        Err(why) => {
            said.warn(&format!("carry: {why}\n"));
            said.reply(2)
        }
    }
}

#[cfg(test)]
mod tests;
