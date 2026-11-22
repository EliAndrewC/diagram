//! `gate-write-hooks` (feature 385 T02, plan D13; ported from the shell of the same name, feature 449 T024): NO WRITE TO THE WORKING TREE
//! WHILE THIS TREE'S OWN `make done` RUNS. A gate ends by checking that the tree did not move while it ran; a session voided two gates
//! this way, the second an hour after the round arbiter named the slip (the GM, 2026-10-17: "a guard, not a reminder"). A change the gate
//! does not see passes, asked of the gate's own `l7r-gate preflight --tree-check` (feature 405 T41). `GATE_WRITE_OK` with a reason is the
//! escape. (Feature 426 T10's refusal while `make cache-audit` ran left with that target, deleted by 449 T218: nothing runs it, so the
//! branch watched for a process that cannot exist - removed by 449 T223.)
//!
//! Plan T024's decisions: (a) the guard and `own-make.sh`'s question in-process, by pid; (b) `preflight.py` is a phase-2 piece, asked by
//! path, only while a gate runs.

use std::path::{Path, PathBuf};
use std::sync::LazyLock;
use std::time::Duration;

use fancy_regex::Regex;

use crate::guards::finished_run_hooks::runs::{realpath, Procs};
use crate::guards::make_only_hooks::interp;
use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;
use crate::shared::tool::{ask, ask_within};
use crate::shared::tree::program::writes_computed;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "gate-write-hooks",
    events: &["PreToolUse"],
    matcher: "Bash|Edit|Write|NotebookEdit",
    decide,
};

const FILE_TOOLS: [&str; 3] = ["Edit", "Write", "NotebookEdit"];

/// `git commit` or `git add` - the subcommand, past git's own options: `git notes add`, `git worktree add` and `git remote add`
/// write no index or HEAD (451 T33, a HEAD false refusal found by its gate replay, measured 2026-11-20: the word anywhere in the
/// segment - `git worktree add`, a Python `moved.add(` - refused them).
static GIT_WRITE: LazyLock<Regex> = LazyLock::new(|| {
    crate::shared::regex::build(
        r"(?:\A|(?<=[;&|]))[^;&|]*?\bgit(?:\s+(?:-[Cc]\s+\S+|-\S+))*\s+(commit|add)\b",
    )
    .unwrap_or_else(|e| unreachable!("{e}"))
});
/// A function the program defines, by its name: `def name(`.
static OWN_DEF: LazyLock<Regex> = LazyLock::new(|| {
    crate::shared::regex::build(r"\bdef\s+([A-Za-z_]\w*)\s*\(")
        .unwrap_or_else(|e| unreachable!("{e}"))
});

/// The program with every string literal handed to a function of its own blanked to `$` (451 T33, window#72 - round 2 of its
/// plan review ruled the fail-closed count NOT LEGITIMATE, measured 2026-11-20: `edit("vegetation.html", ...)` writes
/// `f"{R}/{rel}"`, another tree, and was refused for the literal where the shell stands). The function places the literal where
/// the gate does not read, so it is a path not resolved and fails open, as an f-string's placeholder does - a literal holding `$`
/// is no path to `program_names`. The `def`s and calls are found, and a call's arguments read to its closing parenthesis, on
/// `masked`'s copy, so a `def` or a parenthesis inside a string or a comment is neither (window#220's `s.index("def
/// brook_skirt(")` named a function and opened a call that blanked every literal after it); a span that never closes is
/// blanked to the end, failing open. Make-only, fail-closed, still counts such a literal.
fn own_args(body: &str) -> String {
    let mask = masked(body.as_bytes());
    // every byte replaced is a whole character's (a string's content, a comment), so the copy stays UTF-8
    let text = String::from_utf8(mask.clone()).unwrap_or_else(|e| unreachable!("{e}"));
    let names: Vec<&str> = OWN_DEF
        .captures_iter(&text)
        .map_while(Result::ok)
        .filter_map(|c| c.get(1).map(|m| m.as_str()))
        .collect();
    if names.is_empty() {
        return body.to_owned();
    }
    let call = crate::shared::regex::build(&format!(r"(?<![\w.])(?:{})\s*\(", names.join("|")))
        .unwrap_or_else(|e| unreachable!("{e}"));
    let mut out = body.as_bytes().to_vec();
    for m in call.find_iter(&text).map_while(Result::ok) {
        let mut depth = 1;
        for (&b, o) in mask.iter().zip(out.iter_mut()).skip(m.end()) {
            match b {
                b'(' => depth += 1,
                b')' => depth -= 1,
                STRING => *o = b'$',
                _ => {}
            }
            if depth == 0 {
                break;
            }
        }
    }
    String::from_utf8(out).unwrap_or_else(|e| unreachable!("{e}"))
}

