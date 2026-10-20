"""Math symbol table and search. Stdlib only, so it is testable without Ulauncher."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

# code point ranges in the table, on top of every char named in LATEX and NICKNAMES
BLOCKS = [
    (0x0391, 0x03C9),  # greek letters
    (0x03D0, 0x03F6),  # greek variants (ϑ ϕ ϖ ϵ)
    (0x2100, 0x214F),  # letterlike symbols
    (0x2190, 0x21FF),  # arrows
    (0x2200, 0x22FF),  # mathematical operators
    (0x2308, 0x230B),  # ceiling and floor
    (0x27C0, 0x27EF),  # misc mathematical symbols-a
    (0x27F0, 0x27FF),  # long arrows
    (0x2980, 0x29FF),  # misc mathematical symbols-b
    (0x2A00, 0x2AFF),  # supplemental mathematical operators
    (0x1D400, 0x1D7FF),  # mathematical alphanumeric symbols
]

# char, then its latex commands; the first one is primary
LATEX = r"""
α \alpha  β \beta  γ \gamma  δ \delta  ϵ \epsilon  ε \varepsilon  ζ \zeta  η \eta
θ \theta  ϑ \vartheta  ι \iota  κ \kappa  ϰ \varkappa  λ \lambda  μ \mu  ν \nu
ξ \xi  π \pi  ϖ \varpi  ρ \rho  ϱ \varrho  σ \sigma  ς \varsigma  τ \tau
υ \upsilon  ϕ \phi  φ \varphi  χ \chi  ψ \psi  ω \omega  ϝ \digamma
Γ \Gamma  Δ \Delta  Θ \Theta  Λ \Lambda  Ξ \Xi  Π \Pi  Σ \Sigma  Υ \Upsilon
Φ \Phi  Ψ \Psi  Ω \Omega

ℏ \hbar  ℓ \ell  ℘ \wp  ℜ \Re  ℑ \Im  ℵ \aleph  ℶ \beth  ℷ \gimel  ℸ \daleth
℧ \mho  Ⅎ \Finv  ⅁ \Game

∀ \forall  ∃ \exists  ∄ \nexists  ¬ \neg \lnot  ∧ \wedge \land  ∨ \vee \lor
⊻ \veebar  ⊼ \barwedge  ⊤ \top  ⊥ \bot  ⊢ \vdash  ⊣ \dashv  ⊨ \vDash  ⊧ \models
⊩ \Vdash  ⊪ \Vvdash  ⊬ \nvdash  ⊭ \nvDash  ∴ \therefore  ∵ \because

∈ \in  ∉ \notin  ∋ \ni  ∅ \emptyset \varnothing  ∁ \complement
⊂ \subset  ⊃ \supset  ⊆ \subseteq  ⊇ \supseteq  ⊈ \nsubseteq  ⊉ \nsupseteq
⊊ \subsetneq  ⊋ \supsetneq  ⋐ \Subset  ⋑ \Supset  ⊏ \sqsubset  ⊐ \sqsupset
⊑ \sqsubseteq  ⊒ \sqsupseteq  ∩ \cap  ∪ \cup  ⋒ \Cap  ⋓ \Cup  ⊓ \sqcap  ⊔ \sqcup
⊎ \uplus  ∖ \setminus

≠ \neq \ne  ≡ \equiv  ≈ \approx  ≊ \approxeq  ∼ \sim  ≃ \simeq  ≅ \cong  ≇ \ncong
≁ \nsim  ∽ \backsim  ⋍ \backsimeq  ≍ \asymp  ≐ \doteq  ≑ \doteqdot
≒ \fallingdotseq  ≓ \risingdotseq  ≔ \coloneqq  ≕ \eqqcolon  ≖ \eqcirc  ≗ \circeq
≜ \triangleq  ≎ \Bumpeq  ≏ \bumpeq  ∝ \propto  ≬ \between  ⋔ \pitchfork

