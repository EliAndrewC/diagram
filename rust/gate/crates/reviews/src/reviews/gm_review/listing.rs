//! What `make gm-review` prints (feature 449 T91, from `scripts/gm_review.py`'s `listing`, `explain` and `_needs_you`): the questions
//! escalation-check KEPT (the GM's decisions, the one source - feature 432), the ones OWED it, the ranking rows held behind another
//! (328's `audit/overrides.json`, which waits on other work and is no decision of his), and per feature the rows he may overturn; with
//! `EXPLAIN=1`, each row in full - what fired it, what the arbiter ruled and why, the tooling fix and its fate, what he is asked.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::py_text::{strip, SPACE_CLASS};
use serde_json::{Map, Value};

use super::py::{get, has, head, len, py_str, read_text, rstrip, text, truthy, wrap, Raised, R};
use super::{feature, name, num, re, rows, Ctx, QUESTION};

/// 328's ranking: its rows held behind another wait on other work, never on the GM (feature 432, FR-004).
const HELD: &str = "specs/328-match-the-research/audit/overrides.json";

/// Each kind of row, in the order a feature's rows are shown, with its heading and its count's word.
const KINDS: [(&str, &str, &str); 5] = [
    ("arbiter", "arbiter rulings", "rulings"),
    ("accepted", "findings accepted with a reason", "accepted"),
    (
        "arbiter-fix-done",
        "tooling fixes the arbiter asked for, made",
        "fixes made",
    ),
    (
        "arbiter-fix-declined",
        "tooling fixes the arbiter asked for, declined to the GM",
        "fixes DECLINED",
    ),
    (
        "known-drift",
        "known drifts landed on their open fixing task (feature 430)",
        "known drifts",
    ),
];

/// What each ruling DID, in the words the GM reads it in (continue lifts a cap by one round, accept and process-fault close the unit).
const VERDICTS: [(&str, &str); 3] = [
    ("accept", "ACCEPT - stop checking; the work stands as it is now and this check runs no further round on it"),
    ("continue", "CONTINUE - allow one more round of the check"),
    ("process-fault", "PROCESS FAULT - the tooling, not the work, was at fault; the fix below is what it asks for"),
];

static ROUND: LazyLock<Regex> = LazyLock::new(|| re(r"\Around:([^|]+)\|[a-z]+:(.+?)(?:@(\d+))?\z"));
static KIND_AT: LazyLock<Regex> = LazyLock::new(|| re(r"\A([a-z-]+)[:@](.+?)\z"));
static Q_PAGE: LazyLock<Regex> = LazyLock::new(|| re(r"\|q:(\d{4})"));
static MODAL: LazyLock<Regex> = LazyLock::new(|| re(r"\|modal:(.+?)(?:@\d+)?(?=\n?\z)"));
static HELD_BEHIND: LazyLock<Regex> =
    LazyLock::new(|| re(&format!(r"\AHeld behind[:,]?[{SPACE_CLASS}]*")));
static HELD_PLAIN: LazyLock<Regex> =
    LazyLock::new(|| re(&format!(r"\AHeld behind[{SPACE_CLASS}]*")));
static DESCRIPTION: LazyLock<Regex> =
    LazyLock::new(|| re(&format!(r"(?m)^description:[{SPACE_CLASS}]*(.+)$")));

fn caps(r: &Regex, t: &str) -> Option<Vec<String>> {
    r.captures(t).ok().flatten().map(|c| {
        (0..c.len())
            .map(|i| c.get(i).map_or_else(String::new, |m| m.as_str().to_owned()))
            .collect()
    })
}

/// `_fit`: a line cut to `width` with `...`.
fn fit(line: &str, width: i128) -> String {
    if i128::try_from(len(line)).unwrap_or(i128::MAX) <= width {
        return line.to_owned();
    }
    format!("{}...", rstrip(&head(line, width - 3)))
}

/// `_wrap`: a labeled paragraph wrapped under a four-space indent; nothing where the text is empty.
fn para(label: &str, t: &str, width: i128) -> Vec<String> {
    if t.is_empty() {
        return Vec::new();
    }
    wrap(&format!("{label}{t}"), width, "    ", "      ")
}

