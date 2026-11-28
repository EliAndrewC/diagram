//! A feature's `report.md` cut into parts (462 T555): where a split feature's report runs past [`BOUND`], its large sections move to
//! `report/` beside it, each cut at its table's rows into parts of at most [`BOUND`] bytes, and `report.md` becomes the index - its
//! title, a note opening "Load this file when:", its small sections inline and, for each moved one, its heading and its parts.
//!
//! WHY (the GM 2026-11-27, 462's request.md, on sessions "naively just opening these very large files and then blowing through their
//! own context windows"): 451's report.md stood at 1,496,878 bytes after `make archive-split` cut its plan-done.md and tasks-done.md
//! (observed 2026-11-28, method: `ls -la` of the feature directory), three tables holding 1,448,740 of them - the critical path
//! 130,450, each task's phases 442,621, each task's decision-log skeleton 875,669 (observed 2026-11-27, method: its `## ` sections
//! measured). A table is cut between rows, never inside one, each part repeating its section's heading and the table's header so a
//! part reads alone; a task's rows (the first cell) stay in one part where they fit one.
//!
//! WHO READS IT: `make feature-report F= WRITE=1` writes it (through [`write`], split only where the feature is split), the close's
//! check asks only that `report.md` stands (`reviews/closing.rs`), and the GM and the retro read it. `make archive-split` cuts an
//! existing report the same way.

use std::fmt::Write as _;
use std::path::Path;

use super::{io, BOUND};

/// The report, feature-relative.
pub const REPORT: &str = "report.md";
/// Its parts' directory, feature-relative.
pub const DIR: &str = "report";
/// A section larger than this moves to parts; a smaller one stays inline in the index. 16 KiB (a GUESS knob, 462 T555): 451's
/// sections ran 83 to 24,344 bytes but for the three tables.
pub const INLINE: usize = 16_384;
/// The line a split report's index carries, so a second split leaves it as it stands.
pub const MARK: &str = "<!-- report split into report/ (462 T555): what is where is below -->";

/// A section's title words, for a part's name: its letters and digits in lower case, words joined by `-`, at most 40 characters.
fn slug(title: &str) -> String {
    let mut out = String::new();
    for w in title
        .split(|c: char| !c.is_ascii_alphanumeric())
        .filter(|w| !w.is_empty())
    {
        if out.len() + w.len() + 1 > 40 {
            break;
        }
        if !out.is_empty() {
            out.push('-');
        }
        out += &w.to_ascii_lowercase();
    }
    out
}

/// A table row's first cell, trimmed (a task id in 451's tables).
fn first_cell(row: &str) -> &str {
    row.trim_start_matches('|')
        .split('|')
        .next()
        .unwrap_or("")
        .trim()
}

/// One piece of a section: a table row's run of one first cell (`Some(cell)`, under its table's header), or other lines.
struct Unit {
    cell: Option<String>,
    text: String,
    header: Option<String>,
}

/// `section` (its heading line first) cut at its tables' rows: (the first row's first cell, the last's, the part's text). A part
/// opens with the section's heading and, where it starts inside a table, that table's header and separator; a section may hold
/// several tables (451's critical path holds eight). A task's rows stay in one part where they fit half of [`BOUND`]; a longer run
/// (451's decision-log skeleton held tasks of 120 KB of rows) is cut between rows.
fn rows_cut(section: &str) -> Vec<(String, String, String)> {
    let lines: Vec<&str> = section.split_inclusive('\n').collect();
    let mut units: Vec<Unit> = Vec::new();
    let mut header: Option<String> = None;
    let mut i = 1;
    while i < lines.len() {
        let line = lines[i];
        let row = line.starts_with('|');
        if row && header.is_none() && lines.get(i + 1).is_some_and(|l| l.starts_with("|-")) {
            let pair = format!("{line}{}", lines[i + 1]);
            units.push(Unit {
                cell: None,
                text: pair.clone(),
                header: None,
            });
            header = Some(pair);
            i += 2;
            continue;
        }
        let cell = (row && header.is_some()).then(|| first_cell(line).to_owned());
        if cell.is_none() {
            header = None;
        }
        match units.last_mut() {
            Some(u)
                if u.cell == cell
                    && u.header == header
                    && u.text.len() + line.len() <= BOUND / 2 =>
            {
                u.text += line;
            }
            _ => units.push(Unit {
                cell,
                text: line.to_owned(),
                header: header.clone(),
            }),
        }
        i += 1;
    }
    let heading = lines.first().copied().unwrap_or("");
    let mut parts: Vec<(String, String, String)> = Vec::new();
    let mut p = (String::new(), String::new(), heading.to_owned());
    for u in units {
        if p.2.len() + u.text.len() > BOUND {
            let opening = format!("{heading}\n{}", u.header.as_deref().unwrap_or(""));
            parts.push(std::mem::replace(
                &mut p,
                (String::new(), String::new(), opening),
            ));
        }
        if let Some(cell) = &u.cell {
            if p.0.is_empty() {
                p.0.clone_from(cell);
            }
            p.1.clone_from(cell);
        }
        p.2 += &u.text;
    }
    parts.push(p);
    parts
}

