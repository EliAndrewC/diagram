//! WHOSE A RECORD OR POP-UP PASS IS (feature 451 T157). WHY: T147 left another open task's plan review to that task's landing, and
//! every other owed pass still refused every landing - so 449 T252, CLEAR and committed, was refused on 21 quote-check, record-format,
//! source-reader, translation-check and source-applicability passes of two other started bundles' page sessions, and 451 T153 on
//! several (observed 2026-11-22), passes `make ledger-owed WRITE=` cannot write as the landing session's and `LEDGER_ROWS_OK` does not
//! reach in the first pass. Measured 2026-11-22 (this clone's 26 owed record and pop-up passes of the day, each agent's meta file and
//! session read): 25 were named by a page session's brief (`t283-checks.md`, `t275-checks.md`, `t197-g1-checks.md`, ...), one by its
//! builder's description (`449 T260, T282-T287: the shrine and record bundle`); the prompts' bodies named other tasks besides
//! (a modal-form pass T284, T260, T289 and T300 at once, building-review passes the landed T276), so a body is never read.
//!
//! So a pass is that task's, owed at its own landing or written by its own session, where the first of these names a task - the order
//! 449 T258's `check_bundle_hooks/own.rs` reads a live dispatch in, read here after the fact, since `own.rs` reads a hook's payload and
//! `L7R_PAGE_SESSION` and lives in the guard, which no gate crate may name (`check guard-deps`):
//! - its OWN WORDS: the logged subject (its prompt's first line, cut at 100 characters) - a task id, the feature the number before it,
//!   or a check bundle's `-t<n>` suffix (`q-0229-quote-check-t283`) - else its meta file's `description`;
//! - its BUILDER: the agent its meta names as `parentAgentId`, read as the Stop hook reads a builder (`set_down_hooks::builder_brief`, a
//!   bundle's every member);
//! - its PAGE SESSION: its transcript's session directory looked up in the clone's `page-sessions/index.txt`, the brief's
//!   `specs/<feature>/` path and its first line's task, else its file name's (`t283-checks.md`).
//!
//! A source naming only a task never started in its feature gives way to the next (451 T167): a page session's bundle carries its
//! session's letter (`q-0123-quote-check-t330a`, read as T330a), and the reading stopped there, short of the brief's T330 - a 451
//! landing refused on it (replayed 2026-11-23 on the landing's tree af418b90c5 and the pass log as it stood at 02:33Z).
//!
//! Since 451 T305 (`pool.rs`) a pass none of its own words ties is the task's that HELD THE POOL TREE it was dispatched from, when it
//! was dispatched - before its builder and its page session are read - and that hold stands for the task's start: a pool builder's
//! task is started in the clone only as it lands.
//!
//! A task named without its feature takes the feature that started it (`event_log_hooks::started`). The pass is left only where that
//! task is STARTED (`task-starts.jsonl`) and has an OPEN line (`- [ ] T<n>`) in its feature's `tasks.md` (451 T311, the rule T231 gave
//! plan reviews: read as "ticked in neither file", a started task whose line is gone - renumbered, never filed there - had its passes
//! left to a landing that never comes), and none of the tasks named is one this landing lands; a pass naming nothing, a task never
//! started, one with no open line (ticked, withdrawn, built inside another, absent), or one of the landing's own still refuses here.

use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::guards::event_log_hooks::{common_git_dir, started, starts, Start};
use l7r_shared::guards::set_down_hooks::builder_brief;
use serde_json::Value;

use super::super::settle::Transcripts;
use super::super::{text, Pass};
use super::pool::{first_record, Holds};
use super::{open, re, Landing, Side};

/// A task id, and the feature number before it where one stands there (`own.rs`'s `NAMED`).
static NAMED: LazyLock<Regex> = LazyLock::new(|| re(r"(?:\b(\d{3})\s+)?\b(T\d+[a-z]?)\b"));
/// A check bundle's directory named for its task: `/tmp/l7r-check/q-0229-quote-check-t283/`.
static BUNDLE: LazyLock<Regex> = LazyLock::new(|| re(r"/l7r-check/[^/\s]*-t(\d+[a-z]?)/"));
/// A page-session brief's file name: `t283-checks.md`.
static BRIEF_FILE: LazyLock<Regex> = LazyLock::new(|| re(r"^t(\d+[a-z]?)-"));

