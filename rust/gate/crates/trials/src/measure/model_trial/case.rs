//! `prepare` and `snapshot`: a case's own clone, its frozen inputs and its rebuilt review snapshots.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};
use serde_json::{json, Value};

use super::{
    at, bundle_root, compiled, newest, outside_paths, read, records_of, text_of, Run, Trial, Words,
    REFLOG, SONNET,
};
use crate::measure::text_err;
use crate::plan::pretty;

const SNAP_SUFFIXES: [&str; 5] = [".json", ".svg", ".png", ".html", ".notes.md"];
const DISPATCH_END: &str = "as your last act, and quote the line it prints.";

static MODEL_LINE: LazyLock<Regex> = LazyLock::new(|| compiled(r"(?m)^model:.*$"));
static OMIT_LINE: LazyLock<Regex> = LazyLock::new(|| compiled(r"(?m)^omitClaudeMd:.*\n?"));
static A_CLONE: LazyLock<Regex> = LazyLock::new(|| compiled(r"/diagram/\.clones/([\w-]+)"));
static SNAPSHOT_UNIT: LazyLock<Regex> =
    LazyLock::new(|| compiled(r"/diagram/\.clones/[\w-]+/\.git/review-snapshot/([\w.-]+)"));
static CHECKOUT: LazyLock<Regex> =
    LazyLock::new(|| compiled(r"/diagram/\.clones/[\w-]+(?!/\.git/)"));
static MIRROR: LazyLock<Regex> = LazyLock::new(|| {
    compiled(
        r"(?<![\w.-])/diagram(?=/(?:\.claude|specs|scripts|docs|research|l7r|pool|tests|dev)\b)",
    )
});
static LINE_NUMBER: LazyLock<Regex> = LazyLock::new(|| compiled(r"^\s*\d+\t"));
static ANY_CLONE: LazyLock<Regex> = LazyLock::new(|| compiled(r"/diagram/\.clones/[\w-]+"));

/// `subject` with every match of `re` replaced by `by`, taken literally.
fn literally(re: &Regex, subject: &str, by: &str) -> String {
    re.replace_all(subject, |_: &Captures| by.to_owned())
        .into_owned()
}

/// How a case is asked to be built.
pub struct Asked {
    pub model: String,
    pub at_head: bool,
    pub omit: Option<bool>,
    pub as_subagent: bool,
    pub at_commit: String,
}

impl Asked {
    pub fn from_words(w: &Words) -> Self {
        Self {
            model: w.get("--model").unwrap_or(SONNET).to_owned(),
            at_head: w.has("--head"),
            omit: w.get("--omit-claude-md").map(|v| v == "yes"),
            as_subagent: w.has("--as-subagent"),
            at_commit: w.get("--at").unwrap_or("").to_owned(),
        }
    }
}

/// A frontmatter's head and the rest; a text with no closing line is all head.
fn split_head(text: &str) -> (&str, &str) {
    text.find("\n---\n")
        .map_or((text, ""), |i| text.split_at(i))
}

/// The tested model in the agent file's frontmatter (the case's copy).
pub fn set_model(agent_file: &Path, model: &str) -> Result<(), String> {
    let text = std::fs::read_to_string(agent_file)
        .map_err(|e| format!("{}: {e}", agent_file.display()))?;
    let (head, rest) = split_head(&text);
    let line = format!("model: {model}");
    let head = if MODEL_LINE.is_match(head).unwrap_or(false) {
        literally(&MODEL_LINE, head, &line)
    } else {
        format!("{head}\n{line}")
    };
    std::fs::write(agent_file, head + rest).map_err(text_err)
}

