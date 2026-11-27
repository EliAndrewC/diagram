//! A search that prints the held code (feature 449 T204). During T202 a `grep -rn X rust/mode_a/src` printed lines of the held
//! `labels/placer.rs`: the guard looked for a read aimed at a held file or its directory, never a search of a parent that reaches
//! one - a check passing the bad (constitution XIV). Here a search - the Grep tool, a shell `grep`, `egrep`, `fgrep`, `ugrep`, `rg`,
//! `ag`, `git grep`, a `find` whose results reach a reader (its `-exec`, an `xargs` later in its pipeline, a `$(...)` or backtick
//! filling a reader's arguments - T204's plan review) - is judged by the files it reaches: refused while
//! one of them is held, unless its own flags leave that file out, and the refusal names the flags that do.
//!
//! WHAT LEAVES A FILE OUT is what each tool was measured doing on 2026-11-19 (GNU grep 3.11, ripgrep 14, ag 2.2, git 2.43), never what
//! its manual suggests: GNU grep's `--exclude`/`--include` match a found file's base name (a path in them matches nothing), and an
//! `--exclude` wins over any `--include`; ripgrep's `-g` matches a glob holding a `/` against the path from the working directory,
//! the last matching glob winning, and a file named on the command line is searched whatever the globs say (as the Grep tool, which
//! is ripgrep); ag's `--ignore` matches a base name, a directory's name or a path's tail, never a `**`. A form this module cannot read
//! leaves nothing out, so the search is refused: a wrong refusal costs one rewritten command, a wrong pass prints the code.
//!
//! WHAT IS NOT A READ (T204, T202's deletion step): `make phase-read`, the escape the refusal prescribes, and `git status` or a `git
//! diff` or `log` that prints names and counts only. Those segments, and every search that reached a held file and left each out,
//! are blanked before the guard's whole-command rule looks for a read verb beside a held file's name; a search that reached none stays
//! for that rule, so a form misread here is still held to the rule the guard had before T204. A search inside a `$(...)` kept whole
//! by quotes, or in a shell's `-c` script, is judged too.

use std::path::Path;

use serde_json::Value;

use crate::guards::finished_run_hooks::runs::realpath;
use crate::shared::spelled;
use crate::shared::state::field;

mod filter;
mod tools;

use filter::{rel_to, Filter, Hit, Reach, RgGlob, Root};
use tools::{find_search, git_grep_search, grep_search, producer_search, rg_ag_search};

/// One simple command of a shell line: its words unquoted, where it stands (char indices), and whether a `|` feeds it.
#[derive(Debug, Default)]
pub(super) struct Seg {
    pub words: Vec<String>,
    pub span: Option<(usize, usize)>,
    pub piped: bool,
    /// For a segment a `$(` or backtick opens, the command whose arguments it fills (`cat` in `cat $(find ...)`).
    pub host: Option<String>,
    /// Whether a `$(` or an opening backtick starts it, so that its output fills the arguments of what holds it.
    pub opened: bool,
}

