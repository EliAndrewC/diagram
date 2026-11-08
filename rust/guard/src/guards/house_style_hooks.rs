//! `house-style-hooks` (ported from the shell of the same name and the decision of `lib/hm_house.py`, feature 449 T036): THE TWO HOUSE-STYLE RULES A REGEX CAN DECIDE. Hyphens only,
//! and American spellings, corrected rather than refused where the correction is exact (the GM 2026-08-30). The GM's own writing, the files that must quote the rule, and a quotation of
//! someone else's text are exempt. A Bash command carries text it WRITES and text it only NAMES, so it is read in ranges: corrected by default, left alone where a word is named, warned
//! on where the command is the spelling fix (the GM 2026-09-12). The word table is `house_style_words.tsv`, generated from `hm_house.py`, because this hook would correct a copy typed here.

use std::collections::HashSet;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::drop_search_segments;
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;
use crate::shared::tree::walk;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "house-style-hooks",
    events: &["PreToolUse"],
    matcher: "Bash|Edit|Write|NotebookEdit",
    decide,
};

const SEARCHERS: &str = "grep|egrep|fgrep|rg|ack|ag|ripgrep";
const DASHES: &str = "\u{2014}\u{2013}";
const EM: &str = "\u{2014}";
const EN: &str = "\u{2013}";

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{pattern}: {e}"))
}

fn found(pattern: &Regex, text: &str) -> bool {
    pattern.is_match(text).unwrap_or(false)
}

