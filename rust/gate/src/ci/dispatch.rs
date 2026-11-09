//! The dispatch sequence (from `ci/dispatch.py`; FR-033 to FR-037, the GM's five arrows): the conditions, free; lint, format and types; the mailbox push and the build started parked; the local reference run; the go signal; the
//! log streamed. Everything external is behind `Host` and `Aws`, so that the tests can assert the two things that matter most: no `start_build` on any refusal, and `stop_build` only ever with the id this dispatcher got back.
//! A remote build runs `soak`, not `done` (GM 2026-09-05): `sync-in` merges main into every clone on every message, so the remote does the tier the laptop skips (`l7r/diagram/ci/CLAUDE.md`).

use std::cell::RefCell;
use std::path::{Path, PathBuf};
use std::time::Instant;

use serde_json::{json, Value};

use super::aws::{Aws, AwsError};
use super::config::{self, Secrets};
use super::decision::{self, Decision, VerifiedRecord};
use super::runlog::{self, Remote};
use super::{door, features, imagecheck, switches};
use crate::delta;
use crate::state;

pub(crate) trait Host {
    fn sh(&self, args: &[&str], cwd: &Path, env: &[(&str, &str)]) -> (i32, String);
    fn sleep(&self, secs: u64);
    fn out(&self, line: &str);
    fn err(&self, line: &str);
}

/// What one dispatch works with.
pub(crate) struct Context<'a> {
    pub root: &'a Path,
    pub mode: &'a str,
    pub scope: &'a str,
    pub operation: Option<&'a str>,
    pub compute: &'a str,
    pub no_go: bool,
    pub secrets: Option<Secrets>,
    pub client: Option<&'a dyn Aws>,
    pub host: &'a dyn Host,
    pub python: &'a str,
    pub poll_s: u64,
    pub events: RefCell<Vec<String>>,
}

#[derive(Clone, Debug, Default, PartialEq)]
pub(crate) struct Outcome {
    pub rc: i32,
    pub verdict: String,
    pub build_id: String,
    pub result: String,
    pub minutes: f64,
}

fn refused(verdict: &str) -> Outcome {
    Outcome {
        rc: 1,
        verdict: verdict.to_owned(),
        ..Outcome::default()
    }
}

fn aws<T>(done: Result<T, AwsError>) -> Result<T, String> {
    done.map_err(|e| e.text())
}

/// The registered operations' (make target, cost), read from the one registry; it stays in `_invocation.py`, with the Python entry points it names, until phase 4.
pub(crate) fn operations(root: &Path) -> Vec<(String, String)> {
    let text = std::fs::read_to_string(root.join("l7r/diagram/_invocation.py")).unwrap_or_default();
    text.lines()
        .filter_map(|l| {
            let (_, rest) = l.trim().strip_prefix("\"l7r.")?.split_once("\": (\"")?;
            let (target, rest) = rest.split_once("\", \"")?;
            Some((target.to_owned(), rest.split_once('"')?.0.to_owned()))
        })
        .collect()
}

/// The registered name of an operation target: a cache location must not be keyed on a free-form string, or `cohort SEEDS=8` and `cohort SEEDS=9` would each grow an S3 object (feature 177).
fn registered_operation(root: &Path, target: Option<&str>) -> Option<String> {
    let head = target?.split_whitespace().next()?;
    operations(root)
        .iter()
        .find(|(name, _)| name == head)
        .map(|(name, _)| name.clone())
}

/// Where CodeBuild keeps the generation cache: bounded by construction, one object a project, scope and registered operation (features 175, 177), and never a commit.
fn cache_location(bucket: &str, project: &str, scope: &str, operation: Option<&str>) -> String {
    let tail = operation.map_or_else(String::new, |o| format!("/{o}"));
    format!("{bucket}/cache/{project}/{scope}{tail}")
}

fn mailbox(root: &Path) -> String {
    let name = root
        .file_name()
        .map_or_else(String::new, |n| n.to_string_lossy().into_owned());
    format!("{}{name}", config::MAILBOX_PREFIX)
}

/// What a remote build runs; the scope still selects, so a full soak stays available the moment the suite has anything in it.
pub(crate) fn make_target(operation: Option<&str>, scope: &str) -> String {
    operation.map_or_else(
        || {
            if scope == "full" {
                "soak FULL=1".to_owned()
            } else {
                "soak".to_owned()
            }
        },
        str::to_owned,
    )
}

