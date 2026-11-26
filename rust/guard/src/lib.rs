//! The guards on Claude Code's tool calls (feature 449 phase 1): one process for a hook event, every guard's check in it, their
//! answers merged by the hook protocol (`specs/449-rust-codebase/contracts/guard-protocol.md`). Each guard moves here from its shell
//! one task at a time (T006-T049); until then the dispatcher holds none.

pub mod guards;
// the hook protocol and what every guard reads live in `l7r_shared` (`shared/`, feature 451 T58), so the gate's crates build on it
// and not on the hooks; re-exported here under their old names, so `crate::shared::...` and `crate::protocol::...` read as before
pub use l7r_shared as shared;
pub use l7r_shared::protocol;
pub mod suite_tools;

use protocol::{run, Event, Guard, Reply};

/// The guards, in their fixed order (plan D2): each moves here from its shell in its own task (T006-T049).
#[must_use]
pub fn guards() -> Vec<Guard> {
    vec![
        guards::pair_hooks::GUARD,
        guards::gate_hooks::GUARD,
        guards::measure_hooks::GUARD,
        guards::no_poll_hooks::GUARD,
        guards::main_tree_hooks::GUARD,
        guards::event_log_hooks::GUARD,
        guards::context_cap_hooks::GUARD,
        guards::clone_sync_hooks::GUARD,
        guards::idle_tests_hooks::GUARD,
        guards::agent_stall_hooks::GUARD,
        guards::stall_watchdog_hooks::GUARD,
        guards::scratch_sweep_hooks::GUARD,
        guards::finished_run_hooks::GUARD,
        guards::engine_freeze_hooks::GUARD,
        guards::gm_tree_hooks::GUARD,
        guards::batching_hooks::GUARD,
        guards::no_branch_hooks::GUARD,
        guards::discard_hooks::GUARD,
        guards::builder_pool_hooks::GUARD,
        guards::conflict_marker_hooks::GUARD,
        guards::gate_write_hooks::GUARD,
        guards::feature_approval_hooks::GUARD,
        guards::budget_change_hooks::GUARD,
        guards::ledger_hooks::GUARD,
        guards::archive_first_hooks::GUARD,
        guards::claims_file_hooks::GUARD,
        guards::readme_hooks::GUARD,
        guards::download_copy_hooks::GUARD,
        guards::phase_source_hooks::GUARD,
        guards::new_file_hooks::GUARD,
        guards::blocked_fetch_hooks::GUARD,
        guards::set_down_hooks::GUARD,
        guards::repo_safety_hooks::GUARD,
        guards::agent_model_hooks::GUARD,
        guards::wakeup_hooks::GUARD,
        guards::agent_prefix_hooks::GUARD,
        guards::workflow_hooks::GUARD,
        guards::source_block_hooks::GUARD,
        guards::house_style_hooks::GUARD,
        guards::escalation_hooks::GUARD,
        guards::review_round_hooks::GUARD,
        guards::make_only_hooks::GUARD,
        guards::guard_file_hooks::GUARD,
        guards::record_edit_hooks::GUARD,
        guards::check_bundle_hooks::GUARD,
        guards::checks_hooks::GUARD,
        guards::builder_stop_hooks::GUARD,
        guards::static_runs_hooks::GUARD,
        guards::research_switch_hooks::GUARD,
        // last, so no guard reads its rewrite of a commit message (T035 decision (d)): a guard ported later goes before it
        guards::shell_check_hooks::GUARD,
    ]
}

