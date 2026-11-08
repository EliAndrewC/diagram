//! Where a command's writes land (`scripts/hooks/lib/hm_tree.py` - feature 449 T010 decision (a)): the effective directory walked
//! through the command's own `cd`s, variables and subshells, every write classified by where it lands - the mirror, a clone or
//! elsewhere - and a write that lands in the mirror by where the shell stands rewritten into the session's clone, the rewrite
//! re-judged so it never returns a command it would refuse. Each pattern is the Python's verbatim; the reasons stand in its
//! comments, kept in git history.

use std::collections::HashMap;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};
use serde_json::{json, Value};

use super::shape::strip_heredocs;

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("a guard's own pattern: {e}"))
}

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
const FILE_TOOLS_ALL: [&str; 12] = [
    "vim", "vi", "nano", "emacs", "tee", "touch", "mkdir", "rmdir", "rm", "mv", "chmod", "chown",
];
const FILE_TOOLS_LAST: [&str; 3] = ["cp", "ln", "install"];
const WRAPPERS: [&str; 9] = [
    "sudo", "nohup", "setsid", "env", "command", "exec", "time", "nice", "builtin",
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

static ASSIGN: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r#"(?:^|[;&|\n(]|&&|\|\|)\s*(?:export\s+)?([A-Za-z_]\w*)=(?:"([^"\n]*)"|'([^'\n]*)'|([^\s;&|)]*))"#,
    )
});
static VAR: LazyLock<Regex> = LazyLock::new(|| re(r"\$\{(\w+)\}|\$(\w+)"));
static QUOTED: LazyLock<Regex> = LazyLock::new(|| re(r#"(?s)(["'])((?:\\.|(?!\1).)*)\1"#));
static PLAIN_QUOTE_BODY: LazyLock<Regex> = LazyLock::new(|| re(r"^[^\s;|&()<>`\n]*$"));
static REDIRECT: LazyLock<Regex> = LazyLock::new(|| re(r"(?<![<>])\d?>{1,2}\|?\s*([^\s;&|()<>]+)"));
static FUNCTION_DEF: LazyLock<Regex> = LazyLock::new(|| re(r"^\s*[\w-]+\s*\(\s*\)"));
static DUP_FD: LazyLock<Regex> = LazyLock::new(|| re(r"\d*>&[0-9-]"));
static DEV_NULL: LazyLock<Regex> = LazyLock::new(|| re(r"\d*>\s*/dev/null"));
static ASSIGNMENT_WORD: LazyLock<Regex> = LazyLock::new(|| re(r"^[A-Za-z_]\w*="));
static PYTHON: LazyLock<Regex> = LazyLock::new(|| re(r"^python3?$"));

fn found(p: &Regex, text: &str) -> bool {
    p.is_match(text).unwrap_or(false)
}

/// Python's `posixpath.normpath`.
#[must_use]
pub fn normpath(path: &str) -> String {
    if path.is_empty() {
        return ".".to_owned();
    }
    let slashes = if path.starts_with("//") && !path.starts_with("///") {
        2
    } else {
        usize::from(path.starts_with('/'))
    };
    let mut out: Vec<&str> = Vec::new();
    for comp in path.split('/') {
        if comp.is_empty() || comp == "." {
            continue;
        }
        if comp != ".." || (slashes == 0 && out.is_empty()) || out.last() == Some(&"..") {
            out.push(comp);
        } else if !out.is_empty() {
            out.pop();
        }
    }
    let joined = format!("{}{}", "/".repeat(slashes), out.join("/"));
    if joined.is_empty() {
        ".".to_owned()
    } else {
        joined
    }
}

/// Python's `posixpath.join` of two parts.
fn join(a: &str, b: &str) -> String {
    if b.starts_with('/') || a.is_empty() {
        b.to_owned()
    } else if a.ends_with('/') {
        format!("{a}{b}")
    } else {
        format!("{a}/{b}")
    }
}

/// Python's `os.path.relpath` of two absolute paths.
fn relpath(path: &str, start: &str) -> String {
    let (p, s) = (normpath(path), normpath(start));
    let pc: Vec<&str> = p.split('/').filter(|c| !c.is_empty()).collect();
    let sc: Vec<&str> = s.split('/').filter(|c| !c.is_empty()).collect();
    let common = pc.iter().zip(&sc).take_while(|(a, b)| a == b).count();
    let parts: Vec<&str> = std::iter::repeat_n("..", sc.len() - common)
        .chain(pc[common..].iter().copied())
        .collect();
    if parts.is_empty() {
        ".".to_owned()
    } else {
        parts.join("/")
    }
}

/// A quoted string kept as its body where it is one plain word (a path), else blanked to an empty pair (`_quotes_to_paths`).
fn quotes_to_paths(cmd: &str) -> String {
    QUOTED
        .replace_all(cmd, |c: &Captures| {
            let body = c.get(2).map_or("", |m| m.as_str());
            if found(&PLAIN_QUOTE_BODY, body) {
                body.to_owned()
            } else {
                c.get(1).map_or("", |m| m.as_str()).repeat(2)
            }
        })
        .into_owned()
}

fn sanitize(cmd: &str) -> String {
    let text = quotes_to_paths(&strip_heredocs(cmd));
    let text = DUP_FD.replace_all(&text, " ");
    DEV_NULL.replace_all(&text, " ").into_owned()
}

type Env = HashMap<String, String>;

/// A token with its variables and `~` substituted, or None where something in it cannot be (`_expand`).
fn expand(token: &str, env: &Env, home: &str) -> Option<String> {
    let mut token = token
        .strip_prefix('~')
        .map_or_else(|| token.to_owned(), |rest| format!("{home}{rest}"));
    for _ in 0..6 {
        if !token.contains('$') {
            break;
        }
        token = VAR
            .replace_all(&token, |c: &Captures| {
                let name = c.get(1).or_else(|| c.get(2)).map_or("", |m| m.as_str());
                env.get(name)
                    .cloned()
                    .unwrap_or_else(|| c.get(0).map_or("", |m| m.as_str()).to_owned())
            })
            .into_owned();
    }
    (!token.contains('$') && !token.contains('`')).then_some(token)
}

/// `NAME=value` assignments at command positions, resolved through each other in order (`_env_from`).
fn env_from(cmd: &str, start: Option<&str>, home: &str) -> Env {
    let mut env = Env::from([("HOME".to_owned(), home.to_owned())]);
    if let Some(c) = start {
        env.insert("PWD".to_owned(), c.to_owned());
    }
    let text = strip_heredocs(cmd);
    for c in ASSIGN.captures_iter(&text).filter_map(Result::ok) {
        let name = c.get(1).map_or("", |m| m.as_str()).to_owned();
        let value = (2..=4)
            .find_map(|i| c.get(i))
            .map_or("", |m| m.as_str())
            .to_owned();
        let expanded = expand(&value, &env, home).unwrap_or(value);
        env.insert(name, expanded);
    }
    env
}

fn strip_quote_chars(token: &str) -> &str {
    token.trim_matches(|c| c == '"' || c == '\'')
}

/// A path token as an absolute, normalized path, or None where it cannot be known (`_resolve`).
fn resolve(token: &str, env: &Env, home: &str, effective: Option<&str>) -> Option<String> {
    let expanded = expand(strip_quote_chars(token), env, home).filter(|e| !e.is_empty())?;
    if expanded.starts_with('/') {
        return Some(normpath(&expanded));
    }
    effective.map(|e| normpath(&join(e, &expanded)))
}

/// The mirror outside its `.clones`, a clone, elsewhere, or unknown (`classify`).
#[must_use]
pub fn classify(path: Option<&str>, main: &str) -> &'static str {
    let Some(path) = path else {
        return "unknown";
    };
    let clones = format!("{main}/.clones");
    if path == clones || path.starts_with(&format!("{clones}/")) {
        "clone"
    } else if path == main || path.starts_with(&format!("{main}/")) {
        "main"
    } else {
        "elsewhere"
    }
}

/// One piece of a command split at its separators: a segment, or a subshell's opening or closing (`_segments`).
#[derive(Debug, PartialEq, Eq)]
enum Piece {
    Seg(String),
    Push,
    Pop,
}

fn segments(text: &str) -> Vec<Piece> {
    let chars: Vec<char> = text.chars().collect();
    let (mut out, mut buf, mut i) = (Vec::new(), String::new(), 0);
    let flush = |buf: &mut String, out: &mut Vec<Piece>| {
        let seg = buf.trim().to_owned();
        buf.clear();
        if !seg.is_empty() {
            out.push(Piece::Seg(seg));
        }
    };
    while i < chars.len() {
        let ch = chars[i];
        let next = chars.get(i + 1).copied();
        if (ch == '&' && next == Some('&')) || (ch == '|' && next == Some('|')) {
            flush(&mut buf, &mut out);
            i += 2;
        } else if ch == '$' && next == Some('(') {
            flush(&mut buf, &mut out);
            out.push(Piece::Push);
            i += 2;
        } else if (ch == '|' || ch == '&') && buf.ends_with('>') {
            buf.push(ch); // `>|` and `>&` belong to the redirection, not a separator (feature 429)
            i += 1;
        } else if matches!(ch, ';' | '|' | '&' | '\n') {
            flush(&mut buf, &mut out);
            i += 1;
        } else if ch == '(' {
            flush(&mut buf, &mut out);
            out.push(Piece::Push);
            i += 1;
        } else if ch == ')' {
            flush(&mut buf, &mut out);
            out.push(Piece::Pop);
            i += 1;
        } else if ch == '{' || ch == '}' {
            flush(&mut buf, &mut out);
            i += 1;
        } else {
            buf.push(ch);
            i += 1;
        }
    }
    flush(&mut buf, &mut out);
    out
}

/// The segment's words with leading wrappers and `VAR=value` prefixes removed (`_words`).
fn words(seg: &str) -> Vec<&str> {
    let mut toks: Vec<&str> = seg.split_whitespace().collect();
    while let Some(t) = toks.first() {
        if WRAPPERS.contains(t) || found(&ASSIGNMENT_WORD, t) {
            toks.remove(0);
        } else if *t == "timeout" && toks.len() > 1 {
            toks.drain(..2);
        } else {
            break;
        }
    }
    toks
}

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

/// A write's target and whether the command named it (`named`) or it lands where the shell stands (`shell`).
type Write = (Option<String>, &'static str);

/// (target, how) where a git invocation writes (`_git_write`).
fn git_write(toks: &[&str], env: &Env, home: &str, eff: Option<&str>) -> Option<Write> {
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
    let sub = *toks.get(i)?;
    if !(GIT_WRITES.contains(&sub) || (sub == "branch" && branch_writes(&toks[i + 1..]))) {
        return None;
    }
    let Some(c) = c_path else {
        return Some((eff.map(str::to_owned), "shell"));
    };
    let how = if strip_quote_chars(c).starts_with('/') {
        "named"
    } else {
        "shell"
    };
    Some((resolve(c, env, home, eff), how))
}

/// The paths a file tool writes (`_tool_paths`): `sed`'s files past its script, the last argument of a copy, else every argument.
fn tool_paths<'a>(tool: &str, toks: &[&'a str]) -> Vec<&'a str> {
    let args: Vec<&str> = toks[1..]
        .iter()
        .copied()
        .filter(|t| !matches!(*t, "''" | "\"\"" | "--") && !t.contains("<<"))
        .collect();
    if tool == "sed" {
        let (mut keep, mut skip_next) = (Vec::new(), false);
        let mut script_seen = args.contains(&"-e") || args.contains(&"--expression");
        for t in args {
            if skip_next {
                skip_next = false;
            } else if matches!(t, "-e" | "--expression" | "-f" | "--file") {
                skip_next = true;
            } else if t.starts_with('-') {
            } else if !script_seen {
                script_seen = true; // the first bare argument is the sed script, not a file
            } else {
                keep.push(t);
            }
        }
        return keep;
    }
    let args: Vec<&str> = args.into_iter().filter(|t| !t.starts_with('-')).collect();
    if FILE_TOOLS_LAST.contains(&tool) {
        return args.last().copied().into_iter().collect();
    }
    args
}

