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
    
    Distances must be specified in rotor diameters from upstream turbine.
    Distances can be negative.
    """
    
    directory = const.PARAVIEW_DIRECTORY/casename/'streamtube'
    if not directory.is_dir():
        logger.warning(f'No directory found for case {casename}')
        return
    
    logger.info(f'Processing case {casename}')
    
    # Load streamtube file
    streamtubefile = directory/f'{casename}_streamtube_{turbine}Turbine_forwardBackward.vtp'
    logger.debug(f'Reading file {streamtubefile.name}')
    streamtube = pv.XMLPolyDataReader(registrationName='streamtube',
                                        FileName=[str(streamtubefile)])
    streamtube.PointArrayStatus = []
    streamtube.TimeArray = 'None'
    pv.UpdatePipeline(time=0.0, proxy=streamtube)
    
    for distance in distances:
        
        distance_str = int(distance) if distance.is_integer() else str(distance).replace('.','_')
        
        outputfile = directory/f'{casename}_streamtube_{turbine}Turbine_slice_{distance_str}D.csv'
        if not overwrite and outputfile.exists():
            logger.warning(f'{outputfile.name} exists. skipping.')
            continue
        
        # Create a slice
        x = distance*const.TURBINE_DIAMETER
        if distance == 12:  # 12D is slightly outside refined region.
            x -= 3          # a small adjustment fixes the issue.
            
        logger.debug(f'Creating slice at {distance}D ({x:.0f}m)')
        pvslice = pv.Slice(registrationName='pvslice', Input=streamtube)
        pvslice.SliceType.Origin = [x,0,0]
        
        logger.info(f'Writing file {outputfile.name}')
        pv.SaveData(str(outputfile), proxy=pvslice)

        pv.Delete(pvslice)
        del pvslice
        
    pv.Delete(streamtube)
    del streamtube

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
                        nargs='+',type=float,required=True)
    parser.add_argument('-t', '--turbine', help='which turbine? upstream or downstream',
                        choices=['upstream','downstream'], required=True)
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed Command Line Arguments: {args}')
    
    for casename in args.cases:
        turbineStreamTubeSlice(casename,args.distances,args.turbine)