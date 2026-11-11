//! A review check's dispatch (`pair-hooks.sh`'s Agent branch): decided first, one unit an agent, a glyph unit at its hour, its
//! prerequisites met, under the round cap, and a green gate for the content it reviews - each refusal in the shell's words.

use std::fmt::Write as _;
use std::sync::LazyLock;
use std::time::SystemTime;

use fancy_regex::Regex;

use super::{python, reviews, state, Ctx};
use crate::protocol::Answer;
use crate::shared::checks;
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

/// The review units owed now (`l7r-gate reviews owed`).
fn owed(cx: &Ctx) -> Vec<String> {
    words(&reviews(cx, &["owed", "--root", &cx.clone.to_string_lossy()]).out)
}

pub(super) fn dispatch(cx: &Ctx, atype: &str) -> Vec<Answer> {
    let ptext = cx.field("prompt");
    if let Some(refused) = decided(cx, atype, ptext) {
        return vec![refused];
    }
    let pf = PromptFile::new(ptext);
    let clone = cx.clone.to_string_lossy().into_owned();
    let named = words(
        &reviews(
            cx,
            &[
                "prereq",
                "named",
                "--clone",
                &clone,
                "--prompt-file",
                &pf.0.to_string_lossy(),
            ],
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
    let script = cx.tree.join("scripts/gates/l7r-gate.sh");
    let why = python(
        "bash",
        &cx.clone,
        &script,
        &["plan", "decided", &cx.clone.to_string_lossy()],
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
    if atype != "glyph-check" || named.is_empty() {
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
        let early = reviews(
            cx,
            &["owed", "--root", &cx.clone.to_string_lossy(), "--glyph-gate", m],
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
    let said = reviews(
        cx,
        &[
            "prereq",
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

/// A review unit's sheet as it reads now (`l7r-gate reviews prereq content-key`), or "" where it has none.
fn unit_content_key(cx: &Ctx, unit: &str) -> String {
    let bare = unit.split_once('|').map_or(unit, |(_, b)| b);
    reviews(
        cx,
        &[
            "prereq",
            "content-key",
            "--clone",
            &cx.clone.to_string_lossy(),
            "--map",
            bare,
        ],
    )
    .out
    .trim()
    .to_owned()
}

/// `(closed, ...)`, `(owed, ...)` or `(continue, )`: the round arbiter's check on a third round, in-process.
fn arbiter_verdict(cx: &Ctx, unit: &str, n: usize) -> String {
    let (root, prefix) = (&cx.clone, format!("round:{unit}@"));
    let ck = if checks::arbiter::closed(root, &prefix, None).is_empty() {
        None
    } else {
        Some(unit_content_key(cx, unit))
    };
    let shut = checks::arbiter::closed(root, &prefix, ck.as_deref());
    if !shut.is_empty() {
        return format!("closed\tthe round arbiter closed {unit} ({shut}) - what is left is filed; the session does not re-ask (FR-011)");
    }
    if u64::try_from(n.saturating_sub(2)).unwrap_or(u64::MAX)
        > checks::arbiter::continues(root, &prefix, 0)
            + checks::arbiter::lapsed(root, &prefix, ck.as_deref())
    {
        let trigger = format!("round:{unit}@{n}");
        let _ = checks::arbiter::trip(
            root,
            &trigger,
            "round",
            unit,
            &format!("round {n} of a review check"),
            &serde_json::Value::Null,
            "",
        );
        return format!("owed\t{}", checks::arbiter::refusal(&[trigger], Some(root)));
    }
    "continue\t".to_owned()
}

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
    let arb = arbiter_verdict(cx, &format!("{atype}|{unit}"), n);
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
            let clone = cx.clone.to_string_lossy();
            let mut args = vec!["owed", "--root", clone.as_ref(), "--glyph-dispatched", m.as_str()];
            if glyph_escaped {
                args.push("--escaped");
            }
            let _ = reviews(cx, &args);
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
