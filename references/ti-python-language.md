# TI-Python language reference (TI-84 Evo / Evo-T)

The Python App on the TI-84 Evo runs **TI-Python**, Texas Instruments' build derived from
CircuitPython, which is itself a fork of MicroPython. It is Python 3 syntax with pieces
removed to fit a microcontroller. Assume "MicroPython, not CPython" whenever you are unsure.

Verified against the TI-84 Evo product documentation and the TI-84 Plus CE Python guides,
which share the same Python engine. Items marked **[verify on device]** are behaviours that
are near-certain from the MicroPython lineage but that TI does not document explicitly.

---

## 1. Hardware and environment

| Property | TI-84 Evo | Notes |
|---|---|---|
| CPU | ARM Cortex, 156 MHz | ~3× the TI-84 Plus CE's 48 MHz ez80 |
| User memory | 3.5 MB | Up from 3 MB on the CE |
| Graph area | 319 × 209 px | Borderless, ~50% more than the CE |
| Port | USB-C | Data + charging |
| Languages | Python, TI-BASIC | **No C, no assembly** — TI blocks both |
| Released | 28 April 2026 | |

The **TI-84 Evo-T** is the European variant. Functionally identical for programming purposes;
it adds an exam-mode LED on the top edge that several European examination boards require.
Everything in this skill applies to both.

Python programs are portable between the TI-84 Plus CE Python and the TI-84 Evo. TI-BASIC
programs are **not** — the Evo uses a new `.8xp2` format because the BASIC engine was rewritten.
This is one more reason to write Python.

---

## 2. Modules

### Available on the Evo

| Module | Use |
|---|---|
| `math` | `sqrt`, `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `log`, `log10`, `exp`, `pow`, `floor`, `ceil`, `pi`, `e`, `radians`, `degrees`, `fabs`, `fmod` |
| `random` | `random()`, `randint()`, `choice()`, `seed()` |
| `time` | `sleep()`, `monotonic()` |
| `cmath` | Complex math. **[verify on device]** |
| `ti_system` | Calculator interop — read/write TI lists and variables |
| `ti_plotlib` | On-screen plotting (TI's own, not matplotlib) |
| `ti_hub`, `ti_rover` | TI-Innovator Hub / Rover hardware |

### Not available — these are the usual hallucinations

`numpy`, `pandas`, `matplotlib`, `scipy`, `sympy`, `statistics`, `decimal`, `fractions`,
`datetime`, `os`, `sys.argv`, `json`, `re`, `csv`, `pathlib`, `typing`, `dataclasses`,
`itertools`, `functools`, `collections.OrderedDict`, `argparse`, `logging`, `secrets`,
`tkinter`, `requests`.

**`turtle` was removed on the Evo.** It existed on the TI-84 Plus CE Python, so older tutorials
and forum posts will show it. Do not use it.

There is no filesystem exposed to user Python. `open()` is not usable.

---

## 3. Syntax that does not work

### f-strings — the single most common failure

```python
print(f"Total: {total:.2f}")     # SyntaxError on the calculator
```

TI-Python's parser predates f-strings. Use one of these instead:

```python
print("Total: {:.2f}".format(total))       # preferred
print("Total: " + str(round(total, 2)))    # fine, but drops trailing zeros
```

`str.format()` with format specs (`{:.2f}`, `{:>8}`, `{:d}`) is supported.

### Other gaps

| Feature | Status |
|---|---|
| Walrus `:=` | Avoid. **[verify on device]** |
| `async` / `await` | Not supported |
| Type-annotation *imports* (`from typing import ...`) | Not available; bare annotations parse but add nothing |
| `match` statements | Not supported |
| Nested/`!r`/`=` inside `.format()` | Keep format specs simple |
| Very deep recursion | Small stack; prefer loops |
| Lists of hundreds of elements | Memory fills fast; keep data small |

### Things that do work

`if/elif/else`, `for`, `while`, `break`, `continue`, `def`, default arguments, `try/except`
(including bare `except:`), tuples, lists, dicts, slicing, list comprehensions, `round()`,
`abs()`, `min()`, `max()`, `sum()`, `sorted()`, `len()`, `int()`, `float()`, `str()`,
`enumerate()`, `zip()`, `range()`, string methods, integer `//` and `%`.

`eval()` is present in the MicroPython lineage and is what makes `6*pi` work at a prompt.
**[verify on device]** — if a user reports `NameError: eval`, fall back to `float(input(...))`
and drop the expression-input quirk from the documentation.

---

## 4. Input and output

`input(prompt)` returns a **string**, always. Convert it.

The template's `getnum()` wraps `eval()` so a prompt accepts:

- `48.50` — a plain number
- `40+8.50` — arithmetic
- `6*pi` — anything in scope after `from math import *`

Screen width in the Python App is roughly **26 characters** before wrapping at the default
font size. Keep labels short:

```python
print("Total: {:.2f}".format(t))       # good
print("The total including tip is: {:.2f}".format(t))   # wraps
```

Use plain ASCII. `°`, `±`, `≈`, `√`, and smart quotes render unreliably. Write `deg`, `+/-`,
`~`, `sqrt`.

---

## 5. Trigonometry and MODE — read this before writing any trig

**Python's `math` module is always in radians.** The calculator's `MODE` screen
(DEGREE / RADIAN) governs TI-BASIC and the home screen. It has **no effect** on Python.

This trips up nearly everyone, because the same calculator behaves differently in its two
languages. Handle it explicitly:

```python
from math import *

deg = getnum("Angle in degrees: ")
print("sin = {:.4f}".format(sin(radians(deg))))   # correct
print("sin = {:.4f}".format(sin(deg)))            # WRONG - treats it as radians
```

Decide at design time whether the prompt takes degrees or radians, say so in the prompt text
itself (`"Angle (deg): "`), and convert inside the program.

---

## 6. Program naming

Names become AppVars on the calculator, which imposes the rules:

- 1–8 characters
- Letters `A–Z` and digits `0–9` only
- First character must be a letter
- Lowercase is converted to uppercase automatically on send
- No spaces, hyphens, underscores, or accented characters

A filename that violates these is not rejected — TI Connect silently renames it to
`PYTHON01`, `PYTHON02`, and so on. Always validate the name first.

---

## 7. Running a program on the calculator

1. Press `[apps]`, choose **Python App**.
2. The file manager lists Python AppVars. Highlight the program.
3. Press the **Run** soft key (or `[enter]` to edit, then **Run**).
4. The Shell opens, the program executes, prompts appear inline.
5. Press `[clear]` or the **Esc**/quit soft key to return to the file manager.

From the Shell prompt you can also run it by importing:

```python
>>> from TIPCALC import *
```

Because of that import behaviour, **never** wrap the program body in
`if __name__ == "__main__":` — the calculator would import the module and run nothing.
Keep the executable statements at module top level.
