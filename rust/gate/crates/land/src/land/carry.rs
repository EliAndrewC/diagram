//! `l7r-gate land --carry <tree> [<commit>]` (`make carry FROM=<tree> [COMMIT=<sha>]`, feature 451 T292): a builder worktree's commit
//! reaches the current tree by ONE command that carries it and verifies it, in place of a hand `git cherry-pick`. WHY: three landings
//! ran over a hand cherry-pick left unfinished on a conflict (451 T235, T262, T270 - [`super::unfinished`] has T270's), and every
//! carry-over of the parallel trials conflicted in the same two files, each time resolved by hand the same way.
//!
//! The commit carried is the tree's HEAD, or the one named; it is cherry-picked, never merged (the worktree's branch is not the
//! clone's). A conflict is resolved here only where keeping both sides is provably what a hand would do:
//!
//! - `specs/*/tasks.md`, where every conflicting hunk is one both sides only ADDED to (nothing of the base between them) and every
//!   added line is a list line, its continuation or blank - an Occasions line, a task's line appended: ours, then theirs' lines ours
//!   lacks. Two tasks' Occasions lines added after the same line is the conflict of every parallel carry-over (2026-11-26: 20347702fc
//!   against be3f3a248b's parent).
//! - `specs/*/plan-review.json`, merged three-way by the record's own merge (`plan merge-record`, 451 T256), asked in process where
//!   the tree's git config defines no driver.
//!
//! Any other conflict - another file, or a hunk both sides changed - stops: nothing is resolved, the files and the next command are
//! printed, the pick is left standing, and `make land` refuses until it is finished. The carry ENDS by verifying: nothing in
//! progress, nothing unmerged, nothing staged, and each non-spec file of the carried commit in HEAD - changed by the carry (HEAD
//! against the commit before it names the path) or already holding the carried commit's content. Its last line says so.
//!
//! Exit: 0 carried and verified (or already in HEAD's history), 2 refused or stopped (the stop leaves the pick in progress), 1 the
//! end's verification failed.

use std::path::Path;

use l7r_gate_core::Reply;

use super::unfinished::{git, git_dir, lines, refusals};

const USAGE: &str =
    "usage: l7r-gate land --carry <tree> [<commit>]   (make carry FROM=<builder's worktree> [COMMIT=<sha>])";
/// The pick's own continue, its editor answered.
const CONTINUE: &str = "-c core.editor=true cherry-pick --continue";

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

/// A line both sides may add at one place and keep: a list line (an Occasions line, a task's line), its continuation, or a blank.
fn listed(line: &str) -> bool {
    line.starts_with("- ") || line.starts_with([' ', '\t']) || line.trim().is_empty()
}

/// A diff3 merge (`git merge-file -p --diff3`) with every conflict resolved by keeping both sides - ours, then theirs' lines ours
/// lacks - or why not: a hunk with base lines between its sides (both changed something), or an added line that is no list line.
fn keep_both(merged: &str) -> Result<String, String> {
    let mut out = String::new();
    // 0 outside a conflict, 1 in ours, 2 in the base, 3 in theirs
    let mut part = 0;
    let mut ours: Vec<&str> = Vec::new();
    for line in merged.split_inclusive('\n') {
        match (part, line.get(..7)) {
            (0, Some("<<<<<<<")) => part = 1,
            (1, Some("|||||||")) => part = 2,
            (2, Some("=======")) => part = 3,
            (3, Some(">>>>>>>")) => {
                part = 0;
                ours.clear();
            }
            (0, _) => out += line,
            (2, _) => return Err("a hunk both sides changed, not only added to".to_owned()),
            (_, _) if !listed(line) => {
                return Err(format!(
                    "an added line that is no list line: {}",
                    line.trim_end()
                ))
            }
            (1, _) => {
                ours.push(line);
                out += line;
            }
            (_, _) => {
                if !ours.contains(&line) {
                    out += line;
                }
            }
        }
    }
    Ok(out)
}

/// One unmerged path resolved by keeping both sides: its merged text, or why it is left to a hand. Its three stages are written under
/// `scratch` and merged there.
fn resolved(root: &Path, scratch: &Path, path: &str) -> Result<String, String> {
    let tasks = spec_file(path, "tasks.md");
    if !tasks && !spec_file(path, "plan-review.json") {
        return Err("not a tasks.md or plan-review.json of a feature".to_owned());
    }
    let mut files = Vec::new();
    for stage in ["1", "2", "3"] {
        let (rc, text) = git(root, &["show", &format!(":{stage}:{path}")])?;
        if rc != 0 {
            return Err("added or deleted by one side".to_owned());
        }
        let file = scratch.join(stage);
        std::fs::write(&file, text).map_err(super::io)?;
        files.push(file.to_string_lossy().into_owned());
    }
    if tasks {
        let (_, merged) = git(
            root,
            &[
                "merge-file",
                "-p",
                "--diff3",
                &files[1],
                &files[0],
                &files[2],
            ],
        )?;
        return keep_both(&merged);
    }
    let said = l7r_gate_plan::plan::merge_files(
        Path::new(&files[0]),
        Path::new(&files[1]),
        Path::new(&files[2]),
    );
    if said.code != 0 {
        return Err("a side is not JSON".to_owned());
    }
    std::fs::read_to_string(&files[1]).map_err(super::io)
}

