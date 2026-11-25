//! The answer modes' command line and the findings a reply files outside the change (split from `answers.rs` at the 1,000-line bar,
//! feature 451 T38): `run` (the listing, `--answer`, `--fixed-by`) and `file_outside`.

use super::*;

/// A line saying its section is empty: `None.`, `none (every block and note is listed under THE CHANGE).` - never `None of the
/// pages ...`, a note's own words (the forms read 2026-11-25 over the saved replies under `/tmp` and P7's cascade).
static NONE: LazyLock<Regex> = LazyLock::new(|| re(r"^(?i)none\s*(?:$|[.:(,;-])"));

/// One line under a reply's `OUTSIDE THE CHANGE` or `NOTED, NOT FILED` heading: its (file, block, finding) where it takes the row
/// form, else its bare words; and whether it may be filed - an OUTSIDE line may, a NOTED one never (the check chose; 451 T229).
struct Note {
    row: Option<(String, String, String)>,
    bare: String,
    may_file: bool,
}

/// Every line under the reply's `OUTSIDE THE CHANGE` and `NOTED, NOT FILED` headings (feature 451 T229, which read the second and
/// a prose line: P7's cascade's two notes were one of each, and neither was echoed). A section ends at any other `#` heading, a
/// `---` rule, or a prose line after a blank one - a closing paragraph, not a note; a bullet after a blank line is still its own.
fn outside(reply: &str) -> Vec<Note> {
    let (mut under, mut broke, mut seen) = (None, false, false);
    let mut notes = Vec::new();
    for line in crate::record::py_lines(reply) {
        let open = |r: &Regex| r.is_match(line).unwrap_or(false);
        if open(&OUTSIDE) || open(&NOTED) {
            (under, broke, seen) = (Some(open(&OUTSIDE)), false, false);
            continue;
        }
        let Some(may_file) = under else { continue };
        let t = line.trim();
        let bullet = t.starts_with("- ") || t.starts_with("* ");
        if t.starts_with('#') || t.starts_with("---") || (broke && !bullet && !t.is_empty()) {
            under = None;
            continue;
        }
        if t.is_empty() {
            broke = seen;
            continue;
        }
        seen = true;
        let row = ROW.captures(line).ok().flatten().map(|r| {
            (
                l7r_shared::py_text::strip(&r[1]).to_owned(),
                r[2].to_owned(),
                r[3].to_owned(),
            )
        });
        let bare = if bullet { &t[2..] } else { t }.trim().to_owned();
        // `None.`, `none (every block ... is listed)`: the section says it is empty, the common form, and is no note - its
        // paragraph still ends the section, so a `Files:` list after it is never read as notes
        if NONE.is_match(&bare).unwrap_or(false) {
            continue;
        }
        notes.push(Note {
            row,
            bare,
            may_file,
        });
    }
    notes
}

/// What a reply's `OUTSIDE THE CHANGE` lines came to (feature 451 T219): the rows filed, each naming the wrong outcome a reader of
/// the map, the sheet or the page, or the user of a tool, would meet, and the lines naming none, listed and dropped - with the
/// `NOTED, NOT FILED` lines, each kept in the feature's `noted.jsonl` (`kept`, the file, where any was listed; 451 T229).
#[derive(Debug, Default)]
pub struct Outside {
    pub filed: Vec<Map<String, Value>>,
    pub dropped: Vec<String>,
    pub kept: Option<String>,
}

impl Outside {
    /// What `make <cmd>` says of them: each row filed, each line dropped, and the form a filed line takes.
    #[must_use]
    pub fn said(&self, cmd: &str) -> String {
        let mut out = String::new();
        for row in &self.filed {
            let text = |k: &str| row.get(k).and_then(Value::as_str).unwrap_or("");
            let _ = writeln!(
                out,
                "{cmd}: filed, not fixed - {} | {} | {} | effect: {}",
                text("file"),
                text("block"),
                text("finding"),
                text("effect")
            );
        }
        for line in &self.dropped {
            let _ = writeln!(out, "{cmd}: listed, not filed - {line}");
        }
        if !self.dropped.is_empty() {
            let _ = writeln!(
                out,
                "{cmd}: a note outside the change is filed only where it ends `| {}` (451 T219); the rest are listed, not filed, and kept in {} (451 T229)",
                crate::record::effect::FORM,
                self.kept.as_deref().unwrap_or("no file")
            );
        }
        out
    }
}

