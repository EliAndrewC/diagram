"""Give freed C memory back to the kernel (feature 210, GM 2026-09-07: "we should do the malloc_trim after a roll").

WHY THIS EXISTS. A hamlet roll allocates and frees a great deal of C memory - the geometry indexes'
buckets, the router's path lists - and glibc keeps the freed arena pages for reuse rather than returning
them: measured at the end of a full run, 14 to 68 MB per test worker sat freed-but-retained
(`mallinfo2.fordblks`; `specs/210-the-roll-leaves-the-worker/research.md` R1). Eight workers, all of it
charged to the container. `malloc_trim(0)` returns the free pages at the top of every arena to the
kernel; it costs a few milliseconds and nothing is lost, since the next roll allocates afresh.

Called from `hamletgen.driver.roll_scope()` when a roll ends - every roll, whatever ran it.
"""

from __future__ import annotations

import ctypes


def trim_heap() -> bool:
    """`malloc_trim(0)`; True when it ran. False - never an exception - where libc or the symbol is not
    there (a non-glibc platform), because a memory courtesy must never turn a roll red."""
    try:
        libc = ctypes.CDLL("libc.so.6")
        libc.malloc_trim(0)
    except OSError, AttributeError:
        return False
    return True
