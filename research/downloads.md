# The archive and the download list

**Load this file when:** a source can be read only by the GM (a download to ask for), the GM's downloads in
`academic-sources/` are to be processed, a cited URL has to be archived, or the GM says "ingest" or "sync".

The rules a session needs on every research turn (archive first, `make download-add`) are one line each in the root
`CLAUDE.md`; this is the workflow behind them. Why: [`../docs/research-doctrine.md`](../docs/research-doctrine.md) and
`specs/309-source-archive/`, `specs/313-download-list/`.

## Look in the archive before the web (feature 309)

The GM, 2026-10-02: *"first check to see if we already have something, rather than going out and trying to find it on
the internet"*. A research pass starts with `make archive-inbox`: the GM's downloads in
`/host-l7r-repo/academic-sources/` are archived, the push confirmed, and the files removed, so whatever is still there is
unprocessed. A NEW download is listed WAITING until the session reads its first page, finds the source it copies
(`research/to-download.md` names what each download was asked for) and gives its keys, `make archive-inbox
MATCH='<file>=<key>'`, or the list entry it answers, `MATCH='<file>=#<id>'` (`NONE='<file>'` for one that copies no
cited source). Then `make archive-find URL=<u> | KEY=<k> | TERMS="a|b"` is asked of every source before searching or
fetching; it names the local copy to read (exit 1: nothing held, go to the web).

## Every cited page is archived

A hedge against *"websites going offline"*: every URL in a registry entry (its comments' too) and every URL a footnote
links has a copy - served bytes, the whole page as MHTML, its text - in the PRIVATE repository
`EliAndrewC/diagram-research` (the host's one working copy: `<mirror>/.specify/source-archive/`), and a row in
`research/archive/<id[:2]>/<id>.json`. `make reserve KIND=registry ... URL=<u>` and `make source-outcome
OUTCOME=cited:<key>` archive their URLs themselves (a page read and not cited is on the ledger, not in the archive); a URL
cited any other way (a footnote's direct link, a URL added to an entry) is archived with `make archive URL=<u>`, and `make
record` refuses a cited URL with no row, naming that command. `make archive-sources REPORT=1` prints the coverage. Never
link or copy the archive anywhere public: much of it is copyrighted.

## A source only the GM can fetch

A page the container cannot fetch is not thereby unreadable - if the GM can open it, anyone can. The GM downloads it to
`/host-l7r-repo/academic-sources/` and `make archive-inbox` moves it into the archive (`gm-copies/<file>`, found with
`make archive-find`). The session reads the archived copy, the footnote links the PUBLIC page and says the copy was read,
and the quote-check runs against the copy; a paywalled text with a public abstract is cited for the abstract's words only;
what a read copy does NOT say is written down where the claim stands, and the rest labeled GUESS.

**Asking for one** (feature 313): append it to the canonical download list `research/to-download.md` with `make
download-add FILE=<draft.md>`, one entry per work headed `### NEW. <the work>`: a link to where the session believes it
lives (`- **[...](https://...)**`), `- Fallback:` with a Google-search link that uniquely finds it, `- **Rests on it:**`
naming the `research/questions/` files, and `- Blocked by:` - BOTH links, always. The command numbers it under a
host-wide lock and appends it at the end; the push refuses an entry lost, moved or inserted (`downloads.py check`).
Never write the GM's copy, `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md` (`download-copy-hooks.sh` refuses it).

## The GM's two words (feature 313)

The GM marks their copy - downloaded, partial, paywalled, not found, found elsewhere - and says:

- **"ingest"**: run `make downloads-ingest`. It records each changed mark in the canonical list, dated, names
  contradictory marks and ids it lacks, holds each text edit of the GM's until `KEEP="<ids>"` or `DROP="<ids>"`, then
  archives the inbox (a saved-as name matches its file). Commit both files it names.
- **"sync"**: `make downloads-sync` writes the canonical list over the copy - refused while the copy holds anything not
  ingested.

**What can be got of a source**: `make access-tags [KEY=<key|download:ID>] [JSON=1]` - open, gm-full, gm-partial,
paywalled, bot-refused, down, gone, never-read, derived from the archive, the registry and the GM's marks; a state nothing
else records is `make access-tags SET=<state> KEY= DATE= REASON=`.
