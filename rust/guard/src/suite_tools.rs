//! The guard suites' own tooling (feature 449 T050), ported from `tests/hooks/`: which suites a change makes stale (`deps`), what a suite read (`trace`), the replay of real
//! commands through a guard (`bench`), and the facts of a Python file those need (`pylex`).

pub mod bench;
pub mod deps;
pub use l7r_shared::suite_tools::pylex;
pub mod trace;