/// The command line: `<event>` decides the hook input on `stdin` with every guard; `--only <guard> <event>` with that one guard
/// (its suite's entry point, plan D4); `--self-check` runs every guard on a fixed input, which a build must pass to be kept as the
/// last good one (plan D7); `--version`. An input that is not JSON runs no guard and lets the call go on (T012).
#[must_use]
pub fn cli(args: &[String], stdin: &str, all: &[Guard]) -> Reply {
    let say = |stderr: String, code: i32| Reply {
        stdout: String::new(),
        stderr,
        code,
    };
    match args.first().map(String::as_str) {
        Some("--version") => Reply {
            stdout: format!("l7r-guard {}", version()),
            stderr: String::new(),
            code: 0,
        },
        Some("--self-check") => {
            for name in [
                "PreToolUse",
                "PostToolUse",
                "UserPromptSubmit",
                "Stop",
                "SubagentStop",
                "SubagentStart",
                "PostToolUseFailure",
            ] {
                let mut e = Event {
                    name: name.to_owned(),
                    input: serde_json::json!({"tool_name": "Bash", "tool_input": {"command": "true"}}),
                };
                let _ = run(&mut e, all);
            }
            Reply {
                stdout: format!("l7r-guard self-check: {} guard(s) answered", all.len()),
                stderr: String::new(),
                code: 0,
            }
        }
        Some("--only") => {
            let (Some(name), Some(event)) = (args.get(1), args.get(2)) else {
                return say("l7r-guard: --only <guard> <event>".to_owned(), 1);
            };
            let one: Vec<Guard> = all
                .iter()
                .filter(|g| g.name == name)
                .map(|g| Guard { matcher: "*", ..*g })
                .collect();
            if one.is_empty() {
                return say(format!("l7r-guard: no guard named {name}"), 1);
            }
            // an event no guard of this binary takes is an unknown mode, an error and not a pass (T041 decision (c)); "" is the payload's own
            if !event.is_empty() && !all.iter().any(|g| g.events.contains(&event.as_str())) {
                return say(format!("l7r-guard: unknown event {event}"), 1);
            }
            decide(event, stdin, &one)
        }
        // the detached timer and the printed stagger, the guard's two entries that are not a hook event (T014 decision (a))
        Some("--idle-tests") => guards::idle_tests_hooks::cli(&args[1..]),
        // the Stop's background idle check (451 T183): exit 2 wakes an idle session with the block on stderr, anything else is silent
        Some("--idle-check") => {
            let input = serde_json::from_str(stdin).unwrap_or_default();
            guards::set_down_hooks::idle_check_with(&input, &guards::finished_run_hooks::idle_procs()).map_or_else(|| say(String::new(), 0), |t| say(t, 2))
        }
        // the status probe (451 T193): each builder of an open task working or stalled, by the idle check's own reading
        Some("--builder-status") => {
            let transcript = std::path::Path::new(args.get(1).map_or("", String::as_str));
            let input = serde_json::json!({
                "transcript_path": transcript,
                "session_id": transcript.file_stem().unwrap_or_default().to_string_lossy(),
                "cwd": std::env::current_dir().unwrap_or_default(),
            });
            Reply {
                stdout: guards::set_down_hooks::status(&input, &guards::finished_run_hooks::idle_procs()) + "\n",
                stderr: String::new(),
                code: 0,
            }
        }
        Some("--agent-stall") => guards::agent_stall_hooks::cli(&args[1..]),
        Some("--escalation") => guards::escalation_hooks::cli(&args[1..]),
        Some("--review-round") => guards::review_round_hooks::cli(&args[1..]),
        Some("--stall-watchdog") => guards::stall_watchdog_hooks::cli(&args[1..]),
        Some("--scratch-sweep") => guards::scratch_sweep_hooks::cli(&args[1..]),
        Some("--finished-run") => guards::finished_run_hooks::cli(&args[1..]),
        // the suites' own tooling (T050)
        Some("permit") => guards::guard_file_hooks::cli(&args[1..]),
        Some("dropped") => guards::pair_hooks::dropped::cli(&args[1..]),
        Some("deps") => suite_tools::deps::cli(&args[1..]),
        Some("trace") => suite_tools::trace::cli(&args[1..]),
        Some("bench") => suite_tools::bench::cli(&args[1..]),
        // every guard message the suites render, held to its budget and its review (451 T170)
        Some("messages") => suite_tools::messages::cli(&args[1..]),
        Some(event) => decide(event, stdin, all),
        None => say(
            "l7r-guard: <event> | --only <guard> <event> | --idle-tests <mode> | --agent-stall <mode> | --stall-watchdog <mode> | --scratch-sweep <mode> | --finished-run <mode> | --self-check | --version".to_owned(),
            1,
        ),
    }
}

