//! A review check's dispatch (`pair-hooks.sh`'s Agent branch): decided first, one unit an agent, a glyph unit at its hour, its
//! prerequisites met, under the round cap, and a green gate for the content it reviews - each refusal in the shell's words.

use std::fmt::Write as _;
use std::sync::LazyLock;
use std::time::SystemTime;

use fancy_regex::Regex;

use super::{python, state, Ctx};
use crate::protocol::Answer;
use crate::shared::escape::enough;

static DECIDE_OK: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r#"\bDECIDE_OK="([^"]*)""#).unwrap());
static GLYPH_DUE_OK: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r#"GLYPH_DUE_OK="([^"]*)""#).unwrap());
static PREREQ_REASON: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r#"REVIEW_PREREQ_OK="([^"]*)""#).unwrap());
static BUNDLE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r#"[^ `"]*/MANIFEST\.md|/tmp/l7r-check/[^ `")]*"#).unwrap());

/// The first capture of `re` in `text`, or "".
fn quoted(re: &Regex, text: &str) -> String {
    re.captures(text)
        .ok()
        .flatten()
        .and_then(|c| c.get(1))
        .map(|m| m.as_str().to_owned())
        .unwrap_or_default()
}

/// A prompt written to a temporary file, for the tools that read one (`--prompt-file`); removed when dropped.
struct PromptFile(std::path::PathBuf);

impl PromptFile {
    fn new(text: &str) -> Self {
        let p = std::env::temp_dir().join(format!(
            "l7r-guard-prompt-{}-{:?}",
            std::process::id(),
            SystemTime::now()
        ));
        let _ = std::fs::write(&p, text);
        Self(p)
    }
}

impl Drop for PromptFile {
    fn drop(&mut self) {
        let _ = std::fs::remove_file(&self.0);
    }
}

/// The units a tool named, one a line, as the shell's `tr '\n' ' '` read them.
fn words(text: &str) -> Vec<String> {
    text.split_whitespace().map(str::to_owned).collect()
}

/// The maps whose manifest moved against main (`review_owed_names`).
fn owed(cx: &Ctx) -> Vec<String> {
    words(
        &python(
            cx.python,
            &cx.clone,
            &cx.tree.join("scripts/reviews/review_owed.py"),
            &["--root", &cx.clone.to_string_lossy()],
            "",
        )
        .out,
    )
}

