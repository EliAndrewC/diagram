"""`scripts/claim-feature.py` - `make claim` (feature 197): the next spec-kit number, under a lock.

Every case runs on a fixture built in `tmp_path`: a MIRROR (a real git repository whose `origin/main`
ref is one commit ahead of its working tree) with two real clones under `.clones/`. The concurrency
case runs twelve real processes against the one lock file. The one `tooling`-marked case drives the
real Makefile.

No seam is injected anywhere: `--root` and `--main` are ordinary arguments, and the lock is the real
`flock`. The proof that the lock DOES something is a measurement recorded in
`specs/197-claim-feature-numbers/research.md` R1 - the same twelve-process run with the flock lines
removed - because a test that disables its own lock would need a switch a session could reach."""

from __future__ import annotations

import fcntl
import importlib.util
import json
import os
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[5]
TOOL = REPO / "scripts" / "claim-feature.py"
SKILL = REPO / ".claude" / "skills" / "diagram"
_spec = importlib.util.spec_from_file_location("claim_feature", TOOL)
assert _spec and _spec.loader
cf = importlib.util.module_from_spec(_spec)
sys.modules["claim_feature"] = cf
_spec.loader.exec_module(cf)


def git(cwd: pathlib.Path, *args: str) -> str:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    return subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True, env=env).stdout.strip()


@pytest.fixture
def world(tmp_path: pathlib.Path) -> dict[str, pathlib.Path]:
    """mirror: specs/001-a, 002-b in the working tree; origin/main one commit ahead with 003-c.
    Two clones, alpha and beta, cloned at the working-tree commit."""
    mirror = tmp_path / "mirror"
    mirror.mkdir()
    git(mirror, "init", "-q")
    for name in ("001-a", "002-b"):
        (mirror / "specs" / name).mkdir(parents=True)
        (mirror / "specs" / name / "spec.md").write_text(name)
    git(mirror, "add", "-A")
    git(mirror, "commit", "-qm", "two")
    c1 = git(mirror, "rev-parse", "HEAD")
    (mirror / "specs" / "003-c").mkdir()
    (mirror / "specs" / "003-c" / "spec.md").write_text("c")
    git(mirror, "add", "-A")
    git(mirror, "commit", "-qm", "three")
    c2 = git(mirror, "rev-parse", "HEAD")
    git(mirror, "update-ref", "refs/remotes/origin/main", c2)
    git(mirror, "reset", "-q", "--hard", c1)
    assert not (mirror / "specs" / "003-c").exists()
    (mirror / ".clones").mkdir()
    for c in ("alpha", "beta"):
        git(tmp_path, "clone", "-q", str(mirror), str(mirror / ".clones" / c))
    return {"mirror": mirror, "alpha": mirror / ".clones" / "alpha", "beta": mirror / ".clones" / "beta"}


def run(root: pathlib.Path, slug: str, *opts: str, timeout: float | None = None) -> subprocess.CompletedProcess[str]:
    """The slug follows `--`, as the Makefile passes it, so `-a` is a bad slug rather than an option."""
    extra = ["--lock-timeout", str(timeout)] if timeout is not None else []
    return subprocess.run([sys.executable, str(TOOL), "--root", str(root), *opts, *extra, "--", slug], capture_output=True, text=True)


def ledger(world: dict[str, pathlib.Path]) -> list[dict]:
    p = world["mirror"] / ".specify" / "feature-numbers.jsonl"
    return [json.loads(line) for line in p.read_text().splitlines()] if p.exists() else []


# --- the four sources --------------------------------------------------------------------------------


def test_origin_main_ahead_of_the_working_tree_counts(world) -> None:
    """The mirror's tree says 002; its fetched origin/main says 003; the answer is 004."""
    r = run(world["alpha"], "first")
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "004-first"
    assert (world["alpha"] / "specs" / "004-first").is_dir()
    assert "main=002" in r.stderr and "origin/main=003" in r.stderr


def test_the_mirror_working_tree_alone_when_there_is_no_origin_ref(world) -> None:
    git(world["mirror"], "update-ref", "-d", "refs/remotes/origin/main")
    assert run(world["alpha"], "x").stdout.strip() == "003-x"