/// `masked`'s mark on a byte of a string's content.
const STRING: u8 = 1;

/// The program byte for byte with each string's content marked `STRING` and each comment blanked: quotes single, double and
/// triple, a backslash's escape, and a single-quoted string the line ends before it closes.
fn masked(body: &[u8]) -> Vec<u8> {
    let mut out = body.to_vec();
    let mut i = 0;
    while let Some(&ch) = body.get(i) {
        match ch {
            b'#' => {
                while let Some(o) = out.get_mut(i).filter(|o| **o != b'\n') {
                    *o = b' ';
                    i += 1;
                }
            }
            q @ (b'\'' | b'"') => {
                let triple = body.get(i + 1..i + 3) == Some(&[q, q][..]);
                i += if triple { 3 } else { 1 };
                while let Some(&b) = body.get(i) {
                    let closes = b == q && (!triple || body.get(i + 1..i + 3) == Some(&[q, q][..]));
                    if closes || (!triple && b == b'\n') {
                        i += if closes && triple { 2 } else { 0 };
                        break;
                    }
                    let skip = if b == b'\\' { 2 } else { 1 };
                    for o in out.iter_mut().skip(i).take(skip) {
                        *o = STRING;
                    }
                    i += skip;
                }
            }
            _ => {}
        }
        i += 1;
    }
    out
}

/// The make targets that write a tracked record, read by the one make detector (feature 451 D1 - its own pattern took any word after
/// `make`, so `make land NOTE=tick` read as a tick).
const MAKE_WRITE: [&str; 3] = ["record-checked", "tick", "accept"];

/// What one decision reads.
pub(crate) struct Ctx {
    pub procs: Procs,
    pub top: PathBuf,
}

/// Whether a make of this target runs in this tree (`own-make.sh`): the program by its name, the tree by its cwd.
fn runs_here(c: &Ctx, target: &str) -> bool {
    let wanted = format!("make {target}");
    let top = format!("{}/", c.top.display());
    c.procs.pids().into_iter().any(|p| {
        let raw = c.procs.read(p, "cmdline");
        let program = raw.split('\0').next().unwrap_or("");
        let name = program.rsplit('/').next().unwrap_or("");
        let is_make = ["make", "gmake"]
            .iter()
            .any(|m| name == *m || name.starts_with(&format!("{m} ")));
        is_make
            && raw.replace('\0', " ").contains(&wanted)
            && c.procs
                .link(p, "cwd")
                .is_some_and(|d| format!("{}/", d.display()).starts_with(&top))
    })
}

fn running(c: &Ctx, target: &str) -> bool {
    runs_here(c, &format!("--no-print-directory {target}")) || runs_here(c, target)
}

/// The escape's verdict: `Some(answers)` when it decides the call.
fn escaped(event: &Event, session: &Session, cmd: &str) -> Option<Vec<Answer>> {
    match escape_or_refuse(cmd, "GATE_WRITE_OK") {
        Escape::Escaped(why) => {
            log::fire(
                "gate-write",
                "escaped",
                &why,
                "gate-write-ok",
                &event.input,
                session,
            );
            Some(Vec::new())
        }
        Escape::Refused(text) => {
            let shown: String = cmd.chars().take(200).collect();
            log::fire(
                "gate-write",
                "blocked",
                &shown,
                "GATE_WRITE_OK-no-reason",
                &event.input,
                session,
            );
            Some(vec![Answer::Refuse(text)])
        }
        Escape::None => None,
    }
}

fn relative_in(top: &Path, file: &str) -> Option<String> {
    realpath(Path::new(file))
        .strip_prefix(realpath(top))
        .ok()
        .map(|r| r.to_string_lossy().into_owned())
}

fn input_field<'a>(event: &'a Event, key: &str) -> &'a str {
    event.input.get("tool_input").map_or("", |t| field(t, key))
}

fn file_of(event: &Event) -> &str {
    Some(input_field(event, "file_path"))
        .filter(|f| !f.is_empty())
        .unwrap_or(input_field(event, "notebook_path"))
}

/// The question the gate itself asks: exit 0 when the change is one it does not see.
fn unseen(c: &Ctx, extra: &[&str]) -> bool {
    let top = c.top.to_string_lossy();
    let gate_dir = ask(&c.top, "git", &["rev-parse", "--absolute-git-dir"], "").out;
    let snap = format!("{gate_dir}/gate-tree.json");
    let tool = c.top.join("scripts/gates/l7r-gate.sh");
    let mut args = vec![
        "preflight",
        "--root",
        top.as_ref(),
        "--tree-check",
        snap.as_str(),
    ];
    args.extend_from_slice(extra);
    ask_within(
        &c.top,
        &tool.to_string_lossy(),
        &args,
        Duration::from_secs(20),
    )
    .ok()
}

