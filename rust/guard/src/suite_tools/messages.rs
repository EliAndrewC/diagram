//! EVERY GUARD MESSAGE HELD TO A BUDGET AND REVIEWED ONCE A WORDING (feature 451 T170; the GM 2026-11-23, on hook output length:
//! "could we accomplish the same thing with no loss of fidelity and fewer tokens? ... Maybe even something mechanically enforced,
//! where each hook must contain a comment explaining how many words it uses and mentioning the subagent check that reviewed it").
//! A comment beside a message drifts from the text it describes, so the text itself is read: each refusal, block and notice a guard
//! suite renders (`protocol::keep`, under `tests/hooks/hookrun.sh`) is held to its kind's budget, and its wording - the text with its
//! paths, ids and numbers masked, keyed by the SHA-256 of guard, kind and that text - must have a verdict in `dev/guard-messages.tsv`:
//! `PASS` from the `message-check` agent (`.claude/agents/message-check.md`), or `BASELINE`, a message that stood before T170 and is
//! unreviewed. A new or changed wording is owed that review; past its budget it passes only where the review rules every word needed.
//! A message that grows with a list is held at its worst case too, many items, rendered by [`worst`] beside the suites' renderings.
//!
//! ```text
//! l7r-guard messages check <corpus dir> <record>            exit 1 naming each message unreviewed or over its budget, with the fix
//! l7r-guard messages owed <corpus dir> <record> <bundle>    the unreviewed messages, one unit each, written for message-check
//! l7r-guard messages verdict <corpus dir> <record> <key> <PASS|FAIL|BREVITY:<failed key>> <by> [<over>]   a review's verdict by its key
//!                                         (BREVITY:<failed key>: a second review failing on brevity alone, <failed key> the failed wording
//!                                         this text replaced - the text stands, 451 T177)
//! l7r-guard messages verdict <corpus dir> <record> <key> BASELINE <why>   a wording newly rendered left unreviewed, <why> its measured
//!                                         characters a session under T177's break-even (451 T174)
//! l7r-guard messages baseline <corpus dir> <record> <why>   the first record: every message rendered, BASELINE, unreviewed
//! l7r-guard messages rehead <corpus dir> <record>           every stored head written again, its paths masked; no other column moves
//! ```
//!
//! The corpus directory is the TREE's own store, never one the clone's worktrees share (451 T281): [`store`].

use std::collections::BTreeMap;
use std::fmt::Write as _;
use std::path::Path;

use fancy_regex::Regex;
use serde_json::Value;

use crate::protocol::Reply;
use crate::shared::sha256;

/// THE BUDGETS, in characters, a GUESS (451 T170): a notice is read on the call it rides, often every call, a refusal or a block once
/// a fix. Set 2026-11-23 from the wordings `make hooks-test HOOKS_ALL=1` rendered after T170's cuts: the longest notice 838
/// characters (main-tree's), refusal 1,777 (measure's), block 514, each rounded up; the 90th percentiles, 675 and 967, were priced
/// and not taken, since a baselined message is not yet known to be needed. A knob, moved by a measurement, never a target to defend.
pub const NOTICE_BUDGET: usize = 900;
/// A refusal's or a block's budget (see [`NOTICE_BUDGET`]).
pub const REFUSE_BUDGET: usize = 1_800;

const HEADER: &str = "key\tverdict\tchars\tguard\tkind\tby\tover\thead";

/// One wording as the suites rendered it: its guard, kind, longest rendering and that text.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Message {
    pub guard: String,
    pub kind: String,
    pub chars: usize,
    pub text: String,
}

impl Message {
    fn budget(&self) -> usize {
        if self.kind == "notice" {
            NOTICE_BUDGET
        } else {
            REFUSE_BUDGET
        }
    }
}

/// A row of the record.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Row {
    pub verdict: String,
    pub chars: usize,
    pub guard: String,
    pub kind: String,
    pub by: String,
    pub over: String,
    pub head: String,
}

