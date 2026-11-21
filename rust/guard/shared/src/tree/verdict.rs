//! The verdict on one hook input (`judge`), the rewrite into the clone it re-judges, and the words the session is told
//! (`context_line`, `explain`) - the main-tree guard's half of the walk, split from `tree.rs` (451 T42, its file-scale bar).

use std::path::Path;

use fancy_regex::Captures;
use serde_json::{json, Value};

use super::{join, re, relpath, walk_judged, Target, Walk, FUNCTION_DEF};

/// Every command-position `cd <main>[/sub]` of the original text made `cd <clone>[/sub]` (`_rewrite_cds`).
fn rewrite_cds(cmd: &str, main: &str, clone: &str) -> String {
    let pat = re(&format!(
        r#"(?m)((?:^|[;&|(\n]|&&|\|\|)\s*(?:\(\s*)?(?:cd|pushd)\s+)(["']?){}(?=/(?!\.clones(?:/|$))|["'\s;&|)]|$)"#,
        fancy_regex::escape(main)
    ));
    pat.replace_all(cmd, |c: &Captures| {
        format!(
            "{}{}{clone}",
            c.get(1).map_or("", |m| m.as_str()),
            c.get(2).map_or("", |m| m.as_str())
        )
    })
    .into_owned()
}

/// The verdict on one hook input (`judge`): its kind, reason and cause, the walk's context, and a rewrite's command.
#[derive(Debug, Clone)]
pub struct Verdict {
    pub verdict: &'static str,
    pub reason: &'static str,
    pub cause: &'static str,
    pub cwd: Option<String>,
    pub walk: Walk,
    pub clone: Option<String>,
    pub prepended: Option<bool>,
    pub command: Option<String>,
}

impl Verdict {
    /// The verdict as the Python's JSON, its `hook` left out (`log-context`).
    #[must_use]
    pub fn context(&self) -> Value {
        let targets: Vec<Value> = self
            .walk
            .targets
            .iter()
            .map(|t| json!({"path": t.path, "class": t.class, "how": t.how, "segment": t.segment}))
            .collect();
        let mut ctx = json!({
            "cwd": self.cwd, "standing": self.walk.standing, "final_dir": self.walk.final_dir, "cd_into_main": self.walk.cd_into_main,
            "targets": targets, "clone": self.clone,
        });
        if let Some(p) = self.prepended {
            ctx["prepended"] = Value::Bool(p);
        }
        let mut out = json!({"verdict": self.verdict, "reason": self.reason, "cause": self.cause, "context": ctx});
        if let Some(c) = &self.command {
            out["command"] = Value::String(c.clone());
        }
        out
    }
}

/// Whether a re-judged walk's target still writes in main: a `python3 -c` read (how "read", 451 T31) is no write.
fn lands_in_main(t: &Target) -> bool {
    t.class == "main" && t.how != "read"
}

/// The verdict for one hook input; `resolved` says the caller already tried to find the clone (`judge`).
#[must_use]
pub fn judge(
    input: &Value,
    main: &str,
    clone: Option<&str>,
    home: &str,
    resolved: bool,
) -> Verdict {
    let ti = input.get("tool_input").cloned().unwrap_or(Value::Null);
    let cmd = ti.get("command").and_then(Value::as_str).unwrap_or("");
    let start = input
        .get("cwd")
        .and_then(Value::as_str)
        .filter(|c| !c.is_empty());
    let main = main.trim_end_matches('/');
    let w = walk_judged(cmd, start, main, home);
    let named = w
        .targets
        .iter()
        .any(|t| t.class == "main" && t.how == "named");
    let shell = w
        .targets
        .iter()
        .any(|t| t.class == "main" && t.how == "shell");
    let mut v = Verdict {
        verdict: "allow",
        reason: "no-write-in-main",
        cause: "",
        cwd: start.map(str::to_owned),
        walk: w.clone(),
        clone: clone.map(str::to_owned),
        prepended: None,
        command: None,
    };
    let mut out = |verdict, reason, cause| {
        (v.verdict, v.reason, v.cause) = (verdict, reason, cause);
        v.clone()
    };
    if named {
        return out("refuse", "named-main", "named");
    }
    if !shell {
        return out("allow", "no-write-in-main", "");
    }
    let cause = if w.cd_into_main { "cd" } else { "standing" };
    let Some(clone) = clone else {
        return out(
            if resolved { "refuse" } else { "needs-clone" },
            "clone-unresolved",
            cause,
        );
    };
    if !Path::new(clone).join(".git").exists() {
        return out("refuse", "clone-missing", cause);
    }
    if FUNCTION_DEF.is_match(cmd) {
        return out("refuse", "shape", cause);
    }
    let mut new = rewrite_cds(cmd, main, clone);
    let mut prepended = false;
    let mut w2 = walk_judged(&new, start, main, home);
    if w2.targets.iter().any(lands_in_main) && w.standing == "main" {
        let sub = start
            .filter(|c| *c != main)
            .map(|c| relpath(c, main))
            .unwrap_or_default();
        let at = if sub.is_empty() || sub == "." {
            clone.to_owned()
        } else {
            join(clone, &sub)
        };
        new = format!("cd {at} && {new}");
        prepended = true;
        w2 = walk_judged(&new, start, main, home);
    }
    if w2.targets.iter().any(lands_in_main) {
        return out("refuse", "shape", cause); // re-judged and still lands in main: never emit that
    }
    v.prepended = Some(prepended);
    v.command = Some(new);
    (v.verdict, v.reason, v.cause) = ("rewrite", "moved-to-clone", cause);
    v
}

