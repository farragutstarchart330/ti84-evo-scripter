# Sandbox — five working programs

Five TI-Python programs built with this skill, as a worked demonstration and as
programs genuinely worth putting on a calculator. Requirements are in
[REQUIREMENTS.md](REQUIREMENTS.md).

Built for `evo-t` (TI-84 Evo-T). **All five pass on all six Python-capable
models** — `evo`, `evo-t`, `ce-python`, `ce-t-python`, `83pce-python`, `82aep`.

| Program | Does | Tests | Trig mode |
|---|---|---|---|
| [QUADRT](QUADRT/) | Quadratic roots + discriminant + vertex, all three cases incl. complex | 7 | not applicable |
| [TRISOLV](TRISOLV/) | Triangle solver: SSS, SAS, ASA → sides, angles, area, perimeter | 7 | **degrees in, converted internally** |
| [STATS1](STATS1/) | One-variable stats: five-number summary, IQR, both SDs | 6 | not applicable |
| [COMPINT](COMPINT/) | Compound interest and monthly-savings growth | 7 | not applicable |
| [KINEMAT](KINEMAT/) | Constant acceleration: know 3 of v0/v/a/t/d, get the other 2 | 8 | not applicable |

**35 test cases, all passing. Zero lint warnings.**

Each folder holds `<NAME>.py` (send this one), `tests.json`, `handout.json`,
and the generated `<NAME>-handout.pdf` / `.html`.

## Verify them yourself

```bash
cd sandbox
for p in QUADRT TRISOLV STATS1 COMPINT KINEMAT; do
  python ../scripts/run_checks.py --program $p/$p.py --tests $p/tests.json --target evo-t
done
```

See what any of them prints, without a calculator:

```bash
python ../scripts/simulate_ti84.py --program TRISOLV/TRISOLV.py --target evo-t --inputs 1 3 4 5
python ../scripts/simulate_ti84.py --program STATS1/STATS1.py --interactive
```

## Getting them onto the calculator

Send the `.py` files — never the `.pdf` or `.json`. TI Connect converts `.py` to
the calculator's Python format during the send.

**Evo / Evo-T:**

1. Open `connectevo.ti.com` in Chrome 143+ and accept the terms.
2. Plug the calculator in with a USB-C **data** cable and switch it on.
3. Click **CONNECT TO CALCULATOR**, pick your calculator, click **Connect**.
4. Click **SEND TO CALCULATOR** and select the `.py` files — all five at once is fine.
5. Check each name reads e.g. `QUADRT`, not `PYTHON01`. Send.

**CE family** (`ce-python`, `ce-t-python`, `83pce-python`, `82aep`): same idea but
with the **TI Connect CE** desktop app. The two Connect apps are not
interchangeable.

Then: `[apps]` → **Python App** → highlight the program → **Run**.

## One test per program

Type the bracketed values; the rest is what the screen shows.

| Program | Type | Expect |
|---|---|---|
| QUADRT | `1`, `-1`, `-6` | `D = 25.0000` / `x1 = 3.0000` / `x2 = -2.0000` |
| TRISOLV | `1`, `3`, `4`, `5` | `A = 36.870` / `C = 90.000` / `Area  = 6.000` |
| STATS1 | `2 4 5 7 7 9 12 14`, blank | `n = 8` / `mean = 7.5000` / `sx   = 4.0356` |
| COMPINT | `1`, `1000`, `5`, `12`, `10` | `FV    = 1647.01` / `Grown = 647.01` |
| KINEMAT | `1`, `0`, `9.81`, `3` | `v = 29.430` / `d = 44.145` |

## Quirks that apply to all five

- **Any prompt accepts an expression**, not just a decimal: `40+8.50`, `3/4`,
  `6*pi`, `sqrt(2)`.
- **A decimal comma works**: `9,81` is read as `9.81`. Without the guard in
  `getnum()`, `eval("9,81")` would return the tuple `(9, 81)` and the program
  would say "Not a number" at a perfectly valid entry.
- **Typos never crash it.** Bad input prints `Not a number` and re-asks.
- **No currency or unit symbols** are printed. `€`, `°` and `±` are non-ASCII and
  render unreliably in the calculator font.

## Trig and MODE

Only **TRISOLV** uses trigonometry. Its prompts take **degrees**, and it converts
with `radians()` internally.

Leave the calculator's `MODE` alone in every case. Python's `math` module is
always in radians; the DEGREE / RADIAN setting governs TI-BASIC and the home
screen and does **not** affect Python. That is the single most common wrong
assumption about TI-Python.

## Exam legality

All five are numeric-only and non-CAS — they print numbers, never manipulated
expressions. `QUADRT` prints the numeric roots of a quadratic; it does not
factor or output the quadratic formula as an expression.

Under ACT's published policy the TI-84 family is permitted and CAS is
prohibited; user-written non-CAS programs are not banned. **But** if your exam
requires exam mode (standard across much of Europe, and the reason the Evo-T has
the LED), Press-to-Test **disables user programs** while it is active. The files
survive and return when exam mode is exited. Check your own exam board — see
[../references/exam-legality.md](../references/exam-legality.md).

## Known limitation on the 82aep

The TI-82 Advanced Edition Python has a ~16-column screen. All five programs run
correctly there, but some lines wrap: TRISOLV wraps 4, COMPINT and KINEMAT 2,
QUADRT and STATS1 1 each. Wrapping is cosmetic — no value is lost. To see it:

```bash
python ../scripts/simulate_ti84.py --program TRISOLV/TRISOLV.py --target 82aep --inputs 1 3 4 5
```

Shortening the labels (`Area  =` → `A=`) would fix it at the cost of readability
on the wider screens. Left as-is deliberately, since the Evo is the target.

## How the expected values were established

Every expected value was computed **independently of the programs**, by a
reference script using different formulations — Heron's formula cross-checked
against `ab·sin(C)/2`, quadratic roots cross-checked against `2c/(−b−√D)` plus a
residual check that `ax²+bx+c ≈ 0`, compound interest cross-checked against an
explicit period-by-period loop, standard deviation cross-checked two-pass versus
the sum-of-squares identity. Only values agreeing to 1e-9 across both methods
were written into `tests.json`.

No expected value was adjusted to match program output. Two genuine bugs were
caught this way and fixed before delivery:

- **QUADRT** printed `-0.0000` for the vertex when `b = 0`, because `-0.0/2` is
  negative zero in IEEE arithmetic.
- **STATS1** raised `IndexError` on a single data point, because the quartile
  half-lists were empty.
