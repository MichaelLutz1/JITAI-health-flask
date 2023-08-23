import math


def calcVM(acc):
    vals = acc.split(' ', 3)
    x = float(vals[0].split(':')[1])
    y = float(vals[1].split(':')[1])
    z = float(vals[2].split(':')[1])
    mag = math.sqrt(x**2 + y**2 + z**2)
    return round(mag, 3)


def calcENMO(vm):
    g = 9.81
    enmo = vm - g
    if enmo < 0:
        return 0
    return round(enmo, 3)
