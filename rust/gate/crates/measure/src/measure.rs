//! What things cost (feature 449 T75, the second slice of `scripts/measure/`, `ask:449-T068-scope`): the recorded figures re-run, the time
//! ratchets, what a gate run costs and what a change does to every seed.

use std::path::Path;

pub mod event_log;
pub mod events;
pub mod feature_report;
pub mod figures;
pub mod fix_yield;
pub mod fresh_tally;
pub mod gate_costs;
pub mod gatecost;
pub mod guard_log;
pub mod maps_moved;
pub mod probe;
pub mod push_check_times;
pub mod review_yield;
pub mod runstats;
pub mod stepback_bundle;
pub mod task_phases;
pub mod tool_yield;
pub mod turn_time;
pub mod wave_report;
pub mod where_time;

pub use l7r_gate_tree::measure::*;
pub use l7r_gate_trials::measure::popup_rounds;
pub use l7r_gate_trials::measure::*;

/// `l7r-gate measure ...`.
pub fn cli(args: &[String], root: &Path) -> crate::Reply {
    let rest = args.get(1..).unwrap_or(&[]);
    match args.first().map(String::as_str) {
        Some("figures") => figures::cli(rest, root),
        Some("gate-costs") => gate_costs::cli(rest, root),
        Some("gatecost") => gatecost::cli(rest, root),
        Some("ratchet") => ratchet::cli(rest, root),
        Some("probe") => probe::cli(rest, root),
        Some("runstats") => runstats::cli(rest),
        Some("guard-log") => guard_log::cli(rest, &home()),
        Some("review-yield") => review_yield::cli(rest, root),
        Some("wave-report") => wave_report::cli(rest, &home()),
        Some("subagent-cache") => subagent_cache::cli(rest, &home(), &a_week_ago()),
        Some("fresh-tally") => fresh_tally::cli(rest, root),
        Some("maps-moved") => maps_moved::cli(rest, root),
        Some("popup-rounds") => popup_rounds::cli(rest),
        Some("work-budget") => work_budget::cli(rest, root),
        Some("push-check-times") => push_check_times::cli(rest, root, root),
        Some("depiction-replay") => depiction_replay::cli(rest, root),
        Some("model-trial") => model_trial::cli(rest, &model_trial::live(&home(), root)),
        // the measure chain (feature 449 T119): the review passes are costed from the process's own directory and `$HOME`, as the
        // Python's `l7r-gate reviews ledger-passes` run read them
        Some("feature-report") => feature_report::cli(
            rest,
            &l7r_gate_reviews::reviews::ledger_passes::Env::of_process(),
            Path::new(events::CLONES),
        ),
        Some("where-time") => where_time::cli(rest, &home().join(".claude/projects"), Path::new(events::CLONES)),
        Some("event-log") => event_log::cli(rest, &mut std::io::stdin()),
        // T83's fourth slice (feature 449 T120): the step-back bundle and the yield reports, the step-back reading the reviews crate in
        // process where `stepback_bundle.py` reached it through `reviews_door.py`
        Some("step-back") => stepback_bundle::cli(
            rest,
            &stepback_bundle::Env {
                home: home(),
                now: tool_yield::now(),
            },
        ),
        Some("fix-yield") => fix_yield::cli(rest, &home()),
        Some("tool-yield") => tool_yield::cli(rest, root, &home()),
        Some("turn-time") => turn_time::cli(rest),
        _ => reply(
            String::new(),
            "usage: l7r-gate measure figures | gate-costs | gatecost | ratchet | probe | runstats | guard-log | review-yield | wave-report | subagent-cache | fresh-tally | maps-moved | popup-rounds | work-budget | push-check-times | model-trial | depiction-replay | feature-report | where-time | event-log | step-back | fix-yield | tool-yield | turn-time\n"
                .to_owned(),
            2,
        ),
    }
}

/// The date seven days before today, as `YYYY-MM-DD`: the default window of the subagent report.
fn a_week_ago() -> String {
    let now = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0, |d| d.as_secs());
    let (y, m, d, ..) = l7r_guard::shared::log::civil(now.saturating_sub(7 * 86_400));
    format!("{y:04}-{m:02}-{d:02}")
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
        let there = dir.display().to_string();
        let ask = |words: &[&str]| {
            cli(
                &words.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>(),
                &dir,
            )
            .code
        };
        assert_eq!(ask(&["runstats"]), 2);
        assert_eq!(ask(&["guard-log", "--dir", &there]), 0);
        assert_eq!(ask(&["review-yield"]), 0);
        assert_eq!(ask(&["wave-report", "--root", &there]), 1);
        assert_eq!(ask(&["subagent-cache", "--root", &there]), 0);
        assert_eq!(ask(&["fresh-tally", "--log", &there]), 0);
        assert_eq!(ask(&["feature-report"]), 2);
        assert_eq!(ask(&["where-time"]), 2);
        assert_eq!(ask(&["event-log"]), 2);
        assert_eq!(ask(&["step-back"]), 2);
        assert_eq!(ask(&["fix-yield"]), 2);
        assert_eq!(ask(&["tool-yield", "--kind", "x"]), 2);
        assert_eq!(ask(&["turn-time"]), 2);
    }
}
