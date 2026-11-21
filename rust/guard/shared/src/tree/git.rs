//! What a git invocation writes (`_git_write`; 451 T50 moved it out of `tree.rs`, past the file-scale bar): `GIT_WRITES` and a
//! writing `branch` where git runs, a read-only subcommand's output file (451 T33), and the tree the twelve subcommands outside
//! `GIT_WRITES` change (451 T50), each read from its own `-h` and measured.

use super::{path_write, resolve, strip_quote_chars, Env, Write};

const GIT_WRITES: [&str; 17] = [
    "commit",
    "add",
    "merge",
    "rebase",
    "reset",
    "checkout",
    "restore",
    "rm",
    "mv",
    "apply",
    "am",
    "stash",
    "cherry-pick",
    "push",
    "pull",
    "clean",
    "tag",
];

const BRANCH_WRITE_FLAGS: [&str; 16] = [
    "-d",
    "-D",
    "-m",
    "-M",
    "-c",
    "-C",
    "-f",
    "-u",
    "--delete",
    "--move",
    "--copy",
    "--force",
    "--set-upstream-to",
    "--unset-upstream",
    "--edit-description",
    "--track",
];
const BRANCH_LIST_FLAGS: [&str; 11] = [
    "-l",
    "--list",
    "-r",
    "--remotes",
    "-a",
    "--all",
    "--contains",
    "--no-contains",
    "--merged",
    "--no-merged",
    "--points-at",
];
const BRANCH_LIST_SHOW: &str = "--show-current";
const BRANCH_VALUE_FLAGS: [&str; 8] = [
    "--contains",
    "--no-contains",
    "--merged",
    "--no-merged",
    "--points-at",
    "--sort",
    "--format",
    "--column",
];

fn branch_writes(args: &[&str]) -> bool {
    let flags: Vec<&str> = args
        .iter()
        .filter(|a| a.starts_with('-'))
        .map(|a| a.split('=').next().unwrap_or(a))
        .collect();
    if flags.iter().any(|f| BRANCH_WRITE_FLAGS.contains(f))
        || args.iter().any(|a| a.starts_with("--set-upstream-to="))
    {
        return true;
    }
    let (mut names, mut skip) = (0, false);
    for a in args {
        if skip {
            skip = false;
        } else if a.starts_with('-') {
            skip = BRANCH_VALUE_FLAGS.contains(a);
        } else {
            names += 1;
        }
    }
    names > 0
        && !flags
            .iter()
            .any(|f| BRANCH_LIST_FLAGS.contains(f) || *f == BRANCH_LIST_SHOW)
}

/// (target, how) of each place a git invocation writes (`_git_write`).
pub(super) fn git_write(toks: &[&str], env: &Env, home: &str, eff: Option<&str>) -> Vec<Write> {
    let (mut i, mut c_path) = (1, None);
    while i < toks.len() {
        let t = toks[i];
        if (t == "-C" || t == "-c") && i + 1 < toks.len() {
            if t == "-C" {
                c_path = Some(toks[i + 1]);
            }
            i += 2;
        } else if t.starts_with('-') {
            i += 1;
        } else {
            break;
        }
    }
    let Some(&sub) = toks.get(i) else {
        return Vec::new();
    };
    let (at, at_how) = match c_path {
        None => (eff.map(str::to_owned), "shell"),
        Some(c) if strip_quote_chars(c).starts_with('/') => (resolve(c, env, home, eff), "named"),
        Some(c) => (resolve(c, env, home, eff), "shell"),
    };
    // a stash's `list` and `show` only read (451 T33: its gate's shell-write check refused `git stash list` as a write of `.`)
    let stash_reads = sub == "stash" && matches!(toks.get(i + 1).copied(), Some("list" | "show"));
    if (GIT_WRITES.contains(&sub) && !stash_reads)
        || (sub == "branch" && branch_writes(&toks[i + 1..]))
    {
        return vec![(at, at_how)];
    }
    // 451 T33: a read-only subcommand's writing option lands where it names, relative to where git runs; 451 T50: so does a
    // tree one of the twelve below writes
    let args = &toks[i + 1..];
    let place = |word: Option<&str>| match word {
        None => (at.clone(), at_how),
        Some(file) => {
            let (path, how) = path_write(file, env, home, at.as_deref());
            (path, if how == "shell" { at_how } else { how })
        }
    };
    if let Some(words) = git_tree(sub, args) {
        // 451 T50: a place the walk cannot resolve is not read toward the mirror (D6) for these forms, which HEAD read as no
        // write - its replay moved tx#63, `T=$(mktemp -d); ...; git clone -q . $T/clone` standing in the mirror, a scratch clone,
        // allowed -> refused that way (measured 2026-11-21); it fails open, as the gate's unresolvable path does
        return words
            .iter()
            .map(|w| place(w.as_deref()))
            .filter(|(path, _)| path.is_some())
            .collect();
    }
    git_output(sub, args).map(place).into_iter().collect()
}