def test_another_clones_unpushed_claim_counts(world) -> None:
    """THE source the old protocol could not see: beta claimed 009 and has not pushed."""
    (world["beta"] / "specs" / "009-betas").mkdir()
    assert run(world["alpha"], "mine").stdout.strip() == "010-mine"


def test_a_ledger_row_with_no_directory_anywhere_still_counts(world) -> None:
    (world["mirror"] / ".specify").mkdir()
    (world["mirror"] / ".specify" / "feature-numbers.jsonl").write_text(json.dumps({"number": 20, "slug": "gone", "clone": "x", "utc": "t"}) + "\n" + "not json\n")
    assert run(world["alpha"], "after").stdout.strip() == "021-after"


def test_a_missing_ledger_is_recreated_not_an_error(world) -> None:
    assert not (world["mirror"] / ".specify").exists()
    r = run(world["alpha"], "fresh")
    assert r.returncode == 0
    rows = ledger(world)
    assert len(rows) == 1 and rows[0]["number"] == 4 and rows[0]["slug"] == "fresh" and rows[0]["clone"] == "alpha"


# --- outputs -----------------------------------------------------------------------------------------


def test_writes_feature_json_and_prints_the_two_exports(world) -> None:
    r = run(world["alpha"], "point")
    fj = json.loads((world["alpha"] / ".specify" / "feature.json").read_text())
    assert fj == {"feature_directory": "specs/004-point"}
    assert "export SPECIFY_FEATURE=004-point" in r.stderr
    assert "export SPECIFY_FEATURE_DIRECTORY=specs/004-point" in r.stderr


def test_dry_run_names_the_claim_and_creates_and_records_nothing(world) -> None:
    r = run(world["alpha"], "look", "--dry-run")
    assert r.returncode == 0 and r.stdout.strip() == "004-look"
    assert not (world["alpha"] / "specs" / "004-look").exists()
    assert ledger(world) == []
    assert not (world["alpha"] / ".specify" / "feature.json").exists()
    assert run(world["alpha"], "look", "--dry-run").stdout.strip() == "004-look", "a look does not move the number"


def test_two_claims_in_a_row_are_consecutive(world) -> None:
    assert run(world["alpha"], "one").stdout.strip() == "004-one"
    assert run(world["beta"], "two").stdout.strip() == "005-two"
    assert [r["number"] for r in ledger(world)] == [4, 5]


# --- refusals: exit 2, nothing created, nothing appended -----------------------------------------------


def _refused(world, r: subprocess.CompletedProcess[str], *words: str) -> None:
    assert r.returncode == 2, (r.stdout, r.stderr)
    assert r.stdout == ""
    assert "REFUSED" in r.stderr and all(w in r.stderr for w in words), r.stderr
    assert ledger(world) == []
    for c in ("alpha", "beta"):
        assert sorted(p.name for p in (world[c] / "specs").iterdir()) == ["001-a", "002-b"]


def test_refuses_to_run_from_the_mirror(world) -> None:
    _refused(world, run(world["mirror"], "x"), "MIRROR", "never a workspace")
    assert not (world["mirror"] / "specs" / "003-x").exists()


@pytest.mark.parametrize("bad", ["Bad_Slug", "a--b", "-a", "a-", "with space", "", "ünï"])
def test_refuses_a_slug_that_is_not_kebab(world, bad: str) -> None:
    _refused(world, run(world["alpha"], bad), "kebab")


def test_refuses_a_slug_already_in_use_in_another_clone(world) -> None:
    (world["beta"] / "specs" / "007-taken").mkdir()
    r = run(world["alpha"], "taken")
    assert r.returncode == 2 and "007-taken" in r.stderr and "already in use" in r.stderr
    assert not any(p.name.endswith("-taken") for p in (world["alpha"] / "specs").iterdir())


def test_refuses_when_the_lock_is_held_and_names_the_file(world) -> None:
    lock = world["mirror"] / ".specify" / "feature-numbers.lock"
    lock.parent.mkdir()
    fd = os.open(lock, os.O_RDWR | os.O_CREAT)
    fcntl.flock(fd, fcntl.LOCK_EX)
    try:
        r = run(world["alpha"], "waiting", timeout=0.3)
        _refused(world, r, "lock", str(lock))
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
    assert run(world["alpha"], "waiting").returncode == 0, "released, the same claim goes through"