fn path_write(p: &str, env: &Env, home: &str, eff: Option<&str>) -> Write {
    let bare = strip_quote_chars(p);
    match expand(bare, env, home) {
        Some(e) if e.starts_with('/') => (Some(normpath(&e)), "named"),
        None => (
            None,
            if bare.starts_with('/') {
                "named"
            } else {
                "shell"
            },
        ),
        Some(_) => (resolve(bare, env, home, eff), "shell"),
    }
}

/// Every write in one segment (`_writes_in`).
fn writes_in(seg: &str, env: &Env, home: &str, eff: Option<&str>) -> Vec<Write> {
    let mut found_writes = Vec::new();
    let toks = words(seg);
    if let Some(head) = toks.first() {
        let base = head.rsplit('/').next().unwrap_or(head);
        if *head == "git" {
            found_writes.extend(git_write(&toks, env, home, eff));
        } else if base == "make" || (found(&PYTHON, base) && toks.get(1) == Some(&"-c")) {
            found_writes.push((eff.map(str::to_owned), "shell"));
        } else if base == "sed"
            && toks[1..]
                .iter()
                .any(|t| t.starts_with("-i") || *t == "--in-place")
        {
            found_writes.extend(
                tool_paths("sed", &toks)
                    .into_iter()
                    .map(|p| path_write(p, env, home, eff)),
            );
        } else if FILE_TOOLS_ALL.contains(&base) || FILE_TOOLS_LAST.contains(&base) {
            found_writes.extend(
                tool_paths(base, &toks)
                    .into_iter()
                    .map(|p| path_write(p, env, home, eff)),
            );
        }
    }
    for c in REDIRECT.captures_iter(seg).filter_map(Result::ok) {
        found_writes.push(path_write(
            c.get(1).map_or("", |m| m.as_str()),
            env,
            home,
            eff,
        ));
    }
    found_writes
}