/// Keep each listed note in the feature's `noted.jsonl` (feature 451 T229), beside `found.jsonl` and never in it: a found row is open
/// work, which T219 took away from these. A note already kept for the same check, unit and words is not written again - a reply is
/// recorded again after a refused line or a hold. The file's path from the root, or none where nothing was listed.
fn keep_noted(root: &Rooted, rows: &[Value]) -> Result<Option<String>, Fail> {
    if rows.is_empty() {
        return Ok(None);
    }
    let dir = checks::arbiter::feature_dir_in(root, "", root.reader())
        .unwrap_or_else(|| root.join("specs/_unfiled"));
    let target = dir.join("noted.jsonl");
    let had = std::fs::read_to_string(&target).unwrap_or_default();
    let same = |a: &Value, b: &Value| {
        ["check", "file", "block", "units", "note"]
            .iter()
            .all(|k| a.get(k) == b.get(k))
    };
    let old: Vec<Value> = had
        .lines()
        .filter_map(|l| serde_json::from_str(l).ok())
        .collect();
    let mut body = String::new();
    for row in rows.iter().filter(|r| !old.iter().any(|o| same(o, r))) {
        body.push_str(&pyjson::dumps(row, None, false));
        body.push('\n');
    }
    std::fs::create_dir_all(&dir).map_err(fail)?;
    std::io::Write::write_all(
        &mut std::fs::OpenOptions::new()
            .append(true)
            .create(true)
            .open(&target)
            .map_err(fail)?,
        body.as_bytes(),
    )
    .map_err(fail)?;
    let shown = target.strip_prefix(root.path()).unwrap_or(&target);
    Ok(Some(shown.display().to_string()))
}

/// Append a reply's OUTSIDE THE CHANGE findings to the active feature's `found.jsonl` as open rows.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn file_outside(root: &Path, check: &str, reply: &str, units: &str) -> Result<Outside, Fail> {
    file_outside_with(&Rooted::process(root), check, reply, units)
}

/// [`file_outside_with`] naming no units: a note in no row form is listed as the check's reply's.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn file_outside_in(root: &Rooted, check: &str, reply: &str) -> Result<Outside, Fail> {
    file_outside_with(root, check, reply, "")
}

/// [`file_outside`] with the root's environment carried (feature 451 T38): the active feature read through it. `units` are the
/// reply's units, which a listed note naming no file and block is printed and kept with (451 T229).
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn file_outside_with(
    root: &Rooted,
    check: &str,
    reply: &str,
    units: &str,
) -> Result<Outside, Fail> {
    let mut out = Outside::default();
    let mut body = String::new();
    let mut noted = Vec::new();
    let utc = utc_now();
    // the check's words in the house style a JSON record takes (feature 449 T242): found.jsonl is no prose file to the push's
    // delta check, so a straight-quoted word is corrected too; its file and block name things and are written as given
    let style = l7r_shared::guards::house_style_hooks::americanize_record;
    let units = if units.is_empty() {
        format!("{check}'s reply, no unit named")
    } else {
        units.to_owned()
    };
    for note in outside(reply) {
        // a note is filed only where it names the wrong outcome its reader or user meets (feature 451 T219); `effect: none` names none
        let named = note
            .row
            .as_ref()
            .filter(|_| note.may_file)
            .and_then(|(_, _, f)| crate::record::effect::named(f));
        let (Some((file, block, _)), Some((finding, effect))) = (&note.row, named) else {
            let (line, row) = match &note.row {
                Some((file, block, finding)) => (
                    format!("{file} | {block} | {finding}"),
                    json!({"check": check, "file": file, "block": block, "note": style(finding), "utc": utc}),
                ),
                None => (
                    format!("{units} | {}", note.bare),
                    json!({"check": check, "units": units, "note": style(&note.bare), "utc": utc}),
                ),
            };
            out.dropped.push(line);
            noted.push(row);
            continue;
        };
        let row = json!({"check": check, "file": file, "block": block, "finding": style(&finding), "effect": style(&effect), "status": "open", "utc": utc});
        body.push_str(&pyjson::dumps(&row, None, false));
        body.push('\n');
        out.filed.push(row.as_object().cloned().unwrap_or_default());
    }
    out.kept = keep_noted(root, &noted)?;
    if out.filed.is_empty() {
        return Ok(out);
    }
    let target = checks::arbiter::feature_dir_in(root, "", root.reader())
        .unwrap_or_else(|| root.join("specs/_unfiled"))
        .join("found.jsonl");
    std::fs::create_dir_all(target.parent().unwrap_or(root)).map_err(fail)?;
    std::io::Write::write_all(
        &mut std::fs::OpenOptions::new()
            .append(true)
            .create(true)
            .open(&target)
            .map_err(fail)?,
        body.as_bytes(),
    )
    .map_err(fail)?;
    Ok(out)
}

