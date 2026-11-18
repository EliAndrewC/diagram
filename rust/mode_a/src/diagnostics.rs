//! The reviewer's two picture measures (feature 231): [`picture_diff`] (`make picture-diff`) and [`page_lit`] (`make page-lit`), ported
//! from `l7r/diagram/tools/picture_diff.py` and `page_lit.py` by feature 449 T150 (the engine port's step 2) and the Python deleted;
//! their command lines read as argparse read them ([`args`]) and their images as PIL read them ([`image`]).
//!
//! Research: the reviewer's measures - NONE: measurements for a reviewer, no map decision

use l7r_gate_core::Reply;
use l7r_gate_research::Error;

pub mod args;
pub mod image;
pub mod page_lit;
pub mod picture_diff;

/// A pixel count or index as a float: an image's pixels are far under 2^52, so the cast is exact.
#[expect(
    clippy::cast_precision_loss,
    reason = "pixel counts and indices, far under 2^52"
)]
fn f(n: usize) -> f64 {
    n as f64
}

fn reply(stdout: String, stderr: &str, code: i32) -> Reply {
    Reply {
        stdout,
        stderr: stderr.to_owned(),
        code,
    }
}

/// A malformed command line: exit 2, nothing on stdout, the usage and one line naming the tool and the complaint (`ask:449-usage-text`:
/// argparse's own words are not bound).
fn usage(usage: &str, tool: &str, complaint: &str) -> Reply {
    reply(
        String::new(),
        &format!("{usage}l7r-mode-a {tool}: error: {complaint}\n"),
        2,
    )
}

/// A measure's report, or its refusal: a `SystemExit` message as Python printed one (the message alone, exit 1), any other the last
/// line of the traceback it ended on.
fn answer(done: Result<String, Error>) -> Reply {
    match done {
        Ok(out) => reply(out, "", 0),
        Err(e) if e.kind == "SystemExit" => reply(String::new(), &format!("{}\n", e.message), 1),
        Err(e) => reply(String::new(), &crate::py::uncaught(&e), 1),
    }
}