/// One write found by the walk: where it lands, its class, how it was reached, and the segment it is in.
#[derive(Debug, Clone)]
pub struct Target {
    pub path: Option<String>,
    pub class: &'static str,
    pub how: &'static str,
    pub segment: String,
}

/// The walk's answer (`walk`).
#[derive(Debug, Clone)]
pub struct Walk {
    pub targets: Vec<Target>,
    pub final_dir: Option<String>,
    pub cd_into_main: bool,
    pub standing: &'static str,
}

/// The effective directory through the command, and every write with where it lands (`walk`).
#[must_use]
pub fn walk(cmd: &str, start: Option<&str>, main: &str, home: &str) -> Walk {
    let env = env_from(cmd, start, home);
    let text = sanitize(cmd);
    let mut eff: Option<String> = start.map(str::to_owned);
    let mut hint = classify(eff.as_deref(), main); // where the shell was last KNOWN to be (spec D6)
    let (mut stack, mut targets, mut cd_into_main) = (Vec::new(), Vec::new(), false);
    for piece in segments(&text) {
        let seg = match piece {
            Piece::Push => {
                stack.push((eff.clone(), hint));
                continue;
            }
            Piece::Pop => {
                if let Some((e, h)) = stack.pop() {
                    (eff, hint) = (e, h);
                }
                continue;
            }
            Piece::Seg(s) => s,
        };
        let toks = words(&seg);
        if matches!(toks.first(), Some(&"cd" | &"pushd")) {
            eff = match toks.get(1) {
                None | Some(&"--") => Some(home.to_owned()),
                Some(&"-") => None,
                Some(t) => resolve(t, &env, home, eff.as_deref()),
            };
            if eff.is_some() {
                hint = classify(eff.as_deref(), main);
                cd_into_main |= hint == "main";
            }
            continue;
        }
        if toks.first() == Some(&"popd") {
            eff = None;
            continue;
        }
        for (path, how) in writes_in(&seg, &env, home, eff.as_deref()) {
            let mut class = classify(path.as_deref(), main);
            if class == "unknown" {
                class = if hint == "main" { "main" } else { "elsewhere" }; // D6: unknown resolves toward main
            }
            targets.push(Target {
                path,
                class,
                how,
                segment: seg.chars().take(120).collect(),
            });
        }
    }
    Walk {
        targets,
        final_dir: eff,
        cd_into_main,
        standing: classify(start, main),
    }
}

