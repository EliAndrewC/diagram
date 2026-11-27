//! THE PARKED HAMLET STAGES WAIT FOR THE GM (feature 449 T244; the GM 2026-11-21, `docs/gm-rulings.md`, "Stop before homesteads, and
//! talk first"): once everything else is ported, the session stops and talks with the GM before a parked stage's work starts. The stages
//! are what `rust/parked/src/` holds (a directory or a `.rs` file each: `homesteads`, `track`, `appurtenances`, `law`, `ways` on
//! 2026-11-22), read from the tree, so a stage moved back is no longer held. Three doors refuse to resume one without the GM's words in
//! `GM_RESUMED`: a write moving one into `rust/phases/src/` or declaring it in `rust/phases/src/lib.rs` (the guard's
//! `phase_source_hooks`), and a `make task-start` of a task whose line opens `phase: <a parked stage>` (the gate's `task_start`). The
//! escape taken at the task's start is written to `<git common dir>/parked-resumed.jsonl`, and a stage named there is held no longer;
//! the set-down guard's pickers skip a held task, and `make set-down` takes the stop where only held tasks are left (the gate's
//! `set_down`). The one reader of all three.

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

/// The escape: the GM's words resuming a parked stage.
pub const ESCAPE: &str = "GM_RESUMED";

/// The record of a stage resumed, in the git common directory.
pub const RESUMED: &str = "parked-resumed.jsonl";

/// The ruling, its date and where it is recorded, as every refusal prints it.
pub const RULING: &str = "The GM, 2026-11-21 (docs/gm-rulings.md, \"Stop before homesteads, and talk first\"): \"When you get to the point where you have ported everything else and then we're ready to go back to homesteads, then don't actually proceed. Why don't you go ahead and stop, and then we can talk more after everything else is done before you get started on that.\"";

fn re(pattern: &str) -> Regex {
    crate::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

// a task's stage: the box line's title opening `phase: <stage>` (444's T30-T33), or a line of its block that is `phase: <stage>`
static PHASE: LazyLock<Regex> = LazyLock::new(|| {
    re(r"(?m)^(?:- \[[ x]\] T\d+[a-z]? +|[ \t]*)(?:\[[^\]\n]*\] +)*phase:[ \t]*(\w+)")
});
// git by its name however spelled, behind any wrapper (451 T453: `\git mv` and `command git mv` were walked as git's, but their
// destination was not read, and a parked stage moved into the phases passed)
static GIT_MV: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r#"^\s*(?:\w+=\S*\s+|{})*{}git["']?\s+(?:-[Cc]\s+\S+\s+|--?\S+\s+)*mv\s"#,
        crate::spelled::WRAPPER_WORDS,
        crate::spelled::before("git")
    ))
});
static WORDS: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?<![\w-])GM_RESUMED=(?:"([^"]*)"|'([^']*)'|(\S+))"#));

/// The parked stages under `root`: each directory and `.rs` file of `rust/parked/src/` but the crate's own `lib.rs`, sorted.
#[must_use]
pub fn stages(root: &Path) -> Vec<String> {
    let Ok(dir) = std::fs::read_dir(root.join("rust/parked/src")) else {
        return Vec::new();
    };
    let mut found: Vec<String> = dir
        .filter_map(Result::ok)
        .filter_map(|e| {
            let name = e.file_name().to_string_lossy().into_owned();
            if e.path().is_dir() {
                Some(name)
            } else {
                name.strip_suffix(".rs").map(str::to_owned)
            }
        })
        .filter(|n| n != "lib" && n != "main")
        .collect();
    found.sort();
    found.dedup();
    found
}

/// The stage a task's line or block names (`phase: <stage>`), or None.
#[must_use]
pub fn stage_of(text: &str) -> Option<String> {
    PHASE
        .captures(text)
        .ok()
        .flatten()
        .and_then(|c| c.get(1).map(|m| m.as_str().to_owned()))
}