pub(super) fn dispatch(cx: &Ctx, atype: &str) -> Vec<Answer> {
    let ptext = cx.field("prompt");
    if let Some(refused) = decided(cx, atype, ptext) {
        return vec![refused];
    }
    let pf = PromptFile::new(ptext);
    let clone = cx.clone.to_string_lossy().into_owned();
    let named = words(
        &python(
            cx.python,
            &cx.clone,
            &cx.tree.join("scripts/reviews/review_prereq.py"),
            &[
                "named",
                "--clone",
                &clone,
                "--prompt-file",
                &pf.0.to_string_lossy(),
            ],
            "",
        )
        .out,
    );
    if named.len() > 1 {
        let mut text = format!(
            "\n\x1b[1mBLOCKED: this {atype} asks for {} units in ONE agent - one unit per agent, all in this same message.\x1b[0m\n\
             The sweeps share no work across maps, so one agent serializes them (feature 247: four maps, 11 of 36 minutes).\n\
             Dispatch one agent per unit now, each with the contents of its prompt file:\n",
            named.len()
        );
        for m in &named {
            let pf = cx
                .clone
                .join(".git/review-snapshot")
                .join(m)
                .join("dispatch.md");
            let _ = if pf.is_file() {
                writeln!(text, "    {}", pf.display())
            } else {
                writeln!(text, "    {m}: no prompt file (not owed, or the snapshot was never taken - `make verify` writes it)")
            };
        }
        text += "There is no escape for this shape (feature 248 D1).\n";
        cx.log("blocked", atype, "review-multi-map");
        return vec![Answer::Refuse(text)];
    }
    let glyph_escaped = match glyph(cx, atype, ptext, &named) {
        Ok(escaped) => escaped,
        Err(refused) => return vec![refused],
    };
    if let Some(refused) = prerequisites(cx, atype, ptext, &named, &pf) {
        return vec![refused];
    }
    let key = state::engine_key(&cx.clone);
    if let Some(refused) = rounds(cx, atype, &named, &key) {
        return vec![refused];
    }
    if !key.is_empty() {
        state::write_pairing(&cx.clone, "review_dispatch_key", &key);
    }
    let prompt = cx
        .event
        .input
        .get("tool_input")
        .map(ToString::to_string)
        .unwrap_or_default();
    if prompt.contains("PAIR_OK") {
        cx.log("escaped", atype, "pair-ok-review");
        state::log_bypass(
            &cx.clone,
            "named in the dispatch",
            "review alone",
            SystemTime::now(),
        );
        dispatched(cx, atype, &named, &key, glyph_escaped);
        return Vec::new();
    }
    if state::gate_green(&cx.clone, &key) {
        dispatched(cx, atype, &named, &key, glyph_escaped);
        return Vec::new();
    }
    let mut text = format!(
        "\n\x1b[1mBLOCKED: a {atype} with no green gate for this content.\x1b[0m\n\
         A review is dispatched once the gate is GREEN on the content it reviews (feature 294, US6): a gate that\n\
         goes red under a running review makes the round NOT-REVIEWABLE, and that round is the cost this avoids.\n\n    \
         make verify        # starts the gate and writes the owed prompts; dispatch when it reports green\n\n\
         Deliberately one-sided? Put PAIR_OK and the reason in the dispatch prompt.\n"
    );
    if cx.fell_back {
        text += "NOTE: this session's clone could not be resolved (an unnamed session, or a clone claimed but never created), so this verdict was judged against MAIN's tree, where the shell is standing - not against your work. Ask the GM to /rename this session, or run from your clone, and the pairing will read the right tree.\n";
    }
    cx.log("blocked", atype, "review-without-gate");
    vec![Answer::Refuse(text)]
}

/// DECIDE FIRST (feature 375): a check's dispatch waits for the plan's decisions to be ruled, unless `DECIDE_OK="<reason>"`.
fn decided(cx: &Ctx, atype: &str, ptext: &str) -> Option<Answer> {
    let why = quoted(&DECIDE_OK, ptext);
    if why.split_whitespace().count() >= 2 && why.chars().count() >= 8 {
        cx.log("escaped", &why, "decide-ok");
        return None;
    }
    let script = cx.tree.join("scripts/gates/plan_gate.py");
    let why = python(
        cx.python,
        &cx.clone,
        &script,
        &["decided", &cx.clone.to_string_lossy()],
        "",
    )
    .out;
    if why.is_empty() {
        return None;
    }
    let on = BUNDLE
        .find(ptext)
        .ok()
        .flatten()
        .map_or("its prompt", |m| m.as_str())
        .to_owned();
    cx.log("blocked", atype, "decide-first");
    Some(Answer::Refuse(format!(
        "\nBLOCKED: {atype} on {on}: {why}\n(or DECIDE_OK=\"<reason>\" in the prompt; the pair-hooks guard, rust/guard/src/guards/pair_hooks/review.rs, feature 375)\n"
    )))
}

/// The reason an `*_OK="<why>"` escape gives, refused when it is not two words and eight characters.
fn reasoned(
    cx: &Ctx,
    atype: &str,
    re: &Regex,
    token: &str,
    ptext: &str,
    rule: &str,
) -> Result<String, Answer> {
    let why = quoted(re, ptext);
    if why.is_empty() || !enough(why.trim()) {
        cx.log("blocked", atype, &format!("{rule}-no-reason"));
        return Err(Answer::Refuse(format!(
            "\n\x1b[1mBLOCKED: {token} needs a REASON\x1b[0m (two words, eight characters, in quotes) - it is what a later audit reads.\n"
        )));
    }
    Ok(why)
}