/// (the spelling corrected, the house form), in the table's order.
static PAIRS: LazyLock<Vec<(&'static str, &'static str)>> = LazyLock::new(|| {
    include_str!("house_style_words.tsv")
        .lines()
        .filter_map(|l| l.split_once('\t'))
        .collect()
});
/// Each pair's whole-word pattern, in the table's order.
static PAIR_PATTERNS: LazyLock<Vec<(Regex, &'static str, &'static str)>> = LazyLock::new(|| {
    PAIRS
        .iter()
        .map(|(b, a)| (re(&format!(r"(?i)\b{}\b", fancy_regex::escape(b))), *b, *a))
        .collect()
});
pub(crate) static WORDS: LazyLock<Regex> = LazyLock::new(|| {
    let list: Vec<String> = PAIRS
        .iter()
        .map(|(b, _)| fancy_regex::escape(b).into_owned())
        .collect();
    re(&format!(r"(?i)\b({})\b|[{DASHES}]", list.join("|")))
});
static LEAD: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"^(?:\s+|!|\(|\{|\$\(|`|(?:then|do|else|elif|if|while|until|time|sudo|command|env|nohup|git)\b|[A-Za-z_][A-Za-z0-9_]*=\S*|xargs(?:\s+-\S+)*\b)+",
    )
});
static HELD_SHAPES: LazyLock<Vec<Regex>> = LazyLock::new(|| {
    vec![
        re(&format!(r"\$\(\s*(?:git\s+)?(?:{SEARCHERS})\b[^)]*\)")),
        re(r"[\w\\.?*+-]+(?:\\?\|[\w\\.?*+-]+)+"),
        re(&format!(
            r"\[[^\]\n]*[{DASHES}][^\]\n]*\]|\$'[^'\n]*[{DASHES}][^'\n]*'"
        )),
        re(&format!(r#"(['"])[{DASHES}]\1"#)),
        re(
            r"[\w.~$-]*/[\w./~$-]+|[\w-]+\.(?:md|py|sh|html|json|jsonl|txt|toml|js|css|ya?ml|csv)\b",
        ),
        re(r#"(['"])[\w\\.?*+()\[\]{}|-]{1,40}\1"#),
        re(
            r#"(?s)re\.(?:compile|search|match|fullmatch|split|sub|subn|findall|finditer)\(\s*[rbuf]{0,2}(['"])(?:\\.|(?!\1).)*\1"#,
        ),
    ]
});
static HEREDOC_BODY: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?s)<<-?\s*(['"]?)(\w+)\1[^\n]*\n(.*?)\n[ \t]*\2\b"#));
static QUOTED_SPAN: LazyLock<Regex> = LazyLock::new(|| re(r#"(?s)(["'])(?:\\.|(?!\1).)*\1"#));
static SEPARATOR: LazyLock<Regex> = LazyLock::new(|| re(r"&&|\|\||;|\||\n"));
static SED_EXEC: LazyLock<Regex> = LazyLock::new(|| re(r"-exec\s+sed\b"));
static HEREDOC_TO: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r#"(?:\b(?:cat|tee)\s+(?:-a\s+)?(?:>>?\s*)?(?P<p1>/\S+)\s*<<-?\s*(?P<q1>['"]?)(?P<t1>\w+)\k<q1>|\bcat\s*<<-?\s*(?P<q2>['"]?)(?P<t2>\w+)\k<q2>\s*>>?\s*(?P<p2>/\S+))[^\n]*\n"#,
    )
});
static NAMED_PATH: LazyLock<Regex> = LazyLock::new(|| re(r"[\w./-]+\.(?:md|py|sh|toml|json)"));
static EXEMPT: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(^|/)(CLAUDE\.md|constitution\.md|l7r-style\.md|house_style_hooks\.rs|house_style_words\.tsv|house_style_cases\.rs|test-house-style-hooks\.sh|house_style_cases\.rs|check-house-style-delta\.py|test_house_style_delta\.py|test_guard_firing_log\.py|hm_house\.py)$",
    )
});
static SOURCE_BLOCK: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?si)<!--\s*SOURCE: GM NOTES.*?<!--\s*END SOURCE\s*-->"));
static PROSE_FILE: LazyLock<Regex> = LazyLock::new(|| re(r"\.(?:md|html|txt)(\s|$)"));
static GM_REQUEST: LazyLock<Regex> = LazyLock::new(|| re(r"specs/[^/\s]+/request\.md"));
const CODE_AND_QUOTE: &str = "(?s)```.*?```|`[^`]*`|\u{300c}[^\u{300d}]*\u{300d}|\u{300e}[^\u{300f}]*\u{300f}|\u{201c}[^\u{201d}]*\u{201d}|<q\\b[^>]*>.*?</q>|<blockquote\\b[^>]*>.*?</blockquote>";
static SPAN: LazyLock<Regex> = LazyLock::new(|| re(CODE_AND_QUOTE));
static PROSE_SPAN: LazyLock<Regex> =
    LazyLock::new(|| re(&format!("{CODE_AND_QUOTE}|\"[^\"\\n]*\"")));

/// `text` with each match of `pattern` replaced by what `with` says of it.
fn sub_all(pattern: &Regex, text: &str, with: &dyn Fn(&str) -> String) -> String {
    let (mut out, mut from) = (String::new(), 0);
    for m in pattern.find_iter(text).flatten() {
        out.push_str(&text[from..m.start()]);
        out.push_str(&with(m.as_str()));
        from = m.end();
    }
    out + &text[from..]
}

fn cased(src: &str, dst: &str) -> String {
    if src.chars().all(char::is_uppercase) {
        return dst.to_uppercase();
    }
    if src.chars().next().is_some_and(char::is_uppercase) {
        let mut chars = dst.chars();
        return chars
            .next()
            .map_or_else(String::new, |c| c.to_uppercase().chain(chars).collect());
    }
    dst.to_owned()
}

/// The mechanical corrections on text with no span held out: a dash to a hyphen, the table, case kept.
fn correct_plain(text: &str) -> (String, Vec<String>) {
    let (mut text, mut notes) = (text.to_owned(), Vec::new());
    for (dash, name) in [(EM, "em-dash"), (EN, "en-dash")] {
        if text.contains(dash) {
            text = sub_all(&re(&format!(r"\s*{dash}\s*")), &text, &|_| " - ".to_owned());
            notes.push(format!("{name} -> hyphen"));
        }
    }
    for (pattern, brit, amer) in PAIR_PATTERNS.iter() {
        if found(pattern, &text) {
            text = sub_all(pattern, &text, &|m| cased(m, amer));
            notes.push(format!("{brit} -> {amer}"));
        }
    }
    (text, notes)
}