/// Whether `stage` was resumed with the GM's words, by a row of `<common>/parked-resumed.jsonl`.
#[must_use]
pub fn resumed(common: &Path, stage: &str) -> bool {
    std::fs::read_to_string(common.join(RESUMED)).is_ok_and(|text| {
        text.lines()
            .filter_map(|l| serde_json::from_str::<Value>(l).ok())
            .any(|row| row.get("stage").and_then(Value::as_str) == Some(stage))
    })
}

/// One row of a stage resumed, appended to `<common>/parked-resumed.jsonl`.
///
/// # Errors
/// The record that cannot be opened or written.
pub fn record(common: &Path, row: &Value) -> std::io::Result<()> {
    use std::io::Write as _;
    let mut file = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(common.join(RESUMED))?;
    file.write_all(format!("{}\n", crate::pyjson::dumps(row, None, true)).as_bytes())
}

/// The parked stage a task's text names and that no row has resumed, or None.
#[must_use]
pub fn held_task(root: &Path, common: &Path, text: &str) -> Option<String> {
    let stage = stage_of(text)?;
    (stages(root).contains(&stage) && !resumed(common, &stage)).then_some(stage)
}

/// The git common directory of the checkout at `root`, or `root/.git`.
#[must_use]
pub fn common_of(root: &Path) -> std::path::PathBuf {
    let said = crate::tool::ask(
        Path::new("/"),
        "git",
        &[
            "-C",
            &root.to_string_lossy(),
            "rev-parse",
            "--path-format=absolute",
            "--git-common-dir",
        ],
        "",
    );
    let out = said.out.trim();
    if said.ok() && !out.is_empty() {
        std::path::PathBuf::from(out)
    } else {
        root.join(".git")
    }
}

/// A write that resumes a parked stage: the checkout it is in, the stage, and whether it declares it in `lib.rs` (else moves it in).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Hit {
    /// The checkout's top level.
    pub root: String,
    /// The parked stage.
    pub stage: String,
    /// A declaration in `rust/phases/src/lib.rs`, not a file moved in.
    pub declares: bool,
}

fn declares(text: &str, stage: &str) -> bool {
    re(&format!(r"\bmod\s+{}\b", fancy_regex::escape(stage)))
        .is_match(text)
        .unwrap_or(false)
}

/// The checkout and the path within `rust/phases/src` an absolute path names ("" for the directory itself), or None.
fn in_phases(path: &str) -> Option<(&str, &str)> {
    let at = path.find("/rust/phases/src")?;
    let rest = &path[at + "/rust/phases/src".len()..];
    (rest.is_empty() || rest.starts_with('/')).then(|| (&path[..at], rest.trim_start_matches('/')))
}

/// What a write of the absolute `path` resumes: a parked stage's file under `rust/phases/src/`, or, in its `lib.rs`, a parked stage's
/// `mod` that `new` holds and `old` (the text it replaces) does not.
#[must_use]
pub fn write_hits(path: &str, new: &str, old: &str) -> Vec<Hit> {
    let Some((root, rest)) = in_phases(path) else {
        return Vec::new();
    };
    let parked = stages(Path::new(root));
    let hit = |stage: &String, declares: bool| Hit {
        root: root.to_owned(),
        stage: stage.clone(),
        declares,
    };
    if rest == "lib.rs" {
        return parked
            .iter()
            .filter(|s| declares(new, s) && !declares(old, s))
            .map(|s| hit(s, true))
            .collect();
    }
    let first = rest.split('/').next().unwrap_or_default();
    let stem = first.strip_suffix(".rs").unwrap_or(first);
    parked
        .iter()
        .filter(|s| !stem.is_empty() && s.as_str() == stem)
        .map(|s| hit(s, false))
        .collect()
}