/// The stopped pick's conflicts resolved where each can be kept both - all of them, or none: the paths resolved, or each path with
/// why it stops.
fn resolve_all(
    root: &Path,
    unmerged: &[String],
) -> Result<Result<Vec<String>, Vec<String>>, String> {
    let scratch = git_dir(root)?.join("l7r-carry");
    std::fs::create_dir_all(&scratch).map_err(super::io)?;
    let texts: Vec<Result<String, String>> = unmerged
        .iter()
        .map(|p| resolved(root, &scratch, p))
        .collect();
    let _ = std::fs::remove_dir_all(&scratch);
    let stops: Vec<String> = unmerged
        .iter()
        .zip(&texts)
        .filter_map(|(p, t)| t.as_ref().err().map(|why| format!("{p} ({why})")))
        .collect();
    if !stops.is_empty() {
        return Ok(Err(stops));
    }
    for (path, text) in unmerged.iter().zip(texts) {
        std::fs::write(root.join(path), text.unwrap_or_default()).map_err(super::io)?;
        git(root, &["add", "--", path])?;
    }
    Ok(Ok(unmerged.to_vec()))
}

/// The carried commit's files outside `specs/` that HEAD does not hold: neither changed since `before` nor at the commit's content.
fn missing(root: &Path, sha: &str, before: &str) -> Result<(usize, Vec<String>), String> {
    let names = lines(
        &git(
            root,
            &["diff-tree", "--no-commit-id", "--name-only", "-r", sha],
        )?
        .1,
    );
    let moved = lines(&git(root, &["diff", "--name-only", before, "HEAD"])?.1);
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
        if !moved.contains(path) && blob("HEAD")? != blob(sha)? {
            lacks.push(path.clone());
        }
    }
    Ok((own.len(), lacks))
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
        return Ok(2);
    }
    let sha = out.trim().to_owned();
    let short: String = sha.chars().take(10).collect();
    let known = |root: &Path| git(root, &["cat-file", "-e", &format!("{sha}^{{commit}}")]);
    // a linked worktree shares the clone's objects; another clone's commit is fetched from it
    if known(root)?.0 != 0 {
        git(root, &["fetch", "-q", &from.to_string_lossy(), "HEAD"])?;
        if known(root)?.0 != 0 {
            said.warn(&format!("carry: refused - nothing carried: {short} is not HEAD of {} nor in its history, so it cannot be fetched from there\n", from.display()));
            return Ok(2);
        }
    }
    if git(root, &["merge-base", "--is-ancestor", &sha, "HEAD"])?.0 == 0 {
        said.say(&format!(
            "carry: {short} is already in {tree}'s history - nothing to carry\n"
        ));
        return Ok(0);
    }
    let before = git(root, &["rev-parse", "HEAD"])?.1.trim().to_owned();
    let (rc, out) = git(root, &["-c", "core.editor=true", "cherry-pick", &sha])?;
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
            // nothing to resolve: the pick refused to start (a local edit in its way) or came out empty
            let why = lines(&out).join(" | ");
            return stopped(said, &format!("git cherry-pick said: {why}"));
        }
        match resolve_all(root, &unmerged)? {
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
        if rc != 0 {
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
    let (count, lacks) = missing(root, sha, before)?;
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
        format!("; both sides kept in {}", kept.join(", "))
    };
    said.say(&format!("carry: {short} carried into {tree} as {head} - verified: nothing in progress, nothing unmerged, nothing staged, its {count} non-spec file(s) in HEAD{both}\n"));
    Ok(0)
}

/// `l7r-gate land --carry <tree> [<commit>]`, run in `root`.
pub(super) fn cli(args: &[String], root: &Path) -> Reply {
    let mut said = Said {
        out: String::new(),
        err: String::new(),
    };
    let (Some(from), true) = (args.first().filter(|f| !f.is_empty()), args.len() <= 2) else {
        said.err = format!("{USAGE}\n");
        return said.reply(2);
    };
    let commit = args
        .get(1)
        .filter(|c| !c.is_empty())
        .map_or("HEAD", String::as_str);
    match carry(root, Path::new(from), commit, &mut said) {
        Ok(code) => said.reply(code),
        Err(why) => {
            said.warn(&format!("carry: {why}\n"));
            said.reply(2)
        }
    }
}

#[cfg(test)]
mod tests;
