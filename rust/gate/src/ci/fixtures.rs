//! What the remote path's tests share: a repository with an `origin/main`, a stand-in for Python, and the two boundaries faked, the `git` underneath real.

use std::cell::RefCell;
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::atomic::{AtomicUsize, Ordering};

use serde_json::{json, Value};

use super::aws::{Aws, AwsError};
use super::config::Secrets;
use super::dispatch::Host;

pub(crate) fn git(dir: &Path, args: &[&str]) -> String {
    let done = Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(args)
        .output()
        .unwrap();
    assert!(done.status.success(),);
    String::from_utf8_lossy(&done.stdout).trim().to_owned()
}

pub(crate) fn put(dir: &Path, rel: &str, text: &str) {
    let path = dir.join(rel);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

pub(crate) fn commit(dir: &Path, rel: &str, text: &str) {
    put(dir, rel, text);
    git(dir, &["add", "-A"]);
    git(dir, &["commit", "-qm", "c"]);
}

pub(crate) fn scratch(tag: &str) -> PathBuf {
    static SEQ: AtomicUsize = AtomicUsize::new(0);
    let dir = std::env::temp_dir().join(format!(
        "l7r-gate-ci-{tag}-{}-{}",
        std::process::id(),
        SEQ.fetch_add(1, Ordering::Relaxed)
    ));
    let _ = std::fs::remove_dir_all(&dir);
    std::fs::create_dir_all(&dir).unwrap();
    dir
}

/// A repository, with `origin/main` at its first commit, each buildspec and an operation registry.
pub(crate) fn repo(tag: &str) -> PathBuf {
    let dir = scratch(tag);
    git(&dir, &["init", "-q", "-b", "main"]);
    git(&dir, &["config", "user.email", "t@t"]);
    git(&dir, &["config", "user.name", "t"]);
    for spec in ["check", "merge", "measure", "image"] {
        put(
            &dir,
            &format!("buildspec/{spec}.yml"),
            &format!("# {spec}\n"),
        );
    }
    put(&dir, "l7r/diagram/_invocation.py", "    \"l7r.diagram.tools.cohort\": (\"cohort\", \"expensive\"),\n    \"l7r.diagram.tools.pack_audit\": (\"pack-audit\", \"cheap\"),\n");
    commit(&dir, "l7r/diagram/m.py", "x = 1\n");
    git(&dir, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    dir
}

/// A stand-in for `python3`: the `.py` ids by a hash of the bytes, `--holding` from `<feature>/.holding`, and a verdict by `<feature>/.faithful`.
pub(crate) fn python(dir: &Path) -> String {
    let path = dir.join(".git/stand-in-python");
    std::fs::write(&path, "#!/bin/bash\ncase \"$1\" in\n *codeid.py) if [ \"$2\" = --semantic ]; then shift 3; for f in \"$@\"; do printf '1\\nz'; done; else shift 2; for f in \"$@\"; do sha1sum \"$f\" | cut -d' ' -f1; done; fi;;\n *speckit-todo.py) cat \"$3/.holding\" 2>/dev/null; true;;\n *hm_arbiter.py) [ -f \"$3/.faithful\" ];;\nesac\n").unwrap();
    Command::new("chmod").arg("+x").arg(&path).status().unwrap();
    path.to_string_lossy().into_owned()
}

pub(crate) fn secrets() -> Secrets {
    Secrets {
        region: "us-east-1".to_owned(),
        access_key_id: "AK".to_owned(),
        secret_access_key: "SK".to_owned(),
        ci_bucket: "bucket".to_owned(),
        ecr_image: "123.dkr.ecr/x".to_owned(),
        log_group: "/aws/codebuild/gm-assistant".to_owned(),
        github_pat: "PAT".to_owned(),
    }
}

/// `git` runs for real; a make target answers from a script; a push and a fetch do nothing.
#[derive(Default)]
pub(crate) struct FakeHost {
    pub make: BTreeMap<String, (i32, String)>,
    pub push_rc: i32,
    pub ran: RefCell<Vec<String>>,
    pub lines: RefCell<Vec<String>>,
    pub errs: RefCell<Vec<String>>,
}

impl FakeHost {
    pub(crate) fn said(&self) -> String {
        self.lines.borrow().join("\n")
    }

    pub(crate) fn told(&self) -> String {
        self.errs.borrow().join("\n")
    }
}

impl Host for FakeHost {
    fn sh(&self, args: &[&str], cwd: &Path, env: &[(&str, &str)]) -> (i32, String) {
        self.ran.borrow_mut().push(args.join(" "));
        match args[..2] {
            ["make", _] => {
                let key = args[1..]
                    .iter()
                    .filter(|a| !a.starts_with("--"))
                    .copied()
                    .collect::<Vec<_>>()
                    .join(" ");
                self.make.get(&key).cloned().unwrap_or((0, String::new()))
            }
            ["git", "push"] => {
                assert!(
                    env.iter()
                        .any(|(k, v)| *k == "GIT_ASKPASS" && v.ends_with("git-askpass-token.sh"))
                        && env.iter().any(|(k, _)| *k == "GITHUB_TOKEN")
                );
                (
                    self.push_rc,
                    if self.push_rc == 0 {
                        String::new()
                    } else {
                        "fatal: could not push".to_owned()
                    },
                )
            }
            ["git", "fetch"] => (0, String::new()),
            _ => {
                let o = Command::new(args[0])
                    .args(&args[1..])
                    .current_dir(cwd)
                    .output()
                    .unwrap();
                (
                    o.status.code().unwrap_or(1),
                    format!(
                        "{}{}",
                        String::from_utf8_lossy(&o.stdout),
                        String::from_utf8_lossy(&o.stderr)
                    ),
                )
            }
        }
    }

    fn sleep(&self, _secs: u64) {}

    fn out(&self, line: &str) {
        self.lines.borrow_mut().push(line.to_owned());
    }

    fn err(&self, line: &str) {
        self.errs.borrow_mut().push(line.to_owned());
    }
}

/// Replays `CodeBuild`'s shapes and logs every call.
pub(crate) struct FakeAws {
    pub calls: RefCell<Vec<String>>,
    pub deny_start: RefCell<Option<String>>,
    pub fail_start: bool,
    pub statuses: RefCell<Vec<String>>,
    pub objects: RefCell<BTreeMap<String, Vec<u8>>>,
    pub pages: RefCell<Vec<Value>>,
    pub logs: Value,
    pub started: RefCell<Option<Value>>,
    pub vanish: Option<String>,
}

impl Default for FakeAws {
    fn default() -> Self {
        Self {
            calls: RefCell::default(),
            deny_start: RefCell::default(),
            fail_start: false,
            statuses: RefCell::new(vec!["IN_PROGRESS".to_owned(), "SUCCEEDED".to_owned()]),
            objects: RefCell::default(),
            pages: RefCell::default(),
            logs: json!({"streamName": "the-stream", "groupName": "the-group"}),
            started: RefCell::default(),
            vanish: None,
        }
    }
}

impl FakeAws {
    pub(crate) fn called(&self, name: &str) -> usize {
        self.calls
            .borrow()
            .iter()
            .filter(|c| c.starts_with(name))
            .count()
    }

    pub(crate) fn request(&self) -> Value {
        self.started.borrow().clone().unwrap()
    }
}

impl Aws for FakeAws {
    fn start_build(&self, request: &Value) -> Result<Value, AwsError> {
        self.calls.borrow_mut().push("start_build".to_owned());
        *self.started.borrow_mut() = Some(request.clone());
        if let Some(operation) = self.deny_start.borrow().clone() {
            return Err(AwsError::Denied {
                operation,
                message: "denied".to_owned(),
            });
        }
        if self.fail_start {
            return Err(AwsError::Other("throttled".to_owned()));
        }
        Ok(json!({"build": {"id": "gm-assistant-check:abc-123"}}))
    }

    fn batch_get_builds(&self, id: &str) -> Result<Value, AwsError> {
        self.calls
            .borrow_mut()
            .push(format!("batch_get_builds {id}"));
        let mut statuses = self.statuses.borrow_mut();
        let status = if statuses.len() > 1 {
            statuses.remove(0)
        } else {
            statuses[0].clone()
        };
        Ok(
            json!({"builds": [{"id": id, "buildStatus": status, "currentPhase": status, "logs": self.logs, "phases": [{"phaseType": "SUBMITTED", "durationInSeconds": 500}, {"phaseType": "PROVISIONING", "durationInSeconds": 30}, {"phaseType": "BUILD", "durationInSeconds": 40}]}]}),
        )
    }

    fn stop_build(&self, id: &str) -> Result<(), AwsError> {
        self.calls.borrow_mut().push(format!("stop_build {id}"));
        Ok(())
    }

    fn get_log_events(
        &self,
        group: &str,
        stream: &str,
        _token: Option<&str>,
    ) -> Result<Value, AwsError> {
        self.calls
            .borrow_mut()
            .push(format!("get_log_events {group} {stream}"));
        let mut pages = self.pages.borrow_mut();
        Ok(if pages.is_empty() {
            json!({"events": [], "nextForwardToken": "t"})
        } else {
            pages.remove(0)
        })
    }

    fn put_object(&self, _bucket: &str, key: &str, body: &[u8]) -> Result<(), AwsError> {
        self.calls.borrow_mut().push(format!("put_object {key}"));
        self.objects
            .borrow_mut()
            .insert(key.to_owned(), body.to_vec());
        Ok(())
    }

    fn get_object(&self, _bucket: &str, key: &str) -> Result<Option<Vec<u8>>, AwsError> {
        self.calls.borrow_mut().push(format!("get_object {key}"));
        Ok(if self.vanish.as_deref() == Some(key) {
            None
        } else {
            self.objects.borrow().get(key).cloned()
        })
    }

    fn list_prefix(&self, _bucket: &str, prefix: &str) -> Result<Vec<String>, AwsError> {
        Ok(self
            .objects
            .borrow()
            .keys()
            .filter(|k| k.starts_with(prefix))
            .cloned()
            .collect())
    }

    fn delete_object(&self, _bucket: &str, key: &str) -> Result<(), AwsError> {
        self.calls.borrow_mut().push(format!("delete_object {key}"));
        self.objects.borrow_mut().remove(key);
        Ok(())
    }
}
