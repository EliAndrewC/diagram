//! A long report through a pager when it goes to a terminal, as git does (`scripts/record/pager.py`, ported by feature 449 T82; the GM
//! 2026-10-27): `make claims-report` wrote about 128 KB at once and the laptop's `podman exec -it` dropped the tab. A pipe or a file still
//! gets the whole text, and `NO_PAGER=1` turns it off.

use std::io::{IsTerminal, Write};
use std::process::{Command, Stdio};

/// Where the text goes: whether stdout is a terminal, its height, the pager's command and `NO_PAGER`.
pub(crate) struct Screen {
    pub(crate) tty: bool,
    pub(crate) rows: usize,
    pub(crate) pager: String,
    pub(crate) off: bool,
}

/// `shutil.get_terminal_size().lines`: `LINES`, else the terminal's, else 24.
pub(crate) fn rows(lines: Option<String>, probe: &str) -> usize {
    if let Some(n) = lines
        .and_then(|l| l.parse::<usize>().ok())
        .filter(|n| *n > 0)
    {
        return n;
    }
    Command::new("sh")
        .arg("-c")
        .arg(probe)
        .stderr(Stdio::null())
        .output()
        .ok()
        .and_then(|o| {
            String::from_utf8_lossy(&o.stdout)
                .split_whitespace()
                .next()
                .and_then(|r| r.parse().ok())
        })
        .filter(|n: &usize| *n > 0)
        .unwrap_or(24)
}

impl Screen {
    /// The process's own stdout and environment.
    pub(crate) fn here() -> Self {
        let var = |k: &str| std::env::var(k).ok();
        Self::of(
            std::io::stdout().is_terminal(),
            var("LINES"),
            var("PAGER"),
            var("NO_PAGER"),
        )
    }

    /// From whether stdout is a terminal and the values of `LINES`, `PAGER` and `NO_PAGER`.
    pub(crate) fn of(
        tty: bool,
        lines: Option<String>,
        pager: Option<String>,
        no_pager: Option<String>,
    ) -> Self {
        let rows = if tty {
            rows(lines, "stty size < /dev/tty")
        } else {
            24
        };
        let pager = pager.filter(|p| !p.is_empty());
        Self {
            tty,
            rows,
            pager: pager.unwrap_or("less -FRSX".to_owned()),
            off: no_pager.is_some_and(|v| !v.is_empty()),
        }
    }
}

fn on_path(word: &str) -> bool {
    if word.contains('/') {
        return std::path::Path::new(word).is_file();
    }
    std::env::var_os("PATH")
        .is_some_and(|p| std::env::split_paths(&p).any(|d| d.join(word).is_file()))
}

/// `text` through the pager when the screen is a terminal and the text is longer than it; what is left to print (all of it, or nothing).
pub(crate) fn page(text: &str, screen: &Screen) -> String {
    let first = screen.pager.split_whitespace().next().unwrap_or_default();
    if screen.off || !screen.tty || text.matches('\n').count() + 1 < screen.rows || !on_path(first)
    {
        return format!("{text}\n");
    }
    let _ = std::io::stdout().flush();
    let child = Command::new("sh")
        .arg("-c")
        .arg(&screen.pager)
        .stdin(Stdio::piped())
        .spawn();
    let _ = child.map(|mut child| {
        let _ = child
            .stdin
            .take()
            .map(|mut pipe| pipe.write_all(format!("{text}\n").as_bytes()));
        child.wait()
    });
    String::new()
}

#[cfg(test)]
mod tests;
