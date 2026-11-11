//! `l7r-gate reviews-door`: the step-back bundle's one door to the reviews' port until T83 ports it (`ask:449-T89-reviews`): three
//! verbs, `gitdir`, `git` and `checkpoint_state`, `scripts/reviews_door.py`'s forwarders, one process a run, no logic of its own.

use std::io::{BufRead, Write};
use std::path::Path;

use serde_json::{json, Value};

use crate::Reply;

fn arg(args: &[Value], i: usize) -> &str {
    args.get(i).and_then(Value::as_str).unwrap_or("")
}

fn answer(verb: &str, args: &[Value]) -> Result<Value, String> {
    let root = Path::new(arg(args, 0));
    Ok(match verb {
        "gitdir" => super::gitdir(root).map_or(Value::Null, |g| json!(g.to_string_lossy())),
        "git" => {
            let rest: Vec<&str> = args.iter().skip(1).filter_map(Value::as_str).collect();
            super::git(root, &rest).map_or(Value::Null, Value::String)
        }
        "checkpoint_state" => Value::Object(super::checkpoint::state(root, None)),
        other => return Err(format!("reviews-door: no verb {other}")),
    })
}

/// The door's loop: until stdin closes.
pub fn serve(input: &mut dyn BufRead, output: &mut dyn Write) -> Reply {
    crate::checks_door::serve_with(input, output, &answer)
}

#[cfg(test)]
mod tests;
