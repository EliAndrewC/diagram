//! The guards on Claude Code's tool calls (feature 449 phase 1): one process for a hook event, every guard's check in it, their
//! answers merged by the hook protocol (`specs/449-rust-codebase/contracts/guard-protocol.md`). Each guard moves here from its shell
//! one task at a time (T006-T049); until then the dispatcher holds none.

/// The guard binary's version, which `l7r-guard --version` prints.
#[must_use]
pub fn version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

#[cfg(test)]
mod tests {
    #[test]
    fn the_version_is_the_crates() {
        assert_eq!(super::version(), "0.1.0");
    }
}
