import socket

import pytest

pytest.importorskip("ulauncher.api")
from ulauncher.api import effects


@pytest.fixture
def ext(monkeypatch):
    # Extension() needs the env ulauncher passes to the extension process
    ours, theirs = socket.socketpair()
    monkeypatch.setenv("ULAUNCHER_EXTENSION_ID", "math-symbols")
    monkeypatch.setenv("SOCKETPAIR_FD", str(theirs.fileno()))
    monkeypatch.setenv("EXTENSION_PREFERENCES", '{"math": "m", "max_results": 3}')
    from main import MathSymbols

    yield MathSymbols()
    ours.close()
    theirs.close()


def test_results(ext):
    results = ext.on_input("sum", "math")
    assert len(results) == 3
    top = results[0]
    assert top.name == r"∑    \sum"
    assert top.description == "N-Ary Summation · U+2211"
    assert [a["name"] for a in top.actions.values()] == [
        "Copy ∑",
        r"Copy \sum",
        "Copy U+2211",
    ]


@pytest.mark.parametrize(
    ("action", "text"), [("char", "∑"), ("latex", r"\sum"), ("codepoint", "U+2211")]
)
def test_activation_copies(ext, action, text):
    copied = []
    ext.clipboard_store = copied.append
    effect = ext.on_result_activation(action, ext.on_input("sum", "math")[0])
    assert copied == [text]
    assert effect == effects.close_window()


def test_symbol_without_latex_has_no_latex_action(ext):
    top = ext.on_input("U+1F600", "math")[0]
    assert top.name == "😀"
    assert list(top.actions) == ["char", "codepoint"]


def test_hint_and_no_match_have_no_actions(ext):
    (hint,) = ext.on_input("", "math")
    (no_match,) = ext.on_input("qwertyzzz", "math")
    assert hint.actions == {}
    assert no_match.actions == {}
    assert "qwertyzzz" in no_match.name
