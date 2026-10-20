import pytest

from symbols import SYMBOLS, search

TOP_RESULTS = [
    ("sum", "∑"),
    (r"\sum", "∑"),
    ("forall", "∀"),
    ("in", "∈"),
    ("subseteq", "⊆"),
    ("mathbb R", "ℝ"),
    (r"\mathbb{R}", "ℝ"),
    ("mathbbR", "ℝ"),
    ("reals", "ℝ"),
    ("expectation", "𝔼"),
    ("mathcal L", "ℒ"),
    ("indicator", "𝟙"),
    ("mathbb 1", "𝟙"),
    ("sigma", "σ"),
    ("Sigma", "Σ"),
    ("le", "≤"),
    ("not equal", "≠"),
    ("implies", "⟹"),
    ("norm", "‖"),
    ("U+2211", "∑"),
    ("0x2211", "∑"),
    ("2211", "∑"),
    ("∑", "∑"),
    ("double struck r", "ℝ"),
]


@pytest.mark.parametrize(("query", "char"), TOP_RESULTS)
def test_top_result(query, char):
    assert search(query)[0].char == char


def test_every_alias_resolves_to_its_own_symbol():
    wrong = [
        (alias, s.char, search(alias)[0].char) for s in SYMBOLS for alias in s.aliases
    ]
    assert [w for w in wrong if w[1] != w[2]] == []


def test_pasted_symbol_outside_the_table_shows_its_name():
    (result,) = search("😀")
    assert result.name == "Grinning Face"
    assert result.codepoint == "U+1F600"


def test_no_results():
    assert search("") == []
    assert search("qwertyzzz") == []
