#!/usr/bin/env python3
"""A `then:` step that ADOPTS a session a stopped runner left running (2026-09-27, swapping the queue onto the runner
that resumes a session the usage limit ends, without killing the session in flight).

    adopt.py <pid> <session id> <brief>   -> waits for <pid> to exit; if its session failed, resumes it with the
                                              runner's own wait-and-resume; prints nothing (it queues no briefs)
"""

from __future__ import annotations

import importlib.util
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("runner", ROOT / "scripts" / "_page_session_runner.py")
assert spec and spec.loader
ps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ps)


def main(pid: int, sid: str, brief: str) -> int:
    while os.path.exists(f"/proc/{pid}"):
        time.sleep(30)
    log = ROOT / ".git" / "page-sessions" / sid
    asp = ROOT / "container-scripts" / "append-system-prompt.md"
    extra = ["--append-system-prompt", asp.read_text(encoding="utf-8")] if asp.is_file() else []
    base = ps.command(str(ROOT), ROOT.name, extra, brief, sid)
    env = ps.headless_env(os.environ, ps.dispatcher(str(ROOT)))
    for attempt in range(ps.RETRIES):
        text = ps._read(str(log / "result.json")) + ps._read(str(log / "stderr.txt"))
        # an orphan's exit code is not ours to read; its JSON result says whether it ended well, and no result is a failure
        if text.strip() and not ps.failed(0, text):
            return 0
        time.sleep(ps.wait_for(text, attempt, time.time()) if text.strip() else 60)
        with open(log / "result.json", "w") as out, open(log / "stderr.txt", "w") as err:
            subprocess.run(ps.resume_command(base, sid), cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=err, check=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(int(sys.argv[1]), sys.argv[2], sys.argv[3]))
