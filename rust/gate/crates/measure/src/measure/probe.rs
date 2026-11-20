//! `make probe`: what a change does to every seed and every pool map, against HEAD, in one command (feature 426, D5; feature 449 T75, from
//! `probe.py`). It replaces the hand-written probe scripts of feature 417, one of which compared the SETS of failing seeds and missed a seed
//! whose failure changed. HEAD's verdicts are stored per engine key and block, so two probes at one HEAD roll HEAD's block once.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::sha256;
use serde_json::{json, Value};

use super::reply;

const SEEDS: usize = 48;

/// THE POOL IS NOT COMPARED (feature 449 T222): the probe once regenerated each hamlet's `.gen.py` and listed the fields of its committed
/// `<name>.json` that moved against HEAD's. Both went with the Python engine (444 T39, 449 T221): the Rust driver draws a hamlet into its
/// gitignored `.driver.json`, so no committed manifest holds HEAD's drawing, and the section filtered on a file no map has - it printed
/// nothing for every hamlet, which read as a pool unchanged. Said, never silent, until a comparison draws HEAD too.
const POOL_NOT_COMPARED: &str = "\nthe pool against HEAD: NOT COMPARED by the probe since feature 449 T222 - a hamlet's drawing is its gitignored .driver.json, so no committed manifest holds HEAD's; nothing here says which maps the change moved. `make map MAP=--all` draws the pool, but its REGENERATED says only what moved since that tree last drew a map, not against HEAD\n";
type Verdicts = BTreeMap<i64, Vec<String>>;

static RECORD: LazyLock<Regex> = LazyLock::new(|| {
    l7r_guard::shared::regex::build(r"record committed \([^)]*\): (\S+\.json)")
        .unwrap_or_else(|e| unreachable!("{e}"))
});

/// How a probe reaches a command, so a test can answer for make.
pub trait Runs {
    fn run(&self, cmd: &[String], dir: &Path) -> (i32, String);
}

struct Live;

impl Runs for Live {
    fn run(&self, cmd: &[String], dir: &Path) -> (i32, String) {
        let done = Command::new(&cmd[0])
            .args(&cmd[1..])
            .current_dir(dir)
            .output();
        done.map_or((127, String::new()), |o| {
            (
                o.status.code().unwrap_or(1),
                format!(
                    "{}{}",
                    String::from_utf8_lossy(&o.stdout),
                    String::from_utf8_lossy(&o.stderr)
                ),
            )
        })
    }
}

fn words(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

fn git(h: &dyn Runs, root: &Path, args: &[&str]) -> String {
    let mut cmd = words(&["git", "-C", &root.display().to_string()]);
    cmd.extend(words(args));
    h.run(&cmd, root).1.trim().to_owned()
}

/// The cohort record a `make cohort` run names, read from the clone it lands in.
fn record_of(h: &dyn Runs, out: &str, root: &Path) -> Result<Value, String> {
    let last = RECORD
        .captures_iter(out)
        .map_while(Result::ok)
        .last()
        .map(|c| c[1].to_owned());
    let Some(name) = last else {
        let tail: String = out
            .chars()
            .rev()
            .take(1500)
            .collect::<Vec<_>>()
            .into_iter()
            .rev()
            .collect();
        return Err(format!(
            "probe: the cohort wrote no record - its output ended:\n{tail}"
        ));
    };
    let common = PathBuf::from(git(
        h,
        root,
        &["rev-parse", "--path-format=absolute", "--git-common-dir"],
    ));
    let path = if Path::new(&name).is_absolute() {
        PathBuf::from(&name)
    } else {
        common.parent().unwrap_or(root).join(&name)
    };
    serde_json::from_str(&std::fs::read_to_string(&path).unwrap_or_default())
        .map_err(|e| format!("probe: {}: {e}", path.display()))
}

fn verdicts(rec: &Value) -> Verdicts {
    let mut out = Verdicts::new();
    for s in rec["seeds"].as_array().map_or(&[][..], Vec::as_slice) {
        let mut failures: Vec<String> = s["failures"].as_array().map_or_else(Vec::new, |a| {
            a.iter()
                .filter_map(|f| f.as_str().map(str::to_owned))
                .collect()
        });
        failures.sort();
        out.insert(s["seed"].as_i64().unwrap_or(0), failures);
    }
    out
}

fn stems(list: &[String]) -> BTreeSet<&str> {
    list.iter()
        .map(|f| f.split('[').next().unwrap_or_default())
        .collect()
}

/// How a seed's verdict moved against HEAD's: a check new to it is worse whatever else it fails.
fn mark(head: Option<&Vec<String>>, now: Option<&Vec<String>>) -> &'static str {
    let Some(now) = now else {
        return "not rolled";
    };
    let Some(head) = head else {
        return "new seed";
    };
    if head.is_empty() && now.is_empty() {
        "same pass"
    } else if now.is_empty() {
        "FIXED"
    } else if !stems(now).is_subset(&stems(head)) {
        "NEW FAILURE"
    } else if now == head {
        "same failure"
    } else {
        "changed failure"
    }
}

