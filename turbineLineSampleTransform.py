#!/bin/python3

import logging
LEVEL = logging.INFO
logger = logging.getLogger(__name__)

from pathlib import Path
import argparse

import numpy as np

import utils
import constants as const

CASESDIR = Path('/mnt/d/johnston_2024_thesis')

SCALAR_QUANTITIES = {'T', 'TAvg', 'Tprime', 'TTPrime2', 'TRMS', 'SourceT',
                     'p_rgh', 'p_rghAvg', 'Q',
                     'nuSgs', 'nuSGSmean', 'kSGS', 'kSGSmean', 'kResolved',
                     'omega', 'omegaAvg', 'kappat', 'epsilonSGSmean'}

VECTOR_QUANTITIES = {'U', 'UAvg', 'Uprime', 'uRMS', 'SourceU', 'phi',
                     'bodyForce', 'qmean', 'qwall'}

SYMMTENSOR_QUANTITIES = {'uuPrime2', 'uTPrime2', 'Rmean', 'Rwall'}

 
QUANTITIES_TO_KEEP = {'UAvg', 'uuPrime2', 'kResolved'}


################################################################################

def turbineLineSampleTransform(casename, times, overwrite=False):
    #casedir = const.CASES_DIR / casename
    casedir = CASESDIR / casename
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
        
    filepaths = [file for file in lsDir.iterdir()]
    
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
        
        if time not in times:
            logger.debug(f'{filepath.name} does not match requested times. '
                         f'Skipping.')
            continue
        
        # Identify scalar, vector or tensor
        vector = False
        if quantity in SCALAR_QUANTITIES:
            logger.debug(f'{filepath.name} is a scalar. Skipping.')
            continue
            
        elif quantity in VECTOR_QUANTITIES:
            vector = True
            
        elif quantity in SYMMTENSOR_QUANTITIES:
            # To support tensor rotation later
            logger.debug(f'{filepath.name} is a tensor. Skipping.')
            continue
            
        ########################################################################
        
        writefile = (lsDir / f'{linename}_{quantity}_transformed_{time}.gz')
        if not overwrite:
            if writefile.exists():
                logger.warning(f'{writefile} exists. skipping. ')
                continue
            
        data = np.loadtxt(filepath)
        
        if vector:
            data[:,1:] = const.WIND_ROTATION.apply(data[:,1:])
                
            logger.debug(f'Saving file {writefile.name}')
            np.savetxt(writefile,data,fmt='%.11e')


################################################################################

if __name__=='__main__':
    utils.configure_root_logger(level=LEVEL)
    
    description = """Stitch lineSample data from different time directories"""
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument('cases', help='cases to perform analysis for',
                        nargs='+')
    parser.add_argument('-t','--times', help='times to perfrom analysis for',
                        nargs='+', required=True)
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed Command Line Arguments: {args}')
    
    for casename in args.cases:
        turbineLineSampleTransform(casename,args.times)
        