# ti84-evo-scripter

[![version](https://img.shields.io/badge/version-1.2.0-blue)](CHANGELOG.md)
[![status](https://img.shields.io/badge/status-production--ready-brightgreen)](SKILL.md)
[![category](https://img.shields.io/badge/category-code--generation-0a7ea4)](SKILL.md)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Validate Skill](https://github.com/jovd83/ti84-evo-scripter/actions/workflows/validate.yml/badge.svg)](https://github.com/jovd83/ti84-evo-scripter/actions/workflows/validate.yml)
[![python](https://img.shields.io/badge/python-3.9%2B-blue)](.github/workflows/validate.yml)
[![models](https://img.shields.io/badge/models-6%20TI--Python-informational)](references/model-matrix.md)
[![tests](https://img.shields.io/badge/tests-41%20cases%20passing-brightgreen)](sandbox/)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=flat&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/jovd83)

An [AgentSkill](https://agentskills.io) that turns a plain-language description of a
calculation into a **working Python program for the TI-84 Evo / Evo-T**, delivered as a real
`.py` file you can upload with TI Connect Evo.

> *"A program called TIPCALC that asks for a bill amount and a tip percentage, then displays
> the tip amount and the total."*

...produces `TIPCALC.py`, a verified test report, upload instructions, and a printable
one-page handout.

---

## Why this exists

Agents get TI calculator programs wrong in predictable ways. They emit f-strings that raise
`SyntaxError` on the device, import `numpy`, hand-write `.8xv` binaries that the calculator
rejects, wrap the program in `if __name__ == "__main__":` so nothing runs, claim the
calculator can't accept uploaded files, or assert that the `MODE` screen changes what
`math.sin()` does. It doesn't.

This skill encodes the platform's real constraints and ships deterministic tooling that
catches those mistakes before the file leaves the machine.

## What you get

| Deliverable | How |
|---|---|
| A real `.py` file | Written to disk, ready for TI Connect |
| Verified math | `verify_program.py` runs the program against ≥3 cases including an edge case |
| Lint-clean source | `lint_ti_python.py` rejects f-strings, dead imports, illegal names, degree-trig bugs |
| Simulated run | `simulate_ti84.py` runs it under the device's constraints and draws the screen |
| One-page PDF handout | `make_handout.py` — print it, hand it to a class |
| Upload + run steps | For every transfer path and the right Connect app for the family |
| Trig-mode statement | Radians / not applicable, stated explicitly every time |

## Supported models

Pass `--target <key>` to every script.

| Key | Model | Region | Exam LED |
|---|---|---|---|
| `evo` | TI-84 Evo | US / intl. | no |
| `evo-t` | TI-84 Evo-T | Europe | yes |
| `ce-python` | TI-84 Plus CE Python | US | no |
| `ce-t-python` | TI-84 Plus CE-T Python Edition | Europe | yes |
| `83pce-python` | TI-83 Premium CE Édition Python | France | yes |
| `82aep` | TI-82 Advanced Edition Python | France | yes |

`ce`, `ce-t`, `84t` and `82advanced` have **no Python App**. The tooling refuses
them with exit 2 and an explanation rather than generating code that cannot run.
TI-Nspire, Casio and NumWorks are different platforms and out of scope. Full
matrix: [references/model-matrix.md](references/model-matrix.md), machine-readable
in [scripts/ti_models.py](scripts/ti_models.py).

Model choice is not cosmetic. It changes the module set (`turtle` is removed on
the Evo but a separate download on the French CE models), the screen width
(~30 columns on an Evo, ~16 on the monochrome `82aep`), and which transfer app
applies — TI Connect Evo and TI Connect CE are not interchangeable.

## There is no TI-Python emulator, so this simulates the constraints

CEmu, the standard third-party TI-84 Plus CE emulator, does not emulate the
Atmel ATSAMD21 coprocessor that runs Python on the CE Python models; its
experimental branch is unusable and its maintainers point people at TI's paid
SmartView. Nothing emulates the Evo at all, and SmartView cannot be scripted.

`simulate_ti84.py` therefore reproduces what the device *forbids* rather than
how it computes: imports outside the model's set raise `ImportError`, `open`,
`exec` and `compile` are unavailable, f-strings are rejected before the run, and
output is drawn at the model's screen width so wrapping is visible.

```
  +--------------------------------+
  |          TI-84 Evo-T           |
  +--------------------------------+
  | TIP CALCULATOR                 |
  | Bill amount: 48,50             |
  | Tip percent: 18                |
  | Tip:   8.73                    |
  | Total: 57.23                   |
  +--------------------------------+
```

`verify_program.py` runs inside the same sandbox, so a program importing
`statistics` fails its tests even though it passes on a desktop. What the
simulator cannot reach — timing, memory exhaustion, `ti_plotlib`/`ti_hub`/
`ti_rover` hardware — is stated rather than glossed over.

## Install

With the [Skills CLI](https://github.com/vercel-labs/skills) — detects your agent
and installs to the right directory:

```bash
npx skills add jovd83/ti84-evo-scripter
```

Install globally rather than into the current project, and confirm it landed:

```bash
npx skills add -g jovd83/ti84-evo-scripter
npx skills list
```

Or clone it directly:

```bash
git clone https://github.com/jovd83/ti84-evo-scripter.git ~/.agents/skills/ti84-evo-scripter
```

Either way, the folder just needs to sit in a skills directory your agent loads —
`~/.agents/skills/`, `~/.claude/skills/`, or the project-local equivalent.

Requires **Python 3.9+** for the scripts, standard library only — no `pip install`.
PDF generation uses headless Chrome or Edge if present; otherwise the handout is
written as HTML for you to print.

## Use

Just describe the program:

> Make me a QUADRT that takes a, b, c and shows the two roots.

The agent asks for anything missing, picks a legal 8-character name, writes the program,
lints it, runs the tests, and delivers everything at once.

## Tooling, standalone

The scripts work without an agent:

```bash
# What is missing, what got fixed, what still degrades
python scripts/preflight.py --target evo-t --fix

# One gate: lint -> simulate -> verify, with a single NEXT ACTION on failure
python scripts/run_checks.py --program MYPROG.py --tests tests.json --target evo-t

# Individual stages
python scripts/lint_ti_python.py MYPROG.py --target 83pce-python
python scripts/simulate_ti84.py --program MYPROG.py --target 82aep --inputs 3 4
python scripts/simulate_ti84.py --program MYPROG.py --interactive
python scripts/verify_program.py --program MYPROG.py --tests tests.json

# Printable reference sheet
python scripts/make_handout.py --spec handout.json --out MYPROG-handout.pdf

# What can I target?
python scripts/lint_ti_python.py --list-targets
```

Every script exits non-zero on failure and takes `--json`, so they drop straight
into CI, a pre-commit hook, or an agent loop.

### The correction loop

`run_checks.py` is built to be run repeatedly. It stops at the first failing
stage and prints one instruction:

```
  [PASS] lint
  [PASS] simulate
  [FAIL] verify

  Lint warnings (not blocking, but review them):
    W010 line 14: sin(ang) where 'ang' was read from a degrees prompt
------------------------------------------------------------------
  NEXT ACTION:
    Test 'right angle' failed with inputs ['3', '4', '90']: missing
    expected output: 'Area: 6.00'. Fix the program -- never edit the
    expected value to match a wrong result.

  Fix that, then re-run with --iteration 2
```

Wrap `radians()` around the input, re-run, and it reports `ALL CHECKS PASSED`.
Past five iterations it tells the caller to stop looping and explain what is
stuck, so a confused agent cannot spin.

## Missing prerequisites degrade, they do not block

`preflight.py` sorts requirements into `BLOCKING` and `DEGRADED` and emits a
capability set:

```json
{"can_generate": true, "can_simulate": true, "handout_format": "pdf"}
```

No browser means `handout_format: "html"` — the run continues and the user gets
an HTML handout plus print-to-PDF instructions. `--fix` remediates what is local
and reversible. System-level installs are opt-in via `--fix-system`; without it
the exact `winget` / `brew` / `apt` command is printed for a human to approve.
Nothing is installed silently.

The preflight also self-tests the sandbox by running `import numpy` through it
and confirming it was blocked, so a broken simulator is caught before it can
green-light a bad program.

## The sandbox — five real programs you can send today

[`sandbox/`](sandbox/) is not a scratch directory. It holds five complete,
verified deliverables produced by running this skill's own workflow end to end,
kept in the repo for three reasons:

1. **Working programs.** Send the `.py` files to a calculator and use them.
2. **Reference output.** They show an agent what "done" looks like — comment
   density, output formatting, edge-case coverage, handout structure.
3. **A regression suite.** CI gates all five on all six Python-capable models
   on every push, so a change to the linter or the sandbox cannot quietly break
   the programs the skill is supposed to produce.

| Program | Does | Curriculum area | Tests |
|---|---|---|---|
| [QUADRT](sandbox/QUADRT/) | Quadratic roots, discriminant, vertex — all three cases incl. complex | Algebra | 7 |
| [TRISOLV](sandbox/TRISOLV/) | Triangle solver: SSS, SAS, ASA → sides, angles, area, perimeter | Geometry + trig | 7 |
| [STATS1](sandbox/STATS1/) | One-variable statistics: five-number summary, IQR, both SDs | Statistics | 6 |
| [COMPINT](sandbox/COMPINT/) | Compound interest and monthly-savings growth | Percentages, exponentials | 7 |
| [KINEMAT](sandbox/KINEMAT/) | Constant acceleration: know 3 of v0/v/a/t/d, get the other 2 | Physics | 8 |

**35 sandbox cases + 6 for the bundled `TIPCALC` example = 41, all passing, zero
lint warnings, across 30 program×model combinations.**

Each folder contains `<NAME>.py` (the file you send), `tests.json`,
`handout.json`, and a generated one-page `<NAME>-handout.pdf`.

- [sandbox/README.md](sandbox/README.md) — per-program test cards, upload steps,
  shared input quirks, trig-mode notes, exam-legality summary, and the known
  `82aep` line-wrapping limitation.
- [sandbox/REQUIREMENTS.md](sandbox/REQUIREMENTS.md) — the 12 common requirements
  and per-program specifications the five were built against, including which
  edge cases are mandatory.

Run the whole suite yourself:

```bash
cd sandbox
for p in QUADRT TRISOLV STATS1 COMPINT KINEMAT; do
  python ../scripts/run_checks.py --program $p/$p.py --tests $p/tests.json --target evo-t
done
```

### Why the sandbox is evidence, not decoration

Every expected value in those `tests.json` files was computed **independently of
the programs**, by a reference script using different formulations — Heron's
formula cross-checked against `ab·sin(C)/2`, quadratic roots against
`2c/(−b−√D)` plus a residual check that `ax²+bx+c ≈ 0`, compound interest
against an explicit period-by-period loop, standard deviation two-pass versus
the sum-of-squares identity. Only values agreeing to 1e-9 across both methods
were written down.

That independence is the point: because the tests were not fitted to the
programs, they caught two genuine bugs before delivery.

- **QUADRT** printed `-0.0000` for the vertex when `b = 0`, because `-0.0/2` is
  negative zero in IEEE arithmetic. Harmless numerically, but it reads as a bug
  to a student looking at the screen.
- **STATS1** raised `IndexError` on a single data point, because the quartile
  half-lists were empty.

Both surfaced at gate iteration 1, were fixed, and passed at iteration 2. No
expected value was ever adjusted to match program output.

## Continuous integration

[`.github/workflows/validate.yml`](.github/workflows/validate.yml) runs three
jobs on every push and pull request.

| Job | What it proves |
|---|---|
| **structure** | [`scripts/validate_skill.py`](scripts/validate_skill.py) checks required files, frontmatter validity, the ≤500-line / ≤5k-token budget, that every path and lint rule code cited in `SKILL.md` actually exists, model-registry integrity, JSON validity, that every `tests.json` has ≥3 cases with a named edge case and real assertions, and that no shipped `.py` contains an f-string, a `__main__` guard, a non-ASCII character, or an illegal AppVar name. Also runs preflight to confirm it **degrades rather than fails** on a runner with no browser. |
| **behaviour** | On Python 3.9, 3.11 and 3.13: the sandbox really blocks `import statistics`; all four non-Python models are refused; an illegal program name is rejected; the bundled example passes the full gate; the handout builds and falls back to HTML with no browser present. |
| **sandbox** | All five sandbox programs gated on all six Python-capable models — 30 combinations, run in parallel. |

The validator is self-checking in the sense that matters: deliberately breaking
seven things (bad `description`, a removed non-negotiable, a dead `references/`
link, a bogus lint code, an added f-string, a deleted reference file) produces
seven distinct failures and exit 1.

```bash
python scripts/validate_skill.py .
```

## Layout

```
SKILL.md                      the agent's instructions
.github/workflows/validate.yml  CI: structure + behaviour + sandbox matrix
references/
  model-matrix.md             every model, what differs, which are unsupported
  ti-python-language.md       supported syntax, module allow/deny list, quirks
  transfer-options.md         all four ways to get a file onto the calculator
  exam-legality.md            ACT / SAT / AP rules, EU exam mode, the exam LED
assets/
  program_template.py         canonical skeleton, incl. the decimal-comma guard
  handout_template.html       one-page reference sheet layout
scripts/
  ti_models.py                model registry -- source of truth for all checks
  validate_skill.py           repository-shape validation, used by CI
  preflight.py                prerequisite check, auto-remediation, capabilities
  run_checks.py               the gate: lint -> simulate -> verify, one NEXT ACTION
  lint_ti_python.py           model-aware static checks
  simulate_ti84.py            runs it under device constraints, draws the screen
  _ti_sandbox.py              the constraint sandbox itself (not run directly)
  verify_program.py           runs the program in the sandbox and asserts output
  make_handout.py             HTML + PDF handout builder
  ti_stubs/                   stubs so ti_system imports don't crash a PC run
examples/TIPCALC/             a complete, verified deliverable to pattern-match
sandbox/                      five real programs, gated by CI on every model
evals/evals.json              behavioural cases + tooling checks
evals/fixtures/BADIMP.py      passes on desktop, must fail in the sandbox
```

## Scope

**In:** numeric programs — formulas, conversions, finance, physics, geometry, statistics
computed from typed inputs.

**Out:** symbolic algebra, equation solving, factoring, calculus. Not a limitation of the
tool — a deliberate constraint. CAS functionality is what gets a calculator banned from an
exam, so this skill stays on the safe side of that line. It will print the two numeric roots
of a quadratic; it will not print `x = (-b ± √(b²-4ac)) / 2a` as a manipulated expression.

## Platform notes

Targets the **TI-84 Evo** and **TI-84 Evo-T** (the European variant with the exam-mode LED).
Everything it produces also runs on the **TI-84 Plus CE Python** — Python programs are
portable between them. TI-BASIC programs are not, since the Evo uses a new `.8xp2` format.

Three facts worth internalising:

1. **f-strings do not work.** TI-Python descends from CircuitPython/MicroPython and its
   parser predates them. Use `"{:.2f}".format(x)`.
2. **`MODE` does not affect Python.** The DEGREE / RADIAN setting governs TI-BASIC and the
   home screen. `math.sin()` is always radians. Convert with `radians()`.
3. **A decimal comma silently breaks input.** `eval("48,50")` returns the tuple
   `(48, 50)`, so a European user typing a perfectly valid amount is told
   "Not a number". Every generated program carries the two-line guard.

## License

MIT. See [LICENSE](LICENSE).