≤ \leq \le  ≥ \geq \ge  ≦ \leqq  ≧ \geqq  ⩽ \leqslant  ⩾ \geqslant  ≨ \lneqq  ≩ \gneqq
≪ \ll  ≫ \gg  ⋘ \lll  ⋙ \ggg  ≮ \nless  ≯ \ngtr  ≰ \nleq  ≱ \ngeq
≲ \lesssim  ≳ \gtrsim  ⪅ \lessapprox  ⪆ \gtrapprox  ≶ \lessgtr  ≷ \gtrless
⋚ \lesseqgtr  ⋛ \gtreqless  ⋖ \lessdot  ⋗ \gtrdot  ⋦ \lnsim  ⋧ \gnsim
≺ \prec  ≻ \succ  ≼ \preccurlyeq  ≽ \succcurlyeq  ⪯ \preceq  ⪰ \succeq
≾ \precsim  ≿ \succsim  ⊀ \nprec  ⊁ \nsucc  ⋨ \precnsim  ⋩ \succnsim
∣ \mid  ∤ \nmid  ∥ \parallel  ∦ \nparallel  ⟂ \perp
⊲ \lhd \vartriangleleft  ⊳ \rhd \vartriangleright  ⊴ \unlhd \trianglelefteq
⊵ \unrhd \trianglerighteq  ⋪ \ntriangleleft  ⋫ \ntriangleright
⋬ \ntrianglelefteq  ⋭ \ntrianglerighteq

± \pm  ∓ \mp  × \times  ÷ \div  ⋅ \cdot  ∗ \ast  ⋆ \star  ∘ \circ  ∙ \bullet
∔ \dotplus  ⊕ \oplus  ⊖ \ominus  ⊗ \otimes  ⊘ \oslash  ⊙ \odot  ⊚ \circledcirc
⊛ \circledast  ⊝ \circleddash  ⊞ \boxplus  ⊟ \boxminus  ⊠ \boxtimes  ⊡ \boxdot
⋄ \diamond  ≀ \wr  ⨿ \amalg  ⋉ \ltimes  ⋊ \rtimes  ⋋ \leftthreetimes
⋌ \rightthreetimes  ⋇ \divideontimes  ⋈ \bowtie  ⋎ \curlyvee  ⋏ \curlywedge
⊺ \intercal  ⊸ \multimap  √ \sqrt \surd

∑ \sum  ∏ \prod  ∐ \coprod  ∫ \int  ∬ \iint  ∭ \iiint  ⨌ \iiiint  ∮ \oint
⋀ \bigwedge  ⋁ \bigvee  ⋂ \bigcap  ⋃ \bigcup  ⨁ \bigoplus  ⨂ \bigotimes
⨀ \bigodot  ⨄ \biguplus  ⨆ \bigsqcup

∂ \partial  ∇ \nabla  ∞ \infty  ∠ \angle  ∡ \measuredangle  ∢ \sphericalangle
′ \prime  † \dagger  ‡ \ddagger  ° \degree  … \ldots \dots  ⋯ \cdots  ⋮ \vdots  ⋱ \ddots

⟨ \langle  ⟩ \rangle  ⌈ \lceil  ⌉ \rceil  ⌊ \lfloor  ⌋ \rfloor
⟦ \llbracket  ⟧ \rrbracket  ‖ \| \Vert \lVert \rVert

