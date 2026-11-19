//! Each search tool's words read into a `Search` (T204): GNU grep and its kin, ripgrep, ag, `git grep`, and a `find` running a grep.

use std::path::Path;

use super::filter::{rel_to, Filter, FindTest, RgGlob, Root, Style};
use super::{Search, Tool};
use crate::guards::finished_run_hooks::runs::realpath;
/// A tool's words parsed: (flag, value) in order, and the positional words. `short` lists the short flags that take a value,
/// `long` the long ones.
pub(super) fn options(
    args: &[&str],
    short: &str,
    long: &[&str],
) -> (Vec<(String, String)>, Vec<String>) {
    let (mut opts, mut pos) = (Vec::new(), Vec::new());
    let mut it = args.iter();
    while let Some(&a) = it.next() {
        if a == "--" {
            pos.extend(it.by_ref().map(|s| (*s).to_owned()));
        } else if let Some(name) = a.strip_prefix("--") {
            let (name, value) = match name.split_once('=') {
                Some((n, v)) => (n, v.to_owned()),
                None if long.contains(&name) => (name, it.next().map_or("", |v| v).to_owned()),
                None => (name, String::new()),
            };
            opts.push((format!("--{name}"), value));
        } else if a.len() > 1 && a.starts_with('-') {
            for (k, ch) in a.char_indices().skip(1) {
                if short.contains(ch) {
                    let rest = &a[k + ch.len_utf8()..];
                    let value = if rest.is_empty() {
                        it.next().map_or("", |v| v)
                    } else {
                        rest
                    };
                    opts.push((format!("-{ch}"), value.to_owned()));
                    break;
                }
                opts.push((format!("-{ch}"), String::new()));
            }
        } else {
            pos.push(a.to_owned());
        }
    }
    (opts, pos)
}

pub(super) fn has(opts: &[(String, String)], names: &[&str]) -> bool {
    opts.iter().any(|(k, _)| names.contains(&k.as_str()))
}

