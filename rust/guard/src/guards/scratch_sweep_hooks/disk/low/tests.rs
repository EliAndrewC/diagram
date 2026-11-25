//! The low-disk trigger on a fixture: the disk's size and free bytes set (`Config::space`), a cargo root with an idle clone's profile,
//! a stand-in `/proc`, and a stand-in sweeper that writes its arguments.

use std::fs::File;
use std::path::Path;
use std::time::{Duration, SystemTime};

use serde_json::json;

use super::{evict, note, trigger, EVERY};
use crate::guards::scratch_sweep_hooks::{judge, Config};
use crate::protocol::{Answer, Event};
use crate::shared::tempdir::TempDir;

fn put(top: &Path, path: &Path, h: u64) {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, vec![b'x'; 8192]).unwrap();
    let when = SystemTime::now() - Duration::from_secs(h * 3600);
    let mut at = Some(path);
    while let Some(p) = at {
        File::open(p).unwrap().set_modified(when).unwrap();
        if p == top {
            break;
        }
        at = p.parent();
    }
}

fn world() -> (TempDir, Config) {
    crate::shared::log::quiet();
    let base = TempDir::new("guard-low-disk");
    let mut c = Config::from_env(&|_| None, 4242);
    c.cargo = base.join("cargo");
    c.clones = base.join("clones");
    c.mirror = base.join("diagram");
    c.state = base.join("state");
    c.proc = base.join("proc");
    // the age shares' places (451 T246), never the machine's own
    c.root = base.join("root");
    c.projects = base.join("projects");
    c.sessions = base.join("sessions");
    c.tmp = base.join("tmp");
    std::fs::create_dir_all(&c.root).unwrap();
    std::fs::create_dir_all(c.proc.join("1")).unwrap();
    std::fs::write(c.proc.join("1/comm"), "bash\n").unwrap();
    std::fs::create_dir_all(c.clones.join("idle")).unwrap();
    put(&c.cargo, &c.cargo.join("idle/cover-gate/x"), 30);
    put(&c.cargo, &c.cargo.join("diagram/debug/x"), 30);
    // 25% free: above the 20% share
    c.space = Some((1000, 250));
    (base, c)
}

#[test]
fn below_the_share_free_a_prompt_starts_one_eviction_an_hour_and_says_once_what_it_freed() {
    let (base, mut c) = world();
    let marker = base.join("spawned");
    let exe = base.join("sweeper");
    crate::guards::write_executable(
        &exe,
        &format!("#!/bin/sh\necho \"$@\" > {}\n", marker.display()),
    );
    c.exe = exe;
    let now = SystemTime::now();
    assert!(!trigger(&c, "sid", now), "above the share: nothing");
    c.space = Some((1000, 150));
    assert!(trigger(&c, "sid", now), "below it: started");
    assert!((0..2500).any(|_| {
        std::thread::sleep(Duration::from_millis(2));
        std::fs::read_to_string(&marker).is_ok_and(|t| t.contains("evict --keep sid"))
    }));
    let soon = trigger(&c, "sid", now + EVERY / 2);
    assert!(!soon, "within the hour: not again");
    assert!(trigger(&c, "sid", now + EVERY * 2), "an hour on: again");
    // the eviction: what it may take goes (the idle clone's profile, never the mirror's), and its line is said once at a prompt
    let dry = evict(&c, now, true);
    assert!(dry.stdout.contains("would remove") && c.cargo.join("idle/cover-gate").exists());
    assert!(note(&c).is_none(), "a dry run says nothing at a prompt");
    let ran = evict(&c, now, false);
    assert_eq!(ran.code, 0, "{}", ran.stdout);
    assert!(!c.cargo.join("idle/cover-gate").exists() && c.cargo.join("diagram/debug").exists());
    let e = Event {
        name: "UserPromptSubmit".to_owned(),
        input: json!({"session_id": "sid"}),
    };
    c.space = Some((1000, 900));
    let said = judge(&e, &c, now);
    let shown = format!("{said:?}");
    assert!(said.len() == 1 && matches!(said[0], Answer::Notice(_)));
    assert!(shown.contains("the eviction removed") && shown.contains("L7R_DISK_FREE_PCT"));
    assert!(judge(&e, &c, now).is_empty(), "said once");
    // nothing left it may take: said so
    c.space = Some((1000, 10));
    let none = evict(&c, now, false);
    assert!(none.stdout.contains("found nothing it may take"));
    assert!(note(&c).is_some_and(|t| t.contains("make disk-audit")));
    // ...once: the next eviction that finds nothing says nothing, until one frees something again
    let _ = evict(&c, now, false);
    assert!(note(&c).is_none(), "nothing new to say");
    put(&c.cargo, &c.cargo.join("idle/debug/x"), 30);
    let _ = evict(&c, now, false);
    assert!(note(&c).is_some_and(|t| t.contains("the eviction removed")));
    let _ = evict(&c, now, false);
    assert!(note(&c).is_some_and(|t| t.contains("found nothing")));
    // switched off: no notice, no start
    c.off = true;
    let _ = evict(&c, now, false);
    assert!(judge(&e, &c, now).is_empty());
}

