//! A conflicted `specs/*/tasks.md` keeps every open box's lines under it (feature 451 T300): the line FOLLOWING a box - its
//! `      research: rendering`, or a physical task's five boxes - stays with ITS box.
//!
//! WHY: on 2026-11-26 the session resolved about fifteen stopped carries by hand, keeping both sides of each conflict block, and
//! seven open tasks lost their research line - git's own conflict block ended between a box and the line under it, the same words
//! under every box (restored by hand in 39801a6844). The carry's own merge of a tasks.md keeps theirs by block
//! (`super::both`); what this adds: after the merge, an open box left bare that either side holds with lines under it takes
//! them back, the clone's first ([`restored`]) - a box the clone already lost the line of, where the builder's tree still has it -
//! in the tasks.md it resolved and in one git merged cleanly beside a conflict.
//!
//! Don't merge the sides with a box and its lines JOINED as one line: tried here (2026-11-26), it stopped three carries of that day
//! the line merge resolves (T251, T293 and T334's: "a hunk both sides changed"), a box's edit on one side then meeting an added
//! box on the other.

/// Does `line` continue the list line over it?
fn under(line: &str) -> bool {
    line.starts_with([' ', '\t']) && !line.trim().is_empty()
}

/// The lines under each open box of `text`: `(the box's line, the lines under it)`, a bare box left out.
fn held(text: &str) -> Vec<(&str, String)> {
    let mut out: Vec<(&str, String)> = Vec::new();
    let mut open = false;
    for line in text.split_inclusive('\n') {
        match out.last_mut() {
            Some(last) if open && under(line) => last.1.push_str(line),
            _ => {
                open = line.starts_with("- [ ] ");
                if open {
                    out.push((line, String::new()));
                }
            }
        }
    }
    out.retain(|(_, lines)| !lines.is_empty());
    out
}

/// `merged` with each bare open box given the lines a side holds under it, the first side's first.
pub(super) fn restored(merged: &str, sides: [&str; 2]) -> String {
    let known: Vec<(&str, String)> = sides.iter().flat_map(|s| held(s)).collect();
    let mut out = String::new();
    let mut lines = merged.split_inclusive('\n').peekable();
    while let Some(line) = lines.next() {
        out.push_str(line);
        let bare = line.starts_with("- [ ] ") && !lines.peek().is_some_and(|next| under(next));
        if let Some((_, under)) = known
            .iter()
            .find(|(open, _)| bare && open.trim_end() == line.trim_end())
        {
            if !out.ends_with('\n') {
                out.push('\n');
            }
            out.push_str(under);
        }
    }
    out
}
