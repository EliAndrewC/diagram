//! What `make decide` refuses before a plan section reaches its review (feature 385 T84 and T86; feature 449 T066, from `plan_lint.py`).
//! The evening of 2026-10-18 sent 42 plan reviews, and four came back unreviewable for what a script can see first.

use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};

use super::sections::re;

mod deferral;
use crate::checks::{figure_pattern, one_shot_pattern};

// The red exit the hint quotes: the template's own (feature 449 T135, one text where this held a copy).
use super::template::RED_EXIT as RED_EXIT_HINT;

static GM: LazyLock<Regex> = LazyLock::new(|| re(r"(?i)\bthe GM(?:'s)?\b"));
static WORD: LazyLock<Regex> = LazyLock::new(|| re(r"[a-z0-9]+"));
static CODE_SPAN: LazyLock<Regex> = LazyLock::new(|| re(r"`[^`\n]*`"));
static ITEM4: LazyLock<Regex> = LazyLock::new(|| re(r"(?ms)^4\. \*\*.*?(?=^\d+\. \*\*|^#|\z)"));
static SPAN: LazyLock<Regex> = LazyLock::new(|| re(r"`([^`\n]*)`"));
static NOT_A_FIGURE: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"\b\d{4}-\d\d-\d\d(?:T\d\d:\d\d(?::\d\d)?Z?)?\b|\b\d\d:\d\d(?::\d\d)?Z?\b|\b(?:FR|SC)-\d+[a-z]?\b|\b[TDA]\d+[a-z]?\b|\b0\d{3}\b",
    )
});
static NAMED: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?i)\b(?:round|rounds|seed|seeds|hour|amendment|item|items|change|wave|batch|step|task|feature|proposal|part|tier|version|line|group)\s+\d+(?:\s*(?:-|and|to)\s*\d+)?\b",
    )
});
/// A sentence's label: a measurement's word, date and method anywhere in it, or an `m:` key - three plain searches, not one pattern. WHY:
/// the one pattern held three greedy lookaheads anchored at the start, which ran out of `fancy_regex`'s fixed backtracking stack on a
/// sentence near a megabyte and so answered "no label" in error (T185's plan review, 2026-11-18: 449's own 1.1 MB of plan as one
/// sentence, `t185/after-concat449.jsonl`); each search here is linear and keeps no stack.
static MEASURED_WORD: LazyLock<Regex> = LazyLock::new(|| re(r"(?i)\bmeasured\b"));
static ISO_DATE: LazyLock<Regex> = LazyLock::new(|| re(r"\b20\d\d-\d\d-\d\d\b"));
static M_KEY: LazyLock<Regex> = LazyLock::new(|| re(r"\bm:[\w.-]+"));

/// Whether a sentence carries a measurement's label (see [`MEASURED_WORD`]); a search that errs counts as no label.
fn has_label(sentence: &str) -> bool {
    let hit = |p: &Regex| p.is_match(sentence).unwrap_or(false);
    (hit(&MEASURED_WORD) && hit(&ISO_DATE) && sentence.contains('(')) || hit(&M_KEY)
}
static COMMAND_SPAN: LazyLock<Regex> = LazyLock::new(|| re(r"/|::|=|\bmake "));
static SPLIT4: LazyLock<Regex> = LazyLock::new(|| re(r"(?<=\.)\s+|\n(?=\S)"));
static LEAD4: LazyLock<Regex> = LazyLock::new(|| re(r"^\s*4\."));
static BARE_FIGURE: LazyLock<Regex> = LazyLock::new(|| re(r"(?<![\w-])\d[\d,.]*(?![\w-])"));
static FENCE: LazyLock<Regex> = LazyLock::new(|| re(r"(?ms)^```.*?^```"));
static SPLIT_UNIT: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?<=[.;])\s+|\n\s*\n|\n(?=\s*(?:[-*] |\d+\. |#|\|))"));
/// A decided figure's labels (root CLAUDE.md, "every rendering decision is labeled"), and a source's verdict in a research-record plan.
static DECISION_LABEL: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"\b(?:GUESS|CONVENTION|DEVIATION|UNRESEARCHED|ACCURATE|HISTORICALLY ACCURATE|ATTESTED|SILENT)\b|this project's arithmetic|research/questions/|\bknob\b|\bR\d+\b",
    )
});
/// A rule stated as a figure, which measures nothing: the coverage floor.
static RULE: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?i)\b100\s*%\s+(?:code\s+|line\s+)?coverage\b"));
static APPROACH_HEAD: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^### (T\d+[a-z]?) Approach\b.*$"));
static HEADING_LINE: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^#.*$"));
static APPROACH_BLOCK: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?i)^#{2,4}\s+T\d+[a-z]?\s+(?:Approach|part B)\b"));
static NEXT_23: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^#{2,3} "));
static ITEM6: LazyLock<Regex> = LazyLock::new(|| re(r"(?ms)^6\.\s.*?(?=^\d+\.\s|\z)"));
static OPEN_TASK: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^- \[ \] (T\d+[a-z]?)\b"));

