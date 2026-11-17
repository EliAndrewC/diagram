//! `l7r-gate record footnote-census` (`make footnote-census`; `tools/footnote_census.py`, feature 235; ported by feature 449 T148): the
//! record's footnotes counted BY KIND - the number that says what is owed (the GM, 2026-09-12: *"if we're counting things that are not
//! actually problems in a category that is meant to denote problems, then we're just gonna keep getting confused"*). Of the four columns
//! only ABSENT is a backlog; the classifier is the record's own ([`crate::citations::footnote_form`]).

use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;

use l7r_gate_core::record::args::parse;

use super::{said, usage, Run};
use crate::citations::{footnote_form, is_settled};
use crate::record::{contents, store};
use crate::sources::Reader;

/// The four kinds; anything else is `malformed`.
pub const KINDS: [&str; 4] = ["citation", "grounds", "absence", "settled"];

type Counts = BTreeMap<String, usize>;

/// The kind of every footnote among `bodies`.
#[must_use]
pub fn kinds_of(bodies: &[&str], canon: &BTreeSet<String>) -> Counts {
    let mut counted = Counts::new();
    for body in bodies {
        let mut kind = footnote_form(body, canon).unwrap_or_default();
        if kind == "absence" && is_settled(body) {
            "settled".clone_into(&mut kind);
        }
        let key = if KINDS.contains(&kind.as_str()) {
            kind
        } else {
            "malformed".to_owned()
        };
        *counted.entry(key).or_default() += 1;
    }
    counted
}

/// Per section of each half, in the rows' order, then the total.
///
/// # Errors
/// The record's refusal, or a page's notes'.
pub fn census(
    research: &Path,
    canon: &BTreeSet<String>,
) -> crate::Result<(Vec<(String, Counts)>, Counts)> {
    let record = store::load(research)?;
    let mut per: BTreeMap<String, Counts> = BTreeMap::new();
    let mut total = Counts::new();
    for page in record.pages(None) {
        let home = record.question_of(page).home.clone().unwrap_or_default();
        let titles: Vec<&str> = contents::path(&record.sections, &home)
            .iter()
            .map(|s| s.title.as_str())
            .collect();
        let row = format!("{}: {}", page.half(), titles.join(" / "));
        let notes = store::page_notes(&page.file, research)?;
        let bodies: Vec<&str> = notes.iter().map(|(_, b)| b.as_str()).collect();
        let counted = kinds_of(&bodies, canon);
        for (k, n) in counted {
            *per.entry(row.clone())
                .or_default()
                .entry(k.clone())
                .or_default() += n;
            *total.entry(k).or_default() += n;
        }
        per.entry(row).or_default();
    }
    Ok((per.into_iter().collect(), total))
}

fn width_pad(text: &str, width: usize) -> String {
    let n = text.chars().count();
    format!("{text}{}", " ".repeat(width.saturating_sub(n)))
}

/// The report, widest column first, with the backlog called what it is.
#[must_use]
pub fn render(rows: &[(String, Counts)], total: &Counts) -> String {
    let get = |c: &Counts, k: &str| c.get(k).copied().unwrap_or(0);
    let width = rows
        .iter()
        .map(|(n, _)| n.chars().count())
        .chain([5])
        .max()
        .unwrap_or(5);
    let head = format!(
        "{}  {:>6}{:>9}{:>8}{:>9}",
        width_pad("section", width),
        "cited",
        "grounds",
        "ABSENT",
        "settled"
    );
    let rule = "-".repeat(head.chars().count());
    let line = |name: &str, c: &Counts| {
        format!(
            "{}  {:>6}{:>9}{:>8}{:>9}",
            width_pad(name, width),
            get(c, "citation"),
            get(c, "grounds"),
            get(c, "absence"),
            get(c, "settled")
        )
    };
    let mut lines = vec![head.clone(), rule.clone()];
    lines.extend(rows.iter().map(|(n, c)| line(n, c)));
    lines.push(rule);
    lines.push(line("TOTAL", total));
    if get(total, "malformed") > 0 {
        lines.push(format!(
            "\nMALFORMED: {} footnote(s) match no form - the gate will name them",
            get(total, "malformed")
        ));
    }
    lines.push(format!(
        "\nThe backlog is ABSENT: {}. The other three columns owe nothing.",
        get(total, "absence")
    ));
    lines.join("\n")
}

/// The command, over the repository `tree`'s record.
///
/// # Errors
/// The record's or the registry's refusal, which the Python let through.
pub fn run(args: &[String], tree: &Path) -> Run {
    if let Err(complaint) = parse(args, &[]) {
        return Ok(usage("footnote-census", &complaint));
    }
    let research = tree.join("research");
    let canon = Reader::new(&research).canon_keys()?;
    let (rows, total) = census(&research, &canon)?;
    Ok(said(format!("{}\n", render(&rows, &total)), "", 0))
}

#[cfg(test)]
mod tests;