/// Each of the twelve's options that take the next word as their value (451 T50), read from its own `-h` - `git <sub> -h`, and
/// `git worktree <action> -h`, `git config set -h` and `git config get -h` - by `/tmp/t50/scripts/valued.py`, measured 2026-11-21
/// (git 2.53.0): one list a subcommand, since one for all twelve misread `-f`, `worktree`'s `--force` and `config`'s `--file` (the
/// review of T33's addition, 2026-11-20). `bisect`'s `--term-*` show only `=` in its usage, yet take the next word too (`git
/// bisect start --term-new fixed HEAD HEAD~5` named its term `fixed`, measured 2026-11-21); `sparse-checkout`, `submodule`,
/// `fetch`, `notes`, `update-ref` and `symbolic-ref` need none: their action leads, or no form writes a tree.
const GIT_VALUED: [(&str, &[&str]); 6] = [
    ("worktree", &["-b", "-B", "--reason", "--expire"]),
    (
        "clone",
        &[
            "-j",
            "-o",
            "-b",
            "-u",
            "-c",
            "--jobs",
            "--template",
            "--reference",
            "--reference-if-able",
            "--origin",
            "--branch",
            "--revision",
            "--upload-pack",
            "--depth",
            "--shallow-since",
            "--shallow-exclude",
            "--separate-git-dir",
            "--ref-format",
            "--config",
            "--server-option",
            "--filter",
            "--bundle-uri",
        ],
    ),
    (
        "init",
        &[
            "-b",
            "--template",
            "--separate-git-dir",
            "--initial-branch",
            "--object-format",
            "--ref-format",
        ],
    ),
    (
        "switch",
        &[
            "-c",
            "-C",
            "--create",
            "--force-create",
            "--conflict",
            "--orphan",
        ],
    ),
    (
        "bisect",
        &["--term-good", "--term-old", "--term-bad", "--term-new"],
    ),
    (
        "config",
        &[
            "-f",
            "--file",
            "--blob",
            "-t",
            "--type",
            "--value",
            "--comment",
            "--default",
            "--url",
        ],
    ),
];

/// A git subcommand's operands past its options (`valued`'s take the next word, unless written `--name=value`; all past `--`),
/// the names of the options given, and whether the walk cut them: a `\` ends the line, or a word ends in the `$` of a `${` the
/// segments split at (main-tree#10's `"https://x-access-token:${PAT}@github.com/..."`, 451 T50's replay) - the operands go on in
/// pieces the walk reads as commands of their own, so the word and those after it are not read.
fn operands<'a>(args: &[&'a str], valued: &[&str]) -> (Vec<&'a str>, Vec<&'a str>, bool) {
    let (mut ops, mut flags, mut dashed, mut it) = (Vec::new(), Vec::new(), false, args.iter());
    while let Some(&a) = it.next() {
        if a == "\\" || a.ends_with('$') {
            return (ops, flags, true);
        } else if dashed || a == "-" || !a.starts_with('-') {
            ops.push(a);
        } else if a == "--" {
            dashed = true;
        } else {
            let name = a.split('=').next().unwrap_or(a);
            if name == a && valued.contains(&a) {
                it.next();
            }
            flags.push(name);
        }
    }
    (ops, flags, false)
}

