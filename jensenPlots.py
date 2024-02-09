#!/bin/python3

import numpy as np
import matplotlib.pyplot as plt

plt.ioff()

alpha = 0.01 * np.arange(1,11) # Wake decay coefficient
x_d = np.arange(1,16) # Streamwise Turbine Spacing in Diameters

# Plot Asymptotoic Velocity for different spacings and decay coefficients

plt.xlabel("x0/r0")
plt.ylabel("Vinf/u")

for a in alpha:
    x = (1/3) * (1/(1+2*a*x_d))**2 # Jensen, 1983. eq. 12
    v = 1 - (2*x/(1-x)) # Jensen, 1983. eq. 12
    plt.plot(x_d, v, label=f'alpha={a}')
    
plt.legend()    
plt.savefig("jensenPlot.png")