fn folded(text: &str) -> String {
    let lower = text.to_lowercase();
    let words: Vec<&str> = WORD
        .find_iter(&lower)
        .map_while(Result::ok)
        .map(|m| m.as_str())
        .collect();
    format!(" {} ", words.join(" "))
}

fn split_on<'t>(pattern: &Regex, text: &'t str) -> Vec<&'t str> {
    let mut out = Vec::new();
    let mut at = 0;
    for gap in pattern.find_iter(text).map_while(Result::ok) {
        out.push(&text[at..gap.start()]);
        at = gap.end();
    }
    out.push(&text[at..]);
    out
}

/// Where `part`, a slice of `whole`, starts in it, and where it ends with its surrounding whitespace trimmed.
fn trimmed_span(whole: &str, part: &str) -> (usize, usize) {
    let at = part.as_ptr() as usize - whole.as_ptr() as usize;
    let lead = part.len() - part.trim_start().len();
    (at + lead, at + part.trim_end().len().max(lead))
}

/// A text a pattern rewrote, with the way back to the original's offsets: each check reads the rewritten text exactly as it always
/// did, and a finding's place is mapped back on the side (feature 451 T25: every finding named by its line).
struct Rewritten {
    text: String,
    /// (the end of a replacement in the new text, the end of what it replaced in the original), in order.
    marks: Vec<(usize, usize)>,
}

impl Rewritten {
    fn new(pattern: &Regex, text: &str, with: impl Fn(&Captures<'_>) -> String) -> Self {
        let (mut out, mut marks, mut last) = (String::new(), Vec::new(), 0);
        for c in pattern.captures_iter(text).map_while(Result::ok) {
            let whole = c.get(0).map_or((last, last), |g| (g.start(), g.end()));
            out.push_str(&text[last..whole.0]);
            out.push_str(&with(&c));
            marks.push((out.len(), whole.1));
            last = whole.1;
        }
        out.push_str(&text[last..]);
        Self { text: out, marks }
    }

    /// The original offset of `at`, an offset of the rewritten text outside a replacement.
    fn original(&self, at: usize) -> usize {
        self.marks
            .iter()
            .rev()
            .find(|(new, _)| *new <= at)
            .map_or(at, |(new, old)| at - new + old)
    }

    /// `part`'s span (see [`trimmed_span`]) in the original.
    fn span(&self, part: &str) -> (usize, usize) {
        let (a, b) = trimmed_span(&self.text, part);
        (self.original(a), self.original(b))
    }
}

/// What a lint rule found: its kind, its span in the section, and the words shown.
#[derive(Debug, Clone, PartialEq, Eq)]
pub(super) struct Finding {
    kind: Kind,
    pub(super) start: usize,
    end: usize,
    text: String,
}

/// The lint's rules, in the order they are reported.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Kind {
    GmQuote,
    Item4,
    UnitFigure,
    Differential,
    Count,
    RedExit,
    /// A found-and-left deferral without its form (feature 451 T17, D15).
    Deferral,
    /// A deferral to a task not open when `make decide` judges it (D15: the decision's half alone).
    DeferralClosed,
    /// A fix of a class of defect with no labeled line on how every instance was found (D15).
    ClassFix,
}

impl Finding {
    /// Whether `DEFER_FORM_OK` reaches this finding: the deferral's form and the class fix's line (D15).
    pub(super) fn deferral(&self) -> bool {
        matches!(
            self.kind,
            Kind::Deferral | Kind::DeferralClosed | Kind::ClassFix
        )
    }
}

