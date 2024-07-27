#!/bin/python3
"""Written for Python 3.12, SOWFA 2.4.x
Part of github.com/NotDrJeff/sowfatools
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
    
    logfilename = 'log.precursorAveraging'
    utils.configure_function_logger(sowfatoolsdir/logfilename, level=LEVEL)
    
    ############################################################################
    
    logger.info(f'Processing averaging for case {casename}')
    
    readdir = casedir / 'postProcessing/averaging'
    if not readdir.is_dir():
        logger.warning(f'{readdir.stem} directory does not exist. '
                       f'Skipping case {casename}.')
        return
    
    writedir = sowfatoolsdir / 'averaging'
    utils.create_directory(writedir)
    
    timefolders = [timefolder for timefolder in readdir.iterdir()]
    timefolders.sort(key=lambda x: float(x.name))
    
    quantities = set()
    for timefolder in timefolders:
        for file in timefolder.iterdir():
            if file.stem != 'hLevelsCell':
                quantities.add(Path(file.name))
            
    logger.info(f'Found {len(quantities)} quantities across '
                f'{len(timefolders)} time folders')
    
    for timefolder in timefolders:
        try:
            heights = np.genfromtxt(timefolder/'hLevelsCell')
            break
        except FileNotFoundError:
            continue
            
    if 'heights' not in locals():
        logger.error('hLevelsCell file not found in any timefolder. Exiting.')
        raise FileNotFoundError('hLevelsCell not found')
                
    header = ['time','dt']
    header.extend([f'{int(i)}m' for i in heights])
    header = ' '.join(header)
    
    ############################################################################
    
    for quantity in quantities:
        logger.info(f'Processing {quantity.stem} for {casename}')
        
        writefile = writedir / (f'{casename}_{quantity.stem}.gz')
        if writefile.exists() and overwrite is False:
            logger.warning(f'{writefile} exists. Skipping {quantity.stem}.')
            continue
        
        for timefolder in timefolders:
            readfile = timefolder / quantity
            logger.debug(f'Reading {readfile}')
            rawdata = np.genfromtxt(readfile)
            if 'data' not in locals():
                data = np.array(rawdata)
            else:
                data = np.vstack((data,rawdata))
                
            del rawdata  # Deleted for memory efficiency only
            
        data = utils.remove_overlaps(data,0)
        
        writefile = writedir / (f'{casename}_{quantity.stem}.gz')
        logger.debug(f'Saving file {writefile.name}')
        np.savetxt(writefile,data,header=header,fmt='%.12g')
        
        del data  # Must be deleted for next loop to work
        
    logger.info(f'Finished processing averaging for case {casename}')


################################################################################

if __name__ == '__main__':
    utils.configure_root_logger(level=LEVEL)

    description = """Stitch precursor averaging data, removing overlaps"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('cases', help='list of cases to perform analysis for',
                        nargs='+')
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed the command line arguments: {args}')
    
    for casename in args.cases:
        precursorAveraging(casename)
        