/// The corrected text and what was corrected, the spans exactly as they are.
fn correct(text: &str, spans: &Regex) -> (String, Vec<String>) {
    let (mut out, mut notes, mut last) = (String::new(), Vec::new(), 0);
    for m in spans.find_iter(text).flatten() {
        let (piece, got) = correct_plain(&text[last..m.start()]);
        out += &piece;
        notes.extend(got);
        out += m.as_str();
        last = m.end();
    }
    let (piece, got) = correct_plain(&text[last..]);
    notes.extend(got);
    (out + &piece, notes)
}

/// `cmd` with heredoc bodies and the insides of quoted strings blanked, at the same length: a separator inside quotes is not a separator.
fn masked(cmd: &str) -> String {
    let mut bytes = cmd.as_bytes().to_vec();
    for m in HEREDOC_BODY.captures_iter(cmd).flatten() {
        if let Some(body) = m.get(3) {
            bytes[body.start()..body.end()].fill(b' ');
        }
    }
    let blanked = String::from_utf8_lossy(&bytes).into_owned();
    for m in QUOTED_SPAN.find_iter(&blanked).flatten() {
        bytes[m.start() + 1..m.end() - 1].fill(b' ');
    }
    String::from_utf8_lossy(&bytes).into_owned()
}

fn split_segments(cmd: &str) -> Vec<(usize, usize)> {
    let (mut out, mut start) = (Vec::new(), 0);
    for m in SEPARATOR.find_iter(&masked(cmd)).flatten() {
        out.push((start, m.start()));
        start = m.end();
    }
    out.push((start, cmd.len()));
    out
}

/// The program a segment runs, past whatever stands in front of it.
fn head(text: &str) -> &str {
    let lead = LEAD.find(text).ok().flatten().map_or(0, |m| m.end());
    let rest = if lead > 0 {
        &text[lead..]
    } else {
        text.trim_start()
    };
    rest.split_whitespace()
        .next()
        .unwrap_or("")
        .rsplit('/')
        .next()
        .unwrap_or("")
}

#[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
enum Kind {
    Mention,
    Warn,
}

type Held = (usize, usize, Kind);

fn outside(path: &str) -> bool {
    path.starts_with("/tmp/") || path.contains("/.claude/projects/")
}

/// The body of each heredoc whose file lands outside the project, held whole: a reply is a quotation (feature 405 T109).
fn outside_heredocs(cmd: &str) -> Vec<Held> {
    let mut out = Vec::new();
    for m in HEREDOC_TO.captures_iter(cmd).flatten() {
        let named = |a: &str, b: &str| m.name(a).or_else(|| m.name(b)).map_or("", |g| g.as_str());
        let (path, tag) = (named("p1", "p2"), named("t1", "t2"));
        if !outside(path) {
            continue;
        }
        let from = m.get(0).map_or(0, |g| g.end());
        let end = re(&format!(r"(?m)^\s*{}\s*$", fancy_regex::escape(tag)))
            .find_from_pos(cmd, from)
            .ok()
            .flatten();
        out.push((from, end.map_or(cmd.len(), |e| e.start()), Kind::Mention));
    }
    out
}

fn held_ranges(cmd: &str) -> Vec<Held> {
    let mut held = outside_heredocs(cmd);
    for (a, b) in split_segments(cmd) {
        let seg = &cmd[a..b];
        let program = head(seg);
        if program == "sed" || found(&SED_EXEC, seg) {
            held.push((a, b, Kind::Warn));
        } else if SEARCHERS.split('|').any(|s| s == program) {
            held.push((a, b, Kind::Mention));
        }
    }
    for pattern in HELD_SHAPES.iter() {
        held.extend(
            pattern
                .find_iter(cmd)
                .flatten()
                .map(|m| (m.start(), m.end(), Kind::Mention)),
        );
    }
    held
}

