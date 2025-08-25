#!/usr/bin/env python3

import gzip as gz

import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate as interpolate


U = np.loadtxt('p001_U_mean.gz')
V = np.loadtxt('p001_V_mean.gz')

U = U[(U[:,0]>=18000),:]
V = V[(V[:,0]>=18000),:]

with gz.open('p001_U_mean.gz', 'rt') as f:
    header = f.readline()
    
header = header.removeprefix('# ').split()
idx = (header.index('85m'),header.index('245m'),header.index('495m'))

t  = U[:,0]
dt = U[:,1]
t_uniform = np.linspace(t[0],t[-1],t.size)
dt_uniform = t_uniform[1] - t_uniform[0]

U = U[:,idx]
V = V[:,idx]

u = U - np.average(U,axis=0)
v = V - np.average(V,axis=0) 

for i,_ in enumerate(idx):
    for j,vel in enumerate((u[:,i],v[:,i])):
        interpolation_function = interpolate.interp1d(t,vel,kind='linear')
        vel_uniform = interpolation_function(t_uniform)

        R = np.correlate(vel_uniform,vel_uniform,mode='full')
        R = R[R.size//2:] # keep only positive lags (symmetry)
        R = R / R[0] # normalize

        lag = np.arange(R.size) * dt_uniform

        zero_idx = np.nonzero(R<=0)[0] # where returns tuple of arrays.
        zero_idx = zero_idx[0] if len(zero_idx) > 0 else R.size
            # Find first time R is 0 or less.

        integral = np.trapezoid(R[:zero_idx],lag[:zero_idx])

        print(f'Height {i}, Component {j} : {integral} s')
