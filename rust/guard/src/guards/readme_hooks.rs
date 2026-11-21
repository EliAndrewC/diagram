//! `readme-hooks` (constitution XVII; ported from the shell of the same name, feature 449 T032): A SESSION DOES NOT WRITE A README. A README is
//! not loaded into a session's context; a directory `CLAUDE.md` is, automatically, whenever work happens in that directory, so anything a README
//! holds is invisible to the next session unless it happens to look. `README_OK` with a reason that quotes the GM's authorization is the escape.
//!
//! Judged (451 T67): the file a file tool names, and a Bash command's WRITE targets as `shared::tree`'s walk finds them - a README written
//! in the tree (the mirror, a clone, or a copy of this project anywhere, `copy`) is refused wherever the call names it; a name the
//! command merely holds (a copy's source, a sed script, a heredoc's text, a Python string's text) and a README outside the tree (a
//! `/tmp` scratch file or a scratch repository of its own, by either route) are not. T58's builder's
//! `cp rust/guard/src/guards/readme_hooks.rs /tmp/t58/readme.keep` was refused, its destination a README by name outside the tree
//! (observed 2026-11-21, method: the guard log's refusals, each replayed or read).

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;

use crate::guards::make_only_hooks::interp;
use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::shape::{shlex, triple_quoted_spans};
use crate::shared::state::field;
use crate::shared::tree::{classify, normpath, walk_judged, Target};

/// The guard.
pub const GUARD: Guard = Guard {
    name: "readme-hooks",
    events: &["PreToolUse"],
    matcher: "Bash|Edit|Write|NotebookEdit",
    decide,
};