/// The directory `clone` makes where no operand names one, as git names it (`git_url_basename`): the repository's last path part,
/// a trailing `/` or `/.git` and a `.git` dropped, `.git` added for `--bare` or `--mirror` (measured 2026-11-21: `/src/y/`,
/// `/src/y/.git` and `file:///src/y` made `y`, `--bare /src/y` and `--mirror /src/y/.git` made `y.git`); None where the walk cannot
/// read the name (a variable, a blanked quote), and then the clone lands where git runs.
fn clone_name(repo: &str, bare: bool) -> Option<String> {
    let r = repo.trim_end_matches('/');
    let r = r.strip_suffix("/.git").unwrap_or(r);
    let last = r.rsplit(['/', ':']).next().unwrap_or(r);
    let name = last.strip_suffix(".git").unwrap_or(last);
    (!name.is_empty()
        && name
            .chars()
            .all(|c| c.is_alphanumeric() || "._-".contains(c)))
    .then(|| {
        if bare {
            format!("{name}.git")
        } else {
            name.to_owned()
        }
    })
}

/// Where one of the twelve subcommands outside `GIT_WRITES` writes (451 T50): None not one of them; else each write, `Some(word)`
/// a path it names (relative to where git runs), `None` where git runs - empty for a form that writes only `.git` or nothing.
/// Each form's write measured 2026-11-21 (git 2.53.0, run in a scratch repository and its work tree, `.git`, the directory
/// beside it and the home compared before and after, `/tmp/t50/scripts/writes.sh`, `/tmp/t50/writes.txt`):
/// - `worktree add`, `remove` and `move` make, delete or move the work tree they name; `list`, `prune`, `lock`, `unlock` and
///   `repair` write `.git` or nothing.
/// - `clone` makes the directory its second operand names, else one named from the repository where git runs.
/// - `init <dir>` makes `<dir>` (an existing one gets only its `.git`: the walk reads no disk, so it reads the making - the class
///   is the same, a directory and its `.git` landing in one place); `init` with no directory writes `.git` where it runs, `init
///   --bare` the repository's own files there.
/// - `switch` checks out a branch or a start point (and `--orphan` empties the tree); `-c`/`-C` with no start point, or
///   `--detach` with none, moves only HEAD.
/// - `bisect` checks out a commit at `start` with a bad and a good (unless `--no-checkout`), and may at every step after
///   (`good`, `bad`, `skip`, `next`, `reset`, `replay`, `run`, a term of its own); `log`, `view`, `visualize`, `terms` and `help`
///   only read.
/// - `sparse-checkout set`, `add`, `reapply`, `disable` and `init` add or remove the tree's files; `list` and `check-rules` read.
/// - `submodule add`, `update`, `deinit`, `set-branch` and `set-url` write a submodule's tree or `.gitmodules`, and `foreach`
///   runs a command in each tree that the walk does not read (a write where git runs, as an unread program is); `init`, `sync`,
///   `absorbgitdirs`, `status` and `summary` write `.git` or nothing.
/// - `config`'s writing forms write `--file`'s file, `--global`'s `~/.gitconfig` (or the XDG file when only it is there - the home
///   either way) and `--system`'s `/etc/gitconfig`, else `.git/config`; its read forms (`get`, `list`, `--get*`, `-l`, a lone
///   name) and `--blob` write nothing.
/// - `fetch` (`--dry-run` and `-n`, which is `--no-tags`, included), `notes`, `update-ref` and `symbolic-ref` write `.git` alone
///   in every form, so they reach `git_output`, which finds no write for them.
fn git_tree(sub: &str, args: &[&str]) -> Option<Vec<Option<String>>> {
    let valued = GIT_VALUED
        .iter()
        .find(|(s, _)| *s == sub)
        .map_or(&[][..], |(_, v)| *v);
    // `bisect start`'s revisions stand before its `--`, its pathspecs after
    let before = args.split(|a| *a == "--").next().unwrap_or(args);
    let (ops, flags, cut) = operands(if sub == "bisect" { before } else { args }, valued);
    let has = |f: &str| flags.contains(&f);
    let word = |w: &str| Some(w.to_owned());
    let here = vec![None];
    Some(match (sub, ops.first().copied()) {
        ("worktree", Some("add" | "remove")) => ops.get(1).map(|p| word(p)).into_iter().collect(),
        ("worktree", Some("move")) => ops.iter().skip(1).take(2).map(|p| word(p)).collect(),
        ("clone", _) => match ops[..] {
            [_, dir, ..] => vec![word(dir)],
            [repo] if !cut => vec![clone_name(repo, has("--bare") || has("--mirror"))],
            _ => Vec::new(),
        },
        ("init", Some(dir)) if !matches!(dir, "." | "./") => vec![word(dir)],
        ("init", _) if has("--bare") && !cut => here,
        ("switch", first) if first.is_some() || has("--orphan") => here,
        ("bisect", Some("start")) if has("--no-checkout") || ops.len() < 3 => Vec::new(),
        ("bisect", Some(a)) if !matches!(a, "log" | "view" | "visualize" | "terms" | "help") => {
            here
        }
        ("sparse-checkout", Some("set" | "add" | "reapply" | "disable" | "init"))
        | ("submodule", Some("add" | "update" | "deinit" | "set-branch" | "set-url" | "foreach")) => {
            here
        }
        ("config", action) => config_file(args, action, &ops, &flags)
            .map(Some)
            .into_iter()
            .collect(),
        ("worktree" | "init" | "switch" | "bisect" | "sparse-checkout" | "submodule", _) => {
            Vec::new()
        }
        _ => return None,
    })
}