/// `cmd` cut into simple commands at its unquoted separators, quotes and escapes removed from each word, comments dropped.
pub(super) fn segments(cmd: &str) -> Vec<Seg> {
    let c: Vec<char> = cmd.chars().collect();
    let (mut out, mut seg, mut word, mut started) =
        (Vec::new(), Seg::default(), String::new(), false);
    let mut ticks = 0usize;
    let mut i = 0;
    while i < c.len() {
        let (ch, next, at) = (c[i], c.get(i + 1).copied(), i);
        let touch = move |seg: &mut Seg, to: usize| {
            seg.span = Some((seg.span.map_or(at, |s| s.0), to));
        };
        let in_redirect = ch == '&' && (word.ends_with('>') || (!started && next == Some('>')));
        if ch == '#' && !started {
            while i < c.len() && c[i] != '\n' {
                i += 1;
            }
            continue;
        } else if ch == ' ' || ch == '\t' {
            end_word(&mut seg, &mut word, &mut started);
        } else if !in_redirect && matches!(ch, ';' | '&' | '|' | '\n' | '(' | ')' | '`')
            || (ch == '$' && next == Some('('))
        {
            end_word(&mut seg, &mut word, &mut started);
            let host = command(&seg.words).first().map(|h| (*h).to_owned());
            out.push(std::mem::take(&mut seg));
            ticks += usize::from(ch == '`');
            seg.opened = ch == '$' || (ch == '`' && ticks % 2 == 1);
            seg.host = host.filter(|_| seg.opened);
            let doubled = matches!((ch, next), ('&', Some('&')) | ('|', Some('|')) | ('$', _));
            seg.piped = ch == '|' && !doubled;
            i += usize::from(doubled);
        } else if ch == '\'' || ch == '"' {
            started = true;
            i += 1;
            while i < c.len() && c[i] != ch {
                if ch == '"' && c[i] == '\\' && matches!(c.get(i + 1), Some('"' | '\\' | '$' | '`'))
                {
                    i += 1;
                }
                word.extend(c.get(i));
                i += 1;
            }
            touch(&mut seg, i + 1);
        } else {
            started = true;
            if ch == '\\' && next.is_some() {
                i += 1;
            }
            word.push(c[i]);
            touch(&mut seg, i + 1);
        }
        i += 1;
    }
    end_word(&mut seg, &mut word, &mut started);
    out.push(seg);
    out.retain(|s| !s.words.is_empty());
    out
}

fn end_word(seg: &mut Seg, word: &mut String, started: &mut bool) {
    if *started {
        seg.words.push(std::mem::take(word));
        *started = false;
    }
}

/// A segment's command and arguments: leading `VAR=value` words and wrappers with their options dropped, the command word by its
/// name however it is spelled (451 T453: `/usr/bin/grep`, `\cat` and `nice -n 5 cat` were no reader), redirections and their targets
/// left out. `xargs` stays the command word: what it runs is its reader (`xargs_reader`).
fn command(words: &[String]) -> Vec<&str> {
    let assignment = |w: &str| {
        w.split_once('=').is_some_and(|(k, _)| {
            !k.is_empty() && k.chars().all(|c| c.is_alphanumeric() || c == '_')
        })
    };
    let mut start = 0;
    while let Some(w) = words.get(start) {
        let name = spelled::name_of(w);
        let next = words.get(start + 1).map(String::as_str);
        if name != "xargs" && spelled::WRAPPERS.contains(&name) && !spelled::lookup(name, next) {
            start +=
                1 + spelled::options(name, &words[start + 1..]) + usize::from(name == "timeout");
        } else if assignment(w) {
            start += 1;
        } else {
            break;
        }
    }
    let (mut out, mut skip) = (Vec::new(), false);
    for w in words.get(start..).unwrap_or_default() {
        let bare = w.trim_start_matches(|c: char| c.is_ascii_digit() || c == '&');
        if skip {
            skip = false;
        } else if bare.starts_with('>') || bare.starts_with('<') {
            skip = bare.trim_start_matches(['>', '<']).is_empty();
        } else if out.is_empty() {
            out.push(spelled::name_of(w));
        } else {
            out.push(w.as_str());
        }
    }
    out
}

/// The tools whose refusal names a fix.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(super) enum Tool {
    GrepCall,
    Grep,
    Rg,
    Ag,
    GitGrep,
    Find,
    Ls,
    Tree,
    Fd,
    /// A reader handed a glob, or a list this module cannot read: no flag leaves a file out, only a narrower path or list.
    Narrow,
}

/// A search refused: the held files it reaches (relative to the checkout), each with its path below the search's root, the root as
/// written, and the flags that would leave them out.
#[derive(Debug)]
pub(super) struct Found {
    pub files: Vec<String>,
    pub root: String,
    pub fix: String,
}

