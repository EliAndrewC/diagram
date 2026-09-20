# Contract: what a fragment must contain, and every refusal

The layout is [data-model.md](../data-model.md). This is what the assembler accepts, what it produces,
and every case in which it refuses rather than guesses.

## The assembly

    assembled page = _front.html
                   + each NNN-<slug>.html in prefix order
                       ( + each NNNN-<key>.html in that section's directory, in prefix order )
                   + _tail.html

Concatenation, byte for byte, with no separator, no re-indentation, no whitespace normalization and no
re-encoding. Whatever a fragment holds is what the page gets. The only bytes the assembler WRITES rather
than copies are footnote numbers and the anchors that carry them (below).

The citations page is the same shape:

    assembled citations page = _citations-front.html
                             + _citations-works.html
                             + "<section class=\"footnotes\"><ol>\n"
                             + each question's notes, in question order, numbered
                             + _citations-tail.html

## What each fragment must contain

| fragment | must | must not |
|---|---|---|
| `_front.html` | begin `<!DOCTYPE html>`; contain exactly one `<h1` | contain any `<h2` |
| `NNN-<slug>.html` | begin with `<h2 id="..."` | contain a second `<h2`; contain `fn-<n>` or `fnref-<n>` |
| `NNN-<slug>.notes.html` | hold only `<li data-note="<key>">...</li>` items | carry a number, an `id="fn-...`, or a `<a class="fnback">` |
| `NNNN-<key>.html` | begin with `<h3 id="..."`; its filename key matches the key its heading registers | contain a second `<h3` |
| `_tail.html` | close every tag the front opened | contain any `<h2` |
| `_citations-works.html` | begin with the DERIVED marker line `make citations` writes | be hand-edited |

## References and notes

In a question fragment, a reference is:

```html
<sup class="fn" data-note="bearing-length"></sup>
```

In the notes fragment beside it, the note is:

```html
<li data-note="bearing-length"><a href="..."><code>ritter-timber-bridges</code></a> - ... </li>
```

The assembler allocates `N` in the order references appear in the assembled research page and writes:

- into the research page: `<sup class="fn"><a id="fnref-N" href="citations/<page>.html#fn-N">N</a></sup>`
  (`../citations/cities/<page>.html` from a `cities/` page - the prefix is computed from the page's own
  depth, never stored);
- into the citations page: `<li id="fn-N">BODY <a class="fnback" href="../<page>.html#fnref-N">back</a></li>`;
- into `citations/<page>.js`: the same note body under the key `fn-N`, exactly as `make citations`
  derives it today.

**A note referenced more than once**: the first reference is `fnref-N`, the second `fnref-N-2`, the third
`fnref-N-3`; the note's back link points at `fnref-N`. Every reference on a page therefore carries a
document-unique id, which fixes the 4 references that carry no id and the 2 pages that carry a duplicated
one (R4, R5).

## Refusals

The assembly refuses - it never picks one of two possibilities, and never drops something it does not
recognize. Every message names the file.

| case | message names |
|---|---|
| two fragments claim the same prefix | both paths, and the prefix |
| a file in a page directory matches no known name | the path, and the four names that are legal there |
| a reference names a key no note defines | the key, the question fragment, the page |
| a note no reference names | the key, the notes fragment |
| a key defined twice on one page | the key and both notes fragments |
| a key that is not lower-case kebab | the key and its file |
| a fragment holds a hand-typed `fn-<n>`, `fnref-<n>` or `class="fnback"` | the file and the offending text |
| a question fragment holds a second `<h2` | the file and the second heading |
| a registry entry's filename key differs from the key its heading registers | the file, both keys |
| `_front.html` or `_tail.html` missing | the page directory, and what is missing |
| a prefix gap is exhausted (no free number between two neighbors) | the two neighbors, and the re-spacing command |
| the committed page differs from the assembly (`CHECK=1`) | every such page, and `make record` |

A refusal exits non-zero and writes nothing. A page whose fragments are refused is left exactly as it is
on disk: the assembly is all-or-nothing per page.

## The invariant the tests hold

For every page in the record:

    assemble(split(committed_page)) == committed_page

at stages 1 and 2 byte for byte, and at stage 3 up to footnote numbers - where "up to footnote numbers"
is itself checked, not asserted: the test strips `fn-<n>`, `fnref-<n>` and the visible number from both
sides and requires equality, and separately requires that the multiset of (question, note body) pairs is
unchanged across the renumbering.
