"""The controller writes the collected ids into `.testmondata` only after EVERY worker has collected
(`tests/_testmon_sync.py` carries the defect, the mechanism and the measurement)."""

from __future__ import annotations

from types import SimpleNamespace

from tests._testmon_sync import SyncWhenEveryWorkerHasCollected, install


class _Data:
    def __init__(self) -> None:
        self.synced: list[set[str]] = []

    def sync_db_fs_tests(self, retain: set[str]) -> None:
        self.synced.append(retain)


class _Inner:
    def __init__(self) -> None:
        self.nodes: list[object] = []

    def pytest_configure_node(self, node: object) -> None:
        self.nodes.append(node)


def _node(data: _Data) -> SimpleNamespace:
    return SimpleNamespace(config=SimpleNamespace(testmon_data=data))


def test_a_fast_worker_finishing_first_does_not_sync_early():
    data, inner = _Data(), _Inner()
    sync = SyncWhenEveryWorkerHasCollected(inner)
    nodes = [_node(data) for _ in range(3)]
    for n in nodes:
        sync.pytest_configure_node(n)
    assert inner.nodes == nodes  # each worker is still handed its execution id

    sync.pytest_xdist_node_collection_finished(nodes[0], ["a", "b"])
    sync.pytest_xdist_node_collection_finished(nodes[1], ["a", "b"])
    assert data.synced == []  # upstream's ready/finished counter reads zero here and writes

    sync.pytest_xdist_node_collection_finished(nodes[2], ["a", "b"])
    assert data.synced == [{"a", "b"}]


class TestmonXdistSync:
    """Named as testmon names it: `install` matches the class by name."""


class _Plugins:
    def __init__(self, *plugins: object) -> None:
        self.plugins = list(plugins)
        self.names: list[str] = []

    def get_plugins(self) -> list[object]:
        return self.plugins

    def unregister(self, plugin: object) -> None:
        self.plugins.remove(plugin)

    def register(self, plugin: object, name: str) -> None:
        self.plugins.append(plugin)
        self.names.append(name)


def test_install_replaces_testmons_sync_and_keeps_it_as_the_inner():
    upstream, other = TestmonXdistSync(), object()
    pm = _Plugins(other, upstream)
    assert install(SimpleNamespace(pluginmanager=pm)) is True
    assert upstream not in pm.plugins and other in pm.plugins
    (ours,) = [p for p in pm.plugins if isinstance(p, SyncWhenEveryWorkerHasCollected)]
    assert ours.inner is upstream and pm.names == ["SyncWhenEveryWorkerHasCollected"]


def test_install_leaves_a_run_without_testmons_sync_alone():
    pm = _Plugins(object())
    assert install(SimpleNamespace(pluginmanager=pm)) is False
    assert len(pm.plugins) == 1 and pm.names == []


def test_the_installed_testmon_still_has_the_counter_this_replaces():
    """When this fails, testmon changed its sync: read the new one, and retire the replacement if it
    now waits for every worker."""
    from testmon.pytest_testmon import TestmonXdistSync as Upstream

    assert hasattr(Upstream(), "await_nodes")
    assert {"pytest_configure_node", "pytest_xdist_node_collection_finished"} <= set(vars(Upstream))


def test_the_conftest_installs_it_after_testmon_has_registered_its_own():
    """Unmarked, the conftest's hook ran BEFORE testmon's and found nothing to replace: the forced
    reproduction still failed, which is how the ordering was found."""
    from tests import conftest

    assert conftest.pytest_configure.pytest_impl["trylast"] is True
