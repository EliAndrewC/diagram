# Quickstart: working on the record after this lands

The rule in one line: **edit the fragment, run `make record`, never open the assembled page.**

## Find the entry

| you want | do this |
|---|---|
| a source by its key | `ls research/sources/*/*fei-1939*` |
| a question, by something it says | `grep -rl "dike-pond" research/water/` |
| a question, by its heading | `ls research/water/ \| grep -i weir` |
| the notes for a question | the `.notes.html` file beside it, same prefix and slug |
| what a page's questions are, in order | `ls research/water/` |

There is no index to consult and none to keep in step. Do not `ls research/sources/` bare - it is 920
entries; glob for the key you want.

## Change something

1. Edit the fragment. It is 1-6 KB; read it whole.
2. `make record` - the assembled pages are rewritten.
3. `make quick` if anything else moved; the gate and the push both refuse a stale page.

An `Edit` aimed at an assembled page does not silently land: the guard rewrites it to the one fragment
that holds the text, or refuses and names the candidates.

## Add a question

1. Pick a free prefix between its neighbors - they count by ten, so there are nine.
2. `research/<page>/NNN-<slug>.html`, beginning with its `<h2 id="...">`. The id is the record's anchor,
   so choose it as carefully as you would a heading today.
3. Notes, if it has any, go in `research/<page>/NNN-<slug>.notes.html`.
4. `make record`.

## Add a footnote

No number anywhere. In the prose:

```html
...the pond is dug and the dike raised from its spoil.<sup class="fn" data-note="gmrb-2024-sangji"></sup>
```

In the `.notes.html` beside it:

```html
<li data-note="gmrb-2024-sangji"><a href="https://epaper.gmw.cn/..."><code>gmrb-2024-sangji</code></a> - 「...」 (the gloss)</li>
```

`make record` allocates the numbers in document order and writes the reference, the note, the back link
and the hover script. A key is unique within its page; where a page cites one work several times, the
keys are `gmrb-2024-sangji`, `gmrb-2024-sangji-2`, and so on.

## Check one entry

The whole point of the split: a check reads the entry, not the page.

```
make record-prepass PAGE=water SECTION=040-what-does-a-weir-look-like
make quote-verbatim PAGE=water SECTION=040-what-does-a-weir-look-like
```

Then dispatch `record-format` or `quote-check` with the fragment paths the prepass printed. The agents'
contracts tell them to read the fragment they are given and not the assembled page; that instruction is
in the contracts and not in a `CLAUDE.md`, because since feature 256 a defined agent never sees one.

## A source

`research/sources/010-works-cited/NNNN-<key>.html` holds one registry entry: its heading, its citation
line, and the two write-ups (what it is; why it applies, and its limits). Adding a source is a new file
with a free prefix at the end; `source-applicability` then reads that one file.