fn fail_line(code: i32, stderr: &str) -> Reply {
    Reply {
        stdout: String::new(),
        stderr: format!("{stderr}\n"),
        code,
    }
}

fn run_fixed(root: &Path, parsed: &Parsed) -> Result<Reply, Fail> {
    let (q, notes) = (parsed.text("--q", ""), parsed.text("--notes", ""));
    if parsed.text("--answer", "") != "quote-check" || q.is_empty() || notes.is_empty() {
        return Ok(fail_line(2, "record-checked: FIXED_BY= declares a fix of another check's finding on quote-check notes: CHECK=quote-check Q=<NNNN> NOTES=<k,k> FIXED_BY=\"<check>: <its finding>\""));
    }
    let (done, refused) = fixed_answer(root, q, notes, parsed.text("--fixed-by", ""))?;
    if !refused.is_empty() {
        return Ok(fail_line(
            2,
            &format!(
                "record-checked: REFUSED - the quotation or its claim changed, so quote-check is owed (feature 399): {} - check it: make check-bundle Q={} FOR=quote-check NOTES={notes}",
                refused.join(" "),
                zfill4(q)
            ),
        ));
    }
    if done.is_empty() {
        return Ok(fail_line(
            3,
            &format!("_record_owed: no owed quote-check unit on {notes} - nothing recorded"),
        ));
    }
    Ok(Reply {
        stdout: format!(
            "record-checked: {} unit(s) answered as another check's fix - {}\n",
            done.len(),
            done.join(" ")
        ),
        stderr: String::new(),
        code: 0,
    })
}

fn run_answer(root: &Rooted, parsed: &Parsed) -> Result<Reply, Fail> {
    let (check, result, bundle) = (
        parsed.text("--answer", ""),
        parsed.text("--result", ""),
        parsed.text("--bundle", ""),
    );
    if result.is_empty() {
        return Ok(fail_line(
            2,
            "_record_owed: --answer needs --result \"<the check's counts>\"",
        ));
    }
    let (notes, reason) = (parsed.text("--notes", ""), parsed.text("--reason", ""));
    let refusal = if bundle.is_empty() {
        bundle_less_refusal(check, notes, reason)
    } else {
        String::new()
    };
    if !refusal.is_empty() {
        return Ok(fail_line(
            2,
            &format!("record-checked: REFUSED - {refusal}"),
        ));
    }
    let reply_arg = parsed.text("--reply", "");
    let reply = if reply_arg.is_empty() {
        String::new()
    } else {
        reply_of(root, reply_arg)?
    };
    let named = Named {
        q: parsed.text("--q", ""),
        notes,
        key: parsed.text("--key", ""),
        kind: parsed.text("--kind", ""),
    };
    let done = answer(root, check, result, bundle, &named, &reply)?;
    let mut out = String::new();
    if !reply.is_empty() {
        out.push_str(
            &file_outside_with(root, check, &reply, &done.join(", "))?.said("record-checked"),
        );
    }
    if !done.is_empty() && bundle.is_empty() && !reason.is_empty() {
        bypass_log(
            root,
            "record-checked",
            &format!("{check} on {}: {reason}", done.join(" ")),
        )?;
    }
    if done.is_empty() {
        return Ok(Reply { stdout: out, stderr: format!("_record_owed: no owed {check} unit matched - nothing recorded (`make record-owed` lists what is owed)\n"), code: 3 });
    }
    let _ = writeln!(
        out,
        "record-checked: {} unit(s) answered - {}",
        done.len(),
        done.join(" ")
    );
    Ok(Reply {
        stdout: out,
        stderr: String::new(),
        code: 0,
    })
}

/// The command line's modes, past `--root`, the root's environment carried (feature 451 T38: `record-owed`'s `cli_in` hands it its own).
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn run_in(root: &Rooted, parsed: &Parsed) -> Result<Reply, Fail> {
    if !parsed.text("--answer", "").is_empty() && !parsed.text("--fixed-by", "").is_empty() {
        return run_fixed(root, parsed);
    }
    if !parsed.text("--answer", "").is_empty() {
        return run_answer(root, parsed);
    }
    listing(root, parsed)
}
