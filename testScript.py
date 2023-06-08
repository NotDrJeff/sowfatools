#!/bin/python3

import logging
from pathlib import Path
import numpy as np
import pvtools
import waketools

if __name__=='__main__':
    logging.basicConfig(force=True, level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    # paraview.compatibility.major = 5
    # paraview.compatibility.minor = 11

    CASE_NAME = 't001'
    CASE_DIR = Path(f'/users/40146600/sharedscratch/{CASE_NAME}')
    CASE_FILE = CASE_DIR/f'{CASE_NAME}.foam'

    TURBINE_TIP_RADIUS = 63.0
    TURBINE_DIAMETER = 2 * TURBINE_TIP_RADIUS
    TURBINE_HUB_HEIGHT = 90.0
    TURBINE_BASE_COORDINATES = (1118.0, 1280.0)
    # incoming wind direction in degrees clockwise from North
    WIND_DIRECTION = np.radians(240)
    DOMAIN_HEIGHT = 1000

    CELLARRAYS = [
                  'U', 'UAvg',
                  'Uprime', 'uRMS', 'uuPrime2',
                  'p_rgh', 'p_rghAvg',
                  'T', 'TAvg',
                  'Tprime', 'TRMS', 'TTPrime2', 'uTPrime2',
                  'Rmean', 'qmean',
                  'kResolved', 'kSGS', 'kSGSmean',
                  'bodyForce',
                  'Rwall', 'qwall',
                  'SourceT', 'SourceU',
                  'T_0', 'U_0',
                  'epsilonSGSmean', 'kappat', 'nuSGSmean', 'nuSgs',
                  'omega', 'omegaAvg',
                  'Q'
                 ]

    ofcase = pvtools.loadof(CASE_FILE)
    
    turbine_origin = np.array([*TURBINE_BASE_COORDINATES, TURBINE_HUB_HEIGHT])
    turbine_radius = TURBINE_TIP_RADIUS
    unit_normal = np.array([1.0, 0.577, 0.0])
    unit_normal /= np.linalg.norm(unit_normal)
    wind_vector = np.array([-np.sin(WIND_DIRECTION),
                            -np.cos(WIND_DIRECTION),
                            0])
    
            
    pvtools.integrated_wake(ofcase, Path('turbineIntegratedWake'), turbine_origin,
                            unit_normal, turbine_radius)
    
    # pvtools.wake_line_sample(ofcase, Path(f"{CASE_NAME}_turbineLineSample"), turbine_origin,
    #                          turbine_radius, DOMAIN_HEIGHT, wind_vector)
    

    
    logger.info("Finished")