/// `_wrap` of a row's value: nothing where it is false, its `str()` otherwise.
fn para_of(label: &str, v: Option<&Value>, width: i128) -> Vec<String> {
    if !truthy(v) {
        return Vec::new();
    }
    para(label, &v.map_or_else(String::new, py_str), width)
}

/// A row's trigger as (check, subject): `round:modal-form|modal:sheet/kitchen@3` -> (`modal-form`, `sheet/kitchen`), `red-gate@<utc>`
/// -> (`red-gate`, `<utc>`), a reversal -> its file's name; an accepted finding is its own subject.
fn subject(r: &Value) -> R<(String, String)> {
    let trigger = get(r, "trigger")?;
    let t = if truthy(trigger) {
        trigger.map_or_else(String::new, py_str)
    } else {
        String::new()
    };
    if t.is_empty() {
        return Ok((String::new(), text(r, "finding")?));
    }
    if let Some(m) = caps(&ROUND, &t) {
        return Ok((m[1].clone(), m[2].clone()));
    }
    if let Some(m) = caps(&KIND_AT, &t) {
        let s = if m[1] == "reversal" {
            m[2].rsplit('/').next().unwrap_or_default().to_owned()
        } else {
            m[2].clone()
        };
        return Ok((m[1].clone(), s));
    }
    Ok((String::new(), t))
}

/// `" ".join(x for x in _subject(r) if x)`.
fn subject_line(r: &Value) -> R<String> {
    let (a, b) = subject(r)?;
    Ok([a, b]
        .into_iter()
        .filter(|x| !x.is_empty())
        .collect::<Vec<_>>()
        .join(" "))
}

/// Row numbers as runs: [0, 1, 2, 5] -> `0-2,5`.
fn ids(ids: &[usize]) -> String {
    let mut runs: Vec<(usize, usize)> = Vec::new();
    for &i in ids {
        match runs.last_mut() {
            Some(run) if i == run.1 + 1 => run.1 = i,
            _ => runs.push((i, i)),
        }
    }
    runs.iter()
        .map(|(a, b)| {
            if a == b {
                a.to_string()
            } else {
                format!("{a}-{b}")
            }
        })
        .collect::<Vec<_>>()
        .join(",")
}

type Open = Vec<(PathBuf, Vec<(usize, Value)>)>;

/// Rows sharing one reason: (the ruling, the why or the fix) and the rows.
type Group<'a> = ((Value, Value), Vec<&'a (usize, Value)>);

/// `sorted((root / "specs").glob("*/"))`: every directory, hidden ones and links to one included.
fn spec_dirs(root: &Path) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = std::fs::read_dir(root.join("specs"))
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter(|p| p.is_dir())
        .collect();
    out.sort();
    out
}

/// Each feature with rows the GM has not reviewed, and those rows with their numbers (OVERTURN= takes the number).
pub(super) fn open_rows(root: &Path) -> R<Open> {
    let mut out = Vec::new();
    for d in spec_dirs(root) {
        let mut o = Vec::new();
        for (i, r) in rows(&d)?.into_iter().enumerate() {
            if !has(&r, "reviewed")? {
                o.push((i, r));
            }
        }
        if !o.is_empty() {
            out.push((d, o));
        }
    }
    Ok(out)
}

/// Every open question of `status` (owed or kept), by feature and row.
fn questions(root: &Path, status: &str) -> R<Vec<(PathBuf, usize, Value)>> {
    let mut out = Vec::new();
    for (d, o) in open_rows(root)? {
        for (i, r) in o {
            if is(&r, "kind", QUESTION)? && is(&r, "status", status)? {
                out.push((d.clone(), i, r));
            }
        }
    }
    Ok(out)
}

/// `r.get(key) == want`.
fn is(r: &Value, key: &str, want: &str) -> R<bool> {
    Ok(get(r, key)?.and_then(Value::as_str) == Some(want))
}

/// `r.get("kind", "")`, the value a row's kind is grouped by.
fn kind_of(r: &Value) -> R<Value> {
    Ok(get(r, "kind")?
        .cloned()
        .unwrap_or_else(|| Value::String(String::new())))
}