/// A search read from its words: where it starts, what it leaves out, and which tool's fix to name.
struct Search {
    tool: Tool,
    roots: Vec<Root>,
    filter: Filter,
}

const GREPS: &[&str] = &["grep", "egrep", "fgrep", "ugrep"];

/// The commands that print what the files they are handed hold: the searches and the guard's read verbs (T204, the plan review: a
/// `find` feeding one of these is a read of every held file it finds).
const READERS: &[&str] = &[
    "grep", "egrep", "fgrep", "ugrep", "rg", "ag", "cat", "head", "tail", "sed", "awk", "less",
    "more", "bat", "nl", "strings", "od", "xxd", "python", "python3", "perl",
];

/// A reader and its arguments, owned: what a `find`'s results are handed to.
type Fed = (String, Vec<String>);

fn reader_at(words: &[&str], at: usize, end: &[&str]) -> Option<Fed> {
    // the reader behind its own wrappers (451 T453: `xargs command cat` was no reader)
    let at = at + spelled::command_at(words.get(at..).unwrap_or_default());
    let cmd = words
        .get(at)
        .map(|c| spelled::name_of(c))
        .filter(|c| READERS.contains(c))?;
    let args = words[at + 1..]
        .iter()
        .take_while(|w| !end.contains(w))
        .filter(|w| **w != "{}");
    Some((cmd.to_owned(), args.map(|a| (*a).to_owned()).collect()))
}

/// The reader a `find -exec` runs, with its arguments but `{}`.
fn exec_reader(find: &[&str]) -> Option<Fed> {
    let at = find
        .iter()
        .position(|w| matches!(*w, "-exec" | "-execdir" | "-ok" | "-okdir"))?;
    reader_at(find, at + 1, &[";", "+"])
}

/// The reader `xargs` runs, with its arguments.
fn xargs_reader(words: &[&str]) -> Option<Fed> {
    let (mut i, valued) = (1, ["-n", "-I", "-P", "-d", "-L", "-s", "-E", "-a"]);
    while i < words.len() && words[i].starts_with('-') {
        i += 1 + usize::from(valued.contains(&words[i]));
    }
    reader_at(words, i, &[])
}

/// Whether a word is a command that prints the files it is handed.
fn reads(cmd: Option<&str>) -> bool {
    cmd.is_some_and(|c| READERS.contains(&c))
}

/// What a reader fed by `xargs` reads: the files its pipeline's first command could list (a lone `xargs`, fed by a file, could read
/// any), a grep's own exclusions counted beside the lister's.
fn xargs_fed(segs: &[Seg], k: usize, fed: &Fed, here: &str, top: &str) -> Search {
    let head = (0..=k).rev().find(|&j| !segs[j].piped).unwrap_or(0);
    let words = if head == k {
        vec!["<a file>"]
    } else {
        command(&segs[head].words)
    };
    let mut search = producer_search(&words, here, top);
    if GREPS.contains(&fed.0.as_str()) {
        let args: Vec<&str> = fed.1.iter().map(String::as_str).collect();
        let grep = grep_search(&args, here, top, true).filter;
        search.filter.grep_ex.extend(grep.grep_ex);
        search.filter.grep_in.extend(grep.grep_in);
        search.filter.grep_ex_dir.extend(grep.grep_ex_dir);
    }
    search
}

/// A reader's own arguments that are shell globs, each judged as the paths bash would hand it (a literal path is the whole-command
/// rule's): `cat <held dir>/*` read the held code (T204, the plan review's second round).
fn glob_args(w: &[&str], here: &str, top: &str) -> Option<Search> {
    let roots: Vec<Root> = w[1..]
        .iter()
        .filter(|a| !a.starts_with('-') && a.contains(['*', '?', '[']))
        .map(|a| Root::new(a, here, top, false))
        .collect();
    (!roots.is_empty()).then(|| Search {
        tool: Tool::Narrow,
        roots,
        filter: Filter::default(),
    })
}

