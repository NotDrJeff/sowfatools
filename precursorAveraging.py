#!/bin/python3
"""Written for Python 3.12
Jeffrey Johnston   NotDrJeff@gmail.com  March 2024"""

import logging
LEVEL = logging.INFO
logger = logging.getLogger(__name__)

import argparse
from pathlib import Path

import numpy as np

import constants as const
import utils

# Suppress output from matplotlib before importing
if __name__ == '__main__':
    logging.getLogger(f'matplotlib').setLevel(logging.WARNING)
else:
    logging.getLogger(f'{__name__}.matplotlib').setLevel(logging.WARNING)
    
import matplotlib.pyplot as plt


################################################################################

def precursorAveraging(casename):
    
    casedir = const.CASES_DIR / casename
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
        logger.info(f'Processing {quantity.stem} for {casename}')
        
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
        
        fname = outputdir / (f'{casename}_{quantity.stem}.gz')
        logger.debug(f'Saving file {fname.name}')
        np.savetxt(fname,data,header=header)
        
        ########################################################################
        
        averagedata = np.empty(data.shape)
        averagedata[:,:2] = data[:,:2]
        for i in range(heights.shape[0]):
            averagedata[:,i+2] = utils.calculate_moving_average(data,i+2,1)
            
        fname = outputdir / (f'{casename}_{quantity.stem}_runningAverage.gz')
        logger.debug(f'Saving file {fname.name}')
        np.savetxt(fname,data,header=header)
        
        ########################################################################
        
        logger.info(f'Average for {quantity.stem} at hub height after '
                    f'{data[-1,0]:.2f}s is {averagedata[-1,hubheight_idx+2]:.3e}')
        
        ########################################################################
        
        plt.plot(data[:,0],data[:,hubheight_idx+2])
        plt.plot(data[:,0],averagedata[:,hubheight_idx+2])
        
        fname = outputdir / (f'{casename}_{quantity.stem}_hubHeight.png')
        logger.debug(f'Saving file {fname.name}')
        plt.savefig(fname)
        plt.cla()
        
        ########################################################################
        
        del data, averagedata
        
    logger.info(f'Finished processing averaging for case {casename}')


################################################################################

if __name__ == "__main__":
    utils.configure_root_logger(level=LEVEL)

    description = """Stitch precursor averaging data, calculate running time
                     average and plot at turbine hub height"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('cases', help='list of cases to perform analysis for',
                        nargs='+')
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed the command line arguments: {args}')
    
    for casename in args.cases:
        precursorAveraging(casename)
        