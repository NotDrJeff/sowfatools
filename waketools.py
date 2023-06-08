#!/bin/python3

import logging
import numpy as np

logger = logging.getLogger(__name__)

###############################################################################

def calculate_induction_factor():
    velocities = []
    for label in ["-7D", "0D"]:
        rotordata = np.genfromtxt(f'turbineIntegratedWake{label}.csv',
                                  delimiter=',', names=True)
        velocities.append(rotordata['UAvg0'] * np.cos(np.radians(30))
                          + rotordata['UAvg1'] * np.sin(np.radians(30)))
        
    induction_factor = 1 - velocities[1]/velocities[0]
    
    logger.debug(f"{induction_factor=}")
    
    return induction_factor, *velocities

