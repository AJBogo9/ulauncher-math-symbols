# Math Symbols

A [Ulauncher](https://ulauncher.io) 6 extension that searches math symbols and copies them to the clipboard. Type `m sum`, press Enter, and ∑ is on the clipboard.

It needs Ulauncher 6 (extension API v3) and does not run on Ulauncher 5.

## Usage

Type the keyword `m`, a space, then a query. Each result shows the symbol, its LaTeX command, its Unicode name and its code point.

| Query | First result |
| --- | --- |
| `m sum`, `m \sum` | ∑ |
| `m mathbb R`, `m \mathbb{R}`, `m reals` | ℝ |
| `m sigma`, `m Sigma` | σ, Σ |
| `m le`, `m subseteq`, `m implies` | ≤, ⊆, ⟹ |
| `m expectation`, `m indicator`, `m norm` | 𝔼, 𝟙, ‖ |
| `m not equal` | ≠ |
| `m ^2`, `m _t` | ², ₜ |
| `m U+2211`, `m 0x2211`, `m 2211` | ∑ |
| `m ∑` (pasted) | ∑, with its name |

Enter copies the symbol. Alt+Enter lists the actions: copy the symbol, its LaTeX command, or its code point.

### Match order

1. A code point, or a pasted symbol.
2. A LaTeX command, exactly. A match in the same case comes first, so `sigma` gives σ and `Sigma` gives Σ.
3. The start of a LaTeX command: `subs` finds `\subset` and `\subseteq`.
4. A nickname, for symbols with a hard-to-guess Unicode name: `reals`, `expectation`, `indicator`, `gradient`, `norm`, `qed`, `hadamard`, `distributed as` (the full list is `NICKNAMES` in `symbols.py`).
5. Words of the Unicode name, each query word the start of a name word: `double struck r`, `not equal`.

LaTeX names ignore backslashes, braces and spaces, so `mathbb R`, `\mathbb{R}` and `mathbbR` are the same query. Styled letters from the Mathematical Alphanumeric block (𝕣, 𝐱) come after other matches of the same kind.

The LaTeX names follow what LaTeX draws: `\epsilon` is ϵ and `\varepsilon` is ε, `\phi` is ϕ and `\varphi` is φ, and `\implies` is ⟹ (⇒ is `\Rightarrow`). As in standard LaTeX, `\mathbb` and `\mathcal` cover capitals only, plus digits for `\mathbb`; 𝕣 is found by its name.

### Preferences

- Keyword: `m`
- Max results: 10

## Development

Tests run on the system Python. Ulauncher starts extensions with it, and the Unicode names come from its `unicodedata` (Unicode 15.0 on Python 3.12). `tests/test_main.py` builds the extension against the installed Ulauncher package, so the venv sees system site-packages.

```sh
uv venv --system-site-packages --python /usr/bin/python3
uv pip install pytest
.venv/bin/pytest
```

Print results in the terminal (quote anything with a backslash):

```sh
python3 scripts/try.py mathbb R
python3 scripts/try.py '\subseteq'
```

Link the repo into Ulauncher's extensions folder, then restart Ulauncher so it starts the extension:

```sh
scripts/dev-install.sh
pkill -f '[p]ython3 -m ulauncher'
while pgrep -f '[p]ython3 -m ulauncher' > /dev/null; do sleep 0.1; done
ulauncher start -v
```

Ulauncher starts extensions when it starts, so restart it after each change. In Ulauncher 6:

- `pkill ulauncher` matches only the `/bin/sh` wrapper, while the app runs as `python3 -m ulauncher`. That stops the systemd service, whose cleanup takes the app down too, but a copy started from a terminal keeps running.
- `ulauncher -v` means `ulauncher show -v` and only shows the window. `ulauncher start -v` starts the app with debug logs in the terminal.

To go back to the background service, stop the terminal copy the same way and run `systemctl --user start ulauncher`.

## License

MIT
