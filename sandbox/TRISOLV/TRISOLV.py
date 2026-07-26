# TRISOLV -- triangle solver: SSS, SAS, ASA
# TI-84 Evo / Evo-T / CE Python / 83 Premium CE Python
#
# Numeric output only. No CAS.
# ANGLES ARE IN DEGREES at every prompt. Python's math module is always
# in radians, so this program converts with radians() internally. The
# calculator's MODE setting does not affect Python -- leave it alone.

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


def getpos(msg):
    while True:
        v = getnum(msg)
        if v > 0:
            return v
        print("Must be > 0")


def show(a, b, c, A, B, C):
    print("a = {:.3f}  A = {:.3f}".format(a, A))
    print("b = {:.3f}  B = {:.3f}".format(b, B))
    print("c = {:.3f}  C = {:.3f}".format(c, C))
    s = (a + b + c) / 2
    area = sqrt(s * (s - a) * (s - b) * (s - c))
    print("Area  = {:.3f}".format(area))
    print("Perim = {:.3f}".format(a + b + c))


print("TRIANGLE SOLVER")
print("1 SSS  2 SAS  3 ASA")

while True:
    m = int(getnum("Mode: "))
    if m in (1, 2, 3):
        break
    print("Pick 1, 2 or 3")

if m == 1:
    a = getpos("a = ")
    b = getpos("b = ")
    c = getpos("c = ")
    if a + b <= c or a + c <= b or b + c <= a:
        print("Not a triangle")
    else:
        A = degrees(acos((b * b + c * c - a * a) / (2 * b * c)))
        B = degrees(acos((a * a + c * c - b * b) / (2 * a * c)))
        show(a, b, c, A, B, 180 - A - B)

elif m == 2:
    a = getpos("a = ")
    b = getpos("b = ")
    C = getpos("angle C (deg) = ")
    if C >= 180:
        print("Angle must be < 180")
    else:
        c = sqrt(a * a + b * b - 2 * a * b * cos(radians(C)))
        A = degrees(acos((b * b + c * c - a * a) / (2 * b * c)))
        show(a, b, c, A, 180 - A - C, C)

else:
    A = getpos("angle A (deg) = ")
    B = getpos("angle B (deg) = ")
    c = getpos("side c = ")
    if A + B >= 180:
        print("A + B must be < 180")
    else:
        C = 180 - A - B
        k = c / sin(radians(C))
        show(k * sin(radians(A)), k * sin(radians(B)), c, A, B, C)