/// The held ranges as one sorted, non-overlapping list; a range the sed shape covers stays a warning.
fn merged(mut held: Vec<Held>) -> Vec<Held> {
    held.sort_unstable();
    let mut out: Vec<Held> = Vec::new();
    for (a, b, kind) in held {
        match out.last_mut() {
            Some(last) if a <= last.1 => {
                last.1 = last.1.max(b);
                last.2 = last.2.max(kind);
            }
            _ => out.push((a, b, kind)),
        }
    }
    out
}

fn unique(items: Vec<String>) -> Vec<String> {
    let mut seen = HashSet::new();
    items
        .into_iter()
        .filter(|i| seen.insert(i.clone()))
        .collect()
}

/// (the command to run, the corrections made, the words warned on and left as typed).
fn plan(cmd: &str, spans: &Regex) -> (String, Vec<String>, Vec<String>) {
    if !found(&WORDS, cmd) {
        return (cmd.to_owned(), Vec::new(), Vec::new());
    }
    // Both spellings in one command is a fix, however it is written (the GM's reason for the sed shape).
    let mut both: Vec<String> = PAIRS
        .iter()
        .filter(|(w, a)| {
            found(&re(&format!(r"(?i)\b{w}\b")), cmd) && found(&re(&format!(r"(?i)\b{a}\b")), cmd)
        })
        .map(|(w, _)| (*w).to_owned())
        .collect();
    if !both.is_empty() {
        both.sort_unstable();
        return (cmd.to_owned(), Vec::new(), both);
    }
    let mut held: Vec<Held> = spans
        .find_iter(cmd)
        .flatten()
        .map(|m| (m.start(), m.end(), Kind::Mention))
        .collect();
    held.extend(held_ranges(cmd));
    let mut ranges = merged(held);
    ranges.push((cmd.len(), cmd.len(), Kind::Mention));
    let (mut out, mut notes, mut warned, mut last) = (String::new(), Vec::new(), Vec::new(), 0);
    for (a, b, kind) in ranges {
        let piece = &cmd[last..a];
        if found(&WORDS, piece) {
            let (fixed, got) = correct_plain(piece);
            out += &fixed;
            notes.extend(got);
        } else {
            out += piece;
        }
        if kind == Kind::Warn {
            warned.extend(
                WORDS
                    .find_iter(&cmd[a..b])
                    .flatten()
                    .map(|m| m.as_str().to_lowercase()),
            );
        }
        out += &cmd[a..b];
        last = b;
    }
    (out, unique(notes), unique(warned))
}

