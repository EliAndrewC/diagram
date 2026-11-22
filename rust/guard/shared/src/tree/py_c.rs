//! Whether a `python3 -c` program only READS (451 T31). Feature 204's D5 kept every `python3 -c` a write where the shell stands,
//! its cost "zero" because a write in the mirror is moved to the clone - but where the clone cannot be resolved the move is a
//! refusal, and T15's corpus replay found `python3 -c "data = open('$SP/x.html','rb').read() ..."` refused so. The judgment fails
//! CLOSED on what it can see: a program is a read only when no known writer appears in it, no command substitution or shell
//! expansion outside a Python literal can put code into it, every `open` is in a read mode, and no import the directory it runs
//! in could answer (the tree's own code, which can write anything); anything else stays a write, as D5 had it. The judgment is a
//! DENYLIST of known writers - the calls, modules and argument shapes below - not a proof: a writer it does not name passes as a
//! read, so each one found is added with its case.
//!
//! 451 T42: the same reader judges a program run from stdin - a heredoc's body (an unquoted delimiter's expanded by the shell
//! first, a quoted one's literal) or a readable file's text - so `reads` takes the quote `'h'` for an unquoted heredoc's body.
//!
//! 451 T44: `subprocess` stays a writer except where the reader accounts for every mention of it - a plain `import subprocess`,
//! a `subprocess.PIPE`/`DEVNULL`/`STDOUT`, and a `run`/`check_output`/`check_call`/`call` whose argv is ONE literal list naming
//! a read-only command (`GIT_READS`, `TOOLS`), with only the keywords `SUBPROCESS_KWARGS` beside it (window#307's
//! `subprocess.run(["git","-C",root,"ls-files"])`, a read refused or rewritten before). A shell string, `shell=True`, a
//! non-literal argv or element (git's `-C` directory alone may be any expression), a writing git subcommand, `make`, an unknown
//! command or an alias of the module stays a write.
//!
//! 451 T63: an f-string argv element that is a long option with its name literal and a value that calls nothing is that option
//! with the value `_` (`FIXED_OPTION`): T58's read of the event logs, `f'--since={prev["t0"]}'` in a `git log` argv, was the one
//! read-only program among the 250 make-only refusals the guard log replayed (measured 2026-11-21).
//!
//! 451 T89: a program that writes only through `sys.argv[N]` writes the command's N-th word after the program (`argv_places`),
//! where D5 had it write where the shell stands: `cd <mirror>/research/questions; python3 -c "...open(sys.argv[2],'w')..." a
//! /tmp/q/a.txt` was refused through main-tree, and so were four corpus commands writing scratch so (bx#29969, bx#54240,
//! bx#58694, ux#2209), measured 2026-11-21. `argv_word` is the binding alone, for the program reader (`tree::program`, T125).
//! A name bound once to `sys.argv[N]` and only opened is that `sys.argv[N]` (`argv_inlined`, bx#58999, the review's ruling).

use std::borrow::Cow;
use std::path::Path;

use fancy_regex::Regex;

use super::{path_write, program_of, quoted, substituted, Env, Known, Program, Write};
use crate::regex::Lazy;

fn re(pattern: &str) -> Regex {
    crate::regex::build(pattern).unwrap_or_else(|e| unreachable!("a guard's own pattern: {e}"))
}