fn show(v: Option<&Vec<String>>) -> String {
    v.map_or_else(
        || "-".to_owned(),
        |f| {
            if f.is_empty() {
                "pass".to_owned()
            } else {
                f.join(", ")
            }
        },
    )
}

/// Every seed's line, HEAD's verdict beside the probe's, and how many are worse.
fn compare(head: &Verdicts, now: &Verdicts) -> (Vec<String>, usize) {
    let seeds: BTreeSet<&i64> = head.keys().chain(now.keys()).collect();
    let mut worse = 0;
    let lines = seeds
        .into_iter()
        .map(|seed| {
            let m = mark(head.get(seed), now.get(seed));
            worse += usize::from(m == "NEW FAILURE");
            format!(
                "  {seed:>7}  {m:<16} HEAD: {}  now: {}",
                show(head.get(seed)),
                show(now.get(seed))
            )
        })
        .collect();
    (lines, worse)
}

fn cohort_cmd(jobs: &str, seed: Option<i64>) -> Vec<String> {
    let mut cmd = words(&[
        "make",
        "--no-print-directory",
        "cohort",
        &format!("N={SEEDS}"),
        "FRESH=0",
        &format!("JOBS={jobs}"),
    ]);
    cmd.extend(seed.map(|s| format!("SEED={s}")));
    cmd
}

fn keyed(data: &Value) -> Verdicts {
    data.as_object().map_or_else(Verdicts::new, |o| {
        o.iter()
            .map(|(k, v)| {
                (
                    k.parse().unwrap_or(0),
                    v.as_array().map_or_else(Vec::new, |a| {
                        a.iter()
                            .filter_map(|f| f.as_str().map(str::to_owned))
                            .collect()
                    }),
                )
            })
            .collect()
    })
}

fn string_keyed(v: &Verdicts) -> Value {
    Value::Object(v.iter().map(|(k, f)| (k.to_string(), json!(f))).collect())
}

/// What a probe is run over.
struct Probe<'a> {
    h: &'a dyn Runs,
    root: &'a Path,
    gate: PathBuf,
    jobs: String,
    exitfirst: bool,
    tmp: PathBuf,
}

