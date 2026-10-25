"""`record/money.py` - the conversion of a marked amount of money, shown on hover (feature 413, diagram#14).

WHAT THESE PROVE. The issue's worked example (20 mon at Kyoto 1745-54 = about $4.07 in goods, $41.71 in wages, 4.2 sen);
the Rokugani format matches gm-assistant's `conversions.rokugani()`; a range converts both ends; an era is inherited from an
enclosing element, also across the record's unclosed blocks; a borrowed era says so, and no distance in years is refused (the GM, #14); every bad
mark is refused, naming the amount; an awaiting era and an unmarked amount pass untouched (the glossary tooltip alone); the
site build carries the box text and gathers the refusals.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from l7r.diagram.interactive.record import money

#: The two units of gm-assistant's kyoto-1745 row the tests use (conversions.json, snapshot 2026-10).
KYOTO = {
    "place": "Kyoto",
    "years": "1745-1754",
    "confidence": "Salt, fuel and housing are guesses.",
    "basket_coverage": "the whole basket",
    "goods_left_out": [],
    "units": {
        "mon": {"silver_g": 0.04712, "goods_dollars": 0.203442, "wage_dollars": 2.085311, "rokugan_sen": 0.208719},
        "ryo": {"silver_g": 186.6, "goods_dollars": 805.649085, "wage_dollars": 8258.042553, "rokugan_sen": 826.550336},
    },
}
TOKYO = {
    "place": "Tokyo",
    "years": "1882-1886",
    "basket_coverage": "9 of 12 goods",
    "goods_left_out": ["Salt", "Fuel", "Housing"],
    "units": {"yen": {"silver_g": 25.0, "goods_dollars": 73.9, "wage_dollars": 693.3, "rokugan_sen": 130.5}},
}
TABLE = money.Table({"kyoto-1745": KYOTO, "tokyo-1882": TOKYO}, {"beijing-1736": {"place": "Beijing", "years": "1736-1760"}})


def _span(amount: str, coin: str, text: str, extra: str = "") -> str:
    return f'<span class="money" data-amount="{amount}" data-coin="{coin}"{extra}>{text}</span>'


def test_the_issues_worked_example() -> None:
    out, errors = money.annotate(f'<p data-era="kyoto-1745">It cost {_span("20", "mon", "20 mon")}.</p>', "q", TABLE)
    assert errors == []
    assert "20 mon: about $4.07 in goods, $41.71 in wages, 4.2 sen in Rokugan" in out
    assert "Kyoto 1745-1754: the whole basket" in out and "Salt, fuel and housing are guesses." in out
    assert "at Kyoto" not in out  # its own era: no borrowed line


@pytest.mark.parametrize(("sen", "said"), [(0.5, "0.5 sen"), (9.94, "9.9 sen"), (42, "4 zeni 2 sen"), (137, "about 1 bu 4 zeni"), (1234, "about 1 koku 2 bu"), (1200, "1 koku 2 bu"), (0, "0.0 sen")])
def test_rokugani_matches_gm_assistants_format(sen: float, said: str) -> None:
    assert money.rokugani(sen) == said


def test_fmt_of_nothing_and_dollars() -> None:
    assert money.fmt(0) == "0 sen"
    assert [money.dollars(x) for x in (4.0688, 41.706, 805.6, 12345.0)] == ["$4.07", "$41.71", "$806", "$12,300"]
    assert [money.dollars(x, 54321.0) for x in (5432.1, 54321.0)] == ["$5,400", "$54,300"]


def test_a_range_converts_both_ends_and_the_coverage_names_what_is_left_out() -> None:
    out, errors = money.annotate(f'<li data-era="tokyo-1882">{_span("1-2", "yen", "1-2 yen")}</li>', "q", TABLE)
    assert errors == []
    assert "1-2 yen: about $74-$148 in goods, $693-$1,387 in wages, 1 bu 3 zeni to about 2 bu 6 zeni in Rokugan" in out
    assert "Tokyo 1882-1886: 9 of 12 goods; leaves out salt, fuel, housing" in out


def test_the_era_is_inherited_across_unclosed_blocks() -> None:
    markup = f'<ul data-era="kyoto-1745"><li>a {_span("1", "ryo", "1 ryo")}<li>b {_span("2", "ryo", "2 ryo")}</ul><p>{_span("3", "ryo", "3 ryo")}</p>'
    out, errors = money.annotate(markup, "q", TABLE)
    assert out.count("data-def=") == 2
    assert errors == ["q: the amount '3 ryo' names no era - put data-era=\"<era id>\" on it or on an element around it (feature 413)"]


def test_a_borrowed_era_says_so_and_no_distance_in_years_is_refused() -> None:
    """The GM withdrew the 25-year rule (#14, 2026-10-24): an era's distance is the author's judgment until #15 measures it."""
    near, errors = money.annotate(_span("20", "mon", "20 mon", ' data-era="kyoto-1745" data-paid="Osaka 1766"'), "q", TABLE)
    assert errors == [] and "at Kyoto 1745-54 prices" in near
    far, errors = money.annotate(_span("20", "mon", "20 mon", ' data-era="kyoto-1745" data-paid="Edo 1804-1830"'), "q", TABLE)
    assert errors == [] and "at Kyoto 1745-54 prices" in far
    _, yearless = money.annotate(_span("20", "mon", "20 mon", ' data-era="kyoto-1745" data-paid="Osaka"'), "q", TABLE)
    assert len(yearless) == 1 and "with no year" in yearless[0]


@pytest.mark.parametrize(
    ("mark", "says"),
    [
        (_span("20", "mon", "20 mon", ' data-era="kyoto-1754"'), "which the conversion table does not have"),
        (_span("20", "wen", "20 wen", ' data-era="kyoto-1745"'), "names coin 'wen'"),
        (_span("about 20", "mon", "about 20 mon", ' data-era="kyoto-1745"'), "a number, or two joined by a hyphen"),
        (_span("20", "mon", "20 mon"), "names no era"),
    ],
)
def test_each_bad_mark_is_refused_naming_the_amount(mark: str, says: str) -> None:
    out, errors = money.annotate(mark, "research/questions/0001-x.html", TABLE)
    assert len(errors) == 1 and says in errors[0] and errors[0].startswith("research/questions/0001-x.html: the amount")
    assert "data-def" not in out


def test_an_awaiting_era_and_unmarked_markup_pass_untouched() -> None:
    awaiting = _span("800", "wen", "800 cash", ' data-era="beijing-1736"')
    assert money.annotate(awaiting, "q", TABLE) == (awaiting, [])
    plain = "<p>20 mon, <br>and <img src='x'/> more</p>"
    assert money.annotate(plain, "q", TABLE) == (plain, [])
    voids = f'<p data-era="kyoto-1745">a<br>b<img src="x"/> {_span("20", "mon", "20 mon")}</p>'
    assert money.annotate(voids, "q", TABLE)[0].count("data-def=") == 1


def test_years_and_short_years() -> None:
    assert money.years("1745-1754") == (1745, 1754)
    assert money.years("Osaka 1766") == (1766, 1766)
    assert money.years("1804-30") == (1804, 1830)
    assert money.years("Osaka") is None
    assert money.short_years("1745-1754") == "1745-54"
    assert money.short_years("1766") == "1766"
    assert money.short_years("1795-1805") == "1795-1805"


def test_load_reads_the_table_and_a_missing_file_as_empty(tmp_path: pathlib.Path) -> None:
    assert money.load(str(tmp_path)) == money.Table({}, {})
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / money.CONVERSIONS).write_text(json.dumps({"eras": {"kyoto-1745": KYOTO}}), encoding="utf-8")
    (tmp_path / "assets" / money.AWAITING).write_text("[]", encoding="utf-8")
    assert money.load(str(tmp_path)) == money.Table({"kyoto-1745": KYOTO}, {})


