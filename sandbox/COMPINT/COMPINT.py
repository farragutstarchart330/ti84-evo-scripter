# COMPINT -- compound interest and monthly-savings growth
# TI-84 Evo / Evo-T / CE Python / 83 Premium CE Python
#
# Numeric output only. No CAS. Mode does not matter -- arithmetic only.
# Enter the rate as a percentage: 5 means 5%, not 0.05.
# No currency symbol: the euro sign is non-ASCII and renders badly.

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


def getnonneg(msg):
    while True:
        v = getnum(msg)
        if v >= 0:
            return v
        print("Cannot be negative")


print("COMPOUND INTEREST")
print("1 lump sum")
print("2 monthly deposits")

while True:
    m = int(getnum("Mode: "))
    if m in (1, 2):
        break
    print("Pick 1 or 2")

if m == 1:
    p = getnonneg("Principal: ")
    r = getnonneg("Rate % /yr: ")
    while True:
        n = getnum("Times/yr: ")
        if n > 0:
            break
        print("Must be > 0")
    t = getnonneg("Years: ")

    fv = p * (1 + r / (100 * n)) ** (n * t)
    print("FV    = {:.2f}".format(fv))
    print("Grown = {:.2f}".format(fv - p))

else:
    d = getnonneg("Monthly dep: ")
    r = getnonneg("Rate % /yr: ")
    t = getnonneg("Years: ")

    i = r / 1200
    k = 12 * t
    if i == 0:
        # The annuity formula divides by i, so zero rate needs its own case.
        fv = d * k
    else:
        fv = d * (((1 + i) ** k - 1) / i)
    print("FV    = {:.2f}".format(fv))
    print("Paid  = {:.2f}".format(d * k))
    print("Grown = {:.2f}".format(fv - d * k))