struct Masks {
    ansi: Regex,
    path: Regex,
    hex: Regex,
    digits: Regex,
    space: Regex,
    relative: Regex,
}

impl Masks {
    fn new() -> Self {
        let b = |p: &str| crate::shared::regex::build(p).expect("a fixed pattern");
        Self {
            ansi: b(r"\x1b\[[0-9;]*m"),
            path: b(r"(?<![\w.])(?:~|\.{1,2})?/(?:[\w.@+~-]+/)*[\w.@+~-]+/?"),
            hex: b(r"\b[0-9a-f]{7,}\b"),
            digits: b(r"\d+"),
            space: b(r"\s+"),
            // a relative path (`research/questions/`, `lNr/diagram/m.py`), which the wording leaves, since a key stands on it; one
            // with a lowercase letter, so `N/N` and `PASS/FAIL` stay words
            relative: b(
                r"(?<![\w.@+~*$/<>-])(?=[\w.@+~*$/-]*[a-z])[\w.@+~*$-]+/(?:[\w.@+~*$-]+/)*[\w.@+~*$-]*",
            ),
        }
    }

    /// A head as the record stores it: its relative paths masked too, so no stored row is a pointer a check resolves (451 T170 at
    /// its landing: record-edit's notice, rendered with its fixture's edited path, a built research page, failed the gate's pointer
    /// check). Neither a space nor a backtick is masked, so a head's words and code spans stand.
    fn stored(&self, head: &str) -> String {
        self.relative.replace_all(head, "<path>").into_owned()
    }

    /// The wording: `text` with its paths, ids and numbers masked and its whitespace one space - what a suite's fixture or clock
    /// changes and a guard's author does not.
    fn wording(&self, text: &str) -> String {
        let t = self.ansi.replace_all(text, "");
        let t = self.path.replace_all(&t, "<path>");
        // an id and a number are one mask, so a pid of 7 digits and one of 1 are the same wording
        let t = self.hex.replace_all(&t, "N");
        let t = self.digits.replace_all(&t, "N");
        self.space.replace_all(t.trim(), " ").into_owned()
    }
}

/// The key of a wording: the first 16 hex digits of SHA-256 over guard, kind and wording.
#[must_use]
pub fn key(guard: &str, kind: &str, wording: &str) -> String {
    sha256::hex(format!("{guard}\0{kind}\0{wording}").as_bytes())[..16].to_owned()
}

/// Every wording the corpus directory's `*.jsonl` files hold, by key, each at its longest rendering.
#[must_use]
pub fn corpus(dir: &Path) -> BTreeMap<String, Message> {
    let masks = Masks::new();
    let mut files: Vec<_> = std::fs::read_dir(dir)
        .map(|d| d.filter_map(Result::ok).map(|e| e.path()).collect())
        .unwrap_or_default();
    files.retain(|p| p.extension().is_some_and(|e| e == "jsonl"));
    files.sort();
    let mut out = BTreeMap::new();
    let lines: Vec<String> = files
        .iter()
        .flat_map(|f| {
            std::fs::read_to_string(f)
                .unwrap_or_default()
                .lines()
                .map(str::to_owned)
                .collect::<Vec<_>>()
        })
        .collect();
    for line in lines {
        let Ok(v) = serde_json::from_str::<Value>(&line) else {
            continue;
        };
        let field = |k: &str| v.get(k).and_then(Value::as_str).unwrap_or("").to_owned();
        let (guard, kind, text) = (field("guard"), field("kind"), field("text"));
        if text.trim().is_empty() {
            continue;
        }
        let chars = text.chars().count();
        let m = out
            .entry(key(&guard, &kind, &masks.wording(&text)))
            .or_insert_with(|| Message {
                guard,
                kind,
                chars: 0,
                text: String::new(),
            });
        if chars > m.chars {
            m.chars = chars;
            m.text = text;
        }
    }
    out
}