/// The tasks a pass serves: the feature named (a number, a specs directory's name, or none) and its tasks.
struct Named {
    feature: Option<String>,
    tasks: Vec<String>,
    /// read from the pool: the tasks held the tree the pass was dispatched from, which stands for their start (451 T305)
    held: bool,
}

/// What a landing reads once to say whose each pass is.
pub(super) struct Clues<'a> {
    repo: &'a Path,
    transcripts: Transcripts<'a>,
    starts: Vec<Start>,
    sessions: String,
    pool: Holds,
}

impl<'a> Clues<'a> {
    pub(super) fn new(repo: &'a Path, transcripts: &'a Path) -> Self {
        let sessions =
            std::fs::read_to_string(common_git_dir(repo).join("page-sessions/index.txt"))
                .unwrap_or_default();
        Self {
            repo,
            transcripts: Transcripts::new(transcripts),
            starts: starts(repo),
            sessions,
            pool: Holds::read(&common_git_dir(repo)),
        }
    }

    /// Whose landing or session owes this pass's row: the landing asking, where a task it names is one of the landing's; another
    /// started (or tree-holding), open task's (`<feature> <task>`); else nobody's, and it is owed here.
    pub(super) fn side(&mut self, p: &Pass, landing: &Landing) -> Side {
        let Some((feature, named)) = self.named(p) else {
            return Side::Unowned;
        };
        if landing.feature == feature
            && named
                .tasks
                .iter()
                .any(|t| landing.tasks.contains(&t.as_str()))
        {
            return Side::Own;
        }
        // started (or tree-holding) and its line open in tasks.md (451 T311, T231's rule): a task ticked Withdrawn, ticked built inside
        // another, or with no line here has no landing left to write the row
        let left_to = |t: &&String| {
            (named.held || self.starts.iter().any(|(f, s, _)| *f == feature && s == *t))
                && open(self.repo, &feature, t)
        };
        named
            .tasks
            .iter()
            .find(left_to)
            .map_or(Side::Unowned, |t| Side::Left(format!("{feature} {t}")))
    }

    /// The feature a source's tasks are served in - its number's specs directory, else the feature that started its first task - where
    /// one of them was started there; None for a source naming no task started (451 T167).
    fn served(&self, n: Named) -> Option<(String, Named)> {
        let feature = match &n.feature {
            Some(f) => self.feature_dir(f)?,
            None => started(&self.starts, n.tasks.first()?, None)?,
        };
        let begun = n.held
            || n.tasks
                .iter()
                .any(|t| self.starts.iter().any(|(f, s, _)| *f == feature && s == t));
        begun.then_some((feature, n))
    }

    /// The first source that names a STARTED task, with its feature: the subject, the meta's description, the builder, the page
    /// session's brief. A source naming only a task never started gives way to the next (451 T167): the bundle
    /// `q-0123-quote-check-t330a` carries its page session's letter, read as T330a, and stopped the reading short of its brief's T330.
    fn named(&mut self, p: &Pass) -> Option<(String, Named)> {
        if let Some(hit) = words(text(p, "subject")).and_then(|n| self.served(n)) {
            return Some(hit);
        }
        let transcript = self.transcripts.find(text(p, "agent"))?;
        let meta = meta_of(&transcript);
        let field = |k: &str| {
            meta.get(k)
                .and_then(Value::as_str)
                .unwrap_or_default()
                .to_owned()
        };
        let dir = transcript
            .parent()
            .map(Path::to_path_buf)
            .unwrap_or_default();
        words(&field("description"))
            .and_then(|n| self.served(n))
            .or_else(|| {
                self.pooled(p, &transcript, &dir, &field("parentAgentId"))
                    .and_then(|n| self.served(n))
            })
            .or_else(|| {
                builder_brief(&dir, &field("parentAgentId")).and_then(|(feature, tasks)| {
                    self.served(Named {
                        feature: Some(feature),
                        tasks,
                        held: false,
                    })
                })
            })
            .or_else(|| self.page_session(&dir).and_then(|n| self.served(n)))
    }

