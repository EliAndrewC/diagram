//! `l7r-gate ci <subcommand>`, reached only through `make ci-*` (feature 127; from `ci/__main__.py`, which keeps `incremental` until T071).

use std::cell::RefCell;
use std::path::{Path, PathBuf};
use std::process::Command;

use super::aws::{Aws, CliAws};
use super::config::{self, Secrets};
use super::dispatch::{self, Context, Host};
use super::{decision, door, runlog, switches, via_make};

/// The parsed command line.
#[derive(Debug, Default)]
struct Args {
    command: String,
    rest: Vec<String>,
    full: bool,
    target: Option<String>,
    route: bool,
    compute: Option<String>,
    no_go: bool,
}

const COMMANDS: [&str; 8] = [
    "status",
    "check",
    "merge",
    "measure",
    "image",
    "door",
    "remote-spend",
    "remote-ok",
];

fn parse(args: &[String]) -> Result<Args, String> {
    let mut out = Args::default();
    let mut words = args.iter();
    while let Some(word) = words.next() {
        match word.as_str() {
            "--full" => out.full = true,
            "--route" => out.route = true,
            "--no-go" => out.no_go = true,
            "--target" => out.target = Some(words.next().ok_or("--target needs a value")?.clone()),
            "--compute" => {
                let value = words.next().ok_or("--compute needs a value")?;
                if config::rate_of(value) == config::RATE_PER_MIN && value != config::COMPUTE_TYPE {
                    return Err(format!("--compute: {value} is not a known compute type"));
                }
                out.compute = Some(value.clone());
            }
            other if out.command.is_empty() && COMMANDS.contains(&other) => {
                other.clone_into(&mut out.command);
            }
            other if !out.command.is_empty() && !other.starts_with("--") => {
                out.rest.push(other.to_owned());
            }
            other => return Err(format!("no such argument {other}")),
        }
    }
    if out.command.is_empty() {
        return Err(format!("a command is needed: {}", COMMANDS.join(", ")));
    }
    Ok(out)
}

/// What the real command runs with: printing as it goes, because a paid run's log is streamed.
pub(crate) struct LiveHost;

impl Host for LiveHost {
    fn sh(&self, args: &[&str], cwd: &Path, env: &[(&str, &str)]) -> (i32, String) {
        let done = Command::new(args[0])
            .args(&args[1..])
            .current_dir(cwd)
            .envs(env.iter().copied())
            .output();
        done.map_or_else(
            |e| (127, e.to_string()),
            |o| {
                (
                    o.status.code().unwrap_or(1),
                    format!(
                        "{}{}",
                        String::from_utf8_lossy(&o.stdout),
                        String::from_utf8_lossy(&o.stderr)
                    ),
                )
            },
        )
    }

    fn sleep(&self, secs: u64) {
        std::thread::sleep(std::time::Duration::from_secs(secs));
    }

    fn out(&self, line: &str) {
        println!("{line}");
    }

    fn err(&self, line: &str) {
        eprintln!("{line}");
    }
}

/// `aws` from the path, or `L7R_AWS` (the tests' fake).
pub(crate) fn real_client(secrets: &Secrets) -> Box<dyn Aws> {
    Box::new(CliAws {
        program: std::env::var_os("L7R_AWS").map_or_else(|| PathBuf::from("aws"), PathBuf::from),
        secrets: secrets.clone(),
    })
}

type Clients<'a> = &'a dyn Fn(&Secrets) -> Box<dyn Aws>;

/// What the command line is given rather than finds: the Python to ask, the host, the AWS client and the secrets.
pub(crate) struct World<'a> {
    pub python: &'a str,
    pub host: &'a dyn Host,
    pub clients: Clients<'a>,
    pub secrets: &'a dyn Fn(&Path) -> Result<Secrets, String>,
    pub specify: Option<&'a str>,
}

fn would_have(
    root: &Path,
    host: &dyn Host,
    what: &str,
    scope: &str,
    operation: Option<&str>,
    kind: &str,
) -> Result<(), String> {
    let est = decision::estimate(kind, 0.0, operation);
    let reason = format!("remote off: `make {what}` attempted and refused");
    runlog::write_would_have(root, what, scope, est.minutes, &reason)?;
    host.err(&format!("(recorded as would-have-dispatched, ~{:.0} build-min ~${:.2} - `make ci-status` lists these; the period's audit reads them)", est.minutes, est.cost_usd));
    Ok(())
}

