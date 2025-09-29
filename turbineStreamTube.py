#!/usr/bin/env python3

import logging
LEVEL = logging.INFO
logger = logging.getLogger(__name__)

import sys
import argparse

import paraview
paraview.compatibility.major = 5
paraview.compatibility.minor = 13
import paraview.simple as pv
pv._DisableFirstRenderCameraReset()  # disable automatic camera reset on 'Show'

import utils
import constants as const

################################################################################

def turbineStreamTube(casename):
    """Created by Jeffrey Johnston for sowfatools. October 2024.
    Use paraview to generate turbine streamtubes.
    """
    
    directory = const.PARAVIEW_DIRECTORY/casename
    if not directory.is_dir():
        logger.warning(f'No directory found for case {casename}')
        return
    
    logger.info(f'Processing case {casename}')
    
    utils.create_directory(directory/'streamtube')
    
    # Load case data
    datafilepath = directory/f'{casename}_transform&calculate.vtu'
    data = pv.XMLUnstructuredGridReader(registrationName='data.vtu',
                                        FileName=[str(datafilepath)])
    data.CellArrayStatus = ['UAvg']
    data.TimeArray = 'None'
    
    pointdata = pv.CellDatatoPointData(registrationName='pointdata', Input=data)
    
    logger.debug(f'Loading {datafilepath.name}')
    pv.UpdatePipeline(time=0.0, proxy=pointdata)
    
    # Create ellipse for streamtube seeding
    rotor_untilted = pv.Ellipse(registrationName='rotor_untilted')
    rotor_untilted.Normal = [1,0,0]
    rotor_untilted.MajorRadiusVector = [0, const.TURBINE_RADIUS, 0]
    rotor_untilted.Resolution = 1000
    
    rotor_tilted = pv.Transform(registrationName='rotor_tilted',
                                Input=rotor_untilted)
    rotor_tilted.Transform = 'RotateAroundOriginTransform'
    
    # Generate streamtubes for upstream and downstream turbines
    for turbine in ['upstream','downstream']:
        outputfile = directory/'streamtube'/f'{casename}_streamtube_{turbine}Turbine_forwardBackward.vtp'
        
        rotor_center = 0 if turbine == 'upstream' else const.TURBINE_SPACING_m
        rotor_untilted.Center = [rotor_center,0,0]
        rotor_tilted.Transform.Originofrotation = [rotor_center,0,0]
        
        if casename in ['t007','t009'] and turbine == 'upstream':
            tilt_angle = -30
        else:
            tilt_angle = 5
        rotor_tilted.Transform.Rotate = [0,tilt_angle,0]
        pv.UpdatePipeline(time=0.0, proxy=rotor_tilted)
        
        streamtubes = pv.StreamTracerWithCustomSource(registrationName='streamtubes',
                                                      Input=pointdata,
                                                      SeedSource=rotor_tilted)
        streamtubes.ComputeVorticity = 0
        
        logger.debug(f'Generating streamtubes for {turbine} turbine')
        pv.UpdatePipeline(time=0.0, proxy=streamtubes)

        logger.info(f'Saving {outputfile.name}')
        pv.SaveData(str(outputfile),proxy=streamtubes,
                    ChooseArraysToWrite=1,PointDataArrays=[],CellDataArrays=[],
                    CompressorType='ZLib')
        
        pv.Delete(streamtubes)
        del streamtubes
        
    pv.Delete(data)
    pv.Delete(rotor_tilted)
    pv.Delete(rotor_untilted)
    pv.Delete(pointdata)
    pv.Delete(data)
    del rotor_tilted, rotor_untilted, pointdata, data
    
        
################################################################################


if __name__ == '__main__':
    utils.configure_root_logger(level=LEVEL)
    logger.debug(f'Python version: {sys.version}')
    logger.debug(f'Python executable location: {sys.executable}')
    
    description = """Use paraview to generate turbine streamtubes"""
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument('cases',
                        help='List of turbine cases',
                        nargs='+')
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed Command Line Arguments: {args}')
    
    for casename in args.cases:
        turbineStreamTube(casename)
        