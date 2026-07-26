# {PROGNAME} -- {one-line description of what it calculates}
# TI-84 Evo / Evo-T / TI-84 Plus CE Python  (Python App)
#
# Numeric output only. No CAS, no symbolic algebra.
# No f-strings: TI-Python raises SyntaxError on f"...".
#
# Delete this template's unused parts. Keep the file short --
# calculator memory and typing effort both reward brevity.

from math import *


def getnum(msg):
    """Prompt until a number is entered.

    Accepts a plain number (48.50), a decimal comma (48,50), arithmetic
    (40+8.50), or any expression using names in scope (6*pi, sqrt(2)).

    Keep the comma line on any calculator sold outside the US. Without
    it, eval("48,50") returns the tuple (48, 50) and the value is
    rejected -- which reads to the user as "my calculator is broken".

    If a device reports that eval() is unavailable, replace the body
    with:  return float(input(msg).replace(",", "."))
    """
    while True:
        s = input(msg)
        if "," in s and "(" not in s:
            s = s.replace(",", ".")
        try:
            return float(eval(s))
        except:
            print("Not a number")


def getpos(msg):
    """Same as getnum(), but rejects zero and negatives."""
    while True:
        v = getnum(msg)
        if v > 0:
            return v
        print("Must be > 0")


# ---- program starts here -------------------------------------------
# Keep executable code at module top level.
# Do NOT wrap it in `if __name__ == "__main__":` -- the calculator runs
# a program by importing it, and the guard would suppress everything.

print("{TITLE}")                       # <= 26 chars fits without wrapping

a = getnum("{Prompt 1}: ")             # state units in the prompt text
b = getnum("{Prompt 2}: ")

result = a * b                         # <-- the actual calculation

print("{Label}: {:.2f}".format(result))
