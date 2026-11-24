//! The answer modes' command line and the findings a reply files outside the change (split from `answers.rs` at the 1,000-line bar,
//! feature 451 T38): `run` (the listing, `--answer`, `--fixed-by`) and `file_outside`.

use super::*;

/// (file, block, finding) of every line under a reply's `OUTSIDE THE CHANGE` heading.
fn outside(reply: &str) -> Vec<(String, String, String)> {
    let Ok(Some(m)) = OUTSIDE.find(reply) else {
        return Vec::new();
    };
    let mut rows = Vec::new();
    for line in crate::record::py_lines(&reply[m.end()..]) {
        if line.starts_with('#') {
            break;
        }
        if let Ok(Some(r)) = ROW.captures(line) {
            rows.push((
                l7r_shared::py_text::strip(&r[1]).to_owned(),
                r[2].to_owned(),
                r[3].to_owned(),
            ));
        }
    }
    rows
}

/// What a reply's `OUTSIDE THE CHANGE` lines came to (feature 451 T219): the rows filed, each naming the wrong outcome a reader of
/// the map, the sheet or the page, or the user of a tool, would meet, and the lines naming none, listed and dropped.
#[derive(Debug, Default)]
pub struct Outside {
    pub filed: Vec<Map<String, Value>>,
    pub dropped: Vec<String>,
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
                "{cmd}: a note outside the change is filed only where it ends `| {}` (451 T219); the rest are dropped",
                crate::record::effect::FORM
            );
        }
        out
    }
}

/// Append a reply's OUTSIDE THE CHANGE findings to the active feature's `found.jsonl` as open rows.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn file_outside(root: &Path, check: &str, reply: &str) -> Result<Outside, Fail> {
    file_outside_in(&Rooted::process(root), check, reply)
}

/// [`file_outside`] with the root's environment carried (feature 451 T38): the active feature read through it.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn file_outside_in(root: &Rooted, check: &str, reply: &str) -> Result<Outside, Fail> {
    let mut out = Outside::default();
    let mut body = String::new();
    let utc = utc_now();
    for (file, block, finding) in outside(reply) {
        // a note is filed only where it names the wrong outcome its reader or user meets (feature 451 T219); `effect: none` names none
        let Some((finding, effect)) = crate::record::effect::named(&finding) else {
            out.dropped.push(format!("{file} | {block} | {finding}"));
            continue;
        };
        // the check's finding in the house style a JSON record takes (feature 449 T242): found.jsonl is no prose file to the push's
        // delta check, so a straight-quoted word is corrected too; its file and block name things and are written as given
        let style = l7r_shared::guards::house_style_hooks::americanize_record;
        let row = json!({"check": check, "file": file, "block": block, "finding": style(&finding), "effect": style(&effect), "status": "open", "utc": utc});
        body.push_str(&pyjson::dumps(&row, None, false));
        body.push('\n');
        out.filed.push(row.as_object().cloned().unwrap_or_default());
    }
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
        out.push_str(&file_outside_in(root, check, &reply)?.said("record-checked"));
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
