"""Give a worker's freed heap back to the kernel after a test that grew it (2026-10-04, GM: "land the trim hook").

WHY. A test worker never shrinks on its own: a test that builds the record's site, parses every engine module or
loads the record frees what it built, but glibc keeps the freed arenas, so the worker rests at its high-water mark
for the rest of the run. Measured on a `make test-full` (10 workers, 10,921 tests): workers started at ~180 MB and
ended at 250-770 MB, and the run peaked at 5.7 GB of resident memory - two gates at once overran the 10 GB cap the
containers share. With `gc.collect()` + `malloc_trim(0)` after any test that grew the worker past `GROWTH_KB`,
21 tests triggered it, they returned 1.36 GB between them, and the peak fell to 4.1 GB (median 2.9 -> 2.5 GB);
the trims themselves cost nothing measurable. The roll does the same when it ends (`l7r/diagram/_memory.py`,
feature 210); this is that courtesy for the tests that are not rolls.

THE GATE IS GROWTH, NOT EVERY TEST: a trim after each of 11k tests would cost a collection each; growth past
16 MB is rare (the 21) and is exactly where the freed memory is.

/proc IS READ THROUGH os.open, BOUND AT IMPORT: tests stub `builtins.open` to fail (feature 221's memory sampler
found it). Off Linux there is no /proc and nothing is trimmed.
"""

from __future__ import annotations

import gc
import os

import pytest

from l7r.diagram import _memory

GROWTH_KB = 16 * 1024  # the measured run's 21 trimming tests each grew 30-480 MB; ordinary tests grow 0-2 MB

_os_open, _os_read, _os_close = os.open, os.read, os.close


def rss_kb() -> int:
    """This process's resident set in kB, or 0 where /proc is not there."""
    try:
        fd = _os_open("/proc/self/statm", os.O_RDONLY)
    except OSError:
        return 0
    try:
        return int(_os_read(fd, 128).split()[1]) * (os.sysconf("SC_PAGE_SIZE") // 1024)
    finally:
        _os_close(fd)


def trim_if_grown(before_kb: int, after_kb: int) -> bool:
    """Collect and trim when the test grew the worker past `GROWTH_KB`; say whether it did."""
    if after_kb - before_kb <= GROWTH_KB:
        return False
    gc.collect()
    _memory.trim_heap()
    return True


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):  # type: ignore[no-untyped-def]
    before = rss_kb()
    yield
    trim_if_grown(before, rss_kb())
