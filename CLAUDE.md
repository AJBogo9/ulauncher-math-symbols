# Math Symbols (Ulauncher 6 extension)

Searches math symbols in Ulauncher (keyword `m`) and copies them. Usage and the dev workflow are in README.md.

## Layout

- `symbols.py`: symbol table and search. Stdlib only, no Ulauncher import.
  - `BLOCKS`: code point ranges in the table. `LATEX`: a `char \alias ...` text table, first alias is primary. `SUPERSCRIPTS`, `SUBSCRIPTS`: `^2`, `_t` aliases. `NICKNAMES`: one char per line, comma-separated phrases. Every char named in these tables joins the table.
  - `\mathbb`, `\mathcal`, `\mathfrak`, `\mathbf` aliases are generated from Unicode names, only for the letter kinds standard LaTeX has. Plane 1 claims an alias first, so Letterlike chars (ℝ ℒ ℜ) only fill its holes, and ℘ ("SCRIPT CAPITAL P") leaves `\mathcal{P}` to 𝒫.
  - The `search()` docstring lists the ranking tiers.
- `main.py`: the extension. `SymbolResult` declares `char`, `latex`, `codepoint`; the action ids are those keys, so activation copies `result[action_id]`.
- `manifest.json`: trigger `math` (keyword `m`), number preference `max_results`.
- `tests/test_search.py`: top results, and every alias resolving to its own symbol, which catches duplicate aliases. `tests/test_main.py`: builds `MathSymbols` against the installed Ulauncher, with a socketpair for `SOCKETPAIR_FD`.
- `scripts/try.py`; `scripts/dev-install.sh` symlinks the repo to `~/.local/share/ulauncher/extensions/math-symbols` (the dir name is the extension id).

## Commands

- Tests: `.venv/bin/pytest`, in a venv on /usr/bin/python3 with system site-packages (README).
- Restart Ulauncher with logs: README, Development.
- `ulauncher show "m sum"` types a query into the running app over D-Bus. Under `start -v` the log then shows the request to `math-symbols` and `Render N results`. `gapplication action io.ulauncher.Ulauncher hide-window` closes the window.

## Ulauncher 6 API, checked in 6.0.0~beta35

Source: /usr/lib/python3/dist-packages/ulauncher. It is a beta, so recheck there before trusting notes online, most of which use the v2 API.

- `from ulauncher.api import Extension, Result, effects`. Override `on_input(query, trigger_id)` and return a list of `Result`; a generator streams (`yield result` appends, `yield [results]` replaces). `api/extension.py`
- `query` is the text after the keyword. `internals/query.py` says it is None when nothing follows the keyword; `main.py` treats None as empty.
- `Result` is a dict (`data/base_data_class.py`). Undeclared kwargs become keys and travel to the app and back, as long as they do not shadow a class member (`get`, `copy`, `keys`).
- The extension caches the Results it sent for the current request, and `on_result_activation(action_id, result)` receives that same object (`_assign_result_ids` in `api/extension.py`).
- Enter runs the first key of `actions`; Alt+Enter or right click lists them. A result without actions does nothing on Enter, so it works as a hint row. `core.py`, `activate_result`
- Copy with `self.clipboard_store(text)`, then return `effects.close_window()`.
- Names render as plain text, not Pango markup, unless the result is `highlightable` or `searchable`; descriptions go through `html.unescape`. `ui/result_widget.py`
- `self.preferences[id]` comes from the `EXTENSION_PREFERENCES` env (trigger keywords mixed in) and is updated before `on_preferences_update` runs. Saved values: `~/.config/ulauncher/ext_preferences/math-symbols.json`.
- Manifest: required `api_version`, `authors`, `name`, `icon`, `triggers`, and each trigger needs `name`. Preference types: input, checkbox, number, select, text. A number needs an int `default_value`, and only numbers take `min` and `max`. `modes/extensions/extension_manifest.py`
- Extensions run as `/usr/bin/python3 <realpath>/main.py` with Ulauncher on PYTHONPATH, and `VERBOSE=1` under `start -v`. Symlinked extension dirs are followed. `modes/extensions/extension_service.py`, `extension_finder.py`
- `ulauncher preview <path>` runs an extension from a path inside the running app and tails its log. Not tried here.

## Gotchas

- `ulauncher -v` is `ulauncher show -v`: it shows the window and ignores `-v`. Use `ulauncher start -v`.
- `pkill ulauncher` matches only the `/bin/sh` wrapper. Under the systemd unit, cgroup cleanup stops the app as well, and `Restart=on-failure` leaves it stopped. A copy started from a terminal survives as an orphan and keeps the bus name. Kill `python3 -m ulauncher` and wait for it to exit before `ulauncher start`. Starting while the old app holds the name is untested; GApplication would normally hand off to the old instance.
- In `zsh -c` (the Bash tool), `pgrep -f 'python3 -m ulauncher'` matches its own shell; use `'[p]ython3 -m ulauncher'`. Quote `grep --include='*.py'`.
- Unicode names depend on the Python version, so tests use /usr/bin/python3, the interpreter Ulauncher runs extensions with.
