# Sandbox: five programs — requirements

Five TI-Python programs chosen for coverage of what students actually get tested
on, built with `ti84-evo-scripter` as a working demonstration of the skill.

**Target model:** `evo-t` (TI-84 Evo-T). All five also run unchanged on `evo`,
`ce-python`, `ce-t-python` and `83pce-python`. The `82aep` has a ~16-column
screen and will wrap some labels — noted per program where it matters.

## Why these five

Grounded in the ACT Math blueprint (Preparing for Higher Mathematics ~80%,
Integrating Essential Skills ~20%) and in what the TI program archives show
students actually download — quadratic solvers and triangle solvers are the two
largest categories on ticalc.org.

| # | Program | Curriculum area | ACT weight | Why a program beats doing it by hand |
|---|---|---|---|---|
| 1 | `QUADRT` | Algebra — quadratics | Algebra ~12–15% | Three discriminant cases, sign errors everywhere |
| 2 | `TRISOLV` | Geometry + basic trig | Geometry, largest single block | Law of cosines by hand is slow and error-prone |
| 3 | `STATS1` | Statistics | Stats & Prob ~8–12% | Quartiles and SD over 8+ values is pure tedium |
| 4 | `COMPINT` | Percentages, exponential growth | Essential Skills ~20% | Repeated compounding is unreasonable by hand |
| 5 | `KINEMAT` | Physics (secondary school) | — | Picking the right equation is the hard part |

## Requirements common to all five

| ID | Requirement |
|---|---|
| R1 | Numeric output only. No symbolic algebra, no CAS. Print numbers, never manipulated expressions. |
| R2 | Program name 1–8 chars, `A–Z0–9`, first char a letter, uppercase. |
| R3 | No f-strings. Format with `"{:.Nf}".format(x)`. |
| R4 | Every input read through `getnum()`, which accepts `12.5`, `12,5`, `40+8.50` and `6*pi`. |
| R5 | Invalid input re-prompts; the program never crashes on a typo. |
| R6 | Printed lines ≤ 30 characters (Evo width). |
| R7 | Plain ASCII only — `deg`, `+/-`, `sqrt`, no `°` or `≈`. |
| R8 | No `if __name__ == "__main__":`. Code at module top level. |
| R9 | Every value printed carries a label. |
| R10 | Domain guards: reject division by zero, impossible triangles, negative radicands — with a message, not a traceback. |
| R11 | ≥ 4 test cases per program, at least one an edge case. All must pass `run_checks.py`. |
| R12 | Trig-mode statement in the delivery: degrees converted with `radians()` internally; `MODE` does not affect Python. |

## Per-program requirements

### 1. QUADRT — quadratic roots

Solves `ax^2 + bx + c = 0` numerically.

- Prompts: `a`, `b`, `c`. Reject `a = 0` and re-prompt (it is not quadratic).
- Compute `D = b^2 - 4ac`, print it to 4 decimals.
- `D > 0`: two distinct real roots, `x1` and `x2`, 4 decimals.
- `D = 0`: one repeated root, labelled as such.
- `D < 0`: no real roots. Print the complex pair as real part `+/-` imaginary part `i`.
- Also print the vertex `x = -b/(2a)` — useful for graphing and free to compute.
- **Legality:** prints numeric roots only. It does not factor, rearrange, or output the quadratic formula as an expression.

### 2. TRISOLV — triangle solver

Menu-driven, three modes. All angles in **degrees** at the interface, radians internally.

- Mode `1` SSS: three sides → three angles (law of cosines), area (Heron), perimeter.
  Reject a triangle violating the inequality.
- Mode `2` SAS: two sides + included angle → third side (law of cosines), remaining angles, area `= ab·sin(C)/2`, perimeter.
- Mode `3` ASA: two angles + the included side → third angle, remaining sides (law of sines), area, perimeter.
  Reject if the two angles sum to ≥ 180.
- Output all three sides (3 dp) and all three angles in degrees (3 dp), plus area and perimeter.
- Reject any non-positive side or angle.

### 3. STATS1 — one-variable statistics

- Reads values one per prompt. **Empty input ends the list.**
- Reports: `n`, `sum`, `mean`, `min`, `Q1`, `median`, `Q3`, `max`, `IQR`, `range`, sample SD `sx`, population SD `sigx`.
- **Quartiles must use the TI-84 convention** (Moore & McCabe): the median of the values strictly below the median, excluding the median itself when `n` is odd. This is what the calculator's own `1-Var Stats` reports, so the program must agree with it.
- `n = 1`: print `sx = n/a` rather than dividing by zero.
- `n = 0`: say "No data" and stop cleanly.
- Values printed to 4 decimals; `n` as an integer.
- **82aep note:** this one has the most lines of output and will scroll on a 16-column screen. Acceptable.

### 4. COMPINT — compound interest and savings

Menu-driven, two modes. Rate entered as a percentage (`5`, not `0.05`).

- Mode `1` lump sum: principal `P`, annual rate `r%`, compounds per year `n`, years `t`.
  `FV = P(1 + r/100n)^(nt)`. Print `FV` and interest earned, 2 decimals.
- Mode `2` monthly deposits: monthly deposit `D`, annual rate `r%`, years `t`.
  `FV = D·((1+i)^m − 1)/i` with `i = r/1200`, `m = 12t`.
  Print `FV`, total deposited, interest earned.
- **Zero-rate edge case is mandatory:** at `r = 0` the annuity formula divides by zero. Fall back to `FV = D·m`.
- Reject `n <= 0`, negative `t`, negative `P`.
- Currency to 2 decimals, no currency symbol (`€` is non-ASCII).

### 5. KINEMAT — constant-acceleration solver

Menu of which three quantities are known; solves for the other two. SI units, no unit conversion.

| Mode | Known | Solves |
|---|---|---|
| `1` | `v0`, `a`, `t` | `v = v0 + at`, `d = v0·t + at²/2` |
| `2` | `v0`, `v`, `t` | `a = (v − v0)/t`, `d = (v0 + v)t/2` |
| `3` | `v0`, `v`, `a` | `t = (v − v0)/a`, `d = (v² − v0²)/2a` |
| `4` | `v0`, `a`, `d` | `v = sqrt(v0² + 2ad)`, `t = (v − v0)/a` |

- Mode 3 must reject `a = 0`. Mode 4 must reject `a = 0` and a negative radicand `v0² + 2ad < 0`, with a readable message.
- Negative values are legal throughout (deceleration, downward motion) and must not be rejected.
- Results to 3 decimals.

## Verification standard

Each program's expected values were computed **independently** of the program —
by a separate reference script using different formulations (e.g. Heron's
formula cross-checked against `ab·sin(C)/2`, compound interest cross-checked
against an explicit period-by-period loop). Only values that agreed to 1e-9
across both methods were written into `tests.json`.

No expected value was ever adjusted to match program output.