/// One sentence's words as a finding shows them: its whitespace collapsed, at most 160 characters.
fn shown(sentence: &str) -> String {
    sentence
        .split_whitespace()
        .collect::<Vec<_>>()
        .join(" ")
        .chars()
        .take(160)
        .collect()
}

/// Each double-quoted span that follows "the GM" within the same sentence, with its offset; a code span names words, it quotes no one.
/// The sentence ends at `.`, `!` or `?` before a space or a line's end, or at a blank line - so a bullet list with no blank line and
/// no full stop is one sentence, and a quote in a later bullet is read as the GM's (the unit the refusal states, feature 451 T25).
fn gm_quotes(section: &str) -> Vec<(usize, String)> {
    let masked = CODE_SPAN
        .replace_all(section, |c: &Captures<'_>| " ".repeat(c[0].len()))
        .into_owned();
    let bytes = masked.as_bytes();
    let mut out: Vec<(usize, String)> = Vec::new();
    for m in GM.find_iter(&masked).map_while(Result::ok) {
        let line_start = masked[..m.start()].rfind('\n').map_or(0, |p| p + 1);
        if masked[line_start..m.start()].matches('"').count() % 2 == 1 {
            continue;
        }
        let (mut i, mut quoting, mut start) = (m.end(), false, 0);
        while i < bytes.len() {
            let next = bytes.get(i + 1).copied();
            let ch = bytes[i];
            if ch == b'"' {
                if quoting && !out.iter().any(|(_, q)| q == &section[start..i]) {
                    out.push((start, section[start..i].to_owned()));
                }
                start = i + 1;
                quoting = !quoting;
            } else if !quoting
                && ((ch == b'\n' && matches!(next, Some(b'\n') | None))
                    || (matches!(ch, b'.' | b'!' | b'?')
                        && matches!(next, Some(b' ' | b'\n') | None)))
            {
                break;
            }
            i += 1;
        }
    }
    out
}

/// The GM quotes whose words, folded, are not a run in the request folded the same way (D105) - every length, no escape.
fn gm_quotes_missing(section: &str, request: &str) -> Vec<(usize, String)> {
    let req = folded(request);
    gm_quotes(section)
        .into_iter()
        .filter(|(_, q)| {
            let pieces = q.split("...").flat_map(|p| p.split('\u{2026}'));
            !folded(q).trim().is_empty()
                && !pieces
                    .filter(|p| !folded(p).trim().is_empty())
                    .all(|p| req.contains(&folded(p)))
        })
        .collect()
}

/// Every figure an Approach item 4 states whose own sentence carries no label (feature 385 T86): (its span, its sentence). Every item 4
/// of the section is read: a section holding a re-answered Approach block has two, and reading only the first let the second's
/// unlabeled figure reach its plan review unrefused (feature 451 T25).
/// An item 4 is an Approach block's (part A or B) or stands under no heading; a performance checklist's item 4, whose block says it
/// prompts and never gates, is not read (feature 451 T25: 444's T26 and T27 would have been refused on theirs).
fn unlabeled_figure(section: &str) -> Vec<((usize, usize), String)> {
    ITEM4
        .find_iter(section)
        .map_while(Result::ok)
        .filter(|item| {
            HEADING_LINE
                .find_iter(&section[..item.start()])
                .map_while(Result::ok)
                .last()
                .is_none_or(|h| APPROACH_BLOCK.is_match(h.as_str()).unwrap_or(false))
        })
        .flat_map(|item| unlabeled_in_item(item.start(), item.as_str()))
        .collect()
}

/// One item 4's figures with no label in their sentence, placed in the section by the item's offset `at`.
fn unlabeled_in_item(at: usize, item: &str) -> Vec<((usize, usize), String)> {
    let spaced = Rewritten::new(&SPAN, item, |c: &Captures<'_>| {
        if COMMAND_SPAN.is_match(&c[1]).unwrap_or(false) {
            " ".to_owned()
        } else {
            c[1].to_owned()
        }
    });
    let mut out = Vec::new();
    for sentence in split_on(&SPLIT4, &spaced.text) {
        let lead = LEAD4.replace(sentence, " ");
        let bare = NOT_A_FIGURE.replace_all(&lead, " ");
        let bare = NAMED.replace_all(&bare, " ");
        if BARE_FIGURE.is_match(&bare).unwrap_or(false) && !has_label(sentence) {
            let (a, b) = spaced.span(sentence);
            out.push((
                (at + a, at + b),
                sentence.trim().chars().take(160).collect(),
            ));
        }
    }
    out
}

