#!/bin/python3
"""Written for Python 3.12 as part of github.com/NotDrJeff/sowfatools
Jeffrey Johnston   NotDrJeff@gmail.com  March 2024

Stitches SOWFA precursor averaging files from mutliple run start times together,
removing overlaps. Takes a list of cases as command line arguments.
"""

import logging
LEVEL = logging.INFO
logger = logging.getLogger(__name__)

import argparse
from pathlib import Path

import numpy as np

import constants as const
import utils


################################################################################

def precursorAveraging(casename, overwrite=False):
    
    casedir = const.CASES_DIR / casename
    if not casedir.is_dir():
        logger.warning(f'{casename} directory does not exist. Skipping.')
        return
    
    sowfatoolsdir = casedir / const.SOWFATOOLS_DIR
    utils.create_directory(sowfatoolsdir)
    
    filename = f'log.precursorAveraging'
    utils.configure_function_logger(sowfatoolsdir/filename, level=LEVEL)
    
    ############################################################################
    
    logger.info(f'Processing averaging for case {casename}')
    
    avgdir = casedir / 'postProcessing/averaging'
    outputdir = sowfatoolsdir / 'averaging'
    utils.create_directory(outputdir)
    
    timefolders = [timefolder for timefolder in avgdir.iterdir()]
    timefolders.sort(key=lambda x: float(x.name))
    
    quantities = set()
    for timefolder in timefolders:
        for quantity in timefolder.iterdir():
            if quantity.stem != 'hLevelsCell':
                quantities.add(Path(quantity.name))
            
    logger.info(f'Found {len(quantities)} quantities across '
                f'{len(timefolders)} time folders')
    
    for timefolder in timefolders:
                try:
                    heights = np.genfromtxt(timefolder/'hLevelsCell')
                    break
                except FileNotFoundError:
                    continue
                
    header = ['time','dt']
    header.extend([f'{int(i)}m' for i in heights])
    header = ' '.join(header)
    
    hubheight_idx = np.argmin(np.abs(const.TURBINE_HUB_HEIGHT - heights))
    
    ############################################################################
    
    for quantity in quantities:
        outputfile = outputdir / (f'{casename}_{quantity.stem}.gz')
        
        logger.info(f'Processing {quantity.stem} for {casename}')
        
        if outputfile.exists() and overwrite is False:
            logger.warning(f'{outputfile} exists. Skipping.')
            continue
        
        for timefolder in timefolders:
            fname = timefolder / quantity
            logger.debug(f'Reading {fname}')
            rawdata = np.genfromtxt(fname)
            if 'data' in locals():
                data = np.vstack((data,rawdata))
            else:
                data = np.array(rawdata)
                
            del rawdata
            
        data = utils.remove_overlaps(data,0)
        
        outputfile = outputdir / (f'{casename}_{quantity.stem}.gz')
        logger.debug(f'Saving file {outputfile.name}')
        np.savetxt(outputfile,data,header=header)
        
        del data
        
    logger.info(f'Finished processing averaging for case {casename}')


################################################################################

if __name__ == "__main__":
    utils.configure_root_logger(level=LEVEL)

    description = """Stitch precursor averaging data, removing overlaps"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('cases', help='list of cases to perform analysis for',
                        nargs='+')
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed the command line arguments: {args}')
    
    for casename in args.cases:
        precursorAveraging(casename)
        