/// The kinds of `o` in the order `KINDS` gives, any other after them (the Python's tie among those was its set's order; here, by name).
fn kinds(o: &[(usize, Value)]) -> R<Vec<Value>> {
    let mut ks: Vec<Value> = Vec::new();
    for (_, r) in o {
        let k = kind_of(r)?;
        if !ks.contains(&k) {
            ks.push(k);
        }
    }
    let rank = |k: &Value| {
        KINDS
            .iter()
            .position(|(n, _, _)| Some(*n) == k.as_str())
            .unwrap_or(99)
    };
    ks.sort_by(|a, b| {
        rank(a)
            .cmp(&rank(b))
            .then_with(|| py_str(a).cmp(&py_str(b)))
    });
    Ok(ks)
}

fn kind_word(k: &Value, which: usize) -> String {
    KINDS
        .iter()
        .find(|(n, _, _)| Some(*n) == k.as_str())
        .map_or_else(
            || py_str(k),
            |row| if which == 1 { row.1 } else { row.2 }.to_owned(),
        )
}

/// `49 rulings (2 continue), 34 fixes made` - the feature's rows by kind; a ruling other than accept is counted by verdict.
fn counts(o: &[(usize, Value)]) -> R<String> {
    let mut parts = Vec::new();
    for kind in kinds(o)? {
        let mut of = Vec::new();
        for (_, r) in o {
            if kind_of(r)? == kind {
                of.push(r);
            }
        }
        let mut verdicts: Vec<(Value, usize)> = Vec::new();
        for r in &of {
            let v = get(r, "ruling")?
                .cloned()
                .unwrap_or_else(|| Value::String(String::new()));
            match verdicts.iter_mut().find(|(k, _)| *k == v) {
                Some(slot) => slot.1 += 1,
                None => verdicts.push((v, 1)),
            }
        }
        verdicts.sort_by(|a, b| b.1.cmp(&a.1));
        let by = if kind.as_str() == Some("arbiter") {
            verdicts
                .iter()
                .filter(|(v, _)| v.as_str() != Some("accept"))
                .map(|(v, n)| format!("{n} {}", py_str(v)))
                .collect::<Vec<_>>()
                .join(", ")
        } else {
            String::new()
        };
        let by = if by.is_empty() {
            by
        } else {
            format!(" ({by})")
        };
        parts.push(format!("{} {}{by}", of.len(), kind_word(&kind, 2)));
    }
    Ok(parts.join(", "))
}

/// One feature's rows by kind; rows sharing one reason are one line naming every subject.
fn detail(d: &Path, o: &[(usize, Value)], width: i128) -> R<Vec<String>> {
    let mut out = vec![format!("{}: {} row(s) - {}", name(d), o.len(), counts(o)?)];
    for kind in kinds(o)? {
        out.extend([String::new(), format!("  {}", kind_word(&kind, 1))]);
        let mut groups: Vec<Group> = Vec::new();
        for row in o {
            if kind_of(&row.1)? != kind {
                continue;
            }
            let ruling = get(&row.1, "ruling")?
                .cloned()
                .unwrap_or_else(|| Value::String(String::new()));
            let key = (
                ruling,
                super::first_truthy(&row.1, &["why", "tooling_fix"])?,
            );
            match groups.iter_mut().find(|(k, _)| *k == key) {
                Some(g) => g.1.push(row),
                None => groups.push((key, vec![row])),
            }
        }
        for ((verdict, why), g) in groups {
            let mut subjects: Vec<String> = Vec::new();
            for (_, r) in &g {
                let s = subject_line(r)?;
                if !subjects.contains(&s) {
                    subjects.push(s);
                }
            }
            subjects.sort();
            let verdict = if truthy(Some(&verdict)) {
                format!("{}: ", py_str(&verdict))
            } else {
                String::new()
            };
            let numbers: Vec<usize> = g.iter().map(|(i, _)| *i).collect();
            out.push(fit(
                &format!("    [{}] {verdict}{}", ids(&numbers), subjects.join("; ")),
                width,
            ));
            if truthy(Some(&why)) {
                out.push(fit(&format!("        {}", py_str(&why)), width));
            }
        }
    }
    Ok(out)
}

