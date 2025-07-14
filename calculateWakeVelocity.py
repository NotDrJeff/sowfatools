#!/bin/python3
"""Load an openfoam case and calculate average velocity at different wake
cross-sections"""

import logging
import sys
from pathlib import Path

import numpy as np
import paraview.simple as simple

import pvtools
import utils
import constants

logger = logging.getLogger(__name__)

def main(case_name):
    CASE_DIR = constants.CASES_DIR / case_name
    SOWFATOOLS_DIR = CASE_DIR / 'sowfatools'
    WAKESAMPLING_DIR = SOWFATOOLS_DIR / 'wakeSampling'
    CASE_FILE = CASE_DIR / f'{case_name}.foam'
    CELLARRAYS = ['UAvg']
    
    utils.create_directory(WAKESAMPLING_DIR)
    
    case = pvtools.loadof(CASE_FILE,CELLARRAYS)
    transform = pvtools.create_transform(case,
                                         (0,0,constants.WIND_DIRECTION_DEG+90))
    pointData = pvtools.create_cellDataToPointData(transform,CELLARRAYS)
    
    def calculateSliceOrigin(i):
        return (constants.TURBINE_ORIGIN_ROTATED
                + i * np.array([constants.TURBINE_DIAMETER, 0, 0]))
    
    slice_origin = calculateSliceOrigin(1)
    wakeslice = pvtools.create_slice(pointData,slice_origin,(1,0,0))
    wakeclip = pvtools.create_cylinder_clip(wakeslice, slice_origin, (1,0,0),
                                            constants.TURBINE_RADIUS)
    integratedwake = pvtools.integrate_variables(wakeclip, per_volume=False)
    filename = WAKESAMPLING_DIR / f'{case_name}_wakeMassFlow'
    pvtools.save_csv(integratedwake, filename=filename, field='Point Data')
    
    data = np.genfromtxt(f'{filename}.csv',delimiter=',',names=True)
    turbineflux = data['UAvg0']
    del data
    logger.info(f'Flow Rate through turbine is {turbineflux:.2f} m^3/s')
    
    for i in range(1,2):
        logger.info(f"Considering flow at {i}D downstream")
        slice_origin = calculateSliceOrigin(i)
        logger.debug(f"Moving slice. {slice_origin=}")
        wakeslice.SliceType.Origin = slice_origin
        
        converged = False
        radius_step = 10
        wakeflux = [turbineflux]
        j = 0
        
        while not converged:
            j += 1
            logger.info(f"Iteration {j}")
            
            filename = WAKESAMPLING_DIR / f'{case_name}_wakeMassFlow_{i}D'
            pvtools.save_csv(integratedwake,filename=filename,
                             field='Point Data')
            logger.debug(f"Reading data from file {filename}")
            data = np.genfromtxt(filename,delimiter=',',names=True)
            wakeflux.append(data['UAvg0']) 
            del data
            
            percent_difference = ((wakeflux[-1] - turbineflux)
                                  / turbineflux * 100)
            
            logger.info(f'Flow Rate = {wakeflux}. '
                        f'% difference = {percent_difference}.')
            
            # If percentage difference is less than 1%, stop.
            if abs(percent_difference) <= 1:
                logger.debug(f"Converged for iteration {j}. "
                            f"Change = {percent_difference}%")
                converged = True
                continue
            
            # If this is the first wake measurement, then add or substract
            # the radius_step accordingly
            if len(wakeflux) == 2:
                if wakeflux[-1] < wakeflux[0]:
                    logger.debug(f"Increasing clip radius by {radius_step}")
                    new_radius = wakeclip.ClipType.Radius + radius_step
                else:
                    logger.debug(f"Reducing clip radius by {radius_step}")
                    new_radius = wakeclip.ClipType.Radius - radius_step
            
            # If this is the second or subsequent wake measurement, we may
            # need to reduce the size of radius_step
            if len(wakeflux) >= 3:
                if wakeflux[-1] < wakeflux[0]:
                    if wakeflux[-2] > wakeflux[0]:
                        radius_step /= 2
                    logger.debug(f"Increasing clip radius by {radius_step}")
                    new_radius = wakeclip.ClipType.Radius + radius_step
                else:
                    if wakeflux[-2] < wakeflux[0]:
                        radius_step /= 2
                    logger.debug(f"Reducing clip radius by {radius_step}")
                    new_radius = wakeclip.ClipType.Radius - radius_step
            
            if len(wakeflux) == 100:
                logger.warning("Reached maximum iterations. Exiting.")
                sys.exit()
    
    # pvtools.integrate_wake(ofcase, (SOWFATOOLS_DIR
    #                                 /f'{TURBINE_CASE}_turbineIntegratedWake'),
    #                        turbine_origin,
    #                        wind_vector, turbine_radius, distances=rangetoplot)
    
    # Vertical Slices
      
    # filepaths = [(SOWFATOOLS_DIR/f'{TURBINE_CASE}_verticalLineSample_{i}D')
    #              for i in rangetoplot]
    
    # start_point = np.array([*turbine_origin[:2], 0])
    # end_point = np.array([*turbine_origin[:2], DOMAIN_HEIGHT])
    
    # start_points = np.array([(start_point + i * 2 * turbine_radius * wind_vector)
    #                         for i in rangetoplot])
    # end_points = np.array([(end_point + i * 2 * turbine_radius * wind_vector)
    #                        for i in rangetoplot])
    
    # pvtools.create_line_sample_series(ofcase, filepaths, start_points, end_points)
    
    
    # Horizontal Slices
      
    # filepaths = [(SOWFATOOLS_DIR/f'{TURBINE_CASE}_horizontalLineSample_{i}D')
    #              for i in rangetoplot]
    
    # crossstream_vector = np.cross(wind_vector, np.array([0,0,1]))
    # start_point = start_point - TURBINE_DIAMETER * crossstream_vector
    # start_point[2] = TURBINE_HUB_HEIGHT
    # end_point = end_point + TURBINE_DIAMETER * crossstream_vector
    # end_point[2] = TURBINE_HUB_HEIGHT
    
    # start_points = np.array([(start_point + i * 2 * turbine_radius * wind_vector)
    #                         for i in rangetoplot])
    # end_points = np.array([(end_point + i * 2 * turbine_radius * wind_vector)
    #                        for i in rangetoplot])
    
    # pvtools.create_line_sample_series(ofcase, filepaths, start_points, end_points)
    
    logger.info("Finished")

if __name__=='__main__':
    utils.configure_logging(f'log.{Path(__file__).stem}', logging.DEBUG)
    main(*sys.argv[1:])
    sys.exit(0)
