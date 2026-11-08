//! The guards, one module each, in the fixed order `lib::guards` runs them (plan D2): each ported from its shell guard by its own
//! task (feature 449 T006-T049), its suite replayed against `l7r-guard --only <guard>` before its shell is deleted (D3, D4).

pub mod gate_hooks;
pub mod measure_hooks;
pub mod no_poll_hooks;
pub mod pair_hooks;