/// Every sentence anywhere in the section stating a figure with a unit and carrying no label (feature 430 T05, D5).
fn unlabeled_unit_figure(section: &str) -> Vec<((usize, usize), String)> {
    let text = Rewritten::new(&FENCE, section, |_| " ".to_owned());
    let mut out = Vec::new();
    for sentence in split_on(&SPLIT_UNIT, &text.text) {
        let bare = SPAN.replace_all(sentence, " ");
        let bare = NOT_A_FIGURE.replace_all(&bare, " ");
        let bare = RULE.replace_all(&bare, " ");
        let labeled = has_label(sentence)
            || [one_shot_pattern(), &*DECISION_LABEL]
                .iter()
                .any(|p| p.is_match(sentence).unwrap_or(false));
        if figure_pattern().is_match(&bare).unwrap_or(false) && !labeled {
            out.push((text.span(sentence), shown(sentence)));
        }
    }
    out
}

// A COUNT is a figure too (feature 449 T159, the GM 2026-11-16): "(183, 98 and 57 lines)", "1,261 cases" - the plan review sent T145
// back unreviewable on that one parenthesis, a round of about 15 minutes a script could have spent in a second. The nouns are what this
// project's plans count by measuring; the plan's own parts ("14 decisions", "two tasks", "11 recipes") name, not measure, and stay out.
static COUNT: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?<![\w.-])\d[\d,]*(?:\.\d+)?\s*(?:lines?|cases?|files?|pages?|calls?|callers?|crates?|suites?|tests?|rows?|keys?|entries|entry|findings?|differences?|mismatches?|runs?|sites?|commits?|bytes?|KB|KiB|tokens?|questions?|sources?|modules?|functions?|mutations?|outputs?|hits?|fragments?|footnotes?|URLs?|domains?|processes|process|invocations?)(?![\w-])",
    )
});
// A count is split into sentences only, where a unit figure is split at ";" too: over the sixteen reviewed sections of 449 (T121-T145),
// the ";" split flagged 8 counts their reviews had passed, the sentence split 3, each a count no label reached (feature 449 T159).
static SPLIT_SENTENCE: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?<=\.)\s+|\n\s*\n|\n(?=\s*(?:[-*] |\d+\. |#|\|))"));
// A rule's threshold ("no file over 1,000 lines") states a limit, not a measurement.
static THRESHOLD: LazyLock<Regex> = LazyLock::new(|| {
    re(r"(?i)\b(?:over|under|at most|at least|past|beyond|exceeds?|up to)\s+\d[\d,]*\s+[a-z]+")
});

/// Every sentence stating a count with no label (feature 449 T159).
fn unlabeled_count(section: &str) -> Vec<((usize, usize), String)> {
    let text = Rewritten::new(&FENCE, section, |_| " ".to_owned());
    let mut out = Vec::new();
    // split outside code spans: a method span such as `wc -l a. b` held the sentence's end and cut the count from its label (T161)
    for sentence in sentences_outside_spans(&SPLIT_SENTENCE, &text.text) {
        let bare = SPAN.replace_all(sentence, " ");
        let bare = NOT_A_FIGURE.replace_all(&bare, " ");
        let bare = THRESHOLD.replace_all(&bare, " ");
        let labeled = has_label(sentence)
            || [one_shot_pattern(), &*DECISION_LABEL]
                .iter()
                .any(|p| p.is_match(sentence).unwrap_or(false));
        if COUNT.is_match(&bare).unwrap_or(false) && !labeled {
            out.push((text.span(sentence), shown(sentence)));
        }
    }
    out
}

// A DIFFERENTIAL'S CASE COUNT CITES THE RUNNER'S VERIFY REPORT (feature 449 T161, the plan's enforcement of the GM's 2026-11-16 approval and his 2026-11-11 words):
// the runner reruns only the sides whose key moved, and a declaration of what a case exercises can be too narrow, so the count a plan
// reports is the one `make diff-run ... VERIFY=1` wrote - every case's new side rerun against the kept old sides, its report's path
// carrying `diff-run-verify`. An incremental report's path does not, nor does a hand-written loop's results file, so a port whose
// comparison ran outside the runner cannot reach its review with that figure. The citation is looked for in the raw sentence, since
// the path stands in a code span; the count with its code spans read as words and up to three words before its noun ("1,261 `cmd` and `sources` cases").
static CASE_COUNT: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?i)(?<![\w.-])\d[\d,]*\s+(?:\S+\s+){0,3}?cases?\b"));
static DIFFERENTIAL: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?i)\bdifferentials?\b|\bsame\s+outputs\b"));
static VERIFY_REPORT: LazyLock<Regex> = LazyLock::new(|| re(r"(?i)diff-run-verify[^\s`)]*\.json"));

