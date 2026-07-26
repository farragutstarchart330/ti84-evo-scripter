# KINEMAT -- constant-acceleration motion: know 3, get the other 2
# TI-84 Evo / Evo-T / CE Python / 83 Premium CE Python
#
# Numeric output only. No CAS. Mode does not matter -- arithmetic only,
# no trig. SI units throughout: m/s, m/s^2, s, m.
# Negative values are legal: use them for deceleration or downward motion.

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


def getnonzero(msg):
    while True:
        v = getnum(msg)
        if v != 0:
            return v
        print("Cannot be 0 here")


print("KINEMATICS")
print("1 v0,a,t  2 v0,v,t")
print("3 v0,v,a  4 v0,a,d")

while True:
    m = int(getnum("Mode: "))
    if m in (1, 2, 3, 4):
        break
    print("Pick 1 to 4")

v0 = getnum("v0 (m/s): ")

if m == 1:
    a = getnum("a (m/s2): ")
    t = getnum("t (s): ")
    print("v = {:.3f}".format(v0 + a * t))
    print("d = {:.3f}".format(v0 * t + a * t * t / 2))

elif m == 2:
    v = getnum("v (m/s): ")
    t = getnonzero("t (s): ")
    print("a = {:.3f}".format((v - v0) / t))
    print("d = {:.3f}".format((v0 + v) * t / 2))

elif m == 3:
    v = getnum("v (m/s): ")
    a = getnonzero("a (m/s2): ")
    print("t = {:.3f}".format((v - v0) / a))
    print("d = {:.3f}".format((v * v - v0 * v0) / (2 * a)))

else:
    a = getnonzero("a (m/s2): ")
    d = getnum("d (m): ")
    q = v0 * v0 + 2 * a * d
    if q < 0:
        print("No real answer")
        print("v0^2+2ad < 0")
    else:
        v = sqrt(q)
        print("v = {:.3f}".format(v))
        print("t = {:.3f}".format((v - v0) / a))
