//! `l7r-gate reviews owed`'s command line (split from `owed.rs` by feature 451 T164, past the 1,000-line bar): the modes, their
//! parse and the run that answers each.
//!
//! Research: plumbing - NONE: parses and dispatches the owed tool's modes, deciding nothing about a map

use std::fmt::Write as _;
use std::path::Path;

use l7r_shared::env::Rooted;

use super::super::{git, glyph, py_path, reply};
use super::{check_declared, check_drawn, folders, owed_discharged, ruling, undrawn, Unit};
use crate::record::args::{parse, Spec};
use crate::record::bundle::py_repr;
use crate::Reply;

const MODES: [&str; 8] = [
    "--why",
    "--units",
    "--undrawn",
    "--check-declared",
    "--check-drawn",
    "--glyph-gate",
    "--glyph-dispatched",
    "--landing-mark",
];

fn usage(why: &str) -> Reply {
    reply(String::new(), format!("l7r-gate reviews owed: {why}\n"), 2)
}

/// `review_owed.py`'s command line.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    cli_in(args, &Rooted::process("."))
}

/// [`cli`] with the environment its root is read with: `base`'s (feature 451 T38: a test's own, never a session's exports).
#[must_use]
pub fn cli_in(args: &[String], base: &Rooted) -> Reply {
    let specs = [
        Spec::value("--root"),
        Spec::flag("--why"),
        Spec::flag("--units"),
        Spec::flag("--undrawn"),
        Spec::flag("--check-declared"),
        Spec::flag("--check-drawn"),
        Spec::value("--glyph-gate"),
        Spec::value("--glyph-dispatched"),
        Spec::value("--landing-mark"),
        Spec::flag("--landing"),
        Spec::flag("--escaped"),
        Spec::flag("--help"),
    ];
    let p = match parse(args, &specs) {
        Ok(p) => p,
        Err(why) => return usage(&why),
    };
    if p.on("--help") {
        return reply(
            "usage: l7r-gate reviews owed [--root DIR] [--why | --units | --undrawn | --check-declared | --check-drawn | --glyph-gate SLUG | --glyph-dispatched SLUG | --landing-mark {on,off}] [--landing] [--escaped]\n".to_owned(),
            String::new(),
            0,
        );
    }
    let given: Vec<&str> = MODES
        .iter()
        .copied()
        .filter(|m| p.on(m) || p.has(m))
        .collect();
    if given.len() > 1 {
        return usage(&format!(
            "argument {}: not allowed with argument {}",
            given[1], given[0]
        ));
    }
    let mark = p.text("--landing-mark", "");
    if p.has("--landing-mark") && !matches!(mark, "on" | "off") {
        return usage(&format!(
            "argument --landing-mark: invalid choice: {}",
            py_repr(mark)
        ));
    }
    let asked = p.text("--root", ".");
    let Some(top) =
        git(&py_path(asked), &["rev-parse", "--show-toplevel"]).filter(|t| !t.is_empty())
    else {
        return reply(
            String::new(),
            format!("_review_owed: {asked} is not a git repository\n"),
            1,
        );
    };
    let root = base.at(top);
    run(&root, &p, mark)
}

fn run(root: &Rooted, p: &crate::record::args::Parsed, mark: &str) -> Reply {
    let check = if p.on("--check-declared") {
        Some(check_declared as fn(&Path) -> Option<String>)
    } else if p.on("--check-drawn") {
        Some(check_drawn as fn(&Path) -> Option<String>)
    } else {
        None
    };
    if let Some(check) = check {
        return check(root).map_or_else(
            || reply(String::new(), String::new(), 0),
            |r| reply(r + "\n", String::new(), 1),
        );
    }
    if p.on("--undrawn") {
        // the folders alone, no base read and no legend: what a gate run with nothing stale pays for the question
        let mut currency = l7r_gate_pool::Currency::new(root);
        let out = undrawn(root, &folders(root), &mut |d| {
            currency.of(&d.path.display().to_string())
        })
        .into_iter()
        .fold(String::new(), |mut o, (kind, at)| {
            let _ = writeln!(o, "{kind}\t{at}");
            o
        });
        return reply(out, String::new(), 0);
    }
    if !mark.is_empty() {
        glyph::mark_landing(root, mark == "on");
        return reply(String::new(), String::new(), 0);
    }
    let (gate, dispatched) = (p.text("--glyph-gate", ""), p.text("--glyph-dispatched", ""));
    if !gate.is_empty() || !dispatched.is_empty() {
        let slug = if gate.is_empty() { dispatched } else { gate };
        let (code, out) = glyph::glyph_cli(root, slug, !gate.is_empty(), p.on("--escaped"));
        return reply(out, String::new(), code);
    }
    let landing = p.on("--landing");
    let (desc, all, problems, taken) = owed_discharged(root);
    let (due, waiting) = if landing {
        (all.clone(), Vec::new())
    } else {
        glyph::glyph_due(root, &all, None)
    };
    let units: Vec<Unit> = all
        .into_iter()
        .filter(|u| landing || u.check != "glyph-check" || due.contains(u))
        .collect();
    let mut out = String::new();
    if p.on("--why") {
        out += &ruling(&desc, &units, &problems);
        out.push('\n');
        if !taken.is_empty() {
            let each: Vec<String> = taken.iter().map(|(s, by)| format!("{s} ({by})")).collect();
            let _ = writeln!(
                out,
                "glyph checks discharged by the round arbiter's accept, their marks as it bound them (449 T377): {}",
                each.join(", ")
            );
        }
        if !waiting.is_empty() {
            let each: Vec<String> = waiting
                .iter()
                .map(|(u, when)| format!("{} ({when})", u.slug()))
                .collect();
            let _ = writeln!(
                out,
                "glyph checks owed and not yet due (feature 375 amendment 9 - on the feature's hour, or at landing): {}",
                each.join(", ")
            );
        }
    } else if p.on("--units") {
        for u in &units {
            let _ = writeln!(
                out,
                "{}\t{}\t{}\t{}\t{}",
                u.slug(),
                u.check,
                u.subject,
                u.on,
                u.occasion
            );
        }
    } else {
        for u in &units {
            let _ = writeln!(out, "{}", u.slug());
        }
    }
    reply(out, String::new(), 0)
}
