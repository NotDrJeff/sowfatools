#!/usr/bin/env python3

import logging
LEVEL = logging.DEBUG
logger = logging.getLogger(__name__)

import sys
import argparse

import numpy as np

import utils
import constants as const


################################################################################

def turbineLineSampleFluxes(casename, overwrite=False):
    """Calculate mean and turbulent vertical fluxes from transformed line sample
    data."""
    
    casedir = const.CASES_DIR / casename
    if not casedir.is_dir():
        logger.warning(f'{casename} directory does not exist. Skipping.')
        return
    
    sowfatoolsdir = casedir / const.SOWFATOOLS_DIR
    
    logfilename = 'log.turbineLineSampleFluxes'
    utils.configure_function_logger(sowfatoolsdir/logfilename, level=LEVEL)
    
    ############################################################################
    
    logger.info(f'Calculating fluxes from lineSample for case {casename}')
    
    lsDir = sowfatoolsdir / 'lineSample'
    if not lsDir.is_dir():
        logger.warning(f'{lsDir.name} directory does not exist. Skipping.')
        return
        
    filepaths = [file for file in lsDir.iterdir()
                 if ('UAvg_transformed' in file.name
                     or 'uuPrime2_transfomed' in file.name)]
    
    logger.debug(f'Found {len(filepaths)} filenames')
    
    ############################################################################
    
    times = set()
    linenames = set()
    for filepath in filepaths:
            
        # Separate information in filename           
        fileparts = filepath.stem.split('_')
        times.add(fileparts[-1])

        # Account for half diamters, e.g. lineV0_5
        if fileparts[1] == '5':
            linenames.add('_'.join(fileparts[:2]))
        else:
            linenames.add(fileparts[0])
            
    ############################################################################
            
    for linename in linenames:
        for time in times:
            
            logger.debug(f'Processing time {time} for {linename}')
            writefile = (lsDir / f'{linename}_fluxes_{time}.gz')
            
            if not overwrite:
                if writefile.exists():
                    logger.warning(f'{writefile} exists. skipping. ')
                    continue
            
            U = np.loadtxt(lsDir / f'{linename}_UAvg_transformed_{time}')
            uu = np.loadtxt(lsDir / f'{linename}_uuPrime2_transformed_{time}')
            
            # Mean vertical flux of streamwise MKE
            flux1 = U[:,1] * U[:,1] * U[:,3]
            
            # Mean vertical flux of streamwise TKE
            flux2 = uu[:,1] * U[:,3]
            
            data = np.column_stack((U[:,0],flux1,flux2))
            
            logger.debug(f'Saving file {writefile.name}')
            np.savetxt(writefile,data,fmt='%.11e')
            
            
################################################################################

if __name__=='__main__':
    utils.configure_root_logger(level=LEVEL)
    logger.debug(f'Python version: {sys.version}')
    logger.debug(f'Python executable location: {sys.executable}')
    
    description = """Calculate mean and turbulent vertical fluxes"""
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument('cases', help='cases to perform analysis for',
                        nargs='+')
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed Command Line Arguments: {args}')
    
    for casename in args.cases:
        turbineLineSampleFluxes(casename)
        