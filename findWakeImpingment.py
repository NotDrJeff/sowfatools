#!/bin/python3

import logging
import sys
from pathlib import Path

import numpy as np
import sympy.geometry as geom
import paraview
import paraview.simple as simple

import constants as const
import utils
import pvtools as pv

logger = logging.getLogger(__name__)

def main(casename):
    utils.configure_logging((const.CASES_DIR / casename / const.SOWFATOOLS_DIR
                             / f'log.{Path(__file__).stem}'),
                            level=logging.DEBUG)
    
    casedir = const.CASES_DIR / casename
    fname = casedir / f'{casename}.foam'
    
    pv.calculateDownstreamWakeLocation(casename,fname,casedir)
    
    ###########################################################################
    
    logger.debug(f'Reading file {fname}')
    data = np.genfromtxt(fname,names=True, delimiter=',')
    
    logger.debug(f'Rotating Point Coordinates unto plane normal to x axis')
    points = list(zip(data['Points0'],data['Points1'],data['Points2']))
    points = const.WIND_ROTATION.apply(points)
    x = [i[0] for i in points]
    logger.debug(f'New x values: Max={max(x)} Min={min(x)} Diff={max(x)-min(x)}')
    points = np.array([i[1:] for i in points])
    
    # downstream_wake_impingement = geom.Polygon(*points)
    # downstream_turbine = geom.Circle(const.TURBINE_ORIGIN_ROTATED[1:],
    #                                  const.TURBINE_RADIUS)
    # intersect = geom.intersection(downstream_turbine,
    #                               downstream_wake_impingement)
    
    import pdb; pdb.set_trace()
    
    # create 2d cartestian grid based on number of wake sample points and
    
    c = 2*np.pi*const.TURBINE_RADIUS # circumference of turbine
    n = len(points) # Number of sample points
    # Grid spacing should be significantly larger than spacing
    # between sample points. Here 10 times bigger.
    grid_spacing =  10*c/n
    
    # bounding box
    turbineMaxX = const.TURBINE_ORIGIN_ROTATED[1] + const.TURBINE_RADIUS
    turbineMinX = const.TURBINE_ORIGIN_ROTATED[1] - const.TURBINE_RADIUS
    maxX = max(np.max(points[:,0]),turbineMaxX)
    minX = min(np.min(points[:,0]),turbineMinX)
    
    np.linspace(0,)
    
    np.meshgrid()
    
    logger.info("Finished")
    
    

if __name__ == "__main__":
    main(*sys.argv[1:])
    