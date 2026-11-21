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

use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;

fn re(pattern: &str) -> Regex {
    crate::regex::build(pattern).unwrap_or_else(|e| unreachable!("a guard's own pattern: {e}"))
}

/// A call or module that can write, read as a substring so a near miss is a write (`.copy()`, `list.remove` - the closed side).
static WRITES: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"write|\.touch\(|mkdir|makedirs|unlink|remove|rmdir|rmtree|rename|shutil|subprocess|system\(|popen|spawn|exec|\beval\(|__import__|importlib|runpy|\.dump\(|\bsave\w*\(|\bto_[a-z]+\(|tofile|chmod|chown|symlink|link_to|hardlink|\blink\(|truncate|os\.open|fdopen|sqlite3|dbm|shelve|tarfile|zipfile|tempfile|copy|move|sys\.path|setattr|getattr\(|vars\(|globals\(|__builtins__|__dict__|\bcompile\(|urlretrieve|FileIO|GzipFile|fileinput|utime|mknod|mkfifo|ctypes",
    )
});
/// `re.compile(` builds a pattern, never code, so it is read past before the writers are sought; the builtin `compile` and any
/// other name's `.compile(` stay a write (451 T42: window#307's heredoc, a read, judged a write on its `re.compile`).
static RE_COMPILE: LazyLock<Regex> = LazyLock::new(|| re(r"(?<![\w.])re\.compile\("));
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
static SUBPROCESS_CALL: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?<![\w.])subprocess\.(?:run|check_output|check_call|call)\("));
static SUBPROCESS_CONST: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?<![\w.])subprocess\.(?:PIPE|DEVNULL|STDOUT)\b"));
/// One argv element that is a string literal holding no quote of its own delimiter (`'a' if c else 'b'` is no literal).
static ARGV_LITERAL: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?s)^([rRbBuUfF]{0,2})(?:"([^"]*)"|'([^']*)')$"#));
/// `replace(` writes only as `os.replace` or a `Path`'s (`str.replace`, the common read, cannot reach either without these names).
static REPLACE: LazyLock<Regex> = LazyLock::new(|| re(r"replace\("));
static PATHS: LazyLock<Regex> = LazyLock::new(|| re(r"\bos\b|Path|pathlib"));
static OPEN: LazyLock<Regex> = LazyLock::new(|| re(r"\bopen\("));
static KWARG_OK: LazyLock<Regex> =
    LazyLock::new(|| re(r"^(?:encoding|errors|newline|buffering)\s*=[^=]"));
static MODE_KW: LazyLock<Regex> = LazyLock::new(|| re(r"^mode\s*="));
static KWARG: LazyLock<Regex> = LazyLock::new(|| re(r"^\w+\s*=[^=]"));
static LITERAL: LazyLock<Regex> = LazyLock::new(|| re(r#"(?s)^(?i:[rbfu]{0,2})(["'])(.*)\1$"#));
static READ_MODE: LazyLock<Regex> = LazyLock::new(|| re(r"^[rbtU]*$"));
static ANY_MODE: LazyLock<Regex> = LazyLock::new(|| re(r"^[rbtUwax+]*$"));
/// An import where a statement can start: a line, after `;`, or after a compound statement's `:` (`try: import l7r`).
static IMPORT: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)(?:^|[;:])\s*import\s+([^;\n#]+)"));
static FROM: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)(?:^|[;:])\s*from\s+(\S+)\s+import\b"));
/// What follows an unescaped `$` that the shell expands inside double quotes: a name, a brace, a digit or a special parameter.
static EXPANDS: LazyLock<Regex> = LazyLock::new(|| re(r"^[A-Za-z_{0-9@*#?!$-]"));

fn found(p: &Regex, text: &str) -> bool {
    p.is_match(text).unwrap_or(false)
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
/// only where its value cannot open as an option (`f"HEAD:{p}"` is one; `f"{flag}"` and `f"--{o}"` are not).
fn argv_literal(arg: &str) -> Option<String> {
    let c = ARGV_LITERAL.captures(arg).ok().flatten()?;
    let f = c.get(1).is_some_and(|p| p.as_str().contains(['f', 'F']));
    let text = c.get(2).or_else(|| c.get(3)).map_or("", |m| m.as_str());
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
        .ok()
        .flatten()
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

/// Whether the program `body` (quoted with `quote` on the command line, `'h'` an unquoted heredoc's), run in `dir`, only reads.
pub(super) fn reads(body: &str, quote: char, dir: Option<&str>) -> bool {
    if quote != '\'' && (body.contains("$(") || body.contains('`')) {
        return false; // the shell runs a command substitution before Python sees the program
    }
    let (program, at) = expansions(body, quote);
    if outside_literals(&program, &at) {
        return false; // the shell puts text into the program's code before Python sees it
    }
    if found(
        &WRITES,
        &subprocess_masked(&RE_COMPILE.replace_all(&program, "re.pattern(")),
    ) || (found(&REPLACE, &program) && found(&PATHS, &program))
    {
        return false;
    }
    if !opens_read(&program) {
        return false;
    }
    let Some(names) = imports(&program) else {
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

#[cfg(test)]
mod tests;
