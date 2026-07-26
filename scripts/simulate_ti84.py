#!/usr/bin/env python3
"""Run a TI-Python program under the calculator's constraints and draw the
screen, so mistakes surface before anyone plugs in a cable.

WHY THIS EXISTS -- there is no emulator that runs TI-Python.
CEmu, the standard third-party TI-84 Plus CE emulator, does not emulate the
Atmel ATSAMD21 coprocessor that executes Python on the CE Python models; its
experimental branch is not usable, and its own maintainers point people at
TI's paid SmartView for Python work. No emulator exists for the Evo at all.
SmartView is GUI-only and cannot be scripted.

So this simulates the *constraints* rather than the silicon:

  * module imports outside the target model's set raise ImportError
  * f-strings are rejected before the run, as the device's parser would
  * open/exec/compile are unavailable to the program
  * output is drawn in a screen frame at the model's width, so wrapping and
    over-long labels are visible

It cannot reproduce timing, memory exhaustion, or ti_plotlib/ti_hub/ti_rover
hardware behaviour. Programs using those must still be tried on the device.

Usage:
    python simulate_ti84.py --program TIPCALC.py --inputs 48.50 18
    python simulate_ti84.py --program TIPCALC.py --target 82aep --inputs 100 15
    python simulate_ti84.py --program TIPCALC.py --interactive
    python simulate_ti84.py --program TIPCALC.py --inputs 0 20 --json

Exit codes:
    0  ran to completion with no error
    1  the program raised, or a constraint was violated
    2  bad invocation, or the target model has no Python App
"""

import argparse
import ast
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ti_models  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SANDBOX = os.path.join(HERE, "_ti_sandbox.py")
STUBS = os.path.join(HERE, "ti_stubs")
TIMEOUT = 15


def precheck(path):
    """Reject what the device's parser would reject, before running."""
    problems = []
    with open(path, "r", encoding="utf-8") as fh:
        src = fh.read()
    try:
        tree = ast.parse(src, filename=path)
    except SyntaxError as exc:
        return ["SyntaxError: %s (line %s)" % (exc.msg, exc.lineno)]

    seen = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr) and node.lineno not in seen:
            seen.add(node.lineno)
            problems.append(
                "line %d: f-string -- the calculator's parser raises "
                "SyntaxError here" % node.lineno)
    return problems


def run(path, model, inputs, interactive=False):
    env = dict(os.environ)
    env["PYTHONPATH"] = STUBS + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    allowed = ",".join(sorted(model["modules"] | model["extra_modules"]))
    cmd = [sys.executable, SANDBOX, os.path.abspath(path), allowed]
    cwd = os.path.dirname(os.path.abspath(path)) or "."

    if interactive:
        proc = subprocess.run(cmd, env=env, cwd=cwd)
        return "", "", proc.returncode

    try:
        proc = subprocess.run(
            cmd,
            input="".join(str(x) + "\n" for x in inputs),
            capture_output=True, text=True, timeout=TIMEOUT,
            env=env, cwd=cwd)
    except subprocess.TimeoutExpired:
        return "", ("Timed out after %ds -- probably looping on an input it "
                    "never accepts." % TIMEOUT), 124
    return proc.stdout, proc.stderr, proc.returncode


def draw_screen(text, cols, label):
    """Render output inside a fixed-width frame, marking wrapped lines."""
    top = "+" + "-" * (cols + 2) + "+"
    lines = []
    wrapped = 0
    for raw in text.split("\n"):
        if raw == "":
            lines.append("")
            continue
        if len(raw) <= cols:
            lines.append(raw)
            continue
        wrapped += 1
        while raw:
            lines.append(raw[:cols])
            raw = raw[cols:]

    out = ["  %s" % top, "  |%s|" % label.center(cols + 2)[:cols + 2],
           "  %s" % top]
    for line in lines:
        out.append("  | %s |" % line.ljust(cols))
    out.append("  %s" % top)
    if wrapped:
        out.append("  ^ %d line(s) exceeded %d columns and wrapped."
                   % (wrapped, cols))
    return "\n".join(out), wrapped


def explain_stderr(stderr):
    """Translate a sandbox failure into device-flavoured advice."""
    if "EOFError" in stderr:
        return ("The program asked for more input than you supplied. Add "
                "values to --inputs.")
    if "ImportError" in stderr:
        mod = stderr.rsplit("'", 2)
        name = mod[-2] if len(mod) >= 2 else "?"
        return ("Blocked import '%s'. That module is not on this model. "
                "Recompute with math or plain arithmetic." % name)
    if "NameError" in stderr and "not defined on the calculator" in stderr:
        return ("The program called open(), exec() or compile(). None exist "
                "in the Python App.")
    if "ZeroDivisionError" in stderr:
        return ("Division by zero reached the user. Guard the input or the "
                "denominator.")
    if "SyntaxError" in stderr:
        return "The calculator's parser would reject this file."
    return ""


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--program", required=True)
    ap.add_argument("--target", default=ti_models.DEFAULT_MODEL)
    ap.add_argument("--inputs", nargs="*", default=[],
                    help="answers fed to the program's prompts, in order")
    ap.add_argument("--interactive", action="store_true",
                    help="type the answers yourself, as on the device")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if not os.path.isfile(args.program):
        print("error: no such program: %s" % args.program, file=sys.stderr)
        return 2

    try:
        model = ti_models.get(args.target)
    except KeyError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2

    if not model["python"]:
        print("error: %s has no Python App. %s"
              % (model["label"], model["notes"]), file=sys.stderr)
        return 2

    problems = precheck(args.program)
    if problems:
        if args.json:
            print(json.dumps({"program": args.program, "target": model["key"],
                              "ok": False, "precheck": problems}, indent=2))
        else:
            print("SIMULATION REFUSED -- the device would not parse this:")
            for p in problems:
                print("  %s" % p)
        return 1

    if args.interactive:
        print("Simulating %s -- %s. Ctrl+C to stop.\n"
              % (os.path.basename(args.program), model["label"]))
        _, _, rc = run(args.program, model, [], interactive=True)
        return 0 if rc == 0 else 1

    stdout, stderr, rc = run(args.program, model, args.inputs)
    screen, wrapped = draw_screen(stdout.rstrip("\n"), model["screen_cols"],
                                  model["label"])
    advice = explain_stderr(stderr)
    ok = rc == 0 and not stderr.strip()

    if args.json:
        print(json.dumps({
            "program": args.program,
            "target": model["key"],
            "ok": ok,
            "exit_code": rc,
            "inputs": args.inputs,
            "stdout": stdout,
            "stderr": stderr,
            "wrapped_lines": wrapped,
            "advice": advice,
        }, indent=2))
        return 0 if ok else 1

    print("Simulated on %s (screen ~%d cols, %s)"
          % (model["label"], model["screen_cols"], model["engine"]))
    print("Inputs: %s\n" % (" | ".join(map(str, args.inputs)) or "(none)"))
    print(screen)
    print()
    if stderr.strip():
        print("  RUNTIME ERROR:")
        for line in stderr.rstrip().splitlines()[-6:]:
            print("    %s" % line)
        if advice:
            print("\n  -> %s" % advice)
        print()
    elif wrapped:
        print("  Ran clean, but shorten the labels above.\n")
    else:
        print("  Ran clean. No constraint violations.\n")

    print("  Note: constraint simulation, not hardware emulation. No public")
    print("  emulator runs TI-Python. Timing, memory limits and ti_plotlib /")
    print("  ti_hub / ti_rover behaviour still need the real device.\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
