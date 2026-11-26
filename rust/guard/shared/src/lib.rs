//! What every guard reads, ported from `scripts/hooks/lib/` (feature 449 T003, plan D5-D6): the shell's shape (`hm_shape.py`'s
//! heredoc and quote stripping), the escape rule (`hm_escape.py`), the session's facts read once a process, and the guard log
//! (`guardlog.sh`), written in today's format.

pub mod attempts;
pub mod blocked;
// GUARD_EDIT_OK: feature 451 T285 - adding an operation, the builder pool's registry
pub mod builder_pool;
pub mod checks;
pub mod cited_url;
pub mod consulted;
pub mod context;
pub mod difflib;
pub mod env;
pub mod escape;
pub mod html_text;
pub mod iso;
pub mod ledger;
pub mod listed;
pub mod log;
pub mod make;
pub mod once;
pub mod parked;
pub mod plan_text;
pub mod protocol;
pub mod py_text;
pub mod pyjson;
pub mod regex;
pub mod session;
pub mod sha1;
pub mod sha256;
pub mod shape;
pub mod speckit;
pub mod state;
pub mod switches;
pub mod tempdir;
pub mod tool;
pub mod transcript;
pub mod tree;
pub mod url_host;
pub mod usage;
pub mod wait;

/// The guards whose code the gate's crates call (feature 451 T58): the event log and its readers (`measure`, `arbiter`, `land`, `rustc`,
/// `bundle`, `reviews`), the house style's corrections, the feature approval's form, the set-down's performance tasks and the conflict
/// markers. Each is a guard of the guard's fixed order still, which names it through its own `guards` module.
pub mod guards {
    pub mod conflict_marker_hooks;
    pub mod event_log_hooks;
    pub mod feature_approval_hooks;
    pub mod house_style_hooks;
    pub mod set_down_hooks;
}

/// The suites' tooling the gate's `registry` tests read: what a Python file imports and quotes.
pub mod suite_tools {
    pub mod pylex;
}