/// `omitClaudeMd: true` in the agent file's frontmatter, or none (the case's copy) - feature 383 amendment 6, plan D34.
pub fn set_field(agent_file: &Path, omit: bool) -> Result<(), String> {
    let text = std::fs::read_to_string(agent_file)
        .map_err(|e| format!("{}: {e}", agent_file.display()))?;
    let (head, rest) = split_head(&text);
    let head = literally(&OMIT_LINE, head, "");
    let head = head.trim_end_matches('\n');
    let field = if omit { "\nomitClaudeMd: true" } else { "" };
    std::fs::write(agent_file, format!("{head}{field}{rest}")).map_err(text_err)
}

/// A clone's HEAD at a moment, from its reflog ("" when the reflog does not reach back that far).
pub fn clone_head_at(clone: &Path, when: f64) -> String {
    let log = crate::cohort::git(
        clone,
        &["log", "-g", "--date=unix", "--format=%H %gd", "HEAD"],
    )
    .1;
    for line in log.lines() {
        let (sha, rest) = line.split_once(' ').unwrap_or((line, ""));
        let seconds = REFLOG
            .captures(rest)
            .ok()
            .flatten()
            .and_then(|c| c[1].parse::<f64>().ok());
        if seconds.is_some_and(|s| s <= when) {
            return sha.to_owned();
        }
    }
    String::new()
}

fn must_git(root: &Path, args: &[&str]) -> Result<String, String> {
    let (fine, out) = crate::cohort::git(root, args);
    if fine {
        Ok(out.trim().to_owned())
    } else {
        Err(format!(
            "git {} failed in {}",
            args.join(" "),
            root.display()
        ))
    }
}

/// A clone of its own, not a worktree: a check's last act writes review state into its git directory, and a worktree's is this clone's - a trial
/// would overwrite a real verdict.
fn own_clone(source: &Path, tree: &Path, commit: &str) -> Result<(), String> {
    if !tree.is_dir() {
        let (from, to) = (source.display().to_string(), tree.display().to_string());
        must_git(
            source,
            &["clone", "-q", "--shared", "--no-checkout", &from, &to],
        )?;
        must_git(tree, &["checkout", "-q", "--detach", commit])?;
    }
    Ok(())
}

/// `src` copied over `dest`, file by file.
pub fn copy_tree(src: &Path, dest: &Path) -> std::io::Result<()> {
    std::fs::create_dir_all(dest)?;
    for entry in std::fs::read_dir(src)? {
        let path = entry?.path();
        let to = dest.join(path.file_name().unwrap_or_default());
        if path.is_dir() {
            copy_tree(&path, &to)?;
        } else {
            std::fs::copy(&path, &to)?;
        }
    }
    Ok(())
}

fn text_path(p: &Path) -> String {
    p.display().to_string()
}

/// What a prompt became: its text, and the outside paths gone or changed since the run.
struct Frozen {
    prompt: String,
    missing: Vec<String>,
    stale: Vec<String>,
    rebuild: Vec<String>,
}

impl Trial {
    /// The clone a case's commit is held by, at the run's start, fetched here so this history has it.
    fn fetched_from(&self, home: &Path, started: f64) -> Option<String> {
        let at = clone_head_at(home, started);
        if at.is_empty() {
            return None;
        }
        let (mine, from) = (self.clone.clone(), text_path(home));
        let _ = crate::cohort::git(&mine, &["fetch", "-q", &from, &at]);
        Some(at)
    }

    fn sibling(&self, name: &str) -> Option<PathBuf> {
        let there = self.clone.parent()?.join(name);
        there.join(".git").exists().then_some(there)
    }