fn would_be_tree(ctx: &Context<'_>) -> (Option<String>, String) {
    let (rc, out) = ctx.host.sh(
        &["git", "merge-tree", "--write-tree", "origin/main", "HEAD"],
        ctx.root,
        &[],
    );
    if rc != 0 {
        return (None, out.trim().to_owned());
    }
    (
        out.lines().next().map(|l| l.trim().to_owned()),
        String::new(),
    )
}

fn verified_lookup(
    ctx: &Context<'_>,
    tree: Option<&str>,
) -> Result<Option<VerifiedRecord>, String> {
    let (Some(tree), Some(client), Some(secrets)) = (tree, ctx.client, ctx.secrets.as_ref()) else {
        return Ok(None);
    };
    let key = delta::engine_key(ctx.root, tree, ctx.python)?;
    let Some(body) = aws(client.get_object(&secrets.ci_bucket, &format!("verified/{key}.json")))?
    else {
        return Ok(None);
    };
    let d: Value = serde_json::from_slice(&body).unwrap_or_default();
    let of = |k: &str, default: &str| d[k].as_str().unwrap_or(default).to_owned();
    Ok(Some(VerifiedRecord {
        tree: of("tree", tree),
        build_id: of("build_id", "?"),
        scope: of("scope", "reference"),
        utc: of("utc", ""),
    }))
}

fn remote_off_reason(root: &Path) -> Option<String> {
    let sw = switches::read(root);
    let a = &sw.remote;
    let who = if a.who.is_empty() { "?" } else { &a.who };
    sw.remote_off().then(|| format!("remote is OFF since {} by {who}: {} - nothing dispatches; `make ci-on REASON=...` releases it", a.utc, a.why))
}

/// CodeBuild bills every phase from provisioning on, rounded up to the minute.
pub(crate) fn billed_minutes(build: &Value) -> f64 {
    let secs: i64 = build["phases"]
        .as_array()
        .into_iter()
        .flatten()
        .filter(|p| {
            !["SUBMITTED", "QUEUED", "COMPLETED"]
                .contains(&p["phaseType"].as_str().unwrap_or_default())
        })
        .map(|p| p["durationInSeconds"].as_i64().unwrap_or(0))
        .sum();
    if secs == 0 {
        return 0.0;
    }
    (((secs + 59) / 60).max(1)) as f64
}

fn describe_state(st: Option<&state::State>, now_hash: &str) -> String {
    st.map_or_else(
        || "no local check recorded in this clone".to_owned(),
        |s| {
            format!(
                "{} from `make {}` at {} ({}), against {}",
                s.event,
                s.target,
                s.utc,
                s.commit,
                if s.hash == now_hash {
                    "current code"
                } else {
                    "DIFFERENT code (a source edit happened since)"
                }
            )
        },
    )
}