/// Every command-position `cd <main>[/sub]` of the original text made `cd <clone>[/sub]` (`_rewrite_cds`).
fn rewrite_cds(cmd: &str, main: &str, clone: &str) -> String {
    let pat = re(&format!(
        r#"(?m)((?:^|[;&|(\n]|&&|\|\|)\s*(?:\(\s*)?(?:cd|pushd)\s+)(["']?){}(?=/(?!\.clones(?:/|$))|["'\s;&|)]|$)"#,
        fancy_regex::escape(main)
    ));
    pat.replace_all(cmd, |c: &Captures| {
        format!(
            "{}{}{clone}",
            c.get(1).map_or("", |m| m.as_str()),
            c.get(2).map_or("", |m| m.as_str())
        )
    })
    .into_owned()
}

/// The verdict on one hook input (`judge`): its kind, reason and cause, the walk's context, and a rewrite's command.
#[derive(Debug, Clone)]
pub struct Verdict {
    pub verdict: &'static str,
    pub reason: &'static str,
    pub cause: &'static str,
    pub cwd: Option<String>,
    pub walk: Walk,
    pub clone: Option<String>,
    pub prepended: Option<bool>,
    pub command: Option<String>,
}

impl Verdict {
    /// The verdict as the Python's JSON, its `hook` left out (`log-context`).
    #[must_use]
    pub fn context(&self) -> Value {
        let targets: Vec<Value> = self
            .walk
            .targets
            .iter()
            .map(|t| json!({"path": t.path, "class": t.class, "how": t.how, "segment": t.segment}))
            .collect();
        let mut ctx = json!({
            "cwd": self.cwd, "standing": self.walk.standing, "final_dir": self.walk.final_dir, "cd_into_main": self.walk.cd_into_main,
            "targets": targets, "clone": self.clone,
        });
        if let Some(p) = self.prepended {
            ctx["prepended"] = Value::Bool(p);
        }
        let mut out = json!({"verdict": self.verdict, "reason": self.reason, "cause": self.cause, "context": ctx});
        if let Some(c) = &self.command {
            out["command"] = Value::String(c.clone());
        }
        out
    }
}