fn remote_ok(a: &Args, root: &Path, host: &dyn Host) -> Result<i32, String> {
    let what = a.rest.first().map_or("ci-check", String::as_str);
    let Some(text) = switches::refusal(&switches::read(root), what) else {
        return Ok(0);
    };
    host.err(&text);
    let operation = if what.starts_with("ci-image") {
        Some("image")
    } else if what == "ci-check" {
        None
    } else {
        Some("operation")
    };
    let scope = if what == "ci-check" {
        "reference"
    } else {
        "operation"
    };
    would_have(root, host, what, scope, operation, "reference")?;
    Ok(1)
}

/// Only an expensive operation runs remotely (FR-010): the registry decides, so a cheap diagnostic is refused before any AWS call.
fn target_refusal(root: &Path, target: &str, host: &dyn Host) -> bool {
    let head = target.split_whitespace().next().unwrap_or_default();
    let ops = dispatch::operations(root);
    let cost = ops
        .iter()
        .find(|(name, _)| name == head)
        .map_or("not a registered operation", |(_, c)| c.as_str());
    if cost == "expensive" {
        return false;
    }
    host.out(&format!("ci-check: REFUSED - TARGET='{head}' is {cost}; only an EXPENSIVE operation runs remotely (cohort, cache-audit, regressions, ...). Run it locally."));
    true
}

fn verdict_file(root: &Path, verdict: &str) -> Result<(), String> {
    crate::codeid::stated(
        std::fs::write(root.join(".git/ci-verdict"), format!("{verdict}\n")),
        "ci-verdict",
    )
}

/// With remote off a merge is local-gated: it dispatches nothing, and its verdict is SKIP-VERIFIED only when a green local `make done` vouches for exactly the engine content it would produce.
fn local_gated(ctx: &Context<'_>, scope: &str) -> Result<i32, String> {
    let (text, d) = dispatch::status_text(ctx)?;
    let host = ctx.host;
    host.out(&text);
    verdict_file(ctx.root, &d.verdict)?;
    if d.skip_verified() {
        host.out("ci-merge: LOCAL-GATED (remote off) - a green local `make done` vouches for this engine content; the caller pushes directly, no build");
        return Ok(0);
    }
    if d.verdict == "REFUSE(remote-enabled)" {
        let reason = "remote off: the gated merge would have DISPATCHED (no green local `make done` on the merged engine content)";
        runlog::write_would_have(ctx.root, "ci-merge", scope, d.estimate.minutes, reason)?;
        host.out(&format!(
            "(recorded as would-have-dispatched, ~{:.0} build-min ~${:.2})",
            d.estimate.minutes, d.estimate.cost_usd
        ));
    }
    host.out(&format!("ci-merge: LOCAL-GATED (remote off) - {}: nothing landed. With remote off the merge needs a green local `make done` on the", d.verdict));
    host.out("  merged engine content: `git pull --no-rebase origin main` (if main moved), then `make done`, then `scripts/sync-with-main.sh done` again.");
    Ok(1)
}

fn status(a: &Args, root: &Path, world: &World<'_>, off: bool) -> Result<i32, String> {
    let (python, host) = (world.python, world.host);
    let empty = RefCell::new(Vec::new());
    if a.route {
        host.sh(&["git", "fetch", "-q", "origin"], root, &[]);
        let route = crate::delta::compute_delta(root, "origin/main", python)?.route();
        host.out(if route == "GATED" && off {
            "GATED-LOCAL"
        } else {
            route
        });
        return Ok(0);
    }
    let secrets = if off {
        None
    } else {
        match (world.secrets)(root) {
            Ok(s) => Some(s),
            Err(why) => {
                host.out(&format!("(no AWS lookup: {why})"));
                None
            }
        }
    };
    let owned = secrets.as_ref().map(world.clients);
    let scope = if a.full { "full" } else { "reference" };
    let ctx = Context {
        root,
        mode: decision::CHECK,
        scope,
        operation: a.target.as_deref(),
        compute: config::COMPUTE_TYPE,
        no_go: false,
        secrets,
        client: owned.as_deref(),
        host,
        python,
        specify: world.specify,
        poll_s: config::STREAM_POLL_S,
        events: empty,
    };
    host.out(&dispatch::status_text(&ctx)?.0);
    host.out(&runlog::remote_spend_report(root));
    Ok(0)
}

