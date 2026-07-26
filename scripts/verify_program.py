#!/usr/bin/env python3
"""Run a TI-Python program off-calculator and check its output.

Feeds scripted answers to the program's input() prompts, captures stdout,
and asserts that each expected string appears. This is what makes
"verified before delivery" a fact rather than a claim.

Usage:
    python verify_program.py --program TIPCALC.py --tests tests.json
    python verify_program.py --program TIPCALC.py --inputs 48.50 18   # ad hoc
    python verify_program.py --program TIPCALC.py --tests tests.json --json

tests.json:
    {
      "program": "TIPCALC.py",
      "cases": [
        {"name": "typical", "inputs": ["48.50", "18"],
         "expect": ["Tip:   8.73", "Total: 57.23"]},
        {"name": "edge: zero", "inputs": ["0", "20"],
         "expect": ["Tip:   0.00"], "reject": ["Traceback"]}
      ]
    }

Fields per case: name, inputs[], expect[] (substrings that must appear),
reject[] (optional substrings that must NOT appear).

Exit codes:
    0  all cases passed
    1  at least one case failed
    2  bad invocation
"""

import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ti_models  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
STUBS = os.path.join(HERE, "ti_stubs")
SANDBOX = os.path.join(HERE, "_ti_sandbox.py")
TIMEOUT = 15


def run_once(program, inputs, model):
    """Execute the program in the constraint sandbox with piped stdin.

    Running through _ti_sandbox.py rather than plain CPython means a test
    cannot pass on a program that imports a module the calculator lacks, and
    the captured output is laid out the way the screen lays it out.

    Returns (stdout, stderr, rc).
    """
    env = dict(os.environ)
    env["PYTHONPATH"] = STUBS + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    allowed = ",".join(sorted(model["modules"] | model["extra_modules"]))
    stdin_data = "".join(str(x) + "\n" for x in inputs)
    try:
        proc = subprocess.run(
            [sys.executable, SANDBOX, os.path.abspath(program), allowed],
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            env=env,
            cwd=os.path.dirname(os.path.abspath(program)) or ".",
        )
    except subprocess.TimeoutExpired:
        return "", ("Timed out after %ds. The program is probably looping on "
                    "an input it never accepts." % TIMEOUT), 124
    return proc.stdout, proc.stderr, proc.returncode


def evaluate(case, stdout, stderr, rc):
    """Returns (passed, list_of_problem_strings)."""
    problems = []

    if "EOFError" in stderr:
        problems.append("program requested more input than the case supplied "
                        "(add values to \"inputs\")")
    elif rc != 0 and stderr.strip():
        first = stderr.strip().splitlines()[-1]
        problems.append("program exited %d: %s" % (rc, first))

    for want in case.get("expect", []):
        if want not in stdout:
            problems.append("missing expected output: %r" % want)
    for bad in case.get("reject", []):
        if bad in stdout:
            problems.append("found rejected output: %r" % bad)

    if not case.get("expect") and not case.get("reject"):
        problems.append("case declares no expect[] or reject[] - nothing "
                        "was actually checked")

    return (not problems), problems


def show_block(label, text):
    if not text.strip():
        return
    print("      %s:" % label)
    for line in text.rstrip().splitlines():
        print("        | %s" % line)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--program", required=True, help="the .py file to run")
    ap.add_argument("--tests", help="JSON file of test cases")
    ap.add_argument("--inputs", nargs="*",
                    help="ad-hoc run: feed these answers and print the output")
    ap.add_argument("--target", default=ti_models.DEFAULT_MODEL,
                    help="calculator model key (default: %s)"
                         % ti_models.DEFAULT_MODEL)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    try:
        model = ti_models.get(args.target)
    except KeyError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    if not model["python"]:
        print("error: %s has no Python App. %s"
              % (model["label"], model["notes"]), file=sys.stderr)
        return 2

    if not os.path.isfile(args.program):
        print("error: no such program: %s" % args.program, file=sys.stderr)
        return 2

    # Ad-hoc mode: just show what the program does.
    if args.inputs is not None and not args.tests:
        stdout, stderr, rc = run_once(args.program, args.inputs, model)
        print("--- stdout ---")
        print(stdout, end="")
        if stderr.strip():
            print("--- stderr ---")
            print(stderr, end="")
        print("--- exit %d ---" % rc)
        return 0 if rc == 0 else 1

    if not args.tests:
        print("error: pass --tests FILE or --inputs ...", file=sys.stderr)
        return 2

    with open(args.tests, "r", encoding="utf-8") as fh:
        spec = json.load(fh)

    cases = spec.get("cases", [])
    if len(cases) < 3:
        print("warning: %d case(s) defined. The skill requires at least 3, "
              "one of them an edge case." % len(cases))

    results = []
    failed = 0

    if not args.json:
        print("=" * 62)
        print("Verifying %s against %s" % (args.program, args.tests))
        print("target: %s" % model["label"])
        print("=" * 62)

    for idx, case in enumerate(cases, 1):
        name = case.get("name", "case %d" % idx)
        inputs = case.get("inputs", [])
        stdout, stderr, rc = run_once(args.program, inputs, model)
        passed, problems = evaluate(case, stdout, stderr, rc)
        if not passed:
            failed += 1

        results.append({
            "name": name,
            "inputs": inputs,
            "passed": passed,
            "problems": problems,
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": rc,
        })

        if args.json:
            continue

        print("  [%s] %s" % ("PASS" if passed else "FAIL", name))
        print("      inputs: %s" % (" | ".join(map(str, inputs)) or "(none)"))
        show_block("screen", stdout)
        if not passed:
            for p in problems:
                print("      -> %s" % p)
            show_block("stderr", stderr)
        print()

    if args.json:
        print(json.dumps({
            "program": args.program,
            "total": len(cases),
            "failed": failed,
            "results": results,
        }, indent=2))
    else:
        print("-" * 62)
        print("  %d/%d passed" % (len(cases) - failed, len(cases)))
        print()

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
