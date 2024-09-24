#!/usr/bin/env python3

import logging
LEVEL = logging.INFO
logger = logging.getLogger(__name__)

import sys
import argparse

import numpy as np

import utils
import constants as const


################################################################################

def turbineLineSampleTransform(casename, requested_time, overwrite=False):
    """Takes line sample data already processed by turbineLineSample and
    transforms so that vector and tensor components align with new axes."""
    casedir = const.CASES_DIR / casename
    if not casedir.is_dir():
        logger.warning(f'{casename} directory does not exist. Skipping.')
        return
    
    sowfatoolsdir = casedir / const.SOWFATOOLS_DIR
    
    logfilename = 'log.turbineLineSampleTransform'
    utils.configure_function_logger(sowfatoolsdir/logfilename, level=LEVEL)
    
    ############################################################################
    
    logger.info(f'Transforming lineSample for case {casename}')
    
    lsDir = sowfatoolsdir / 'lineSample'
    if not lsDir.is_dir():
        logger.warning(f'{lsDir.name} directory does not exist. Skipping.')
        return
    
    # exclude already transformed files
    filepaths = [file for file in lsDir.iterdir()
                 if 'transformed' not in file.name]
    
    logger.debug(f'Found {len(filepaths)} filenames')
    
    ############################################################################
    
    for filepath in filepaths:
        logger.debug(f'Processing file {filepath.name}')
            
        # Separate information in filename           
        fileparts = filepath.stem.split('_')
        
        # Account for half diamters, e.g. lineV0_5
        if fileparts[1] == '5':
            linename = '_'.join(fileparts[:2])
        else:
            linename = fileparts[0]
        
        # Get quantity and time
        quantity = fileparts[-2]
        time = fileparts[-1]
        
        if not time == requested_time:
            logger.debug(f'{filepath.name} does not match requested time. '
                         f'Skipping.')
            continue
        
        # Identify scalar, vector or tensor
        vector = False
        tensor = False
        if quantity in const.SCALAR_QUANTITIES:
            logger.debug(f'{filepath.name} is a scalar. Skipping.')
            continue
            
        elif quantity in const.VECTOR_QUANTITIES:
            vector = True
            
        elif quantity in const.SYMMTENSOR_QUANTITIES:
            tensor = True
            
        ########################################################################
        
        writefile = (lsDir / f'{linename}_{quantity}_transformed_{time}.gz')
        if not overwrite:
            if writefile.exists():
                logger.warning(f'{writefile} exists. skipping. ')
                continue
            
        data = np.loadtxt(filepath)
        
        if vector:
            data[:,1:] = const.WIND_ROTATION.apply(data[:,1:])
            
        if tensor:
            
            # Because we are limited to a rotation in the horizontal plane only
            # we can apply a simple vector rotation to stresses on the z plane.
            # z_stress contains components (sw_z, cs_z, zz)
            data[:,[3,5,6]] = const.WIND_ROTATION.apply(data[:,[3,5,6]])
            
            
            
            # Rotate other components using 2D stress balance in xy plane
            
            THETA_DEG = 30
            theta_rad = np.deg2rad(THETA_DEG)
            sin = np.sin(theta_rad)
            cos = np.cos(theta_rad)
            xx = np.copy(data[:,1])
            xy = np.copy(data[:,2])
            yy = np.copy(data[:,4])
            
            data[:,4] = xx*sin**2 + yy*cos**2 + 2*xy*sin*cos # cs,cs
            data[:,1] = xx + yy - data[:,4] # sw,sw
            data[:,2] = ( xx*sin + xy*cos - data[:,4]*sin ) / cos # cs,sw
                
        logger.debug(f'Saving file {writefile.name}')
        np.savetxt(writefile,data,fmt='%.11e')
            
            
################################################################################

if __name__=='__main__':
    utils.configure_root_logger(level=LEVEL)
    logger.debug(f'Python version: {sys.version}')
    logger.debug(f'Python executable location: {sys.executable}')
    
    description = """Rotates line sample data to new axis."""
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument('cases', help='cases to perform analysis for',
                        nargs='+')
    parser.add_argument('-t','--time', help='time to perfrom analysis for',
                        required=True)
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed Command Line Arguments: {args}')
    
    for casename in args.cases:
        turbineLineSampleTransform(casename,args.time)
        