# QUADRT -- numeric roots of a*x^2 + b*x + c = 0
# TI-84 Evo / Evo-T / CE Python / 83 Premium CE Python
#
# Numeric output only. No CAS: it prints the roots as numbers, it does
# not factor or rearrange the equation.
# Mode does not matter -- arithmetic only, no trig.

from math import *


def getnum(msg):
    while True:
        s = input(msg)
        if "," in s and "(" not in s:
            s = s.replace(",", ".")
        try:
            return float(eval(s))
        except:
            print("Not a number")


def nz(v):
    """Turn -0.0 into 0.0.

    With b = 0, -b/(2a) is negative zero, and "{:.4f}".format(-0.0)
    prints "-0.0000" -- which looks like a bug to a student reading
    the screen. Adding 0.0 normalises the sign.
    """
    return v + 0.0


print("QUADRATIC")

while True:
    a = getnum("a = ")
    if a != 0:
        break
    print("a cannot be 0")

b = getnum("b = ")
c = getnum("c = ")

d = b * b - 4 * a * c
print("D = {:.4f}".format(nz(d)))
print("vertex x = {:.4f}".format(nz(-b / (2 * a))))

if d > 0:
    r = sqrt(d)
    print("2 real roots")
    print("x1 = {:.4f}".format(nz((-b + r) / (2 * a))))
    print("x2 = {:.4f}".format(nz((-b - r) / (2 * a))))
elif d == 0:
    print("1 repeated root")
    print("x = {:.4f}".format(nz(-b / (2 * a))))
else:
    print("No real roots")
    print("re = {:.4f}".format(nz(-b / (2 * a))))
    print("im = +/-{:.4f}".format(sqrt(-d) / (2 * abs(a))))