/// The held files the search reaches that its flags do not leave out (Err), or whether it reached any (Ok): a search that reached a
/// held file and left each out is blanked for the whole-command rule, one that reached none is left to it (T204 review: a form this
/// module misreads, such as `git grep x HEAD:<held dir>`, must still meet the rule the guard had before).
fn reached(search: &Search, cwd: &str, top: &str, held: &[&str]) -> Result<bool, Found> {
    let mut any = false;
    let real_top = realpath(Path::new(top)).to_string_lossy().into_owned();
    let cwd_rel = rel_to(&realpath(Path::new(cwd)).to_string_lossy(), top);
    let mut found: Vec<(String, String)> = Vec::new();
    let mut root_shown = String::new();
    for root in &search.roots {
        for file in held {
            let Some(reach) = root.reach(file) else {
                continue;
            };
            any = true;
            let below = match &reach {
                Reach::Named => None,
                Reach::Below(r) => Some(r.as_str()),
            };
            let printed = match below {
                None => root.written.clone(),
                Some(r) => format!("{}/{r}", root.written.trim_end_matches('/')),
            };
            let from_cwd = cwd_rel.as_deref().and_then(|c| {
                if c.is_empty() {
                    Some((*file).to_owned())
                } else {
                    file.strip_prefix(c)?.strip_prefix('/').map(str::to_owned)
                }
            });
            let hit = Hit {
                file,
                below,
                cwd_rel: from_cwd,
                abs: format!("{real_top}/{file}"),
                printed,
            };
            if !search.filter.excludes(&hit) && !found.iter().any(|(f, _)| f == file) {
                found.push((
                    (*file).to_owned(),
                    below.map_or_else(|| hit.base().to_owned(), str::to_owned),
                ));
                if root_shown.is_empty() {
                    root_shown.clone_from(&root.written);
                }
            }
        }
    }
    if found.is_empty() {
        return Ok(any);
    }
    Err(Found {
        files: found.iter().map(|(f, _)| f.clone()).collect(),
        root: root_shown,
        fix: fix(search.tool, &found),
    })
}

/// Whether the Grep tool's `glob` is one glob ripgrep reads as written: none holding whitespace or a comma outside braces, which a
/// caller may split into several (T204 review: not confirmed either way, so not credited).
fn one_glob(glob: &str) -> bool {
    let mut depth = 0i32;
    glob.chars().all(|c| {
        depth += i32::from(c == '{') - i32::from(c == '}');
        !c.is_whitespace() && (c != ',' || depth != 0)
    })
}

/// The flags that leave `found` (each held file and its path below the root) out, for the tool that searched.
fn fix(tool: Tool, found: &[(String, String)]) -> String {
    let base = |f: &str| f.rsplit('/').next().unwrap_or(f).to_owned();
    let mut bases: Vec<String> = found.iter().map(|(f, _)| base(f)).collect();
    bases.dedup();
    let each = |make: &dyn Fn(&(String, String)) -> String| {
        found.iter().map(make).collect::<Vec<_>>().join(" ")
    };
    match tool {
        Tool::GrepCall => match found {
            [(_, below)] => format!("glob: \"!**/{below}\""),
            _ => format!(
                "glob: \"!**/{{{}}}\"",
                found
                    .iter()
                    .map(|(_, b)| b.as_str())
                    .collect::<Vec<_>>()
                    .join(",")
            ),
        },
        Tool::Grep => bases
            .iter()
            .map(|b| format!("--exclude={b}"))
            .collect::<Vec<_>>()
            .join(" "),
        Tool::Ag => bases
            .iter()
            .map(|b| format!("--ignore {b}"))
            .collect::<Vec<_>>()
            .join(" "),
        Tool::Rg => each(&|(_, below)| format!("-g '!**/{below}'")),
        Tool::GitGrep => each(&|(file, _)| format!("':(top,exclude){file}'")),
        Tool::Find => each(&|(_, below)| format!("-not -path '*/{below}'")),
        Tool::Ls => bases
            .iter()
            .map(|b| format!("--ignore={b}"))
            .collect::<Vec<_>>()
            .join(" "),
        Tool::Tree => format!("-I '{}'", bases.join("|")),
        Tool::Fd => bases
            .iter()
            .map(|b| format!("-E {b}"))
            .collect::<Vec<_>>()
            .join(" "),
        Tool::Narrow => "a narrower path, glob or list that names none of them".to_owned(),
    }
}

