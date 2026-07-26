#!/usr/bin/env python3
"""One gate for the whole correctness loop: lint -> simulate -> verify.

Runs the three checks in dependency order, stops at the first that fails, and
emits a single NEXT ACTION telling the caller exactly what to fix. Designed so
an agent can loop:

    run_checks.py  ->  read NEXT ACTION  ->  edit the program  ->  run again

until it prints ALL CHECKS PASSED. Each stage is cheap, so looping is cheap.

Usage:
    python run_checks.py --program TIPCALC.py --tests tests.json
    python run_checks.py --program TIPCALC.py --tests tests.json --target 82aep
    python run_checks.py --program TIPCALC.py --tests tests.json --json

Exit codes:
    0  every stage passed -- safe to deliver
    1  a stage failed -- read next_action and fix
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
MAX_ADVISED_ITERATIONS = 5


def call(script, extra):
    cmd = [sys.executable, os.path.join(HERE, script)] + extra
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    return proc.returncode, proc.stdout, proc.stderr


def stage_lint(program, target):
    rc, out, err = call("lint_ti_python.py",
                        [program, "--target", target, "--json"])
    try:
        blob = json.loads(out[out.index("{"):]) if "{" in out else {}
    except ValueError:
        blob = {}
    findings = []
    for res in blob.get("results", []):
        findings.extend(res.get("findings", []))
    errors = [f for f in findings if f["level"] == "ERROR"]
    warns = [f for f in findings if f["level"] == "WARN"]

    if rc == 2:
        return False, {"errors": [], "warnings": [], "fatal": err.strip()}, \
            err.strip() or "lint could not run"
    if errors:
        first = errors[0]
        action = ("Fix lint %s at line %s: %s -- %s"
                  % (first["code"], first["line"], first["message"],
                     first["fix"]))
        return False, {"errors": errors, "warnings": warns}, action
    return True, {"errors": [], "warnings": warns}, None


def stage_simulate(program, target, tests):
    """Run the first test case's inputs through the constraint sandbox."""
    inputs = []
    if tests and os.path.isfile(tests):
        with open(tests, "r", encoding="utf-8") as fh:
            cases = json.load(fh).get("cases", [])
        if cases:
            inputs = [str(x) for x in cases[0].get("inputs", [])]

    rc, out, err = call("simulate_ti84.py",
                        ["--program", program, "--target", target,
                         "--json"] + (["--inputs"] + inputs if inputs else []))
    try:
        blob = json.loads(out[out.index("{"):]) if "{" in out else {}
    except ValueError:
        blob = {}

    if blob.get("precheck"):
        return False, blob, ("The device's parser would reject this: %s"
                             % "; ".join(blob["precheck"]))
    if not blob.get("ok", False):
        advice = blob.get("advice") or (blob.get("stderr", "") or err).strip()
        tail = advice.splitlines()[-1] if advice else "simulation failed"
        return False, blob, "Simulation failed: %s" % tail
    if blob.get("wrapped_lines"):
        return True, blob, None      # a warning, not a blocker
    return True, blob, None


def stage_verify(program, tests, target):
    if not tests or not os.path.isfile(tests):
        return False, {}, ("No tests.json. Write at least 3 cases including "
                           "one edge case, then re-run.")
    rc, out, err = call("verify_program.py",
                        ["--program", program, "--tests", tests,
                         "--target", target, "--json"])
    try:
        blob = json.loads(out[out.index("{"):]) if "{" in out else {}
    except ValueError:
        blob = {}

    total = blob.get("total", 0)
    if total < 3:
        return False, blob, ("Only %d test case(s). The skill requires at "
                             "least 3, one of them an edge case." % total)
    failures = [r for r in blob.get("results", []) if not r.get("passed")]
    if failures:
        f = failures[0]
        why = "; ".join(f.get("problems", [])) or "unknown"
        return False, blob, ("Test '%s' failed with inputs %s: %s. Fix the "
                             "program -- never edit the expected value to "
                             "match a wrong result."
                             % (f.get("name"), f.get("inputs"), why))
    return True, blob, None


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--program", required=True)
    ap.add_argument("--tests")
    ap.add_argument("--target", default=ti_models.DEFAULT_MODEL)
    ap.add_argument("--iteration", type=int, default=1,
                    help="which loop pass this is, for the advisory cap")
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

    stages = []
    next_action = None

    ok, detail, action = stage_lint(args.program, args.target)
    stages.append({"stage": "lint", "passed": ok, "detail": detail})
    if not ok:
        next_action = action
    else:
        ok, detail, action = stage_simulate(args.program, args.target,
                                            args.tests)
        stages.append({"stage": "simulate", "passed": ok, "detail": detail})
        if not ok:
            next_action = action
        else:
            ok, detail, action = stage_verify(args.program, args.tests,
                                              args.target)
            stages.append({"stage": "verify", "passed": ok, "detail": detail})
            if not ok:
                next_action = action

    passed = next_action is None
    warns = stages[0]["detail"].get("warnings", []) if stages else []
    wrapped = 0
    for s in stages:
        if s["stage"] == "simulate":
            wrapped = s["detail"].get("wrapped_lines", 0)

    if args.json:
        print(json.dumps({
            "program": args.program,
            "target": model["key"],
            "iteration": args.iteration,
            "passed": passed,
            "stages": stages,
            "warnings": warns,
            "wrapped_lines": wrapped,
            "next_action": next_action,
            "deliverable": passed,
        }, indent=2))
        return 0 if passed else 1

    print("=" * 66)
    print("Check gate -- %s on %s  (iteration %d)"
          % (os.path.basename(args.program), model["label"], args.iteration))
    print("=" * 66)
    for s in stages:
        print("  [%s] %s" % ("PASS" if s["passed"] else "FAIL", s["stage"]))
    for s in ("lint", "simulate", "verify"):
        if s not in [x["stage"] for x in stages]:
            print("  [ -- ] %s (not reached)" % s)

    if warns:
        print("\n  Lint warnings (not blocking, but review them):")
        for w in warns[:8]:
            print("    %s line %s: %s" % (w["code"], w["line"], w["message"]))
    if wrapped:
        print("\n  %d printed line(s) wrap on this model's screen. Shorten "
              "the labels." % wrapped)

    print("-" * 66)
    if passed:
        print("  ALL CHECKS PASSED -- safe to deliver.")
        print("  Paste the verify output into the reply as evidence.")
    else:
        print("  NEXT ACTION:")
        print("    %s" % next_action)
        if args.iteration >= MAX_ADVISED_ITERATIONS:
            print("\n  This is iteration %d. If the same stage keeps failing,"
                  % args.iteration)
            print("  stop looping and tell the user what is stuck and why.")
        else:
            print("\n  Fix that, then re-run with --iteration %d"
                  % (args.iteration + 1))
    print()
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
