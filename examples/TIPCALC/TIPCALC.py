# TIPCALC -- tip amount and total from a bill and a tip percentage
# TI-84 Evo / Evo-T / TI-84 Plus CE Python / TI-83 Premium CE Python
#
# Numeric output only. No CAS. Mode does not matter -- arithmetic only.

from math import *


def getnum(msg):
    """Prompt until a number is entered.

    Accepts a plain number (48.50), a decimal comma (48,50), arithmetic
    (40+8.50), or an expression using math names (6*pi).
    """
    while True:
        s = input(msg)
        # European keypads and habits produce "48,50". Without this line
        # eval() would read it as the tuple (48, 50) and reject it.
        if "," in s and "(" not in s:
            s = s.replace(",", ".")
        try:
            return float(eval(s))
        except:
            print("Not a number")


print("TIP CALCULATOR")

bill = getnum("Bill amount: ")
pct = getnum("Tip percent: ")

tip = bill * pct / 100
total = bill + tip

print("Tip:   {:.2f}".format(tip))
print("Total: {:.2f}".format(total))