/// The Grep tool's call judged: its `path` (the working directory when none), `glob` and `type`, read as ripgrep reads them.
pub(super) fn grep_tool(input: &Value, cwd: &str, top: &str, held: &[&str]) -> Option<Found> {
    let path = Some(field(input, "path"))
        .filter(|p| !p.is_empty())
        .unwrap_or(".");
    let mut filter = Filter {
        bypass_named: true,
        ..Filter::default()
    };
    let glob = field(input, "glob");
    if !glob.is_empty() && one_glob(glob) {
        filter.globs.push(RgGlob::new(glob, false));
    }
    let kind = field(input, "type");
    if !kind.is_empty() {
        filter.types_in.push(kind.to_owned());
    }
    let search = Search {
        tool: Tool::GrepCall,
        roots: vec![Root::new(path, cwd, top, true)],
        filter,
    };
    reached(&search, cwd, top, held).err()
}

/// A shell command judged: the first search that reaches a held file, or the command with every segment that is not a read blanked
/// (`make phase-read`, a listing, a search judged and passed), for the whole-command rule to read.
pub(super) fn shell(line: &str, cwd: &str, top: &str, held: &[&str]) -> Result<String, Found> {
    shell_in(line, cwd, top, held, None)
}

/// `shell`, for a line that fills the arguments of `outer` (the inside of a quoted `$(...)`).
fn shell_in(
    line: &str,
    cwd: &str,
    top: &str,
    held: &[&str],
    outer: Option<&str>,
) -> Result<String, Found> {
    let mut text: Vec<char> = line.chars().collect();
    let mut here = cwd.to_owned();
    let segs = segments(line);
    for (k, seg) in segs.iter().enumerate() {
        let w = command(&seg.words);
        inner(&seg.words, &w, &here, top, held)?;
        let host = seg.host.as_deref().or(outer.filter(|_| seg.opened));
        let host_reads = !seg.piped && reads(host);
        let kind = match w.first().copied() {
            // a command whose output fills a reader's arguments, through `$(...)` or backticks
            Some(_) if host_reads => Kind::Search(Box::new(producer_search(&w, &here, top))),
            Some("cd") => {
                if let Some(d) = w.get(1) {
                    here = Path::new(&here).join(d).to_string_lossy().into_owned();
                }
                Kind::Other
            }
            Some("make") if w.contains(&"phase-read") => Kind::NotRead,
            Some("git") => git_segment(&w, &here, top),
            Some(g) if GREPS.contains(&g) => {
                Kind::Search(Box::new(grep_search(&w[1..], &here, top, seg.piped)))
            }
            Some(t @ ("rg" | "ag")) => {
                let tool = if t == "rg" { Tool::Rg } else { Tool::Ag };
                rg_ag_search(tool, &w[1..], &here, top, seg.piped)
                    .map_or(Kind::NotRead, |s| Kind::Search(Box::new(s)))
            }
            Some("find") => {
                exec_reader(&w).map_or(Kind::Other, |(cmd, args)| {
                    // a grep's own exclusions count beside the find's; any other reader's arguments leave nothing out
                    let args: Vec<&str> = args
                        .iter()
                        .map(String::as_str)
                        .filter(|_| GREPS.contains(&cmd.as_str()))
                        .collect();
                    Kind::Search(Box::new(find_search(&w[1..], &args, &here, top)))
                })
            }
            Some("xargs") => xargs_reader(&w).map_or(Kind::Other, |fed| {
                Kind::Search(Box::new(xargs_fed(&segs, k, &fed, &here, top)))
            }),
            r if reads(r) => {
                glob_args(&w, &here, top).map_or(Kind::Other, |s| Kind::Search(Box::new(s)))
            }
            _ => Kind::Other,
        };
        match kind {
            Kind::Other => continue,
            Kind::Search(search) => {
                if !reached(&search, &here, top, held)? {
                    continue;
                }
            }
            Kind::NotRead => {}
        }
        if let Some((from, to)) = seg.span {
            text[from..to].iter_mut().for_each(|c| *c = ' ');
        }
    }
    Ok(text.into_iter().collect())
}