/// The file a `config` writes outside `.git` (451 T50, its forms in `git_tree`'s comment): None for a read, `--blob`, or
/// `.git/config`.
fn config_file(
    args: &[&str],
    action: Option<&str>,
    ops: &[&str],
    flags: &[&str],
) -> Option<String> {
    let any = |names: &[&str]| flags.iter().any(|f| names.contains(f));
    let reads = [
        "--get",
        "--get-all",
        "--get-regexp",
        "--get-urlmatch",
        "-l",
        "--list",
        "--get-color",
        "--get-colorbool",
    ];
    let writes = [
        "--add",
        "--replace-all",
        "--unset",
        "--unset-all",
        "--rename-section",
        "--remove-section",
        "-e",
        "--edit",
    ];
    let writing = match action {
        Some("set" | "unset" | "rename-section" | "remove-section" | "edit") => true,
        Some("get" | "list") => false,
        _ => any(&writes) || (!any(&reads) && ops.len() > 1),
    };
    if !writing || any(&["--blob"]) {
        return None;
    }
    let file = option_value(args, &["-f", "--file"])
        .or_else(|| any(&["--global"]).then_some("~/.gitconfig"))
        .or_else(|| any(&["--system"]).then_some("/etc/gitconfig"))?;
    Some(file.to_owned())
}

/// The value of the first of `names` given, written `--name=value` or `--name value` (git takes no long option abbreviated in
/// these, measured 2026-11-20).
fn option_value<'a>(args: &[&'a str], names: &[&str]) -> Option<&'a str> {
    args.iter().enumerate().find_map(|(k, a)| {
        names.iter().find_map(|n| {
            a.strip_prefix(n)
                .and_then(|rest| rest.strip_prefix('='))
                .or_else(|| (*a == *n).then(|| args.get(k + 1).copied()).flatten())
        })
    })
}

/// Where a subcommand outside `GIT_WRITES` writes a file (451 T33): `Some(Some(word))` the file or directory an option names,
/// `Some(None)` where git runs, None nowhere. Found as T44 found its screen, measured 2026-11-20 (git 2.53.0, each subcommand's
/// `--git-completion-helper` in a scratch repository, searched for an output file or directory): the diff options' `--output`
/// (`diff`, `diff-tree`, `diff-files`, `diff-index`, `range-diff`, `rev-list`, and `log`, `show`, `whatchanged` through them),
/// `archive`'s `-o`/`--output`, `format-patch`'s `-o`/`--output-directory` (else the files land where it runs, unless
/// `--stdout`), `bundle create`'s file, `bugreport`'s and `diagnose`'s `-o`/`--output-directory`. git takes none of them
/// abbreviated (`--outpu=`, `--outp=` exit 129, measured 2026-11-20), so only the whole name is read.
#[expect(
    clippy::option_option,
    reason = "three answers: no write, a write where git runs, a write where a word names"
)]
fn git_output<'a>(sub: &str, args: &[&'a str]) -> Option<Option<&'a str>> {
    let value = |names: &[&str]| option_value(args, names);
    if let Some(file) = value(&["--output"]) {
        return Some(Some(file));
    }
    match sub {
        "archive" => value(&["-o"]).map(Some),
        "bundle" => args
            .first()
            .filter(|a| **a == "create")
            .and(args.iter().skip(1).find(|a| !a.starts_with('-')))
            .map(|f| Some(*f)),
        "format-patch" if !args.contains(&"--stdout") => Some(value(&["-o", "--output-directory"])),
        "bugreport" | "diagnose" => Some(value(&["-o", "--output-directory"])),
        _ => None,
    }
}