/// What the session is told of a rewrite into its clone (`_context_line`).
#[must_use]
pub fn context_line(v: &Verdict, main: &str) -> String {
    let clone = v.clone.as_deref().unwrap_or("");
    let opening = if v.cause == "cd" {
        format!(
            "This command cd'd into {main} - the MIRROR, main's tree, never a workspace - and then wrote there. The cd was rewritten to \
your clone, {clone}, at the same relative position"
        )
    } else {
        format!(
            "Your shell was standing in {}, inside {main} - the MIRROR, main's tree, never a workspace - so this command's write would have \
landed in main. It was rewritten to run in your clone: `cd {clone}` was prepended",
            v.cwd.as_deref().unwrap_or("None")
        )
    };
    format!(
        "{opening}, and the shell stays in the clone for later commands. Read main with `git -C {main} <read>`; do everything else in the \
clone (CLAUDE.md, 'Session clones'). Rewritten rather than refused: a refusal costs a model round trip to say the same thing. \
(rust/guard/src/guards/main_tree_hooks.rs; feature 204)"
    )
}

/// The refusal text, naming the actual cause (`explain`).
#[must_use]
pub fn explain(v: &Verdict, main: &str) -> String {
    let clone = v.clone.as_deref().unwrap_or("<your clone under .clones/>");
    let where_ = match v.cause {
        "named" => "this command names a path inside the mirror and writes to it".to_owned(),
        "cd" => format!("this command cds into {main} - the MIRROR - and then writes there"),
        _ => format!(
            "your shell is standing in {}, inside {main} - the MIRROR - and this command writes where it stands",
            v.cwd.as_deref().unwrap_or("None")
        ),
    };
    let mut lines = vec![
        format!("BLOCKED: {where_}."),
        String::new(),
        "Main is the integration point, never a workspace. The only write a session makes there is".to_owned(),
        "render-sync, and that names the tree with `git -C` from sync-with-main.sh rather than cd-ing.".to_owned(),
        String::new(),
    ];
    match v.reason {
        "named-main" => {
            let named: Vec<String> = v
                .walk
                .targets
                .iter()
                .filter(|t| t.class == "main" && t.how == "named")
                .map(|t| {
                    t.path.clone().unwrap_or_else(|| {
                        format!("a target this cannot resolve, in `{}`", t.segment)
                    })
                })
                .collect();
            lines.push(format!("Named: {}", named.join(", ")));
            lines.push("A write that merely LANDS in main because of where the shell stands is moved to your clone".to_owned());
            lines.push("(feature 204); one that names main by its path says what it means, and a guard never guesses at".to_owned());
            lines.push(format!("that. Do it in your clone instead: {clone}."));
        }
        "clone-unresolved" => {
            lines.push("It would have been moved to your clone, but this session's clone cannot be resolved: no claim".to_owned());
            lines.push("under .clones/.session-clones, no /rename record in the transcript, no sessions entry. Ask the".to_owned());
            lines.push("GM to /rename the session, then work in .clones/<kebab-name>.".to_owned());
        }
        "clone-missing" => {
            lines.push(format!("It would have been moved to your clone, {clone}, which does not exist yet. Create it:"));
            lines.push(format!(
                "  git clone {main} {clone} && ( cd {clone} && scripts/sync-with-main.sh sync-in )"
            ));
        }
        _ => {
            lines.push("It would have been moved to your clone, but the command's shape could not be rewritten safely".to_owned());
            lines.push("(it opens with a function definition, or the cd into main is reached through a variable and".to_owned());
            lines.push(format!("cannot be located in the original text). Run it as `( cd {clone} && ... )` yourself."));
        }
    }
    lines.push(String::new());
    lines.push(format!("Reading main stays fine: `git -C {main} <read>`. If this genuinely needs to write in main, put"));
    lines.push(
        "MAIN_TREE_OK in the command with the reason, and the reason ships with it.".to_owned(),
    );
    lines.push(String::new());
    lines.push("(rust/guard/src/guards/main_tree_hooks.rs; features 169 and 204)".to_owned());
    lines.join("\n")
}
