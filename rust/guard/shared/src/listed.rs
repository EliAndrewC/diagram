//! A LIST IN A GUARD MESSAGE IS HELD AT A FEW ITEMS (feature 451 T170; the GM 2026-11-23, on hook output length: "could we accomplish
//! the same thing with no loss of fidelity and fewer tokens?"). A message that grows with a list reached a session at many times its
//! budget - static-runs' refusal at 7,909 characters over 25 crates, review-round's stale-term refusal at 10,345 over 25 candidates,
//! blocked-fetch's attempts notice at 6,077 over one URL's earlier attempts (measured 2026-11-23 over the coordinator's transcript and
//! its subagents', `/tmp/t170/census/var.py`) - so each such list shows its first few items and "and N more:" with the
//! command that prints them all, its fix commands and escapes in full. Where no command lists them, [`kept`]
//! writes them all to a file under the clone's git directory and names the `cat` that prints it. Each message is held at its worst
//! case, many items, by `suite_tools/messages/worst.rs`.

use std::path::Path;

use crate::sha256;

/// The items a capped list shows before its `and N more`: a GUESS (451 T170, the brief's "a few items") - three of the longest
/// measured, review-round's candidates at about 385 characters and a prerequisite's at 511 (2026-11-23), put those refusals past
/// their budget; a knob, moved by a measurement of what a session does with the rest.
pub const SHOWN: usize = 2;

/// `items`' first `shown`, one a line, then `<indent>and N more:` and `rest` in backticks when there are more; the items carry their own indent and
/// are never cut, since an item may end in its own fix command. Every item where the whole list is no longer than that: a cap that
/// does not shorten only hides items (451 T170: three short prerequisites said as two and a `cat` of a kept file).
#[must_use]
pub fn capped_n(items: &[String], shown: usize, indent: &str, rest: &str) -> String {
    let all = items.join("\n");
    match items.get(shown..) {
        Some(more) if !more.is_empty() => {
            let short = format!(
                "{}\n{indent}and {} more: `{rest}`",
                items[..shown].join("\n"),
                more.len()
            );
            if short.chars().count() < all.chars().count() {
                short
            } else {
                all
            }
        }
        _ => all,
    }
}

/// [`capped_n`] at [`SHOWN`].
#[must_use]
pub fn capped(items: &[String], indent: &str, rest: &str) -> String {
    capped_n(items, SHOWN, indent, rest)
}

/// `items` as one line, comma-separated: its first [`SHOWN`] and `, and N more:` with `rest` in backticks when there are more and `rest` is said, else
/// every item.
#[must_use]
pub fn inline(items: &[String], rest: &str) -> String {
    let all = items.join(", ");
    if items.len() <= SHOWN || rest.is_empty() {
        return all;
    }
    let short = format!(
        "{}, and {} more: `{rest}`",
        items[..SHOWN].join(", "),
        items.len() - SHOWN
    );
    if short.chars().count() < all.chars().count() {
        short
    } else {
        all
    }
}

/// The file [`kept`] writes `items` to: `<git dir>/l7r-lists/<key>.txt`, the key the first 16 hex digits of the items' SHA-256 (so
/// two sessions writing one list write one file).
fn kept_path(git_dir: &Path, items: &[String]) -> std::path::PathBuf {
    let text = items.join("\n") + "\n";
    git_dir
        .join("l7r-lists")
        .join(format!("{}.txt", &sha256::hex(text.as_bytes())[..16]))
}

/// Every item written to [`kept_path`], and the command that prints it; "" where the file cannot be written.
#[must_use]
pub fn kept(git_dir: &Path, items: &[String]) -> String {
    let path = kept_path(git_dir, items);
    let wrote = std::fs::create_dir_all(git_dir.join("l7r-lists"))
        .and_then(|()| std::fs::write(&path, items.join("\n") + "\n"));
    if wrote.is_ok() {
        format!("cat {}", path.display())
    } else {
        String::new()
    }
}

/// [`capped_n`] with the rest [`kept`] under `git_dir`, the file written only when the cap shortens the list; every item where it
/// does not or the file cannot be written.
#[must_use]
pub fn capped_kept_n(items: &[String], shown: usize, indent: &str, git_dir: &Path) -> String {
    let all = items.join("\n");
    let rest = format!("cat {}", kept_path(git_dir, items).display());
    if capped_n(items, shown, indent, &rest) == all {
        return all;
    }
    match kept(git_dir, items) {
        rest if rest.is_empty() => all,
        rest => capped_n(items, shown, indent, &rest),
    }
}

/// [`capped_kept_n`] at [`SHOWN`].
#[must_use]
pub fn capped_kept(items: &[String], indent: &str, git_dir: &Path) -> String {
    capped_kept_n(items, SHOWN, indent, git_dir)
}

#[cfg(test)]
mod tests;
