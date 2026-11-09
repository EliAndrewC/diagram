//! What things cost (feature 449 T75, the second slice of `scripts/measure/`, `ask:449-T068-scope`): the recorded figures re-run, the time
//! ratchets, what a gate run costs and what a change does to every seed.

use std::path::Path;

pub(crate) mod figures;
pub(crate) mod gate_costs;
pub(crate) mod gatecost;
pub(crate) mod probe;
pub(crate) mod ratchet;

pub(crate) fn reply(stdout: String, stderr: String, code: i32) -> crate::Reply {
    crate::Reply {
        stdout,
        stderr,
        code,
    }
}

/// `l7r-gate measure ...`.
pub(crate) fn cli(args: &[String], root: &Path) -> crate::Reply {
    let rest = args.get(1..).unwrap_or(&[]);
    match args.first().map(String::as_str) {
        Some("figures") => figures::cli(rest, root),
        Some("gate-costs") => gate_costs::cli(rest, root),
        Some("gatecost") => gatecost::cli(rest, root),
        Some("ratchet") => ratchet::cli(rest, root),
        Some("probe") => probe::cli(rest, root),
        _ => reply(
            String::new(),
            "usage: l7r-gate measure figures | gate-costs | gatecost | ratchet | probe\n"
                .to_owned(),
            2,
        ),
    }
}

/// Every `.json` under `dir`, recursively, sorted.
pub(crate) fn json_files(dir: &Path) -> Vec<std::path::PathBuf> {
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
pub(crate) fn median(values: &mut [f64]) -> f64 {
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
    use super::{cli, json_files, median};

    #[test]
    fn the_door_says_how_to_use_it_and_the_helpers_hold() {
        let dir = crate::checks::scratch("measure");
        assert_eq!(cli(&["nonsense".to_owned()], &dir).code, 2);
        assert_eq!(cli(&[], &dir).code, 2);
        std::fs::create_dir_all(dir.join("a")).unwrap();
        std::fs::write(dir.join("a/x.json"), "{}").unwrap();
        std::fs::write(dir.join("y.txt"), "").unwrap();
        assert_eq!(json_files(&dir).len(), 1);
        assert!((median(&mut [3.0, 1.0, 2.0]) - 2.0).abs() < f64::EPSILON);
        assert!((median(&mut [4.0, 1.0]) - 2.5).abs() < f64::EPSILON);
    }
}