/// The commands a segment runs inside one of its words: a `$(...)` or backtick span kept whole by its quotes, and the script a
/// shell's `-c` runs (T204 review: `echo "$(grep -rn X <parent>)"` and `bash -c '...'` were never judged).
fn inner(words: &[String], w: &[&str], here: &str, top: &str, held: &[&str]) -> Result<(), Found> {
    for word in words.iter().filter(|x| x.contains("$(") || x.contains('`')) {
        shell_in(word, here, top, held, w.first().copied())?;
    }
    if matches!(w.first(), Some(&("bash" | "sh" | "zsh" | "dash"))) {
        let at = w
            .iter()
            .position(|x| x.starts_with('-') && !x.starts_with("--") && x.ends_with('c'));
        if let Some(script) = at.and_then(|k| w.get(k + 1)) {
            shell(script, here, top, held)?;
        }
    }
    Ok(())
}

/// What one segment is to the guard: a search to judge, a command that prints no line of a file, or anything else.
enum Kind {
    Search(Box<Search>),
    NotRead,
    Other,
}

/// Where a git command's subcommand stands, past its global options, and the directory `-C` moves it to.
fn git_sub(w: &[&str], cwd: &str) -> (usize, String) {
    let (mut i, mut here) = (1, cwd.to_owned());
    while i < w.len() && w[i].starts_with('-') {
        if matches!(w[i], "-C" | "-c") {
            if w[i] == "-C" {
                here = Path::new(&here)
                    .join(w.get(i + 1).unwrap_or(&"."))
                    .to_string_lossy()
                    .into_owned();
            }
            i += 1;
        }
        i += 1;
    }
    (i, here)
}

/// A git segment: a listing that prints no line of a file (`status` without `-v`; `diff` or `log` with names or counts and no patch
/// flag - not `show`, which prints a blob whatever its flags), `git grep`'s search, or anything else.
fn git_segment(w: &[&str], cwd: &str, top: &str) -> Kind {
    let (i, here) = git_sub(w, cwd);
    let rest = w.get(i + 1..).unwrap_or_default();
    let names = [
        "--stat",
        "--name-only",
        "--name-status",
        "--numstat",
        "--shortstat",
    ];
    // every flag that prints a patch beside the names (T204 review: `--cc`, `-c`, `--binary`, `-L` each do)
    let patch = |a: &&str| {
        matches!(
            *a,
            "-p" | "--patch"
                | "-u"
                | "--patch-with-stat"
                | "--patch-with-raw"
                | "-c"
                | "--cc"
                | "--binary"
                | "--color-words"
        ) || ["-U", "--unified", "-L", "--word-diff"]
            .iter()
            .any(|p| a.starts_with(p))
    };
    let verbose = |a: &&str| matches!(*a, "-v" | "-vv" | "--verbose");
    let counts = rest
        .iter()
        .any(|a| names.contains(&a.split('=').next().unwrap_or(a)));
    let listing = counts && !rest.iter().any(patch);
    match w.get(i).copied() {
        Some("status") if !rest.iter().any(verbose) => Kind::NotRead,
        Some("diff" | "log") if listing => Kind::NotRead,
        Some("grep") => Kind::Search(Box::new(git_grep_search(rest, &here, top))),
        _ => Kind::Other,
    }
}
