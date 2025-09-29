#!/bin/python3

"""
Created by Jeffrey Johnston. Jun, 2023.
"""

import logging
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

###############################################################################

def calculate_induction(upstreamfile: Path, rotorfile: Path,
                        wind_vector: np.array):
    
    logger.debug(f'Calculating induction factor from {upstreamfile.name}'
                 f'and {rotorfile.name}')
    
    def calculate_streamwise_velocity(file):
        data = np.genfromtxt(f'{file}.csv', delimiter=',', names=True)
        velocity = np.array([data['UAvg0'], data['UAvg1'], data['UAvg2']])
        return (np.dot(velocity, wind_vector))
    
    freestreamvelocity = calculate_streamwise_velocity(upstreamfile)
    inducedvelocity = calculate_streamwise_velocity(rotorfile)
    
    induction_factor = 1 - inducedvelocity / freestreamvelocity
    
    logger.debug(f"{induction_factor=}")
    
    return induction_factor, freestreamvelocity, inducedvelocity


def jensen_velocity(u0,a,alpha,i):
    return (u0 * (1 - (2*a) / (1 + 2*alpha*i)**2))

def jensen_wake_width(d, alpha,i):
    return d * (1 + 2*alpha*i) / 2