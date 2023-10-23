import math
import statistics


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


def calcAcceleration(acceleration_string):
    accel_arr = acceleration_string.split(';')
    xs = ys = zs = []
    for accel in accel_arr:
        if accel == '':
            continue
        accel = accel.split(' ', 3)
        xs.append(float(accel[0].split(':')[1]))
        ys.append(float(accel[1].split(':')[1]))
        zs.append(float(accel[2].split(':')[1]))
    return f"x:{round(statistics.mean(xs), 3)} y:{round(statistics.mean(ys), 3)} z:{round(statistics.mean(zs), 3)}"