/// The rows of 328's ranking held behind another row (`Held behind ...`), which wait on other work (`full`: the whole flag, and the
/// fix it would make). A ranking row's own "Held" flag or `held` key is NOT a decision of the GM's: those come only from the questions
/// escalation-check kept (feature 432, FR-004).
fn held(root: &Path, full: bool) -> R<Vec<String>> {
    let f = root.join(HELD);
    let load = |p: &Path| -> R<Value> {
        if !p.is_file() {
            return Ok(Value::Object(Map::new()));
        }
        serde_json::from_str(&read_text(p)?).map_err(|e| Raised::Refused(e.to_string()))
    };
    let data = load(&f)?;
    // a row the ranking closed (`audit/waves.json`, the wave that closed it) waits on nothing, whatever its flag still says: the tubs row
    // stayed "Held behind" after 374's wave 115 closed it and the row it waited on (the GM, 2026-10-12)
    let closed = load(&f.with_file_name("waves.json"))?;
    let Value::Object(data) = data else {
        return Err(Raised::Trace(
            "AttributeError: object has no attribute 'items'".to_owned(),
        ));
    };
    let mut keys: Vec<&String> = Vec::new();
    for k in data.keys() {
        if !has(&closed, k)? {
            keys.push(k);
        }
    }
    keys.sort();
    let mut out = Vec::new();
    for k in keys {
        let v = &data[k];
        let flag = text(v, "flag")?;
        if !flag.starts_with("Held behind") {
            continue;
        }
        let fix = get(v, "fix")?;
        let mut line = format!("{k}: {}", if full { flag } else { head(&flag, 160) });
        if full && truthy(fix) {
            let _ = write!(
                line,
                ". The fix it would make: {}.",
                fix.map_or_else(String::new, py_str)
            );
        }
        out.push(line);
    }
    Ok(out)
}

/// `listing`: the whole queue, or one feature's rows.
pub(super) fn listing(ctx: &Ctx, feat: &str) -> R<String> {
    let width = i128::try_from((ctx.columns)(140).max(80)).unwrap_or(i128::MAX);
    let features = open_rows(ctx.root)?;
    if !feat.is_empty() {
        let d = feature(ctx.root, feat)?;
        let o = features
            .into_iter()
            .find(|(f, _)| *f == d)
            .map(|(_, o)| o)
            .unwrap_or_default();
        if o.is_empty() {
            return Ok(format!(
                "gm-review: nothing of {} waits on the GM\n",
                name(&d)
            ));
        }
        let mut out = detail(&d, &o, width)?;
        let n = num(&d)?;
        out.extend([
            String::new(),
            format!("  reviewed:     make gm-reviewed F={n}"),
            format!("  overturn one: make gm-reviewed F={n} OVERTURN=<row> TO=<feature>"),
        ]);
        return Ok(out.join("\n") + "\n");
    }
    let hs = held(ctx.root, false)?;
    let (kept, owed) = (questions(ctx.root, "kept")?, questions(ctx.root, "owed")?);
    let mut rest: Open = Vec::new();
    for (d, o) in features {
        let mut keep = Vec::new();
        for (i, r) in o {
            if !is(&r, "kind", QUESTION)? {
                keep.push((i, r));
            }
        }
        if !keep.is_empty() {
            rest.push((d, keep));
        }
    }
    if hs.is_empty() && rest.is_empty() && kept.is_empty() && owed.is_empty() {
        return Ok("gm-review: nothing waits on the GM\n".to_owned());
    }
    let n: usize = rest.iter().map(|(_, o)| o.len()).sum();
    let mut out = vec![
        format!(
            "GM REVIEW - {} decision(s) for the GM, {} question(s) owed escalation-check, {} waiting on other work, {n} landed row(s) to review in {} feature(s)",
            kept.len(),
            owed.len(),
            hs.len(),
            rest.len()
        ),
        String::new(),
    ];
    for (title, group) in [
        ("NEEDS YOUR DECISION - the questions escalation-check kept (feature 432)", &kept),
        ("OWED ESCALATION-CHECK - the session's, not the GM's: judge each, then make gm-escalated F=<n> ROW=<n> VERDICT=KEEP|CUT REASON=\"...\"", &owed),
    ] {
        if group.is_empty() {
            continue;
        }
        out.push(title.to_owned());
        for (d, i, r) in group {
            out.push(fit(&format!("  * {}#{i}: {}", num(d)?, text(r, "question")?), width));
        }
        out.push(String::new());
    }
    if !hs.is_empty() {
        out.push(
            "WAITING ON OTHER WORK - held in the ranking behind another row, not on the GM"
                .to_owned(),
        );
        for h in &hs {
            let (key, flag) = h.split_once(": ").unwrap_or((h, ""));
            out.push(fit(&format!("  * {key}"), width));
            out.push(fit(
                &format!("      {}", HELD_BEHIND.replace(flag, "waits on ")),
                width,
            ));
        }
        out.push(String::new());
    }
    if !rest.is_empty() {
        out.extend(to_review(&rest, kept.len(), width)?);
    }
    Ok(out.join("\n") + "\n")
}

