#!/usr/bin/env python3
"""Print search results in the terminal: python3 scripts/try.py mathbb R"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from symbols import search

results = search(" ".join(sys.argv[1:]), limit=10)
for symbol in results:
    print(f"{symbol.char}    {symbol.latex:<20} {symbol.name} · {symbol.codepoint}")
if not results:
    print("no match")