// Each pattern built only for a text that could match it (`Lazy`, 451 T97): its gate the literals one of which every match holds,
// none (`|_| true`) where a match needs none.
/// A call or module that can write, read as a substring so a near miss is a write (`.copy()`, `list.remove` - the closed side).
static WRITES: Lazy = Lazy::new(
    |_| true,
    || {
        re(
            r"write|\.touch\(|mkdir|makedirs|unlink|remove|rmdir|rmtree|rename|shutil|subprocess|system\(|popen|spawn|exec|\beval\(|__import__|importlib|runpy|\.dump\(|\bsave\w*\(|\bto_[a-z]+\(|tofile|chmod|chown|symlink|link_to|hardlink|\blink\(|truncate|os\.open|fdopen|sqlite3|dbm|shelve|tarfile|zipfile|tempfile|copy|move|sys\.path|setattr|getattr\(|vars\(|globals\(|__builtins__|__dict__|\bcompile\(|urlretrieve|FileIO|GzipFile|fileinput|utime|mknod|mkfifo|ctypes",
        )
    },
);
/// `re.compile(` builds a pattern, never code, so it is read past before the writers are sought; the builtin `compile` and any
/// other name's `.compile(` stay a write (451 T42: window#307's heredoc, a read, judged a write on its `re.compile`).
static RE_COMPILE: Lazy = Lazy::new(
    |t| t.contains("re.compile("),
    || re(r"(?<![\w.])re\.compile\("),
);
/// 451 T44: the git subcommands a subprocess argv may name and stay a read: those the corpora run so (`ls-files` window#307,
/// `show` window#112, `rev-parse` parse#173 and refusals#27, `log` parse#229) and the plumbing T44's line names (`cat-file`,
/// `ls-tree`). `status` and `diff` are left out: each rewrote `.git/index` after a tracked file was touched, where these six
/// left it unchanged (measured 2026-11-20, a scratch repository, the index's hash before and after each); window#328's
/// `git diff` is a `cat >` heredoc's text, never run, so no corpus row runs either from Python.
const GIT_READS: [&str; 6] = [
    "ls-files",
    "log",
    "show",
    "rev-parse",
    "cat-file",
    "ls-tree",
];
/// The other commands an argv may name: none writes a file (`grep` refusals#42; the rest as T44's brief lists them). `rg` is
/// left out: its `--pre` and `--hostname-bin` run a program (spec-fidelity, 2026-11-20), and no corpus row runs it from Python.
const TOOLS: [&str; 5] = ["grep", "ls", "cat", "head", "wc"];
/// The keywords that change no command or environment; `shell`, `executable`, `env`, `preexec_fn` and any other are a write.
const SUBPROCESS_KWARGS: [&str; 12] = [
    "capture_output",
    "text",
    "check",
    "cwd",
    "encoding",
    "errors",
    "timeout",
    "input",
    "universal_newlines",
    "stdout",
    "stderr",
    "stdin",
];
static SUBPROCESS_CALL: Lazy = Lazy::new(
    |t| t.contains("subprocess."),
    || re(r"(?<![\w.])subprocess\.(?:run|check_output|check_call|call)\("),
);
static SUBPROCESS_CONST: Lazy = Lazy::new(
    |t| t.contains("subprocess."),
    || re(r"(?<![\w.])subprocess\.(?:PIPE|DEVNULL|STDOUT)\b"),
);
/// One argv element that is a string literal holding no quote of its own delimiter (`'a' if c else 'b'` is no literal).
static ARGV_LITERAL: Lazy = Lazy::new(
    |t| t.contains(['"', '\'']),
    || re(r#"(?s)^([rRbBuUfF]{0,2})(?:"([^"]*)"|'([^']*)')$"#),
);
/// 451 T63: an f-string's text that is a long option with its name literal - `--`, a letter, letters, digits and `-`, then `=` -
/// and a value holding no call's bracket, `\`, `$` or line break, so no call can stand in its fields (`f'--since={prev["t0"]}'`,
/// T58's read of the event logs, refused as a guard write on 2026-11-21T05:51:53Z). `writes_flag` judges an option by its name
/// alone, and `--name=_` can never be `-C`, a subcommand or a command, so the element is judged as a literal `--name=v` was; a
/// writing option (`f'--output={p}'`) stays a write by its name, and a short option, a name a field can reach and every other
/// f-string opening with `-` or `{` stay unknowable.
static FIXED_OPTION: Lazy = Lazy::new(
    |t| t.starts_with("--"),
    || re(r"^(--[A-Za-z][A-Za-z0-9-]*=)[^()\\$\n]*$"),
);
static PATHS: Lazy = Lazy::new(
    |t| t.contains("os") || t.contains("Path") || t.contains("pathlib"),
    || re(r"\bos\b|Path|pathlib"),
);
static OPEN: Lazy = Lazy::new(|t| t.contains("open("), || re(r"\bopen\("));
static KWARG_OK: Lazy = Lazy::new(
    |t| t.contains('='),
    || re(r"^(?:encoding|errors|newline|buffering)\s*=[^=]"),
);
static MODE_KW: Lazy = Lazy::new(|t| t.starts_with("mode"), || re(r"^mode\s*="));
static KWARG: Lazy = Lazy::new(|t| t.contains('='), || re(r"^\w+\s*=[^=]"));
static LITERAL: Lazy = Lazy::new(
    |t| t.contains(['"', '\'']),
    || re(r#"(?s)^(?i:[rbfu]{0,2})(["'])(.*)\1$"#),
);
static READ_MODE: Lazy = Lazy::new(|_| true, || re(r"^[rbtU]*$"));
static ANY_MODE: Lazy = Lazy::new(|_| true, || re(r"^[rbtUwax+]*$"));
/// An import where a statement can start: a line, after `;`, or after a compound statement's `:` (`try: import l7r`).
static IMPORT: Lazy = Lazy::new(
    |t| t.contains("import"),
    || re(r"(?m)(?:^|[;:])\s*import\s+([^;\n#]+)"),
);
static FROM: Lazy = Lazy::new(
    |t| t.contains("from"),
    || re(r"(?m)(?:^|[;:])\s*from\s+(\S+)\s+import\b"),
);
/// What follows an unescaped `$` that the shell expands inside double quotes: a name, a brace, a digit or a special parameter.
static EXPANDS: Lazy = Lazy::new(|_| true, || re(r"^[A-Za-z_{0-9@*#?!$-]"));

fn found(p: &Lazy, text: &str) -> bool {
    p.is_match(text)
}

/// The program Python receives - a double-quoted body with the shell's `\"`, `\\`, `\$` and `` \` `` undone, an unquoted
/// heredoc's (`'h'`) with all but `\"` undone (there `\"` is two characters, 451 T42) - and the byte offsets in it where the
/// shell expands a `$` first (none in a single-quoted body, a quoted heredoc's or a file's, `'\''`).
fn expansions(body: &str, quote: char) -> (String, Vec<usize>) {
    if quote == '\'' {
        return (body.to_owned(), Vec::new());
    }
    let escapes = if quote == 'h' { "\\$`" } else { "\"\\$`" };
    let (mut out, mut at) = (String::new(), Vec::new());
    let mut chars = body.char_indices().peekable();
    while let Some((i, c)) = chars.next() {
        match (c, chars.peek()) {
            ('\\', Some(&(_, n))) if escapes.contains(n) => {
                out.push(n);
                chars.next();
            }
            ('$', _) if found(&EXPANDS, &body[i + 1..]) => {
                at.push(out.len());
                out.push(c);
            }
            _ => out.push(c),
        }
    }
    (out, at)
}

/// Python's string delimiters, the triple ones first.
const QUOTES: [&str; 4] = ["\"\"\"", "'''", "\"", "'"];

/// Whether any of the offsets `at` stands outside a Python string literal of `program` (in code or a comment), where the
/// shell's expansion becomes code.
fn outside_literals(program: &str, at: &[usize]) -> bool {
    let (mut inside, mut quote, mut i) = (Vec::new(), None::<&str>, 0);
    let bytes = program.as_bytes();
    while i < bytes.len() {
        let rest = &program[i..];
        if let Some(q) = quote {
            if rest.starts_with(q) {
                (i, quote) = (i + q.len(), None);
                continue;
            }
            inside.push(i);
            if bytes[i] == b'\\' && i + 1 < bytes.len() {
                i += 1;
                inside.push(i);
            }
        } else if let Some(q) = QUOTES.into_iter().find(|q| rest.starts_with(q)) {
            (i, quote) = (i + q.len(), Some(q));
            continue;
        } else if bytes[i] == b'#' {
            i += rest.find('\n').unwrap_or(rest.len()); // a comment to its line's end: its quotes open no literal (451 T31)
            continue;
        }
        i += program[i..].chars().next().map_or(1, char::len_utf8); // a whole character: the text is UTF-8
    }
    at.iter().any(|a| !inside.contains(a))
}

/// The arguments of the call whose `(` ends at `from`, split at its top-level commas (Python's quotes and brackets respected).
fn call_args(text: &str, from: usize) -> Vec<String> {
    split_args(text, from).0
}

/// `call_args`, and the byte offset of the bracket that closes the call (None where the text ends first).
fn split_args(text: &str, from: usize) -> (Vec<String>, Option<usize>) {
    let (mut args, mut cur, mut depth, mut quote, mut esc, mut end) =
        (Vec::new(), String::new(), 1usize, None::<char>, false, None);
    for (i, c) in text[from..].char_indices() {
        if let Some(q) = quote {
            if esc {
                esc = false;
            } else if c == '\\' {
                esc = true;
            } else if c == q {
                quote = None;
            }
        } else if c == '\'' || c == '"' {
            quote = Some(c);
        } else if "([{".contains(c) {
            depth += 1;
        } else if ")]}".contains(c) {
            depth -= 1;
            if depth == 0 {
                end = Some(from + i);
                break;
            }
        } else if c == ',' && depth == 1 {
            args.push(std::mem::take(&mut cur).trim().to_owned());
            continue;
        }
        cur.push(c);
    }
    args.push(cur.trim().to_owned());
    args.retain(|a| !a.is_empty());
    (args, end)
}

/// The elements of an argument that is one list display and nothing past it (`[...] + extra` is none).
fn list_items(arg: &str) -> Option<Vec<String>> {
    if !arg.starts_with('[') {
        return None;
    }
    let (items, end) = split_args(arg, 1);
    (end == Some(arg.len() - 1)).then_some(items)
}

/// One argv element's text where it is a literal whose value the reader knows: no `$` the shell may expand, and an f-string
/// only where its value cannot open as an option (`f"HEAD:{p}"` is one; `f"{flag}"` and `f"--{o}"` are not) - or, where it is a
/// long option whose name is literal and whose value calls nothing (`FIXED_OPTION`), that option with the value `_` (451 T63).
fn argv_literal(arg: &str) -> Option<String> {
    let c = ARGV_LITERAL.captures(arg)?;
    let f = c.get(1).is_some_and(|p| p.as_str().contains(['f', 'F']));
    let text = c.get(2).or_else(|| c.get(3)).map_or("", |m| m.as_str());
    let option = f.then(|| FIXED_OPTION.captures(text)).flatten();
    if let Some(o) = option {
        return Some(format!("{}_", o.get(1).map_or("", |m| m.as_str())));
    }
    let opaque = text.contains('$') || (f && (text.starts_with('{') || text.starts_with('-')));
    (!opaque).then(|| text.to_owned())
}

/// Whether an option writes or runs a program, or any abbreviation of one: git's `--output`, `--ext-diff`, `--textconv`,
/// `--filters`; this container's `grep` (ugrep) `--filter`, `--pager`, `--view`, `--save-config`, `--query` and `-Q` in any
/// short cluster, and `--config`/`---FILE`, which load options from a file. Found in each git subcommand's full option list
/// (`--git-completion-helper`; `log` and `show` take `diff`'s) and each tool's `--help`, searched for an option that names an
/// output file, a command, a program, a pager, a filter or a config (2026-11-20); `ls`, `cat`, `head` and `wc` name none.
fn writes_flag(cmd: &str, arg: &str) -> bool {
    let deny: &[&str] = match cmd {
        "git" => &["--output", "--ext-diff", "--textconv", "--filters"],
        "grep" => &[
            "--filter",
            "--pager",
            "--view",
            "--save-config",
            "--query",
            "--config",
        ],
        _ => &[],
    };
    let name = arg.split('=').next().unwrap_or(arg);
    let cluster_q =
        cmd == "grep" && !arg.starts_with("--") && arg.starts_with('-') && arg.contains('Q');
    cluster_q
        || (cmd == "grep" && arg.starts_with("---"))
        || (name.len() > 2 && name.starts_with("--") && deny.iter().any(|f| f.starts_with(name)))
}

/// Whether an argv's elements name a read-only command: git's `-C <any expression>` pairs and a `GIT_READS` subcommand, or a
/// `TOOLS` command; every other element a literal no `writes_flag` names.
fn argv_reads(items: &[String]) -> bool {
    let lit: Vec<Option<String>> = items.iter().map(|a| argv_literal(a)).collect();
    let Some(Some(cmd)) = lit.first() else {
        return false;
    };
    let mut i = 1;
    if cmd == "git" {
        while lit.get(i).and_then(Option::as_deref) == Some("-C") {
            match items.get(i + 1) {
                Some(d) if !d.starts_with('*') => i += 2,
                _ => return false,
            }
        }
        match lit.get(i) {
            Some(Some(sub)) if GIT_READS.contains(&sub.as_str()) => i += 1,
            _ => return false,
        }
    } else if !TOOLS.contains(&cmd.as_str()) {
        return false;
    }
    lit[i..]
        .iter()
        .all(|a| a.as_deref().is_some_and(|a| !writes_flag(cmd, a)))
}

/// Whether the subprocess call whose `(` ends at `from` runs a read-only argv with only `SUBPROCESS_KWARGS` beside it.
fn call_reads(text: &str, from: usize) -> bool {
    let parts = call_args(text, from);
    let Some((argv, rest)) = parts.split_first() else {
        return false;
    };
    list_items(argv).is_some_and(|items| argv_reads(&items))
        && rest.iter().all(|a| {
            found(&KWARG, a)
                && SUBPROCESS_KWARGS.contains(&a.split('=').next().unwrap_or("").trim())
        })
}

/// The program with each `subprocess` the reader accounts for renamed, so the writers are sought past it: a plain import of
/// the module, a constant, a call `call_reads` judges a read. Any other mention stays, and is a write.
fn subprocess_masked(program: &str) -> String {
    let mut at = Vec::new();
    for c in IMPORT.captures_iter(program).map_while(Result::ok) {
        let Some(g) = c.get(1) else { continue };
        let mut off = g.start();
        for part in g.as_str().split(',') {
            if part.trim() == "subprocess" {
                at.push(off + part.len() - part.trim_start().len());
            }
            off += part.len() + 1;
        }
    }
    at.extend(
        SUBPROCESS_CONST
            .find_iter(program)
            .map_while(Result::ok)
            .map(|m| m.start()),
    );
    at.extend(
        SUBPROCESS_CALL
            .find_iter(program)
            .map_while(Result::ok)
            .filter(|m| call_reads(program, m.end()))
            .map(|m| m.start()),
    );
    at.sort_unstable();
    let (mut out, mut last) = (String::new(), 0);
    for a in at {
        out.push_str(&program[last..a]);
        out.push_str("sp_ro");
        last = a + "subprocess".len();
    }
    out.push_str(&program[last..]);
    out
}

/// A literal's content, or None where the argument is not one string literal.
fn literal(arg: &str) -> Option<String> {
    LITERAL
        .captures(arg)
        .and_then(|c| c.get(2).map(|m| m.as_str().to_owned()))
}

/// Whether one argument of an `open` call (the `k`th; `method` for `x.open(`) leaves it a read.
fn reads_arg(k: usize, arg: &str, method: bool) -> bool {
    if found(&KWARG_OK, arg) {
        return true;
    }
    if arg.starts_with('*') {
        return false; // `open(*a)`, `open(**kw)`: the mode cannot be read
    }
    let mode_kw = found(&MODE_KW, arg);
    let bare = if mode_kw {
        MODE_KW.replace(arg, "").trim().to_owned()
    } else {
        arg.to_owned()
    };
    if !mode_kw && found(&KWARG, arg) {
        return false;
    }
    let lit = literal(&bare);
    if k == 0 && !method && !mode_kw {
        return true; // the path
    }
    match lit {
        Some(s) if found(&READ_MODE, &s) => true,
        // a method's first argument is a path (`codecs.open('x')`) or a mode (`Path.open('w')`)
        Some(s) => k == 0 && method && !mode_kw && !found(&ANY_MODE, &s),
        None => false,
    }
}

/// Whether every `open(...)` in the program opens for reading.
fn opens_read(program: &str) -> bool {
    OPEN.find_iter(program).map_while(Result::ok).all(|m| {
        let method = program[..m.start()].ends_with('.');
        call_args(program, m.end())
            .iter()
            .enumerate()
            .all(|(k, a)| reads_arg(k, a, method))
    })
}

/// The top-level modules the program imports, or None where one is relative (`from . import x`).
fn imports(program: &str) -> Option<Vec<String>> {
    let mut names = Vec::new();
    for c in IMPORT.captures_iter(program).map_while(Result::ok) {
        for part in c.get(1).map_or("", |m| m.as_str()).split(',') {
            names.extend(part.split_whitespace().next().map(str::to_owned));
        }
    }
    for c in FROM.captures_iter(program).map_while(Result::ok) {
        names.push(c.get(1).map_or("", |m| m.as_str()).to_owned());
    }
    if names.iter().any(|n| n.starts_with('.')) {
        return None;
    }
    Some(
        names
            .into_iter()
            .filter_map(|n| n.split('.').next().map(str::to_owned))
            .filter(|n| !n.is_empty())
            .collect(),
    )
}

/// The program Python receives from `body` (quoted with `quote` on the command line, `'h'` an unquoted heredoc's), or None where
/// the shell puts code into it first.
fn received(body: &str, quote: char) -> Option<String> {
    if quote != '\'' && (body.contains("$(") || body.contains('`')) {
        return None; // the shell runs a command substitution before Python sees the program
    }
    let (program, at) = expansions(body, quote);
    // the shell puts text into the program's code before Python sees it
    (!outside_literals(&program, &at)).then_some(program)
}

/// Whether the program `body` (quoted with `quote` on the command line, `'h'` an unquoted heredoc's), run in `dir`, only reads.
pub(super) fn reads(body: &str, quote: char, dir: Option<&str>) -> bool {
    received(body, quote).is_some_and(|program| only_reads(&program, dir))
}

/// Whether the program Python receives, run in `dir`, only reads.
fn only_reads(program: &str, dir: Option<&str>) -> bool {
    // `replace(` writes only as `os.replace` or a `Path`'s (`str.replace`, the common read, cannot reach either without these
    // names); a literal, read without a pattern (451 T97)
    if found(
        &WRITES,
        &subprocess_masked(&RE_COMPILE.replace_all(program, "re.pattern(")),
    ) || (program.contains("replace(") && found(&PATHS, program))
    {
        return false;
    }
    if !opens_read(program) {
        return false;
    }
    let Some(names) = imports(program) else {
        return false;
    };
    match dir {
        None => names.is_empty(),
        Some(d) => !names.iter().any(|n| {
            let at = Path::new(d);
            at.join(n).exists() || at.join(format!("{n}.py")).exists()
        }),
    }
}

// 451 T89's patterns, each built only for a text that could match it.
/// An `open` whose path is `sys.argv[N]`, N the capture, its `(` the match's fifth character.
static ARGV_OPEN: Lazy = Lazy::new(
    |t| t.contains("argv"),
    || re(r"(?<![\w.])open\(\s*sys\.argv\[(\d+)\]\s*(?=[,)])"),
);
/// A `.write(` or `.writelines(` chained on the call just closed, the method's name the capture.
static CHAINED_WRITE: Lazy = Lazy::new(
    |t| t.contains("write"),
    || re(r"^\s*(\.\s*write(?:lines)?)\s*\("),
);
/// A `json.dump(` call, which writes its second argument.
static JSON_DUMP: Lazy = Lazy::new(
    |t| t.contains("json.dump("),
    || re(r"(?<![\w.])json\.dump\("),
);
/// Each mention of `argv`, every one of which must be a `sys.argv[N]` read for the program to be bound.
static ARGV_NAME: Lazy = Lazy::new(|t| t.contains("argv"), || re(r"\bargv\b"));
/// `[N]`, then anything but an assignment to it (`=`, `+=` and the rest; `==` compares).
static INDEX_READ: Lazy = Lazy::new(
    |t| t.starts_with('['),
    || re(r"^\[\d+\](?!\s*(?:[-+*/%&|^@]|//|\*\*|<<|>>)?=(?!=))"),
);
/// `NAME = sys.argv[N]`, a statement of its own (451 T89's review): the name and N the captures.
static ARGV_BOUND: Lazy = Lazy::new(
    |t| t.contains("argv"),
    || re(r"(?m)(?:^|;)[ \t]*([A-Za-z_]\w*)[ \t]*=[ \t]*sys\.argv\[(\d+)\][ \t]*(?=$|;)"),
);
/// The text before a bound name that an `open` takes as its path: `open(`, not another module's or object's.
static OPENS_NAME: Lazy = Lazy::new(|t| t.contains("open("), || re(r"(?<![\w.])open\(\s*$"));
/// The text after it: the path's end, the mode or the call's close next.
static NAME_ENDS: Lazy = Lazy::new(|_| true, || re(r"^\s*[,)]"));
/// `import sys`, alone or in a list (`import re,sys,html`).
static IMPORTS_SYS: Lazy = Lazy::new(
    |t| t.contains("import"),
    || re(r"\bimport\s+(?:[\w.]+(?:\s+as\s+\w+)?\s*,\s*)*sys\b"),
);
/// `sys` bound to something other than the module: `import os as sys`, `sys = ...`, a `def`, `class`, loop or lambda of it.
static SYS_REBOUND: Lazy = Lazy::new(
    |t| t.contains("sys"),
    || {
        re(
            r"\bas\s+sys\b|(?<![\w.])sys\s*(?:[-+*/%&|^@:]|//|\*\*|<<|>>)?=(?!=)|\b(?:def|class|for|lambda|global|nonlocal)\s+sys\b",
        )
    },
);
/// A word of a command that is a redirect, its target the capture (empty where the target is the next word); a process
/// substitution (`<(...)`) is no redirect but a word, a path the shell makes.
static REDIRECT_WORD: Lazy = Lazy::new(
    |t| t.contains(['<', '>']),
    || re(r"^(?:\d+|&)?(?:<<<|<<-?|<>|<&|>&|>>|>\||<|>)(?!\()(.*)$"),
);

/// Whether every `argv` the program names is `sys.argv[N]` read - never sliced, aliased, assigned, deleted from or imported by
/// name - with `sys` the module it imports, so `sys.argv[N]` is the command's word.
fn argv_indexed(program: &str) -> bool {
    found(&IMPORTS_SYS, program)
        && !found(&SYS_REBOUND, program)
        && ARGV_NAME.find_iter(program).map_while(Result::ok).all(|m| {
            program[..m.start()]
                .strip_suffix("sys.")
                .is_some_and(|owner| {
                    !owner.ends_with(|c: char| c.is_alphanumeric() || c == '_' || c == '.')
                        && !owner.trim_end().ends_with("del")
                })
                && found(&INDEX_READ, &program[m.end()..])
        })
}

/// 451 T89, its review (bx#58999's `p=sys.argv[1]; t=open(p).read(); ...; open(p,'w').write(t)`): the program with a name bound
/// once to `sys.argv[N]` - `p = sys.argv[1]`, a statement of its own - read as `sys.argv[N]` where an `open` takes it as its path,
/// where that is every other mention of the name, so nothing can bind it again (no assignment, loop, `as`, parameter or `del`
/// of it is an `open`'s path); unchanged where a name is mentioned any other way, even in a literal. A stdin program's reader is
/// to call it too (T137).
pub(super) fn argv_inlined(program: &str) -> Cow<'_, str> {
    let mut edits = Vec::new();
    let bound = ARGV_BOUND.captures_iter(program).map_while(Result::ok);
    for (name, n) in bound.filter_map(|c| Some((c.get(1)?, c.get(2)?))) {
        let len = name.as_str().len();
        let ident = |c: char| c.is_alphanumeric() || c == '_';
        let mentions: Vec<usize> = program
            .match_indices(name.as_str())
            .map(|(at, _)| at)
            .filter(|&at| at != name.start())
            .filter(|&at| {
                !program[..at].ends_with(|c: char| ident(c) || c == '.')
                    && !program[at + len..].starts_with(ident)
            })
            .collect();
        let opened = |at: &usize| {
            found(&OPENS_NAME, &program[..*at]) && found(&NAME_ENDS, &program[*at + len..])
        };
        if !mentions.is_empty() && mentions.iter().all(opened) {
            edits.extend(
                mentions
                    .into_iter()
                    .map(|at| (at, at + len, format!("sys.argv[{}]", n.as_str()))),
            );
        }
    }
    if edits.is_empty() {
        return Cow::Borrowed(program);
    }
    edits.sort_unstable_by_key(|e| e.0);
    let mut inlined = program.to_owned();
    for (start, end, with) in edits.into_iter().rev() {
        inlined.replace_range(start..end, &with);
    }
    Cow::Owned(inlined)
}

/// The program with each write through `sys.argv[N]` read past - an `open` of it in a mode that writes, its chained `.write(`
/// or `.writelines(`, and a `json.dump` into it - and each such N; None where `sys.argv` is read any other way. A name bound
/// once to `sys.argv[N]` and only opened is that `sys.argv[N]` (`argv_inlined`).
fn argv_masked(program: &str) -> Option<(String, Vec<usize>)> {
    let inlined = argv_inlined(program);
    let program = &*inlined;
    if !argv_indexed(program) {
        return None;
    }
    let (mut edits, mut ns) = (Vec::new(), Vec::new());
    for c in ARGV_OPEN.captures_iter(program).map_while(Result::ok) {
        let (whole, n) = (c.get(0)?, c.get(1)?);
        let (args, end) = split_args(program, whole.start() + 5);
        if args.iter().enumerate().all(|(k, a)| reads_arg(k, a, false)) {
            continue; // a read, which `opens_read` judges
        }
        // the open's name and path go, its mode and keywords stay for the writers to be sought in (`opener=`)
        edits.push((whole.start(), whole.end(), "_argv_("));
        let chained = end.and_then(|e| CHAINED_WRITE.captures(&program[e + 1..]));
        if let (Some(e), Some(m)) = (end, chained.as_ref().and_then(|c| c.get(1))) {
            edits.push((e + 1 + m.start(), e + 1 + m.end(), ""));
        }
        ns.push(n.as_str().parse::<usize>().ok()?);
    }
    let mut masked = program.to_owned();
    edits.sort_unstable_by_key(|e| e.0); // an open inside another's arguments is masked before the outer one's chained write
    for (start, end, with) in edits.into_iter().rev() {
        masked.replace_range(start..end, with);
    }
    let dumps: Vec<usize> = JSON_DUMP
        .find_iter(&masked)
        .map_while(Result::ok)
        .filter(|m| {
            call_args(&masked, m.end())
                .get(1)
                .is_some_and(|f| f.starts_with("_argv_("))
        })
        .map(|m| m.start())
        .collect();
    for start in dumps.into_iter().rev() {
        masked.replace_range(start..start + "json.dump(".len(), "_argv_(");
    }
    ns.sort_unstable();
    ns.dedup();
    Some((masked, ns))
}

/// The N of each `sys.argv[N]` the program writes, where it writes nowhere else (`only_reads` holds with those writes read
/// past, run in `dir`); None where it writes otherwise, writes none so, or writes `sys.argv[0]`, the `-c` itself.
fn argv_writes(body: &str, quote: char, dir: Option<&str>) -> Option<Vec<usize>> {
    let (masked, ns) = argv_masked(&received(body, quote)?)?;
    (ns.first().is_some_and(|n| *n > 0) && only_reads(&masked, dir)).then_some(ns)
}

/// Whether a word of a command after a program is one word of the program's argv as bash makes it, `$__unread__` (`bind`'s
/// mark for a loop's value cut at a glob, or a name read from input) counting one where it is the word asked for, its first piece
/// lying where its start does (one bash may split ends the count past it, `may_split`). A plain quoted word reaches the walk without its quotes, so a value holding a blank or empty may be one word
/// or none and more - not one; nor is a glob, a brace, `$@`, a substitution of either kind or a name the walk does not know. A held word (a quoted
/// body with a blank or shell character) is one where it is quoted whole.
fn one_word(word: &str, env: &Env, home: &str) -> bool {
    let quote = |c: Option<char>| {
        c.is_some_and(|c| c == quoted::stand_in('"') || c == quoted::stand_in('\''))
    };
    if matches!(word, "\"\"" | "''") {
        return true; // an empty quote, one empty word
    }
    if matches!(quoted::unheld(word), Cow::Owned(_)) {
        return quote(word.chars().next()) && quote(word.chars().last()) && !word.contains("$@");
    }
    let value = substituted(word, env, home);
    let known = value.replace(super::bind::UNREAD, "");
    !value.is_empty() && !known.contains(|c: char| c.is_whitespace() || "$`*?[{<>()".contains(c))
}

/// 451 T89, the binding: the word of the command a program's `sys.argv[n]` holds, `after` the command's words past the program
/// (a `-c` program's word, or stdin's `-`) as the walk holds them, a name it binds in the text (`bind`) or in `env`. A redirect
/// is no word of argv, and a name unset is dropped from the text by `bind`, as bash drops its unquoted expansion. None for 0 -
/// the `-c` or `-` itself - for an index past the words, and where a word up to it may be other than one word (`one_word`).
pub(super) fn argv_word<'a>(n: usize, after: &[&'a str], env: &Env, home: &str) -> Option<&'a str> {
    let (mut words, mut k) = (after.iter(), 0);
    while let Some(&w) = words.next() {
        if let Some(c) = REDIRECT_WORD.captures(w) {
            if c.get(1).is_some_and(|t| t.as_str().is_empty()) {
                words.next(); // its target
            }
            continue;
        }
        if !one_word(w, env, home) {
            return None;
        }
        k += 1;
        if k == n {
            return Some(w);
        }
        if may_split(w) {
            return None; // every index past it shifts by what bash makes of it
        }
    }
    None
}

