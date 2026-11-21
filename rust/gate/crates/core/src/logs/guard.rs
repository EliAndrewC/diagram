//! The shell's door to the guard log (feature 449 T143, `ask:449-phase4-slices` Q12): `l7r-gate log guard <guard> <event> <detail> <sid>
//! [rule] [context]`, the hook input on stdin, is `scripts/hooks/lib/guardlog.sh`'s `guard_log` - its inline Python and the
//! `clone-resolve.sh resolve` it ran for the session's name, both deleted - over the guard's one writer (`shared::log::write_entry`) and
//! its one resolver (`shared::session`), since the shell cannot reach the guard's functions but by a command.
//!
//! WHY THE GATE'S BINARY, NOT THE GUARD'S: every caller but one is a gate, `sync-with-main.sh` or `make`'s `LOGESCAPE`, which has just run
//! `l7r-gate.sh escape reason-ok`, so the binary is there and current; and the suites' fixture trees stand `l7r-gate.sh` in as a link to
//! the real one, where a guard binary is found by its tree's own build directory under `HOME`, which a suite moves. The one hook-time
//! caller, `l7r-guard.sh`'s no-binary path, runs it with `L7R_GATE_STALE_OK` and `L7R_GATE_NO_BUILD`, so a hook never waits on a build.

use std::ffi::OsString;
use std::io::Read;
use std::os::unix::ffi::OsStrExt as _;
use std::path::Path;
use std::time::SystemTime;

use l7r_shared::log::{surrogate_escaped, write_entry, Entry};
use l7r_shared::pyjson::{loads, plain};
use l7r_shared::session::Session;
use serde_json::{json, Value};

use crate::Reply;

const USAGE: &str = "usage: l7r-gate log guard <guard> <event> <detail> <sid> [rule] [context] (the hook input on stdin)\n";

/// One entry into `dir`: exit 0 when it is written, 1 when it is not (the Python's raise, which `guard_log` swallowed), 2 for a usage
/// error. Each argument is read from its bytes as the Python's `sys.argv` read it (`surrogateescape`); the input is a dict only when it
/// parses as JSON (`json.load` of it raising made it `{}`); the context is its JSON, else the text itself, else none.
pub fn cli(args: &[OsString], stdin: &mut dyn Read, dir: &Path) -> Reply {
    let text: Vec<String> = args
        .iter()
        .map(|a| surrogate_escaped(a.as_bytes()))
        .collect();
    let [guard, event, detail, sid, rest @ ..] = text.as_slice() else {
        return Reply {
            stdout: String::new(),
            stderr: USAGE.to_owned(),
            code: 2,
        };
    };
    if rest.len() > 2 {
        return Reply {
            stdout: String::new(),
            stderr: USAGE.to_owned(),
            code: 2,
        };
    }
    let rule = rest.first().map_or("", String::as_str);
    let context = rest
        .get(1)
        .filter(|c| !c.is_empty())
        .map(|c| loads(c).unwrap_or_else(|_| Value::String(c.clone())));
    let mut raw = Vec::new();
    let _ = stdin.read_to_end(&mut raw);
    // read as Python's `json` reads (`pyjson::loads`: an integer past 64 bits keeps its digits, `NaN` and `Infinity` are numbers)
    let text = std::str::from_utf8(&raw).ok();
    let input: Value = text
        .and_then(|t| loads(t).ok())
        .unwrap_or_else(|| json!({}));
    // input that is not UTF-8: the writer's `json.load(open(...))` raised and wrote `{}`, but `clone-resolve.sh` read its stdin with
    // `surrogateescape` and still named the session - so the name is read from the bytes as that read them, a field only a string
    let naming = match text {
        Some(_) => plain(&input),
        None => loads(&surrogate_escaped(&raw)).map_or_else(|_| json!({}), |v| plain(&v)),
    };
    let name = Session::from_input(&naming).name();
    let entry = Entry {
        guard,
        event,
        detail,
        rule,
        context,
        input: &input,
        session_name: &name,
    };
    let code = i32::from(write_entry(dir, &entry, sid, SystemTime::now()).is_none());
    Reply {
        stdout: String::new(),
        stderr: String::new(),
        code,
    }
}

#[cfg(test)]
mod tests;
