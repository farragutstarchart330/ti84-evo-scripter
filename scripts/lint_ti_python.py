#!/usr/bin/env python3
"""Static checker for TI-Python programs, aware of the whole model family.

Catches the failures that only surface once the file is on the calculator:
f-strings, modules the target model does not have, illegal program names,
degree-input trig without radians(), over-wide output, non-ASCII characters,
and CAS-flavoured code that could fail an exam policy.

Usage:
    python lint_ti_python.py TIPCALC.py
    python lint_ti_python.py TIPCALC.py --target 83pce-python
    python lint_ti_python.py TIPCALC.py --json
    python lint_ti_python.py --list-targets

Exit codes:
    0  no errors (warnings may be present)
    1  at least one ERROR
    2  bad invocation, or the target model has no Python App
"""

import argparse
import ast
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ti_models  # noqa: E402

# Modules that do not exist on any TI calculator.
BANNED_MODULES = {
    "numpy", "pandas", "matplotlib", "scipy", "sympy", "statistics",
    "decimal", "fractions", "datetime", "json", "re", "csv", "os",
    "pathlib", "typing", "dataclasses", "itertools", "functools",
    "collections", "argparse", "logging", "secrets", "string",
    "tkinter", "requests", "urllib", "subprocess", "threading",
    "sqlite3", "pickle", "abc", "enum", "io", "copy", "textwrap",
    "unittest", "socket", "hashlib", "base64", "struct", "array",
}

CAS_MARKERS = {"symbols", "Symbol", "solveset", "integrate", "simplify",
               "factor_poly", "nsolve", "dsolve", "series_expand"}

BANNED_BUILTINS = {"open", "exec", "compile", "breakpoint", "__import__",
                   "memoryview", "vars", "globals", "locals", "help",
                   "dir", "input_raw"}

TRIG_FUNCS = {"sin", "cos", "tan", "asin", "acos", "atan", "atan2",
              "sinh", "cosh", "tanh"}

# Filenames the skill must never produce.
CALC_BINARY_EXT = {".8xv", ".8xp", ".8xp2", ".8xv2", ".8xi", ".8ck", ".tns",
                   ".82p", ".83p"}

NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]{0,7}$")
DEGREE_HINT = re.compile(r"deg|degree|graad|degre|grad", re.I)


class Finding:
    def __init__(self, level, code, line, message, fix=""):
        self.level = level
        self.code = code
        self.line = line
        self.message = message
        self.fix = fix

    def as_dict(self):
        return {"level": self.level, "code": self.code, "line": self.line,
                "message": self.message, "fix": self.fix}


def check_name(path, out):
    base = os.path.basename(path)
    stem, ext = os.path.splitext(base)

    if ext.lower() in CALC_BINARY_EXT:
        out.append(Finding(
            "ERROR", "E010", 0,
            "'%s' is a calculator binary format, not source" % ext,
            "Never hand-write these. Deliver a .py file and let TI Connect "
            "convert it on send."))
        return
    if ext.lower() != ".py":
        out.append(Finding(
            "ERROR", "E001", 0,
            "File must have a .py extension, got '%s'" % base,
            "Rename so TI Connect recognises it as a Python program."))
        return
    if not NAME_RE.match(stem):
        out.append(Finding(
            "ERROR", "E002", 0,
            "Program name '%s' is not a legal AppVar name" % stem,
            "Use 1-8 characters, A-Z and 0-9 only, first character a letter. "
            "Otherwise TI Connect silently renames it to PYTHON01."))
    elif stem != stem.upper():
        out.append(Finding(
            "WARN", "W001", 0,
            "Program name '%s' is not uppercase" % stem,
            "It becomes '%s' on the calculator. Rename the file to match."
            % stem.upper()))


def check_text(src, out):
    for i, line in enumerate(src.splitlines(), 1):
        for col, ch in enumerate(line, 1):
            if ord(ch) > 126:
                out.append(Finding(
                    "WARN", "W002", i,
                    "Non-ASCII character U+%04X at column %d renders "
                    "unreliably on the calculator" % (ord(ch), col),
                    "Write 'deg' for the degree sign, '+/-', '~', 'sqrt'. "
                    "Accented characters in prompts are a real risk on "
                    "localised models."))
                break
        if "\t" in line:
            out.append(Finding("WARN", "W003", i, "Tab character in source",
                               "Use two spaces per indent level."))


