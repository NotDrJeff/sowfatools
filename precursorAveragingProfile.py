#!/bin/python3
"""Written for python 3.12 for the sowfatools package.
Jeffrey Johnston    NotDrJeff@gmail.com   February 2024.

Calculates time-average from sowfatools/averaging at every height for specified
time window.

Accepts three inputs. casename, starttime, endtime"""

import logging
import sys
import gzip
from pathlib import Path

import numpy as np

import constants as const
import utils

logger = logging.getLogger(__name__)
LEVEL = logging.DEBUG

def main(casename, starttime, endtime):    
    casedir = const.CASES_DIR / casename
    avgdir = casedir / const.SOWFATOOLS_DIR / 'averaging'
    utils.configure_logging((avgdir / f'log.{Path(__file__).stem}_{starttime}_{endtime}'),
                            level=LEVEL)
    
    logger.info(f'Processing averaging for case {casename}')
    
    quantities = set()
    for quantity in const.AVERAGING_QUANTITIES:
        filepath = avgdir/f'{casename}_{quantity}.gz'
        if (filepath.is_file()):
            quantities.add(quantity)
            
    logger.info(f'Found {len(quantities)} quantities')
    
    logger.debug(f"Reading heights from {filepath}")
    with gzip.open(filepath, mode='rt') as file:
        header = file.readline().split()[3::2]
        
    heights = np.array([(i.split('_')[-1]) for i in header],dtype=int)

    for quantity in quantities:
        filepath = avgdir/f'{casename}_{quantity}.gz'
        logger.info(f'Processing {filepath.stem}')
        
        try:
            starttime_flt = float(starttime)
            endtime_flt = float(endtime)
        except ValueError:
            logger.error('starttime and endtime should be floats. exiting')
            raise
        
        if starttime_flt >= endtime_flt:
            logger.error('startime is more than or equal to endtime. exiting')
            raise ValueError
        
        logger.info(f"Generating array from {filepath}")
        data = np.genfromtxt(filepath)
        
        upper_limit = ((data[-1,0]//10) + 1) * 10
        lower_limit = (data[0,0,]//10) * 10
        
        
        if (starttime_flt < lower_limit) or (endtime_flt > upper_limit):
            logger.error(f'starttime and/or endtime are out of range. data '
                         f'ranges from {data[0,0]:.2f}s to {data[-1,0]:.2f}s. exiting')
            raise ValueError
        
        startidx = np.argmin(np.abs(data[:,0] - starttime_flt))
        endidx = np.argmin(np.abs(data[:,0] - endtime_flt))
    
        timesteps = data[startidx:endidx+1,1]
        data = data[startidx:endidx+1,2::2]
        
        averages = np.average(data,axis=0,weights=timesteps)
        
        header = f'heights_m {quantity}'
        
        logger.info(f'Calculating time average from {starttime} to {endtime}')
        data = np.column_stack((heights,averages))
        
        filename = \
            f'{casename}_{quantity}_timeaveraged_{starttime}_{endtime}.gz'
        filepath = avgdir/filename
        logger.info(f"Writing output to {filepath}")
        
        np.savetxt(filepath, data, fmt='%.3e', header=header)
        
    logger.info(f'Finished Processing.')
        
        
if __name__ == "__main__":
    main(*sys.argv[1:])
    