#!/usr/bin/env python3
"""451 T336: does a test build cut short (as the pre-warm cuts it) leave a state the next build fails to link from?

usage: t336-harness.py ARM N SEED OUT.jsonl
ARM: control  - dirty, one full build
     cut1     - dirty, one build cut (TERM to the group, cargo alone waited for - prewarm.rs's own kill), full build
     cut2     - dirty, two builds cut, full build (the sequence of 2026-11-26)
     cut2wait - as cut2, each cut then waits until the killed group is empty
     cut2inc0 - as cut2, the cut builds under CARGO_INCREMENTAL=0 (the full build as a real run's)
     int2     - as cut2 with SIGINT
     kill2    - as cut2 with SIGKILL
One cargo at a time, each under a machine build slot (flock of ~/.cache/l7r-build-slots/slot-<i>).
"""
import fcntl, hashlib, json, os, random, shutil, signal, subprocess, sys, time

ROOT = "/diagram/.clones/diagram-backlog-t270"
TGT = os.path.expanduser("~/.cache/l7r-cargo-target/diagram-backlog-t270")
INC = TGT + "/debug/incremental"
DEPS = TGT + "/debug/deps"
SLOTS = os.path.expanduser("~/.cache/l7r-build-slots")
WORK = os.path.dirname(os.path.abspath(__file__))
FILES = [ROOT + "/rust/guard/src/" + f for f in (
    "lib.rs", "guards/review_round_hooks.rs", "guards/make_only_hooks.rs", "guards/no_poll_hooks.rs",
    "guards/clone_sync_hooks.rs", "guards/idle_tests_hooks.rs", "guards/escalation_hooks.rs",
    "guards/context_cap_hooks.rs")]
MARK = "// t336-probe "
WORDS = ["cargo", "test", "--no-run", "--quiet", "--manifest-path", ROOT + "/rust/guard/Cargo.toml"]


def dirty(tag, two):
    for f in FILES:
        lines = open(f).read().split("\n")
        if lines[0].startswith(MARK):
            lines = lines[1:]
        # a new first line AND one line more or fewer by turns: every span of the file moves
        head = [MARK + tag] + ([MARK + tag + " b"] if two else [])
        open(f, "w").write("\n".join(head + [l for l in lines if not l.startswith(MARK)]))


def clean():
    for f in FILES:
        lines = open(f).read().split("\n")
        open(f, "w").write("\n".join(l for l in lines if not l.startswith(MARK)))


def slot():
    while True:
        for i in (0, 1):
            fd = os.open(f"{SLOTS}/slot-{i}", os.O_RDWR)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return fd
            except OSError:
                os.close(fd)
        time.sleep(0.25)


def group(pgid):
    out = []
    for p in os.listdir("/proc"):
        if not p.isdigit():
            continue
        try:
            st = open(f"/proc/{p}/stat").read()
            rest = st[st.rindex(")") + 2:].split()
            if int(rest[2]) != pgid or rest[0] == "Z":
                continue
            cmd = open(f"/proc/{p}/cmdline").read().split("\0")
        except (OSError, ValueError):
            continue
        exe = os.path.basename(cmd[0]) if cmd and cmd[0] else "?"
        what = exe
        if exe == "rustc" and "--crate-name" in cmd:
            what = "rustc:" + cmd[cmd.index("--crate-name") + 1] + (":test" if "--test" in cmd else "") + \
                (":bin" if "bin" in cmd[cmd.index("--crate-type") + 1:cmd.index("--crate-type") + 2] else "") \
                if "--crate-type" in cmd else "rustc:" + cmd[cmd.index("--crate-name") + 1] + (":test" if "--test" in cmd else "")
        out.append(what)
    return sorted(out)


def sessions():
    """Each finalized session file of the guard's incremental directories: (inode, size, mtime_ns)."""
    got = {}
    for d in sorted(os.listdir(INC)):
        if not d.startswith("l7r_guard-"):
            continue
        for s in os.listdir(f"{INC}/{d}"):
            p = f"{INC}/{d}/{s}"
            if not os.path.isdir(p):
                continue
            for f in os.listdir(p):
                try:
                    st = os.stat(f"{p}/{f}")
                except OSError:
                    continue
                got[f"{d}/{s}/{f}"] = (st.st_ino, st.st_size, st.st_mtime_ns, st.st_nlink)
    return got


def session_dirs():
    out = []
    for d in sorted(os.listdir(INC)):
        if d.startswith("l7r_guard-"):
            out += [f"{d}/{s}" for s in sorted(os.listdir(f"{INC}/{d}"))]
    return out


def strays():
    n = links = 0
    for f in os.listdir(DEPS):
        if f.startswith("l7r_guard-") and f.endswith(".rcgu.o"):
            n += 1
            try:
                links += os.stat(f"{DEPS}/{f}").st_nlink > 1
            except OSError:
                pass
    return n, links


