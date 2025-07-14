#!/bin/python3

import logging
from pathlib import Path
import numpy as np
import utils
import pvtools
import waketools
import plottools
from constants import *

logger = logging.getLogger(__name__)

if __name__=='__main__':
    utils.configure_logging(filename="jensenTest.log")
    
    logger.setLevel(logging.DEBUG)
    
    # From Gocmen et al, 2016
    TURBINE_DIAMETER = 31.0
    TURBINE_RADIUS = TURBINE_DIAMETER / 2
    TURBINE_HUB_HEIGHT = 35.0
    STREAMWISE_SPACING = 5
    NUMBER_TURBINES = 3

    first_turbine_origin = np.array([0, 0, TURBINE_HUB_HEIGHT])
    
    
    # predict velocity deficit and wake diameter for each turbine separately
    
    # 3D field
    dx = dy = dz = 10
    nx = DOMAIN_X/dx
    ny = DOMAIN_Y/dy
    nz = 500/dz
    
    velocity = np.full((nx,ny,nz), MEAN_WIND_VELOCITY, dtype=float)
    
    
    # An array of turbine hub coordinates, based on spacing    
    turbine_origins = np.array([first_turbine_origin
                                + (i*STREAMWISE_SPACING*TURBINE_DIAMETER
                                   *WIND_UNIT_VECTOR)
                                for i in range(NUMBER_TURBINES)])
    
    # sampling points downstream of each turbine. Axis 0 gives turbine, axis 1
    # gives downstream location (in intervals of turbine diamter), and axis 2
    # gives x,y,z coordinates
    sampling_points = np.array([(first_turbine_origin
                                 + i*TURBINE_DIAMETER*WIND_UNIT_VECTOR)
                                 for i in range(1,(NUMBER_TURBINES
                                                   *STREAMWISE_SPACING + 1))])
    
    axial_induction_factor = 0.3
    wake_decay_coefficient = 0.05
    
    jensen_velocity = np.full((NUMBER_TURBINES, sampling_points.shape[0], 3), np.NaN, dtype=float)
    
    for turbine in range(NUMBER_TURBINES):
        
        
        jensenvelocity = (u0 * (1 - (2*a) / (1 + 2*alpha*i)**2))
        import pdb; pdb.set_trace()
            rw = TURBINE_DIAMETER * (1 + 2*alpha*i) / 2
            jensenbottom = TURBINE_HUB_HEIGHT - rw
            jensentop = TURBINE_HUB_HEIGHT + rw
            axes[i+5].vlines(jensenvelocity, jensenbottom, jensentop, color='green')
            axes[i+5].text(jensenvelocity, 60, f'{jensenvelocity:.1f}', ha='left',
                           va='top', color='green')
        
    
    # calculate field based on superpostion of values. include mirror images
    
    # plot
    
    
    rangetoplot = range(-4,8)
    
    SOWFATOOLS_DIR = CASE_DIR / 'postProcessing/sowfatools'
    logger.debug(f'Creating directory {SOWFATOOLS_DIR}')
    SOWFATOOLS_DIR.mkdir(parents=True, exist_ok=True)