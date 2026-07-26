---
name: ti84-evo-scripter
description: Use when the user wants a working calculator program for a TI-84 Evo, Evo-T, TI-84 Plus CE/CE-T Python, TI-83 Premium CE Python, or TI-82 Advanced Edition Python — delivered as a real, uploadable .py file. Trigger on requests like "make a TIPCALC that asks for a bill and a tip percent", on turning a formula into an on-calculator prompt-and-print program, on TI-Python syntax errors, on getting a program onto the calculator (TI Connect Evo or CE, unit-to-unit, on-device typing), and on exam-legality questions (ACT/SAT/AP, EU exam mode). Produces a lint-clean .py simulated against the target model's constraints, verified test cases with exact expected output, upload steps, and a printable one-page PDF handout.
metadata:
  dispatcher-layer: production
  dispatcher-lifecycle: active
  dispatcher-category: code-generation
  dispatcher-capabilities: ti-python-program-generation, calculator-file-delivery, exam-legality-check
  dispatcher-accepted-intents: write_calculator_program, generate_ti84_python, make_calculator_handout
  dispatcher-input-artifacts: program_spec, formula, prompt_list
  dispatcher-output-artifacts: py_program, test_report, handout_pdf
  dispatcher-stack-tags: ti-python, circuitpython, ti-84-evo
  dispatcher-risk: low
  dispatcher-writes-files: true
---

# TI-84 Evo Scripter

> **Author:** jovd83 | **Version:** 1.2.0

Turn a plain-language description of a calculation into a **numeric-only Python program** that runs in the TI Python App, and deliver it as a real `.py` file.

## Non-negotiables

1. **The calculator accepts uploaded files.** Never tell the user it cannot. Delivery is always a real `.py` file written to disk.
2. **Ship `.py` only.** Never hand-write `.8xv`, `.8xp`, `.8xp2`, or any calculator binary. TI Connect does that conversion on send.
3. **Numeric output only.** No symbolic algebra, equation solving, factoring, or calculus. Arithmetic on numbers the user typed is fine. This keeps the program non-CAS and exam-legal.
4. **No f-strings.** TI-Python raises `SyntaxError` on `f"..."`. Use `"{:.2f}".format(x)`.
5. **Never claim a check passed without running it.** `run_checks.py` prints the evidence; paste it.

## Workflow

### 0. Preflight — always first

```bash
python scripts/preflight.py --target <model> --fix
```

It checks Python version, skill files, write access, that the sandbox really blocks imports, and whether a browser exists for PDF export. `--fix` repairs what is local and reversible and prints what it did.

Then act on the result:

- **Exit 0, nothing missing** → continue.
- **Exit 0 with a `DEGRADED` line** → **continue anyway**, and tell the user what you lost. No browser means the handout ships as HTML with print-to-PDF instructions. Never stop over a degraded capability.
- **Exit 1 (`BLOCKING`)** → fix it. If the remedy is a system install, tell the user the exact command, offer to run `--fix-system`, and wait. Do not fake the deliverable.

Report installs in one line: "Preflight installed X; PDF export is available." Never install silently.

### 1. Identify the target model

Ask if unstated. Do not assume the Evo — a user in France likely has a `83pce-python`, in the Netherlands possibly an `84t` with no Python at all.

```bash
python scripts/lint_ti_python.py --list-targets
```

Pass `--target <key>` to **every** script. Full matrix in `references/model-matrix.md`.

**If the model has no Python App** (`ce`, `ce-t`, `84t`, `82advanced`): say so plainly, name the two real options — a Python-capable model, or TI-BASIC which this skill does not cover — and stop. Do not generate Python for it.

**If it is a TI-Nspire, Casio, or NumWorks**: different platform, different transfer. Say so instead of guessing.

### 2. Collect the spec

| Field | Rule |
|---|---|
| Program name | 1–8 characters, `A–Z0–9`, first character a letter. Uppercase. Becomes `<NAME>.py`. |
| What it calculates | The formula or procedure. |
| Prompts | What the user is asked for, in order, with units. |
| Displayed output | What is printed, with labels and decimal places. |

Fix an illegal name and say so in one line (`TIPCALCULATOR` → `TIPCALC`). Illegal names are silently renamed to `PYTHON01` on send, so never pass one through.