/// `text`'s sentences, split where `pattern` matches outside a code span: the cited command `make diff-run ... VERIFY=1` holds a period
/// and a space inside its span, which the plain split took for a sentence's end, leaving the count without its citation (feature 449
/// T161, found on the refusal's own example).
fn sentences_outside_spans<'t>(pattern: &Regex, text: &'t str) -> Vec<&'t str> {
    let masked = CODE_SPAN
        .replace_all(text, |c: &Captures<'_>| "x".repeat(c[0].len()))
        .into_owned();
    let mut out = Vec::new();
    let mut at = 0;
    for gap in pattern.find_iter(&masked).map_while(Result::ok) {
        out.push(&text[at..gap.start()]);
        at = gap.end();
    }
    out.push(&text[at..]);
    out
}

/// Every sentence stating a differential's case count that cites no runner verify report (feature 449 T161).
fn uncited_differential(section: &str) -> Vec<((usize, usize), String)> {
    let text = Rewritten::new(&FENCE, section, |_| " ".to_owned());
    let mut out = Vec::new();
    for sentence in sentences_outside_spans(&SPLIT_SENTENCE, &text.text) {
        let words = SPAN.replace_all(sentence, "$1");
        let words = NOT_A_FIGURE.replace_all(&words, " ");
        if CASE_COUNT.is_match(&words).unwrap_or(false)
            && DIFFERENTIAL.is_match(sentence).unwrap_or(false)
            && !VERIFY_REPORT.is_match(sentence).unwrap_or(false)
        {
            out.push((text.span(sentence), shown(sentence)));
        }
    }
    out
}

/// The first task whose approach block's item 6 routes no red result through `make arbiter-ask` (D35's wording), or "".
#[cfg(test)]
fn missing_red_exit(section: &str) -> String {
    missing_red_exits(section)
        .into_iter()
        .next()
        .map_or_else(String::new, |(_, t)| t)
}

/// Every task whose approach block's item 6 routes no red result through `make arbiter-ask`, with its block heading's offset.
fn missing_red_exits(section: &str) -> Vec<(usize, String)> {
    let mut out = Vec::new();
    for c in APPROACH_HEAD.captures_iter(section).map_while(Result::ok) {
        let rest = &section[c.get(0).map_or(0, |g| g.end())..];
        let block = NEXT_23
            .find(rest)
            .ok()
            .flatten()
            .map_or(rest, |n| &rest[..n.start()]);
        let routed = ITEM6.find(block).ok().flatten().is_some_and(|m| {
            m.as_str().contains("make arbiter-ask") || m.as_str().contains("make budget-change")
        });
        if !routed {
            out.push((c.get(0).map_or(0, |g| g.start()), c[1].to_owned()));
        }
    }
    out
}

/// In a plan whose tasks owe approach blocks, each open task with no `### Txx Approach` block in the plan or plan-done.md (D5).
fn tasks_without_approach(spec_dir: &Path, plan: &str) -> Vec<String> {
    let done = std::fs::read_to_string(spec_dir.join("plan-done.md")).unwrap_or_default();
    let joined = format!("{plan}\n{done}");
    let any = APPROACH_HEAD
        .is_match(&format!("{plan}{done}"))
        .unwrap_or(false);
    if !plan.contains("**Approach checklist**:") && !any {
        return Vec::new();
    }
    let tasks = std::fs::read_to_string(spec_dir.join("tasks.md")).unwrap_or_default();
    let have: Vec<String> = APPROACH_HEAD
        .captures_iter(&joined)
        .map_while(Result::ok)
        .map(|c| c[1].to_owned())
        .collect();
    OPEN_TASK
        .captures_iter(&tasks)
        .map_while(Result::ok)
        .map(|c| c[1].to_owned())
        .filter(|t| !have.contains(t))
        .collect()
}

