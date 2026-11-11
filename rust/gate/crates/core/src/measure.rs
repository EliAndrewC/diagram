//! What the cost tools share with the rest of the gate (feature 449 T75, from `measure.rs`, split out by T92): a reply, the home
//! directory, an error's text, the `.json` files under a directory, a median, and the ISO time reader (`popup_rounds::iso`).

use std::path::{Path, PathBuf};

/// The `popup-rounds` reader's ISO times, which the reviews read too.
pub mod popup_rounds {
    pub mod iso;
}

#[must_use]
pub fn reply(stdout: String, stderr: String, code: i32) -> crate::Reply {
    crate::Reply {
        stdout,
        stderr,
        code,
    }
}

/// `$HOME`, or the empty path where it is unset.
#[must_use]
pub fn home() -> PathBuf {
    std::env::var_os("HOME").map_or_else(PathBuf::new, PathBuf::from)
}

/// An error as its text, for `map_err`.
#[must_use]
pub fn text_err(e: impl std::fmt::Display) -> String {
    e.to_string()
}

/// Every `.json` under `dir`, recursively, sorted.
#[must_use]
pub fn json_files(dir: &Path) -> Vec<PathBuf> {
    let mut out = Vec::new();
    let mut todo = vec![dir.to_path_buf()];
    while let Some(at) = todo.pop() {
        for entry in std::fs::read_dir(&at).into_iter().flatten().flatten() {
            let path = entry.path();
            if path.is_dir() {
                todo.push(path);
            } else if path.extension().is_some_and(|x| x == "json") {
                out.push(path);
            }
        }
    }
    out.sort();
    out
}

/// Python's `median` of what is given: the middle, or the mean of the middle two.
pub fn median(values: &mut [f64]) -> f64 {
    values.sort_by(f64::total_cmp);
    let n = values.len();
    if n % 2 == 1 {
        values[n / 2]
    } else {
        values[n / 2 - 1].midpoint(values[n / 2])
    }
}

#[cfg(test)]
mod tests {
    use super::{home, json_files, median, reply, text_err};

    #[test]
    fn the_helpers_hold() {
        let dir = crate::checks::scratch("core-measure");
        std::fs::create_dir_all(dir.join("a")).unwrap();
        std::fs::write(dir.join("a/x.json"), "{}").unwrap();
        std::fs::write(dir.join("y.txt"), "").unwrap();
        assert_eq!(json_files(&dir).len(), 1);
        assert!((median(&mut [3.0, 1.0, 2.0]) - 2.0).abs() < f64::EPSILON);
        assert!((median(&mut [4.0, 1.0]) - 2.5).abs() < f64::EPSILON);
        assert_eq!(text_err("x"), "x");
        assert_eq!(reply(String::new(), "e".to_owned(), 2).code, 2);
        assert_eq!(home(), std::path::PathBuf::from(std::env::var_os("HOME").unwrap_or_default()));
    }
}
