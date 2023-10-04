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
    
    # pv.calculateDownstreamWakeLocation(casename,fname,casedir)
    
    ###########################################################################
    
    resultsdir = casedir / const.STREAMLINES_DIR
    fname = (resultsdir
             / f'{casename}_streamLines_turbine0_forward_intersect_turbine1.csv')
    logger.info(f'Reading file {fname}')
    data = np.genfromtxt(fname,names=True, delimiter=',')
    
    logger.info(f'Rotating Point Coordinates unto plane normal to x axis')
    points = list(zip(data['Points0'],data['Points1'],data['Points2']))
    points = const.WIND_ROTATION.apply(points)
    points = np.array([i[1:]-const.TURBINE_ORIGIN_ROTATED[1:] for i in points])
    
    # downstream_wake_impingement = geom.Polygon(*points)
    # downstream_turbine = geom.Circle(const.TURBINE_ORIGIN_ROTATED[1:],
    #                                  const.TURBINE_RADIUS)
    # intersect = geom.intersection(downstream_turbine,
    #                               downstream_wake_impingement)
    
    # create 2d cartestian grid based on number of wake sample points and
    
    c = 2*np.pi*const.TURBINE_RADIUS # circumference of turbine
    n = len(points) # Number of sample points
    # Grid spacing should be significantly larger than spacing
    # between sample points. Here 10 times bigger.
    grid_spacing =  10*c/n
    
    # bounding box
    maxX = max(np.max(points[:,0]),const.TURBINE_RADIUS)
    minX = min(np.min(points[:,0]),-const.TURBINE_RADIUS)
    maxY = max(np.max(points[:,1]),const.TURBINE_RADIUS)
    minY = min(np.min(points[:,1]),-const.TURBINE_RADIUS)
    
    x = np.arange(minX,maxX+grid_spacing,grid_spacing)
    y = np.arange(minY,maxY+grid_spacing,grid_spacing)
    
    xx,yy = np.meshgrid(x,y)
    
    distance_from_hub = np.sqrt(xx**2+yy**2)
    inrotor = (distance_from_hub < const.TURBINE_RADIUS)
    
    # find cells where points are located
    aroundwake = np.zeros_like(xx)
    for point in points:
        col = np.argmin(np.abs(x-point[0]))
        row = np.argmin(np.abs(y-point[1]))
        aroundwake[row,col] = 1
        
    # loop through each row of mesh
    inwake = np.zeros_like(xx)
    for row in range(inwake.shape[0]):
        value = 0
        for col in range(inwake.shape[1]):
            if (aroundwake[row,col] == 1) :
                if col == 0:
                    value = 0 if value==1 else 1
                elif (aroundwake[row,col-1] != 1):
                    value = 0 if value==1 else 1
                
            inwake[row,col] = value
    
    logger.info("Plotting")
    
    import matplotlib.pyplot as plt
    plt.ioff()
    
    # plt.pcolormesh(xx,yy,inrotor,cmap='Paired')
    
    # plt.plot(points[:,0],points[:,1], '.', color='r', markersize=0.5)
    
    # plt.pcolormesh(xx,yy,aroundwake,cmap='Paired')
    
    plt.pcolormesh(xx,yy,inwake,cmap='Paired')
    
    plt.xlim(minX,maxX)
    plt.ylim(minY,maxY)
    ax = plt.gca()
    ax.set_aspect('equal', adjustable='box')
    
    from matplotlib.ticker import MultipleLocator
    minorlocator = MultipleLocator(grid_spacing)
    ax.yaxis.set_minor_locator(minorlocator)
    ax.xaxis.set_minor_locator(minorlocator)
    #plt.grid(which='minor')
    
    plt.savefig('test.png',dpi=600)
    
    # # import pdb; pdb.set_trace()
    
    logger.info("Finished")
    
    

if __name__ == "__main__":
    main(*sys.argv[1:])
    