/// What the guard says of a call.
#[derive(Debug, PartialEq)]
pub(crate) enum Report {
    Silent,
    Corrected(Value, String, &'static str),
    Warned(String),
    Refused(String),
}

fn first_six(items: &[String]) -> String {
    items.iter().take(6).cloned().collect::<Vec<_>>().join(", ")
}

/// Whether the call lands wholly outside the project: decided by where the write lands, the paths it merely mentions the fall-back.
fn lands_outside(cmd: &str, is_bash: bool, start: Option<&str>, path: &str) -> bool {
    let home = std::env::var("HOME").unwrap_or_default();
    let targets: Vec<Option<String>> = if is_bash {
        walk(cmd, start, &home, &home)
            .targets
            .into_iter()
            .map(|t| t.path)
            .collect()
    } else {
        Vec::new()
    };
    let judged = if targets.is_empty() {
        path.split_whitespace()
            .map(|p| Some(p.to_owned()))
            .collect()
    } else {
        targets
    };
    !judged.is_empty() && judged.iter().all(|p| p.as_deref().is_some_and(outside))
}

fn bash_report(input: &Value, cmd: &str, hits: &[String], gm: bool) -> Report {
    let (new_cmd, notes, warned) = if gm {
        (None, Vec::new(), hits.to_vec())
    } else {
        let (c, n, w) = plan(cmd, &SPAN);
        (Some(c), n, w)
    };
    if let Some(new) = new_cmd.filter(|c| !notes.is_empty() && c != cmd) {
        let mut payload = input.clone();
        payload["command"] = Value::String(new);
        let tail = if warned.is_empty() {
            String::new()
        } else {
            format!(" Left as typed and NOT corrected, because this command carries both spellings and is therefore a fix: {}.", first_six(&warned))
        };
        return Report::Corrected(payload, format!("House style was applied to this command for you ({}). A write that travels through a Bash payload owes CLAUDE.md exactly as an Edit does. What the command only NAMES was left as typed: a search pattern, a path, a code span and a quotation of someone elses text.{tail}", first_six(&notes)), "corrected-command");
    }
    if warned.is_empty() {
        return Report::Silent;
    }
    let why = if gm {
        "this file records the GM speaking, and their words are reported, never corrected (Principle V)"
    } else {
        "this command carries BOTH spellings of a word (or is the sed shape), which is how a replacement pair looks - correcting it could replace a word with itself and make the fix silently do nothing. If it is not a fix, the word is yours to correct"
    };
    Report::Warned(format!("House style, in this command payload: {}. Not corrected for you: {why}. `make quick` fails on a British spelling in the delta, so it is cheaper to fix now than at the gate.", first_six(&warned)))
}

fn word_hits(visible: &str) -> Vec<String> {
    let mut hits = Vec::new();
    if visible.contains(EM) {
        hits.push("em-dash (U+2014)".to_owned());
    }
    if visible.contains(EN) {
        hits.push("en-dash (U+2013)".to_owned());
    }
    hits.extend(
        PAIR_PATTERNS
            .iter()
            .filter(|(p, _, _)| found(p, visible))
            .map(|(_, b, _)| (*b).to_owned()),
    );
    hits
}

/// Whether lower-cased input text holds a word of the table or a forbidden dash at all.
fn can_hit(text: &str) -> bool {
    text.contains(['\u{2014}', '\u{2013}'])
        || PAIRS.iter().any(|(british, _)| text.contains(british))
}

pub(crate) fn report(event: &Event) -> Report {
    let null = Value::Null;
    let input = event.input.get("tool_input").unwrap_or(&null);
    // no listed word and no dash anywhere in the input, and no span, path or rewrite is worth computing (T052: compiling them was 2.5 ms of a plain Bash call)
    if !can_hit(&input.to_string().to_lowercase()) {
        return Report::Silent;
    }
    let is_bash = event.tool() == "Bash";
    let cmd = field(input, "command");
    let names: Vec<String> = NAMED_PATH
        .find_iter(cmd)
        .flatten()
        .map(|m| m.as_str().to_owned())
        .collect();
    let path = Some(field(input, "file_path").to_owned())
        .filter(|p| !p.is_empty())
        .unwrap_or(if is_bash {
            names.join(" ")
        } else {
            String::new()
        });
    let body = if is_bash {
        drop_search_segments(cmd)
    } else {
        format!("{}{}", field(input, "new_string"), field(input, "content"))
    };
    if body.is_empty()
        || path.contains("/host-l7r-repo")
        || path.ends_with("l7r.md")
        || path.contains("gm-request.md")
    {
        return Report::Silent;
    }
    let start = Some(field(&event.input, "cwd")).filter(|c| !c.is_empty());
    if lands_outside(cmd, is_bash, start, &path)
        || format!("/{path}").contains("/tests/hooks/fixtures/")
        || found(&EXEMPT, &path)
    {
        return Report::Silent;
    }
    let body = sub_all(&SOURCE_BLOCK, &body, &|_| " ".to_owned());
    let prose = !is_bash && found(&PROSE_FILE, &path);
    let spans: &Regex = if prose { &PROSE_SPAN } else { &SPAN };
    let hits = word_hits(&sub_all(spans, &body, &|_| " ".to_owned()));
    if hits.is_empty() {
        return Report::Silent;
    }
    let gm = found(&GM_REQUEST, &path) || path.contains("gm-request.md");
    if is_bash {
        return bash_report(input, cmd, &hits, gm);
    }
    let (mut payload, mut notes, mut written) = (input.clone(), Vec::new(), String::new());
    for key in ["new_string", "content"] {
        if let Some(text) = input.get(key).and_then(Value::as_str) {
            let (got, more) = correct(text, spans);
            written += &got;
            payload[key] = Value::String(got);
            notes.extend(more);
        }
    }
    let still_bad = !word_hits(&sub_all(spans, &written, &|_| " ".to_owned())).is_empty();
    if !notes.is_empty() && !still_bad && !gm {
        return Report::Corrected(payload, format!("House style was applied to this edit for you ({}). Both rules are exact substitutions from CLAUDE.md, so the correction is made rather than the edit refused - a refusal costs a model round trip to say the same thing. Text inside backticks was left alone: a word in a code span is being named, not used. Text inside quotation marks was left alone too: a quotation is someone else text (GM 2026-09-06).", first_six(&notes)), "corrected-edit");
    }
    let shown: Vec<&str> = hits.iter().take(6).map(String::as_str).collect();
    Report::Refused(format!(
        "{}{}",
        shown.join(" | "),
        gm.then_some(" [the GM own words - not corrected, only reported]")
            .unwrap_or_default()
    ))
}

fn refusal(report: &str) -> String {
    let forbidden = concat!("deme", "sne");
    format!(
        "BLOCKED: house style ({report}).

CLAUDE.md, project-wide and for everything - generated content, prose, docs, specs, tests, comments
and code identifiers alike:

  - HYPHENS ONLY. No em-dash (U+2014), no en-dash (U+2013). Use \" - \".
  - AMERICAN SPELLINGS. color, center, gray, honor, judgment, catalog, labeled, behavior, neighbor,
    analyze/organize/recognize, artifact, defense, license, practice, skeptic, story, while,
    traveled, modeled, program, meter, liter, mold, plow, curb, draft, aging, marvelous, jewelry,
    skillful. And \"domain\", never \"{forbidden}\".

NOT flagged, deliberately: the GM's own writing (a SOURCE block, l7r.md, or a direct quotation of
either), and the files that must quote the rule to state it.

If this fired on a legitimate quotation of the GM, that is a bug in this hook worth fixing rather
than working around.

(rust/guard/src/guards/house_style_hooks.rs; CLAUDE.md \"House style\")"
    )
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let input = event.input.get("tool_input");
    let text = input.map_or("", |t| {
        Some(field(t, "command"))
            .filter(|c| !c.is_empty())
            .unwrap_or(field(t, "file_path"))
    });
    let shown: String = text.chars().take(200).collect();
    match report(event) {
        Report::Silent => Vec::new(),
        Report::Corrected(payload, note, rule) => {
            log::fire(
                "house-style",
                "rewrote",
                &shown,
                rule,
                &event.input,
                session,
            );
            vec![Answer::Rewrite(payload), Answer::Notice(note)]
        }
        Report::Warned(note) => {
            log::fire(
                "house-style",
                "warned",
                &shown,
                "bash-payload",
                &event.input,
                session,
            );
            vec![Answer::Notice(note)]
        }
        Report::Refused(what) => {
            log::fire("house-style", "blocked", &shown, "", &event.input, session);
            vec![Answer::Refuse(refusal(&what))]
        }
    }
}

/// Whether `file` is a name the rule's own text must quote in (a seam for the tests).
#[cfg(test)]
fn exempt(file: &str) -> bool {
    found(&EXEMPT, file)
}

#[cfg(test)]
mod tests;