fn decide(event: &str, stdin: &str, guards: &[Guard]) -> Reply {
    match serde_json::from_str::<serde_json::Value>(stdin) {
        Ok(input) => {
            // no event named: the payload's own (`hook_event_name`), as a hook called with no mode reads it (T012 decision (c))
            let name = if event.is_empty() {
                input
                    .get("hook_event_name")
                    .and_then(serde_json::Value::as_str)
                    .unwrap_or("")
                    .to_owned()
            } else {
                event.to_owned()
            };
            run(&mut Event { name, input }, guards)
        }
        // AN INPUT THAT IS NOT JSON IS NOTHING TO JUDGE: no guard runs and the call goes on, as every shell guard read it (each
        // found no command in it) - a guard run on a guessed empty input would act on it, as the event log would write a line
        // the Python never wrote (T012, its suite's `garbage` case)
        Err(_) => Reply {
            stdout: String::new(),
            stderr: String::new(),
            code: 0,
        },
    }
}

/// The guard binary's version, which `l7r-guard --version` prints.
#[must_use]
pub fn version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

#[cfg(test)]
mod tests {
    use super::protocol::{Answer, Event, Guard};
    use super::{cli, guards};

    fn refuse(_: &Event, _: &crate::shared::session::Session) -> Vec<Answer> {
        vec![Answer::Refuse("refused".to_owned())]
    }

    fn args(a: &[&str]) -> Vec<String> {
        a.iter().map(|s| (*s).to_owned()).collect()
    }

    /// The idle check's block reaches the command line as exit 2 and its words on stderr (451 T183: asyncRewake wakes the session).
    #[test]
    fn the_idle_check_s_block_is_exit_2() {
        let g: [Guard; 0] = [];
        let d = crate::shared::tempdir::TempDir::new("cli-idle-check");
        let c = d.join("c");
        std::fs::create_dir_all(c.join("specs/385-x")).unwrap();
        let init = std::process::Command::new("git")
            .args(["init", "-q"])
            .arg(&c)
            .status();
        assert!(init.is_ok_and(|s| s.success()));
        std::fs::write(c.join("specs/385-x/tasks.md"), "- [ ] T02 the next thing\n").unwrap();
        std::fs::write(c.join("specs/385-x/spec.md"), "# F\n\n**Status**: Draft\n").unwrap();
        let start = r#"{"feature": "385-x", "task": "T02", "utc": "2026-10-18T23:00:00Z"}"#;
        std::fs::write(c.join(".git/task-starts.jsonl"), format!("{start}\n")).unwrap();
        std::fs::write(d.join("tr.jsonl"), "").unwrap();
        crate::shared::env::set("SET_DOWN_ROOT", &c);
        crate::shared::env::set("L7R_IDLE_CHECK_SECS", "0");
        let idle = serde_json::json!({"transcript_path": d.join("tr.jsonl"), "background_tasks": [], "session_id": "tr"});
        let said = cli(&args(&["--idle-check"]), &idle.to_string(), &g);
        // the status probe reads the list that Stop kept (451 T193)
        let status = cli(
            &args(&["--builder-status", &d.join("tr.jsonl").to_string_lossy()]),
            "",
            &g,
        );
        assert!(
            status
                .stdout
                .contains("No builder of an open task reads as running."),
            "{}",
            status.stdout
        );
        crate::shared::env::unset("L7R_IDLE_CHECK_SECS");
        crate::shared::env::unset("SET_DOWN_ROOT");
        assert_eq!(said.code, 2, "{}", said.stderr);
    }