/// Every finding of the section, in the order the rules are reported (feature 451 T25: each rule runs to the section's end, where it
/// stopped at its first finding, and a section of four findings took four runs). A label rule's finding is dropped only where an
/// earlier label rule found the very same span, since the one label clears both; a span inside a longer one stays, its own label owed.
pub(super) fn findings(spec_dir: &Path, section: &str) -> Vec<Finding> {
    let req = std::fs::read_to_string(spec_dir.join("request.md")).unwrap_or_default();
    let mut out: Vec<Finding> = gm_quotes_missing(section, &req)
        .into_iter()
        .map(|(at, q)| Finding {
            kind: Kind::GmQuote,
            start: at,
            end: at + q.len(),
            text: format!("\"{}\"", q.trim().chars().take(160).collect::<String>()),
        })
        .collect();
    let labeled = [
        (Kind::Item4, unlabeled_figure(section)),
        (Kind::UnitFigure, unlabeled_unit_figure(section)),
        (Kind::Differential, uncited_differential(section)),
        (Kind::Count, unlabeled_count(section)),
    ];
    for (kind, found) in labeled {
        for ((start, end), text) in found {
            let label_kinds = [Kind::Item4, Kind::UnitFigure, Kind::Count];
            let cleared = label_kinds.contains(&kind)
                && out
                    .iter()
                    .any(|f| label_kinds.contains(&f.kind) && (f.start, f.end) == (start, end));
            if !cleared {
                out.push(Finding {
                    kind,
                    start,
                    end,
                    text,
                });
            }
        }
    }
    let boxes = deferral::boxes(spec_dir);
    for (kind, found) in [
        (Kind::Deferral, deferral::unformed(section, &boxes)),
        (Kind::ClassFix, deferral::class_unlabeled(section)),
    ] {
        out.extend(found.into_iter().map(|((start, end), text)| Finding {
            kind,
            start,
            end,
            text,
        }));
    }
    out.extend(
        missing_red_exits(section)
            .into_iter()
            .map(|(at, task)| Finding {
                kind: Kind::RedExit,
                start: at,
                end: at,
                text: task,
            }),
    );
    out
}