fn re(pattern: &str) -> Regex {
    crate::shared::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static FILE: LazyLock<Regex> = LazyLock::new(|| re(r"(?i)(^|/)README(\.[A-Za-z0-9]+)?$"));
/// The old guard's write positions before a README (a redirect, `sed -i`, `tee`, a copy's or move's second word), a variable's
/// characters allowed in the path: what judges a destination the walk cannot resolve.
static UNRESOLVED: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?i)(?:>>?\s*|sed\s+-i\b[^;|&]*?|tee\s+(?:-a\s+)?|cp\s+\S+\s+|mv\s+\S+\s+)[\w./${}`-]*README(?:\.[A-Za-z0-9]+)?(?=\s|$)",
    )
});
/// A Python program's README literal written in place (`Path('README.md').write_text`), the old guard's rule.
static PY_WRITE: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?i)README(?:\.[A-Za-z0-9]+)?['"]\s*\)?\s*\)?\s*\.write_text"#));
/// A Python line that writes a file: a write, an open (its read-only opens exempt by the literal reader), a move or a removal.
static PY_WRITES: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"\.write(?:_text|_bytes)?\(|\bopen\(|\.(?:touch|unlink|rename)\(|\bshutil\.\w+\(|\bos\.(?:rename|replace|remove|unlink)\(",
    )
});
/// A `mktemp` substitution, with the directory its `-p` names.
static MKTEMP: LazyLock<Regex> =
    LazyLock::new(|| re(r"\$\(\s*mktemp\b(?:[^()]*?\s-p\s+([^\s()]+))?[^()]*\)"));
/// The shells whose `-c` program is walked as a command of its own.
const SHELLS: [&str; 4] = ["bash", "sh", "dash", "zsh"];
/// A call that makes a work tree, whose new directory is not on disk when the guard reads: git's own global options (its valued
/// ones with their values), then the subcommand `worktree add` or `clone`, and its arguments. Only options may stand between, so a
/// word after a subcommand - a commit message's "the clone step", `git grep -n clone` - is no such call: the loose form refused T67's
/// own cp after `git commit -qm "the clone step"`; over every transcript's Bash commands it matched 519 times, this form 374, the
/// difference each a mention (measured 2026-11-21, `/tmp/t67/makes2.py`). A match inside quoted text writes its probe there, where
/// the walk finds no write: a word takes a quote only whole and with no space inside, so a message's closing quote is never taken
/// for an argument (`git commit -m "git clone the tree"` unbalanced the probe's quotes until it was).
static MAKES: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r#"\bgit((?:[ \t]+(?:-(?:[Cc]|-git-dir|-work-tree|-namespace|-config-env)[ \t]+(?:'[^'\s]*'|"[^"\s]*"|[^\s;|&'"])+|-(?:'[^'\s]*'|"[^"\s]*"|[^\s;|&'"])+))*)[ \t]+(worktree[ \t]+add|clone)\b((?:[ \t]+(?:'[^'\s]*'|"[^"\s]*"|[^\s;|&'"])+)*)"#,
    )
});
/// `git clone`'s options that take the next word as their value, so its source is the word after.
const CLONE_VALUED: [&str; 14] = [
    "-b",
    "-o",
    "-u",
    "-c",
    "-j",
    "--branch",
    "--origin",
    "--depth",
    "--reference",
    "--separate-git-dir",
    "--template",
    "--config",
    "--upload-pack",
    "--jobs",
];
/// `git worktree add`'s options that take the next word as their value, so its place is the word after (`git worktree add -h`,
/// git 2.53).
const WORKTREE_VALUED: [&str; 3] = ["-b", "-B", "--reason"];
/// The files a made work tree's call is written as, for the walk to resolve, each followed by the call's number (`made_trees`):
/// the source's, whose place says whether it is this project's, and the new work tree's own.
const MADE: &str = ".l7r-readme-made.";
const PLACE: &str = ".l7r-readme-place.";
static PROBE: LazyLock<Regex> = LazyLock::new(|| re(r"/\.l7r-readme-(made|place)\.(\d+)$"));
/// What the walk keeps of a segment (`shared::tree`'s `Target.segment`): a probe whose place it cannot resolve, cut there, has lost
/// its number.
const SEGMENT_KEPT: usize = 120;
/// A quoted string held in a string's text (`'(tmp / "README.md").write_text(1)'`): the string is a program's text, not a path.
static HELD: LazyLock<Regex> = LazyLock::new(|| re(r#"(['"])[^'"]*\1"#));

/// Whether a path is a README by its name.
fn named(path: &str) -> bool {
    FILE.is_match(path.trim_matches(['\'', '"']))
        .unwrap_or(false)
}

/// Whether a path lies in the tree: the mirror, one of its clones, or a copy of this project anywhere else (`copy`).
fn in_tree(path: &str, main: &str) -> bool {
    matches!(classify(Some(path), main), "main" | "clone") || copy(path, main)
}

/// Whether a path lies in a copy of this project outside the mirror and its clones, known by what its directory IS, never by its
/// path (451 T67, round 2): the repository nearest above it is a copy when its common git dir is the mirror's or a clone's (a
/// builder's `git worktree add /tmp/t58/wt`), or its origin is this repository - the mirror, a clone, the mirror's own origin by
/// any scheme, or a local repository that is itself a copy, followed three hops. A scratch repository of its own (2026-10-10's
/// `git init`), a clone of another repository and a directory in no repository are not. Read from the disk, no process started;
/// `classify` stays the path rule every other guard's walk reads (`main_tree_hooks` moves a write by it).
fn copy(path: &str, main: &str) -> bool {
    Path::new(path)
        .ancestors()
        .skip(1)
        .find_map(repo)
        .is_some_and(|git| ours(&git, main, 3))
}

/// The common git dir of the repository whose work tree is `dir`: its `.git` directory, or the git dir a `.git` file names (a
/// worktree's or a submodule's, relative to `dir` or absolute), through that git dir's `commondir` where it has one.
fn repo(dir: &Path) -> Option<String> {
    let dot = dir.join(".git");
    let git = if dot.is_dir() {
        dot
    } else {
        let text = std::fs::read_to_string(&dot).ok()?;
        let named = dir.join(text.trim().strip_prefix("gitdir:")?.trim());
        match std::fs::read_to_string(named.join("commondir")) {
            Ok(common) => named.join(common.trim()),
            Err(_) => named,
        }
    };
    Some(normpath(&git.to_string_lossy()))
}

/// Whether the repository whose git dir is `git` is this project's: the mirror's or a clone's, or its origin this repository.
fn ours(git: &str, main: &str, hops: u8) -> bool {
    let tree = |p: &str| matches!(classify(Some(&normpath(p)), main), "main" | "clone");
    let Some(url) = origin(git) else {
        return tree(git);
    };
    let local = url.strip_prefix("file://").unwrap_or(&url);
    // a local origin is followed to its own git dir: a work tree's, or a bare repository's own
    let next = || {
        repo(Path::new(local)).or_else(|| {
            Path::new(local)
                .join("objects")
                .is_dir()
                .then(|| normpath(local))
        })
    };
    tree(git)
        || tree(local)
        || origin(&format!("{main}/.git")).is_some_and(|m| key(&m) == key(&url))
        || (hops > 0 && local.starts_with('/') && next().is_some_and(|g| ours(&g, main, hops - 1)))
}

/// The URL of a repository's `origin` remote, read from its git dir's `config`.
fn origin(git: &str) -> Option<String> {
    let text = std::fs::read_to_string(format!("{git}/config")).ok()?;
    let mut inside = false;
    text.lines().map(str::trim).find_map(|line| {
        if line.starts_with('[') {
            inside = line == "[remote \"origin\"]";
            return None;
        }
        let (k, v) = line.split_once('=')?;
        (inside && k.trim() == "url").then(|| v.trim().to_owned())
    })
}

/// A remote's URL as the repository it names: its scheme and user dropped, an scp-style host's `:` a `/`, a trailing `/` and
/// `.git` dropped - `git@github.com:EliAndrewC/diagram.git` and `https://github.com/EliAndrewC/diagram` are one, compared whole,
/// so `.../diagram-research` is another.
fn key(url: &str) -> String {
    let rest = url.split_once("://").map_or(url, |(_, r)| r);
    let rest = rest
        .split_once('@')
        .map_or(rest, |(_, r)| r)
        .trim_end_matches('/');
    rest.strip_suffix(".git")
        .unwrap_or(rest)
        .replacen(':', "/", 1)
}

/// A Python program with each one-line string that holds a quoted string of its own blanked to `""`, read as Python's lexer reads
/// it (a `#` outside a string ends the line's code, kept as it is; a backslash escapes the next character; a string left open at
/// its line's end kept as it is): such a string is the program's text - a test's `write_text('(tmp / "README.md").write_text(1)')`
/// - never a path, which holds no quoted string (451 T67, round 2, the review's L1).
fn without_held(body: &str) -> String {
    let mut out = String::with_capacity(body.len());
    for line in body.split_inclusive('\n') {
        let chars: Vec<char> = line.chars().collect();
        let mut i = 0;
        while let Some(&ch) = chars.get(i) {
            if ch == '#' {
                out.extend(&chars[i..]);
                break;
            }
            if ch != '\'' && ch != '"' {
                out.push(ch);
                i += 1;
                continue;
            }
            let mut j = i + 1;
            while chars.get(j).is_some_and(|&c| c != ch && c != '\n') {
                j += if chars[j] == '\\' { 2 } else { 1 };
            }
            if chars.get(j) != Some(&ch) {
                out.extend(&chars[i..]);
                break;
            }
            let text: String = chars[i + 1..j].iter().filter(|&&c| c != '\\').collect();
            if HELD.is_match(&text).unwrap_or(false) {
                out.push_str("\"\"");
            } else {
                out.extend(&chars[i..=j]);
            }
            i = j + 1;
        }
    }
    out
}

/// What would write a README in the tree `main`, or None.
pub(crate) fn hit(event: &Event, main: &str, home: &str) -> Option<String> {
    let input = event.input.get("tool_input")?;
    // every README is named in the input; with none there the walk is not owed (T052)
    if !input.to_string().to_ascii_lowercase().contains("readme") {
        return None;
    }
    if ["Write", "Edit", "NotebookEdit"].contains(&event.tool()) {
        // the same tree as a command's: a relative path, which no file tool sends, is judged one of its own
        let path = field(input, "file_path");
        let here = || !path.starts_with('/') || in_tree(&normpath(path), main);
        return (named(path) && here()).then(|| path.to_owned());
    }
    let cmd = field(input, "command");
    // an event with no `cwd` stands in the tree, so a relative README is still judged one of its own
    let standing = Some(field(&event.input, "cwd"))
        .filter(|c| !c.is_empty())
        .unwrap_or(main);
    // a directory `mktemp` makes is scratch, outside the tree: named for the walk, which cannot run it (`cd $(mktemp -d)`)
    let cmd = MKTEMP.replace_all(cmd, |c: &fancy_regex::Captures| {
        let dir = c.get(1).map_or("/tmp", |m| m.as_str());
        format!("{dir}/mktemp.scratch")
    });
    // a work tree of this project the command makes is not on disk for `copy` to read: a README under its place counts as the
    // tree's, and where a place cannot be resolved, every README the command writes - its shells' programs' made trees among them,
    // whichever side of the program the write is on
    let made = made_all(&cmd, standing, main, home);
    let tree =
        |p: &str| in_tree(p, main) || made.as_ref().is_none_or(|m| m.iter().any(|d| under(p, d)));
    command_hit(&cmd, standing, &tree, main, home)
}

/// Whether a path is a directory or lies under it, component by component (`/tmp/t58/wt-notes` is not under `/tmp/t58/wt`).
fn under(path: &str, dir: &str) -> bool {
    path == dir
        || path
            .strip_prefix(dir.trim_end_matches('/'))
            .is_some_and(|r| r.starts_with('/'))
}

/// A call's word as git reads it, for the walk to resolve where the command stands: under the call's `-C` (`at`) when relative
/// there; a variable's or home's word (`$d/wt`, `~/wt`), and any word of a call with no `-C`, as it stands - never under `.`, where
/// the walk took `./$d/wt` for a directory under the command's own, passing a README in `$d/wt`.
fn at_git(at: Option<&str>, word: &str) -> String {
    match at {
        Some(c) if !word.starts_with(['/', '$', '~']) => format!("{c}/{word}"),
        _ => word.to_owned(),
    }
}

/// The places of the work trees of this project a command makes (`made_trees`), and those its shells' `-c` programs make, whose
/// calls are quoted text to the command's own walk; None where one cannot be resolved.
fn made_all(cmd: &str, standing: &str, main: &str, home: &str) -> Option<Vec<String>> {
    let mut places = made_trees(cmd, standing, main, home)?;
    for program in programs(cmd) {
        places.extend(made_all(&program, standing, main, home)?);
    }
    Some(places)
}

/// The `-c` programs a command's shells run (`SHELLS`), each one word to the walk.
fn programs(cmd: &str) -> Vec<String> {
    shlex(cmd)
        .unwrap_or_default()
        .windows(3)
        .filter(|w| SHELLS.contains(&w[0].rsplit('/').next().unwrap_or("")) && w[1] == "-c")
        .map(|w| w[2].clone())
        .collect()
}

/// A call's words that are neither an option nor an option's value (`valued`, the options whose value is the next word), unquoted.
fn positional<'a>(args: &[&'a str], valued: &[&str]) -> Vec<&'a str> {
    let (mut i, mut out) = (0, Vec::new());
    while let Some(a) = args.get(i) {
        if a.starts_with('-') {
            i += if valued.contains(a) { 2 } else { 1 };
            continue;
        }
        out.push(a.trim_matches(['\'', '"']));
        i += 1;
    }
    out
}