    /// The tasks that held, when the pass's transcript opens, the pool tree its subject names, else the one the first line of its
    /// dispatching agent's brief names (451 T305, `pool.rs`); None where neither names a tree held then.
    fn pooled(&self, p: &Pass, transcript: &Path, dir: &Path, parent: &str) -> Option<Named> {
        let at = first_record(transcript).0?;
        let brief = first_record(&dir.join(format!("agent-{parent}.jsonl"))).1;
        let (feature, tasks) = self
            .pool
            .holder(text(p, "subject"), at)
            .or_else(|| self.pool.holder(&brief, at))?;
        Some(Named {
            feature: Some(feature),
            tasks,
            held: true,
        })
    }

    /// A feature number or directory name as this repository's specs directory.
    fn feature_dir(&self, named: &str) -> Option<String> {
        if self.repo.join("specs").join(named).is_dir() {
            return Some(named.to_owned());
        }
        let prefix = format!("{named}-");
        let mut hits: Vec<String> = std::fs::read_dir(self.repo.join("specs"))
            .into_iter()
            .flatten()
            .flatten()
            .map(|e| e.file_name().to_string_lossy().into_owned())
            .filter(|n| n.starts_with(&prefix))
            .collect();
        (hits.len() == 1).then(|| hits.remove(0))
    }

    /// The page session whose agent wrote `dir` (`<projects>/<project>/<session>/subagents`): its brief's feature and task.
    fn page_session(&self, dir: &Path) -> Option<Named> {
        let sid = dir.parent()?.file_name()?.to_string_lossy().into_owned();
        let brief = self.sessions.lines().rev().find_map(|l| {
            l.split_once(' ')
                .filter(|(id, _)| *id == sid)
                .map(|(_, path)| PathBuf::from(path.trim()))
        })?;
        let parts: Vec<String> = brief
            .components()
            .map(|c| c.as_os_str().to_string_lossy().into_owned())
            .collect();
        let feature = parts
            .get(parts.iter().rposition(|p| p == "specs")? + 1)?
            .clone();
        let body = std::fs::read_to_string(&brief).unwrap_or_default();
        let head = body.lines().next().unwrap_or_default();
        let name = brief
            .file_name()
            .map(|n| n.to_string_lossy().into_owned())
            .unwrap_or_default();
        let task = group(&NAMED, head, 2)
            .or_else(|| group(&BRIEF_FILE, &name, 1).map(|n| format!("T{n}")))?;
        Some(Named {
            feature: Some(feature),
            tasks: vec![task],
            held: false,
        })
    }
}

/// The capture `at` of `pattern`'s first match in `text`.
fn group(pattern: &Regex, text: &str, at: usize) -> Option<String> {
    pattern
        .captures(text)
        .ok()
        .flatten()?
        .get(at)
        .map(|m| m.as_str().to_owned())
}

/// The first task `text` names, with the feature number before it, else its check bundle's task.
fn words(text: &str) -> Option<Named> {
    if let Some(c) = NAMED.captures(text).ok().flatten() {
        return Some(Named {
            feature: c.get(1).map(|m| m.as_str().to_owned()),
            tasks: vec![c[2].to_owned()],
            held: false,
        });
    }
    group(&BUNDLE, text, 1).map(|n| Named {
        feature: None,
        tasks: vec![format!("T{n}")],
        held: false,
    })
}

/// The meta file beside a transcript, `{}` where it is missing or unreadable.
fn meta_of(transcript: &Path) -> Value {
    let path = transcript.with_extension("meta.json");
    std::fs::read_to_string(path)
        .ok()
        .and_then(|t| serde_json::from_str(&t).ok())
        .unwrap_or(Value::Null)
}
