#!/bin/python3

import logging
from pathlib import Path
import numpy as np
import pvtools
import waketools
import plottools

if __name__=='__main__':
    logging.basicConfig(force=True, level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    PRECURSOR_CASE = 'p002'
    TURBINE_CASE = 't006'
    CASE_DIR = Path(f'/mnt/scratch2/users/40146600/{TURBINE_CASE}')
    TURBINE_CASE_FILE = CASE_DIR/f'{TURBINE_CASE}.foam'

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

    turbine_origin = np.array([*TURBINE_BASE_COORDINATES, TURBINE_HUB_HEIGHT])
    turbine_radius = TURBINE_TIP_RADIUS
    # unit_normal = np.array([1.0, 0.577, 0.0])
    # unit_normal /= np.linalg.norm(unit_normal)
    wind_vector = np.array([-np.sin(WIND_DIRECTION),
                            -np.cos(WIND_DIRECTION),
                            0])
    rangetoplot = range(-4,8)
    
    SOWFATOOLS_DIR = CASE_DIR / 'postProcessing/sowfatools'
    logger.debug(f'Creating directory {SOWFATOOLS_DIR}')
    SOWFATOOLS_DIR.mkdir(parents=True, exist_ok=True)
    
    
    ofcase = pvtools.loadof(TURBINE_CASE_FILE)
    
    pvtools.integrate_wake(ofcase, (SOWFATOOLS_DIR
                                    /f'{TURBINE_CASE}_turbineInte gratedWake'),
                           turbine_origin,
                           wind_vector, turbine_radius)
    
    # Vertical Slices
      
    filepaths = [(SOWFATOOLS_DIR/f'{TURBINE_CASE}_verticalLineSample_{i}D')
                 for i in rangetoplot]
    
    start_point = np.array([*turbine_origin[:2], 0])
    end_point = np.array([*turbine_origin[:2], DOMAIN_HEIGHT])
    
    start_points = np.array([(start_point + i * 2 * turbine_radius * wind_vector)
                            for i in rangetoplot])
    end_points = np.array([(end_point + i * 2 * turbine_radius * wind_vector)
                           for i in rangetoplot])
    
    pvtools.create_line_sample_series(ofcase, filepaths, start_points, end_points)
    
    
    # Horizontal Slices
      
    filepaths = [(SOWFATOOLS_DIR/f'{TURBINE_CASE}_horizontalLineSample_{i}D')
                 for i in rangetoplot]
    
    crossstream_vector = np.cross(wind_vector, np.array([0,0,1]))
    start_point = start_point - TURBINE_DIAMETER * crossstream_vector
    start_point[2] = TURBINE_HUB_HEIGHT
    end_point = end_point + TURBINE_DIAMETER * crossstream_vector
    end_point[2] = TURBINE_HUB_HEIGHT
    
    start_points = np.array([(start_point + i * 2 * turbine_radius * wind_vector)
                            for i in rangetoplot])
    end_points = np.array([(end_point + i * 2 * turbine_radius * wind_vector)
                           for i in rangetoplot])
    
    pvtools.create_line_sample_series(ofcase, filepaths, start_points, end_points)
    
    logger.info("Finished")
