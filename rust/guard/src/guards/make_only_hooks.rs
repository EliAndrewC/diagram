//! `make-only-hooks` (feature 127; features 164, 212, 385, 444; ported from the shell of the same name and the deciding half of `lib/hm_make.py`, feature 449 T028): EVERY OPERATION GOES THROUGH ITS MAKE
//! TARGET, so an expensive run can ask whether the cheap one would do first. A bare pytest, an engine entry point, a bare cargo or a replacement's binary, a foreign makefile, an inline override and a guard
//! file written from the shell are refused; a targeted pytest and an entry point a make target wraps are rewritten into that target. `GUARD_EDIT_OK` with a reason is the escape.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;
use std::time::Duration;

use fancy_regex::Regex;
use serde_json::{json, Value};

use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{escape_or_refuse, used, Escape};
use crate::shared::log;
use crate::shared::make::{pytest_view, POS, PY};
use crate::shared::session::Session;
use crate::shared::shape::{strip_heredocs, strip_quotes};
use crate::shared::state::field;
use crate::shared::tool::ask_within;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "make-only-hooks",
    events: &["PreToolUse"],
    matcher: "Bash",
    decide,
};

/// CONVENTION: the landing lint's limit, as `hm_make.py` gave `ruff`.
const LINT_LIMIT: Duration = Duration::from_secs(60);
const GUARD_FILE: &str = r"[\w./-]*(?:Makefile|[\w-]*-hooks\.sh|settings\.json|tests/rolls\.py)";
const SUITE_NAME: &str = "<a-suite>";

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{pattern}: {e}"))
}

fn hit(pattern: &Regex, text: &str) -> bool {
    pattern.is_match(text).unwrap_or(false)
}

macro_rules! lazy {
    ($name:ident, $pattern:expr) => {
        static $name: LazyLock<Regex> = LazyLock::new(|| re(AsRef::<str>::as_ref(&$pattern)));
    };
}