/// 451 T89, the session's ruling (2026-11-21, option A): whether bash may split a word into more than one - a loop's value cut
/// at a glob or a value read from input (`$__unread__`), or a loop's value with a blank or shell character, which `bind` writes
/// `_` (a typed `_` cannot be told from it, so it counts too). `for f in <glob with a blank-named match>; do python3 -c
/// "...open(sys.argv[2],'w')..." $f /tmp/q/$f.txt; done` writes the name's second piece where the shell stands (measured
/// 2026-11-21, `/tmp/t89/split`), so such a word keeps HEAD's reading past it. A quoted `"$f"` is one word, but the walk holds
/// it without its quotes; the walk carrying them is filed (T140).
fn may_split(word: &str) -> bool {
    word.contains(super::bind::UNREAD) || word.contains('_')
}

/// 451 T89: the writes of the `python3 -c` program at `toks[at + 1]` that writes only through `sys.argv` (`argv_writes`), each
/// word placed as the walk places a word; None - HEAD's reading, D5's write where the shell stands - where it writes otherwise,
/// a word cannot be bound (`argv_word`), or the walk knows nothing of where one lies (`Known::Nothing`, which spec 204's D6
/// puts where the shell was last known, as HEAD's reading does).
pub(super) fn argv_places(
    toks: &[&str],
    at: usize,
    programs: &[Program],
    env: &Env,
    home: &str,
    eff: Option<&str>,
) -> Option<Vec<Write>> {
    let (quote, body) = program_of(toks.get(at + 1), programs)?;
    let after = toks.get(at + 2..).unwrap_or_default();
    argv_writes(body, *quote, eff)?
        .into_iter()
        .map(|n| {
            let w = path_write(argv_word(n, after, env, home)?, env, home, eff);
            (w.0.is_some() || w.2 != Known::Nothing).then_some(w)
        })
        .collect()
}

#[cfg(test)]
mod tests;