def test_the_vendored_table_converts_the_worked_example() -> None:
    """The real copy (`make money-conversions`): 20 mon at kyoto-1745 in gm-assistant's feature 223 table (diagram#17
    issuecomment-6398335706: goods now the spending-weighted geometric mean, $1.54 where the arithmetic gave $3.32)."""
    table = money.load(str(pathlib.Path(__file__).resolve().parents[2] / "research"))
    out, errors = money.annotate(_span("20", "mon", "20 mon", ' data-era="kyoto-1745"'), "q", table)
    assert errors == [] and "about $1.54 in goods, $37.92 in wages, 3.8 sen in Rokugan" in out


def test_the_site_build_writes_the_box_and_gathers_every_refusal(tmp_path: pathlib.Path) -> None:
    from l7r.diagram.interactive.record import site  # noqa: PLC0415 - the build loads the whole record machinery
    from l7r.diagram.interactive.record.store import RecordError  # noqa: PLC0415
    from tests import _flat_record as fr  # noqa: PLC0415

    rec = fr.write(tmp_path)
    (rec / "assets" / money.CONVERSIONS).write_text(json.dumps({"eras": {"kyoto-1745": KYOTO}}), encoding="utf-8")
    mark = _span("20", "mon", "20 mon", ' data-era="kyoto-1745"')
    fr.edit(rec, "0002-bridges.html", "One span.", f"One span, {mark}.")
    files = site.build(str(rec))
    assert "20 mon: about $4.07 in goods" in files["q/bridges.html"] and "20 mon: about $4.07 in goods" in files["all.html"]
    fr.edit(rec, "0002-bridges.html", "kyoto-1745", "kyoto-1754")
    with pytest.raises(RecordError) as e:
        site.build(str(rec))
    assert str(e.value).count("names era 'kyoto-1754'") == 1, "one refusal per amount, however many pages show it"