pub(super) fn values<'a>(opts: &'a [(String, String)], names: &[&str]) -> Vec<String> {
    opts.iter()
        .filter(|(k, _)| names.contains(&k.as_str()))
        .map(|(_, v): &'a (String, String)| v.clone())
        .collect()
}

pub(super) const GREP_LONG: &[&str] = &[
    "regexp",
    "file",
    "max-count",
    "after-context",
    "before-context",
    "context",
    "directories",
    "devices",
    "include",
    "exclude",
    "exclude-dir",
    "exclude-from",
    "label",
    "binary-files",
    "group-separator",
];
pub(super) const RG_LONG: &[&str] = &[
    "regexp",
    "file",
    "glob",
    "iglob",
    "type",
    "type-not",
    "after-context",
    "before-context",
    "context",
    "max-count",
    "max-columns",
    "threads",
    "encoding",
    "replace",
    "max-depth",
    "sort",
    "sortr",
    "pre",
    "pre-glob",
    "type-add",
    "type-clear",
    "colors",
    "color",
    "engine",
    "max-filesize",
    "ignore-file",
    "context-separator",
    "field-match-separator",
    "field-context-separator",
    "path-separator",
    "dfa-size-limit",
    "regex-size-limit",
    "hyperlink-format",
    "generate",
];
pub(super) const AG_LONG: &[&str] = &[
    "after",
    "before",
    "context",
    "file-search-regex",
    "ignore",
    "ignore-dir",
    "max-count",
    "path-to-ignore",
    "pager",
    "depth",
    "workers",
    "width",
];

/// GNU grep and its kin: recursive only when asked, the working directory its default only then and only when nothing is piped in.
pub(super) fn grep_search(args: &[&str], cwd: &str, top: &str, piped: bool) -> Search {
    let (opts, pos) = options(args, "efmABCdD", GREP_LONG);
    let recursive = has(
        &opts,
        &["-r", "-R", "--recursive", "--dereference-recursive"],
    ) || values(&opts, &["-d", "--directories"])
        .iter()
        .any(|v| v == "recurse");
    let skip = usize::from(!has(&opts, &["-e", "-f", "--regexp", "--file"]));
    let mut paths: Vec<String> = pos.into_iter().skip(skip).collect();
    if paths.is_empty() && recursive && !piped {
        paths.push(".".to_owned());
    }
    let filter = Filter {
        grep_ex: values(&opts, &["--exclude"]),
        grep_in: values(&opts, &["--include"]),
        grep_ex_dir: values(&opts, &["--exclude-dir"]),
        ..Filter::default()
    };
    let roots = paths
        .iter()
        .map(|p| Root::new(p, cwd, top, recursive))
        .collect();
    Search {
        tool: Tool::Grep,
        roots,
        filter,
    }
}

/// ripgrep and ag: recursive, the working directory their default when nothing is piped in; a file named is searched whatever the
/// globs say. None for a listing of names (`rg --files`, `ag -g`), which prints no line of a file.
pub(super) fn rg_ag_search(
    tool: Tool,
    args: &[&str],
    cwd: &str,
    top: &str,
    piped: bool,
) -> Option<Search> {
    let rg = tool == Tool::Rg;
    let (opts, pos) = if rg {
        options(args, "efgtTABCmMjErd", RG_LONG)
    } else {
        options(args, "ABCGgmpW", AG_LONG)
    };
    if has(
        &opts,
        if rg {
            &["--files", "--type-list"]
        } else {
            &["-g"]
        },
    ) {
        return None;
    }
    let skip = usize::from(!has(&opts, &["-e", "-f", "--regexp", "--file"]));
    let mut paths: Vec<String> = pos.into_iter().skip(skip).collect();
    if paths.is_empty() && !piped {
        paths.push(".".to_owned());
    }
    let mut filter = Filter {
        bypass_named: true,
        ..Filter::default()
    };
    if rg {
        for (flag, g) in &opts {
            if matches!(flag.as_str(), "-g" | "--glob" | "--iglob") {
                filter.globs.push(RgGlob::new(g, flag == "--iglob"));
            }
        }
        filter.types_in = values(&opts, &["-t", "--type"]);
        filter.types_out = values(&opts, &["-T", "--type-not"]);
    } else {
        filter.ag_ignore = values(&opts, &["--ignore", "--ignore-dir"]);
        filter.ag_regex = values(&opts, &["-G", "--file-search-regex"]);
    }
    let roots = paths.iter().map(|p| Root::new(p, cwd, top, true)).collect();
    Some(Search {
        tool,
        roots,
        filter,
    })
}

/// `git grep`: its pathspecs relative to the working directory (`:/` and `top` from the checkout's), `:!`, `:^` and `exclude` leaving
/// paths out; no positive pathspec searches the working directory. Before `--`, a word naming no path is a revision, as git reads it,
/// and `<rev>:<path>` searches that path of the revision (T204 review: `git grep x HEAD:<held dir>` printed the held code).
pub(super) fn git_grep_search(args: &[&str], cwd: &str, top: &str) -> Search {
    let dashes = args.iter().position(|a| *a == "--");
    let (before, after) = dashes.map_or((args, &[][..]), |k| (&args[..k], &args[k + 1..]));
    let long = [
        "max-depth",
        "threads",
        "context",
        "after-context",
        "before-context",
        "max-count",
    ];
    let (opts, pos) = options(before, "efABCm", &long);
    let skip = usize::from(!has(&opts, &["-e", "-f"]));
    let base = rel_to(&realpath(Path::new(cwd)).to_string_lossy(), top).unwrap_or_default();
    let mut roots = Vec::new();
    let mut specs: Vec<&str> = Vec::new();
    for word in pos.iter().skip(skip) {
        if let Some((_, path)) = word.split_once(':').filter(|_| !word.starts_with(':')) {
            let from = path
                .strip_prefix("./")
                .map_or(path.to_owned(), |p| format!("{base}/{p}"));
            roots.push(Root::new(&format!("{top}/{from}"), cwd, top, true));
            if let Some(r) = roots.last_mut() {
                r.written.clone_from(word);
            }
        } else if word.starts_with(':') || Path::new(cwd).join(word).exists() {
            specs.push(word);
        }
    }
    specs.extend(after);
    let (more, filter) = pathspecs(&specs, cwd, top);
    roots.extend(more);
    if roots.is_empty() {
        roots.push(Root::new(".", cwd, top, true));
    }
    Search {
        tool: Tool::GitGrep,
        roots,
        filter,
    }
}

/// Git pathspecs read: the positive ones as roots, `:!`, `:^` and `exclude` as paths left out.
fn pathspecs(specs: &[&str], cwd: &str, top: &str) -> (Vec<Root>, Filter) {
    let base = rel_to(&realpath(Path::new(cwd)).to_string_lossy(), top).unwrap_or_default();
    let (mut roots, mut filter) = (Vec::new(), Filter::default());
    for &spec in specs {
        let (magic, path) = if let Some(rest) = spec.strip_prefix(":(") {
            rest.split_once(')').map_or(("", rest), |(m, p)| (m, p))
        } else if let Some(rest) = spec.strip_prefix(':') {
            let n = rest
                .find(|c: char| !matches!(c, '!' | '^' | '/'))
                .unwrap_or(rest.len());
            (&rest[..n], &rest[n..])
        } else {
            ("", spec)
        };
        let words: Vec<&str> = magic.split(',').collect();
        let from_top = magic.contains('/') || words.contains(&"top");
        let joined = if from_top || base.is_empty() {
            path.to_owned()
        } else {
            format!("{base}/{path}")
        };
        let rel = crate::shared::tree::normpath(&joined);
        let rel = if rel == "." { String::new() } else { rel };
        if magic.contains(['!', '^']) || words.contains(&"exclude") {
            filter.specs_out.push(rel);
        } else {
            roots.push(Root::new(&format!("{top}/{rel}"), cwd, top, true));
            if let Some(r) = roots.last_mut() {
                spec.clone_into(&mut r.written);
            }
        }
    }
    (roots, filter)
}

/// What a command that hands a reader its file names could list (T204, the plan review's second round): `find`; `ls` (its
/// directories' own files, or all below with -R; `-I`/`--ignore` a base name left out, as GNU ls reads it); `git ls-files` (its
/// pathspecs, the working directory without one); `tree` (`-I` a base name, or several joined by `|`); `fd` and `fdfind` (the pattern,
/// then its paths; `-E` a glob left out); `locate` (the whole checkout); `echo` and `printf` (their words, as paths); `git rev-parse`,
/// `pwd`, `date`, `basename`, `dirname`, `whoami`, `hostname` (no file of the checkout). Anything else - a
/// list file, a script, a variable - could name any file under the working directory.
pub(super) fn producer_search(w: &[&str], cwd: &str, top: &str) -> Search {
    let args = w.get(1..).unwrap_or_default();
    let nothing = || Search {
        tool: Tool::Narrow,
        roots: Vec::new(),
        filter: Filter::default(),
    };
    match w.first().copied().unwrap_or_default() {
        "find" => find_search(args, &[], cwd, top),
        name @ ("ls" | "tree" | "fd" | "fdfind") => lister(name, args, cwd, top),
        "git" => {
            let (at, here) = super::git_sub(w, cwd);
            match w.get(at).copied() {
                Some("rev-parse") => nothing(),
                Some("ls-files") => {
                    let specs: Vec<&str> = w[at + 1..]
                        .iter()
                        .filter(|a| !a.starts_with('-'))
                        .copied()
                        .collect();
                    let (mut roots, filter) = pathspecs(&specs, &here, top);
                    if roots.is_empty() {
                        roots.push(Root::new(".", &here, top, true));
                    }
                    Search {
                        tool: Tool::GitGrep,
                        roots,
                        filter,
                    }
                }
                _ => unknown(w, cwd, top),
            }
        }
        "echo" | "printf" => {
            let words: Vec<String> = args
                .iter()
                .filter(|a| !a.starts_with('-'))
                .map(|a| (*a).to_owned())
                .collect();
            let roots = words
                .iter()
                .map(|p| Root::new(p, cwd, top, false))
                .collect();
            Search {
                tool: Tool::Narrow,
                roots,
                filter: Filter::default(),
            }
        }
        // a directory or a word, never a file of the checkout's list
        "pwd" | "date" | "basename" | "dirname" | "whoami" | "hostname" => nothing(),
        "locate" | "plocate" | "mlocate" => Search {
            tool: Tool::Narrow,
            roots: vec![Root::new(top, cwd, top, true)],
            filter: Filter::default(),
        },
        _ => unknown(w, cwd, top),
    }
}

/// `ls`, `tree`, `fd` and `fdfind` read: their paths (the working directory without one) and what their flags leave out.
fn lister(name: &str, args: &[&str], cwd: &str, top: &str) -> Search {
    let roots_of = |paths: &[String], recursive: bool| -> Vec<Root> {
        let dot = [".".to_owned()];
        let paths = if paths.is_empty() { &dot[..] } else { paths };
        paths
            .iter()
            .map(|p| Root::new(p, cwd, top, recursive))
            .collect()
    };
    let mut filter = Filter::default();
    let (tool, roots) = match name {
        "ls" => {
            let (opts, pos) = options(
                args,
                "IwT",
                &["ignore", "hide", "width", "tabsize", "format", "sort"],
            );
            filter.grep_ex = values(&opts, &["-I", "--ignore"]);
            (Tool::Ls, roots_of(&pos, has(&opts, &["-R", "--recursive"])))
        }
        "tree" => {
            let (opts, pos) = options(args, "LIPo", &["filelimit", "charset", "sort", "timefmt"]);
            for v in values(&opts, &["-I"]) {
                filter.grep_ex.extend(v.split('|').map(str::to_owned));
            }
            (Tool::Tree, roots_of(&pos, true))
        }
        _ => {
            let long = [
                "exclude",
                "extension",
                "type",
                "max-depth",
                "exec",
                "exec-batch",
            ];
            let (opts, pos) = options(args, "EetdcjxXgS", &long);
            for g in values(&opts, &["-E", "--exclude"]) {
                filter.globs.push(RgGlob::new(&format!("!{g}"), false));
            }
            (Tool::Fd, roots_of(pos.get(1..).unwrap_or_default(), true))
        }
    };
    Search {
        tool,
        roots,
        filter,
    }
}

/// A producer this module cannot read: it could name any file under the working directory.
fn unknown(w: &[&str], cwd: &str, top: &str) -> Search {
    let mut root = Root::new(".", cwd, top, true);
    root.written = format!("what `{}` lists", w.join(" "));
    Search {
        tool: Tool::Narrow,
        roots: vec![root],
        filter: Filter::default(),
    }
}

/// `find`'s start points and its expression's name and path tests (`-o` makes its positive tests unreadable); the grep it runs adds
/// its own exclusions.
pub(super) fn find_search(find: &[&str], grep: &[&str], cwd: &str, top: &str) -> Search {
    let mut at = 0;
    while at < find.len() && matches!(find[at], "-H" | "-L" | "-P") {
        at += 1;
    }
    let roots_end = (at..find.len())
        .find(|&i| find[i].starts_with('-') || find[i] == "!" || find[i] == "(")
        .unwrap_or(find.len());
    let mut written: Vec<&str> = find[at..roots_end].to_vec();
    if written.is_empty() {
        written.push(".");
    }
    let mut filter = grep_search(grep, cwd, top, true).filter;
    let (mut neg, mut last) = (false, "");
    let mut words = find[roots_end..].iter();
    while let Some(&w) = words.next() {
        match w {
            "!" | "-not" => neg = true,
            "-name" | "-iname" | "-path" | "-ipath" | "-wholename" | "-iwholename" => {
                let glob = words.next().map_or("", |g| g).to_owned();
                filter.find.push(FindTest {
                    path: !w.ends_with("name") || w.ends_with("wholename"),
                    style: Style {
                        cross: true,
                        braces: false,
                        fold: w.starts_with("-i"),
                    },
                    glob,
                    neg,
                    prune: false,
                });
                neg = false;
            }
            "-prune" => {
                if let Some(t) = filter.find.last_mut() {
                    t.prune = true;
                }
            }
            "-o" | "-or" => filter.find_or |= last != "-prune",
            "-exec" | "-execdir" | "-ok" | "-okdir" => break,
            _ => {}
        }
        last = w;
    }
    let roots = written
        .iter()
        .map(|p| Root::new(p, cwd, top, true))
        .collect();
    Search {
        tool: Tool::Find,
        roots,
        filter,
    }
}
