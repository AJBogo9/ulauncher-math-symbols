from __future__ import annotations

from ulauncher.api import Extension, Result, effects

from symbols import Symbol, search

DEFAULT_MAX_RESULTS = 10


class SymbolResult(Result):
    # action ids double as the keys holding the text to copy
    char: str = ""
    latex: str = ""
    codepoint: str = ""


def _result(symbol: Symbol) -> SymbolResult:
    copies = {"char": symbol.char, "latex": symbol.latex, "codepoint": symbol.codepoint}
    return SymbolResult(
        name=f"{symbol.char}    {symbol.latex}".rstrip(),
        description=f"{symbol.name} · {symbol.codepoint}",
        # enter runs the first action
        actions={key: {"name": f"Copy {text}"} for key, text in copies.items() if text},
        char=symbol.char,
        latex=symbol.latex,
        codepoint=symbol.codepoint,
    )


class MathSymbols(Extension):
    def on_input(self, query: str, _trigger_id: str) -> list[Result]:
        query = (query or "").strip()
        if not query:
            hint = r"A LaTeX name (\sum, mathbb R), a word (reals, gradient) or a code point (U+2211)"
            return [Result(name="Search math symbols", description=hint)]
        symbols = search(query, limit=self._max_results())
        if not symbols:
            hint = "Try a LaTeX name, a word from the Unicode name, or a code point"
            return [Result(name=f"No symbol matches “{query}”", description=hint)]
        return [_result(s) for s in symbols]

    def on_result_activation(self, action_id: str, result) -> effects.CloseWindow:
        self.clipboard_store(result[action_id])
        return effects.close_window()

    def _max_results(self) -> int:
        try:
            return max(1, int(self.preferences.get("max_results", DEFAULT_MAX_RESULTS)))
        except (TypeError, ValueError):
            return DEFAULT_MAX_RESULTS


if __name__ == "__main__":
    MathSymbols().run()
