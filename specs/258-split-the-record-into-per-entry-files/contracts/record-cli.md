# Contract: `make record` and what it says

One command, three modes. The shape is `make citations`' - a derived, committed asset with a `--check` -
because that shape already has its gate wiring, its staleness message and its test form in this
repository, and copying it means a reader of one understands the other.

## Modes

| invocation | does | exits |
|---|---|---|
| `make record` | assembles every committed record page from its fragments and writes the ones that differ | 0, or 1 on any refusal in [fragment-format.md](fragment-format.md) |
| `make record CHECK=1` | writes nothing; reports every page whose committed bytes differ from its assembly | 0 in sync, 1 stale or refused |
| `make record PAGE=<name>` | the same, over one page (`ways`, `cities/defenses`, `sources`) | as above |
| `make record SPLIT=<name>` | the one-time split: takes a page that is still whole and writes its fragments, then asserts the assembly of them is byte-identical and refuses to leave the split behind if it is not | 0, or 1 with the first differing byte's offset and its line |

`make record` runs after `make citations` where both are run, because `_citations-works.html` is an input
to the assembly and an output of the citations derivation. The Makefile states that order rather than
leaving it to the caller.

## Messages

Stale, the common case - the message names what to run, as every guard in this repository does:

```
record: STALE - run `make record`:
  research/water.html
  research/citations/water.html
```

In sync:

```
record: in sync (19 pages, 1 registry, 1,850 notes)
```

A refusal names the file and the thing, never a count alone:

```
record: research/water/040-what-does-a-weir-look-like.html references `mineta-2007-tameike-4`,
        which no note in research/water/040-what-does-a-weir-look-like.notes.html defines
```

## Where it is enforced

- **the gate**: `tests/interactive/test_record_assembly.py` fails while any committed page differs from
  its assembly. This is how a change that touches engine code is caught.
- **the push**: `scripts/sync-with-main.sh` runs `make record CHECK=1` before either route. This is how a
  record-only change is caught, which the gate cannot do - a record-only delta takes the DIRECT route and
  the gate never runs.

Both, deliberately, for the reason `entry-gate.sh` is also in both places: the two routes catch different
work, and a check in only one of them is a check with a hole in it exactly where this feature's own
commits land.

## What does not change

`make citations` keeps its name, its `CHECK=1` and its job. `make record-prepass`, `make quote-verbatim`
and `make page-check` keep their names and grow a way to name one question (FR-023). No existing target
is renamed or retired.