/// A glyph unit goes out at its hour, with the others (feature 294), unless `GLYPH_DUE_OK="<why>"`: whether it escaped, or the refusal.
fn glyph(cx: &Ctx, atype: &str, ptext: &str, named: &[String]) -> Result<bool, Answer> {
    let script = cx.clone.join("scripts/reviews/review_owed.py");
    if atype != "glyph-check" || named.is_empty() || !script.is_file() {
        return Ok(false);
    }
    if ptext.contains("GLYPH_DUE_OK=") {
        let why = reasoned(cx, atype, &GLYPH_DUE_OK, "GLYPH_DUE_OK", ptext, "glyph-due")?;
        cx.log("escaped", atype, "glyph-due-ok");
        state::log_bypass(
            &cx.clone,
            &format!("GLYPH_DUE_OK: {why}"),
            "glyph check before its hour",
            SystemTime::now(),
        );
        return Ok(true);
    }
    for m in named {
        let early = python(
            cx.python,
            &cx.clone,
            &script,
            &["--root", &cx.clone.to_string_lossy(), "--glyph-gate", m],
            "",
        );
        if !early.ok() {
            cx.log("blocked", &format!("{atype}:{m}"), "glyph-not-due");
            return Err(Answer::Refuse(format!(
                "\n\x1b[1mBLOCKED: {}\x1b[0m\nOwed glyph units wait for the hour and go out together; `make verify` names them and when they come due.\n\
                 A check that must run now: GLYPH_DUE_OK=\"<why>\" in the dispatch prompt.\n",
                early.out
            )));
        }
    }
    Ok(false)
}

/// The round is not spent on unverified work (feature 240), unless `REVIEW_PREREQ_OK="<why>"`.
fn prerequisites(
    cx: &Ctx,
    atype: &str,
    ptext: &str,
    named: &[String],
    pf: &PromptFile,
) -> Option<Answer> {
    let script = cx.clone.join("scripts/reviews/review_prereq.py");
    if !script.is_file() {
        return None;
    }
    if ptext.contains("REVIEW_PREREQ_OK=") {
        let why = match reasoned(
            cx,
            atype,
            &PREREQ_REASON,
            "REVIEW_PREREQ_OK",
            ptext,
            "review-prereq",
        ) {
            Ok(why) => why,
            Err(refused) => return Some(refused),
        };
        cx.log("escaped", atype, "review-prereq-ok");
        state::log_bypass(
            &cx.clone,
            &format!("REVIEW_PREREQ_OK: {why}"),
            "review prerequisites",
            SystemTime::now(),
        );
        return None;
    }
    let green = if state::stamp_fresh(&cx.clone) {
        "yes"
    } else {
        "no"
    };
    let maps = if named.is_empty() {
        owed(cx)
    } else {
        named.to_vec()
    }
    .join(" ");
    let clone = cx.clone.to_string_lossy();
    let said = python(
        cx.python,
        &cx.clone,
        &script,
        &[
            "check",
            "--clone",
            &clone,
            "--maps",
            &maps,
            "--prompt-file",
            &pf.0.to_string_lossy(),
            "--gate-green",
            green,
        ],
        "",
    );
    if said.ok() {
        return None;
    }
    let problems = [said.out.as_str(), said.err.as_str()]
        .iter()
        .filter(|s| !s.is_empty())
        .copied()
        .collect::<Vec<_>>()
        .join("\n");
    let listed = problems.lines().fold(String::new(), |mut s, l| {
        let _ = writeln!(s, "  - {l}");
        s
    });
    cx.log("blocked", atype, "review-prerequisites-unmet");
    Some(Answer::Refuse(format!(
        "\n\x1b[1mBLOCKED: this {atype} would spend its round on work that has not been verified.\x1b[0m\n\
         A review round costs minutes; each item below costs seconds to fix (feature 240):\n\n{listed}\n\
         Deliberately reviewing a map left in this state? Put REVIEW_PREREQ_OK=\"<why>\" in the dispatch prompt.\n"
    )))
}