impl Probe<'_> {
    fn cohort(&self, args: &[&str]) -> String {
        let mut cmd = vec![self.gate.display().to_string(), "cohort".to_owned()];
        cmd.extend(words(args));
        self.h.run(&cmd, self.root).1.trim().to_owned()
    }

    fn roll(
        &self,
        wt: &Path,
        seed: Option<i64>,
        against: Option<&Verdicts>,
    ) -> Result<Verdicts, String> {
        let mut cmd = cohort_cmd(&self.jobs, seed);
        if let Some(head) = against {
            let file = self.tmp.join(format!("against-{}.json", seed.unwrap_or(0)));
            let _ = std::fs::write(&file, string_keyed(head).to_string());
            cmd.extend([
                "EXITFIRST=1".to_owned(),
                format!("EXITFIRST_AGAINST={}", file.display()),
            ]);
        }
        let out = self.h.run(&cmd, wt).1;
        Ok(verdicts(&record_of(self.h, &out, self.root)?))
    }

    /// HEAD's (landing, fresh) verdicts: stored per engine key and block, or rolled once in a detached worktree at HEAD.
    fn baseline(&self, block: i64) -> Result<(Verdicts, Verdicts), String> {
        let digest = sha256::hex(self.cohort(&["engine-key", "HEAD"]).as_bytes());
        let common = PathBuf::from(git(
            self.h,
            self.root,
            &["rev-parse", "--path-format=absolute", "--git-common-dir"],
        ));
        let store = common
            .join("probe-baselines")
            .join(format!("{}-{block}.json", &digest[..16]));
        if let Ok(text) = std::fs::read_to_string(&store) {
            let data: Value = serde_json::from_str(&text).unwrap_or_default();
            return Ok((keyed(&data["landing"]), keyed(&data["fresh"])));
        }
        println!("probe: HEAD's verdicts for block {block} are not stored - rolling HEAD once in a detached worktree");
        let wt = self.tmp.join("head");
        git(
            self.h,
            self.root,
            &[
                "worktree",
                "add",
                "-q",
                "--detach",
                &wt.display().to_string(),
                "HEAD",
            ],
        );
        let both = self
            .roll(&wt, None, None)
            .and_then(|l| Ok((l, self.roll(&wt, Some(block), None)?)));
        git(
            self.h,
            self.root,
            &["worktree", "remove", "--force", &wt.display().to_string()],
        );
        let (landing, fresh) = both?;
        let _ = std::fs::create_dir_all(store.parent().unwrap_or(self.root));
        let _ = std::fs::write(
            &store,
            json!({"landing": string_keyed(&landing), "fresh": string_keyed(&fresh)}).to_string(),
        );
        Ok((landing, fresh))
    }

    fn run(&self, wt: &Path) -> Result<(String, i32), String> {
        let block: i64 = self.cohort(&["fresh-seed", "HEAD"]).parse().unwrap_or(0);
        let (head_landing, head_fresh) = self.baseline(block)?;
        let landing = self.roll(wt, None, self.exitfirst.then_some(&head_landing))?;
        let fresh = self.roll(wt, Some(block), self.exitfirst.then_some(&head_fresh))?;
        let mut out = String::new();
        let mut worse = 0;
        for (title, head, now) in [
            ("the landing cohort".to_owned(), &head_landing, &landing),
            (
                format!("HEAD's fresh block from {block}"),
                &head_fresh,
                &fresh,
            ),
        ] {
            let (lines, n) = compare(head, now);
            worse += n;
            let _ = write!(
                out,
                "\n{title} ({n} worse than HEAD):\n{}\n",
                lines.join("\n")
            );
        }
        out.push_str(POOL_NOT_COMPARED);
        let _ = writeln!(
            out,
            "\nprobe: {worse} seed(s) worse than HEAD{}",
            if self.exitfirst && worse > 0 {
                " - EXITFIRST stopped at the first"
            } else {
                ""
            }
        );
        Ok((out, i32::from(worse > 0)))
    }
}

fn flag<'a>(args: &'a [String], name: &str) -> Option<&'a str> {
    args.windows(2)
        .find(|w| w[0] == name)
        .map(|w| w[1].as_str())
}

fn drive(args: &[String], root: &Path, h: &dyn Runs) -> crate::Reply {
    let wt = flag(args, "--wt").map_or_else(
        || root.to_path_buf(),
        |w| std::fs::canonicalize(w).unwrap_or_else(|_| PathBuf::from(w)),
    );
    let tmp = l7r_guard::shared::tempdir::TempDir::new("probe");
    let probe = Probe {
        h,
        root,
        gate: crate::codeid::script(root).with_file_name("l7r-gate.sh"),
        jobs: flag(args, "--jobs").unwrap_or("3").to_owned(),
        exitfirst: args.iter().any(|a| a == "--exitfirst"),
        tmp: tmp.to_path_buf(),
    };
    let got = probe.run(&wt);
    let _ = std::fs::remove_dir_all(&tmp);
    match got {
        Ok((out, code)) => reply(out, String::new(), code),
        Err(why) => reply(String::new(), why + "\n", 1),
    }
}

/// `l7r-gate measure probe [--wt <worktree>] [--exitfirst] [--jobs <n>]`.
#[must_use]
pub fn cli(args: &[String], root: &Path) -> crate::Reply {
    drive(args, root, &Live)
}

#[cfg(test)]
mod tests;