← \leftarrow \gets  → \to \rightarrow  ↑ \uparrow  ↓ \downarrow  ↔ \leftrightarrow
↕ \updownarrow  ↖ \nwarrow  ↗ \nearrow  ↘ \searrow  ↙ \swarrow
↚ \nleftarrow  ↛ \nrightarrow  ↮ \nleftrightarrow  ↦ \mapsto
↩ \hookleftarrow  ↪ \hookrightarrow  ↞ \twoheadleftarrow  ↠ \twoheadrightarrow
↢ \leftarrowtail  ↣ \rightarrowtail  ↫ \looparrowleft  ↬ \looparrowright
↭ \leftrightsquigarrow  ⇝ \rightsquigarrow \leadsto  ↰ \Lsh  ↱ \Rsh
↶ \curvearrowleft  ↷ \curvearrowright  ↺ \circlearrowleft  ↻ \circlearrowright
↼ \leftharpoonup  ↽ \leftharpoondown  ⇀ \rightharpoonup  ⇁ \rightharpoondown
↿ \upharpoonleft  ↾ \upharpoonright  ⇃ \downharpoonleft  ⇂ \downharpoonright
⇋ \leftrightharpoons  ⇌ \rightleftharpoons  ⇄ \rightleftarrows  ⇆ \leftrightarrows
⇇ \leftleftarrows  ⇉ \rightrightarrows  ⇈ \upuparrows  ⇊ \downdownarrows
⇐ \Leftarrow  ⇒ \Rightarrow  ⇑ \Uparrow  ⇓ \Downarrow  ⇔ \Leftrightarrow
⇕ \Updownarrow  ⇍ \nLeftarrow  ⇏ \nRightarrow  ⇎ \nLeftrightarrow
⇚ \Lleftarrow  ⇛ \Rrightarrow
⟵ \longleftarrow  ⟶ \longrightarrow  ⟷ \longleftrightarrow  ⟼ \longmapsto
⟸ \impliedby \Longleftarrow  ⟹ \implies \Longrightarrow  ⟺ \iff \Longleftrightarrow
"""

# latex-style aliases: ² is ^2, ₜ is _t
SUPERSCRIPTS = dict(zip("0123456789+-=()inT", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁱⁿᵀ"))
SUBSCRIPTS = dict(
    zip("0123456789+-=()aehijklmnoprstuvx", "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ")
)

# names for things whose unicode name is unguessable
NICKNAMES = """
ℝ reals, real numbers
ℕ naturals, natural numbers
ℤ integers
ℚ rationals, rational numbers
ℂ complex numbers
ℙ probability, primes
𝔼 expectation, expected value
𝟙 indicator, indicator function
ℒ loss, lagrangian, laplace transform
𝒩 normal distribution, gaussian
𝒪 big o
∇ gradient, del
∆ laplacian, difference
∂ partial derivative
‖ norm
∎ qed, tombstone
⊙ hadamard product, elementwise product
⊗ kronecker product, tensor product, outer product
⊕ direct sum, xor
∗ convolution
∘ composition
∼ distributed as, sampled from, similar
≈ approximately
≅ congruent, isomorphic
≡ equivalent, congruent modulo
≔ defined as, assign
≜ defined as, equal by definition
≝ defined as
∣ given, conditional
⫫ independent, independence
⟂ orthogonal
⊤ transpose, true
⊺ transpose
ᵀ transpose
⊥ false, bottom
† adjoint, conjugate transpose
⇒ implies
↦ maps to
¬ negation
∖ set difference
× cross product
⋅ dot product
⟨ inner product, bra
⟩ ket
° degrees
"""

# \mathbb{R} style aliases, generated from unicode names, for the letter kinds standard latex supports
_STYLED = re.compile(
    r"(?:MATHEMATICAL )?(DOUBLE-STRUCK|SCRIPT|FRAKTUR|BLACK-LETTER|BOLD) (CAPITAL|SMALL|DIGIT) (\w+)"
)
_STYLES = {
    "DOUBLE-STRUCK": (r"\mathbb", {"CAPITAL", "DIGIT"}),
    "SCRIPT": (r"\mathcal", {"CAPITAL"}),
    "FRAKTUR": (r"\mathfrak", {"CAPITAL", "SMALL"}),
    "BLACK-LETTER": (r"\mathfrak", {"CAPITAL", "SMALL"}),
    "BOLD": (r"\mathbf", {"CAPITAL", "SMALL", "DIGIT"}),
}
_DIGITS: dict[str, str] = {
    name: str(i)
    for i, name in enumerate(
        ["ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE"]
    )
}

# U+2211, 0x2211, or bare hex of 4 to 6 digits with at least one decimal digit
_CODEPOINT = re.compile(
    r"(?:u\+|0x)([0-9a-f]{1,6})|(?=[a-f]*[0-9])([0-9a-f]{4,6})", re.IGNORECASE
)


@dataclass(frozen=True)
class Symbol:
    char: str
    name: str  # unicode name in title case
    aliases: tuple[str, ...] = ()  # latex, primary first
    nicknames: tuple[str, ...] = ()

    @property
    def latex(self) -> str:
        return self.aliases[0] if self.aliases else ""

    @property
    def codepoint(self) -> str:
        return f"U+{ord(self.char):04X}"


def _normalize(text: str) -> str:
    return re.sub(r"[\\{}\s]", "", text)


def _phrase(text: str) -> str:
    # " " before every word, so `" " + w in phrase` means w is a prefix of a word
    words = re.split(r"[\s\-\\{}]+", text.lower())
    return "".join(" " + w for w in words if w)


def _styled_alias(name: str) -> str | None:
    match = _STYLED.fullmatch(name)
    if not match:
        return None
    style, kind, value = match.groups()
    command, kinds = _STYLES[style]
    if kind not in kinds:
        return None
    if kind == "DIGIT":
        value = _DIGITS[value]
    elif len(value) == 1:
        value = value if kind == "CAPITAL" else value.lower()
    else:
        return None  # bold greek and friends
    return f"{command}{{{value}}}"


def _wanted(name: str) -> bool:
    # skip unassigned code points, coptic, and greek with tonos or dialytika
    return (
        bool(name)
        and not name.startswith("COPTIC")
        and not (name.startswith("GREEK") and " WITH " in name)
    )


def _build() -> list[Symbol]:
    aliases: dict[str, list[str]] = {}
    current: list[str] = []
    for token in LATEX.split():
        if len(token) == 1 and not token.isascii():
            current = aliases.setdefault(token, [])
        else:
            current.append(token)
    for prefix, table in (("^", SUPERSCRIPTS), ("_", SUBSCRIPTS)):
        for key, char in table.items():
            aliases.setdefault(char, []).append(prefix + key)
    nicknames = {
        line[0]: [p.strip() for p in line[1:].split(",")]
        for line in NICKNAMES.strip().splitlines()
    }

    chars = (
        {chr(cp) for lo, hi in BLOCKS for cp in range(lo, hi + 1)}
        | aliases.keys()
        | nicknames.keys()
    )
    chars = sorted(c for c in chars if _wanted(unicodedata.name(c, "")))

    # plane 1 first, so letterlike chars only fill its holes (ℝ, ℒ), and ℘ "script capital p" leaves \mathcal{P} to 𝒫
    styled: dict[str, str] = {}
    for char in sorted(chars, key=lambda c: ord(c) <= 0xFFFF):
        if alias := _styled_alias(unicodedata.name(char)):
            styled.setdefault(alias, char)
    for alias, char in styled.items():
        aliases.setdefault(char, []).append(alias)

    return [
        Symbol(
            c,
            unicodedata.name(c).title(),
            tuple(aliases.get(c, ())),
            tuple(nicknames.get(c, ())),
        )
        for c in chars
    ]


SYMBOLS = _build()
_BY_CHAR = {s.char: s for s in SYMBOLS}
_INDEX = [
    (
        s,
        [_normalize(a) for a in s.aliases],
        [_normalize(a).lower() for a in s.aliases],
        [_phrase(n) for n in s.nicknames],
        _phrase(s.name),
    )
    for s in SYMBOLS
]


def lookup(char: str) -> Symbol | None:
    """The table entry for char, or a bare entry with its unicode name."""
    if char in _BY_CHAR:
        return _BY_CHAR[char]
    name = unicodedata.name(char, "")
    return Symbol(char, name.title()) if name else None


def _direct(query: str) -> Symbol | None:
    # a code point, or a pasted symbol
    if match := _CODEPOINT.fullmatch(query):
        cp = int(match[1] or match[2], 16)
        return lookup(chr(cp)) if cp <= 0x10FFFF else None
    if len(query) == 1 and not query.isascii():
        return lookup(query)
    return None


def _rank(entry, key: str, words: list[str]) -> tuple[int, int] | None:
    _, keys, lower, nicknames, name = entry
    low = key.lower()
    if key in keys:
        return 0, len(key)
    if low in lower:
        return 1, len(key)
    if prefixed := [k for k in keys if k.startswith(key)]:
        return 2, min(map(len, prefixed))
    if prefixed := [k for k in lower if k.startswith(low)]:
        return 3, min(map(len, prefixed))
    if words:
        if matched := [p for p in nicknames if all(" " + w in p for w in words)]:
            return 4, min(map(len, matched))
        if all(" " + w in name for w in words):
            return 5, len(name)
    return None


def search(query: str, limit: int | None = None) -> list[Symbol]:
    """Symbols matching query, best first.

    Order: a code point or pasted symbol; exact latex alias, case-sensitive, then case-insensitive;
    alias prefix, same two steps; every query word a prefix of a nickname word; then of a unicode
    name word. Within a step, plane-1 chars (𝕣) go after the rest, then shorter matches first.
    Backslashes, braces and whitespace are ignored in aliases, so `mathbb R` finds \\mathbb{R}.
    """
    query = query.strip()
    key = _normalize(query)
    if not key:
        return []
    words = _phrase(query).split()
    direct = _direct(query)

    ranked = []
    for entry in _INDEX:
        symbol = entry[0]
        if symbol is not direct and (rank := _rank(entry, key, words)):
            tier, length = rank
            ranked.append(
                ((tier, ord(symbol.char) > 0xFFFF, length, ord(symbol.char)), symbol)
            )
    ranked.sort(key=lambda r: r[0])

    results = ([direct] if direct else []) + [s for _, s in ranked]
    return results[:limit]
