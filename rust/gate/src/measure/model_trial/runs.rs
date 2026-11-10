//! The runs of a prepared case: each a headless session in the case's own clone, and what they cost.

use std::fmt::Write as _;
use std::fs::File;
use std::os::unix::process::CommandExt as _;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};

use serde_json::Value;

use super::{children, fold_usage, named, read, records_of, Trial};
use crate::cohort::int;
use crate::measure::{commas, text_err};

/// A run as a SUBAGENT (plan D34): `omitClaudeMd` is ignored for a session's main agent, so a cheap headless session dispatches the check once with
/// the recorded prompt.
const DISPATCH: &str = "Read the file {prompt}. Then use the Agent tool EXACTLY ONCE: subagent_type \"{agent}\", description \"seeded run\", and as its prompt the COMPLETE contents of that file, character for character - add nothing, remove nothing, summarize nothing. Do not run it in the background. When it returns, reply with the single word DONE. Do nothing else.";

#[cfg(not(test))]
const POLL: std::time::Duration = std::time::Duration::from_secs(5);
#[cfg(test)]
const POLL: std::time::Duration = std::time::Duration::from_millis(5);

fn parsed(path: &Path) -> Option<Value> {
    serde_json::from_str(&std::fs::read_to_string(path).ok()?).ok()
}

fn meta_of(out: &Path) -> Result<Value, String> {
    parsed(&out.join("meta.json"))
        .ok_or_else(|| format!("{}: no readable meta.json", out.display()))
}

fn clock() -> String {
    let secs = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0, |d| d.as_secs());
    let (.., h, m, s) = l7r_guard::shared::log::civil(secs);
    format!("{h:02}:{m:02}:{s:02}")
}

impl Trial {
    /// The headless session a run is: the check itself, or (`as_subagent`) a Sonnet session that dispatches it once.
    pub(crate) fn run_command(&self, out: &Path, meta: &Value) -> Vec<String> {
        let agent = meta["agent"].as_str().unwrap_or("");
        let off = [
            "--output-format",
            "json",
            "--permission-mode",
            "bypassPermissions",
            "--settings",
            "{\"disableAllHooks\": true}",
        ];
        let mut cmd = vec![self.claude.clone(), "-p".to_owned()];
        if meta["as_subagent"].as_bool().unwrap_or(false) {
            cmd.extend(["--model".to_owned(), "sonnet".to_owned()]);
            cmd.extend(off.map(str::to_owned));
            cmd.push(
                DISPATCH
                    .replace("{prompt}", &out.join("prompt.txt").display().to_string())
                    .replace("{agent}", agent),
            );
        } else {
            cmd.extend(["--agent".to_owned(), agent.to_owned()]);
            cmd.extend(off.map(str::to_owned));
            cmd.push(std::fs::read_to_string(out.join("prompt.txt")).unwrap_or_default());
        }
        cmd
    }

    fn start(&self, out: &Path, meta: &Value, log: &Path, alone: bool) -> Result<Child, String> {
        let cmd = self.run_command(out, meta);
        let file = File::create(log).map_err(text_err)?;
        let copy = file.try_clone().map_err(text_err)?;
        let mut command = Command::new(&cmd[0]);
        command
            .args(&cmd[1..])
            .current_dir(out.join("tree"))
            .stdin(Stdio::null())
            .stdout(file)
            .stderr(copy);
        if alone {
            command.process_group(0);
        }
        command.spawn().map_err(|e| format!("{}: {e}", cmd[0]))
    }

    /// Start each run in the background; each writes `run-<i>.json`.
    pub(crate) fn run_case(&self, out: &Path, runs: usize) -> Result<String, String> {
        let meta = meta_of(out)?;
        let mut shown = String::new();
        for i in 1..=runs {
            let log = out.join(format!("run-{i}.json"));
            let child = self.start(out, &meta, &log, true)?;
            let now = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .map_or(0, |d| d.as_secs());
            std::fs::write(
                out.join(format!("run-{i}.pid")),
                format!("{} {now}\n", child.id()),
            )
            .map_err(text_err)?;
            let _ = writeln!(
                shown,
                "started run {i}: pid {} -> {}",
                child.id(),
                log.display()
            );
        }
        Ok(shown)
    }