/// The TO REVIEW block: each feature's landed rows counted, then what to run.
fn to_review(rest: &Open, kept: usize, width: i128) -> R<Vec<String>> {
    let mut out = vec!["TO REVIEW - landed; the GM may overturn any row".to_owned()];
    let mut declined = 0;
    for (d, o) in rest {
        let f = num(d)?;
        let nm = name(d);
        let after = nm
            .split_once('-')
            .map(|(_, b)| b.to_owned())
            .ok_or_else(|| Raised::Trace("IndexError: list index out of range".to_owned()))?;
        let label = format!("{:<40}", fit(&after, 40));
        out.push(fit(
            &format!("  {f:>3}  {label} {:>3}  {}", o.len(), counts(o)?),
            width,
        ));
        for (_, r) in o {
            declined += usize::from(is(r, "kind", "arbiter-fix-declined")?);
        }
    }
    out.extend([
        String::new(),
        format!("  needs a decision: {kept} question(s), {declined} fix(es) declined to the GM - in full: make gm-review EXPLAIN=1"),
        "  a feature's rows:  make gm-review F=NNN   (each in full: add EXPLAIN=1, one row: ROW=n)".to_owned(),
        "  reviewed:          make gm-reviewed F=NNN   (agreed in discussion with the GM: add WORDS=\"<his words>\")".to_owned(),
    ]);
    Ok(out)
}

/// What a check judges, from its agent file's description (the text before ` - run`).
fn check_says(root: &Path, check: &str) -> R<String> {
    let f = root
        .join(".claude")
        .join("agents")
        .join(format!("{check}.md"));
    if !f.is_file() {
        return Ok(String::new());
    }
    let t = read_text(&f)?;
    Ok(caps(&DESCRIPTION, &t).map_or_else(String::new, |m| {
        let said = m[1].split(" - run").next().unwrap_or_default();
        strip(said).trim_end_matches('.').to_owned()
    }))
}

/// The file a trigger's subject lives in: a research question's page, a pop-up's write-up, a reversal's file.
fn where_(root: &Path, trigger: &str) -> String {
    if let Some(m) = caps(&Q_PAGE, trigger) {
        let mut pages: Vec<PathBuf> = std::fs::read_dir(root.join("research").join("questions"))
            .into_iter()
            .flatten()
            .flatten()
            .map(|e| e.path())
            .filter(|p| {
                let n = name(p);
                n.starts_with(&format!("{}-", m[1]))
                    && Path::new(&n).extension().is_some_and(|e| e == "html")
                    && n.matches('.').count() == 1
            })
            .collect();
        pages.sort();
        return pages
            .first()
            .and_then(|p| p.strip_prefix(root).ok())
            .map_or_else(String::new, |p| p.to_string_lossy().into_owned());
    }
    if let Some(m) = caps(&MODAL, trigger) {
        return format!("l7r/diagram/interactive/assets/modals/{}.md", m[1]);
    }
    trigger
        .strip_prefix("reversal:")
        .map_or_else(String::new, |rest| {
            let tail = rest.split_once("/.clones/").map_or(rest, |(_, b)| b);
            tail.split_once('/').map_or(tail, |(_, b)| b).to_owned()
        })
}

