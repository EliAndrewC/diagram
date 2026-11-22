//! `/tmp`'s share and the task outputs' on a fixture: a stand-in `/tmp`, a root of session scratch, a clone with a scratch worktree,
//! every entry's age set by hand.

use std::fs::File;
use std::os::unix::fs::MetadataExt;
use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime};

use super::{idle_scratch, landed, outputs, scratch_name};
use crate::guards::scratch_sweep_hooks::Config;
use crate::shared::tempdir::TempDir;

const HOUR: u64 = 3600;

fn put(path: &Path, h: u64) {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, "x").unwrap();
    let when = SystemTime::now() - Duration::from_secs(h * HOUR);
    File::open(path).unwrap().set_modified(when).unwrap();
}

fn world() -> (TempDir, Config) {
    let base = TempDir::new("guard-sweep-tmp");
    let mut c = Config::from_env(&|_| None, 4242);
    c.tmp = base.join("tmp");
    c.clones = base.join("clones");
    c.mirror = base.join("diagram");
    std::fs::create_dir_all(&c.tmp).unwrap();
    c.uid = std::fs::metadata(&c.tmp).unwrap().uid();
    (base, c)
}

fn names(found: &[(PathBuf, &str)], top: &Path) -> Vec<String> {
    let mut v: Vec<String> = found
        .iter()
        .map(|(p, _)| p.strip_prefix(top).unwrap().display().to_string())
        .collect();
    v.sort();
    v
}

fn ago(h: u64) -> SystemTime {
    SystemTime::now() - Duration::from_secs(h * HOUR)
}

#[test]
fn a_builder_s_scratch_and_a_mktemp_go_once_idle_a_day_but_one_holding_a_worktree_or_another_name_stays(
) {
    let (_base, c) = world();
    let t = &c.tmp;
    put(&t.join("t42/run.log"), 30);
    put(&t.join("t02-base.log"), 30);
    put(&t.join("tmp.Ab12/x"), 30);
    put(&t.join("t43/fresh"), 1);
    put(&t.join("l7r-guard-x/old"), 30);
    put(&t.join("tea/old"), 30);
    // a registered worktree of the clone inside a scratch dir: kept, its owner's to remove
    put(&t.join("t33/wt/f"), 30);
    let admin = c.clones.join("clone/.git/worktrees/wt");
    std::fs::create_dir_all(&admin).unwrap();
    std::fs::write(
        admin.join("gitdir"),
        format!("{}/.git", t.join("t33/wt").display()),
    )
    .unwrap();
    // parents touched by the writes: set back
    for d in ["t42", "tmp.Ab12", "t33", "t33/wt"] {
        File::open(t.join(d))
            .unwrap()
            .set_modified(ago(30))
            .unwrap();
    }
    assert_eq!(
        names(&idle_scratch(&c, ago(24)), t),
        ["t02-base.log", "t42", "tmp.Ab12"]
    );
    // another uid's entries are never judged
    let (_other_base, mut other) = world();
    other.uid = c.uid + 1;
    other.tmp = c.tmp.clone();
    assert!(idle_scratch(&other, ago(24)).is_empty());
}

#[test]
fn a_task_output_goes_once_idle_and_a_name_reads_as_its_task_number() {
    let (base, _c) = world();
    let root = base.join("root");
    put(&root.join("-proj/s1/tasks/a.output"), 30);
    put(&root.join("-proj/s1/tasks/b.output"), 1);
    put(&root.join("-proj/s1/tasks/c.txt"), 30);
    put(&root.join("-proj/s1/scratchpad/old.output"), 30);
    put(&root.join("loose.output"), 30);
    assert_eq!(
        names(&outputs(&root, ago(24)), &root),
        ["-proj/s1/tasks/a.output"]
    );
    assert_eq!(scratch_name("t216r"), Some(Some(216)));
    assert_eq!(scratch_name("t02-base.log"), Some(Some(2)));
    assert_eq!(scratch_name("tmp.x"), Some(None));
    assert_eq!(scratch_name("tea"), None);
    assert_eq!(scratch_name("other"), None);
}

#[test]
fn a_landed_task_s_own_scratch_goes_unless_another_feature_started_that_number_within_the_day() {
    let (base, c) = world();
    let t = &c.tmp;
    for n in [
        "t158/m.py",
        "t158r/x",
        "t1580/x",
        "t160/x",
        "t161/x",
        "tmp.Q/x",
    ] {
        put(&t.join(n), 0);
    }
    let starts = base.join("task-starts.jsonl");
    let now = SystemTime::now();
    // a start within the day (a stamp ahead of now passes) and one long past; the landing's own feature's start never counts
    let lines = [
        r#"{"feature": "451-time", "task": "T158", "utc": "2999-01-01T00:00:00Z"}"#,
        r#"{"feature": "449-rust", "task": "T160", "utc": "2999-01-01T00:00:00Z"}"#,
        r#"{"feature": "449-rust", "task": "T161", "utc": "2000-01-01T00:00:00Z"}"#,
        "not json",
    ];
    std::fs::write(&starts, lines.join("\n")).unwrap();
    let (gone, shared) = landed(&c, "451", &[158, 160, 161], &starts, now);
    assert_eq!(names(&gone, t), ["t158", "t158r", "t161"]);
    assert_eq!(shared, [160]);
    // no record at all: every landed number's own goes
    let (gone, shared) = landed(&c, "451", &[160], &base.join("none"), now);
    assert!(names(&gone, t) == ["t160"] && shared.is_empty());
}
