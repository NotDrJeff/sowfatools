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

def main(case_name):
    utils.configure_logging((const.CASES_DIR / case_name / const.SOWFATOOLS_DIR
                             / f'log.{Path(__file__).stem}'),
                            level=logging.DEBUG)
    
    paraview.compatibility.major = 5
    paraview.compatibility.minor = 10
    simple._DisableFirstRenderCameraReset()
    
    case_dir = const.CASES_DIR / case_name
    fname = case_dir / f'{case_name}.foam'
    cellarrays = ['UAvg']
    ofcase = pv.loadof(fname,cellarrays)
    
    logger.debug('Extracting Cells')
    extracted_region_origin = [(i+5) for i in const.REFINEMENT_ORIGIN]
    extracted_region_length = [(i-10) for i in const.REFINEMENT_SIZE]
    extractCells = simple.ExtractCellsByRegion(Input=ofcase)
    extractCells.IntersectWith = 'Box'
    extractCells.IntersectWith.Position = extracted_region_origin
    extractCells.IntersectWith.Length = extracted_region_length
    extractCells.IntersectWith.Rotation = [0,0,(270-const.WIND_DIRECTION_DEG)]
    
    logger.debug('Create Ellipse')
    ellipse = simple.Ellipse()
    ellipse.Center = const.TURBINE_ORIGIN
    ellipse.Normal = const.WIND_UNIT_VECTOR
    ellipse.MajorRadiusVector = [const.TURBINE_RADIUS,0,0]
    
    pointdata = pv.create_cellDataToPointData(extractCells,cellarrays)

    logger.debug('Creating stream tracers')
    streamTracer = simple.StreamTracerWithCustomSource(Input=pointdata,
                                                       SeedSource=ellipse)
    streamTracer.Vectors = ['POINTS'] + cellarrays
    streamTracer.MaximumStreamlineLength = const.DOMAIN_MAXDISTANCE
    streamTracer.IntegrationDirection = 'FORWARD'

    slice = pv.create_slice(streamTracer,const.TURBINES_ORIGIN[1],
                            const.WIND_UNIT_VECTOR)
    
    logger.debug('save data')
    streamline_dir = case_dir / const.STREAMLINES_DIR
    utils.create_directory(streamline_dir)
    fname = (streamline_dir
             / f'{case_name}_streamLines_turbine0_forward_intersect_turbine1')
    simple.SaveData(f'{fname}.csv', proxy=slice, PointDataArrays=['UAvg'])
    # pv.save_csv(slice,fname,'Point Data')
    # simple.SaveData(f'{fname}.csv', proxy=slice, PointDataArrays=['UAvg'])
        
    
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
    