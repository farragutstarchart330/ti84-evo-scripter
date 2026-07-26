# Changelog

All notable changes to this skill are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning follows [SemVer](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-07-26

### Added

- `.github/workflows/validate.yml` — CI in three jobs. **structure** runs the new
  validator and confirms preflight degrades rather than fails on a browserless runner;
  **behaviour** runs on Python 3.9/3.11/3.13 and proves the sandbox blocks
  `import statistics`, that all four non-Python models are refused, that an illegal
  AppVar name is rejected, that the bundled example passes the gate, and that the
  handout falls back to HTML; **sandbox** gates all five sandbox programs across all six
  Python-capable models as a 6-way parallel matrix (30 combinations).
- `scripts/validate_skill.py` — repository-shape validation. Checks required files,
  frontmatter validity (name pattern, description length, the mandatory "Use when"
  opening), the ≤500-line / ≤5k-token budget, that every `scripts/`, `references/`,
  `assets/` and `examples/` path cited in `SKILL.md` exists, that every lint rule code
  cited in `SKILL.md` is actually emitted by the linter, model-registry integrity
  including alias targets, JSON validity repo-wide, that every `tests.json` declares ≥3
  cases with a named edge case and real assertions, and that no shipped program contains
  an f-string, a `__main__` guard, a non-ASCII character, or an illegal AppVar name.
  Verified against seven deliberate breakages, each producing a distinct failure.
- `sandbox/` — five complete verified deliverables (`QUADRT`, `TRISOLV`, `STATS1`,
  `COMPINT`, `KINEMAT`) with 35 test cases, chosen against the ACT Math blueprint and
  the TI archive download distribution. Documented in `sandbox/README.md` and
  `sandbox/REQUIREMENTS.md`.
- `evals/fixtures/BADIMP.py` — a program that passes on desktop CPython and must fail in
  the constraint sandbox, so the import blocker itself is regression-tested.
- Badge block and a full sandbox + CI section in `README.md`.

### Changed

- **Minimum Python is now 3.9**, up from 3.8. 3.8 is end-of-life and `setup-python` no
  longer provides it on `ubuntu-latest`, so claiming 3.8 would have been an untestable
  promise. `preflight.py` enforces the new floor.

### Fixed

- Two bugs in sandbox programs, caught by the gate before delivery: `QUADRT` printed
  `-0.0000` for the vertex when `b = 0` (negative zero from `-0.0/2`), and `STATS1`
  raised `IndexError` on a single data point (empty quartile half-lists).

## [1.1.0] - 2026-07-26

### Added

- **Full international model support.** `scripts/ti_models.py` is a registry of ten
  models — TI-84 Evo, Evo-T, TI-84 Plus CE Python, CE-T Python Edition, TI-83 Premium CE
  Édition Python, TI-82 Advanced Edition Python, plus the four non-Python variants
  (`ce`, `ce-t`, `84t`, `82advanced`). Every script takes `--target`. Models without a
  Python App are refused with exit 2 and an explanation rather than being handed code
  that cannot run. `references/model-matrix.md` documents what actually differs:
  module sets, screen width, exam LED, and which Connect app applies.
- `scripts/preflight.py` — classifies requirements as BLOCKING or DEGRADED, emits a
  capability set, and remediates. `--fix` handles local reversible gaps; `--fix-system`
  opts into `winget`/`brew`/`apt`. Without a browser the run continues and the handout
  falls back to HTML instead of stopping. Self-tests the sandbox by confirming that
  `import numpy` is really blocked.
- `scripts/simulate_ti84.py` and `scripts/_ti_sandbox.py` — a constraint simulator.
  No emulator runs TI-Python (CEmu does not emulate the CE's Atmel ATSAMD21 Python
  coprocessor; nothing emulates the Evo; SmartView is paid and unscriptable), so this
  enforces the device's restrictions instead: model-aware import blocking, no
  `open`/`exec`/`compile`, f-string rejection before the run, and output drawn at the
  target's screen width. `input()` is echoed on piped runs so the rendered screen
  matches the device instead of collapsing every prompt onto one line.
- `scripts/run_checks.py` — one gate running lint → simulate → verify, stopping at the
  first failure with a single `NEXT ACTION`. Built for an agent to loop on, with an
  advisory cap at five iterations so a stuck loop reports instead of spinning.
- Lint rule `W010`: trig called on a value read from a degrees-worded prompt without
  `radians()`. Catches the most common TI-Python maths bug statically.
- Lint rule `E010`: refuses a calculator binary extension (`.8xv`, `.8xp2`, `.tns`, …).
- Lint rule `W011`: flags the French CE extra modules (`turtle`, `ce_chart`, `ce_box`,
  `ce_quivr`) as separate downloads rather than assuming they are present.
- Decimal-comma handling in `assets/program_template.py` and the TIPCALC example.
  `eval("48,50")` returns the tuple `(48, 50)`, so without the guard a European user
  entering a valid amount is told "Not a number". Covered by a new test case.

### Changed

- `verify_program.py` now runs programs through the constraint sandbox and takes
  `--target`. A program importing `statistics` fails its tests even though it would
  pass on desktop CPython.
- `lint_ti_python.py` module rules are per-model: `turtle` is an ERROR on the Evo
  (removed) but a WARN on the CE family (separate download). Screen-width warnings use
  the target's width — ~30 columns on an Evo, ~16 on the monochrome `82aep`.
- The `SKILL.md` anti-pattern table now names the check that enforces each row, so it
  is visible which are machine-enforced and which rest on judgement.
- Workflow gained step 0 (preflight) and step 1 (identify the target model).

### Fixed

- Duplicate `E004` findings when an f-string contained a format spec.
- Non-ASCII findings now report the code point (`U+00B0`) instead of a glyph that
  Windows consoles mangle into `?`.

## [1.0.0] - 2026-07-26

### Added

- `SKILL.md` — eight-step workflow from spec to delivered `.py`, with five non-negotiables,
  an anti-pattern table, and a symptom-to-fix troubleshooting table.
- `scripts/lint_ti_python.py` — static checker for TI-Python. Detects f-strings, modules
  absent from the device (including `turtle`, removed on the Evo), illegal AppVar names,
  `if __name__ == "__main__":` guards, CAS-flavoured calls, non-ASCII characters, tabs, and
  print lines wider than the screen. Exits non-zero on any error.
- `scripts/verify_program.py` — executes a program off-calculator with scripted stdin and
  asserts expected output. Supports `expect[]`, `reject[]`, ad-hoc `--inputs`, and `--json`.
- `scripts/make_handout.py` — builds a one-page reference sheet as HTML, then PDF via
  headless Chrome or Edge, degrading to HTML-only when no browser is found.
- `scripts/ti_stubs/ti_system.py` — desktop no-op stub so calculator imports don't crash a
  verification run.
- `assets/program_template.py` — canonical skeleton with the `getnum()` helper that accepts
  expressions such as `6*pi` and `40+8.50`.
- `assets/handout_template.html` — printable A4 two-column layout, self-contained CSS.
- `references/ti-python-language.md` — module allow/deny list, unsupported syntax, memory
  limits, naming rules, and the radians-versus-MODE explanation.
- `references/transfer-options.md` — TI Connect Evo, on-device typing, unit-to-unit USB-C,
  and TI-SmartView Evo, plus what not to use and connection troubleshooting.
- `references/exam-legality.md` — ACT / SAT / AP policy, the CAS boundary, and what exam
  mode does to user programs on the Evo-T.
- `examples/TIPCALC/` — a complete verified deliverable: program, five test cases, handout
  spec, and the generated PDF.

### Notes

- Claims that TI does not document explicitly (`eval()` availability, `cmath`, walrus
  support) are marked **[verify on device]** in the references rather than asserted.
- The ACT "you must clear all calculator memory" claim circulated by third-party test-prep
  sites is not in ACT's published policy; `references/exam-legality.md` corrects it.

[1.0.0]: https://github.com/jovd83/ti84-evo-scripter/releases/tag/v1.0.0