### 3. Ask which transfer path

Offer these; details in `references/transfer-options.md`:

- **TI Connect Evo** — web, `connectevo.ti.com`, Chrome 143+. **Evo family only.**
- **TI Connect CE** — desktop. **CE family only.** The two are not interchangeable.
- **Type it on the calculator** — no cable, viable under ~30 lines. Supply a shortened variant if chosen.
- **Unit-to-unit USB-C** — from another calculator of the same family.

### 4. Write the program

Start from `assets/program_template.py`.

- `from math import *` only when math functions are used.
- Read every input through the template's `getnum()`. It loops on bad input, accepts expressions like `6*pi`, **and converts a decimal comma** — without that, `eval("48,50")` returns the tuple `(48, 50)` and a European user sees "Not a number" on a valid entry.
- Format fixed decimals with `"{:.2f}".format(x)`.
- Keep printed lines inside the target's width: ~30 columns on Evo, ~26 on CE, **~16 on `82aep`**.
- Label every printed value. Plain ASCII only — prompts in the user's language are welcome, accented characters are not.

### 5. Run the check gate, and loop until it passes

```bash
python scripts/run_checks.py --program <NAME>.py --tests tests.json --target <model>
```

One command runs **lint → simulate → verify**, stops at the first failure, and prints a single `NEXT ACTION`. Loop:

1. Run it.
2. Exit 0 and `ALL CHECKS PASSED` → go to step 6.
3. Otherwise read `NEXT ACTION`, edit the program, re-run with `--iteration N+1`.

Fix the **program**, never the expected value. If the same stage fails five times, stop and tell the user what is stuck and why — do not loop forever.

The stages, if you need one alone:

| Stage | Command | Catches |
|---|---|---|
| lint | `lint_ti_python.py <f> --target <m>` | f-strings, absent modules, illegal names, degree-trig bugs, over-wide prints |
| simulate | `simulate_ti84.py --program <f> --target <m> --inputs ...` | runtime failures under the device's real constraints; draws the screen |
| verify | `verify_program.py --program <f> --tests <t> --target <m>` | wrong math |

**About the simulator:** there is no emulator that runs TI-Python. CEmu does not emulate the Atmel ATSAMD21 coprocessor that executes Python on the CE models, and nothing emulates the Evo. So `simulate_ti84.py` reproduces the *constraints* — module blocking, no `open`/`exec`, f-string rejection, screen width — not the silicon. `verify_program.py` runs inside the same sandbox, so a program importing `statistics` fails its tests even though it would pass on a desktop. Timing, memory exhaustion, and `ti_plotlib`/`ti_hub`/`ti_rover` behaviour still need the real device: say so when the program uses them.

`tests.json` needs **at least three cases, one an edge case** (zero, negative, very large, expression input, or decimal comma):

```json
{
  "program": "TIPCALC.py",
  "cases": [
    {"name": "typical",    "inputs": ["48.50", "18"], "expect": ["Tip:   8.73", "Total: 57.23"]},
    {"name": "round pct",  "inputs": ["100", "15"],   "expect": ["Tip:   15.00", "Total: 115.00"]},
    {"name": "edge: zero", "inputs": ["0", "20"],     "expect": ["Tip:   0.00"], "reject": ["Traceback"]}
  ]
}
```

### 6. State the trig mode explicitly

One of these sentences, every time. Never guess.

- **Uses trig:** "Python's `math` module always works in **radians**. The calculator's `MODE` (DEGREE/RADIAN) setting affects TI-BASIC and the home screen only — it does **not** change Python. This program converts your degree input with `radians()` internally, so leave `MODE` alone."
- **No trig:** "Mode does not matter. This program only does arithmetic, so the DEGREE/RADIAN setting has no effect on it."

### 7. Build the handout

```bash
python scripts/make_handout.py --spec handout.json --out <NAME>-handout.pdf
```

Schema and a filled example are in `examples/TIPCALC/handout.json`. Writes HTML, then PDF via headless Chrome/Edge; with no browser it keeps the HTML and says to print from there. Report which happened.

### 8. Deliver

All seven, every time:

1. **File paths** to the `.py` and the handout.
2. **The full source, inline in chat**, in a plain code block.
3. **How it works** — a short paragraph plus the formula.
4. **Upload steps** for the chosen path and the right Connect software, then how to find and run it in the Python App.
5. **Input quirks** — at minimum that expressions (`6*pi`, `40+8.50`) and a decimal comma both work.
6. **Trig-mode sentence** from step 6.
7. **One concrete test** — exact keystrokes in, exact screen output expected.

## Worked example

`examples/TIPCALC/` is a complete verified deliverable: program, six test cases, handout spec, generated PDF. Read it before writing a new program.

Requested: *"A program called TIPCALC that asks for a bill amount and a tip percentage, then displays the tip amount and the total."*

```
Bill amount: 48.50
Tip percent: 18
Tip:   8.73
Total: 57.23
```

## Anti-patterns, and what enforces each

Machine-enforced ones fail the gate — you cannot ship past them. The rest are on you.

| Do not | Enforced by | Because |
|---|---|---|
| `f"Total: {t:.2f}"` | lint `E004` + simulate precheck | `SyntaxError` on the calculator |
| `import numpy` / `sympy` / `statistics` / `decimal` | lint `E003` + sandbox `ImportError` | Not on the device |
| `import turtle` on an Evo | lint `E003` (model-aware) | Removed on the Evo; still in old tutorials |
| Use a French extra module as if standard | lint `W011` | `turtle`/`ce_chart`/`ce_box`/`ce_quivr` are separate downloads |
| `sin(deg_input)` without `radians()` | lint `W010` + verify failure | `MODE` does not affect Python |
| Name it `MYTIPCALCULATOR` | lint `E002` | Over 8 chars → renamed to `PYTHON01` |
| Deliver a `.8xv` / `.8xp2` | lint `E010` | Wrong layer; TI Connect converts `.py` |
| `open()` / `exec()` / `compile()` | lint `E006` + sandbox `NameError` | No filesystem in the Python App |
| `if __name__ == "__main__":` | lint `E008` | The calculator imports to run; the guard suppresses everything |
| Symbolic solving or factoring | lint `E007` (partial) + your judgement | CAS risks the exam rules |
| Labels too long for the screen | lint `W007` + simulator screen frame | Output wraps mid-number |
| Non-ASCII (`°`, `±`, `≈`, `€`) | lint `W002` | Unreliable in the calculator font |
| Skip the comma guard in `getnum()` | verify, if you test `48,50` | Non-US users type a decimal comma |
| Say the Evo can't take uploaded files | nothing — do not do it | False |
| Claim checks passed without running them | nothing — do not do it | The gate prints evidence; paste it |
| Offer TI Connect CE for an Evo (or Evo for a CE) | nothing — check the matrix | They are not interchangeable |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `SyntaxError` at a print | f-string | Use `"{:.2f}".format(x)` |
| `ImportError: no module named ...` | Desktop-only library | Recompute with `math` |
| Program appears as `PYTHON01` | Filename broke the naming rules | Rename to 1–8 chars, letter first, re-send |
| `TypeError: can't convert str to float` | Raw `input()` | Route through `getnum()` |
| "Not a number" on a valid entry | Decimal comma, no guard | Add the comma line from the template |
| Nothing happens after import | `__main__` guard | Remove it; keep code at top level |
| Output wraps mid-number | Line too long for this model | Shorten labels; re-simulate with `--target` |
| Trig answers wrong by a lot | Degrees passed as radians | Wrap in `radians()` |
| Program missing after an exam | Press-to-Test disables user programs | Exit exam mode; see `exam-legality.md` |
| TI Connect won't see the calculator | Wrong browser, charge-only cable, or wrong Connect app | Chrome 143+, USB-C data cable, match app to family |
| Sandbox blocks a module you believe exists | Registry gap | Confirm on device, then fix `scripts/ti_models.py` |
| `verify` says "requested more input" | Fewer `inputs` than `input()` calls | Add the missing values |

## References

Read only when the situation calls for it:

- `references/model-matrix.md` — every model, what differs, which are unsupported.
- `references/ti-python-language.md` — supported syntax, module allow/deny, memory limits, quirks.
- `references/transfer-options.md` — all transfer paths step by step, plus troubleshooting.
- `references/exam-legality.md` — ACT/SAT/AP rules, EU exam mode, the exam LED.
