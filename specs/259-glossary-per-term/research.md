# Research: what a membership test actually needs of the glossary

Every figure in `spec.md` points at a finding here, and each re-runs as one command:

    python3 specs/259-glossary-per-term/measure.py R1

All three read the repository and re-run anywhere. Taken 2026-09-20 at `d7cbe8a8` (feature 258's
landing), before any of this feature's work.

## R1 - What the glossary weighs, against what the question needs

**Question.** Feature 258's report said the glossary "cannot be scoped away". Is that true?

**Finding.** It is not, and the claim was wrong by 114,727 bytes.

| | bytes |
|---|---:|
| `interactive/assets/glossary.json`, the hand-edited source | 137,059 (720 terms) |
| `research/assets/glossary.js`, what a check reads today | 144,524 |
| the 720 term NAMES alone | 5,808 |
| names + their variants | 20,981 |
| the definitions | 114,727 |
| a directory listing of one file per term, prefixed | 13,730 |
| ONE term's file | median 154 bytes, smallest 64, largest 398 |

**What it decides.** `record-format` judges VOCABULARY by asking whether a word is already defined.
That question needs every term's NAME and never a definition. The names are 5,808 bytes of the 144,524
the check reads today; a directory listing that carries them - with the ordering prefix R2 forces - is
13,730. A definition is read only when a check wants that term, and costs about 154 bytes.

**The limit of this finding, stated.** 13,730 bytes is the listing's own text. What it costs a check in
practice depends on how the listing reaches it, which FR-010's re-run measures rather than predicts.

## R2 - Term ORDER decides what a reader sees, which is not obvious

**Question.** Can the terms be sorted, so that a filename is just the word?

**Finding. No.** `research/assets/record.js` builds its matcher as `defs[variant] = entry.def` walking
the glossary in FILE ORDER, then sorts the variants by length for matching. So where two terms claim
one variant, the LATER term in the file silently wins - and **7 variants are in that state**:

| variant | claimed by | the page shows | because |
|---|---|---|---|
| `chaoguan` | `chaoguan`, `lijin` | **lijin** | it is later in the file |
| `qiandao` | `qiandao`, `towpath` | **towpath** | it is later in the file |
| `well-sweep` | `jiegao`, `well-sweep` | `well-sweep` | it is later in the file |
| `windlass` | `lulu`, `windlass` | `windlass` | it is later in the file |
| `tsuijibei` | `neribei`, `tsuijibei` | `tsuijibei` | it is later in the file |
| `water mouth` | `shuikou`, `water-mouth` | `water-mouth` | it is later in the file |
| `water-mouth` | `shuikou`, `water-mouth` | `water-mouth` | it is later in the file |

An eighth case is not a clash between terms but a term listing one variant twice: `bettō` carries
`bettō-ji` in its own `variants` array two times over.

**What it decides.** FR-003: the term files carry an ordering prefix, because sorting them would change
which definition a reader is shown for those words, silently, and this feature must change nothing a
reader sees (SC-003). And FR-011: the clashes are resolved so that the order stops being load-bearing
in a place nobody is looking.

**The resolution, and what it changes.** The rule is the obvious one - the term whose own NAME is the
variant keeps it - with one thing stated that the first draft left implicit: names and variants are
compared with case, spaces and hyphens folded. Without that folding the rule does not decide `water
mouth` at all, because the term that owns it is spelled `water-mouth`; the spec review of 2026-09-20
measured that and it is the reason the folding is written down. With it, five of the seven resolve to
the term the page already shows, so nothing moves; **two change what a reader sees**, and both are
corrections:

- hovering `chaoguan` shows the `chaoguan` definition instead of `lijin`'s;
- hovering `qiandao` shows the `qiandao` definition instead of `towpath`'s.

## R3 - The filename hazards

**Question.** Can a term's name BE the filename, as the GM asked?

**Finding.** For 719 of 720, yes, as they stand.

- **One term cannot**: `dS/m` - a slash is a path separator. It is percent-encoded (`dS%2Fm.json`), and
  the file records the term exactly, so nothing is guessed on the way back.
- **Eight carry macrons** (`Hyōjōsho`, `dōba`, `hyō`, `ōkaji`, `ō-aza`, `bettō`, `jingūji`, `shasō`). A
  filename carries these perfectly well, and transliterating them would make a term harder to find, not
  easier - so they stay as they are.
- **No two terms collide** once encoded.

**What it decides.** FR-002: the filename is the term, percent-encoded only where a filename cannot
carry a character, and the file records the term itself so the assembly reads it from the content and
never from the name.