class Visitor(ast.NodeVisitor):
    def __init__(self, out, model):
        self.out = out
        self.model = model
        self.cols = model["screen_cols"]
        self.available = set(model["modules"])
        self.extra = set(model["extra_modules"])
        self.removed = set(model["removed"])
        self.has_input = False
        self.has_print = False
        self._fstring_lines = set()
        self.star_imports = set()
        self.degree_vars = set()   # variables read from a degree-ish prompt
        self.converted = set()     # variables passed through radians()
        self.trig_on_degree = []   # (lineno, varname)

    # --- imports -----------------------------------------------------
    def _import(self, mod, line):
        root = mod.split(".")[0]
        if root in self.removed:
            self.out.append(Finding(
                "ERROR", "E003", line,
                "Module '%s' was removed on %s" % (root, self.model["label"]),
                "It exists on the TI-84 Plus CE Python but not here. Older "
                "tutorials will show it anyway."))
        elif root in self.available:
            return
        elif root in self.extra:
            self.out.append(Finding(
                "WARN", "W011", line,
                "'%s' is a separate download for %s"
                % (root, self.model["label"]),
                "Not present out of the box. Either send the module to the "
                "calculator too, or avoid it."))
        elif root in BANNED_MODULES:
            self.out.append(Finding(
                "ERROR", "E003", line,
                "Module '%s' does not exist on any TI calculator" % root,
                "Remove it and recompute with math or plain arithmetic."))
        else:
            self.out.append(Finding(
                "WARN", "W005", line,
                "Module '%s' is not in the registry for %s"
                % (root, self.model["label"]),
                "Confirm it exists in the Python App before shipping."))

    def visit_Import(self, node):
        for alias in node.names:
            self._import(alias.name, node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self._import(node.module, node.lineno)
            if any(a.name == "*" for a in node.names):
                self.star_imports.add(node.module)
        self.generic_visit(node)

    # --- f-strings ---------------------------------------------------
    def visit_JoinedStr(self, node):
        # Nested JoinedStr appears inside each FormattedValue format_spec,
        # so report at most once per line.
        if node.lineno not in self._fstring_lines:
            self._fstring_lines.add(node.lineno)
            self.out.append(Finding(
                "ERROR", "E004", node.lineno,
                "f-string -- TI-Python raises SyntaxError on f\"...\"",
                'Rewrite as "{:.2f}".format(x) or "label " + str(x).'))
        self.generic_visit(node)

    def visit_NamedExpr(self, node):
        self.out.append(Finding(
            "WARN", "W006", node.lineno,
            "Walrus operator ':=' may not parse on TI-Python",
            "Split it into a normal assignment."))
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.out.append(Finding("ERROR", "E005", node.lineno,
                                "async def is not supported",
                                "Rewrite as a normal function."))
        self.generic_visit(node)

    def visit_Await(self, node):
        self.out.append(Finding("ERROR", "E005", node.lineno,
                                "await is not supported", "Remove it."))
        self.generic_visit(node)

    # --- degree-input trig without conversion ------------------------
    def visit_Assign(self, node):
        """Remember `angle = getnum("Angle in degrees: ")`."""
        prompt = self._prompt_text(node.value)
        if prompt and DEGREE_HINT.search(prompt):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    self.degree_vars.add(tgt.id)
        self.generic_visit(node)

    @staticmethod
    def _prompt_text(value):
        if not isinstance(value, ast.Call):
            return None
        for arg in value.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                return arg.value
        return None

    def _flag_trig(self, node, name):
        for arg in node.args:
            for sub in ast.walk(arg):
                if isinstance(sub, ast.Name) and sub.id in self.degree_vars:
                    inner = [n for n in ast.walk(arg)
                             if isinstance(n, ast.Call)
                             and (getattr(n.func, "id", None) == "radians"
                                  or getattr(n.func, "attr", None) == "radians")]
                    if not inner:
                        self.trig_on_degree.append((node.lineno, sub.id, name))

    # --- calls -------------------------------------------------------
    def visit_Call(self, node):
        fn = node.func
        name = getattr(fn, "id", None) or getattr(fn, "attr", None)

        if name == "input":
            self.has_input = True
        if name == "print":
            self.has_print = True
            self._check_print_width(node)
        if name in TRIG_FUNCS:
            self._flag_trig(node, name)
        if name in BANNED_BUILTINS:
            self.out.append(Finding(
                "ERROR", "E006", node.lineno,
                "'%s()' is unavailable on the calculator" % name,
                "There is no filesystem or dynamic compilation in the "
                "Python App."))
        if name in CAS_MARKERS:
            self.out.append(Finding(
                "ERROR", "E007", node.lineno,
                "'%s()' looks like symbolic algebra (CAS)" % name,
                "Exam policies prohibit CAS. Compute and print numbers "
                "instead of manipulating expressions."))
        self.generic_visit(node)

    def _check_print_width(self, node):
        width = 0
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                width += len(arg.value)
            elif (isinstance(arg, ast.Call)
                  and getattr(arg.func, "attr", "") == "format"):
                base = arg.func.value
                if isinstance(base, ast.Constant) and isinstance(base.value, str):
                    literal = re.sub(r"\{[^}]*\}", "", base.value)
                    width += len(literal) + 8 * base.value.count("{")
            else:
                width += 8
        if width > self.cols:
            self.out.append(Finding(
                "WARN", "W007", node.lineno,
                "Printed line is about %d chars; %s wraps near %d"
                % (width, self.model["label"], self.cols),
                "Shorten the label."))

    def visit_If(self, node):
        test = node.test
        if (isinstance(test, ast.Compare)
                and isinstance(test.left, ast.Name)
                and test.left.id == "__name__"):
            self.out.append(Finding(
                "ERROR", "E008", node.lineno,
                "'if __name__ == \"__main__\":' guard present",
                "The calculator runs a program by importing it, so the guard "
                "suppresses everything. Move the body to top level."))
        self.generic_visit(node)

    def finish(self):
        for line, var, fn in self.trig_on_degree:
            self.out.append(Finding(
                "WARN", "W010", line,
                "%s(%s) where '%s' was read from a degrees prompt"
                % (fn, var, var),
                "Python's math module is always radians -- the calculator's "
                "MODE setting does not change it. Wrap it: %s(radians(%s))."
                % (fn, var)))


def lint_file(path, model):
    out = []
    check_name(path, out)

    try:
        with open(path, "r", encoding="utf-8") as fh:
            src = fh.read()
    except OSError as exc:
        out.append(Finding("ERROR", "E000", 0, "Cannot read file: %s" % exc))
        return out

    check_text(src, out)

    try:
        tree = ast.parse(src, filename=path)
    except SyntaxError as exc:
        out.append(Finding("ERROR", "E009", exc.lineno or 0,
                           "SyntaxError: %s" % exc.msg,
                           "The file is not valid Python 3."))
        return out

    v = Visitor(out, model)
    v.visit(tree)
    v.finish()

    if not v.has_print:
        out.append(Finding("WARN", "W008", 0, "Program never calls print()",
                           "Nothing will appear on screen."))
    if not v.has_input:
        out.append(Finding("WARN", "W009", 0, "Program never calls input()",
                           "Intentional for a constant-output program; "
                           "otherwise the prompts are missing."))

    out.sort(key=lambda f: (f.line, f.code))
    return out


def report(path, findings, model, use_json):
    if use_json:
        return {"file": path, "target": model["key"],
                "findings": [f.as_dict() for f in findings]}

    errors = [f for f in findings if f.level == "ERROR"]
    warns = [f for f in findings if f.level == "WARN"]

    print("=" * 66)
    print("TI-Python lint: %s" % path)
    print("target: %s (%s)  screen ~%d cols"
          % (model["label"], model["region"], model["screen_cols"]))
    print("=" * 66)
    if not findings:
        print("  clean - no errors, no warnings")
    for f in findings:
        loc = ("line %d" % f.line) if f.line else "file"
        print("  [%s %s] %s: %s" % (f.level, f.code, loc, f.message))
        if f.fix:
            print("      fix: %s" % f.fix)
    print("-" * 66)
    print("  %d error(s), %d warning(s)" % (len(errors), len(warns)))
    print()
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", help=".py program(s) to check")
    ap.add_argument("--target", default=ti_models.DEFAULT_MODEL,
                    help="calculator model key (default: %s)"
                         % ti_models.DEFAULT_MODEL)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--list-targets", action="store_true")
    args = ap.parse_args(argv)

    if args.list_targets:
        ti_models.__name__  # keep the import meaningful for linters
        for key in sorted(ti_models.MODELS):
            m = ti_models.MODELS[key]
            print("%-14s %-36s %-16s %s"
                  % (key, m["label"], m["region"],
                     "Python" if m["python"] else "NO PYTHON APP"))
        return 0

    if not args.files:
        ap.error("give at least one .py file, or use --list-targets")

    try:
        model = ti_models.get(args.target)
    except KeyError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2

    if not model["python"]:
        print("error: %s has no Python App. %s"
              % (model["label"], model["notes"]), file=sys.stderr)
        print("Python-capable targets: %s"
              % ", ".join(ti_models.python_capable()), file=sys.stderr)
        return 2

    payload = []
    worst = 0
    for path in args.files:
        findings = lint_file(path, model)
        blob = report(path, findings, model, args.json)
        if blob:
            payload.append(blob)
        if any(f.level == "ERROR" for f in findings):
            worst = 1

    if args.json:
        print(json.dumps({"results": payload, "exit_code": worst}, indent=2))
    return worst


if __name__ == "__main__":
    sys.exit(main())
