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

def turbineStreamTubeSlice(casename,distances,turbine,overwrite=True):
    """Created by Jeffrey Johnston for sowfatools. October 2024.
    Use paraview to slice a streamtube at specified distances
    and export resulting points as .csv files.
    Distances must be specified as integer rotor diameters from turbine.
    Distances can be negative.
    """
    
    directory = const.PARAVIEW_DIRECTORY/casename
    if not directory.is_dir():
        logger.warning(f'No directory found for case {casename}')
        return
    
    logger.info(f'Processing case {casename}')
    
    for distance in distances:
        
        outputfile = directory/f'{casename}_streamTube_{turbine}Turbine_slice_{distance}D.csv'
        if not overwrite and outputfile.exists():
            logger.warning(f'{outputfile.name} exists. skipping.')
            continue
        
        if distance < 0 :
            streamtubefile = directory/f'{casename}_streamTube_{turbine}Turbine_backward.vtp'
        else:
            streamtubefile = directory/f'{casename}_streamTube_{turbine}Turbine.vtp'
            
        # Load streamtube file   
        logger.debug(f'Reading file {streamtubefile.name}')
        streamtube = pv.XMLPolyDataReader(registrationName='streamtube',
                                          FileName=[str(streamtubefile)])
        streamtube.PointArrayStatus = []
        streamtube.TimeArray = 'None'

        # Create a slice
        x = distance*const.TURBINE_DIAMETER
        logger.debug(f'Creating slice at {distance}D ({x:.0f}m)')
        slice = pv.Slice(registrationName='slice', Input=streamtube)
        slice.SliceType.Origin = [x,0,0]
        
        logger.debug('Processing pipeline')
        pv.UpdatePipeline(time=0.0, proxy=slice)
        
        logger.info(f'Writing file {outputfile.name}')
        pv.SaveData(str(outputfile), proxy=slice)

        pv.Delete(slice)
        pv.Delete(streamtube)
        del slice, streamtube

################################################################################


if __name__ == '__main__':
    utils.configure_root_logger(level=LEVEL)
    logger.debug(f'Python version: {sys.version}')
    logger.debug(f'Python executable location: {sys.executable}')
    
    description = """Use paraview to slice a streamtube at specified distances
                     and export resulting points as .csv files"""
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument('-c', '--cases', help='cases to perform analysis for',
                        nargs='+', required=True)
    parser.add_argument('-d', '--distances', help='distances (in diameters) to slice',
                        nargs='+',type=int,required=True)
    parser.add_argument('-t', '--turbine', help='which turbine? upstream or downstream',
                        choices=['upstream','downstream'], required=True)
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed Command Line Arguments: {args}')
    
    for casename in args.cases:
        turbineStreamTubeSlice(casename,args.distances,args.turbine)