/// What fired the ruling, in plain words.
fn happened(root: &Path, r: &Value) -> R<String> {
    let (t, asked) = (text(r, "trigger")?, text(r, "asked")?);
    let tail = if asked.is_empty() {
        String::new()
    } else {
        format!(" As it fired: {asked}")
    };
    if let Some(m) = caps(&ROUND, &t) {
        let says = check_says(root, &m[1])?;
        let says = says.chars().next().map_or_else(String::new, |c| {
            format!(" ({}{})", c.to_lowercase(), &says[c.len_utf8()..])
        });
        let round = if m[3].is_empty() { "3" } else { &m[3] };
        return Ok(format!(
            "The {} check{says} was owed a round {round} on {}. Three rounds on one thing can mean a loop, so the round arbiter rules before the third runs.{tail}",
            m[1], m[2]
        ));
    }
    let kind = t.split([':', '@']).next().unwrap_or_default();
    let said = match kind {
        "reversal" => "An edit put back text that an earlier edit of the same file in this feature had replaced (A -> B -> A): checks may be pulling the text two ways.".to_owned(),
        "red-gate" => "`make done` went red twice in a row: the arbiter rules on whether the session is stuck.".to_owned(),
        "cascade" => "Checks were dispatched faster than one per changed line: reviews may be triggering reviews.".to_owned(),
        "ask" => "The session put a process question to the round arbiter instead of to the GM.".to_owned(),
        _ => format!("Trigger {t}."),
    };
    Ok(said + &tail)
}

/// The lines of one tooling fix and its fate.
fn fix_lines(i: usize, fx: &Value, width: i128, f: i128) -> R<Vec<String>> {
    let kind = text(fx, "kind")?;
    let status = kind.strip_prefix("arbiter-fix-").unwrap_or(&kind);
    let mut out = vec![format!(
        "    [{i}] the tooling fix: {}",
        status.to_uppercase()
    )];
    out.extend(para_of(
        if status == "done" {
            "Done: "
        } else {
            "Declined because: "
        },
        get(fx, "note")?,
        width,
    ));
    out.extend(para_of("Test: ", get(fx, "test")?, width));
    if status == "declined" {
        out.extend(para(
            "YOUR DECISION: ",
            &format!("should this fix be made after all? Mark it reviewed (make gm-reviewed F={f}) to leave it declined, or OVERTURN={i} TO=<an open feature> to have it built."),
            width,
        ));
    }
    Ok(out)
}

fn explain_row(
    root: &Path,
    f: i128,
    i: usize,
    r: &Value,
    fixes: &[(usize, Value)],
    width: i128,
) -> R<Vec<String>> {
    let (check, subj) = subject(r)?;
    let utc = match get(r, "utc")? {
        None => String::new(),
        Some(Value::String(u)) => head(u, 16).replace('T', " "),
        // `r.get('utc', '')[:16].replace(...)`: a time that is no string raised
        Some(other) => {
            return Err(Raised::Trace(format!(
                "TypeError: cannot slice {}",
                py_str(other)
            )))
        }
    };
    let mut out = vec![fit(
        &format!("{} - {utc} UTC", rstrip(&format!("[{i}] {check} {subj}"))),
        width,
    )];
    if is(r, "kind", "accepted")? {
        out.extend(para(
            "A session accepted this finding without fixing it: ",
            &text(r, "finding")?,
            width,
        ));
        out.extend(para("Its reason: ", &text(r, "why")?, width));
    } else {
        out.extend(para("What happened: ", &happened(root, r)?, width));
        out.extend(para("Where: ", &where_(root, &text(r, "trigger")?), width));
        let ruling = text(r, "ruling")?;
        let ruling_value = get(r, "ruling")?;
        let ruled = if ruling_value.and_then(Value::as_str) == Some("continue")
            && !text(r, "trigger")?.starts_with("round:")
        {
            // no round to add: work goes on
            "CONTINUE - nothing is stuck; the work carries on as it was".to_owned()
        } else {
            VERDICTS
                .iter()
                .find(|(k, _)| *k == ruling)
                .map_or(ruling.clone(), |(_, v)| (*v).to_owned())
        };
        out.extend(para("The arbiter ruled: ", &ruled, width));
        out.extend(para("Why: ", &text(r, "why")?, width));
        out.extend(para("It set the next step: ", &text(r, "what")?, width));
        out.extend(para(
            "It asked for a tooling fix: ",
            &text(r, "tooling_fix")?,
            width,
        ));
    }
    for (j, fx) in fixes {
        out.extend(fix_lines(*j, fx, width, f)?);
    }
    let mut declined = false;
    for (_, fx) in fixes {
        declined |= is(fx, "kind", "arbiter-fix-declined")?;
    }
    if !declined {
        out.extend(para(
            "Your call: ",
            &format!("nothing to do if you agree. To overturn: make gm-reviewed F={f} OVERTURN={i} TO=<an open feature> (it becomes open work there)."),
            width,
        ));
    }
    out.push(String::new());
    Ok(out)
}