/// What a rule's refusal says once, above its findings: what is wrong, the fix, and the unit the rule reads with where its label
/// must sit (feature 451 T25: a rule whose unit surprises its author says so in its refusal, not in a doc).
fn told(kind: Kind) -> String {
    match kind {
        Kind::GmQuote => "the section quotes the GM with words request.md does not hold - add the GM's words to request.md verbatim, or correct the quote (feature 385 T84). The unit: a double-quoted span is read as the GM's when it follows \"the GM\" before that sentence ends - `.`, `!` or `?` then a space or a line break - or the paragraph does, at a blank line; a bullet list with no blank line between its items is one paragraph, so a bullet naming the GM with no full stop runs on into the next bullets' quotes: end that bullet with a full stop where the quote is not his".to_owned(),
        Kind::Item4 => "Approach item 4 states a figure whose sentence carries no `measured <YYYY-MM-DD> (<method>)` or `m:<key>` - label it where it stands (feature 385 T86). The unit: item 4 of every Approach block (part A or B) in the section, each from its `4. **` line to the next numbered bold item or heading, cut into sentences after each `.` and whitespace (a space or a line break) and at each line that starts in column one (an unindented wrapped line starts a new sentence); the label sits in the figure's own sentence, and only those two forms count here - `observed <YYYY-MM-DD>, method: ...` and a research label, which pass elsewhere in the section, do not pass in item 4".to_owned(),
        Kind::UnitFigure => "a figure with a unit whose sentence carries no label - a measurement `measured <YYYY-MM-DD> (<method>)`, `observed <YYYY-MM-DD>, method: ...` or `m:<key>`; a decided size its research label (GUESS, CONVENTION, ...), its page or its knob - label it where it stands (feature 430 D5). The unit: the clause - a sentence is cut after each `.` or `;` and whitespace (a space or a line break), even inside a code span, at a blank line, and where a bullet, a numbered item, a heading or a table row starts (a fenced block is skipped), so a label at a sentence's end does not cover a figure in a clause before its `;`: label each clause, or join them with a comma".to_owned(),
        Kind::Differential => "a differential's case count that cites no verify report - run `make diff-run CASES=<cases file> VERIFY=1` (every case's new side rerun against the kept old sides) and cite the report it writes, `<cases>.diff-run/reports/diff-run-verify-<UTC>.json`, in the sentence beside its label, as in \"16 cases, 0 differing (measured 2026-11-16 (`make diff-run ... VERIFY=1`, `t161/cases.diff-run/reports/diff-run-verify-20261116T120000Z.json`))\"; a hand-written loop's or an incremental run's count does not stand (feature 449 T161). The unit: the sentence, cut after a `.` and whitespace (a space or a line break) outside a code span, at a blank line, and where a bullet, a numbered item, a heading or a table row starts".to_owned(),
        Kind::Count => "a count whose sentence carries no label - `observed <YYYY-MM-DD>, method: ...`, `measured <YYYY-MM-DD> (<method>)` or `m:<key>`; re-read it from the run's own record after the last edit (T145's forwarders were 198 and 66 lines, reported 183 and 57) and label it where it stands (feature 449 T159). The unit: the sentence, cut after a `.` and whitespace (a space or a line break) outside a code span, at a blank line, and where a bullet, a numbered item, a heading or a table row starts - not at `;`, so one label anywhere in the sentence covers it".to_owned(),
        Kind::RedExit => format!("an approach block's item 6 routes no red result through `make arbiter-ask` - give it D35's red exit, as `make task-add`'s template words it (feature 430 D5): \"{RED_EXIT_HINT}\" The unit: item 6 of each `### Txx Approach` block, to the next numbered item or heading; the task of each block"),
        Kind::Deferral => "a found-and-left item defers a defect without its form - fix it in this task by default; an item fixed here says `fixed here`, one that is not a defect says `not a defect` (constitution XIV); a deferral states `Not fixed here: <why>`, `filed as T<n>` (a box of tasks.md, `make task-add`) and `lands before T<m>` (another open task), as \"Not fixed here: it is in the wells stage, outside this task's files. Filed as T32; lands before T22.\" (feature 451 T17, D15). The unit: each `- ` item of the `**Found and left?**` answer, to the next item or bold line; an answer with no list is one item. Taken for a reason: `make decide ... DEFER_FORM_OK=\"<reason>\"`, recorded".to_owned(),
        Kind::DeferralClosed => "a found-and-left deferral names a task that is not open - a ticked box or an entry of tasks-done.md defers to nothing: file it as an open task (`make task-add`) and order it before an open one (feature 451 T17, D15). Judged once, at `make decide`; `make plan-delta` asks only that the ids are filed. Taken for a reason: `make decide ... DEFER_FORM_OK=\"<reason>\"`, recorded".to_owned(),
        Kind::ClassFix => "a fix of a class of defect (every writer, every form, every file of a kind, each of the ..., all the ...) with no line on how every instance was found - add `observed <YYYY-MM-DD>, method: <how every instance was found>` (or `measured <YYYY-MM-DD> (<method>)`) to it (feature 451 T17, D15). The unit: each `**Found and left?**` item, and item 12 (`Before any fix`) of each Approach block. Taken for a reason: `make decide ... DEFER_FORM_OK=\"<reason>\"`, recorded".to_owned(),
    }
}

/// The findings and the section-level refusals as one report: how many, then each rule's words once and its findings beneath, each
/// with the place `place` names for its offset - as `make done` reports every failure together. "" when there is nothing.
pub(super) fn render(
    found: &[Finding],
    place: &dyn Fn(usize) -> String,
    more: &[String],
) -> String {
    let total = found.len() + more.len();
    if total == 0 {
        return String::new();
    }
    let mut text = format!(
        "{total} finding{} - every one of the section's, reported together: fix them all, then run it once more",
        if total == 1 { "" } else { "s" }
    );
    let mut n = 0;
    for kind in [
        Kind::GmQuote,
        Kind::Item4,
        Kind::UnitFigure,
        Kind::Differential,
        Kind::Count,
        Kind::RedExit,
        Kind::Deferral,
        Kind::DeferralClosed,
        Kind::ClassFix,
    ] {
        let mut of: Vec<&Finding> = found.iter().filter(|f| f.kind == kind).collect();
        if of.is_empty() {
            continue;
        }
        of.sort_by_key(|f| f.start);
        n += 1;
        let _ = write!(text, "\n({n}) {}:", told(kind));
        for f in of {
            let _ = write!(text, "\n  {}: {}", place(f.start), f.text);
        }
    }
    for why in more {
        n += 1;
        let _ = write!(text, "\n({n}) {why}");
    }
    text
}

