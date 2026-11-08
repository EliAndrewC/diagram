//! What every guard reads, ported from `scripts/hooks/lib/` (feature 449 T003, plan D5-D6): the shell's shape (`hm_shape.py`'s
//! heredoc and quote stripping), the escape rule (`hm_escape.py`), the session's facts read once a process, and the guard log
//! (`guardlog.sh`), written in today's format.

pub mod escape;
pub mod log;
pub mod make;
pub mod session;
pub mod sha256;
pub mod shape;
pub mod state;
pub mod tool;
pub mod transcript;
pub mod tree;
pub mod wait;