/// The arbiter's own record of each ruling (`arbiter.jsonl`: the next step, the question as fired), by trigger and time.
fn detail_of(d: &Path) -> R<Vec<((Value, Value), Value)>> {
    let f = d.join("arbiter.jsonl");
    let mut out: Vec<((Value, Value), Value)> = Vec::new();
    if !f.is_file() {
        return Ok(out);
    }
    for l in crate::record::py_lines(&read_text(&f)?) {
        let Ok(a) = serde_json::from_str::<Value>(l) else {
            continue;
        };
        let key = (
            get(&a, "trigger")?
                .cloned()
                .unwrap_or_else(|| Value::String(String::new())),
            get(&a, "utc")?
                .cloned()
                .unwrap_or_else(|| Value::String(String::new())),
        );
        match out.iter_mut().find(|(k, _)| *k == key) {
            Some(slot) => slot.1 = a,
            None => out.push((key, a)),
        }
    }
    Ok(out)
}

/// `explain`: each open row in full: what fired it, what the arbiter ruled and why, the tooling fix and its fate, and what the GM is
/// asked. With no feature: only what NEEDS the GM - the held questions and the fixes declined to him.
pub(super) fn explain(ctx: &Ctx, feat: &str, row: &str) -> R<String> {
    let width = i128::try_from((ctx.columns)(110).min(110)).unwrap_or(110);
    if feat.is_empty() {
        return needs_you(ctx.root, width);
    }
    let d = feature(ctx.root, feat)?;
    let o = open_rows(ctx.root)?
        .into_iter()
        .find(|(f, _)| *f == d)
        .map(|(_, o)| o)
        .unwrap_or_default();
    if o.is_empty() {
        return Ok(format!(
            "gm-review: nothing of {} waits on the GM\n",
            name(&d)
        ));
    }
    let extra = detail_of(&d)?;
    let mut rows_in = Vec::new();
    for (i, r) in o {
        let key = (
            get(&r, "trigger")?
                .cloned()
                .unwrap_or_else(|| Value::String(String::new())),
            get(&r, "utc")?
                .cloned()
                .unwrap_or_else(|| Value::String(String::new())),
        );
        let base = extra
            .iter()
            .find(|(k, _)| *k == key)
            .map_or_else(|| Value::Object(Map::new()), |(_, a)| a.clone());
        let pairs: Vec<(String, Value)> = r
            .as_object()
            .into_iter()
            .flatten()
            .map(|(k, v)| (k.clone(), v.clone()))
            .collect();
        let refs: Vec<(&str, Value)> = pairs.iter().map(|(k, v)| (k.as_str(), v.clone())).collect();
        rows_in.push((i, super::merged(&base, &refs)?));
    }
    let o = rows_in;
    // the feature's number is asked only where a row is shown, as the Python's `_num(d)` was
    let f = || num(&d);
    let (fixes, rulings): (Vec<_>, Vec<_>) = o
        .iter()
        .cloned()
        .partition(|(_, r)| text(r, "kind").is_ok_and(|k| k.starts_with("arbiter-fix-")));
    let mut out = wrap(
        &format!("{}: {} row(s) - {}", name(&d), o.len(), counts(&o)?),
        width,
        "",
        "  ",
    );
    out.push(String::new());
    let start = out.len();
    let mut shown: Vec<usize> = Vec::new();
    for (i, r) in &rulings {
        let trig = get(r, "trigger")?;
        let mut mine = Vec::new();
        for (j, fx) in &fixes {
            let ft = get(fx, "trigger")?;
            if truthy(ft) && ft == trig {
                mine.push((*j, fx.clone()));
            }
        }
        if row.is_empty() || row == i.to_string() || mine.iter().any(|(j, _)| row == j.to_string())
        {
            out.extend(explain_row(ctx.root, f()?, *i, r, &mine, width)?);
        }
        shown.extend(mine.iter().map(|(j, _)| *j));
    }
    for (j, fx) in &fixes {
        if !shown.contains(j) && (row.is_empty() || row == j.to_string()) {
            out.push(fit(&format!("[{j}] {}", subject_line(fx)?), width));
            out.extend(para_of(
                "The fix asked for: ",
                get(fx, "tooling_fix")?,
                width,
            ));
            out.extend(fix_lines(*j, fx, width, f()?)?);
            out.push(String::new());
        }
    }
    Ok(if out.len() > start {
        out.join("\n") + "\n"
    } else {
        format!("gm-review: no open row {row} in {}\n", name(&d))
    })
}