/// The record, by key; an absent or unreadable record is empty.
#[must_use]
pub fn record(path: &Path) -> BTreeMap<String, Row> {
    let text = std::fs::read_to_string(path).unwrap_or_default();
    text.lines()
        .filter(|l| !l.is_empty() && *l != HEADER)
        .filter_map(|l| {
            let c: Vec<&str> = l.split('\t').collect();
            (c.len() == 8).then(|| {
                (
                    c[0].to_owned(),
                    Row {
                        verdict: c[1].to_owned(),
                        chars: c[2].parse().unwrap_or(0),
                        guard: c[3].to_owned(),
                        kind: c[4].to_owned(),
                        by: c[5].to_owned(),
                        over: c[6].to_owned(),
                        head: c[7].to_owned(),
                    },
                )
            })
        })
        .collect()
}

fn write_record(path: &Path, rows: &BTreeMap<String, Row>) -> std::io::Result<()> {
    let masks = Masks::new();
    let mut out = format!("{HEADER}\n");
    for (k, r) in rows {
        let _ = writeln!(
            out,
            "{k}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            r.verdict,
            r.chars,
            r.guard,
            r.kind,
            r.by,
            r.over,
            masks.stored(&r.head)
        );
    }
    std::fs::write(path, out)
}

/// The first words of a message's wording - its paths, ids and numbers masked as its key masks them, so a suite's temporary
/// directories and pids never reach the record - as the record's `head` shows it, where its relative paths are masked too
/// ([`Masks::stored`]), which a key leaves so that no key moves. It never ends inside a code span: the push's
/// house-style delta check pairs a file's backticks across its lines, so a head cut mid-span left the next row's named word bare
/// (451 T170: three cut heads turned `centre` in a later row's code span into a British spelling).
fn head(masks: &Masks, text: &str) -> String {
    let wording = masks.wording(text);
    let mut words: Vec<&str> = wording.split(' ').take(12).collect();
    while words.iter().map(|w| w.matches('`').count()).sum::<usize>() % 2 == 1 {
        words.pop();
    }
    words.join(" ")
}

const CUT: &str = "shorten it - keep its fix command and escape in full; a list gives its first few items and `and N more: \
<the command that prints them all>` (shared::listed)";

/// Whether a review of `m` is a SECOND on its subject: `first`, the key of the wording `m` replaced, is a FAIL of the same guard and
/// kind that nothing renders now and no other second review has named; that FAIL's `by` where it is. 451 T177, the round arbiter's
/// tooling fix on ask:guard-wordings-sleep-and-slot: a second review failing on BREVITY alone, its FIDELITY passing, leaves the text
/// as reviewed and passes it (`VERDICT=BREVITY:<first>`), the cap ask:guard-wordings-third-round set - two asks in 15 minutes had
/// ruled the same loop of reviewer taste. A FIDELITY failure is still a FAIL, fixed. WHY the key is named: guard and kind alone hold
/// several wordings (make-only's refusals, finished-run's four), so a FAIL of the kind matched a sibling's first review too (MODE 4 on
/// T177's plan, round 2, D6c); one FAIL is the first of one second review.
fn second_review(
    found: &BTreeMap<String, Message>,
    rows: &BTreeMap<String, Row>,
    m: &Message,
    first: &str,
) -> Option<String> {
    let named = format!("key {first})");
    let spent = rows.values().any(|r| r.by.ends_with(&named));
    rows.get(first)
        .filter(|r| r.verdict == "FAIL" && r.guard == m.guard && r.kind == m.kind)
        .filter(|_| !found.contains_key(first) && !spent)
        .map(|r| r.by.clone())
}

