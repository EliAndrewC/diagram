//! The Mode A engine (feature 449 T168, the first piece of the engine port's step 1 under `ask:449-engine-order`): the building types
//! ([`types`], `l7r/diagram/buildings/types.py`) and `make building-programs` ([`programs`], `tools/building_programs.py`, deleted).
//!
//! WHY ITS OWN CRATE AND BINARY: the engine will pull `geo` and `resvg` (the plan's steps 2-3), and a gate or guard build that compiled
//! them would put minutes in front of every hook and check edit; so `l7r-mode-a` is built alone by `scripts/gates/l7r-gate.sh mode-a`,
//! as the browser and the embedder are, and nothing of the gate depends on it.
//!
//! Research:
//!     the Mode A engine's command - NONE: dispatch to its tools, deciding nothing about a building

use std::path::Path;

use l7r_gate_core::Reply;

pub mod programs;
pub mod py;
pub mod types;

/// The command: `building-programs [--check] [--path PATH]`, or `--version` (the differential's cheap build probe).
#[must_use]
pub fn cli(args: &[String], tree: &Path) -> Reply {
    match args.first().map(String::as_str) {
        Some("building-programs") => programs::main(&args[1..], tree),
        Some("--version") => reply(format!("l7r-mode-a {}\n", env!("CARGO_PKG_VERSION")), "", 0),
        _ => reply(
            String::new(),
            "usage: l7r-mode-a building-programs [--check] [--path PATH] | --version\n",
            2,
        ),
    }
}

fn reply(stdout: String, stderr: &str, code: i32) -> Reply {
    Reply {
        stdout,
        stderr: stderr.to_owned(),
        code,
    }
}

#[cfg(test)]
mod tests {
    use super::cli;

    #[test]
    fn the_command_names_its_tools() {
        let tree = std::path::Path::new("/nonexistent");
        let r = cli(&["--version".to_owned()], tree);
        assert_eq!((r.code, r.stdout.starts_with("l7r-mode-a ")), (0, true));
        let r = cli(&[], tree);
        assert_eq!(
            (r.code, r.stderr.starts_with("usage: l7r-mode-a")),
            (2, true)
        );
        let r = cli(&["building-programs".to_owned(), "--x".to_owned()], tree);
        assert_eq!(r.code, 2);
    }
}