/// The directory `git clone` makes from its source when given none: the source's last component, a trailing `/`, `/.git` and
/// `.git` dropped (`/repo/.clones/c/` is `c`, `git@host:o/project.git` is `project`); None for a source that names none, or whose
/// name is a variable's or a substitution's (`git clone $S`), known only once the shell expands it - a place failing closed.
fn humanish(src: &str) -> Option<String> {
    let s = src.trim_end_matches('/');
    let s = s.strip_suffix("/.git").unwrap_or(s).trim_end_matches('/');
    let name = s.rsplit(['/', ':']).next().unwrap_or(s);
    let name = name.strip_suffix(".git").unwrap_or(name);
    (!name.is_empty() && !name.contains(['$', '`'])).then(|| name.to_owned())
}

/// The places of the work trees of this project a command makes (451 T67, round 2; the plan review's (b)3c), or None where one
/// cannot be resolved - every README the command writes then counts, failing closed. A `git worktree add` whose repository - its
/// `-C`, else where git runs - is the tree, or a `git clone` of this repository - a URL by the mirror's origin, a path in the tree, a
/// copy or a work tree an earlier call of the command makes; its place `worktree add`'s path or the clone's directory (else the one
/// git names from the source), relative to the `-C` (a variable's or home's word as the walk expands it, `at_git`). Each source and
/// place is resolved by the walk itself where the command stands
/// when it runs, the call written as two numbered `touch`es there; a source the walk cannot resolve (`git clone $UNSET y`) counts as
/// this project's. A scratch clone of a repository of its own (`git clone -q remote.git seed` in a `mktemp` directory, twice in the
/// corpus) is no copy, and a README outside every place passes: T67's own cp beside the `git worktree add` it opened with.
fn made_trees(cmd: &str, standing: &str, main: &str, home: &str) -> Option<Vec<String>> {
    if !MAKES.is_match(cmd).unwrap_or(false) {
        return Some(Vec::new());
    }
    let mirror = origin(&format!("{main}/.git"));
    let mut urls = Vec::new();
    let probe = MAKES.replace_all(cmd, |c: &fancy_regex::Captures| {
        let words = |g: usize| {
            c.get(g)
                .map_or("", |m| m.as_str())
                .split_whitespace()
                .collect::<Vec<_>>()
        };
        // a redirect ends the call's own words (`git clone src >/dev/null` names no directory)
        let args: Vec<_> = words(3)
            .into_iter()
            .take_while(|a| !a.contains(['<', '>']))
            .collect();
        // where git runs: its `-C`, else where the command stands
        let opts = words(1);
        let at = opts
            .windows(2)
            .find(|w| w[0] == "-C")
            .map(|w| w[1].trim_matches(['\'', '"']));
        let (source, place, url) = if c.get(2).is_some_and(|m| m.as_str().starts_with("worktree")) {
            let free = positional(&args, &WORKTREE_VALUED);
            let source = at.unwrap_or(".").to_owned();
            (source, free.first().map(|p| (*p).to_owned()), false)
        } else {
            let free = positional(&args, &CLONE_VALUED);
            let src = free.first().copied().unwrap_or("");
            let remote = (src.contains("://") && !src.starts_with("file://"))
                || (src.contains('@') && src.contains(':'));
            let local = src.strip_prefix("file://").unwrap_or(src);
            let source = if remote {
                "/".to_owned()
            } else {
                at_git(at, local)
            };
            let place = free
                .get(1)
                .map(|p| (*p).to_owned())
                .or_else(|| humanish(src));
            let url = remote && mirror.as_deref().is_some_and(|m| key(m) == key(src));
            (source, place, url)
        };
        // a place relative to where git runs; none named (`git worktree add` alone) is one the walk cannot resolve
        let place = place.map_or_else(|| "$L7R_README_NO_PLACE".to_owned(), |p| at_git(at, &p));
        let k = urls.len();
        urls.push(url);
        format!("touch {source}/{MADE}{k} && touch {place}/{PLACE}{k}")
    });
    let (mut ours, mut made) = (vec![false; urls.len()], Vec::new());
    for t in walk_judged(&probe, Some(standing), main, home).targets {
        let text = t.path.as_deref().unwrap_or(&t.segment).trim_end();
        let Some(c) = PROBE.captures(text).ok().flatten() else {
            // a probe the walk cut short, its place unresolved and its number lost: failing closed
            if t.path.is_none()
                && t.segment.starts_with("touch ")
                && t.segment.chars().count() >= SEGMENT_KEPT
            {
                return None;
            }
            continue;
        };
        let k: usize = c[2].parse().unwrap_or(usize::MAX);
        if &c[1] == "made" {
            // this project's: a URL of the mirror's origin, a source in the tree, under a place made before it, or unresolved
            let yes = urls.get(k).copied().unwrap_or(false)
                || t.path.as_deref().is_none_or(|p| {
                    in_tree(p, main) || made.iter().flatten().any(|d: &String| under(p, d))
                });
            if let Some(o) = ours.get_mut(k) {
                *o = yes;
            }
        } else if ours.get(k).copied().unwrap_or(false) {
            made.push(t.path.map(|p| {
                let d = p.rsplit_once('/').map_or("", |(d, _)| d);
                if d.is_empty() { "/" } else { d }.to_owned()
            }));
        }
    }
    made.into_iter().collect()
}