/// What a shell command resumes: each write the tree walk finds ([`crate::tree::walk_judged`] from `start`) of a parked stage's file under
/// `rust/phases/src/`, of `lib.rs` in a segment naming a parked stage's `mod`, or of the directory itself in a segment naming a parked
/// stage's path (`rust/parked/src/<stage>`, or the bare stage where the segment stands in `rust/parked/src/`). A command naming none of
/// `parked`, `phases` and `lib.rs`, from outside `rust/phases`, is not walked.
#[must_use]
pub fn shell_hits(cmd: &str, start: &str, home: &str) -> Vec<Hit> {
    if !["parked", "phases", "lib.rs"]
        .iter()
        .any(|w| cmd.contains(w))
        && !start.contains("/rust/phases")
    {
        return Vec::new();
    }
    let walk = crate::tree::walk_judged(cmd, Some(start), "", home);
    let mut hits = Vec::new();
    for target in &walk.targets {
        let Some(at) = target.path.as_deref() else {
            continue;
        };
        // the segment from its command on, whole: `segment` is cut at 120 characters, which lost a long `git mv`'s destination (462 T371)
        let seg = target.head.as_str();
        // the walk lands a `git mv` where git runs; its destination is its last word, from there
        let path = if GIT_MV.is_match(seg).unwrap_or(false) {
            let last = seg.split_whitespace().last().unwrap_or_default();
            let last = last.trim_matches(|c| c == '"' || c == '\'');
            crate::tree::normpath(&if last.starts_with('/') {
                last.to_owned()
            } else {
                format!("{at}/{last}")
            })
        } else {
            at.to_owned()
        };
        let Some((root, rest)) = in_phases(&path) else {
            continue;
        };
        let found = if rest.is_empty() {
            let parked_dir = format!("{root}/rust/parked/src");
            let standing = start.starts_with(&parked_dir);
            stages(Path::new(root))
                .into_iter()
                .filter(|s| {
                    let named = re(&format!(
                        r"parked/src/(?:{}(?:\.rs)?\b|\*)",
                        fancy_regex::escape(s)
                    ));
                    let bare = re(&format!(
                        r"(?<![\w./-]){}(?:\.rs)?(?![\w.-])",
                        fancy_regex::escape(s)
                    ));
                    named.is_match(seg).unwrap_or(false)
                        || (standing && bare.is_match(seg).unwrap_or(false))
                })
                .map(|s| Hit {
                    root: root.to_owned(),
                    stage: s,
                    declares: false,
                })
                .collect()
        } else {
            // the whole command for a `mod` line: the walk's segment masks the quoted text an `echo` or a `sed` writes
            write_hits(&path, cmd, "")
        };
        for hit in found {
            if !hits.contains(&hit) {
                hits.push(hit);
            }
        }
    }
    hits
}

/// The GM's words a command gives in `GM_RESUMED=`, or None where it gives none: a heredoc's body is text written, never an escape
/// taken (T93's corpus holds one, this task's own line appended to `docs/gm-rulings.md`).
#[must_use]
pub fn words(cmd: &str) -> Option<String> {
    let cmd = crate::shape::strip_heredocs(cmd);
    // nor is one a quoted argument names (T93's corpus: a `make task-add TITLE="... GM_RESUMED=\"<...>\" ..."`)
    let spans = crate::shape::quoted_spans(&cmd);
    let found = WORDS.captures_iter(&cmd).map_while(Result::ok).find(|c| {
        c.get(0)
            .is_some_and(|m| !spans.iter().any(|&(a, b)| a <= m.start() && m.start() < b))
    })?;
    found
        .get(1)
        .or_else(|| found.get(2))
        .or_else(|| found.get(3))
        .map(|m| m.as_str().to_owned())
}

/// The refusal: what was refused, the ruling with its date, the stop and the escape.
#[must_use]
pub fn refusal(what: &str) -> String {
    format!(
        "BLOCKED: {what} - a parked hamlet stage (rust/parked/), and the GM stops the work there to talk first (feature 449 T244).\n\n\
{RULING}\n\n\
Stop instead: set the feature down, which this ruling lets through:  make set-down F=444 WHY=\"the parked stages wait for the GM, 2026-11-21\"\n\
Only once the GM has resumed the stage, quote his words, verbatim from a message he wrote this session:\n  \
GM_RESUMED=\"<the GM's words resuming it>\" make task-start F=444 T=<the stage's task>   (recorded; the stage's moves and lib.rs line then pass)\n  \
a shell move alone: GM_RESUMED=\"<the GM's words>\" git mv rust/parked/src/<stage>.rs rust/phases/src/\n"
    )
}

#[cfg(test)]
mod tests;