/// The round arbiter's check, as the shell ran it (feature 375 amendment 2).
const ARBITER: &str = r#"import sys; sys.path.insert(0, sys.argv[1]); import hm_arbiter as a
from pathlib import Path
root, unit, n = Path(sys.argv[2]), sys.argv[3], int(sys.argv[4])
ck = a.unit_content_key(root, unit) if a.closed(root, f"round:{unit}@") else None  # an accept bound to an older sheet has lapsed
shut = a.closed(root, f"round:{unit}@", ck)
if shut:
    print(f"closed\tthe round arbiter closed {unit} ({shut}) - what is left is filed; the session does not re-ask (FR-011)")
elif n - 2 > a.continues(root, f"round:{unit}@") + a.lapsed(root, f"round:{unit}@", ck):
    a.trip(root, f"round:{unit}@{n}", "round", unit, f"round {n} of a review check")
    print("owed\t" + a.refusal([f"round:{unit}@{n}"], root))
else:
    print("continue\t")"#;

/// The round cap, two a feature (feature 294 FR-009), past which the round arbiter rules.
fn rounds(cx: &Ctx, atype: &str, named: &[String], key: &str) -> Option<Answer> {
    if named.is_empty() || key.is_empty() {
        return None;
    }
    let unit = named.join(" ");
    let n = state::round_number(&cx.clone, &unit, key);
    if n <= 2 {
        return None;
    }
    let lib = cx.tree.join("scripts/hooks/lib");
    let args = [
        lib.to_string_lossy().into_owned(),
        cx.clone.to_string_lossy().into_owned(),
        format!("{atype}|{unit}"),
        n.to_string(),
    ];
    let arb = crate::shared::tool::ask(
        &cx.clone,
        "python3",
        &["-c", ARBITER, &args[0], &args[1], &args[2], &args[3]],
        "",
    )
    .out;
    if arb.starts_with("continue") {
        cx.log(
            "permitted",
            &format!("{atype}:{unit}"),
            "review-round-arbiter-continue",
        );
        return None;
    }
    let said = arb.split_once('\t').map_or(arb.as_str(), |(_, r)| r);
    cx.log("blocked", &format!("{atype}:{unit}"), "review-round-cap");
    Some(Answer::Refuse(format!(
        "\n\x1b[1mBLOCKED: round {n} of {unit} for {atype} in this feature - the cap is two (feature 294 FR-009).\x1b[0m\n{said}\n"
    )))
}

/// Each dispatched unit recorded: its glyph hour, its dispatch (and whether the owed units went out in parallel), its round.
fn dispatched(cx: &Ctx, atype: &str, named: &[String], key: &str, glyph_escaped: bool) {
    if named.is_empty() || key.is_empty() {
        return;
    }
    let owed = owed(cx);
    for m in named {
        if atype == "glyph-check" {
            let script = cx.clone.join("scripts/reviews/review_owed.py");
            let clone = cx.clone.to_string_lossy();
            let mut args = vec!["--root", clone.as_ref(), "--glyph-dispatched", m.as_str()];
            if glyph_escaped {
                args.push("--escaped");
            }
            let _ = python(cx.python, &cx.clone, &script, &args, "");
        }
        let span = state::record_dispatch(&cx.clone, m, key, state::now(&cx.clone), &owed);
        state::record_round(&cx.clone, m, key, state::wall()); // the shell's `time.time()`: the fixture clock is the dispatch record's alone
        cx.log("permitted", &format!("{atype}:{m}"), "review-dispatched");
        if let Some(s) = span.strip_prefix("parallel ") {
            cx.log("permitted", &format!("{atype}:{s}s"), "reviews-parallel");
        } else if let Some(s) = span.strip_prefix("serialized ") {
            cx.log("permitted", &format!("{atype}:{s}s"), "reviews-serialized");
        }
    }
}