/// The README a command writes in the tree (`tree` says where it lies), standing in `standing`, or None.
fn command_hit(
    cmd: &str,
    standing: &str,
    tree: &dyn Fn(&str) -> bool,
    main: &str,
    home: &str,
) -> Option<String> {
    let found = walk_judged(cmd, Some(standing), main, home)
        .targets
        .iter()
        .find_map(|t| written(t, tree));
    // a shell's `-c` program is one word to the walk, which blanks it: its own writes are walked where the shell stands
    found.or_else(|| {
        programs(cmd)
            .iter()
            .find_map(|p| command_hit(p, standing, tree, main, home))
    })
}

/// The README a write target puts in the tree, or None.
fn written(t: &Target, tree: &dyn Fn(&str) -> bool) -> Option<String> {
    if t.how == "read" {
        return None;
    }
    if let Some(body) = &t.program {
        return program_writes(body, t.path.as_deref(), tree);
    }
    match &t.path {
        Some(p) => (named(p) && tree(p)).then(|| p.clone()),
        // a destination the walk cannot resolve (a variable never set): the old guard's destination-position rule judges its
        // segment, whose quoted text and heredoc bodies the walk has already blanked - a README there counts, failing closed
        None => UNRESOLVED
            .find(&t.segment)
            .ok()
            .flatten()
            .map(|m| m.as_str().to_owned()),
    }
}

