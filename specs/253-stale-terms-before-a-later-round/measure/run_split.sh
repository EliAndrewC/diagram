#!/bin/bash
# run_split.sh <scratch> <case>... - the fetcher/reader split of source-reader, per recorded case:
# stage 1 a SONNET ad-hoc session fetches full page text to files (no judging); stage 2 the source-reader agent
# (its pinned tier, opus/high) reads the files. Hooks off; both stages' usage kept.
SC=$1; shift; CL="$(command -v claude)"; HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for c in "$@"; do (
  d=$SC/$c; mkdir -p $d/pages
  { printf 'You are a FETCHER. Do not judge any claim. Below is a request that names claims and source pointers. Your whole job: get the FULL TEXT of every source it points to onto disk.\n\nFor each URL: run `python3 %s/fetch_text.py "<url>" "%s/pages/NN-<host>.txt"` (NN = 01, 02, ...). If it is UNFETCHABLE or NOT-CHECKED (a PDF, a refusal), try up to TWO alternates that would carry the same text (a PMC or J-STAGE HTML copy, a repository copy, the archived page at web.archive.org/web/2/<url>, the Wikipedia article a summary was echoing) - use WebSearch to find them - and never retry a host that refused. A pointer that is a title or a key with no URL: WebSearch for it and fetch the best public copy. A multi-chapter manual: fetch each chapter whose title could bear on the claims.\n\nEnd with a MANIFEST table and nothing else: pointer | file (or UNREACHED) | what was tried. \n\n=== THE REQUEST ===\n' "$HERE" "$d"; cat $d/prompt.txt; } > $d/fetch-prompt.txt
  ( cd $d/tree && timeout 1200 "$CL" -p --model sonnet --settings '{"disableAllHooks": true}' --permission-mode bypassPermissions --output-format json < $d/fetch-prompt.txt > $d/fetch.json 2>$d/fetch.err )
  jq -r '.result // "NO RESULT"' $d/fetch.json > $d/manifest.md
  { cat $d/prompt.txt; printf '\n\n=== THE PAGES WERE FETCHED FOR YOU ===\nA fetcher has already put the full visible text of the sources on disk under `%s/pages/`. Its manifest:\n\n' "$d"; cat $d/manifest.md; printf '\n\nREAD those files (several per message) instead of fetching. Fetch yourself ONLY a pointer the manifest marks UNREACHED, or a lead the files point to that the claim needs. Everything else in your contract stands.\n'; } > $d/read-prompt.txt
  ( cd $d/tree && timeout 1500 "$CL" -p --agent source-reader --settings '{"disableAllHooks": true}' --permission-mode bypassPermissions --output-format json < $d/read-prompt.txt > $d/run.json 2>$d/run.err )
  jq -r '.result // "NO RESULT"' $d/run.json > $d/reply.md
  echo "done $c fetch=$(jq -c '{t: .num_turns, in: (.usage.input_tokens+.usage.cache_creation_input_tokens+.usage.cache_read_input_tokens), out: .usage.output_tokens}' $d/fetch.json) read=$(jq -c '{t: .num_turns, in: (.usage.input_tokens+.usage.cache_creation_input_tokens+.usage.cache_read_input_tokens), out: .usage.output_tokens}' $d/run.json) pages=$(ls $d/pages | wc -l)" >> $SC/split.log ) &
done; wait; echo "ALL DONE" >> $SC/split.log