/// `make ci-status`: the whole picture, with no AWS call unless a lookup is possible and the route is gated.
pub(crate) fn status_text(ctx: &Context<'_>) -> Result<(String, Decision), String> {
    ctx.host
        .sh(&["git", "fetch", "-q", "origin"], ctx.root, &[]);
    let delta_now = delta::compute_delta(ctx.root, "origin/main", ctx.python)?;
    let st = state::read(ctx.root)?;
    let now = state::current_hash(ctx.root, ctx.python)?;
    let active = features::active_feature(ctx.root);
    let feat = features::feature_status(ctx.root, active.as_deref(), ctx.python);
    let (tree, conflict) = would_be_tree(ctx);
    let mut verified = if delta_now.route() == "GATED" {
        verified_lookup(ctx, tree.as_deref())?
    } else {
        None
    };
    // a green local `make done` vouches for the engine content it tested, when main adds none (GM 2026-08-25)
    let key = tree
        .as_deref()
        .map(|t| delta::engine_key(ctx.root, t, ctx.python))
        .transpose()?;
    if let (None, Some(t), Some(s), Some(k)) = (&verified, &tree, &st, &key) {
        if s.event == "green-local"
            && s.target == "done"
            && !s.engine_key.is_empty()
            && s.engine_key == *k
        {
            verified = Some(VerifiedRecord {
                tree: t.clone(),
                build_id: format!("local:make-done@{}", s.commit),
                scope: "reference".to_owned(),
                utc: s.utc.clone(),
            });
        }
    }
    let off = remote_off_reason(ctx.root);
    let mode = if ctx.mode == decision::MERGE {
        decision::MERGE
    } else {
        decision::CHECK
    };
    let d = decision::decide(decision::Inputs {
        delta: &delta_now,
        state: st.as_ref(),
        now_hash: &now,
        verified,
        breaker: None,
        mode,
        feature: Some(&feat),
        scope: ctx.scope,
        month_to_date_usd: runlog::month_to_date(ctx.root, None),
        operation: ctx.operation,
        remote_off: off.as_deref(),
        measure: ctx.mode == decision::MEASURE,
    });
    let base: String = delta_now.base.chars().take(12).collect();
    let tree_line = match (&tree, &key) {
        (Some(t), Some(k)) => format!("would-be tree: {}, engine key {} (what a verified record is keyed by)", &t[..t.len().min(12)], &k[..k.len().min(12)]),
        _ => format!("would-be tree: MERGE CONFLICT with origin/main - merge main locally, resolve, commit:\n  {}", conflict.chars().take(400).collect::<String>()),
    };
    let text = format!(
        "delta: merge-base {base}, {} file(s), route {}\nstate: {}\n{tree_line}\n{}",
        delta_now.files.len(),
        delta_now.route(),
        describe_state(st.as_ref(), &now),
        decision::render(&d, ctx.mode, ctx.scope)
    );
    Ok((text, d))
}

fn event(ctx: &Context<'_>, what: String) {
    ctx.events.borrow_mut().push(what);
}

/// Everything before a build exists: `Err` is the outcome to return, with nothing dispatched.
fn conditions(ctx: &Context<'_>, t0: Instant) -> Result<Result<String, Outcome>, String> {
    let (text, d) = status_text(ctx)?;
    ctx.host.out(&text);
    let (Some(tree), _) = would_be_tree(ctx) else {
        ctx.host.out("ci: REFUSED - the merge with the latest main conflicts locally; nothing dispatched (a paid build would only have told you the same)");
        return Ok(Err(refused("REFUSE(merge-conflict)")));
    };
    if ctx.scope == "full" {
        let (ok, why) = door::check(ctx.root, "origin/main");
        ctx.host.out(&format!("ci: FULL scope - {why}"));
        if !ok {
            return Ok(Err(refused("REFUSE(full-not-authorized)")));
        }
    }
    if !d.dispatches() {
        ctx.host.out(&if d.skip_verified() {
            "ci: SKIP-VERIFIED - no build; the caller pushes directly".to_owned()
        } else {
            format!("ci: {} - nothing dispatched", d.verdict)
        });
        if d.skip_verified() {
            let rec = d
                .conditions
                .iter()
                .find(|c| c.name == "tree-not-already-verified")
                .map_or("", |c| c.why.as_str());
            let by = rec
                .rsplit_once(" by ")
                .map_or("", |(_, r)| r)
                .split(' ')
                .next()
                .unwrap_or_default();
            let target = format!("ci-{}", ctx.mode);
            runlog::write_remote(
                ctx.root,
                &Remote {
                    target: &target,
                    scope: ctx.scope,
                    seconds: t0.elapsed().as_secs(),
                    result: "skip-verified",
                    build_id: by,
                    minutes: 0.0,
                    reason: rec,
                    rate: config::RATE_PER_MIN,
                    compute: config::COMPUTE_TYPE,
                },
            )?;
        }
        return Ok(Err(Outcome {
            rc: i32::from(!d.skip_verified()),
            verdict: d.verdict,
            ..Outcome::default()
        }));
    }
    let (rc, out) = ctx.host.sh(
        &[
            "make",
            "--no-print-directory",
            "static",
            "format",
            "typecheck",
        ],
        ctx.root,
        &[],
    );
    event(ctx, format!("static:{rc}"));
    if rc != 0 {
        ctx.host.out(&out);
        ctx.host
            .out("ci: static/format/types FAILED locally - nothing dispatched");
        return Ok(Err(refused("REFUSE(static)")));
    }
    ctx.host.out("ci: static, format, types clean - starting the build (parked) while the reference check runs locally");
    Ok(Ok(tree))
}