/// What a message owes: None where its row passes it, else the failure's text with its fix.
fn owes(key: &str, m: &Message, row: Option<&Row>) -> Option<String> {
    let budget = m.budget();
    let over = m.chars > budget;
    let fix = format!("make guard-messages BUNDLE=1, dispatch message-check on its unit, then record the verdict: make guard-messages KEY={key} VERDICT=PASS BY=\"<the agent's id>\"");
    let said = |why: &str, fix: &str| {
        let shown: Vec<String> = m.text.lines().map(|l| format!("  | {l}")).collect();
        Some(format!(
            "GUARD MESSAGE {why}: {} {}, key {key}, {} characters, budget {budget} (a GUESS, suite_tools/messages.rs):\n{}\n  fix: {fix}\n",
            m.guard,
            m.kind,
            m.chars,
            shown.join("\n")
        ))
    };
    match row.map(|r| (r.verdict.as_str(), r.over.is_empty())) {
        Some(("BASELINE", _)) => None,
        Some(("PASS", no_reason)) if !over || !no_reason => None,
        Some(("PASS", _)) => said("OVER BUDGET", &format!("{CUT} - and have it reviewed again; or, where message-check ruled every word NEEDED: make guard-messages KEY={key} VERDICT=PASS BY=\"<the agent's id>\" OVER=\"<its reason>\"")),
        Some(_) => said("FAILED ITS REVIEW", &format!("fix the wording message-check faulted, then {fix} (its second review failing on BREVITY alone, FIDELITY passing: VERDICT=BREVITY:{key} - the text stands)")),
        None if over => said("NEW OR CHANGED AND OVER BUDGET", &format!("{CUT} - then {fix} (OVER=\"<its NEEDED reason>\" past the budget)")),
        None => said("NEW OR CHANGED, NOT REVIEWED", &fix),
    }
}

/// `check`: every message's verdict and budget.
fn check(corpus: &BTreeMap<String, Message>, rows: &BTreeMap<String, Row>) -> Reply {
    if corpus.is_empty() {
        return reply(
            String::new(),
            "guard-messages: no message rendered - run make hooks-test HOOKS_ALL=1, which renders every suite's\n".to_owned(),
            1,
        );
    }
    let failed: Vec<String> = corpus
        .iter()
        .filter_map(|(k, m)| owes(k, m, rows.get(k)))
        .collect();
    if failed.is_empty() {
        return reply(
            format!(
                "guard-messages: {} wordings, each reviewed or baselined and within its budget\n",
                corpus.len()
            ),
            String::new(),
            0,
        );
    }
    reply(
        String::new(),
        format!(
            "{}guard-messages: {} of {} wordings owe a review or a cut (451 T170)\n",
            failed.join("\n"),
            failed.len(),
            corpus.len()
        ),
        1,
    )
}

/// `owed`: the bundle message-check reads, one unit a message, and the units named on stdout.
fn owed(corpus: &BTreeMap<String, Message>, rows: &BTreeMap<String, Row>, bundle: &Path) -> Reply {
    let mut text =
        String::from("# Guard messages owed a review (message-check, feature 451 T170)\n");
    let mut units = Vec::new();
    for (k, m) in corpus
        .iter()
        .filter(|(k, m)| owes(k, m, rows.get(*k)).is_some())
    {
        let gone: Vec<String> = rows
            .iter()
            .filter(|(rk, r)| !corpus.contains_key(*rk) && r.guard == m.guard && r.kind == m.kind)
            .map(|(_, r)| format!("- {}", r.head))
            .collect();
        let _ = write!(
            text,
            "\n## KEY {k}\n\nguard: {}\nkind: {}\nlength: {} characters, budget {}\n\nthe message:\n\n```\n{}\n```\n",
            m.guard,
            m.kind,
            m.chars,
            m.budget(),
            m.text
        );
        if !gone.is_empty() {
            let _ = write!(
                text,
                "\nthe same guard's recorded wordings of this kind that no suite renders now (one may be the text it replaced):\n{}\n",
                gone.join("\n")
            );
        }
        units.push(format!(
            "message-check:{k} {} {} ({} characters)",
            m.guard, m.kind, m.chars
        ));
    }
    if units.is_empty() {
        return reply(
            "guard-messages: nothing owed\n".to_owned(),
            String::new(),
            0,
        );
    }
    if let Err(e) = std::fs::write(bundle, text) {
        return reply(
            String::new(),
            format!("guard-messages: cannot write {}: {e}\n", bundle.display()),
            1,
        );
    }
    reply(
        format!(
            "{}\nguard-messages: {} unit(s) in {} - one message-check dispatch reads them all\n",
            units.join("\n"),
            units.len(),
            bundle.display()
        ),
        String::new(),
        0,
    )
}

