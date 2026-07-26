# STATS1 -- one-variable statistics from a typed list
# TI-84 Evo / Evo-T / CE Python / 83 Premium CE Python
#
# Numeric output only. No CAS. Mode does not matter -- arithmetic only.
#
# Quartiles use the TI-84 convention (Moore & McCabe): Q1 is the median
# of the values strictly below the median, excluding the median itself
# when n is odd. This matches the calculator's own 1-Var Stats.

from math import *


def getval(msg):
    """Return a number, or None when the user presses enter on a blank line."""
    while True:
        s = input(msg)
        if s == "":
            return None
        if "," in s and "(" not in s:
            s = s.replace(",", ".")
        try:
            return float(eval(s))
        except:
            print("Not a number")


def med(v):
    n = len(v)
    h = n // 2
    if n % 2 == 1:
        return v[h]
    return (v[h - 1] + v[h]) / 2


print("1-VAR STATS")
print("Blank line = done")

x = []
while True:
    v = getval("x{} = ".format(len(x) + 1))
    if v is None:
        break
    x.append(v)

n = len(x)
if n == 0:
    print("No data")
else:
    x = sorted(x)
    tot = sum(x)
    mean = tot / n
    h = n // 2
    if n == 1:
        # h is 0, so x[:0] and x[1:] are both empty and med() would
        # index off the end. With one value the quartiles are that value.
        q1 = x[0]
        q3 = x[0]
    else:
        q1 = med(x[:h])
        q3 = med(x[n - h:])
    print("n = {}".format(n))
    print("sum  = {:.4f}".format(tot))
    print("mean = {:.4f}".format(mean))
    print("min  = {:.4f}".format(x[0]))
    print("Q1   = {:.4f}".format(q1))
    print("med  = {:.4f}".format(med(x)))
    print("Q3   = {:.4f}".format(q3))
    print("max  = {:.4f}".format(x[-1]))
    print("IQR  = {:.4f}".format(q3 - q1))
    print("rnge = {:.4f}".format(x[-1] - x[0]))

    ss = 0.0
    for v in x:
        ss = ss + (v - mean) ** 2
    print("sigx = {:.4f}".format(sqrt(ss / n)))
    if n > 1:
        print("sx   = {:.4f}".format(sqrt(ss / (n - 1))))
    else:
        print("sx   = n/a")