    /// The guards' fixed order, by name (moved out of the test below when it passed its line limit, 451 T285).
    const ORDER: &[&str] = &[
        "pair-hooks",
        "gate-hooks",
        "measure-hooks",
        "no-poll-hooks",
        "main-tree-hooks",
        "event-log-hooks",
        "context-cap-hooks",
        "clone-sync-hooks",
        "idle-tests-hooks",
        "agent-stall-hooks",
        "stall-watchdog-hooks",
        "scratch-sweep-hooks",
        "finished-run-hooks",
        "engine-freeze-hooks",
        "gm-tree-hooks",
        "batching-hooks",
        "no-branch-hooks",
        "discard-hooks",
        "builder-pool-hooks",
        "conflict-marker-hooks",
        "gate-write-hooks",
        "feature-approval-hooks",
        "budget-change-hooks",
        "ledger-hooks",
        "archive-first-hooks",
        "claims-file-hooks",
        "readme-hooks",
        "download-copy-hooks",
        "phase-source-hooks",
        "new-file-hooks",
        "blocked-fetch-hooks",
        "set-down-hooks",
        "repo-safety-hooks",
        "agent-model-hooks",
        "wakeup-hooks",
        "agent-prefix-hooks",
        "workflow-hooks",
        "source-block-hooks",
        "house-style-hooks",
        "escalation-hooks",
        "review-round-hooks",
        "make-only-hooks",
        "guard-file-hooks",
        "record-edit-hooks",
        "check-bundle-hooks",
        "checks-hooks",
        "builder-stop-hooks",
        "static-runs-hooks",
        "research-switch-hooks",
        "shell-check-hooks",
    ];

    #[test]
    fn the_command_line_answers_each_form() {
        let g = [Guard {
            name: "x-hooks",
            events: &["PreToolUse"],
            matcher: "*",
            decide: refuse,
        }];
        let input = r#"{"tool_name": "Bash", "tool_input": {"command": "ls"}}"#;
        assert_eq!(cli(&args(&["--version"]), "", &g).stdout, "l7r-guard 0.1.0");
        assert_eq!(cli(&args(&["messages"]), "", &g).code, 64);
        // the idle check: a sub-agent's stop is silent at once (451 T183)
        assert_eq!(
            cli(&args(&["--idle-check"]), r#"{"agent_id": "a1"}"#, &g).code,
            0
        );
        assert!(cli(&args(&["--self-check"]), "", &g)
            .stdout
            .contains("1 guard(s) answered"));
        assert_eq!(cli(&args(&["PreToolUse"]), input, &g).code, 2);
        assert_eq!(
            cli(&args(&["--only", "x-hooks", "PreToolUse"]), input, &g).stderr,
            "refused"
        );
        assert_eq!(
            cli(&args(&["--only", "y-hooks", "PreToolUse"]), input, &g).code,
            1
        );
        assert_eq!(cli(&args(&["--only", "x-hooks"]), input, &g).code, 1);
        assert_eq!(
            cli(&args(&["--only", "x-hooks", "bogus"]), input, &g).code,
            1
        );
        assert_eq!(
            cli(&args(&["--only", "x-hooks", "PreToolUse"]), "not json", &g).code,
            0
        );
        assert_eq!(cli(&args(&[]), input, &g).code, 1);
        assert_eq!(
            cli(
                &args(&["--only", "x-hooks", ""]),
                r#"{"hook_event_name": "PreToolUse"}"#,
                &g
            )
            .code,
            2
        );
        let bad = cli(&args(&["PreToolUse"]), "not json", &g);
        assert!(bad.code == 0 && bad.stderr.is_empty() && bad.stdout.is_empty());
        assert!(guards().iter().map(|g| g.name).collect::<Vec<_>>() == ORDER);
    }
}
