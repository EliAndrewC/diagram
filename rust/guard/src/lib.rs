//! The guards on Claude Code's tool calls (feature 449 phase 1): one process for a hook event, every guard's check in it, their
//! answers merged by the hook protocol (`specs/449-rust-codebase/contracts/guard-protocol.md`). Each guard moves here from its shell
//! one task at a time (T006-T049); until then the dispatcher holds none.

pub mod guards;
pub mod protocol;
pub mod shared;

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
        guards::clone_sync_hooks::GUARD,
        guards::idle_tests_hooks::GUARD,
        guards::agent_stall_hooks::GUARD,
        guards::stall_watchdog_hooks::GUARD,
        guards::finished_run_hooks::GUARD,
        guards::engine_freeze_hooks::GUARD,
        guards::gm_tree_hooks::GUARD,
        guards::batching_hooks::GUARD,
        guards::no_branch_hooks::GUARD,
        guards::discard_hooks::GUARD,
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
        Some("--agent-stall") => guards::agent_stall_hooks::cli(&args[1..]),
        Some("--stall-watchdog") => guards::stall_watchdog_hooks::cli(&args[1..]),
        Some("--finished-run") => guards::finished_run_hooks::cli(&args[1..]),
        Some(event) => decide(event, stdin, all),
        None => say(
            "l7r-guard: <event> | --only <guard> <event> | --idle-tests <mode> | --agent-stall <mode> | --stall-watchdog <mode> | --finished-run <mode> | --self-check | --version".to_owned(),
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
        assert!(
            guards().iter().map(|g| g.name).collect::<Vec<_>>()
                == [
                    "pair-hooks",
                    "gate-hooks",
                    "measure-hooks",
                    "no-poll-hooks",
                    "main-tree-hooks",
                    "event-log-hooks",
                    "clone-sync-hooks",
                    "idle-tests-hooks",
                    "agent-stall-hooks",
                    "stall-watchdog-hooks",
                    "finished-run-hooks",
                    "engine-freeze-hooks",
                    "gm-tree-hooks",
                    "batching-hooks",
                    "no-branch-hooks",
                    "discard-hooks",
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
                    "shell-check-hooks"
                ]
        );
    }
}