/// The verdict for one hook input; `resolved` says the caller already tried to find the clone (`judge`).
#[must_use]
pub fn judge(
    input: &Value,
    main: &str,
    clone: Option<&str>,
    home: &str,
    resolved: bool,
) -> Verdict {
    let ti = input.get("tool_input").cloned().unwrap_or(Value::Null);
    let cmd = ti.get("command").and_then(Value::as_str).unwrap_or("");
    let start = input
        .get("cwd")
        .and_then(Value::as_str)
        .filter(|c| !c.is_empty());
    let main = main.trim_end_matches('/');
    let w = walk(cmd, start, main, home);
    let named = w
        .targets
        .iter()
        .any(|t| t.class == "main" && t.how == "named");
    let shell = w
        .targets
        .iter()
        .any(|t| t.class == "main" && t.how == "shell");
    let mut v = Verdict {
        verdict: "allow",
        reason: "no-write-in-main",
        cause: "",
        cwd: start.map(str::to_owned),
        walk: w.clone(),
        clone: clone.map(str::to_owned),
        prepended: None,
        command: None,
    };
    let mut out = |verdict, reason, cause| {
        (v.verdict, v.reason, v.cause) = (verdict, reason, cause);
        v.clone()
    };
    if named {
        return out("refuse", "named-main", "named");
    }
    if !shell {
        return out("allow", "no-write-in-main", "");
    }
    let cause = if w.cd_into_main { "cd" } else { "standing" };
    let Some(clone) = clone else {
        return out(
            if resolved { "refuse" } else { "needs-clone" },
            "clone-unresolved",
            cause,
        );
    };
    if !Path::new(clone).join(".git").exists() {
        return out("refuse", "clone-missing", cause);
    }
    if found(&FUNCTION_DEF, cmd) {
        return out("refuse", "shape", cause);
    }
    let mut new = rewrite_cds(cmd, main, clone);
    let mut prepended = false;
    let mut w2 = walk(&new, start, main, home);
    if w2.targets.iter().any(|t| t.class == "main") && w.standing == "main" {
        let sub = start
            .filter(|c| *c != main)
            .map(|c| relpath(c, main))
            .unwrap_or_default();
        let at = if sub.is_empty() || sub == "." {
            clone.to_owned()
        } else {
            join(clone, &sub)
        };
        new = format!("cd {at} && {new}");
        prepended = true;
        w2 = walk(&new, start, main, home);
    }
    if w2.targets.iter().any(|t| t.class == "main") {
        return out("refuse", "shape", cause); // re-judged and still lands in main: never emit that
    }
    v.prepended = Some(prepended);
    v.command = Some(new);
    (v.verdict, v.reason, v.cause) = ("rewrite", "moved-to-clone", cause);
    v
}