fn reply(stdout: String, stderr: String, code: i32) -> Reply {
    Reply {
        stdout,
        stderr,
        code,
    }
}

fn row(masks: &Masks, m: &Message, verdict: &str, by: &str, over: &str) -> Row {
    Row {
        verdict: verdict.to_owned(),
        chars: m.chars,
        guard: m.guard.clone(),
        kind: m.kind.clone(),
        by: by.replace('\t', " "),
        over: over.replace('\t', " "),
        head: head(masks, &m.text),
    }
}

/// The command line.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let a: Vec<&str> = args.iter().map(String::as_str).collect();
    let usage = || {
        reply(
            String::new(),
            "usage: l7r-guard messages check|owed|verdict|baseline|rehead <corpus dir> <record> ... | store <dir> | gather <rendered dir> <tree store> <list>\n"
                .to_owned(),
            64,
        )
    };
    // the tree's store (451 T281): where it is, and its filling after a run's suites
    match a.as_slice() {
        ["store", dir] => return store::store_cli(dir),
        ["gather", rendered, tree, list] => {
            return store::gather(Path::new(rendered), Path::new(tree), Path::new(list))
        }
        ["store" | "gather", ..] => return usage(),
        _ => {}
    }
    let (Some(verb), Some(dir), Some(path)) = (a.first(), a.get(1), a.get(2)) else {
        return usage();
    };
    let path = Path::new(path);
    let mut found = corpus(Path::new(dir));
    found.extend(worst_cases(path));
    let mut rows = record(path);
    match (*verb, &a[3..]) {
        ("check", []) => check(&found, &rows),
        ("owed", [bundle]) => owed(&found, &rows, Path::new(bundle)),
        ("verdict", [k, "BASELINE", why]) => baselined(&found, rows, path, k, why),
        ("verdict", [k, v, by, over @ ..])
            if over.len() <= 1 && (matches!(*v, "PASS" | "FAIL") || v.starts_with("BREVITY")) =>
        {
            let Some(m) = found.get(*k) else {
                return reply(String::new(), format!("guard-messages: no message rendered has key {k} - make guard-messages lists them\n"), 1);
            };
            if by.trim().is_empty() {
                return reply(
                    String::new(),
                    "guard-messages: BY= names the message-check agent whose reply this is\n"
                        .to_owned(),
                    1,
                );
            }
            let (v, by) = if let Some(first) = v.strip_prefix("BREVITY") {
                let first = first.strip_prefix(':').unwrap_or_default();
                match second_review(&found, &rows, m, first) {
                    Some(by_then) => ("PASS", format!("{by} (a second review failing on BREVITY alone - the text stands, the round arbiter's standing rule, ask:guard-wordings-sleep-and-slot; the first: {by_then}, key {first})")),
                    None => return reply(String::new(), format!("guard-messages: a SECOND review failing on brevity alone is VERDICT=BREVITY:<the key of the failed wording this text replaced> - a {} {} FAIL no suite renders now and no other second review named; \"{first}\" is not one, and a first review's failure is recorded: make guard-messages KEY={k} VERDICT=FAIL BY=\"{by}\"\n", m.guard, m.kind), 1),
                }
            } else {
                (*v, (*by).to_owned())
            };
            rows.insert(
                (*k).to_owned(),
                row(&Masks::new(), m, v, &by, over.first().unwrap_or(&"")),
            );
            written(path, &rows, &format!("guard-messages: {k} recorded {v}\n"))
        }
        ("baseline", [why]) => {
            if !rows.is_empty() {
                return reply(String::new(), format!("guard-messages: {} already holds the baseline - a message new or changed since is reviewed: make guard-messages BUNDLE=1\n", path.display()), 1);
            }
            let masks = Masks::new();
            for (k, m) in &found {
                rows.insert(
                    k.clone(),
                    row(&masks, m, "BASELINE", &format!("unreviewed - {why}"), ""),
                );
            }
            written(
                path,
                &rows,
                &format!("guard-messages: {} wordings baselined\n", rows.len()),
            )
        }
        ("rehead", []) => written(
            path,
            &rows,
            &format!(
                "guard-messages: {} heads written, their paths masked\n",
                rows.len()
            ),
        ),
        _ => usage(),
    }
}

