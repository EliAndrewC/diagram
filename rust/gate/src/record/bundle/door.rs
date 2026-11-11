//! The bundles' runner of the Python they still reach (`ask:449-T88-bundles`): `python3 scripts/bundle_door.py`, started on a bundle run's first verb and never before, one process a run, one JSON line each way a verb. It holds no logic; a failure it reports is the traceback the Python raised.

use std::io::{BufRead, BufReader, Write};
use std::path::{Path, PathBuf};
use std::process::{Child, ChildStdin, ChildStdout, Command, Stdio};

use serde_json::{json, Value};

use crate::record::repo::{fail, Fail};

/// The runner of one bundle run: not started until a verb is asked.
pub(crate) struct Runner {
    script: PathBuf,
    live: Option<(Child, ChildStdin, BufReader<ChildStdout>)>,
}

impl Runner {
    /// The runner of the scripts under `tree`.
    pub(crate) fn new(tree: &Path) -> Self {
        Self {
            script: tree.join("scripts").join("bundle_door.py"),
            live: None,
        }
    }

    fn start(&mut self) -> Result<&mut (Child, ChildStdin, BufReader<ChildStdout>), Fail> {
        if self.live.is_none() {
            let mut cmd = Command::new("python3");
            cmd.arg(&self.script)
                .stdin(Stdio::piped())
                .stdout(Stdio::piped());
            let mut child = cmd.stderr(Stdio::inherit()).spawn().map_err(fail)?;
            let (stdin, stdout) = (child.stdin.take(), child.stdout.take());
            let pipes = stdin.zip(stdout).map(|(i, o)| (i, BufReader::new(o)));
            self.live = pipes.map(|(i, o)| (child, i, o));
        }
        self.live
            .as_mut()
            .ok_or(String::from("bundle-door: no pipe"))
    }

    /// The verb's value, or the traceback the Python raised.
    pub(crate) fn ask(&mut self, verb: &str, args: &Value) -> Result<Value, Fail> {
        let (_, stdin, stdout) = self.start()?;
        let line = json!({"verb": verb, "args": args}).to_string() + "\n";
        let mut said = String::new();
        if stdin
            .write_all(line.as_bytes())
            .and_then(|()| stdin.flush())
            .is_err()
            || stdout.read_line(&mut said).unwrap_or(0) == 0
        {
            return Err(format!("bundle-door: no answer to {verb}"));
        }
        let said: Value =
            serde_json::from_str(&said).map_err(|e| format!("bundle-door: {verb}: {e}"))?;
        if let Some(why) = said.get("error") {
            return Err(why.as_str().unwrap_or_default().to_owned());
        }
        Ok(said.get("ok").cloned().unwrap_or(Value::Null))
    }

    /// `main(args)` of one of the helpers `check_bundle` ran in its own process (feature 383 D6): (its exit, stdout then stderr).
    pub(crate) fn helper(
        &mut self,
        name: &str,
        args: &[String],
        root: &Path,
    ) -> Result<(i32, String), Fail> {
        let got = self.ask("run", &json!([name, args, root.to_string_lossy()]))?;
        let code = got.get(0).and_then(Value::as_i64).unwrap_or(1);
        Ok((
            i32::try_from(code).unwrap_or(1),
            got.get(1)
                .and_then(Value::as_str)
                .unwrap_or_default()
                .to_owned(),
        ))
    }
}

impl Drop for Runner {
    fn drop(&mut self) {
        if let Some((mut child, stdin, _)) = self.live.take() {
            drop(stdin);
            let _ = child.wait();
        }
    }
}

#[cfg(test)]
mod tests;
