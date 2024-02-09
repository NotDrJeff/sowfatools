#!/bin/python3

import numpy as np
import waketools

freestream_velocity = 8.1
alpha = 0.1
a = 2/3

wake_velocity_40m = waketools.jensen_velocity(freestream_velocity, a, alpha, 1)

wake_velocity_100m = waketools.jensen_velocity(freestream_velocity, a, alpha, 2.5)

print(f'{wake_velocity_40m=} {wake_velocity_100m=}')

wake_velocity_8 = waketools.jensen_velocity(freestream_velocity, a, alpha, 8) / freestream_velocity
wake_velocity_5 = waketools.jensen_velocity(freestream_velocity, a, alpha, 5) / freestream_velocity
wake_velocity_3 = waketools.jensen_velocity(freestream_velocity, a, alpha, 3) / freestream_velocity

print(f'{wake_velocity_8=} {wake_velocity_5=}, {wake_velocity_3=}')

wake_velocity_upstream = waketools.jensen_velocity(8, a, 0.05, 7)

power = 0.5 * 1.2 * np.pi * 126**2 / 4 * 1/3 * wake_velocity_upstream * ( (wake_velocity_upstream)**2 - ((1-2*2/3)*wake_velocity_upstream)**2 )

print(f'{wake_velocity_upstream=} {power=}')