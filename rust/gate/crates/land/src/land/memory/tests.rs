//! The cohort's workers from the processors and the memory the gate leaves.

use std::time::SystemTime;

use l7r_gate_core::ci::fixtures::{put, scratch};

use super::super::tests::fx;
use super::{cpus_online, py_int, second, shared_free_mb};

fn now() -> f64 {
    SystemTime::now()
        .duration_since(SystemTime::UNIX_EPOCH)
        .unwrap()
        .as_secs_f64()
}

#[test]
fn the_processors_online_are_counted_from_the_kernel_s_list() {
    let dir = scratch("mem-cpus");
    put(&dir, "a", "0-11\n");
    put(&dir, "b", "0,2-5\n");
    put(&dir, "c", "x\n");
    assert_eq!(cpus_online(&dir.join("a")), Some(12));
    assert_eq!(cpus_online(&dir.join("b")), Some(5));
    assert_eq!(cpus_online(&dir.join("c")), None);
    assert_eq!(cpus_online(&dir.join("none")), None);
}

#[test]
fn an_int_is_read_as_python_reads_one() {
    assert_eq!(py_int(" 12\n"), Ok(12));
    assert_eq!(py_int("1_000"), Ok(1000));
    assert_eq!(py_int("-3"), Ok(-3));
    for bad in ["", "_1", "1_", "1__0", "x", "99999999999999999999"] {
        assert!(py_int(bad).is_err());
    }
    assert_eq!(second("a b"), Ok("b"));
    assert!(second("a").is_err());
}

#[test]
fn the_shared_cap_is_read_from_the_newest_fresh_notice_that_carries_it() {
    let dir = scratch("mem-watch");
    let mw = dir.join("mw");
    assert_eq!(shared_free_mb(&mw, now()), Ok(None));
    put(&mw, "latest", "\n");
    assert!(shared_free_mb(&mw, now()).is_err());
    put(&mw, "latest", "x\n");
    assert_eq!(shared_free_mb(&mw, now()), Ok(None));
    std::fs::write(mw.join("latest"), [0xff]).unwrap();
    assert_eq!(shared_free_mb(&mw, now()), Ok(None));
    put(&mw, "latest", "6 rest\n");
    // a notice whose file is gone between the listing and its stat: passed over
    std::fs::create_dir_all(mw.join("events")).unwrap();
    std::os::unix::fs::symlink(mw.join("nowhere"), mw.join("events/6.txt")).unwrap();
    put(
        &mw,
        "events/1.txt",
        "working set is 8.5 of their shared 10 GB\n",
    );
    put(&mw, "events/2.txt", "memguard killed a process\n");
    std::fs::create_dir_all(mw.join("events/3.txt")).unwrap();
    put(
        &mw,
        "events/7.txt",
        "working set is 1 of their shared 10 GB\n",
    );
    put(
        &mw,
        "events/x.txt",
        "working set is 1 of their shared 10 GB\n",
    );
    put(&mw, "events/5.log", "");
    assert_eq!(shared_free_mb(&mw, now()), Ok(Some(1536)));
    assert_eq!(shared_free_mb(&mw, now() + 10_000.0), Ok(None));
    put(
        &mw,
        "events/2.txt",
        "working set is 1.2.3 of their shared 10 GB\n",
    );
    assert!(shared_free_mb(&mw, now()).is_err());
    put(&mw, "events/2.txt", "nothing\n");
    put(&mw, "events/1.txt", "nothing\n");
    assert_eq!(shared_free_mb(&mw, now()), Ok(None));
}

#[test]
fn the_memory_free_is_the_least_of_the_host_the_cgroup_and_the_shared_cap() {
    let mut fx = fx("mem-free");
    let cg = fx.land.cgroup.clone();
    assert_eq!(fx.land.memory_free_mb(), Ok(5500));
    std::fs::write(
        &fx.land.meminfo,
        "MemTotal: 1 kB\nMemAvailable: 10240000 kB\n",
    )
    .unwrap();
    assert_eq!(fx.land.memory_free_mb(), Ok(10000));
    std::fs::write(&fx.land.meminfo, "MemAvailable: lots kB\n").unwrap();
    assert_eq!(fx.land.memory_free_mb(), Ok(5500));
    std::fs::write(&fx.land.meminfo, "MemAvailable:\n").unwrap();
    assert!(fx.land.memory_free_mb().is_err());
    std::fs::write(&fx.land.meminfo, [0xff]).unwrap();
    assert_eq!(fx.land.memory_free_mb(), Ok(5500));
    std::fs::write(&fx.land.meminfo, "MemAvailable: 10240000 kB\n").unwrap();
    put(&cg, "memory.max", "max\n");
    assert_eq!(fx.land.memory_free_mb(), Ok(10000));
    put(&cg, "memory.max", "4294967296\n");
    assert_eq!(fx.land.memory_free_mb(), Ok(10000));
    put(&cg, "memory.current", "1073741824\n");
    assert_eq!(fx.land.memory_free_mb(), Ok(10000));
    put(
        &cg,
        "memory.stat",
        "active_file 1\ninactive_file 1073741824\n",
    );
    assert_eq!(fx.land.memory_free_mb(), Ok(4096));
    put(&cg, "memory.stat", "anon 1\n");
    assert_eq!(fx.land.memory_free_mb(), Ok(3072));
    put(&cg, "memory.stat", "inactive_file x\n");
    assert_eq!(fx.land.memory_free_mb(), Ok(10000));
    put(&cg, "memory.stat", "inactive_file \n");
    assert!(fx.land.memory_free_mb().is_err());
    put(&cg, "memory.stat", "anon 1\n");
    put(&cg, "memory.current", "lots\n");
    assert_eq!(fx.land.memory_free_mb(), Ok(10000));
    put(&cg, "memory.current", "1073741824\n");
    put(&cg, "memory.max", "big\n");
    assert_eq!(fx.land.memory_free_mb(), Ok(10000));
    put(&fx.land.memwatch, "latest", "1\n");
    put(
        &fx.land.memwatch,
        "events/1.txt",
        "working set is 9 of their shared 10 GB\n",
    );
    assert_eq!(fx.land.memory_free_mb(), Ok(1024));
    assert_eq!(fx.land.cohort_jobs(), Ok((2, 1024)));
    fx.land.cpus = None;
    std::fs::remove_file(fx.land.memwatch.join("latest")).unwrap();
    assert_eq!(fx.land.cohort_jobs(), Ok((2, 10000)));
    put(&fx.land.memwatch, "latest", "\n");
    assert!(fx.land.cohort_jobs().is_err());
}