#[test]
fn a_build_holds_the_eviction_and_the_next_prompt_tries_again() {
    let (_base, mut c) = world();
    c.exe = "/bin/true".into();
    c.space = Some((1000, 100));
    let now = SystemTime::now();
    assert!(trigger(&c, "sid", now));
    std::fs::create_dir_all(c.proc.join("8")).unwrap();
    std::fs::write(c.proc.join("8/comm"), "cargo\n").unwrap();
    // the age shares run while a build holds the cache's (451 T246): a loose entry idle four days goes
    put(&c.root, &c.root.join("old.log"), 96);
    let dry = evict(&c, now, true);
    let listed = dry.stdout.contains("would remove") && c.root.join("old.log").exists();
    assert!(listed, "{}", dry.stdout);
    let held = evict(&c, now, false);
    assert!(held.code == 1 && held.stdout.contains("a build runs (8 cargo)"));
    let swept = held.stdout.contains("old.log") && !c.root.join("old.log").exists();
    assert!(swept, "{}", held.stdout);
    assert!(c.cargo.join("idle/cover-gate").exists());
    assert!(evict(&c, now, false)
        .stdout
        .starts_with("evict: a build runs"));
    // its stamp gone: the next prompt tries again
    assert!(trigger(&c, "sid", now));
    // another sweep holds the lock
    std::fs::remove_dir_all(c.proc.join("8")).unwrap();
    let lock = File::create(c.state.join("lock")).unwrap();
    assert!((0..500).any(|_| crate::shared::tool::flock(&lock, "-n")));
    assert!(evict(&c, now, false).stdout.contains("holds the lock"));
    // a disk df cannot read is never short
    c.space = None;
    c.cargo = c.state.join("no-such-cache");
    assert!(!trigger(&c, "sid", now + EVERY * 3));
}

#[test]
fn the_knob_and_the_stand_in_disk_read_from_the_environment() {
    let c = Config::from_env(
        &|k| match k {
            "L7R_DISK_FREE_PCT" => Some("35".to_owned()),
            "SCRATCH_SWEEP_DF" => Some("1000 20".to_owned()),
            "GUARD_LOG_DIR" => Some("/x/log".to_owned()),
            _ => None,
        },
        1,
    );
    assert!(
        (c.free_at - 0.35).abs() < 1e-9
            && c.space == Some((1000, 20))
            && c.disk() == Some((1000, 20))
    );
    assert_eq!(c.guard_log, Path::new("/x/log"));
    let d = Config::from_env(&|k| (k == "SCRATCH_SWEEP_DF").then(|| "junk".to_owned()), 1);
    assert!((d.free_at - 0.2).abs() < 1e-9 && d.space.is_none());
    assert!(super::super::df(Path::new("/")).is_some_and(|(s, f)| s >= f && s > 0));
    assert!(super::super::df(Path::new("/nonexistent/t245")).is_none());
}