def build(cut_at=None, sig="TERM", wait_group=False, inc0=False, log=None):
    """One test build; cut at `cut_at` seconds where given. Returns a record."""
    env = dict(os.environ, CARGO_TARGET_DIR=TGT)
    if inc0:
        env["CARGO_INCREMENTAL"] = "0"
    fd = slot()
    rec = {}
    t0 = time.time()
    err = open(log, "wb")
    child = subprocess.Popen(WORDS, cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=err, process_group=0)
    try:
        if cut_at is None:
            child.wait()
        else:
            while child.poll() is None and time.time() - t0 < cut_at:
                time.sleep(0.02)
            if child.poll() is None:
                rec["alive_at_cut"] = group(child.pid)
                subprocess.run(["kill", f"-{sig}", "--", f"-{child.pid}"], stderr=subprocess.DEVNULL)
                child.wait()
                rec["cut"] = True
                rec["survivors"] = group(child.pid)
                if wait_group:
                    w0 = time.time()
                    while group(child.pid) and time.time() - w0 < 30:
                        time.sleep(0.02)
                    rec["waited_s"] = round(time.time() - w0, 3)
            else:
                rec["cut"] = False
    finally:
        os.close(fd)
        err.close()
    rec["secs"] = round(time.time() - t0, 2)
    rec["code"] = child.returncode
    text = open(log, errors="replace").read()
    rec["link_fail"] = text.count("undefined hidden symbol")
    rec["other_err"] = [l[:200] for l in text.split("\n") if l.startswith("error") and "linking with" not in l][:3]
    rec["sessions"] = session_dirs()
    rec["strays"] = strays()
    return rec


def changed(before, after):
    """Files of sessions that stood before and still stand, whose inode, size or time moved (a finalized session written into)."""
    out = {}
    for k, v in before.items():
        if k in after and after[k][:3] != v[:3]:
            ext = k.rsplit(".", 1)[-1] + (":same-inode" if after[k][0] == v[0] else ":new-inode")
            out[ext] = out.get(ext, 0) + 1
    return out


def repair(tag):
    """Move the guard's incremental directories aside (the first failures kept as evidence), so the next build is from nothing."""
    keep = f"{WORK}/t336-evidence-{tag}"
    for d in sorted(os.listdir(INC)):
        if d.startswith("l7r_guard-"):
            if len([e for e in os.listdir(WORK) if e.startswith("t336-evidence-")]) < 2 or os.path.isdir(keep):
                os.makedirs(keep, exist_ok=True)
                shutil.move(f"{INC}/{d}", f"{keep}/{d}")
            else:
                shutil.rmtree(f"{INC}/{d}")


def main():
    arm, n, seed, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    rng = random.Random(seed)
    sig = {"int1": "INT", "kill1": "KILL"}.get(arm, "TERM")
    cuts = {"control": 0, "cut1": 1, "int1": 1, "kill1": 1}.get(arm, 2)
    full = float(os.environ.get("T336_FULL", "14"))
    try:
        clean()
        base = build(log=f"{WORK}/t336-last-base.err")
        print(arm, "base", base["code"], base["secs"], flush=True)
        if base["code"] != 0:
            repair("base")
            base = build(log=f"{WORK}/t336-last-base.err")
            print(arm, "base healed", base["code"], base["secs"], flush=True)
        for i in range(n):
            tag = f"{arm}-{seed}-{i}-{int(time.time())}"
            rec = {"arm": arm, "i": i, "tag": tag, "load": os.getloadavg()[0], "builds": []}
            dirty(tag, i % 2 == 1)
            before = sessions()
            for c in range(cuts):
                at = round(rng.uniform(float(os.environ.get("T336_LO", "0.5")), full), 2)
                b = build(cut_at=at, sig=sig, wait_group=arm == "cut2wait", inc0=arm == "cut2inc0",
                          log=f"{WORK}/t336-last-cut.err")
                b["cut_at"] = at
                b["session_files_changed"] = changed(before, sessions())
                rec["builds"].append(b)
            final = build(log=f"{WORK}/t336-last-final.err")
            rec["builds"].append(final)
            rec["final_code"] = final["code"]
            rec["final_link_fail"] = final["link_fail"]
            if final["code"] != 0:
                shutil.copy(f"{WORK}/t336-last-final.err", f"{WORK}/t336-fail-{tag}.err")
                repair(tag)
                healed = build(log=f"{WORK}/t336-last-heal.err")
                rec["healed_code"] = healed["code"]
                rec["healed_secs"] = healed["secs"]
            with open(out, "a") as f:
                f.write(json.dumps(rec) + "\n")
            print(arm, i, "final", final["code"], "link_fail", final["link_fail"],
                  [(b.get("cut_at"), b.get("cut"), b["secs"], b["code"]) for b in rec["builds"]], flush=True)
            if final["code"] != 0 and rec.get("healed_code") != 0:
                print("NOT HEALED - stopping", flush=True)
                break
    finally:
        clean()


if __name__ == "__main__":
    main()
