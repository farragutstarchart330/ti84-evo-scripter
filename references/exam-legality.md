# Exam legality of TI-84 Evo Python programs

This file summarises published policy. It is guidance, not a ruling. Policies change and
proctors have discretion — tell the user to check the current official policy and, when it
matters, their school or exam centre.

---

## The rule that governs everything here

The disqualifying property is **CAS** — a Computer Algebra System. A calculator or program
that manipulates symbols (solves `2x + 3 = 11` for `x`, factors polynomials, differentiates
`x^2` into `2x`) is CAS-like. A program that does **arithmetic on numbers the user typed**
is not.

Every program this skill produces must stay on the non-CAS side of that line. That is why
"numeric output only" is a non-negotiable in `SKILL.md`.

---

## ACT

Per ACT's published calculator policy:

- The **TI-84 family is permitted**. The prohibited list names models beginning with TI-89 or
  TI-92, and the TI-Nspire CAS. The non-CAS TI-Nspire is permitted.
- **Calculators with built-in or downloaded CAS functionality are prohibited.**
- For programmable calculators, examinees are told to *"remove all documents and remove all
  programs with CAS functionality."* Disabling is not enough — they must be deleted.
- The official policy does **not** require clearing all calculator memory. Several third-party
  test-prep sites claim it does; that claim does not appear in ACT's own policy. Correct the
  user if they repeat it, but note that a proctor can still ask.
- User-written **non-CAS** programs are not prohibited by the written policy.

Practical advice for the user: a `TIPCALC` that multiplies a bill by a percentage is fine.
A program that solves quadratics symbolically and prints `x = (-b ± √(b²-4ac))/2a` as an
expression is asking for trouble. Printing the two numeric roots is the safe form of the same
program.

## SAT (digital, Bluebook)

Approved graphing calculators, TI-84 family included, are permitted throughout the math
section. The same CAS prohibition applies. Note that Bluebook also ships a built-in Desmos
graphing calculator, so a student may not need the device at all.

## AP exams

Calculator rules vary by subject — some AP exams allow graphing calculators for part of the
test only, and a few prohibit them entirely. Direct the user to the policy for their specific
AP subject rather than generalising.

---

## Europe and the Evo-T

This is where the `-T` matters.

- The **TI-84 Evo-T** carries an exam-mode LED on its top edge. Several European examination
  boards require a visible light signal confirming the calculator is in exam mode. Because
  the LED is mandatory for French exams, the Evo-T qualifies there and the plain Evo does not.
- **Exam mode (Press-to-Test) disables user programs.** It does not delete them — apps,
  programs, images, and AppVars are switched off and restored when the calculator leaves exam
  mode.

The practical consequence, stated plainly to the user:

> In a European exam that requires exam mode, your Python program will not be available while
> the calculator is in that mode. The file survives — it comes back when exam mode is exited.
> These programs are for homework, practice, labs, and exams that permit stored programs.

Do not tell a user their program will be usable in an exam. Tell them what the mode does and
let them check their own exam board's rules.

## Entering and exiting exam mode

Entering is a power-off-plus-key-combination sequence rather than a menu item, and the exact
keys differ across the TI-84 generations — point the user at TI's current Press-to-Test guide
for the Evo rather than reciting a combination from a CE-era tutorial.

Exiting restores the disabled files. On earlier TI-84 models, sending any file from a computer
or another calculator also re-enables apps and programs.

---

## What to say in a delivery

Include one short line, matched to the user's context:

- Generic / US: "Numeric-only, no CAS — permitted under the ACT calculator policy for the
  TI-84 family. Check your specific exam's rules before test day."
- European exam context: "Numeric-only and non-CAS, but note that exam mode on the Evo-T
  disables user programs while it is active. Confirm with your exam board."
- Homework / class use: no caveat needed.