fn push_mailbox(ctx: &Context<'_>, secrets: &Secrets) -> (i32, String) {
    let askpass = ctx.root.join("scripts/git-askpass-token.sh");
    let (url, dest) = (
        format!("https://github.com/{}", config::GITHUB_REPO),
        format!("HEAD:refs/heads/{}", mailbox(ctx.root)),
    );
    ctx.host.sh(
        &["git", "push", "-q", "--force", &url, &dest],
        ctx.root,
        &[
            ("GIT_ASKPASS", &askpass.to_string_lossy()),
            ("GITHUB_TOKEN", &secrets.github_pat),
            ("GIT_TERMINAL_PROMPT", "0"),
        ],
    )
}

/// The custom image, once its marker exists, with a warning when it no longer matches the tree's recipe.
fn image_override(
    ctx: &Context<'_>,
    client: &dyn Aws,
    secrets: &Secrets,
    request: &mut Value,
) -> Result<(), String> {
    let marker = aws(client.get_object(&secrets.ci_bucket, "image/latest.txt"))?;
    event(
        ctx,
        if marker.is_some() {
            "image:custom"
        } else {
            "image:stock"
        }
        .to_owned(),
    );
    let Some(marker) = marker else {
        return Ok(());
    };
    request["imageOverride"] = json!(format!("{}:latest", secrets.ecr_image));
    request["imagePullCredentialsTypeOverride"] = json!("SERVICE_ROLE");
    if let Some(built_at) = imagecheck::marker_commit(&String::from_utf8_lossy(&marker)) {
        let mut args = vec![
            "git",
            "diff",
            "--name-only",
            built_at.as_str(),
            "HEAD",
            "--",
        ];
        args.extend(imagecheck::IMAGE_INPUTS);
        let (rc, changed) = ctx.host.sh(&args, ctx.root, &[]);
        if let Some(line) = imagecheck::staleness_line(&changed).filter(|_| rc == 0) {
            ctx.host.out(&format!("ci: {line}"));
            event(ctx, "image:stale".to_owned());
        }
    }
    Ok(())
}

fn env_row(name: &str, value: &str) -> Value {
    json!({"name": name, "value": value, "type": "PLAINTEXT"})
}

fn buildspec(ctx: &Context<'_>, name: &str) -> Result<String, String> {
    crate::codeid::stated(
        std::fs::read_to_string(ctx.root.join("buildspec").join(name)),
        name,
    )
}

/// The request that starts a parked build: the buildspec and the cache travel with the call, since project state is something nobody can review in a diff.
fn start_request(
    ctx: &Context<'_>,
    client: &dyn Aws,
    secrets: &Secrets,
    project: &str,
    sha: &str,
) -> Result<Value, String> {
    let target = make_target(ctx.operation, ctx.scope);
    let feature = features::active_feature(ctx.root).unwrap_or_default();
    let ci_scope = if ctx.operation.is_some() {
        "operation"
    } else {
        ctx.scope
    };
    let env = vec![
        env_row("GIT_SHA", sha),
        env_row("MAILBOX", &mailbox(ctx.root)),
        env_row("MAKE_TARGET", &target),
        env_row("CI_MODE", ctx.mode),
        env_row("CI_SCOPE", ci_scope),
        env_row("COMPUTE_TYPE", ctx.compute),
        env_row("PARK_TIMEOUT_S", &config::PARK_TIMEOUT_S.to_string()),
        env_row("SPECIFY_FEATURE", &feature),
    ];
    let op_key = registered_operation(ctx.root, ctx.operation);
    let mut request = json!({"projectName": project, "buildspecOverride": buildspec(ctx, &format!("{}.yml", ctx.mode))?, "environmentVariablesOverride": env, "computeTypeOverride": ctx.compute, "cacheOverride": {"type": "S3", "location": cache_location(&secrets.ci_bucket, project, ctx.scope, op_key.as_deref())}});
    image_override(ctx, client, secrets, &mut request)?;
    event(
        ctx,
        format!(
            "cache:{}{}",
            ctx.scope,
            op_key.map_or_else(String::new, |o| format!("/{o}"))
        ),
    );
    Ok(request)
}

