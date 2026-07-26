#!/usr/bin/env python3
"""Check what this skill needs, fix what can be fixed, and report what was
done -- so a run never dies on a missing prerequisite.

Two classes of requirement:

  BLOCKING  the skill cannot deliver at all without it.
  DEGRADED  the skill delivers something less complete but still useful.
            Never stop on one of these -- note it and carry on.

Usage:
    python preflight.py
    python preflight.py --target 83pce-python
    python preflight.py --fix              # auto-remediate what is safe
    python preflight.py --fix-system       # also install system packages
    python preflight.py --json

--fix does only reversible, local things: create output directories, install
pip packages into the current environment. It never touches system state.

--fix-system additionally runs the platform package manager (winget / brew /
apt) to install a browser for PDF export. That is a system change, so it is
opt-in: without it, the exact command is printed for a human to run and the
handout falls back to HTML.

Exit codes:
    0  ready (possibly degraded -- read the capabilities block)
    1  a BLOCKING requirement is unmet and could not be fixed
    2  bad invocation
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ti_models  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

MIN_PY = (3, 9)

REQUIRED_FILES = [
    "scripts/lint_ti_python.py",
    "scripts/verify_program.py",
    "scripts/simulate_ti84.py",
    "scripts/_ti_sandbox.py",
    "scripts/make_handout.py",
    "scripts/ti_models.py",
    "scripts/ti_stubs/ti_system.py",
    "assets/program_template.py",
    "assets/handout_template.html",
]

BROWSERS = [
    "chrome", "google-chrome", "google-chrome-stable", "chromium",
    "chromium-browser", "msedge",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]

INSTALL_BROWSER = {
    "Windows": ["winget", "install", "--id", "Google.Chrome",
                "--accept-source-agreements", "--accept-package-agreements"],
    "Darwin": ["brew", "install", "--cask", "google-chrome"],
    "Linux": ["sudo", "apt-get", "install", "-y", "chromium-browser"],
}


class Check:
    def __init__(self, name, klass, ok, detail, remedy=None, remedy_kind=None):
        self.name = name
        self.klass = klass          # BLOCKING | DEGRADED
        self.ok = ok
        self.detail = detail
        self.remedy = remedy        # argv list, or a string instruction
        self.remedy_kind = remedy_kind   # "local" | "system" | "manual"
        self.action = "none"        # none | fixed | failed | skipped

    def as_dict(self):
        return {"name": self.name, "class": self.klass, "ok": self.ok,
                "detail": self.detail, "action": self.action,
                "remedy": (" ".join(self.remedy)
                           if isinstance(self.remedy, list) else self.remedy)}


def find_browser():
    for cand in BROWSERS:
        if os.path.sep in cand:
            if os.path.isfile(cand):
                return cand
        else:
            found = shutil.which(cand)
            if found:
                return found
    return None


def collect(target):
    checks = []

    # --- Python version (BLOCKING, unfixable from inside) -------------
    ver = sys.version_info
    checks.append(Check(
        "python>=%d.%d" % MIN_PY, "BLOCKING",
        ver >= MIN_PY,
        "running %d.%d.%d" % (ver[0], ver[1], ver[2]),
        remedy="Install Python %d.%d or newer and re-run." % MIN_PY,
        remedy_kind="manual"))

    # --- skill files present (BLOCKING) ------------------------------
    missing = [p for p in REQUIRED_FILES
               if not os.path.isfile(os.path.join(ROOT, p))]
    checks.append(Check(
        "skill files", "BLOCKING", not missing,
        "all %d present" % len(REQUIRED_FILES) if not missing
        else "missing: %s" % ", ".join(missing),
        remedy="Re-clone or re-sync the skill directory.",
        remedy_kind="manual"))

    # --- target model supports Python (BLOCKING) ---------------------
    try:
        model = ti_models.get(target)
        if model["python"]:
            checks.append(Check("target has Python App", "BLOCKING", True,
                                "%s (%s)" % (model["label"], model["region"])))
        else:
            checks.append(Check(
                "target has Python App", "BLOCKING", False,
                "%s has no Python App" % model["label"],
                remedy="Pick a Python-capable model (%s), or write TI-BASIC "
                       "instead -- which this skill does not cover."
                       % ", ".join(ti_models.python_capable()),
                remedy_kind="manual"))
    except KeyError as exc:
        checks.append(Check("target model known", "BLOCKING", False, str(exc),
                            remedy="Run lint_ti_python.py --list-targets.",
                            remedy_kind="manual"))
        model = None

    # --- writable cwd (BLOCKING) -------------------------------------
    probe = os.path.join(os.getcwd(), ".ti84-preflight-probe")
    try:
        with open(probe, "w") as fh:
            fh.write("ok")
        os.remove(probe)
        writable = True
        detail = "cwd is writable: %s" % os.getcwd()
    except OSError as exc:
        writable = False
        detail = "cannot write to %s: %s" % (os.getcwd(), exc)
    checks.append(Check("writable output dir", "BLOCKING", writable, detail,
                        remedy="cd to a writable directory.",
                        remedy_kind="manual"))

    # --- sandbox actually works (BLOCKING) ---------------------------
    ok, detail = selftest_sandbox()
    checks.append(Check("simulator sandbox", "BLOCKING", ok, detail,
                        remedy="Check scripts/_ti_sandbox.py is intact.",
                        remedy_kind="manual"))

    # --- browser for PDF (DEGRADED) ----------------------------------
    browser = find_browser()
    checks.append(Check(
        "browser for PDF export", "DEGRADED", browser is not None,
        os.path.basename(browser) if browser
        else "no Chrome or Edge found",
        remedy=INSTALL_BROWSER.get(platform.system()),
        remedy_kind="system"))

    return checks, model


def selftest_sandbox():
    """Prove the import blocker really blocks, using a throwaway program."""
    import tempfile
    src = "import numpy\nprint('should not get here')\n"
    tmp = os.path.join(tempfile.mkdtemp(prefix="ti84pre-"), "SELFTST.py")
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(src)
    try:
        proc = subprocess.run(
            [sys.executable, os.path.join(HERE, "simulate_ti84.py"),
             "--program", tmp, "--target", "evo", "--json"],
            capture_output=True, text=True, timeout=60)
        blob = json.loads(proc.stdout or "{}")
        if blob.get("ok") is False and "numpy" in blob.get("stderr", ""):
            return True, "import blocking verified"
        return False, "blocker did not stop 'import numpy'"
    except Exception as exc:            # noqa: BLE001 - report, never crash
        return False, "selftest failed: %s" % exc
    finally:
        shutil.rmtree(os.path.dirname(tmp), ignore_errors=True)


def remediate(checks, allow_system):
    """Fix what is fixable. Returns a list of human-readable actions taken."""
    log = []
    for c in checks:
        if c.ok or not c.remedy:
            continue

        if c.remedy_kind == "local" and isinstance(c.remedy, list):
            try:
                subprocess.run(c.remedy, check=True, capture_output=True)
                c.ok, c.action = True, "fixed"
                log.append("installed locally: %s" % " ".join(c.remedy))
            except Exception as exc:            # noqa: BLE001
                c.action = "failed"
                log.append("could not fix %s: %s" % (c.name, exc))

        elif c.remedy_kind == "system" and isinstance(c.remedy, list):
            if not allow_system:
                c.action = "skipped"
                log.append("system install available but not run for '%s'. "
                           "Command: %s" % (c.name, " ".join(c.remedy)))
                continue
            if not shutil.which(c.remedy[0]):
                c.action = "failed"
                log.append("%s not available to install %s"
                           % (c.remedy[0], c.name))
                continue
            try:
                subprocess.run(c.remedy, check=True, timeout=900)
                c.ok, c.action = find_browser() is not None, "fixed"
                log.append("installed via %s: %s"
                           % (c.remedy[0], " ".join(c.remedy[1:])))
            except Exception as exc:            # noqa: BLE001
                c.action = "failed"
                log.append("system install of %s failed: %s" % (c.name, exc))

        else:
            c.action = "skipped"
    return log


def capabilities(checks):
    by_name = {c.name: c.ok for c in checks}
    return {
        "can_generate": all(c.ok for c in checks if c.klass == "BLOCKING"),
        "can_lint": True,
        "can_simulate": by_name.get("simulator sandbox", False),
        "can_verify": by_name.get("simulator sandbox", False),
        "handout_format": ("pdf" if by_name.get("browser for PDF export")
                           else "html"),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", default=ti_models.DEFAULT_MODEL)
    ap.add_argument("--fix", action="store_true",
                    help="auto-remediate local, reversible gaps")
    ap.add_argument("--fix-system", action="store_true",
                    help="also run the platform package manager")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    checks, model = collect(args.target)
    log = []
    if args.fix or args.fix_system:
        log = remediate(checks, allow_system=args.fix_system)

    caps = capabilities(checks)
    blocked = [c for c in checks if c.klass == "BLOCKING" and not c.ok]
    degraded = [c for c in checks if c.klass == "DEGRADED" and not c.ok]

    if args.json:
        print(json.dumps({
            "target": model["key"] if model else args.target,
            "checks": [c.as_dict() for c in checks],
            "actions_taken": log,
            "capabilities": caps,
            "ready": not blocked,
        }, indent=2))
        return 1 if blocked else 0

    print("=" * 66)
    print("Preflight -- ti84-evo-scripter")
    if model:
        print("target: %s" % ti_models.describe(model["key"]))
    print("=" * 66)
    for c in checks:
        mark = "ok  " if c.ok else ("MISS" if c.klass == "BLOCKING" else "warn")
        print("  [%s] %-26s %s" % (mark, c.name, c.detail))
        if not c.ok and c.remedy:
            r = " ".join(c.remedy) if isinstance(c.remedy, list) else c.remedy
            print("         -> %s" % r)

    if log:
        print("\n  Actions taken:")
        for entry in log:
            print("    - %s" % entry)

    print("\n  Capabilities:")
    for k, v in caps.items():
        print("    %-18s %s" % (k, v))

    if blocked:
        print("\n  BLOCKED: %s" % ", ".join(c.name for c in blocked))
        print("  Fix the above, then re-run preflight.\n")
        return 1

    if degraded:
        print("\n  Degraded but usable. Continuing is correct -- the handout")
        print("  will be written as HTML instead of PDF. Tell the user that,")
        print("  and give them the print-to-PDF fallback.\n")
    else:
        print("\n  Ready. Nothing missing.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
