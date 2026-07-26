# Getting a `.py` file onto a TI-84 Evo / Evo-T

The calculator **does** accept uploaded program files over its USB-C port. There are four
practical paths. Ask the user which they want; default to TI Connect Evo.

Always hand over a plain `.py` file. Never author a `.8xv`, `.8xp`, or `.8xp2` by hand —
that conversion is TI Connect's job, and a hand-built binary will be rejected or corrupt.

---

## Option 1 — TI Connect Evo (default, recommended)

Free, web-based, no sign-in. It converts `.py` to the calculator's Python AppVar format
automatically during the send.

**Requirements**

| Item | Minimum |
|---|---|
| Browser | Chrome 143 or newer (WebUSB) |
| OS | Windows 11 64-bit, macOS 15 or 26, ChromeOS 143+ |
| RAM | 2 GB minimum, 4 GB recommended |
| Screen | 9.5" or larger, 1024 × 768 |
| Cable | USB-C **data** cable — charge-only cables will not enumerate |

**Steps**

1. Open **`connectevo.ti.com`** in Chrome.
2. Accept the cookie notice and TI's terms.
3. Plug the calculator into the computer with the USB-C cable and turn it on.
4. Click **CONNECT TO CALCULATOR**, pick your calculator in the browser's device dialog, click **Connect**.
5. Go to the **Send Files** view, click **SEND TO CALCULATOR**, and choose your `.py` file.
6. Confirm the name shown under *NAME ON CALCULATOR*. If it reads `PYTHON01` instead of your
   program name, cancel — the filename broke the naming rules. Rename to 1–8 characters,
   first character a letter, and send again.
7. On the calculator: `[apps]` → **Python App** → highlight the program → **Run**.

**Retrieving files** uses the same page in reverse: tick the file(s), click **SEND TO COMPUTER**.

---

## Option 2 — Type it directly on the calculator

No cable, no computer. Realistic up to about 30 lines.

1. `[apps]` → **Python App** → **New**.
2. Enter the program name (1–8 characters, letter first) and confirm.
3. Type the source in the editor. The soft keys and `[2nd]` menus insert keywords, `:` and
   quotes, so you rarely spell out `import` or `print` by hand.
4. Indentation is manual — use two spaces consistently.
5. **Run** from the editor to test.

When the user picks this path, hand them a shortened variant: single-letter variable names,
minimal comments, short prompt strings. Typing is the bottleneck, not memory.

---

## Option 3 — Unit-to-unit over USB-C

Copies an existing program from one Evo to another. Useful in a classroom once one device
has the file.

1. Connect the two calculators with a USB-C to USB-C cable.
2. On the **receiving** unit, put it in receive mode from the link/send menu.
3. On the **sending** unit, select the Python AppVar and send.

Both units must be Evo-family. An Evo cannot pull a program from a TI-84 Plus CE this way.

---

## Option 4 — TI-SmartView Evo

TI's emulator software for teachers and classroom projection. Load the `.py` into the emulated
calculator, then push it to a physically connected unit. Choose this only if the user already
runs SmartView; it is not free.

---

## What not to use

| Tool | Why not |
|---|---|
| **TI Connect CE** (desktop) | The previous-generation app for the TI-84 Plus CE family. It does not serve the Evo — use TI Connect Evo. |
| TILP / WebTILP / third-party linkers | Built for the CE-era protocol. Evo support is unverified; do not recommend. |
| Hand-built `.8xv` / `.8xp2` files | Wrong layer, and the Evo's BASIC format changed. Ship `.py`. |
| Emailing the file to the calculator | There is no network stack on the device. |

---

## Connection troubleshooting

| Symptom | Fix |
|---|---|
| Browser shows no devices in the picker | Charge-only cable, or a non-Chrome browser. Swap the cable, use Chrome 143+. |
| "WebUSB not supported" | Firefox or Safari. WebUSB is Chrome/Edge/ChromeOS only. |
| Calculator connects but the send fails | Turn the calculator on and leave it on the home screen before sending. |
| File lands as `PYTHON01` | Filename broke the 1–8 char / letter-first rule. Rename and re-send. |
| Program does not appear in the Python App | It went to the wrong variable type. Confirm the source file's extension is `.py`, not `.py.txt`. |
| Program vanished after an exam | Exam mode disables user programs. Exit exam mode; see `exam-legality.md`. |
| Send works, program errors instantly | Lint it: `python scripts/lint_ti_python.py <NAME>.py`. Usually an f-string or a desktop-only import. |