    /// Every prepared case under `root`, `runs` runs each, at most `parallel` sessions at once (each holds a few hundred MB); a run already finished
    /// (its `run-<i>.json` parses) is not started again. Prints as it goes: a queue runs for hours.
    pub(crate) fn run_all(
        &self,
        root: &Path,
        runs: usize,
        parallel: usize,
    ) -> Result<String, String> {
        let mut queue: Vec<(PathBuf, usize)> = Vec::new();
        for out in children(root)
            .into_iter()
            .filter(|d| d.join("meta.json").is_file())
        {
            queue.extend(
                (1..=runs)
                    .filter(|i| parsed(&out.join(format!("run-{i}.json"))).is_none())
                    .map(|i| (out.clone(), i)),
            );
        }
        let mut live: Vec<Child> = Vec::new();
        let total = queue.len();
        for (out, i) in queue {
            while live.len() >= parallel.max(1) {
                live.retain_mut(|c| matches!(c.try_wait(), Ok(None)));
                std::thread::sleep(POLL);
            }
            live.push(self.start(
                &out,
                &meta_of(&out)?,
                &out.join(format!("run-{i}.json")),
                false,
            )?);
            println!(
                "{} started {} run {i}",
                clock(),
                out.file_name().unwrap_or_default().to_string_lossy()
            );
        }
        for child in &mut live {
            let _ = child.wait();
        }
        Ok(format!("{} all {total} run(s) finished\n", clock()))
    }

    /// (the reply) of the one subagent an `as_subagent` run dispatched, from its own transcript.
    fn subagent_reply(&self, run_json: &Path) -> Option<String> {
        let parsed = parsed(run_json)?;
        let sid = parsed["session_id"].as_str().filter(|s| !s.is_empty())?;
        let sessions = children(&self.projects)
            .into_iter()
            .map(|p| p.join(sid).join("subagents"));
        let first = sessions
            .flat_map(|d| children(&d))
            .find(|p| named(p, "agent-", ".jsonl"))?;
        Some(read(&first).reply).filter(|r| !r.is_empty())
    }

    /// Each `as_subagent` run's reply, from the subagent's own transcript, to `reply-<i>.md` - what the scorer reads.
    pub(crate) fn collect(&self, out: &Path) -> (String, i32) {
        let mut n = 0;
        for run_json in children(out)
            .into_iter()
            .filter(|p| named(p, "run-", ".json"))
        {
            if let Some(reply) = self.subagent_reply(&run_json) {
                let name = run_json
                    .file_name()
                    .unwrap_or_default()
                    .to_string_lossy()
                    .replace("run-", "reply-")
                    .replace(".json", ".md");
                let _ = std::fs::write(out.join(name), reply);
                n += 1;
            }
        }
        (
            format!("collect: {n} repl(ies) in {}\n", out.display()),
            i32::from(n == 0),
        )
    }
}

/// Turns, tokens and seconds of the recorded run and of each new one; each finished run's result is saved beside it.
pub(crate) fn usage(out: &Path) -> Result<String, String> {
    let meta = meta_of(out)?;
    let u = fold_usage(&records_of(Path::new(
        meta["recorded"].as_str().unwrap_or(""),
    )));
    let mut shown = format!(
        "recorded  model={} turns={} in={} out={}\n",
        u["model"].as_str().unwrap_or(""),
        u["turns"],
        commas(int(&u["fresh"]) + int(&u["cached"])),
        commas(int(&u["output"]))
    );
    for file in children(out)
        .into_iter()
        .filter(|p| named(p, "run-", ".json"))
    {
        let stem = file
            .file_stem()
            .unwrap_or_default()
            .to_string_lossy()
            .into_owned();
        let Some(r) = parsed(&file) else {
            let _ = writeln!(shown, "{stem}  not finished");
            continue;
        };
        let uu = &r["usage"];
        let total = int(&uu["input_tokens"])
            + int(&uu["cache_read_input_tokens"])
            + int(&uu["cache_creation_input_tokens"]);
        let models: Vec<Value> = r["modelUsage"].as_object().map_or_else(Vec::new, |m| {
            m.keys().map(|k| Value::String(k.clone())).collect()
        });
        let _ = writeln!(
            shown,
            "{stem}  models={} turns={} in={} out={} {:.0} s cost=${:.2}",
            crate::checks::py_repr(&Value::Array(models)),
            crate::checks::py_repr(&r["num_turns"]),
            commas(total),
            commas(int(&uu["output_tokens"])),
            r["duration_ms"].as_f64().unwrap_or(0.0) / 1000.0,
            r["total_cost_usd"].as_f64().unwrap_or(0.0)
        );
        let _ = std::fs::write(
            out.join(format!("{stem}-reply.md")),
            r["result"].as_str().unwrap_or(""),
        );
    }
    Ok(shown)
}