/// What the session is told of a rewrite into its clone (`_context_line`).
#[must_use]
pub fn context_line(v: &Verdict, main: &str) -> String {
    let clone = v.clone.as_deref().unwrap_or("");
    let opening = if v.cause == "cd" {
        format!(
            "This command cd'd into {main} - the MIRROR, main's tree, never a workspace - and then wrote there. The cd was rewritten to \
your clone, {clone}, at the same relative position"
        )
    } else {
        format!(
            "Your shell was standing in {}, inside {main} - the MIRROR, main's tree, never a workspace - so this command's write would have \
landed in main. It was rewritten to run in your clone: `cd {clone}` was prepended",
            v.cwd.as_deref().unwrap_or("None")
        )
    };
    format!(
        "{opening}, and the shell stays in the clone for later commands. Read main with `git -C {main} <read>`; do everything else in the \
clone (CLAUDE.md, 'Session clones'). Rewritten rather than refused: a refusal costs a model round trip to say the same thing. \
(rust/guard/src/guards/main_tree_hooks.rs; feature 204)"
    )
}

/// The refusal text, naming the actual cause (`explain`).
#[must_use]
pub fn explain(v: &Verdict, main: &str) -> String {
    let clone = v.clone.as_deref().unwrap_or("<your clone under .clones/>");
    let where_ = match v.cause {
        "named" => "this command names a path inside the mirror and writes to it".to_owned(),
        "cd" => format!("this command cds into {main} - the MIRROR - and then writes there"),
        _ => format!(
            "your shell is standing in {}, inside {main} - the MIRROR - and this command writes where it stands",
            v.cwd.as_deref().unwrap_or("None")
        ),
    };
    let mut lines = vec![
        format!("BLOCKED: {where_}."),
        String::new(),
        "Main is the integration point, never a workspace. The only write a session makes there is".to_owned(),
        "render-sync, and that names the tree with `git -C` from sync-with-main.sh rather than cd-ing.".to_owned(),
        String::new(),
    ];
    match v.reason {
        "named-main" => {
            let named: Vec<String> = v
                .walk
                .targets
                .iter()
                .filter(|t| t.class == "main" && t.how == "named")
                .map(|t| {
                    t.path.clone().unwrap_or_else(|| {
                        format!("a target this cannot resolve, in `{}`", t.segment)
                    })
                })
                .collect();
            lines.push(format!("Named: {}", named.join(", ")));
            lines.push("A write that merely LANDS in main because of where the shell stands is moved to your clone".to_owned());
            lines.push("(feature 204); one that names main by its path says what it means, and a guard never guesses at".to_owned());
            lines.push(format!("that. Do it in your clone instead: {clone}."));
        }
        "clone-unresolved" => {
            lines.push("It would have been moved to your clone, but this session's clone cannot be resolved: no claim".to_owned());
            lines.push("under .clones/.session-clones, no /rename record in the transcript, no sessions entry. Ask the".to_owned());
            lines.push("GM to /rename the session, then work in .clones/<kebab-name>.".to_owned());
        }
        "clone-missing" => {
            lines.push(format!("It would have been moved to your clone, {clone}, which does not exist yet. Create it:"));
            lines.push(format!(
                "  git clone {main} {clone} && ( cd {clone} && scripts/sync-with-main.sh sync-in )"
            ));
        }
        _ => {
            lines.push("It would have been moved to your clone, but the command's shape could not be rewritten safely".to_owned());
            lines.push("(it opens with a function definition, or the cd into main is reached through a variable and".to_owned());
            lines.push(format!("cannot be located in the original text). Run it as `( cd {clone} && ... )` yourself."));
        }
    }
    lines.push(String::new());
    lines.push(format!("Reading main stays fine: `git -C {main} <read>`. If this genuinely needs to write in main, put"));
    lines.push(
        "MAIN_TREE_OK in the command with the reason, and the reason ships with it.".to_owned(),
    );
    lines.push(String::new());
    lines.push("(rust/guard/src/guards/main_tree_hooks.rs; features 169 and 204)".to_owned());
    lines.join("\n")
}

#[cfg(test)]
mod tests;