/// The record of a settled run, then a summary for the session.
fn logged(
    ctx: &Context<'_>,
    t0: Instant,
    scope: &str,
    result: &str,
    build_id: &str,
    minutes: f64,
    reason: &str,
) -> Result<f64, String> {
    let rate = config::rate_of(ctx.compute);
    let target = format!("ci-{}", ctx.mode);
    runlog::write_remote(
        ctx.root,
        &Remote {
            target: &target,
            scope,
            seconds: t0.elapsed().as_secs(),
            result,
            build_id,
            minutes,
            reason,
            rate,
            compute: ctx.compute,
        },
    )?;
    Ok(rate)
}

fn abort_on_red(
    ctx: &Context<'_>,
    client: &dyn Aws,
    t0: Instant,
    build_id: &str,
    out: &str,
) -> Result<Outcome, String> {
    ctx.host.out(out);
    aws(client.stop_build(build_id))?;
    event(ctx, format!("stop_build:{build_id}"));
    state::write(
        ctx.root,
        "failed-gate",
        &format!("ci-{}", ctx.mode),
        false,
        ctx.python,
    )?;
    let builds = aws(client.batch_get_builds(build_id))?;
    let mins = billed_minutes(&builds["builds"][0]);
    let rate = logged(
        ctx,
        t0,
        ctx.scope,
        "aborted-local-reference",
        build_id,
        mins,
        "reference settlement red locally; parked build stopped",
    )?;
    ctx.host.out(&format!("ci: reference settlement RED locally - build {build_id} stopped ({mins:.0} billed min, ~${:.2})", mins * rate));
    Ok(Outcome {
        rc: 1,
        verdict: "ABORTED(local-reference)".to_owned(),
        build_id: build_id.to_owned(),
        result: "aborted-local-reference".to_owned(),
        minutes: mins,
    })
}

fn start(
    ctx: &Context<'_>,
    client: &dyn Aws,
    secrets: &Secrets,
) -> Result<Result<String, Outcome>, String> {
    let (rc, out) = push_mailbox(ctx, secrets);
    event(ctx, format!("push:{rc}"));
    if rc != 0 {
        ctx.host.out(&out);
        ctx.host.out(&format!(
            "ci: could not push the mailbox branch {} to GitHub - nothing dispatched",
            mailbox(ctx.root)
        ));
        return Ok(Err(refused("REFUSE(mailbox-push)")));
    }
    let (_, sha) = ctx.host.sh(&["git", "rev-parse", "HEAD"], ctx.root, &[]);
    let project = if ctx.mode == decision::MERGE {
        config::PROJECT_MERGE
    } else {
        config::PROJECT_CHECK
    };
    let request = start_request(ctx, client, secrets, project, sha.trim())?;
    let started = match client.start_build(&request) {
        Ok(started) => started,
        Err(AwsError::Denied { operation, message }) => {
            event(ctx, "start_build:denied".to_owned());
            if operation.contains("StartBuild") || message.contains("StartBuild") {
                ctx.host.out("ci: REFUSED - the monthly hard stop has TRIPPED (FR-021): IAM policy gm-assistant-ci-circuit-breaker is attached to user gm-assistant-ci and denies codebuild:StartBuild.");
                ctx.host.out("    To re-enable (admin key): aws iam detach-user-policy --user-name gm-assistant-ci --policy-arn arn:aws:iam::130071571821:policy/gm-assistant-ci-circuit-breaker");
                return Ok(Err(refused("REFUSE(breaker-tripped)")));
            }
            ctx.host
                .out(&format!("ci: AWS refused {operation}: {message}"));
            return Ok(Err(refused("REFUSE(aws-denied)")));
        }
        Err(e) => return Err(e.text()),
    };
    let build_id = started["build"]["id"]
        .as_str()
        .unwrap_or_default()
        .to_owned();
    event(ctx, format!("start_build:{build_id}"));
    ctx.host.out(&format!(
        "ci: build {build_id} started on {project} / {} (parked at wait-go, {} s ceiling)",
        ctx.compute,
        config::PARK_TIMEOUT_S
    ));
    Ok(Ok(build_id))
}

fn uuid_of(build_id: &str) -> &str {
    build_id.rsplit(':').next().unwrap_or(build_id)
}