/// The file's text as this edit would leave it, or None.
fn after_edit(event: &Event, file: &str) -> Option<String> {
    match event.tool() {
        "Write" => Some(input_field(event, "content").to_owned()),
        "Edit" => {
            let current = std::fs::read_to_string(file).ok()?;
            let (old, new) = (
                input_field(event, "old_string"),
                input_field(event, "new_string"),
            );
            let all = event
                .input
                .get("tool_input")
                .and_then(|t| t.get("replace_all"))
                .and_then(serde_json::Value::as_bool)
                .unwrap_or(false);
            Some(if all {
                current.replace(old, new)
            } else {
                current.replacen(old, new, 1)
            })
        }
        _ => None,
    }
}

/// What a running gate refuses: a change it would see.
fn gate_refusal(event: &Event, c: &Ctx) -> Option<String> {
    let tool = event.tool();
    if FILE_TOOLS.contains(&tool) {
        let file = file_of(event);
        let rel = relative_in(&c.top, file).filter(|r| !r.is_empty())?;
        let invisible = after_edit(event, file).is_some_and(|text| {
            let dir = crate::shared::tempdir::TempDir::new("gate-write");
            let scratch = dir.join("after-edit");
            let wrote = std::fs::write(&scratch, text).is_ok();
            let said = wrote
                && unseen(
                    c,
                    &[
                        "--would-write",
                        &rel,
                        "--content",
                        &scratch.to_string_lossy(),
                    ],
                );
            said
        });
        return (!invisible).then(|| format!("an {tool} of {rel}"));
    }
    if tool != "Bash" {
        return None;
    }
    let cmd = input_field(event, "command");
    if GIT_WRITE.is_match(cmd).unwrap_or(false) {
        return (!unseen(c, &["--quiet"])).then(|| "a git commit or add of a change the gate sees (it moves HEAD, or what the gate compares against it)".to_owned());
    }
    if let Some(found) = crate::shared::make::invoked(cmd)
        .into_iter()
        .find(|t| MAKE_WRITE.contains(&t.as_str()))
    {
        return Some(format!("make {found} (it writes a tracked record)"));
    }
    shell_write(event, cmd, c)
}

/// The command and, for git, its subcommand, of a walk target's segment: past `VAR=value` and the wrappers the walk reads past,
/// `timeout` with its duration among them (451 T79: `timeout 60 make task-add` was refused as a shell write of `.`, 2026-11-21).
fn head_of(segment: &str) -> (&str, &str) {
    let mut words = segment.split_whitespace().peekable();
    while let Some(w) = words.next_if(|w| {
        w.contains('=')
            || matches!(
                *w,
                "sudo" | "env" | "command" | "exec" | "nohup" | "time" | "timeout"
            )
    }) {
        if w == "timeout" {
            words.next();
        }
    }
    let head = words.next().unwrap_or("");
    let head = head.rsplit('/').next().unwrap_or(head);
    if head != "git" {
        return (head, "");
    }
    let mut sub = "";
    let mut skip = false;
    for w in words {
        if std::mem::take(&mut skip) {
            continue;
        }
        if w == "-C" || w == "-c" {
            skip = true;
        } else if !w.starts_with('-') {
            sub = w;
            break;
        }
    }
    (head, sub)
}

