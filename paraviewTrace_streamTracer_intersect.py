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
    simple.SaveData(f'{fname}.csv',
                   proxy=slice,
                   PointDataArrays=['AngularVelocity', 'IntegrationTime', 'Rotation', 'UAvg', 'Vorticity'],
                   CellDataArrays=['ReasonForTermination', 'SeedIds'],
                   FieldDataArrays=['CasePath'])
    # pv.save_csv(slice,fname,'Point Data')
        
    

if __name__ == "__main__":
    main(*sys.argv[1:])
    