/// The five arrows; the outcome's `rc` is what the make target exits with.
pub(crate) fn run(ctx: &Context<'_>) -> Result<Outcome, String> {
    let t0 = Instant::now();
    let (Some(client), Some(secrets)) = (ctx.client, ctx.secrets.as_ref()) else {
        return Err("run needs a client and secrets".to_owned());
    };
    if let Err(outcome) = conditions(ctx, t0)? {
        return Ok(outcome);
    }
    let build_id = match start(ctx, client, secrets)? {
        Ok(id) => id,
        Err(outcome) => return Ok(outcome),
    };
    // the reference run stays local on purpose: it stops a paid build being spent on a map that is already red
    let (rc, out) = ctx.host.sh(
        &["make", "--no-print-directory", "_reference"],
        ctx.root,
        &[],
    );
    event(ctx, format!("reference:{rc}"));
    if rc != 0 {
        return abort_on_red(ctx, client, t0, &build_id, &out);
    }
    let go = format!("go/{}", uuid_of(&build_id));
    if ctx.no_go {
        event(ctx, "go:withheld".to_owned());
        ctx.host.out(&format!(
            "ci: NO_GO=1 - the go signal is WITHHELD; the build must abort itself after {} s",
            config::PARK_TIMEOUT_S
        ));
    } else {
        aws(client.put_object(&secrets.ci_bucket, &go, b"go"))?;
        event(ctx, "go".to_owned());
        ctx.host
            .out("ci: reference settlement clean - build released");
    }
    let build = stream(ctx, client, secrets, &build_id)?;
    let result = build["buildStatus"].as_str().unwrap_or("?").to_owned();
    let mins = billed_minutes(&build);
    // a build that died before wait-go never consumed its signal
    if aws(client.get_object(&secrets.ci_bucket, &go))?.is_some() {
        aws(client.delete_object(&secrets.ci_bucket, &go))?;
        event(ctx, "go:cleaned".to_owned());
    }
    let ok = result == "SUCCEEDED";
    if !ok {
        state::write(
            ctx.root,
            "failed-gate",
            &format!("ci-{}", ctx.mode),
            false,
            ctx.python,
        )?;
    }
    let fetched = fetch_artifacts(ctx, client, secrets, &build_id)?;
    let scope = if ctx.operation.is_some() {
        "operation"
    } else {
        ctx.scope
    };
    let rate = logged(
        ctx,
        t0,
        scope,
        &result,
        &build_id,
        mins,
        &make_target(ctx.operation, ctx.scope),
    )?;
    let artifacts = if fetched.is_empty() {
        String::new()
    } else {
        format!("; {} artifact file(s) fetched", fetched.len())
    };
    ctx.host.out(&format!(
        "ci: build {build_id} {result} - {mins:.0} billed min on {}, ~${:.2}{artifacts}",
        ctx.compute,
        mins * rate
    ));
    Ok(Outcome {
        rc: i32::from(!ok),
        verdict: "DISPATCHED".to_owned(),
        build_id,
        result,
        minutes: mins,
    })
}

fn print_page(ctx: &Context<'_>, page: &Value, token: &mut Option<String>) -> usize {
    let events = page["events"].as_array().map_or(&[][..], Vec::as_slice);
    for ev in events {
        ctx.host.out(&format!(
            "  | {}",
            ev["message"]
                .as_str()
                .unwrap_or_default()
                .trim_end_matches('\n')
        ));
    }
    if let Some(next) = page["nextForwardToken"].as_str().filter(|t| !t.is_empty()) {
        *token = Some(next.to_owned());
    }
    events.len()
}

/// Poll the build and print its log as it is written (R5); once the build is over, drain what CloudWatch still holds, since a poll that stopped at a terminal status once lost the failing command's output (build 93af6342).
fn stream(
    ctx: &Context<'_>,
    client: &dyn Aws,
    secrets: &Secrets,
    build_id: &str,
) -> Result<Value, String> {
    let (mut token, mut phase): (Option<String>, String) = (None, String::new());
    loop {
        let builds = aws(client.batch_get_builds(build_id))?;
        let build = builds["builds"][0].clone();
        let cur = build["currentPhase"]
            .as_str()
            .unwrap_or_default()
            .to_owned();
        if cur != phase {
            ctx.host.out(&format!("ci: [{cur}]"));
            phase = cur;
        }
        let name = build["logs"]["streamName"]
            .as_str()
            .filter(|s| !s.is_empty())
            .unwrap_or(uuid_of(build_id))
            .to_owned();
        let group = build["logs"]["groupName"]
            .as_str()
            .filter(|s| !s.is_empty())
            .unwrap_or(&secrets.log_group)
            .to_owned();
        print_page(
            ctx,
            &aws(client.get_log_events(&group, &name, token.as_deref()))?,
            &mut token,
        );
        if build["buildStatus"] != "IN_PROGRESS" {
            for _ in 0..50 {
                if print_page(
                    ctx,
                    &aws(client.get_log_events(&group, &name, token.as_deref()))?,
                    &mut token,
                ) == 0
                {
                    break;
                }
            }
            return Ok(build);
        }
        ctx.host.sleep(ctx.poll_s);
    }
}

