//! THE HANDOFF A BRIEF NAMES (feature 451 T352): past the cap the exit also takes a Write, Edit or Read of any `.md` file of the
//! handoffs directory that the builder's own brief names there. WHY: the exit took only a name ending `<agent_id>.md`, while
//! `make builder-brief`'s build-half block tells a builder to END at `<task>-build.md` (a bundle's `<a>-<b>-build.md`), its
//! closing-half block reads that file first, and the coordinating session's briefs name `done-pending-<task>.md` - so a builder past
//! the cap could not write the file its brief named, and its successor's brief named a file that did not exist.
//!
//! WHY THE BRIEF, NOT THE TASK ID in the name: the task the cap reads is its call's line's (`filed_at`), the first `T<n>` of a bundle's
//! description, while a bundle's build-half file names every member; and a task id is matched only by guessing at name forms. The
//! brief is the one text that says which file this builder was told to write, read where the split already reads it (its first row).
//! Only a name in THIS clone's handoffs directory counts: a brief's path elsewhere gives its file name, never another directory.

use std::path::{Path, PathBuf};

/// The handoff files `brief` names: each word holding `/l7r-handoffs/` and ending `.md` (its quotes, backticks, brackets and a
/// closing stop or comma trimmed), its name plain (letters, digits, `-`, `_`, `.`), as that file name in `dir`, in the brief's
/// order, each once.
pub(super) fn named(brief: &str, dir: &Path) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = Vec::new();
    for word in brief.split_whitespace() {
        let w = word
            .trim_matches(|c: char| "`\"'()<>[]{},;:".contains(c))
            .trim_end_matches(['.', ',', ';', ':', ')', '`']);
        let Some((_, name)) = w.rsplit_once("/l7r-handoffs/") else {
            continue;
        };
        // a `.md` alone is a dotfile of no extension; a placeholder (`<task>-<agent_id>.md`, `$T.md`) is no plain name, no file
        let plain = name
            .chars()
            .all(|c| c.is_ascii_alphanumeric() || matches!(c, '-' | '_' | '.'));
        if plain && Path::new(name).extension().is_some_and(|e| e == "md") {
            let p = dir.join(name);
            if !out.contains(&p) {
                out.push(p);
            }
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use std::path::{Path, PathBuf};

    use super::named;

    #[test]
    fn a_briefs_handoff_names_are_read_in_order_once() {
        let brief = "END at a handoff, `/c/.git/l7r-handoffs/T1-T2-build.md`, by 200k.\n\
            stop at /c/.git/l7r-handoffs/done-pending-T1.md. Read (/x/l7r-handoffs/T1-T2-build.md) first;\n\
            not /c/.git/l7r-handoffs/sub/x.md, /c/.git/l7r-handoffs/.md, /c/.git/l7r-handoffs/x.txt or /c/notes.md";
        let d = Path::new("/h");
        assert_eq!(
            named(brief, d),
            [
                PathBuf::from("/h/T1-T2-build.md"),
                PathBuf::from("/h/done-pending-T1.md")
            ]
        );
        assert!(named("", d).is_empty());
    }

    /// A brief's prose naming the directory's form (this bundle's own brief: `<git common dir>/l7r-handoffs/<task>-<agent_id>.md`)
    /// names no file: only a plain name counts, so the refusal never names a placeholder.
    #[test]
    fn a_placeholder_name_is_no_file() {
        let brief = "the one exit is a Write of `<git common dir>/l7r-handoffs/<task>-<agent_id>.md`, or $D/l7r-handoffs/$T.md;\n\
            stop with a handoff at /c/.git/l7r-handoffs/done-pending-T417.md";
        assert_eq!(
            named(brief, Path::new("/h")),
            [PathBuf::from("/h/done-pending-T417.md")]
        );
    }
}