/// The README a Python program writes in the tree, standing in `here` (None where unknown), or None.
fn program_writes(body: &str, here: Option<&str>, tree: &dyn Fn(&str) -> bool) -> Option<String> {
    // a literal that is a path where it stands, resolved (make-only's reader as gate-write reads it, 451 T33): a README in the tree
    // counts; one resolved outside it (`Path('/tmp/x') / 'README.md'`) answers for the program
    // only the lines that write: a literal a line compares, passes on or reads is no destination (a fixture's
    // `put(d, "questions/README.txt", t)` beside the `open(..., 'w')` it calls, 2026-11-21); a string's text, triple-quoted or
    // holding a quoted string of its own, is none either
    let text = without_held(&without_triples(body));
    let writing: String = text
        .lines()
        .filter(|l| PY_WRITES.is_match(l).unwrap_or(false))
        .collect::<Vec<_>>()
        .join("\n");
    let reads =
        |want: &dyn Fn(&str) -> bool| interp::program_names(&writing, here, true, true, want);
    if let Some(at) = reads(&|p: &str| named(p) && (here.is_none() || tree(p))) {
        return Some(at);
    }
    if reads(&|p: &str| named(p)).is_some() {
        return None;
    }
    // a README joined onto a base the program computes (`Path(d) / 'README.md'`), written: the old rule, outside its
    // triple-quoted text, failing closed
    PY_WRITE
        .find(&writing)
        .ok()
        .flatten()
        .map(|m| m.as_str().to_owned())
}