/// Full perf snapshots go to `dev/perf-log/`; an operation's report to `dev/ci-artifacts/<uuid>/`.
fn fetch_artifacts(
    ctx: &Context<'_>,
    client: &dyn Aws,
    secrets: &Secrets,
    build_id: &str,
) -> Result<Vec<PathBuf>, String> {
    let uuid = uuid_of(build_id);
    let prefix = format!("artifacts/{uuid}/");
    let mut got = Vec::new();
    for key in aws(client.list_prefix(&secrets.ci_bucket, &prefix))? {
        let rel = key.strip_prefix(&prefix).unwrap_or(&key);
        if rel.is_empty() {
            continue;
        }
        let dest = rel.strip_prefix("perf-log/").map_or_else(
            || ctx.root.join("dev/ci-artifacts").join(uuid).join(rel),
            |tail| ctx.root.join("dev/perf-log").join(tail),
        );
        let Some(body) = aws(client.get_object(&secrets.ci_bucket, &key))? else {
            continue;
        };
        crate::codeid::stated(
            std::fs::create_dir_all(dest.parent().unwrap_or(ctx.root)),
            "dev/",
        )?;
        crate::codeid::stated(std::fs::write(&dest, body), "an artifact")?;
        got.push(dest);
    }
    Ok(got)
}

/// `make ci-image`: one build on the check project that docker-builds `Dockerfile.ci` and pushes it to ECR.
pub(crate) fn run_image(ctx: &Context<'_>) -> Result<Outcome, String> {
    let t0 = Instant::now();
    let (Some(client), Some(secrets)) = (ctx.client, ctx.secrets.as_ref()) else {
        return Err("run_image needs a client and secrets".to_owned());
    };
    let (_, sha) = ctx.host.sh(&["git", "rev-parse", "HEAD"], ctx.root, &[]);
    let (rc, out) = push_mailbox(ctx, secrets);
    if rc != 0 {
        ctx.host.out(&out);
        return Ok(refused("REFUSE(mailbox-push)"));
    }
    let request = json!({"projectName": config::PROJECT_CHECK, "buildspecOverride": buildspec(ctx, "image.yml")?, "environmentVariablesOverride": [env_row("GIT_SHA", sha.trim()), env_row("MAILBOX", &mailbox(ctx.root))], "computeTypeOverride": "BUILD_GENERAL1_MEDIUM", "privilegedModeOverride": true});
    let started = aws(client.start_build(&request))?;
    let build_id = started["build"]["id"]
        .as_str()
        .unwrap_or_default()
        .to_owned();
    event(ctx, format!("start_build:{build_id}"));
    let build = stream(ctx, client, secrets, &build_id)?;
    let result = build["buildStatus"].as_str().unwrap_or("?").to_owned();
    let mins = billed_minutes(&build);
    runlog::write_remote(
        ctx.root,
        &Remote {
            target: "ci-image",
            scope: "image",
            seconds: t0.elapsed().as_secs(),
            result: &result,
            build_id: &build_id,
            minutes: mins,
            reason: "Dockerfile.ci -> ECR",
            rate: config::RATE_PER_MIN,
            compute: config::COMPUTE_TYPE,
        },
    )?;
    ctx.host.out(&format!(
        "ci-image: build {build_id} {result} - {mins:.0} billed min"
    ));
    Ok(Outcome {
        rc: i32::from(result != "SUCCEEDED"),
        verdict: "DISPATCHED".to_owned(),
        build_id,
        result,
        minutes: mins,
    })
}

#[cfg(test)]
mod tests;
