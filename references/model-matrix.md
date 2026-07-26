# TI calculator model matrix

Which models this skill can target, and what changes between them. The machine-
readable version of this table is `scripts/ti_models.py` — that file is the
source of truth for the linter and simulator. Fix facts there, not here.

Check the target before writing code:

```bash
python scripts/lint_ti_python.py --list-targets
python scripts/preflight.py --target 83pce-python
```

---

## Python-capable — the skill can target these

| Key | Model | Region | Exam LED | Python engine | Screen* | Transfer |
|---|---|---|---|---|---|---|
| `evo` | TI-84 Evo | US / intl. | no | native ARM 156 MHz | ~30 | TI Connect Evo |
| `evo-t` | TI-84 Evo-T | Europe | **yes** | native ARM 156 MHz | ~30 | TI Connect Evo |
| `ce-python` | TI-84 Plus CE Python | US | no | ATSAMD21 coprocessor | ~26 | TI Connect CE |
| `ce-t-python` | TI-84 Plus CE-T Python Edition | Europe | **yes** | ATSAMD21 coprocessor | ~26 | TI Connect CE |
| `83pce-python` | TI-83 Premium CE Édition Python | France | **yes** | ATSAMD21 coprocessor | ~26 | TI Connect CE |
| `82aep` | TI-82 Advanced Edition Python | France | **yes** | Python App, monochrome | ~16 | TI Connect CE |

\* Approximate console width, used only for wrap warnings. Conservative
estimates, not documented TI specs.

## No Python App — the skill must refuse, not improvise

| Key | Model | Region | Why |
|---|---|---|---|
| `ce` | TI-84 Plus CE (non-Python) | US | No Python App |
| `ce-t` | TI-84 Plus CE-T (non-Python) | Europe | No Python App |
| `84t` | TI-84 Plus T | Netherlands | Monochrome, TI-BASIC only |
| `82advanced` | TI-82 Advanced (non-Python) | France | No Python App. Not the same as the *Edition Python*. |

If the user names one of these, say plainly that the model has no Python App
and offer the two real choices: a Python-capable model, or TI-BASIC — which
this skill does not cover. Do not silently generate Python for it.

## Out of scope

- **TI-Nspire CX II / CX II-T** run Python, but on a different platform:
  `.tns` documents, different module set, TI-Nspire software rather than
  TI Connect. A `.py` from this skill will not transfer the same way.
- **Casio** (fx-CG50, fx-9750GIII) and **NumWorks** have their own Python
  implementations with different modules.

---

## What actually differs between targets

### 1. Transfer software — easy to get wrong

`TI Connect Evo` (web, `connectevo.ti.com`) serves the **Evo family only**.
`TI Connect CE` (desktop) serves the **CE family only**. They are not
interchangeable. The linter does not catch this; the delivery text must be
right.

### 2. Module availability

| Module | Evo / Evo-T | CE Python family | 82AEP |
|---|---|---|---|
| `math`, `random`, `time` | yes | yes | yes |
| `ti_system`, `ti_plotlib` | yes | yes | yes |
| `ti_hub`, `ti_rover` | yes | yes | assume no |
| `ti_draw`, `ti_image`, `ti_graphics` | assume no | yes | no |
| `turtle` | **removed** | separate download | no |
| `ce_chart`, `ce_box`, `ce_quivr` | no | separate download | no |

The French CE models ship extra downloadable modules. Using one is a lint
**warning**, not an error — it works, but only if the module is also sent to
the calculator. Say so in the delivery.

`turtle` on the Evo is a hard **error**: it existed on the CE Python and every
older tutorial shows it.

### 3. Screen width

The `82aep` is monochrome and roughly 16 columns. A label that fits an Evo will
wrap there. Lint `W007` and the simulator's screen frame are both width-aware,
so lint against the actual target:

```bash
python scripts/simulate_ti84.py --program AREA.py --target 82aep --inputs 3 4
```

### 4. Decimal comma — the biggest non-US trap

European users type `48,50`. Without a guard, `eval("48,50")` returns the
**tuple** `(48, 50)`, `float()` rejects it, and the program prints
"Not a number" at a value that looks perfectly valid to the user.

Every program must include the two-line guard from
`assets/program_template.py`:

```python
if "," in s and "(" not in s:
    s = s.replace(",", ".")
```

The `"(" not in s` condition matters: it leaves genuine multi-argument
expressions such as `atan2(1,2)` alone.

### 5. Localised OS, English Python

The French models present menus in French; the `TI-84 Plus T` is Dutch-market.
Python keywords are English everywhere. What this affects is **prompt text** —
writing prompts in the user's language is fine and often better, but keep them
ASCII. `Montant de l'addition:` is safe; `Bedrag rekening (€):` is not, because
non-ASCII characters render unreliably. Lint `W002` catches this.

### 6. Exam mode

Every European variant carries the Press-to-Test LED. Exam mode **disables user
programs** while active — it does not delete them. Consequence for a user in
France, Belgium, or the Netherlands: the program is unavailable during an exam
that requires exam mode. See `exam-legality.md`.

### 7. TI-BASIC portability, if the user asks

The Evo uses `.8xp2`; the CE family uses `.8xp`, and they are not compatible —
TI rewrote the BASIC engine. **Python is portable across all Python-capable
models in the table.** That is a good reason to answer in Python even when the
user first asks for TI-BASIC.
