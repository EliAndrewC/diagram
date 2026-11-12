//! The model trials and what the subagents cost (feature 449 T75, T88): `measure model-trial`, `subagent-cache`, `depiction-replay`,
//! `popup-rounds`, `work-budget`; the work budget's own tools, `work-budget-bundle` and `budget-change` (T134); and `record agent-census`.

/// The cost tools held here, beside the shared helpers of the core.
pub mod measure {
    pub use l7r_gate_core::measure::*;
    pub mod budget_change;
    pub mod depiction_replay;
    pub mod model_trial;
    pub mod popup_rounds;
    pub mod subagent_cache;
    pub mod work_budget;
    pub mod work_budget_bundle;

    pub use subagent_cache::{at, commas};
}

/// The agent census, beside the record's tools of the owed crate.
pub mod record {
    pub use l7r_gate_owed::record::*;
    pub mod agent_census;
}

#[cfg(test)]
use l7r_gate_core::write_executable;
use l7r_gate_core::{checks, codeid, cohort, logs, plan, Reply};
