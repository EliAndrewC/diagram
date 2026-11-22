//! `make-only-hooks` (feature 127; features 164, 212, 385, 444; ported from the shell of the same name and the deciding half of `lib/hm_make.py`, feature 449 T028): EVERY OPERATION GOES THROUGH ITS MAKE
//! TARGET, so an expensive run can ask whether the cheap one would do first. An engine entry point, a bare cargo or a replacement's binary, a foreign makefile, an inline override and a guard file
//! written from the shell are refused; an entry point a make target wraps is rewritten into that target. `GUARD_EDIT_OK` with a reason is the escape. The bare-pytest branch
//! (refused, or a targeted run rewritten to `make test-file`) left with pytest and its targets (feature 449 T213); with it went T214's defect, a pytest MENTION in a
//! quoted `python3 -c` program refused as a run.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Value};

use crate::guards::guard_file_hooks::{held, named};
use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{escape_or_refuse, used, Escape};
use crate::shared::log;
use crate::shared::make::{POS, PY};
use crate::shared::session::Session;
use crate::shared::shape::{quoted_spans, strip_heredocs, strip_quotes};
use crate::shared::state::field;
use crate::shared::tree::{walk_judged, Target, Walk};

pub(crate) mod interp;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "make-only-hooks",
    events: &["PreToolUse"],
    matcher: "Bash",
    decide,
};

/// The guard files by name, for the patterns over a command's text; T229 added the guards' own sources (every file there but a test file).
const GUARD_FILE: &str = r"[\w./-]*(?:Makefile|[\w-]*-hooks\.sh|settings\.json|tests/rolls\.py|dev/(?:switches|work-budget)\.json|rust/guard/(?:shared/)?src/(?!(?:[\w.-]+/)*tests(?:\.rs|/))[\w./-]+|rust/guard/(?:shared/)?Cargo\.toml|l7r-guard\.sh)";
/// The names a command must hold before its writes are resolved: each guard file's last part, so a `cd` into its directory still
/// names it (T227: `cd dev && cat > switches.json` held none of the old list, which had `tests/rolls.py` and no `dev/` file).
const GUARD_NAMES: [&str; 6] = [
    "Makefile",
    "-hooks.sh",
    "settings.json",
    "rolls.py",
    "switches.json",
    "work-budget.json",
];
/// What else makes a command worth walking (T229): the guards' own sources, whose names are a directory and a script, not a suffix. They
/// never "clear" a write by its name the way `GUARD_NAMES` do - a `.rs` overrules a pattern only where the walk placed it in scratch,
/// for its own statement (451 T87).
const SOURCE_NAMES: [&str; 4] = ["guard/src", "shared/src", "Cargo.toml", "l7r-guard.sh"];
/// The tools that change a file's mode, times or directory but never its text: a guard file `chmod +x`ed is not rewritten.
const NOT_TEXT: [&str; 5] = ["chmod", "chown", "touch", "mkdir", "rmdir"];
const SUITE_NAME: &str = "<a-suite>";