/// The split of a report's `text`: the index's text and each part's (its path, feature-relative, and its text); None where it is
/// already split or no larger than [`BOUND`], to be written as it stands.
#[must_use]
pub fn split(feature: &str, text: &str) -> Option<(String, Vec<(String, String)>)> {
    if text.len() <= BOUND || text.contains(MARK) {
        return None;
    }
    let mut starts: Vec<usize> = text.match_indices("\n## ").map(|(i, _)| i + 1).collect();
    starts.push(text.len());
    let number = feature.split('-').next().unwrap_or(feature);
    let mut index = text[..starts[0]].to_owned();
    let _ = write!(
        index,
        "{MARK}\n\nLoad this file when: you need feature {number}'s report - where its time went, its rounds, tripwires and costs - or \
you are about to open or grep a file under its `report/`. Its small sections are below; each large one names its parts, so open the \
one part you need (a task's rows stand in the part whose range holds it).\n\nWHY: a report's tables ran to megabytes (451's report.md \
1,496,878 bytes); a session that read or grepped it whole spent its context on it (the GM 2026-11-27, 462 T555). Each section past \
{INLINE} bytes is cut at its table's rows into parts of at most {BOUND} bytes, each repeating its heading and its table's header. \
Do not `cat report/*` or grep the directory broadly: grep with `-l` or `-c` first, then read the one part it names.\n\n"
    );
    let mut parts = Vec::new();
    for (n, w) in starts.windows(2).enumerate() {
        let section = &text[w[0]..w[1]];
        if section.len() <= INLINE {
            index += section;
            continue;
        }
        let heading = section.lines().next().unwrap_or("");
        let name = slug(heading);
        let cut = rows_cut(section);
        let _ = write!(
            index,
            "{heading}\n\nIn {} part(s), {} bytes, cut at its rows (462 T555):\n\n",
            cut.len(),
            section.len()
        );
        for (k, (first, last, body)) in cut.into_iter().enumerate() {
            let path = format!("{DIR}/{:02}-{name}-{}.md", n + 1, k + 1);
            let rows = if first.is_empty() {
                String::new()
            } else {
                format!(", rows {first} to {last}")
            };
            let _ = writeln!(index, "- `{path}` ({} bytes{rows})", body.len());
            parts.push((path, body));
        }
        index.push('\n');
    }
    Some((index, parts))
}

/// Write feature directory `d`'s report `text`: split ([`split`]) where `cut` and it runs past [`BOUND`], else whole; the parts an
/// earlier split left are removed first. The parts written, feature-relative.
///
/// # Errors
/// A file that cannot be written or removed.
pub fn write(d: &Path, text: &str, cut: bool) -> Result<Vec<String>, String> {
    let feature = d.file_name().unwrap_or_default().to_string_lossy();
    let split = if cut { split(&feature, text) } else { None };
    let dir = d.join(DIR);
    if !text.contains(MARK) && dir.is_dir() {
        io(&dir, std::fs::remove_dir_all(&dir))?;
    }
    let at = d.join(REPORT);
    let Some((index, parts)) = split else {
        io(&at, std::fs::write(&at, text))?;
        return Ok(Vec::new());
    };
    io(&dir, std::fs::create_dir_all(&dir))?;
    let mut written = Vec::new();
    for (path, body) in parts {
        let part = d.join(&path);
        io(&part, std::fs::write(&part, body))?;
        written.push(path);
    }
    io(&at, std::fs::write(&at, index))?;
    Ok(written)
}

#[cfg(test)]
mod tests;
