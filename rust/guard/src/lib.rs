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
    ]
}

/// The command line: `<event>` decides the hook input on `stdin` with every guard; `--only <guard> <event>` with that one guard
/// (its suite's entry point, plan D4); `--self-check` runs every guard on a fixed input, which a build must pass to be kept as the
/// last good one (plan D7); `--version`. An input that is not JSON is answered with exit 1 - Claude Code's non-blocking error -
/// and its reason on stderr.
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
                .map(|g| Guard { ..*g })
                .collect();
            if one.is_empty() {
                return say(format!("l7r-guard: no guard named {name}"), 1);
            }
            decide(event, stdin, &one)
        }
        Some(event) => decide(event, stdin, all),
        None => say(
            "l7r-guard: <event> | --only <guard> <event> | --self-check | --version".to_owned(),
            1,
        ),
    }
}

fn decide(event: &str, stdin: &str, guards: &[Guard]) -> Reply {
    match serde_json::from_str(stdin) {
        Ok(input) => run(
            &mut Event {
                name: event.to_owned(),
                input,
            },
            guards,
        ),
        Err(e) => Reply {
            stdout: String::new(),
            stderr: format!("l7r-guard: the hook input is not JSON ({e})"),
            code: 1,
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
        assert_eq!(cli(&args(&[]), input, &g).code, 1);
        let bad = cli(&args(&["PreToolUse"]), "not json", &g);
        assert!(bad.code == 1 && bad.stderr.contains("not JSON"));
        assert!(
            guards().iter().map(|g| g.name).collect::<Vec<_>>()
                == ["pair-hooks", "gate-hooks", "measure-hooks"]
        );
    }
}