    /// The commit a case reads: the recording clone's HEAD at the time, the HEAD of a clone the run judged, or a commit named by hand.
    fn commit_for(&self, run: &Run, asked: &Asked) -> Result<String, String> {
        let mut commit = must_git(&self.clone, &["rev-parse", "HEAD"])?;
        if !asked.at_head {
            let started = at(&run.started);
            let cwd = run
                .records
                .iter()
                .find_map(|r| r["cwd"].as_str().filter(|s| !s.is_empty()))
                .unwrap_or("");
            let clone_of = |text: &str| {
                A_CLONE
                    .captures(text)
                    .ok()
                    .flatten()
                    .map(|c| c[1].to_owned())
            };
            let home = clone_of(cwd)
                .and_then(|n| self.sibling(&n))
                .unwrap_or_else(|| self.clone.clone());
            commit = self.fetched_from(&home, started).unwrap_or(commit);
            // A RUN THAT JUDGED ANOTHER CLONE judged that clone's HEAD at the time, unlanded then
            let other = clone_of(&run.prompt).and_then(|n| self.sibling(&n));
            commit = other
                .and_then(|o| self.fetched_from(&o, started))
                .unwrap_or(commit);
        }
        if !asked.at_commit.is_empty() {
            commit = must_git(&self.clone, &["rev-parse", &asked.at_commit])?;
        }
        Ok(commit)
    }

    /// Make the prompt's paths the case's own: snapshots rebuilt in the case's git directory, bundles frozen into `inputs/`, checkout paths rewritten.
    fn freeze(run: &Run, out: &Path, tree: &Path) -> Result<Frozen, String> {
        let mut prompt = run.prompt.clone();
        let mut rebuild: Vec<String> = SNAPSHOT_UNIT
            .captures_iter(&prompt)
            .flatten()
            .map(|c| c[1].to_owned())
            .collect();
        rebuild.sort();
        rebuild.dedup();
        for unit in &rebuild {
            let pattern = compiled(&format!(
                r"/diagram/\.clones/[\w-]+/\.git/review-snapshot/{}",
                fancy_regex::escape(unit)
            ));
            prompt = literally(
                &pattern,
                &prompt,
                &text_path(&tree.join(".git/review-snapshot").join(unit)),
            );
        }
        let (mut missing, mut stale) = (Vec::new(), Vec::new());
        let started = at(&run.started);
        for path in outside_paths(&prompt) {
            let src = Path::new(&path);
            if !src.exists() {
                missing.push(path);
                continue;
            }
            // A BUNDLE IS FROZEN INTO THE CASE: only a bundle not written since the recorded run started is what that run read
            let root = bundle_root(src).to_owned();
            if newest(&root) > started {
                stale.push(path.clone());
            }
            let dest = out
                .join("inputs")
                .join(root.file_name().unwrap_or_default());
            if !dest.exists() {
                copy_tree(&root, &dest).map_err(text_err)?;
            }
            prompt = prompt.replace(&text_path(&root), &text_path(&dest));
        }
        // the frozen inputs first, the checkout's paths after: a rewrite into the case's clone must not be mistaken for an outside input
        let there = text_path(tree);
        let prompt = literally(&MIRROR, &literally(&CHECKOUT, &prompt, &there), &there);
        Ok(Frozen {
            prompt,
            missing,
            stale,
            rebuild,
        })
    }

    fn agent_copies(&self, tree: &Path, agent: &str, asked: &Asked) -> Result<(), String> {
        copy_tree(
            &self.clone.join(".claude/agents"),
            &tree.join(".claude/agents"),
        )
        .map_err(text_err)?;
        let file = tree.join(".claude/agents").join(format!("{agent}.md"));
        set_model(&file, &asked.model)?;
        asked.omit.map_or(Ok(()), |omit| set_field(&file, omit))
    }

