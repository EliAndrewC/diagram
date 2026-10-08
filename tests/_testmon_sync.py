"""testmon's xdist sync, held until EVERY worker has collected (2026-09-19).

THE DEFECT, MEASURED. `make quick` failed with xdist's "Different tests were collected between gw0 and
gwN" on the first run after a test file gained a test id, and passed on an unchanged re-run: six
recorded occurrences since 2026-09-05, always the later-started workers, always missing exactly the
NEW ids while keeping the file's old ones.

THE MECHANISM, in pytest-testmon 2.2.0. The controller's `TestmonXdistSync` counts `await_nodes` up on
`pytest_testnodeready` and down on `pytest_xdist_node_collection_finished`, and writes the collected
ids into `.testmondata` (`sync_db_fs_tests`) whenever the count touches zero. A fast worker can be
ready AND finished before a slow one is ready, so zero arrives early, while other workers are still
inside `TestmonData.determine_stable`. That method reads the database twice without one snapshot:
the affected tests first, `all_tests` after. A sync landing between the two shows the worker the new
ids in `all_tests` but not among the affected, so it files them as stable and deselects them - and
its collection no longer matches gw0's. Proved by widening that window with a sleep on every worker
but gw0: the failure became deterministic with the recorded signature.

NOT the bytecode cache: a `.pyc` is validated by source mtime AND size, and a file that gains a test
changes size.

THE FIX. Sync once, when as many workers have finished collecting as were configured. xdist calls
`pytest_configure_node` for every node before its loop handles any worker event, so the configured
count is complete before the first finish arrives. If a worker dies before it collects, the sync is
skipped for that run: results are still saved as tests report, and the next run syncs.
"""

from __future__ import annotations

from typing import Any


class SyncWhenEveryWorkerHasCollected:
    """Stands in for testmon's `TestmonXdistSync` on the controller. `inner` is the instance it
    replaces, kept for the one job that was never wrong: handing each worker the execution id."""

    def __init__(self, inner: Any) -> None:
        self.inner = inner
        self.configured = 0
        self.finished = 0

    def pytest_configure_node(self, node: Any) -> None:
        self.configured += 1
        self.inner.pytest_configure_node(node)

    def pytest_xdist_node_collection_finished(self, node: Any, ids: list[str]) -> None:
        self.finished += 1
        if self.finished == self.configured:
            node.config.testmon_data.sync_db_fs_tests(retain=set(ids))


def install(config: Any) -> bool:
    """Swap testmon's sync plugin for the one above. Matched by class NAME so that a testmon without
    the class (a fixed release, `--no-testmon`, a worker) leaves everything alone. True when swapped."""
    pm = config.pluginmanager
    for plugin in list(pm.get_plugins()):
        if type(plugin).__name__ == "TestmonXdistSync":
            pm.unregister(plugin)
            pm.register(SyncWhenEveryWorkerHasCollected(plugin), "SyncWhenEveryWorkerHasCollected")
            return True
    return False
