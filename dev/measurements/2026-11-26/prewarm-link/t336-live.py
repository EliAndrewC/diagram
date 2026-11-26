#!/usr/bin/env python3
"""451 T336, the fix run live in the pool tree, on the real path.

usage: t336-live.py slot|run N SEED SINCE OUT.jsonl   - the real `l7r-gate rust prewarm --since SINCE` over dirtied guard sources;
           `slot`: a build slot taken by hand mid-compile and held 3 s (the old code cut the build then);
           `run`:  `make rust-test CRATE=rust/guard` started mid-compile (the old code ended the pre-warm by a kill);
           then, for `slot`, a full test build: does it link?
       t336-live.py heal OUT.jsonl                    - the cache broken by cut builds until a link fails, then the real
           `make rust-test CRATE=rust/guard`: does the gate's own test build heal it?
"""
import fcntl, importlib.util, json, os, random, subprocess, sys, time

WORK = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("h", WORK + "/t336-harness.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
ENV = dict(os.environ, SPECIFY_FEATURE="451-time-retro-and-efficiency",
           SPECIFY_FEATURE_DIRECTORY="specs/451-time-retro-and-efficiency")


def rust_test(log):
    t0 = time.time()
    with open(log, "wb") as out:
        code = subprocess.run(["make", "rust-test", "CRATE=rust/guard"], cwd=h.ROOT, env=ENV, stdin=subprocess.DEVNULL,
                              stdout=out, stderr=subprocess.STDOUT).returncode
    text = open(log, errors="replace").read()
    return {"code": code, "secs": round(time.time() - t0, 2), "link_fail": text.count("undefined hidden symbol"),
            "healed_line": [l[:400] for l in text.split("\n") if "mixed incremental session" in l][:1],
            "blocking": text.count("Blocking waiting for file lock")}


def guard_rustc():
    """Is a rustc of the guard crate at work under this tree's target directory?"""
    for p in os.listdir("/proc"):
        if p.isdigit():
            try:
                cmd = open(f"/proc/{p}/cmdline").read().split("\0")
            except OSError:
                continue
            if cmd and os.path.basename(cmd[0]) == "rustc" and "l7r_guard" in cmd and any(h.TGT in c for c in cmd):
                return True
    return False


def live(mode, n, seed, since, out):
    rng = random.Random(seed)
    h.clean()
    base = h.build(log=f"{WORK}/t336-live-base.err")
    print(mode, "base", base["code"], base["secs"], flush=True)
    try:
        for i in range(n):
            tag = f"live-{mode}-{seed}-{i}-{int(time.time())}"
            h.dirty(tag, i % 2 == 1)
            rec = {"mode": mode, "i": i, "tag": tag, "load": os.getloadavg()[0]}
            log = open(f"{WORK}/t336-live-prewarm.log", "wb")
            t0 = time.time()
            pre = subprocess.Popen(["scripts/gates/l7r-gate.sh", "rust", "prewarm", "--since", since], cwd=h.ROOT, env=ENV,
                                   stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
            # the moment: a rustc of the guard is at work, then a delay into its compile
            while pre.poll() is None and not guard_rustc():
                time.sleep(0.05)
            delay = round(rng.uniform(0.5, 8.0), 2)
            time.sleep(delay)
            rec["delay_into_rustc"] = delay
            rec["rustc_alive_at_moment"] = guard_rustc()
            if mode == "slot":
                held = None
                for s in (0, 1):
                    fd = os.open(f"{h.SLOTS}/slot-{s}", os.O_RDWR)
                    try:
                        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        held = fd
                        break
                    except OSError:
                        os.close(fd)
                rec["slot_taken"] = held is not None
                time.sleep(3)
                if held is not None:
                    os.close(held)
                pre.wait()
                rec["prewarm_secs"] = round(time.time() - t0, 2)
                final = h.build(log=f"{WORK}/t336-live-final.err")
                rec["final_code"], rec["final_link_fail"], rec["final_secs"] = final["code"], final["link_fail"], final["secs"]
            else:
                real = rust_test(f"{WORK}/t336-live-run.log")
                pre.wait()
                rec["prewarm_secs"] = round(time.time() - t0, 2)
                rec["final_code"], rec["final_link_fail"], rec["final_secs"] = real["code"], real["link_fail"], real["secs"]
                rec["run"] = real
            log.close()
            rec["prewarm_lines"] = [l for l in open(f"{WORK}/t336-live-prewarm.log", errors="replace").read().split("\n")
                                    if l.startswith("prewarm:")]
            with open(out, "a") as f:
                f.write(json.dumps(rec) + "\n")
            print(mode, i, "final", rec["final_code"], "link_fail", rec["final_link_fail"], rec["prewarm_lines"][1:], flush=True)
            if rec["final_link_fail"]:
                h.repair(tag)
    finally:
        h.clean()


def heal(out):
    rng = random.Random(99)
    h.clean()
    h.build(log=f"{WORK}/t336-heal-base.err")
    try:
        broke = None
        for i in range(12):
            h.dirty(f"heal-{i}-{int(time.time())}", i % 2 == 1)
            for _ in range(2):
                h.build(cut_at=round(rng.uniform(4, 10), 2), log=f"{WORK}/t336-heal-cut.err")
            probe = h.build(log=f"{WORK}/t336-heal-probe.err")
            print("heal probe", i, probe["code"], probe["link_fail"], flush=True)
            if probe["link_fail"]:
                broke = probe
                break
        if broke is None:
            print("never broke", flush=True)
            return
        before = h.session_dirs()
        first = rust_test(f"{WORK}/t336-heal-run.log")
        after = h.session_dirs()
        rec = {"mode": "heal", "broken_link_fail": broke["link_fail"], "rust_test": first,
               "dirs_before": sorted({d.split("/")[0] for d in before}), "dirs_after": sorted({d.split("/")[0] for d in after})}
        with open(out, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(json.dumps(rec)[:1500], flush=True)
    finally:
        h.clean()


if __name__ == "__main__":
    if sys.argv[1] == "heal":
        heal(sys.argv[2])
    else:
        live(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5])