/// What a running gate refuses of a shell command's writes (451 T33; on 2026-11-20 a builder's `git apply` and `cp` of guard files
/// under T34's `make land` put unfinished code under its gate, which failed static's cover): each write the walk places in this
/// tree - a redirect, `tee`, `cp`, `mv`, `rm`, `sed -i`, a writing git subcommand - that the gate would see, asked of the same tree
/// check an Edit is (the content unknown, so only a record the gate never reads clears). Left alone: `make` (its targets judged
/// above), git's `push`, `tag` and `branch` (refs, not the tree), `mkdir`, `rmdir` and `touch` (no text git compares), a path the
/// walk cannot resolve, `.git/`, and a path git ignores, which the gate's snapshot never holds. A Python program that can write
/// (`py_c`'s judgment) is judged by the files its literals name, as make-only judges it for a guard file (`interp`): where it
/// stands says nothing of where it writes. Only a literal that is a path where the shell stands counts (`program_names`'s
/// `placed`): an f-string's placeholder, a glob, a URL or a literal joined onto a base the program computes is a path not
/// resolved, which fails open (the round-3 replay's false refusals, measured 2026-11-20), and so does a literal handed to a
/// function of the program's own (`own_args`), which make-only, fail-closed, still counts.
fn shell_write(event: &Event, cmd: &str, c: &Ctx) -> Option<String> {
    let given = field(&event.input, "cwd");
    let here = if given.is_empty() {
        c.top.to_string_lossy().into_owned()
    } else {
        given.to_owned()
    };
    let home = std::env::var("HOME").unwrap_or_default();
    let top = realpath(&c.top).to_string_lossy().into_owned();
    // the path's place in the tree when the gate would see a write of it: "" the tree itself
    let seen = |path: &str| -> Option<String> {
        let rel = if path == top {
            ""
        } else {
            path.strip_prefix(&format!("{top}/"))?
        };
        if rel == ".git" || rel.starts_with(".git/") {
            return None;
        }
        let unseen_here = !rel.is_empty()
            && (ask(&c.top, "git", &["check-ignore", "-q", "--", rel], "").ok()
                || unseen(c, &["--would-write", rel]));
        (!unseen_here).then(|| rel.to_owned())
    };
    let walk = crate::shared::tree::walk_judged(cmd, Some(&here), "", &home);
    walk.targets.iter().find_map(|t| {
        let (head, sub) = head_of(&t.segment);
        if t.how == "read"
            || matches!(head, "make" | "mkdir" | "rmdir" | "touch")
            || matches!(sub, "push" | "tag" | "branch")
        {
            return None;
        }
        let rel = match t.program.as_deref() {
            Some(body) => {
                // asked once a program, and only when a literal names a directory
                let writes = std::cell::OnceCell::new();
                let computed = || *writes.get_or_init(|| writes_computed(body));
                let wanted =
                    |p: &str| file_named(p, &computed) && seen(p).is_some_and(|r| !r.is_empty());
                let named =
                    interp::program_names(&own_args(body), t.path.as_deref(), true, true, &wanted)?;
                seen(&named)?
            }
            None => seen(t.path.as_deref()?)?,
        };
        let shown = if rel.is_empty() { "." } else { rel.as_str() };
        Some(format!("a shell write of {shown} (`{}`)", t.segment))
    })
}

/// Whether a Python literal, resolved, names a file the program could write: one that is there, or a name with an extension it would
/// make - an open's mode (`'w'`), an encoding, a word of text resolve into the tree too, and are neither - and a directory only when
/// the program writes a path it computes (`computed`, `shared::tree::program::writes_computed`), which can land under it (451 T118,
/// found by T51 and measured 2026-11-21: a directory named beside no such write - `sys.path.insert(0, "scripts")`,
/// `Path("specs").glob(...)` read, a `git log -- rust/guard` argv - was refused as its write on 2 of T93's commands, 3 of T33's
/// fixtures and 13 of the script runs T51 reads (3 scripts), each only read or run; one beside it - `R = Path("research")`, `p = R / path`, `p.write_text(..)` - is
/// window#170's and refusals#144's true write into the tree, refused as at HEAD).
fn file_named(p: &str, computed: &dyn Fn() -> bool) -> bool {
    let path = Path::new(p);
    let named = p.rsplit('/').next().is_some_and(|n| n.contains('.')) || path.exists();
    named && (!path.is_dir() || computed())
}

/// The working tree a directory stands in, or the directory itself outside one.
pub(crate) fn top_of(here: &Path) -> PathBuf {
    here.ancestors()
        .find(|d| d.join(".git").exists())
        .unwrap_or(here)
        .to_path_buf()
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let here = std::env::current_dir().unwrap_or_default();
    let top = top_of(&here);
    judge(
        event,
        session,
        &Ctx {
            procs: Procs {
                root: PathBuf::from("/proc"),
                mine: std::process::id(),
            },
            top,
        },
    )
}

pub(crate) fn judge(event: &Event, session: &Session, c: &Ctx) -> Vec<Answer> {
    let cmd = input_field(event, "command");
    if !running(c, "done") {
        return Vec::new();
    }
    if let Some(answers) = escaped(event, session, cmd) {
        return answers;
    }
    let Some(what) = gate_refusal(event, c) else {
        return Vec::new();
    };
    log::fire(
        "gate-write",
        "blocked",
        &what,
        "write-during-gate",
        &event.input,
        session,
    );
    vec![Answer::Refuse(format!(
        "\u{1b}[1mBLOCKED (gate-write): {what} while this tree's `make done` runs.\u{1b}[0m\n\
A write during the run voids its verdict (\"the tree moved while the gate ran\") and costs the whole gate again.\n\
Wait for it: `make verify-wait`, run_in_background - its exit is the notification - then make the change.\n\
(feature 385, plan D13; escape GATE_WRITE_OK=\"<reason>\")"
    ))]
}

#[cfg(test)]
mod tests;