/// `body` with each of its triple-quoted strings, a Python program's own words rather than its code, put down as `""` - as the
/// pattern it replaced, `TRIPLE` (`(?s)"""(?:\\.|(?!""").)*"""|'''(?:\\.|(?!''').)*'''`, make-only's), put them down with
/// `replace_all`. The strings are shape's `triple_quoted_spans` (451 T113): the pattern's backtracking search held the guard past
/// 10 s on an opening nothing closes before forty escapes (measured 2026-11-21, the T113 plan section). A test holds the two equal
/// on every text of up to 5 pieces (`tests.rs`).
fn without_triples(body: &str) -> String {
    let (mut out, mut from) = (String::new(), 0);
    for (at, end) in triple_quoted_spans(body) {
        out.push_str(&body[from..at]);
        out.push_str("\"\"");
        from = end + 1;
    }
    out + &body[from..]
}

fn shown(event: &Event) -> String {
    let input = event.input.get("tool_input");
    let text = input.map_or("", |t| {
        Some(field(t, "command"))
            .filter(|c| !c.is_empty())
            .unwrap_or(field(t, "file_path"))
    });
    text.chars().take(200).collect()
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let cmd = event
        .input
        .get("tool_input")
        .map_or("", |t| field(t, "command"));
    match escape_or_refuse(cmd, "README_OK") {
        Escape::Escaped(why) => {
            log::fire(
                "readme",
                "escaped",
                &why,
                "gm-authorized",
                &event.input,
                session,
            );
            return Vec::new();
        }
        Escape::Refused(text) => {
            log::fire(
                "readme",
                "blocked",
                &shown(event),
                "README_OK-no-reason",
                &event.input,
                session,
            );
            return vec![Answer::Refuse(text)];
        }
        Escape::None => {}
    }
    let home = crate::shared::env::opt("HOME").unwrap_or_default();
    let Some(found) = hit(event, &session.main().to_string_lossy(), &home) else {
        return Vec::new();
    };
    log::fire(
        "readme",
        "blocked",
        &shown(event),
        "readme-is-the-gm-s",
        &event.input,
        session,
    );
    vec![Answer::Refuse(format!(
        "BLOCKED: writing a README ({found}).\n\n\
A README is not loaded into a session's context. A directory CLAUDE.md is - automatically, whenever\n\
work happens in that directory. So anything you would put in a README is invisible to the next\n\
session unless it happens to look, which is to say by luck.\n\n\
Put it where it will actually be read:\n\n  \
- a CLAUDE.md in the directory it governs, for a rule that must be known while working there\n  \
- a topic doc referenced from a CLAUDE.md, when it is long enough that always loading it is waste\n\n\
WHAT THIS COST, once: dev/perf-log/README.md carried \"an append-only shared log must be a DIRECTORY,\n\
because concurrent clones conflict on every push\". A session read that file, quoted it, and hours\n\
later created a single-file run-log.jsonl. Had it been a CLAUDE.md the rule would have been in\n\
context when it mattered. It is one now.\n\n\
A README is written by a human for a human; if the GM wants one, the GM writes it. The one escape is\n\
the GM delegating an edit in their own words: README_OK in the command, with a reason that quotes the\n\
authorization (GM 2026-09-06, the research/ link table) - it is recorded, and `make audit` shows it.\n\n\
(rust/guard/src/guards/readme_hooks.rs; constitution XVII, GM 2026-08-24)"
    ))]
}

#[cfg(test)]
mod tests;
