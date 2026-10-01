"""`record/passages.py` - a note quoting several passages, shown as a list (feature 292, GM 2026-09-29: *"anytime we are
citing multiple things from a source instead of one thing, we should display this as a bulleted list within the
footnote"*)."""

from __future__ import annotations

import re

from l7r.diagram.interactive.record.passages import bulleted, bulleted_notes

KEY = '<a href="citations/p.html#work-k" target="_blank" rel="noopener"><code>k</code></a>'


def _view(html: str) -> list[str]:
    """The list as a reader sees it: `*` a passage, `**` one nested under it; separators hidden."""
    html = re.sub(r'<span class="sep">.*?</span>', "", html)
    items = re.findall(r'<span class="(pass(?: sub)?)">(.*?)</span>(?=<span class="pass|</span>)', html, re.S)
    return [("** " if cls == "pass sub" else "* ") + re.sub(r"<[^>]+>", "", text) for cls, text in items]


def _plain(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html)


def test_sibling_passages_are_a_flat_list_and_the_text_is_unchanged() -> None:
    """The GM's second example: four passages joined by `;` - one level."""
    body = f'{KEY} - 「A」 (translated; original: 「甲」); 「B (b)」 (translated; original: 「乙」) ; 「C」 (x)'
    out = bulleted(body)
    assert _view(out) == ["* 「A」 (translated; original: 「甲」)", "* 「B (b)」 (translated; original: 「乙」)", "* 「C」 (x)"]
    assert _plain(out) == _plain(body), "the separators are kept, hidden: the text is unchanged"


def test_a_passage_that_introduces_others_nests_them() -> None:
    """The GM's first example: a passage ending `which the paper glosses:` and the glosses under it."""
    body = f'{KEY} - 「A」 (translated), from a 1750 document, which the paper glosses: 「B」 (translated); 「C」 (translated)'
    assert _view(bulleted(body)) == ["* 「A」 (translated), from a 1750 document, which the paper glosses:", "** 「B」 (translated)", "** 「C」 (translated)"]


def test_a_single_passage_and_a_separator_inside_a_quote_or_a_tag_are_left_alone() -> None:
    one = f"{KEY} - 「The yashikirin: from the south; from the west」 (translated)"
    assert bulleted(one) == one
    assert bulleted('no key link - 「A」; 「B」') == 'no key link - 「A」; 「B」'
    english = f'{KEY} - "one; two" and <a href="x;y">z</a>; not a passage'
    assert bulleted(english) == english
    assert bulleted(f"{KEY} - 「A」 <!-- a; 「B」 --> end") == f"{KEY} - 「A」 <!-- a; 「B」 --> end"
    assert bulleted(f"{KEY} - 「A」 <broken") == f"{KEY} - 「A」 <broken", "an unclosed tag ends the scan"


def test_a_slash_or_another_source_s_key_starts_a_passage_and_trailing_space_stays_outside() -> None:
    body = f'{KEY} - "A." / "B."; <a href="https://x"><code>other</code></a> - 「C」 '
    out = bulleted(body)
    assert _view(out) == ['* "A."', '* "B."', "* other - 「C」"]
    assert out.endswith("</span></span> "), "whitespace ending the note stays outside the list"


def test_every_note_of_a_file_is_listed() -> None:
    notes = f'<li data-note="a">{KEY} - 「A」; 「B」</li>\n<li data-note="b">{KEY} - 「C」</li>\n'
    out = bulleted_notes(notes)
    assert out.count('class="passages"') == 1 and out.endswith(f'<li data-note="b">{KEY} - 「C」</li>\n')


def test_a_collapsed_original_is_never_split() -> None:
    """`original: 「...」` is a colon before a quotation - but inside the collapsed original it introduces nothing: the
    list must never cut into the span the page's toggle hides (found on urban-features by the foreign-quote test)."""
    body = f'{KEY} - "The English above is the author\'s own translation" - <span class="orig">original: 「若造熟鐵」</span>'
    assert bulleted(body) == body
    two = f'{KEY} - 「A」 (translated; <span class="orig">original: 「甲」</span>); 「B」 (translated; <span class="orig">original: 「乙」</span>)'
    assert _view(bulleted(two)) == ["* 「A」 (translated; original: 「甲」)", "* 「B」 (translated; original: 「乙」)"]
    for unclosed in ('<span class="orig">original: 「never closed', "<!-- a comment never closed", "<a tag never closed"):
        body = f"{KEY} - 「A」; 「B」 {unclosed}; 「C」"
        out = bulleted(body)  # returns at all: an unclosed unit ends the scan instead of sending it backwards
        unlisted = re.sub(r'<span class="(?:pass(?: sub)?|passages|sep)">', "", out).replace("</span>", "")
        assert unlisted == body.replace("</span>", "") and _view(out)[0] == "* 「A」", out