/// `verdict <key> BASELINE <why>` (451 T174): a wording a suite renders newly - one sessions already read, brought to the check by a
/// suite that rendered none of its guard's messages - left unreviewed where its review would not repay itself, T177's break-even (one
/// review, 31,680 characters, against what the wording costs a session). `why` carries that measured figure, a number in it. A wording
/// with a verdict keeps it, and one past its budget is cut or ruled needed: neither is baselined.
fn baselined(
    found: &BTreeMap<String, Message>,
    mut rows: BTreeMap<String, Row>,
    path: &Path,
    k: &str,
    why: &str,
) -> Reply {
    let refuse = |why: String| reply(String::new(), format!("guard-messages: {why}\n"), 1);
    let Some(m) = found.get(k) else {
        return refuse(format!(
            "no message rendered has key {k} - make guard-messages lists them"
        ));
    };
    if let Some(r) = rows.get(k) {
        return refuse(format!("{k} already holds {} - a wording's verdict is not undone; a changed wording is reviewed: make guard-messages BUNDLE=1", r.verdict));
    }
    if m.chars > m.budget() {
        return refuse(format!("{k} is {} characters, past its budget {} - cut it and have it reviewed: make guard-messages BUNDLE=1", m.chars, m.budget()));
    }
    if !why.chars().any(|c| c.is_ascii_digit()) {
        return refuse(format!("a baselined wording names what its review would not repay: make guard-messages KEY={k} VERDICT=BASELINE BY=\"<its measured characters a session> - under the break-even 31,680 a key (451 T177)\""));
    }
    rows.insert(
        k.to_owned(),
        row(
            &Masks::new(),
            m,
            "BASELINE",
            &format!("unreviewed - {why}"),
            "",
        ),
    );
    written(
        path,
        &rows,
        &format!("guard-messages: {k} recorded BASELINE\n"),
    )
}

/// The messages that grow with a list at their worst case ([`worst::worst`]), in the repository holding `record` - static-runs' at
/// every crate of it; none outside one.
fn worst_cases(record: &Path) -> BTreeMap<String, Message> {
    let at = record
        .parent()
        .filter(|p| !p.as_os_str().is_empty())
        .unwrap_or(Path::new("."));
    let top = crate::shared::checks::git_stdout(at, &["rev-parse", "--show-toplevel"]);
    if top.is_empty() {
        return BTreeMap::new();
    }
    let root = Path::new(&top);
    let masks = Masks::new();
    worst::worst(&worst::tree_crates(root), root)
        .into_iter()
        .map(|(m, keyed)| (key(&m.guard, &m.kind, &masks.wording(&keyed)), m))
        .collect()
}

fn written(path: &Path, rows: &BTreeMap<String, Row>, said: &str) -> Reply {
    match write_record(path, rows) {
        Ok(()) => reply(said.to_owned(), String::new(), 0),
        Err(e) => reply(
            String::new(),
            format!("guard-messages: cannot write {}: {e}\n", path.display()),
            1,
        ),
    }
}

pub mod store;
pub mod worst;

#[cfg(test)]
mod tests;