/// `_needs_you`: the questions kept for the GM, the fixes declined to him, then what waits on other work.
fn needs_you(root: &Path, width: i128) -> R<String> {
    let waits = held(root, true)?;
    let asks = questions(root, "kept")?;
    let open = open_rows(root)?;
    let mut declined = Vec::new();
    for (d, o) in &open {
        for (i, r) in o {
            if is(r, "kind", "arbiter-fix-declined")? {
                declined.push((d.clone(), *i, r.clone()));
            }
        }
    }
    let none = if asks.is_empty() && declined.is_empty() {
        ": nothing - no question kept for you and no fix declined to you"
    } else {
        ""
    };
    let mut out = vec![format!("WHAT NEEDS YOUR DECISION{none}"), String::new()];
    for (n, (d, i, r)) in asks.iter().enumerate() {
        let f = num(d)?;
        out.push(fit(
            &format!("{}. QUESTION {f}#{i} ({})", n + 1, name(d)),
            width,
        ));
        out.extend(para("", &text(r, "question")?, width));
        out.extend(para(
            "Why it is yours (escalation-check): ",
            &text(r, "escalation")?,
            width,
        ));
        out.extend(para(
            "Answered: ",
            &format!("make gm-reviewed F={f} ROW={i} WORDS=\"<your answer>\""),
            width,
        ));
        out.push(String::new());
    }
    for (n, (d, i, r)) in declined.iter().enumerate() {
        let f = num(d)?;
        out.push(fit(
            &format!(
                "{}. A TOOLING FIX DECLINED TO YOU: feature {f} row [{i}], {}",
                n + 1 + asks.len(),
                subject_line(r)?
            ),
            width,
        ));
        out.extend(para_of(
            "The arbiter asked: ",
            get(r, "tooling_fix")?,
            width,
        ));
        out.extend(para_of("Declined because: ", get(r, "note")?, width));
        out.extend(para(
            "Decide: ",
            &format!("leave it declined (make gm-reviewed F={f}) or have it built (make gm-reviewed F={f} OVERTURN={i} TO=<an open feature>)."),
            width,
        ));
        out.push(String::new());
    }
    if !waits.is_empty() {
        out.extend([
            "WAITING ON OTHER WORK - held in the ranking until another row is done; nothing for you to decide".to_owned(),
            String::new(),
        ]);
        for h in &waits {
            let (key, flag) = h.split_once(": ").unwrap_or((h, ""));
            out.push(fit(&format!("  * {key}"), width));
            out.extend(para("", &HELD_PLAIN.replace(flag, "Waits on "), width));
            out.push(String::new());
        }
    }
    let total: usize = open.iter().map(|(_, o)| o.len()).sum();
    let owed = questions(root, "owed")?.len();
    let rest = i128::try_from(total).unwrap_or(0)
        - i128::try_from(declined.len() + asks.len() + owed).unwrap_or(0);
    out.extend(wrap(
        &format!("The other {rest} row(s) are decisions already made that you may overturn; nothing waits on them. Each in full: make gm-review F=NNN EXPLAIN=1 [ROW=n]."),
        width,
        "",
        "",
    ));
    Ok(out.join("\n") + "\n")
}

#[cfg(test)]
mod tests;