fn re(pattern: &str) -> Regex {
    crate::shared::regex::build(pattern).unwrap_or_else(|e| unreachable!("{pattern}: {e}"))
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
    CARGO,
    format!(
        r"{POS}(?:\S*/)?cargo\s+(?:\+\S+\s+)?(?:build|test|run|clippy|check|fmt|llvm-cov|bench|nextest)\b"
    )
);
lazy!(
    RUSTFMT,
    format!(r"(?:{POS}|\bxargs\s+(?:-\S+\s+)*|-exec(?:dir)?\s+)(?:\S*/)?rustfmt(?![\w.-])")
);
lazy!(
    RUSTFMT_INFO,
    r"(?:\S*/)?rustfmt\s+(?:--version|-V|--help|-h)(?=\s*(?:$|[;&|\n)]))"
);
lazy!(
    BINARY,
    format!(
        r"{POS}(?:\S*/)?(l7r-guard|l7r-gate|l7r-rust|l7r-browser|l7r-embed|l7r-mode-a|hamlet)(?![\w.-])"
    )
);
lazy!(MAKE_ARGS, format!(r"{POS}(?:\$\(MAKE\)|make)\b([^\n;|&]*)"));
lazy!(ASSIGN, r"(?<!\S)([A-Za-z_][A-Za-z0-9_]*)=");
lazy!(OVERRIDE, r"\b(?:REF_WHY|REF_OK|GATE_OK)=");
lazy!(AT_MAKE, format!(r"{POS}make\b"));
lazy!(AT_OVERRIDE, format!(r"{POS}(?:REF_WHY|REF_OK|GATE_OK)="));
lazy!(SUITE, r"[\w./-]*tests/hooks/test-[\w-]*-hooks\.sh");
lazy!(REDIR, r"^(?:\d?>>?&?\S+|\d?<\S+)$");
lazy!(MASK_HEREDOC, r#"(?s)<<-?\s*['"]?(\w+)['"]?\n.*?\n\s*\1\b"#);
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
lazy!(LABEL_MODULE, r"-m\s+(l7r\.diagram\.[\w.]+)");
lazy!(LABEL_TARGET, r"\bmake\s+([a-z][\w-]*(?:\s+[A-Z_]+=\S*)*)");

/// The patterns over the text, for what the shell walk cannot see (a write inside `find -exec`, a loop's body); a name ends at a
/// space, the end, or a separator - `do sed -i s/a/b/ Makefile; done` once passed for its `;` (T227).
static SHELL_WRITES: LazyLock<[Regex; 3]> = LazyLock::new(|| {
    [
        re(&format!(r"(?<![-\w])>>?\s*{GUARD_FILE}(?:[\s;&|)]|$)")),
        re(&format!(r"sed\s+-i\b[^;|&]*?{GUARD_FILE}(?:[\s;&|)]|$)")),
        re(&format!(r"tee\s+(?:-a\s+)?{GUARD_FILE}(?:[\s;&|)]|$)")),
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
        .flat_map(|b| {
            b.captures_iter(raw)
                .map_while(Result::ok)
                .collect::<Vec<_>>()
        })
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
    for m in MAKE_ARGS.captures_iter(clean).map_while(Result::ok) {
        let mut seen = Vec::new();
        for assign in ASSIGN
            .captures_iter(m.get(1).map_or("", |g| g.as_str()))
            .map_while(Result::ok)
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
    for m in SUITE.find_iter(text).map_while(Result::ok) {
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

/// The verdict of a command whose working directory is not known: its relative paths are read from `/`, so a path's own parts
/// (`dev/switches.json`, `cd dev && ... switches.json`) still name the file. The tests' and the refusal corpus's entry; a live call
/// knows its directory and goes through `classify_at`.
#[cfg(test)]
pub(crate) fn classify(cmd: &str) -> String {
    classify_at(cmd, "/")
}

/// What the shell walk makes of a command's writes - a redirect, `sed -i`, `perl -i`, `tee`, `cp`, `mv`, `install`, through its own
/// `cd`s - judged by THE guard file list (`guard_file_hooks::held`): (a write lands on a guard file, a write named like one lands
/// on a file that is not one, the programs whose guard files' names all land in scratch). The walk reads a command at its head, so the
/// patterns over the text still judge what it cannot see (`find -exec sed -i`); the second answer is what lets it overrule them - a
/// `settings.json` in a scratch directory, a suite written after a `cd` into `tests/hooks` (T227), a guard file's name written in
/// scratch (451 T87) - and the third what the Python patterns no longer read.
fn walked_write(cmd: &str, here: &str) -> (bool, bool, Vec<String>) {
    let home = std::env::var("HOME").unwrap_or_default();
    // the judged walk (451 T33): a Python program run from stdin that writes is a write where the shell stands, as a `-c` one is
    let Walk { targets, .. } = walk_judged(cmd, Some(here), "", &home);
    let text_tool = |seg: &str| {
        let head = seg.split_whitespace().next().unwrap_or_default();
        seg.contains('>') || !NOT_TEXT.contains(&head.rsplit('/').next().unwrap_or(head))
    };
    let paths = || {
        targets
            .iter()
            .filter_map(|t| t.path.as_deref().map(|p| (p, t)))
    };
    // a program `py_c` judged a read writes nothing, where it stands too (451 T33: a `-c` read in a guard directory was refused);
    // a writer is judged by where it stands and by the files its body names; a `CDPATH`, which the walk does not read, can carry a
    // `cd` out of scratch into a tree, and a `worktree add` makes a project's worktree in scratch before any pointer shows it, so a
    // command naming either keeps HEAD's reading by name (451 T87: `CDPATH=/diagram/.clones cd s`, `git -C <clone> worktree add`)
    let words: Vec<&str> = cmd.split_whitespace().collect();
    let kept = cmd.contains("CDPATH") || words.windows(2).any(|w| w == ["worktree", "add"]);
    let on_guard = targets.iter().filter(|t| t.how != "read").any(|t| {
        t.path
            .as_deref()
            .is_some_and(|p| (held(p) || (kept && named(p))) && text_tool(&t.segment))
            || t.program.as_deref().is_some_and(|b| {
                interp::program_names_guard(b, t.path.as_deref(), true)
                    || (kept && interp::program_names_named(b, t.path.as_deref()))
            })
    });
    // a guard file's name in scratch (451 T87) overrules them hit by hit, each only where its own statement is a write the walk
    // placed there, so a write beside it the walk cannot place or cannot see keeps HEAD's reading (`cp Makefile /tmp/q/Makefile;
    // ls | xargs sed -i s/a/b/ Makefile`, `printf x > /tmp/q/Makefile; F=$(ls); sed -i s/a/b/ $F/Makefile`)
    let by_name = paths().any(|(p, _)| !named(p) && GUARD_NAMES.iter().any(|n| p.ends_with(n)));
    let c = replace_suites(&strip_quotes(&strip_heredocs(cmd)));
    let programs = targets
        .iter()
        .filter_map(|t| {
            t.program
                .as_deref()
                .filter(|b| !kept && interp::program_names_scratch(b, t.path.as_deref()))
        })
        .map(str::to_owned)
        .collect();
    (
        on_guard,
        by_name || (!kept && scratch_hits_placed(&c, &targets)),
        programs,
    )
}

/// Whether each hit of the text patterns in `c` (the command, its quotes and heredoc bodies blanked) is a write the walk placed in
/// scratch (451 T87): the hit's statement, its stretch of `c` between two separators, pairs with a segment of the walk whose writes
/// all landed on no guard file, one of them a guard file's name, and with no segment that is not so. A segment pairs with a statement
/// whose words, quotes dropped, it holds in order under the same head, so however the walk renders a quoted word (kept, `''`) they
/// pair; a hit the walk did not see (an `xargs`'s, a `find -exec`'s) or could not place (`$F/Makefile`) pairs with none freed.
fn scratch_hits_placed(c: &str, targets: &[Target]) -> bool {
    let mut segments: Vec<(&str, bool, bool)> = Vec::new();
    for t in targets.iter().filter(|t| t.how != "read") {
        let p = t.path.as_deref();
        let (free, name) = (p.is_some_and(|p| !held(p)), p.is_some_and(named));
        match segments.iter_mut().find(|s| s.0 == t.segment) {
            Some(s) => (s.1, s.2) = (s.1 && free, s.2 || name),
            None => segments.push((&t.segment, free, name)),
        }
    }
    let segments: Vec<(Vec<String>, bool)> = segments
        .into_iter()
        .map(|(s, free, name)| (pair_words(&replace_suites(s)), free && name))
        .collect();
    SHELL_WRITES
        .iter()
        .flat_map(|p| {
            p.find_iter(c)
                .map_while(Result::ok)
                .map(|m| (m.start(), m.end()))
        })
        .all(|(at, end)| {
            let (from, to) = statement(c, at);
            let said = pair_words(&c[from..to]);
            let pairs = |freed: bool| segments.iter().any(|(w, f)| *f == freed && holds(w, &said));
            end <= to + 1 && pairs(true) && !pairs(false)
        })
}

/// The stretch of `c` holding byte `at`, between two separators - `;`, a newline, `|`, `(`, `)`, a backquote, an `&` that is no
/// redirect's target (`2>&1`; an `&>` is a separator, as the walk reads it) - as byte offsets.
fn statement(c: &str, at: usize) -> (usize, usize) {
    let b = c.as_bytes();
    let sep = |i: usize| match b[i] {
        b';' | b'\n' | b'|' | b'(' | b')' | b'`' => true,
        b'&' => !(i > 0 && matches!(b[i - 1], b'>' | b'<')),
        _ => false,
    };
    let from = (0..at).rev().find(|&i| sep(i)).map_or(0, |i| i + 1);
    let to = (at..b.len()).find(|&i| sep(i)).unwrap_or(b.len());
    (from, to)
}

/// The shell's reserved words a statement may open with, which the walk's segment, starting at its command, does not hold.
const RESERVED: [&str; 10] = [
    "then", "do", "else", "elif", "if", "while", "until", "!", "{", "}",
];

/// A statement's or a segment's words for pairing the two: each `<` and `>` a word of its own, quotes dropped, a word that was only
/// quotes gone, a leading reserved word skipped, and a redirect to `/dev/null` or onto a descriptor (`2>&1`, `>&2`) gone with its
/// descriptor, as the walk's segment drops them.
fn pair_words(text: &str) -> Vec<String> {
    let spaced = text.replace('>', " > ").replace('<', " < ");
    let out: Vec<String> = spaced
        .split_whitespace()
        .map(|w| w.replace(['\'', '"'], ""))
        .filter(|w| !w.is_empty())
        .collect();
    let lead = out
        .iter()
        .take_while(|w| RESERVED.contains(&w.as_str()))
        .count();
    let mut kept: Vec<String> = Vec::new();
    let mut i = lead;
    while i < out.len() {
        let ops = out[i..]
            .iter()
            .take_while(|w| *w == ">" || *w == "<")
            .count();
        let dropped = out
            .get(i + ops)
            .is_some_and(|t| t == "/dev/null" || t.starts_with('&'));
        if ops > 0 && dropped {
            if kept
                .last()
                .is_some_and(|w| w.chars().all(|c| c.is_ascii_digit()))
            {
                kept.pop();
            }
            i += ops + 1;
        } else {
            kept.push(out[i].clone());
            i += 1;
        }
    }
    kept
}

/// Whether a segment's words hold a statement's, in order, under the same head.
fn holds(segment: &[String], said: &[String]) -> bool {
    let mut rest = segment.iter();
    segment.first() == said.first() && said.iter().all(|w| rest.any(|s| s == w))
}

/// The verdict: `ok`, the rule broken, or `make-dup-var:<name>`; `here` is where the command starts.
pub(crate) fn classify_at(cmd: &str, here: &str) -> String {
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
    if cmd.contains("l7r") && hit(&ENTRY_MODULE, &clean) {
        return "engine-entry-point".to_owned();
    }
    if cmd.contains("cargo") && hit(&CARGO, &clean) {
        return "bare-cargo".to_owned();
    }
    // 451 T33 (T34's found-and-left): a bare rustfmt, at a command position or run by `xargs` or `find -exec`; asking its version
    // or help formats nothing
    if cmd.contains("rustfmt") && hit(&RUSTFMT, &RUSTFMT_INFO.replace_all(&clean, " ")) {
        return "bare-rustfmt".to_owned();
    }
    // every replacement binary (FR-005): `l7r-rust` (T93), `l7r-browser` (T146), `l7r-embed` (T138) and `l7r-mode-a` (T168) too, which
    // `l7r-gate.sh rust`, `browser`, `embed` and `mode-a` run
    if (cmd.contains("l7r-") || cmd.contains("hamlet")) && hit(&BINARY, &clean) {
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
    if guard_write(cmd, here, 0) {
        return "guard-write".to_owned();
    }
    "ok".to_owned()
}

/// Whether the command writes a guard file from the shell: the walk's writes, the patterns over the text, and (451 T33) what it
/// writes through an interpreter - a shell's body judged as a command, another's by the files it names - and a `for` loop's
/// variable read once per word, `depth` deep.
fn guard_write(cmd: &str, here: &str, depth: usize) -> bool {
    if !GUARD_NAMES
        .iter()
        .chain(&SOURCE_NAMES)
        .any(|n| cmd.contains(n))
    {
        return false;
    }
    let (c, raw) = (
        replace_suites(&strip_quotes(&strip_heredocs(cmd))),
        replace_suites(&without_stored_text(cmd)),
    );
    let (on_guard, cleared, programs) = walked_write(cmd, here);
    let shell = on_guard || (!cleared && SHELL_WRITES.iter().any(|p| hit(p, &c)));
    // a program the walk placed in scratch (451 T87), held once in the text, is no Python write of a guard file: the patterns read the rest
    let raw = programs.iter().fold(raw, |text, body| {
        if text.matches(body.as_str()).count() == 1 {
            text.replacen(body.as_str(), &" ".repeat(body.len()), 1)
        } else {
            text
        }
    });
    let deeper = || {
        depth < interp::DEPTH
            && (interp::bodies(cmd).iter().any(|(shell, body)| {
                if *shell {
                    guard_write(body, here, depth + 1)
                } else {
                    interp::program_names_guard(body, Some(here), false)
                }
            }) || interp::loop_expansions(cmd)
                .iter()
                .any(|e| guard_write(e, here, depth + 1)))
    };
    shell || PY_WRITES.iter().any(|p| hit(p, &raw)) || write_via_name(&raw) || deeper()
}

/// `cmd` with heredoc bodies and quoted strings replaced by spaces of the same length, so a match in it sits at the same offset in the raw text.
fn masked(cmd: &str) -> String {
    let blank = |text: &str, spans: Vec<(usize, usize)>| {
        let mut bytes = text.as_bytes().to_vec();
        for (at, end) in spans {
            bytes[at..end].fill(b' ');
        }
        String::from_utf8_lossy(&bytes).into_owned()
    };
    let heredocs = MASK_HEREDOC
        .find_iter(cmd)
        .map_while(Result::ok)
        .map(|m| (m.start(), m.end()))
        .collect();
    let text = blank(cmd, heredocs);
    let quotes = mask_quotes(&text)
        .into_iter()
        .map(|(at, end)| (at, end + 1))
        .collect();
    blank(&text, quotes)
}

/// The quoted strings `masked` blanks, each its opening and its closing quote's byte: shape's `quoted_spans`, but a quote just after
/// `-c ` or `-c\t` opens none, the reading going on from the character after it - as the pattern it replaced, `MASK_QUOTE`
/// (`(?s)(?<!-c )(?<!-c\t)(["'])(?:\\.|(?!\1).)*\1`), found them. Read by the scan (451 T113): the pattern took a backslash with the
/// character after it or alone, so its backtracking search tried 2^n readings of the n backslashes after a quote nothing closes, and
/// the guard gave no answer in 10 s on forty (measured 2026-11-21, the T113 plan section). A pass of the text, and one more from each
/// quote a `-c` passes over; a test holds the two equal on every text of up to 5 pieces (`tests.rs`).
fn mask_quotes(text: &str) -> Vec<(usize, usize)> {
    let after_dash_c =
        |at: usize| at >= 3 && matches!(&text.as_bytes()[at - 3..at], b"-c " | b"-c\t");
    let (mut spans, mut from) = (Vec::new(), 0);
    'read: loop {
        for (at, end) in quoted_spans(&text[from..]) {
            let (at, end) = (from + at, from + end);
            if after_dash_c(at) {
                from = at + 1;
                continue 'read;
            }
            spans.push((at, end));
        }
        return spans;
    }
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
            .map_while(Result::ok)
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

fn block(reason: &str, instead: &str) -> String {
    format!("BLOCKED: {reason}\n\nRun this instead:  {instead}\n\nIf this fired on correct work, it is a bug in the hook: put GUARD_EDIT_OK and a reason in the command.")
}

fn rewrite(input: &Value, command: &str, context: String) -> Vec<Answer> {
    let mut updated = input.clone();
    updated["command"] = json!(command);
    vec![Answer::Rewrite(updated), Answer::Notice(context)]
}

/// What this guard needs from outside the call.
pub(crate) struct Ctx {
    pub(crate) tree: PathBuf,
    pub(crate) here: PathBuf,
}

pub(crate) fn judge(event: &Event, session: &Session, ctx: &Ctx) -> Vec<Answer> {
    let null = Value::Null;
    let input = event.input.get("tool_input").unwrap_or(&null);
    let cmd = field(input, "command");
    let given = field(&event.input, "cwd");
    let verdict = if given.is_empty() {
        classify_at(cmd, &ctx.here.to_string_lossy())
    } else {
        classify_at(cmd, given)
    };
    let shown: String = cmd.chars().take(200).collect();
    let fire =
        |what: &str, rule: &str| log::fire("make-only", what, &shown, rule, &event.input, session);
    let refuse = |rule: &str, reason: &str, instead: &str| {
        fire("blocked", rule);
        vec![Answer::Refuse(block(reason, instead))]
    };
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
        "bare-cargo" => refuse(&verdict, "cargo run outside make. The Rust phases are linted, formatted and tested through make, so the gate's lints and its shared target directory are the ones used.", "make static (clippy, rustfmt --check) | make format FILE=<path> or make format CRATE=<dir> (rustfmt, that file or crate alone) | make rust-test (cargo test)"),
        "bare-rustfmt" => refuse(&verdict, "rustfmt run outside make. A format goes through make so it reaches the files meant and no others: a bare rustfmt follows a file's `mod` children and rewrites them too, and `make format` with no argument rewrites every crate.", "make format FILE=<path> (that file alone, its edition read from its crate) | make format CRATE=<dir> (one crate) | make static (rustfmt --check)"),
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
        "inline-override" => refuse(&verdict, "an override supplied on the command line, which skips the prompt whose default answer is CANCEL. That prompt is the whole mechanism: it exists to be answered, not pre-empted.", "make <target>   without the override, and answer the prompt if it appears"),
        "guard-write" => refuse(&verdict, "a GUARD FILE written from a shell command. Layer 3 only sees the Edit and Write tools, so this route slips past it - the same ungated-sibling shape this feature exists to close.", "make guard-edit FILE=<the guard file> WHY=\"<reason>\", then the Edit tool; or the same command ending in a trailing comment:  <command>  # GUARD_EDIT_OK: <reason>  - a marker INSIDE the text written does not count, since a guard file's text already holds old ones (GUARD_EDIT_OK: the round arbiter's fix on hour:383@4). dev/work-budget.json takes neither: `make guard-edit` refuses it, and it is written by `make budget-change PHASE=<stage> TO=<ops> WORDS=\"<the GM's words>\"` (a first budget: `make budget-set`)"),
        _ => Vec::new(),
    }
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let here = std::env::current_dir().unwrap_or_default();
    let tree = std::env::var("L7R_GUARD_TREE").map_or_else(|_| here.clone(), PathBuf::from);
    judge(event, session, &Ctx { tree, here })
}

#[cfg(test)]
mod tests;
