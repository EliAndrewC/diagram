//! A stopped landing stops its runs: the landings of a tree found, the TERM sent, and the handler's work in a child of the test.

use std::path::Path;
use std::process::{Command, Stdio};
use std::time::Duration;

use l7r_gate_core::ci::fixtures::{put, scratch};

use super::{catch_term, hold, kill_group, landing_pids, release, stop, stopped};

/// A `stop` that prints nothing a test reads.
fn quiet(_: &str) {}

/// The process is gone, or a zombie no one has reaped yet: either way, stopped.
fn ended_or_zombie(pid: u32) -> bool {
    !std::fs::read_to_string(format!("/proc/{pid}/stat"))
        .unwrap_or_default()
        .contains(" S ")
}

/// A fake `/proc` entry: its command line and its working directory.
fn entry(proc: &Path, pid: &str, cmdline: &[&str], cwd: &Path) {
    let d = proc.join(pid);
    std::fs::create_dir_all(&d).unwrap();
    std::fs::write(d.join("cmdline"), cmdline.join("\0") + "\0").unwrap();
    std::os::unix::fs::symlink(cwd, d.join("cwd")).unwrap();
}

#[test]
fn the_tree_s_landings_are_the_land_processes_working_in_it() {
    quiet("unused");
    let dir = scratch("stop-pids");
    let (proc, root, other) = (dir.join("proc"), dir.join("root"), dir.join("other"));
    std::fs::create_dir_all(&root).unwrap();
    std::fs::create_dir_all(&other).unwrap();
    entry(
        &proc,
        "999999999",
        &["/t/l7r-gate", "land", "449", "T1"],
        &root,
    );
    entry(&proc, "11", &["sh", "-c", "l7r-gate land 449 T1"], &root);
    entry(&proc, "12", &["/t/l7r-gate", "land", "449"], &other);
    entry(&proc, "13", &["/t/l7r-gate", "stamp"], &root);
    entry(
        &proc,
        &std::process::id().to_string(),
        &["/t/l7r-gate", "land"],
        &root,
    );
    put(&proc, "self/cmdline", "x");
    std::fs::create_dir_all(proc.join("14")).unwrap();
    put(&proc, "+15/cmdline", "x");
    assert_eq!(landing_pids(&root, &proc), vec![999_999_999]);
    assert!(landing_pids(&root, &dir.join("none")).is_empty());
    let mut said = Vec::new();
    assert_eq!(
        stop(&root, &dir.join("none"), &mut |l| said.push(l.to_owned())),
        Ok(0)
    );
    assert_eq!(
        said,
        vec![format!(
            "land-stop: no landing running in {}",
            root.display()
        )]
    );
    // pid 999999999 is no process here: os.kill raised
    assert!(stop(&root, &proc, &mut quiet).is_err());
}

#[test]
fn a_running_landing_is_sent_term() {
    let dir = scratch("stop-term");
    let root = dir.join("root");
    std::fs::create_dir_all(&root).unwrap();
    let mut child = Command::new("sleep").arg("30").spawn().unwrap();
    let proc = dir.join("proc");
    entry(
        &proc,
        &child.id().to_string(),
        &["/t/l7r-gate", "land"],
        &root,
    );
    let mut said = Vec::new();
    assert_eq!(stop(&root, &proc, &mut |l| said.push(l.to_owned())), Ok(0));
    assert_eq!(said, vec![format!("land-stop: stopped {}", child.id())]);
    let _ = child.wait();
    assert!(!kill_group(u32::MAX));
    hold(1);
    release(1);
    // an INT stops nothing of the landing's own
    stopped(2);
}

/// The handler's work, in a child of this test started in its own process group (its own group is what the handler stops last): the
/// child holds a sleeper's group, catches TERM and says so; TERM to it ends the sleeper and the child exits 143.
#[test]
fn term_stops_every_held_group_and_exits_143() {
    if let Ok(note) = std::env::var("L7R_LAND_TERM_CHILD") {
        #[expect(
            clippy::zombie_processes,
            reason = "the handler under test stops the sleeper and exits; nothing is left to wait"
        )]
        let sleeper =
            std::os::unix::process::CommandExt::process_group(Command::new("sleep").arg("30"), 0)
                .spawn()
                .unwrap();
        hold(sleeper.id());
        catch_term();
        // an in-process call's first scratch directory, after the catch (the replaced-handler fault the differential found)
        let _scratch = l7r_guard::shared::tempdir::TempDir::new("land-stop-scratch");
        std::fs::write(&note, format!("{}\n", sleeper.id())).unwrap();
        std::thread::sleep(Duration::from_secs(30));
        return;
    }
    let dir = scratch("stop-handler");
    let note = dir.join("note");
    let mut child = std::os::unix::process::CommandExt::process_group(
        Command::new(std::env::current_exe().unwrap())
            .args([
                "--exact",
                "land::stop::tests::term_stops_every_held_group_and_exits_143",
            ])
            .env("L7R_LAND_TERM_CHILD", &note)
            .stdout(Stdio::null())
            .stderr(Stdio::null()),
        0,
    )
    .spawn()
    .unwrap();
    let sleeper: u32 = (0..400)
        .find_map(|_| {
            std::thread::sleep(Duration::from_millis(25));
            std::fs::read_to_string(&note)
                .ok()
                .filter(|t| t.ends_with('\n'))
        })
        .unwrap()
        .trim()
        .parse()
        .unwrap();
    assert!(Command::new("kill")
        .args(["-TERM", &child.id().to_string()])
        .status()
        .unwrap()
        .success());
    let ended = (0..400).find_map(|_| {
        std::thread::sleep(Duration::from_millis(25));
        child.try_wait().unwrap()
    });
    let _ = child.kill();
    assert_eq!(ended.and_then(|s| s.code()), Some(143));
    let gone = (0..400).any(|_| {
        std::thread::sleep(Duration::from_millis(25));
        ended_or_zombie(sleeper)
    });
    assert!(gone);
}