fn run_command(a: &Args, root: &Path, world: &World<'_>) -> Result<i32, String> {
    let (python, host) = (world.python, world.host);
    if a.command == "door" {
        let (ok, why) = door::check(root, "origin/main");
        host.out(&format!("bypass-audit: {why}"));
        return Ok(i32::from(!ok));
    }
    if a.command == "remote-spend" {
        host.out(&runlog::remote_spend_report(root));
        return Ok(0);
    }
    if a.command == "remote-ok" {
        return remote_ok(a, root, host);
    }
    if a.target
        .as_deref()
        .is_some_and(|t| target_refusal(root, t, host))
    {
        return Ok(1);
    }
    // read before any credential is loaded or any client built, so that with the switch thrown no AWS call is even possible
    let off = switches::read(root).remote_off();
    if a.command == "status" {
        return status(a, root, world, off);
    }
    let scope = if a.full { "full" } else { "reference" };
    let what = format!("ci-{}", a.command);
    let is_image = a.command == "image";
    let compute = if a.command == "check" || a.command == decision::MEASURE {
        a.compute.as_deref().unwrap_or(config::COMPUTE_TYPE)
    } else {
        config::COMPUTE_TYPE
    };
    let mut ctx = Context {
        root,
        mode: &a.command,
        scope,
        operation: a.target.as_deref(),
        compute,
        no_go: a.no_go && a.command == "check",
        secrets: None,
        client: None,
        host,
        python,
        specify: world.specify,
        poll_s: config::STREAM_POLL_S,
        events: RefCell::new(Vec::new()),
    };
    if off {
        if a.command == "merge" {
            return local_gated(&ctx, scope);
        }
        host.err(&switches::refusal(&switches::read(root), &what).unwrap_or_default());
        let kind = if a.target.is_some() || is_image {
            "operation"
        } else {
            scope
        };
        would_have(
            root,
            host,
            &what,
            kind,
            a.target.as_deref().or(is_image.then_some("image")),
            scope,
        )?;
        return Ok(1);
    }
    let secrets = (world.secrets)(root)?;
    let owned = (world.clients)(&secrets);
    ctx.secrets = Some(secrets);
    ctx.client = Some(owned.as_ref());
    if is_image {
        return Ok(dispatch::run_image(&ctx)?.rc);
    }
    if a.target.is_some() && a.command != "check" {
        return Err("--target is for ci-check only".to_owned());
    }
    if a.command == decision::MEASURE {
        host.out(&format!(
            "ci-measure: this run buys a NUMBER - no verified record, no push ({}, {scope} scope)",
            config::PROJECT_CHECK
        ));
    }
    let out = dispatch::run(&ctx)?;
    verdict_file(root, &out.verdict)?;
    Ok(out.rc)
}

/// The command line, after the make check.
pub(crate) fn run(args: &[String], root: &Path, world: &World<'_>) -> i32 {
    let done = parse(args)
        .map_err(|why| (2, why))
        .and_then(|parsed| run_command(&parsed, root, world).map_err(|why| (1, why)));
    done.unwrap_or_else(|(code, why)| {
        world.host.err(&format!("l7r-gate ci: {why}"));
        code
    })
}

/// `l7r-gate ci ...`: refused outside this project's make, at the top, so that a bare call cannot get as far as a network call.
pub(crate) fn guarded(
    args: &[String],
    root: &Path,
    procs: &dyn via_make::Procs,
    world: &World<'_>,
) -> crate::Reply {
    let tree = crate::codeid::script(root);
    let repo = tree.ancestors().nth(3).unwrap_or(root);
    if let Some(text) = via_make::refusal(procs, repo, "l7r.diagram.ci", "ci-status  (free)  |  make ci-check  |  make ci-merge  (paid; called by sync-with-main.sh)") {
        return crate::Reply { stdout: String::new(), stderr: text, code: 2 };
    }
    crate::Reply {
        stdout: String::new(),
        stderr: String::new(),
        code: run(args, root, world),
    }
}

pub(crate) fn entry(args: &[String], root: &Path) -> crate::Reply {
    let specify = std::env::var("SPECIFY_FEATURE").ok();
    guarded(
        args,
        root,
        &via_make::Live,
        &World {
            python: "python3",
            host: &LiveHost,
            clients: &real_client,
            secrets: &config::load_secrets,
            specify: specify.as_deref(),
        },
    )
}

#[cfg(test)]
mod tests;