# --- the existing collision is reported, never fixed ----------------------------------------------------


def test_a_duplicate_number_in_main_is_warned_about_and_the_claim_proceeds(world) -> None:
    (world["mirror"] / "specs" / "002-other").mkdir()
    r = run(world["alpha"], "go")
    assert r.returncode == 0 and r.stdout.strip() == "004-go"
    assert "WARNING" in r.stderr and "002 twice" in r.stderr and "002-b" in r.stderr and "002-other" in r.stderr
    assert (world["mirror"] / "specs" / "002-other").is_dir() and (world["mirror"] / "specs" / "002-b").is_dir(), "nothing renumbered"


# --- the property the whole feature exists for ---------------------------------------------------------


def _concurrent(roots: list[pathlib.Path], n: int) -> list[str]:
    procs = [subprocess.Popen([sys.executable, str(TOOL), "--root", str(roots[i % len(roots)]), "--", f"s{i}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for i in range(n)]
    outs = []
    for p in procs:
        out, err = p.communicate(timeout=60)
        assert p.returncode == 0, err
        outs.append(out.strip())
    return outs


def test_twelve_concurrent_claims_from_one_clone_are_distinct_and_consecutive(world) -> None:
    names = _concurrent([world["alpha"]], 12)
    numbers = sorted(int(x.split("-")[0]) for x in names)
    assert numbers == list(range(4, 16)), names
    assert len(set(names)) == 12
    assert sorted(r["number"] for r in ledger(world)) == numbers


def test_twelve_concurrent_claims_split_across_two_clones_are_distinct_and_consecutive(world) -> None:
    names = _concurrent([world["alpha"], world["beta"]], 12)
    assert sorted(int(x.split("-")[0]) for x in names) == list(range(4, 16)), names
    created = sorted(p.name for c in ("alpha", "beta") for p in (world[c] / "specs").iterdir() if p.name[0] != "0" or int(p.name[:3]) > 2)
    assert len(created) == 12


# --- renumbering: a deduplication is a claim under the same lock (GM 2026-09-07) --------------------------


def renumber(root: pathlib.Path, spec_dir: str, *opts: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(TOOL), "--root", str(root), "--renumber", spec_dir, *opts], capture_output=True, text=True)


def test_renumber_moves_a_tracked_directory_to_the_next_number_and_records_where_it_came_from(world) -> None:
    """alpha's tracked 002-b is a duplicate of something: it moves to 004-b via git mv, staged."""
    r = renumber(world["alpha"], "specs/002-b")
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "004-b"
    assert not (world["alpha"] / "specs" / "002-b").exists() and (world["alpha"] / "specs" / "004-b" / "spec.md").read_text() == "002-b"
    assert "R" in git(world["alpha"], "status", "--porcelain", "--", "specs"), "git mv staged the rename"
    rows = ledger(world)
    assert rows == [{**rows[0], "number": 4, "slug": "b", "renumbered_from": 2, "clone": "alpha"}]
    assert not (world["alpha"] / ".specify" / "feature.json").exists(), "a renumber does not repoint the clone's active feature"
    assert "renumbered specs/002-b/ -> specs/004-b/" in r.stderr and "fix every reference" in r.stderr


def test_renumber_of_an_untracked_claim_is_a_plain_rename(world) -> None:
    (world["alpha"] / "specs" / "003-mine").mkdir()
    assert renumber(world["alpha"], "specs/003-mine").stdout.strip() == "004-mine"
    assert (world["alpha"] / "specs" / "004-mine").is_dir() and not (world["alpha"] / "specs" / "003-mine").exists()


def test_renumber_is_not_tripped_by_its_own_slug_but_is_by_another_directory_with_it(world) -> None:
    (world["beta"] / "specs" / "007-b").mkdir()
    r = renumber(world["alpha"], "specs/002-b")
    assert r.returncode == 2 and "007-b" in r.stderr and "already in use" in r.stderr
    assert (world["alpha"] / "specs" / "002-b").is_dir(), "nothing moved"


def test_renumber_refuses_a_directory_that_is_not_there_and_a_bare_slug_at_the_same_time(world) -> None:
    r = renumber(world["alpha"], "specs/009-nothing")
    assert r.returncode == 2 and "not an existing" in r.stderr
    r = subprocess.run([sys.executable, str(TOOL), "--root", str(world["alpha"]), "--renumber", "specs/002-b", "--", "also-a-slug"], capture_output=True, text=True)
    assert r.returncode == 2 and "exactly one" in r.stderr
    r = subprocess.run([sys.executable, str(TOOL), "--root", str(world["alpha"])], capture_output=True, text=True)
    assert r.returncode == 2 and "exactly one" in r.stderr
    assert (world["alpha"] / "specs" / "002-b").is_dir() and ledger(world) == []


def test_renumber_dry_run_moves_nothing(world) -> None:
    r = renumber(world["alpha"], "specs/002-b", "--dry-run")
    assert r.returncode == 0 and r.stdout.strip() == "004-b"
    assert (world["alpha"] / "specs" / "002-b").is_dir() and ledger(world) == []


def test_renumber_follows_the_same_sources_as_a_claim(world) -> None:
    (world["beta"] / "specs" / "011-x").mkdir()
    assert renumber(world["alpha"], "specs/001-a").stdout.strip() == "012-a"


# --- the derivations, on their own -----------------------------------------------------------------------


def test_mirror_of_is_the_grandparent_only_under_dot_clones(tmp_path) -> None:
    assert cf.mirror_of(tmp_path / "m" / ".clones" / "x") == tmp_path / "m"
    assert cf.mirror_of(tmp_path / "m" / "elsewhere" / "x") == tmp_path / "m" / "elsewhere" / "x"


def test_numbered_dirs_ignores_files_and_unnumbered_names(tmp_path) -> None:
    (tmp_path / "010-real").mkdir()
    (tmp_path / "notes").mkdir()
    (tmp_path / "011-file").write_text("")
    assert cf.numbered_dirs(tmp_path) == [(10, "010-real")]
    assert cf.numbered_dirs(tmp_path / "absent") == []


def test_duplicates_in_reports_a_number_under_two_names_only() -> None:
    assert cf.duplicates_in([(1, "001-a"), (1, "001-a"), (2, "002-b"), (2, "002-c")]) == [(2, ["002-b", "002-c"])]


# --- the target -----------------------------------------------------------------------------------------


@pytest.mark.tooling
def test_make_claim_through_the_real_makefile(world) -> None:
    """The wiring: `make claim SLUG=... PEEK=1` from a clone's skill dir reaches the tool."""
    clone = world["alpha"]
    skill = clone / ".claude" / "skills" / "diagram"
    skill.mkdir(parents=True)
    (skill / "Makefile").write_bytes((SKILL / "Makefile").read_bytes())
    (skill / "pyproject.toml").write_bytes((SKILL / "pyproject.toml").read_bytes())
    (skill / "l7r").symlink_to(SKILL / "l7r", target_is_directory=True)
    (skill / "dev").mkdir()
    (clone / "scripts").mkdir()
    (clone / "scripts" / "claim-feature.py").write_bytes(TOOL.read_bytes())
    env = {k: v for k, v in os.environ.items() if k not in {"MAKEFLAGS", "MFLAGS", "MAKELEVEL", "FULL", "REF_WHY", "COV_FLOORS"}}
    r = subprocess.run(["make", "--no-print-directory", "-C", str(skill), "claim", "SLUG=wired", "PEEK=1"], capture_output=True, text=True, env=env, timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip().endswith("004-wired"), r.stdout
    assert not (clone / "specs" / "004-wired").exists(), "PEEK claims nothing"
    r = subprocess.run(["make", "--no-print-directory", "-C", str(skill), "claim"], capture_output=True, text=True, env=env, timeout=120)
    assert r.returncode != 0 and "SLUG" in r.stdout + r.stderr, "no slug is a refusal that names the variable"