    /// # Errors
    ///
    /// Where what it reads, writes or runs fails: the error says which and why.
    pub fn prepare(
        &self,
        transcript: &Path,
        out: &Path,
        asked: &Asked,
    ) -> Result<(String, i32), String> {
        let run = read(transcript);
        std::fs::create_dir_all(out).map_err(text_err)?;
        let commit = self.commit_for(&run, asked)?;
        let tree = out.join("tree");
        own_clone(&self.clone, &tree, &commit)?;
        self.agent_copies(&tree, &run.agent, asked)?;
        let frozen = Self::freeze(&run, out, &tree)?;
        let meta = json!({"agent": run.agent, "recorded": text_path(transcript), "started": run.started, "commit": commit, "model": asked.model,
            "missing": frozen.missing, "stale": frozen.stale, "rebuild": frozen.rebuild, "omitClaudeMd": asked.omit, "as_subagent": asked.as_subagent});
        let writes = [
            ("prompt.txt", frozen.prompt.clone()),
            ("recorded-reply.md", run.reply.clone()),
            ("meta.json", pretty(&meta).trim_end().to_owned()),
        ];
        for (name, body) in writes {
            std::fs::write(out.join(name), body).map_err(text_err)?;
        }
        let mut shown = format!(
            "{} @ {} ({}) -> {}\n",
            run.agent,
            &commit[..commit.len().min(9)],
            run.started.chars().take(16).collect::<String>(),
            out.display()
        );
        if !frozen.missing.is_empty() {
            let _ = writeln!(
                shown,
                "  MISSING (not a fair re-run): {}",
                frozen.missing.join(", ")
            );
        }
        if !frozen.stale.is_empty() {
            let _ = writeln!(
                shown,
                "  CHANGED SINCE the run (not a fair re-run): {}",
                frozen.stale.join(", ")
            );
        }
        let code = i32::from(!frozen.missing.is_empty() || !frozen.stale.is_empty());
        Ok((shown, code))
    }
}

/// Draw map or sheet `name` in a checkout (renders are not tracked); its folder, or none.
fn render(tree: &Path, name: &str) -> Option<PathBuf> {
    let file = format!("{name}.gen.py");
    let mut found: Vec<PathBuf> = std::fs::read_dir(tree.join("pool"))
        .ok()?
        .flatten()
        .map(|kind| kind.path().join(name).join(&file))
        .filter(|p| p.is_file())
        .collect();
    found.sort();
    let generator = found.first()?;
    let rel = generator
        .strip_prefix(tree)
        .unwrap_or(generator)
        .display()
        .to_string();
    let _ = Command::new("make")
        .args(["--no-print-directory", "map", &format!("GEN={rel}")])
        .current_dir(tree)
        .output();
    generator.parent().map(Path::to_owned)
}

/// A file's text as the recorded agent read it whole (its Read result, line numbers stripped), or "".
pub fn read_back(records: &[Value], suffix: &str) -> String {
    let blocks = |kind: &'static str| {
        records
            .iter()
            .filter(move |r| r["type"] == kind)
            .filter_map(|r| r["message"]["content"].as_array())
            .flatten()
    };
    let wanted: Vec<&Value> = blocks("assistant")
        .filter(|b| {
            b["type"] == "tool_use"
                && b["name"] == "Read"
                && b["input"]["file_path"]
                    .as_str()
                    .unwrap_or("")
                    .ends_with(suffix)
        })
        .map(|b| &b["id"])
        .collect();
    blocks("user")
        .filter(|b| b["type"] == "tool_result")
        .find(|b| wanted.contains(&&b["tool_use_id"]))
        .map_or_else(String::new, |b| {
            let body = text_of(&b["content"]);
            body.lines()
                .map(|l| literally(&LINE_NUMBER, l, ""))
                .collect::<Vec<_>>()
                .join("\n")
                + "\n"
        })
}

/// The dispatch prompt as the recorded agent saw it: its Read, or any tool output holding the whole prompt (a `cat` serves as well as a Read).
pub fn read_dispatch(transcript: &Path, unit: &str) -> String {
    let records = records_of(transcript);
    let text = read_back(&records, &format!("/{unit}/dispatch.md"));
    if !text.is_empty() {
        return text;
    }
    let mark = format!("UNIT: {unit}");
    for block in records
        .iter()
        .filter_map(|r| r["message"]["content"].as_array())
        .flatten()
    {
        let body = text_of(&block["content"]);
        if block["type"] != "tool_result" {
            continue;
        }
        if let Some(i) = body.find(&mark) {
            if let Some(j) = body[i..].find(DISPATCH_END) {
                return format!("{}\n", &body[i..i + j + DISPATCH_END.len()]);
            }
        }
    }
    String::new()
}