const STORED_WORD: &str = r"(?:[\w./~+,:@%=-]|\$[A-Za-z_]\w*|\$\{[A-Za-z_]\w*\})+";
lazy!(
    STORED_HEREDOC,
    format!(
        r#"(?s)^\s*(?:(?:[A-Za-z]|[a-z_][a-z0-9_]*)=[\w./~:@%+,=-]*\s*;\s*)*(?:cat(?:[ \t]*>>?[ \t]*{STORED_WORD})?|tee(?:[ \t]+-a)?(?:[ \t]+{STORED_WORD})+)[ \t]*<<(-?)[ \t]*(?:'(\w+)'|"(\w+)"|\\(\w+))[ \t]*(?:>>?[ \t]*{STORED_WORD})?[ \t]*\n(.*?)\n(\t*)(?:\2|\3|\4)\n*$"#
    )
);
lazy!(
    FOREIGN,
    format!(r"{POS}make\s+(?:-\S+\s+)*(?:-f|--file|--makefile)(?:[=\s]|$)")
);
lazy!(
    ENTRY_MODULE,
    format!(r"{POS}{PY}\s+(?:-\S+\s+)*-m\s+l7r\.diagram\.")
);
lazy!(
    ENTRY_SCRIPT,
    format!(r"{POS}{PY}\s+\S*l7r/diagram/(?:pipeline/regen|hamletgen/__main__)\.py")
);
lazy!(
    PYTEST,
    format!(r"{POS}(?:{PY}\s+(?:-\S+\s+)*-m\s+)?pytest\b")
);
lazy!(
    CARGO,
    format!(
        r"{POS}(?:\S*/)?cargo\s+(?:\+\S+\s+)?(?:build|test|run|clippy|check|fmt|llvm-cov|bench|nextest)\b"
    )
);
lazy!(
    BINARY,
    format!(r"{POS}(?:\S*/)?(l7r-guard|hamlet)(?![\w.-])")
);
lazy!(MAKE_ARGS, format!(r"{POS}(?:\$\(MAKE\)|make)\b([^\n;|&]*)"));
lazy!(ASSIGN, r"(?<!\S)([A-Za-z_][A-Za-z0-9_]*)=");
lazy!(OVERRIDE, r"\b(?:REF_WHY|REF_OK|GATE_OK)=");
lazy!(AT_MAKE, format!(r"{POS}make\b"));
lazy!(AT_OVERRIDE, format!(r"{POS}(?:REF_WHY|REF_OK|GATE_OK)="));
lazy!(SUITE, r"[\w./-]*tests/hooks/test-[\w-]*-hooks\.sh");
lazy!(
    LANDING,
    r#"\bmake\s+(?:-\S+\s+)*(?:land-tooling\b[^\n;&|]*?\bFILES|arbiter-fix-done\b[^\n;&|]*?\bLAND)=("[^"]*"|'[^']*'|\S+)"#
);
lazy!(
    DROP_FLAG,
    r"^(-q|-qq|--quiet|-x|--exitfirst|--no-cov|--no-header|-v|-vv|-vvv|--tb=\S+|--color=\S+)$"
);
lazy!(REDIR, r"^(?:\d?>>?&?\S+|\d?<\S+)$");
lazy!(REDIR_OP, r"^\d?>>?$");
lazy!(
    TESTPATH,
    r"^(?:tests(?:/[\w.-]+)*/?|(?:[\w.-]+/)*test_[\w-]+\.py(?:::[\w\[\]:.,-]+)?)$"
);
lazy!(
    PYTEST_RUN,
    r"(?:\S*/)?python3?\s+(?:-\S+\s+)*-m\s+pytest\b|(?<![\w/.-])pytest\b"
);
lazy!(MASK_HEREDOC, r#"(?s)<<-?\s*['"]?(\w+)['"]?\n.*?\n\s*\1\b"#);
lazy!(
    MASK_QUOTE,
    r#"(?s)(?<!-c )(?<!-c\t)(["'])(?:\\.|(?!\1).)*\1"#
);
lazy!(
    ENTRY_RUN,
    r"(?:\S*/)?python3?\s+(?:-\S+\s+)*-m\s+l7r\.diagram\.([\w.]+)"
);
lazy!(
    RECIPE_ARG,
    r"\$\(ARGS\)|\$\(or \$\((\w+)\),([^)]*)\)|\$\(if \$\((\w+)\),([^,]*),\)|(\S+)"
);
lazy!(TARGET_LINE, r"^([a-z][\w-]*):(?!=)");
lazy!(RUN_LINE, r"^\$\(RUN\)\.([\w.]+)\s*(.*)$");
lazy!(
    LABEL_FILE,
    r#"make test-file FILE=(?:"[^"]*"|\S+)(?:\s+K="[^"]*")?"#
);
lazy!(LABEL_MODULE, r"-m\s+(l7r\.diagram\.[\w.]+)");
lazy!(LABEL_TARGET, r"\bmake\s+([a-z][\w-]*(?:\s+[A-Z_]+=\S*)*)");

static SHELL_WRITES: LazyLock<[Regex; 3]> = LazyLock::new(|| {
    [
        re(&format!(r"(?<![-\w])>>?\s*{GUARD_FILE}(?:\s|$)")),
        re(&format!(r"sed\s+-i\b[^;|&]*?{GUARD_FILE}(?:\s|$)")),
        re(&format!(r"tee\s+(?:-a\s+)?{GUARD_FILE}(?:\s|$)")),
    ]
});
static PY_WRITES: LazyLock<[Regex; 2]> = LazyLock::new(|| {
    [
        re(&format!(r#"{GUARD_FILE}["']\s*\)?\s*\)?\s*\.write_text"#)),
        re(&format!(
            r#"open\(\s*["'][^"']*{GUARD_FILE}["']\s*,\s*(?:mode\s*=\s*)?["'][wax]"#
        )),
    ]
});
static BINDS: LazyLock<[Regex; 2]> = LazyLock::new(|| {
    [
        re(&format!(
            r#"(\w+)\s*=\s*(?:pathlib\.)?Path\(\s*["'][^"']*{GUARD_FILE}["']\s*\)"#
        )),
        re(&format!(r#"(\w+)\s*=\s*["'][^"']*{GUARD_FILE}["']"#)),
    ]
});

/// A name bound to a guard path, and that same name writing: proximity tied by the variable.
fn write_via_name(raw: &str) -> bool {
    BINDS
        .iter()
        .flat_map(|b| b.captures_iter(raw).flatten().collect::<Vec<_>>())
        .any(|m| {
            let name = fancy_regex::escape(m.get(1).map_or("", |g| g.as_str())).into_owned();
            hit(&re(&format!(r"\b{name}\.write_text\s*\(")), raw)
                || hit(
                    &re(&format!(
                        r#"\bopen\(\s*{name}\s*,\s*(?:mode\s*=\s*)?["'][wax]"#
                    )),
                    raw,
                )
        })
}

/// The variable one make invocation assigns twice, else "".
fn doubled_var(clean: &str) -> String {
    for m in MAKE_ARGS.captures_iter(clean).flatten() {
        let mut seen = Vec::new();
        for assign in ASSIGN
            .captures_iter(m.get(1).map_or("", |g| g.as_str()))
            .flatten()
        {
            let name = assign.get(1).map_or("", |g| g.as_str());
            if seen.contains(&name) {
                return name.to_owned();
            }
            seen.push(name);
        }
    }
    String::new()
}

fn replace_suites(text: &str) -> String {
    let (mut out, mut from) = (String::new(), 0);
    for m in SUITE.find_iter(text).flatten() {
        out.push_str(&text[from..m.start()]);
        out.push_str(SUITE_NAME);
        from = m.end();
    }
    out + &text[from..]
}

/// `cmd` with its body gone when the whole call is one storing `cat` or `tee` (the shape `STORED_HEREDOC` closes, and the terminator as bash reads it): text being stored names a guard without writing
/// one, and no other command in the call can run it (T029's constitution XIV fix; the round arbiter on `ask:449-T029-stored`).
fn without_stored_text(cmd: &str) -> String {
    let Ok(Some(m)) = STORED_HEREDOC.captures(cmd) else {
        return cmd.to_owned();
    };
    let text = |n: usize| m.get(n).map_or("", |g| g.as_str());
    let (dashed, delimiter, tabs) = (
        !text(1).is_empty(),
        [text(2), text(3), text(4)].concat(),
        text(6),
    );
    let ends_early = text(5).split('\n').any(|l| {
        (if dashed {
            l.trim_start_matches('\t')
        } else {
            l
        }) == delimiter
    });
    if ends_early || (!dashed && !tabs.is_empty()) {
        return cmd.to_owned();
    }
    let (start, end) = m.get(5).map_or((0, 0), |b| (b.start(), b.end()));
    format!("{}{}", &cmd[..start], &cmd[end..])
}

/// The verdict: `ok`, the rule broken, or `make-dup-var:<name>`.
pub(crate) fn classify(cmd: &str) -> String {
    if cmd.is_empty() {
        return "ok".to_owned();
    }
    if used(cmd, "GUARD_EDIT_OK") {
        return "guard-edit-ok".to_owned();
    }
    let clean = strip_quotes(&strip_heredocs(cmd));
    // each pattern below is compiled only for a command holding what it must name (T054: 10.9 ms of a `make` call)
    let names_a_file = cmd.split_whitespace().any(|w| {
        w == "-f" || w.starts_with("-f=") || w.starts_with("--file") || w.starts_with("--makefile")
    });
    if cmd.contains("make") && names_a_file && hit(&FOREIGN, &clean) {
        return "foreign-makefile".to_owned();
    }
    if cmd.contains("l7r") && (hit(&ENTRY_MODULE, &clean) || hit(&ENTRY_SCRIPT, &clean)) {
        return "engine-entry-point".to_owned();
    }
    if cmd.contains("pytest") && hit(&PYTEST, &pytest_view(cmd)) {
        return "bare-pytest".to_owned();
    }
    if cmd.contains("cargo") && hit(&CARGO, &clean) {
        return "bare-cargo".to_owned();
    }
    if (cmd.contains("l7r-guard") || cmd.contains("hamlet")) && hit(&BINARY, &clean) {
        return "bare-binary".to_owned();
    }
    if cmd.contains("make") && cmd.matches('=').count() >= 2 {
        let name = doubled_var(&clean);
        if !name.is_empty() {
            return format!("make-dup-var:{name}");
        }
    }
    if (cmd.contains("REF_") || cmd.contains("GATE_OK"))
        && hit(&OVERRIDE, &clean)
        && (hit(&AT_MAKE, &clean) || hit(&AT_OVERRIDE, &clean))
    {
        return "inline-override".to_owned();
    }
    let writes = cmd.contains('>')
        || cmd.contains("sed")
        || cmd.contains("tee")
        || cmd.contains("write_text")
        || cmd.contains("open(");
    let guard_named = ["Makefile", "-hooks.sh", "settings.json", "tests/rolls.py"]
        .iter()
        .any(|n| cmd.contains(n));
    if writes && guard_named {
        let (c, raw) = (
            replace_suites(&clean),
            replace_suites(&without_stored_text(cmd)),
        );
        if SHELL_WRITES.iter().any(|p| hit(p, &c))
            || PY_WRITES.iter().any(|p| hit(p, &raw))
            || write_via_name(&raw)
        {
            return "guard-write".to_owned();
        }
    }
    "ok".to_owned()
}

/// `cmd` with heredoc bodies and quoted strings replaced by spaces of the same length, so a match in it sits at the same offset in the raw text.
fn masked(cmd: &str) -> String {
    let blank = |pattern: &Regex, text: &str| {
        let mut bytes = text.as_bytes().to_vec();
        for m in pattern.find_iter(text).flatten() {
            bytes[m.start()..m.end()].fill(b' ');
        }
        String::from_utf8_lossy(&bytes).into_owned()
    };
    blank(&MASK_QUOTE, &blank(&MASK_HEREDOC, cmd))
}

/// The text after the invocation split at its first unquoted separator: (segment, rest).
fn split_segment(tail: &str) -> (&str, &str) {
    let bytes = tail.as_bytes();
    let (mut i, mut quote) = (0, 0_u8);
    while i < bytes.len() {
        let ch = bytes[i];
        if quote != 0 {
            if ch == b'\\' && quote == b'"' {
                i += 2;
                continue;
            }
            if ch == quote {
                quote = 0;
            }
        } else if ch == b'"' || ch == b'\'' {
            quote = ch;
        } else if ch == b'\\' {
            i += 2;
            continue;
        } else if matches!(ch, b';' | b'\n' | b')' | b'|')
            || (ch == b'&' && (bytes.get(i + 1) == Some(&b'&') || i == 0 || bytes[i - 1] != b'>'))
        {
            return tail.split_at(i);
        }
        i += 1;
    }
    (tail, "")
}

/// Shell-ish word split: (raw word, its unquoted value).
fn words(seg: &str) -> Vec<(String, String)> {
    let chars: Vec<char> = seg.chars().collect();
    let (len, mut start, mut out) = (chars.len(), 0, Vec::new());
    while start < len {
        while start < len && matches!(chars[start], ' ' | '\t') {
            start += 1;
        }
        if start >= len {
            break;
        }
        let (mut end, mut quote, mut buf) = (start, None, String::new());
        while end < len && (quote.is_some() || !matches!(chars[end], ' ' | '\t')) {
            let c = chars[end];
            match quote {
                Some(q) if c == q => quote = None,
                None if c == '"' || c == '\'' => quote = Some(c),
                _ => buf.push(c),
            }
            end += 1;
        }
        out.push((chars[start..end].iter().collect(), buf));
        start = end;
    }
    out
}

/// The compliant command for a targeted pytest, or why the shape keeps its refusal.
pub(crate) fn targeted_pytest(cmd: &str) -> Result<String, String> {
    let view = masked(cmd);
    let Ok(Some(found)) = PYTEST_RUN.find(&view) else {
        return Err("no pytest invocation".to_owned());
    };
    let (head, tail) = (&cmd[..found.start()], &cmd[found.end()..]);
    let (seg, rest) = split_segment(tail);
    let body = seg.trim_end();
    let ending = &seg[body.len()..];
    let list = words(body);
    let (mut paths, mut redirs, mut key): (Vec<String>, Vec<String>, Option<String>) =
        (Vec::new(), Vec::new(), None);
    let mut i = 0;
    while i < list.len() {
        let (raw, w) = (&list[i].0, list[i].1.as_str());
        let next = list.get(i + 1).map(|x| x.1.as_str());
        if w == "-k" || w.starts_with("-k=") {
            if key.is_some() {
                return Err("`-k` given twice".to_owned());
            }
            if let Some(expr) = w.strip_prefix("-k=") {
                key = Some(expr.to_owned());
                i += 1;
            } else {
                key = Some(next.ok_or("`-k` with no expression")?.to_owned());
                i += 2;
            }
        } else if hit(&REDIR_OP, w) {
            next.ok_or("a redirect with no target")?;
            redirs.push(format!("{raw} {}", list[i + 1].0));
            i += 2;
        } else if hit(&REDIR, w) {
            redirs.push(raw.clone());
            i += 1;
        } else if w == "-p" {
            if !next.is_some_and(|p| p.starts_with("no:")) {
                return Err(format!("`-p {}` loads a plugin", next.unwrap_or("")));
            }
            i += 2;
        } else if w.starts_with("-pno:") {
            i += 1;
        } else if ["-n", "--dist", "--tb", "--color"].contains(&w) {
            i += 2;
        } else if hit(&DROP_FLAG, w) {
            i += 1;
        } else if w.starts_with('-') {
            return Err(format!("`{w}`"));
        } else if w.starts_with('/') {
            return Err(format!("the absolute path `{w}`"));
        } else if hit(&TESTPATH, w) {
            paths.push(w.to_owned());
            i += 1;
        } else {
            return Err(format!("the argument `{w}`"));
        }
    }
    if paths.is_empty() {
        return Err("no test path".to_owned());
    }
    let file = if paths.len() > 1 {
        format!("\"{}\"", paths.join(" "))
    } else {
        paths[0].clone()
    };
    let mut out = format!("{head}make test-file FILE={file}");
    if let Some(expr) = key {
        if expr.contains(['"', '$', '`']) {
            return Err("a `-k` expression carrying a quote, a dollar or a backtick".to_owned());
        }
        out.push_str(" K=\"");
        out.push_str(&expr);
        out.push('"');
    }
    if !redirs.is_empty() {
        out.push(' ');
        out.push_str(&redirs.join(" "));
    }
    Ok(format!("{out}{ending}{rest}"))
}

/// One token of a recipe's arguments.
#[derive(Clone, Debug, PartialEq, Eq)]
enum Token {
    Args,
    Or(String),
    If(String, String),
    Literal(String),
}

/// Each target's recipe lines, comments left out.
fn recipes(text: &str) -> Vec<(String, Vec<String>)> {
    let (mut out, mut current): (Vec<(String, Vec<String>)>, Option<usize>) = (Vec::new(), None);
    for line in text.split('\n') {
        if let Some(rest) = line.strip_prefix('\t') {
            let body = rest.trim();
            if let Some(at) = current
                .filter(|_| !body.is_empty() && !body.starts_with('#') && !body.starts_with(": \""))
            {
                out[at].1.push(body.to_owned());
            }
        } else if let Some(name) = group(&TARGET_LINE, line).filter(|_| !line.contains(": export"))
        {
            let at = out.iter().position(|(t, _)| *t == name);
            current = Some(at.unwrap_or(out.len()));
            if at.is_none() {
                out.push((name, Vec::new()));
            }
        } else if !line.starts_with('#') {
            current = None;
        }
    }
    out
}

fn group(pattern: &Regex, text: &str) -> Option<String> {
    Some(pattern.captures(text).ok()??.get(1)?.as_str().to_owned())
}

type Table = BTreeMap<String, Vec<(String, Vec<Token>)>>;

/// Module to (target, recipe tokens) for every one-line `$(RUN).<module>` recipe.
fn wrapped_modules(text: &str) -> Table {
    let mut out: Table = BTreeMap::new();
    for (target, lines) in recipes(text) {
        let [only] = &lines[..] else {
            continue;
        };
        let line = only.trim_start_matches('@');
        let (module, rest) = if let Some(rest) = line.strip_prefix("$(SWITCH)") {
            ("switches".to_owned(), rest.to_owned())
        } else if let Ok(Some(m)) = RUN_LINE.captures(line) {
            (
                m.get(1).map_or("", |g| g.as_str()).to_owned(),
                m.get(2).map_or("", |g| g.as_str()).to_owned(),
            )
        } else {
            continue;
        };
        let tokens = RECIPE_ARG
            .captures_iter(&rest)
            .flatten()
            .map(|a| {
                let at = |n: usize| a.get(n).map_or("", |g| g.as_str()).to_owned();
                if a.get(1).is_some() {
                    Token::Or(at(1))
                } else if a.get(3).is_some() {
                    Token::If(at(3), at(4))
                } else if a.get(5).is_some() {
                    Token::Literal(at(5))
                } else {
                    Token::Args
                }
            })
            .collect();
        out.entry(module).or_default().push((target, tokens));
    }
    out
}

/// The `VAR=value` assignments that reproduce `args` through `tokens`, or None.
fn lay(args: &[String], tokens: &[Token]) -> Option<Vec<String>> {
    let (mut out, mut i) = (Vec::new(), 0);
    for token in tokens {
        let arg = args.get(i);
        match token {
            Token::Literal(l) => {
                if arg != Some(l) {
                    return None;
                }
                i += 1;
            }
            Token::Or(var) => {
                if let Some(a) = arg.filter(|a| !a.starts_with('-')) {
                    out.push(format!("{var}={a}"));
                    i += 1;
                }
            }
            Token::If(var, flag) => {
                if arg == Some(flag) {
                    out.push(format!("{var}=1"));
                    i += 1;
                }
            }
            Token::Args => {
                let rest = &args[i..];
                i = args.len();
                if !rest.is_empty() {
                    if rest.iter().any(|r| r.contains(['"', '\'', '$', '`'])) {
                        return None;
                    }
                    out.push(format!("ARGS=\"{}\"", rest.join(" ")));
                }
            }
        }
    }
    (i == args.len()).then_some(out)
}

/// The Makefile of the tree the command runs in, walking up from `cwd`, else this tree's own.
fn makefile_for(cwd: &str, tree: &Path) -> String {
    let start = if cwd.is_empty() {
        None
    } else {
        Path::new(cwd).canonicalize().ok()
    };
    let found = start
        .as_deref()
        .into_iter()
        .flat_map(Path::ancestors)
        .map(|d| d.join("Makefile"))
        .find(|f| f.is_file());
    std::fs::read_to_string(found.unwrap_or_else(|| tree.join("Makefile"))).unwrap_or_default()
}

/// The make target an engine entry point becomes, or why not.
pub(crate) fn wrapped(cmd: &str, makefile: &str) -> Result<String, String> {
    let view = masked(cmd);
    let Ok(Some(found)) = ENTRY_RUN.captures(&view) else {
        return Err("no engine entry point".to_owned());
    };
    let (start, end) = found.get(0).map_or((0, 0), |w| (w.start(), w.end()));
    let module = found.get(1).map_or("", |g| g.as_str());
    let (head, tail) = (&cmd[..start], &cmd[end..]);
    let (seg, rest) = split_segment(tail);
    let body = seg.trim_end();
    let ending = &seg[body.len()..];
    let (mut args, mut redirs) = (Vec::new(), Vec::new());
    for (raw, w) in words(body) {
        if hit(&REDIR, &w) {
            redirs.push(raw);
        } else if raw != w {
            return Err(format!("the quoted argument {raw}"));
        } else {
            args.push(w);
        }
    }
    let table = wrapped_modules(makefile);
    let Some(entries) = table.get(module) else {
        let listed: Vec<String> = table
            .iter()
            .flat_map(|(m, list)| {
                list.iter()
                    .map(move |(t, _)| format!("`{m}` -> `make {t}`"))
            })
            .collect();
        return Err(format!(
            "no make target wraps `l7r.diagram.{module}` (wrapped: {})",
            listed.join(", ")
        ));
    };
    for (target, tokens) in entries {
        if let Some(laid) = lay(&args, tokens) {
            let mut out = format!("{head}make {target}");
            for value in &laid {
                out.push(' ');
                out.push_str(value);
            }
            if !redirs.is_empty() {
                out.push(' ');
                out.push_str(&redirs.join(" "));
            }
            return Ok(format!("{out}{ending}{rest}"));
        }
    }
    Err(format!(
        "`make {}` cannot carry these arguments",
        entries[0].0
    ))
}

/// The landing's own lint on the `.py` files it names, run before the command does: a refusal naming ruff's first lines, or "".
pub(crate) fn landing_lint(cmd: &str, dir: &Path, python: &str) -> String {
    let Some(named) = group(&LANDING, &strip_heredocs(cmd)) else {
        return String::new();
    };
    let list = named.trim_matches(['"', '\'']).to_owned();
    let files: Vec<&str> = list
        .split_whitespace()
        .filter(|f| Path::new(f).extension().is_some_and(|e| e == "py") && dir.join(f).is_file())
        .collect();
    if files.is_empty() {
        return String::new();
    }
    for args in [vec!["check"], vec!["format", "--check"]] {
        let mut all = vec!["-m", "ruff"];
        all.extend(args);
        all.push("--force-exclude");
        all.extend(files.iter().copied());
        let said = ask_within(dir, python, &all, LINT_LIMIT);
        if said.code > 0 && !said.err.contains("No module named ruff") {
            let joined = format!("{}{}", said.out, said.err);
            let first: Vec<&str> = joined.trim().lines().take(8).collect();
            let listed = files.join(" ");
            return format!("the landing's lint fails on {listed}:\n{}\nRun python3 -m ruff format {listed}, fix what ruff listed, commit, then land (feature 385 T91)", first.join("\n"));
        }
    }
    String::new()
}

fn block(reason: &str, instead: &str) -> String {
    format!("BLOCKED: {reason}\n\nRun this instead:  {instead}\n\nIf this fired on correct work, it is a bug in the hook: put GUARD_EDIT_OK and a reason in the command.")
}

fn rewrite(input: &Value, command: &str, context: String) -> Vec<Answer> {
    let mut updated = input.clone();
    updated["command"] = json!(command);
    vec![Answer::Rewrite(updated), Answer::Notice(context)]
}

/// What this guard needs from outside the call.
pub(crate) struct Ctx<'a> {
    pub(crate) tree: PathBuf,
    pub(crate) here: PathBuf,
    pub(crate) python: &'a str,
}

pub(crate) fn judge(event: &Event, session: &Session, ctx: &Ctx) -> Vec<Answer> {
    let null = Value::Null;
    let input = event.input.get("tool_input").unwrap_or(&null);
    let cmd = field(input, "command");
    let verdict = classify(cmd);
    let given = field(&event.input, "cwd");
    let shown: String = cmd.chars().take(200).collect();
    let fire =
        |what: &str, rule: &str| log::fire("make-only", what, &shown, rule, &event.input, session);
    let refuse = |rule: &str, reason: &str, instead: &str| {
        fire("blocked", rule);
        vec![Answer::Refuse(block(reason, instead))]
    };
    if verdict == "ok" && (cmd.contains("land-tooling") || cmd.contains("arbiter-fix-done")) {
        let at = if given.is_empty() {
            ctx.here.as_path()
        } else {
            Path::new(given)
        };
        let lint = landing_lint(cmd, at, ctx.python);
        if !lint.is_empty() {
            return refuse(
                "landing-lint",
                &lint,
                "python3 -m ruff format <the files>, then the same landing",
            );
        }
    }
    if let Some(name) = verdict.strip_prefix("make-dup-var:").map(str::to_owned) {
        return refuse(
            "make-dup-var",
            &format!(
                "this make call sets {name} twice, and make silently keeps only the last value."
            ),
            &format!(
                "one call with {name}=\"<a> <b>\" (a quoted list), or one make call per value"
            ),
        );
    }
    match verdict.as_str() {
        "guard-edit-ok" => {
            let escape = escape_or_refuse(cmd, "GUARD_EDIT_OK");
            if let Escape::Refused(text) = escape {
                fire("blocked", "GUARD_EDIT_OK-no-reason");
                return vec![Answer::Refuse(text)];
            }
            if let Escape::Escaped(why) = escape {
                log::fire("make-only", "escaped", &why, "guard-edit-ok", &event.input, session);
            }
            Vec::new()
        }
        "bare-cargo" => refuse(&verdict, "cargo run outside make. The Rust phases are linted, formatted and tested through make, so the gate's lints and its shared target directory are the ones used.", "make static (clippy, rustfmt --check) | make format (rustfmt) | make rust-test (cargo test)"),
        "bare-binary" => refuse(&verdict, "a Rust binary run directly rather than through make. make is the one entry point (feature 449 FR-005): the guards' binary is built and driven by its wrapper, and a hamlet is rolled by its target.", "make hooks-test (the guards) | make hamlet SPEC=pool/hamlets/<name>/<name>.spec.json | make cohort"),
        "foreign-makefile" => refuse(&verdict, "a make driven by a named makefile. This project's targets are in its own Makefile, and a foreign one is the documented way to walk past every guard here.", "make <target>   (from the repository root)"),
        "engine-entry-point" => match wrapped(cmd, &makefile_for(given, &ctx.tree)) {
            Ok(fixed) => {
                fire("rewrote", "entry-point");
                let module = group(&LABEL_MODULE, cmd).unwrap_or(String::from("l7r.diagram..."));
                let target = group(&LABEL_TARGET, &fixed).unwrap_or(String::from("<target>"));
                let note = format!("`python3 -m {module}` was rewritten to `make {target}`, the target that wraps it - every engine entry point here is invoked through its make target (`make help` lists them). Corrected rather than refused, because a refusal costs a model round trip.");
                rewrite(input, &fixed, note)
            }
            Err(why) => refuse(&verdict, &format!("an engine entry point run outside make - {why}."), "make <target>   (make help lists the operations)"),
        },
        "bare-pytest" => match targeted_pytest(cmd) {
            Ok(fixed) => {
                fire("rewrote", "targeted-pytest");
                let label = LABEL_FILE.find(&fixed).ok().flatten().map_or("make test-file FILE=...".to_owned(), |m| m.as_str().to_owned());
                let note = format!("That bare pytest was rewritten to `{label}` - everything here goes through make so an expensive run can ask whether the cheap one would do first. Next time write it that way: `make test-file FILE=<file|dir|node id> [K=\"<-k expression>\"]`; a K= or node-id run is a SUBSET and owes a whole-file run before the gate. Corrected rather than refused, because a refusal costs a model round trip.");
                rewrite(input, &fixed, note)
            }
            Err(why) => refuse(&verdict, &format!("pytest run directly rather than through make. Everything here goes through a make target, so an expensive run can ask whether the cheap one would do first. A targeted run (files, a directory, a node id, -k, output flags, a pipeline after it) is rewritten for you; this one was not because of {why} - a marker, a deselect, a collection, a coverage or plugin flag changes WHAT runs, and that is yours to decide."), "make test-file FILE=<file|dir|node id> [K=\"<expr>\"]  or  make quick   (stops at the first failure)  or  make done   (the gate)"),
        },
        "inline-override" => refuse(&verdict, "an override supplied on the command line, which skips the prompt whose default answer is CANCEL. That prompt is the whole mechanism: it exists to be answered, not pre-empted.", "make <target>   without the override, and answer the prompt if it appears"),
        "guard-write" => refuse(&verdict, "a GUARD FILE written from a shell command. Layer 3 only sees the Edit and Write tools, so this route slips past it - the same ungated-sibling shape this feature exists to close.", "the Edit tool, or the same command ending in a trailing comment:  <command>  # GUARD_EDIT_OK: <reason>  - a marker INSIDE the text written does not count, since a guard file's text already holds old ones (GUARD_EDIT_OK: the round arbiter's fix on hour:383@4)"),
        _ => Vec::new(),
    }
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let here = std::env::current_dir().unwrap_or_default();
    let tree = std::env::var("L7R_GUARD_TREE").map_or_else(|_| here.clone(), PathBuf::from);
    judge(
        event,
        session,
        &Ctx {
            tree,
            here,
            python: "python3",
        },
    )
}

#[cfg(test)]
mod tests;