/// The task id a block's heading opens with, or "".
fn block_task(body: &str) -> String {
    let title = body
        .lines()
        .next()
        .unwrap_or("")
        .trim_start_matches('#')
        .trim();
    l7r_shared::plan_text::leading_task(title)
        .unwrap_or("")
        .to_owned()
}

/// The 1-based line of offset `at` in `text`.
pub(super) fn line_at(text: &str, at: usize) -> usize {
    text[..at.min(text.len())].matches('\n').count() + 1
}

/// The plan.md line of each line of `section` (0-based, in order): a section is the plan's slice from its heading, or, for a task
/// with several headings of its own, those slices joined in the plan's order, so each line is found at or after the one before it.
pub(super) fn plan_lines(plan: &str, section: &str) -> Vec<usize> {
    if let Some(base) = plan.find(section) {
        let first = line_at(plan, base);
        return (0..section.split('\n').count())
            .map(|i| first + i)
            .collect();
    }
    let lines: Vec<&str> = plan.split('\n').collect();
    let mut cursor = 0;
    section
        .split('\n')
        .map(|line| {
            if let Some(j) = lines[cursor..].iter().position(|l| *l == line) {
                cursor += j + 1;
            }
            cursor.max(1)
        })
        .collect()
}

/// Every finding `make decide` makes of `section`: the lint's, and the deferrals to a task not open now (D15: judged at the decision).
pub(super) fn decide_findings(spec_dir: &Path, section: &str) -> Vec<Finding> {
    let mut out = findings(spec_dir, section);
    let boxes = deferral::boxes(spec_dir);
    out.extend(
        deferral::closed(section, &boxes)
            .into_iter()
            .map(|((start, end), text)| Finding {
                kind: Kind::DeferralClosed,
                start,
                end,
                text,
            }),
    );
    out
}

/// Why `make decide` refuses `task`'s section of `plan`, or "": every finding of `found` (see [`decide_findings`]), each placed by its
/// plan.md line, and the approach gate's refusal, `more`, in the same report.
pub(super) fn decide_refusal(
    plan: &str,
    section: &str,
    found: &[Finding],
    more: Option<String>,
) -> String {
    let lines = plan_lines(plan, section);
    render(
        found,
        &|at| {
            let i = line_at(section, at) - 1;
            format!("plan.md:{}", lines.get(i).copied().unwrap_or(0))
        },
        &more.into_iter().collect::<Vec<_>>(),
    )
}

/// Why `make decide` refuses this section, or "": every finding, each placed by its line in the section (the tests' form).
#[cfg(test)]
pub(super) fn refusal(spec_dir: &Path, section: &str) -> String {
    render(
        &findings(spec_dir, section),
        &|at| format!("line {}", line_at(section, at)),
        &[],
    )
}

/// Why `make plan-delta` writes no bundle, or "" (feature 430 T05, D5: a plan review is never dispatched on what a script can see):
/// every finding of every changed block, each placed by its plan.md line, and the open tasks with no approach block, in one report.
/// `bodies` are the blocks with their offsets in `plan`. A block's deferral findings are dropped where `excused` answers true for its
/// task (the id its heading opens with, or ""): asked only of a block that has one, since its answer reads the guard log (D15).
pub(super) fn plan_refusal(
    spec_dir: &Path,
    plan: &str,
    bodies: &[(String, usize)],
    excused: &dyn Fn(&str) -> bool,
) -> String {
    let mut found = Vec::new();
    for (body, offset) in bodies {
        let mut own = findings(spec_dir, body);
        if own.iter().any(Finding::deferral) && excused(&block_task(body)) {
            own.retain(|f| !f.deferral());
        }
        found.extend(own.into_iter().map(|mut f| {
            f.start += offset;
            f
        }));
    }
    let missing = tasks_without_approach(spec_dir, plan);
    let more: Vec<String> = if missing.is_empty() {
        Vec::new()
    } else {
        vec![format!("open tasks with no `### Txx Approach (checklist part A)` block in the plan - write one for each, `make task-add`'s template has the form (feature 430 D5):\n  {}", missing.join(", "))]
    };
    render(
        &found,
        &|at| format!("plan.md:{}", line_at(plan, at)),
        &more,
    )
}

#[cfg(test)]
mod tests;