impl Trial {
    fn rebuild_side(tree: &Path, name: &str, side: &str, dest: &Path) -> bool {
        let Some(folder) = render(tree, name) else {
            return false;
        };
        let to = dest.join(side);
        let _ = std::fs::create_dir_all(&to);
        for path in std::fs::read_dir(&folder)
            .into_iter()
            .flatten()
            .flatten()
            .map(|e| e.path())
        {
            let file = path
                .file_name()
                .unwrap_or_default()
                .to_string_lossy()
                .into_owned();
            if SNAP_SUFFIXES.iter().any(|s| file.ends_with(s)) {
                let _ = std::fs::copy(&path, to.join(&file));
            }
        }
        true
    }

    /// Rebuild each review snapshot the recorded run read: the map drawn at the case's commit (`clone/`) and at main's commit of the time (`main/`),
    /// and the dispatch prompt as the recorded agent read it.
    ///
    /// # Errors
    ///
    /// Where what it reads, writes or runs fails: the error says which and why.
    pub fn snapshot(&self, out: &Path) -> Result<(String, i32), String> {
        let meta: Value = std::fs::read_to_string(out.join("meta.json"))
            .ok()
            .and_then(|t| serde_json::from_str(&t).ok())
            .ok_or("meta.json does not read")?;
        let (tree, main_tree) = (out.join("tree"), out.join("main-tree"));
        let commit = meta["commit"].as_str().unwrap_or("");
        let mirror = self
            .clone
            .parent()
            .and_then(Path::parent)
            .unwrap_or(&self.clone);
        // main's tip AT THE TIME, from the mirror's reflog: a commit's own date says when it was made, not when it landed
        let at_main = clone_head_at(mirror, at(meta["started"].as_str().unwrap_or("")));
        let main_commit = if at_main.is_empty() { commit } else { &at_main };
        own_clone(&self.clone, &main_tree, main_commit)?;
        let (mut shown, mut code) = (String::new(), 0);
        for unit in meta["rebuild"]
            .as_array()
            .into_iter()
            .flatten()
            .filter_map(Value::as_str)
        {
            let name = unit.rsplit("--").next().unwrap_or(unit);
            let dest = tree.join(".git/review-snapshot").join(unit);
            for (side, checkout) in [("clone", &tree), ("main", &main_tree)] {
                if !Self::rebuild_side(checkout, name, side, &dest) {
                    let _ = writeln!(shown, "{unit}: no {name} in the {side} checkout");
                    code = 1;
                }
            }
            let text = read_dispatch(Path::new(meta["recorded"].as_str().unwrap_or("")), unit);
            if !text.is_empty() {
                let _ = std::fs::create_dir_all(&dest);
                let _ = std::fs::write(
                    dest.join("dispatch.md"),
                    literally(&ANY_CLONE, &text, &text_path(&tree)),
                );
            }
            let (a, b) = (
                &commit[..commit.len().min(9)],
                &main_commit[..main_commit.len().min(9)],
            );
            let _ = writeln!(
                shown,
                "{unit}: rebuilt at {a} (main {b}){}",
                if text.is_empty() {
                    "; no dispatch.md read in the recorded run"
                } else {
                    ""
                }
            );
        }
        // THE GATE WAS GREEN on this content when the recorded run was dispatched; a case's own clone has no gate record, and the reviewer's contract
        // stops on a red `make review-paired-gate`. The stamp is written in the case's clone alone.
        let _ = Command::new("scripts/gates/l7r-gate.sh")
            .args(["stamp", "--write", "diagram"])
            .current_dir(&tree)
            .output();
        Ok((shown, code))
    }
}
