"""Sandbox runner. Invoked by simulate_ti84.py, not directly.

argv[1] = program path
argv[2] = comma-separated allowed module roots

Enforces, at run time, the restrictions the calculator enforces:

  * `import` of anything outside the model's module set raises ImportError
    with the same shape of message the device gives. Implemented by wrapping
    builtins.__import__ so it also catches modules already in sys.modules.
  * `open`, `exec`, `compile` are shadowed in the program's own globals, so
    the program sees them as unavailable while the interpreter's own
    machinery (traceback rendering, linecache) keeps working.
  * `eval` is deliberately left intact -- it is what makes `6*pi` work at a
    prompt, and it exists in the MicroPython lineage.

This is a constraint simulator, not a hardware emulator. It cannot catch
timing, memory-exhaustion, or coprocessor-specific behaviour.
"""

import sys
import builtins

PROGRAM = sys.argv[1]
ALLOWED = set(filter(None, sys.argv[2].split(","))) if len(sys.argv) > 2 else set()

# Read the source before any builtins are shadowed.
with open(PROGRAM, "r", encoding="utf-8") as _fh:
    _SOURCE = _fh.read()

_real_import = builtins.__import__


def _guarded_import(name, glb=None, loc=None, fromlist=(), level=0):
    root = name.split(".")[0]
    if level == 0 and root not in ALLOWED:
        raise ImportError("no module named '%s'" % root)
    return _real_import(name, glb, loc, fromlist, level)


builtins.__import__ = _guarded_import


def _denied(*_args, **_kwargs):
    raise NameError("name is not defined on the calculator")


def _echo_input(prompt=""):
    """input() that echoes the answer, so piped runs render like the screen.

    On the calculator the typed value appears after the prompt and the line
    then breaks. With piped stdin nothing is echoed and no newline is written,
    so every prompt and result would collapse onto one line and look like an
    over-wide display. Echoing restores the real layout.

    Only used when stdin is not a terminal -- an interactive run is already
    echoed by the terminal itself.
    """
    sys.stdout.write(str(prompt))
    sys.stdout.flush()
    line = sys.stdin.readline()
    if line == "":
        raise EOFError("EOF when reading a line")
    line = line.rstrip("\r\n")
    sys.stdout.write(line + "\n")
    sys.stdout.flush()
    return line


_globals = {
    "__name__": "__main__",
    "__file__": PROGRAM,
    "__builtins__": builtins,
    # Shadow in the program's namespace only. Globals are resolved before
    # builtins, so the program is blocked while the interpreter is not.
    "open": _denied,
    "exec": _denied,
    "compile": _denied,
}

if not sys.stdin.isatty():
    _globals["input"] = _echo_input

try:
    _code = compile(_SOURCE, PROGRAM, "exec")
except SyntaxError as exc:
    sys.stderr.write("SyntaxError: %s (line %s)\n" % (exc.msg, exc.lineno))
    sys.exit(1)

exec(_code, _globals)
