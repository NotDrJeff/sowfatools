#!/bin/python3

"""Written for python 3.12 for the sowfatools package.
Jeffrey Johnston    NotDrJeff@gmail.com    March 2024.

Reads sources from postprocessing/sources data. Data from multiple runs are
combined, overlapping data is removed, and a running average is calculated

The user must specify the casename.

The user can optionally specify times at which to report the running average
to the logging output (console/file)
"""

import argparse
import logging
from pathlib import Path
import gzip

import numpy as np

import constants as const
import utils

def main(casename, times_to_report):
    logger = logging.getLogger(__name__)
    LEVEL = logging.INFO
    
    casedir = const.CASES_DIR / casename
    sowfatoolsdir = casedir / const.SOWFATOOLS_DIR
    
    utils.configure_logging((sowfatoolsdir / f'log.{Path(__file__).stem}'),
                             level=LEVEL)
    
    logger.info(f'Processing sources for case {casename}')
    
    srcdir = casedir / 'postProcessing/SourceHistory'
    outputdir = sowfatoolsdir / 'SourceHistory'
    utils.create_directory(outputdir)
    
    timefolders = [timefolder for timefolder in srcdir.iterdir()]
    timefolders.sort(key=lambda x: float(x.name))
    
    quantities = set()
    for timefolder in timefolders:
        for quantity in timefolder.iterdir():
            quantities.add(Path(quantity.name))
    
    for quantity in quantities:
        logger.info(f'Processing {quantity.name} for {casename}')
        
        for timefolder in timefolders:
            fname = timefolder / quantity
            logger.debug(f'Reading {fname}')
            rawdata = np.genfromtxt(fname, skip_header=1)
            if 'data' in locals():
                data = np.vstack((data,rawdata))
            else:
                data = np.array(rawdata)
                
            del rawdata
        
        data = utils.remove_overlaps(data,0)
        average = utils.calculate_moving_average(data,2,0)
        
        with gzip.open(fname, mode='rt') as file:
            header = file.readline()[:-1] + ' average'
            
        data = np.column_stack((data,average))
        
        fname = outputdir / (f'{casename}_{quantity.stem}.gz')
        logger.debug(f'Saving file {fname.name}')
        np.savetxt(fname,data,header=header)
        
        # Report running average at specified times if requested
        if times_to_report is not None:
            time_indices = np.array([np.argmin(np.abs(data[:,0] - time))
                                    for time in times_to_report])
            
            for i, time in np.ndenumerate(times_to_report):
                logger.info(f'Average after {time} s is '
                            f'{data[time_indices[i],2]:.3e}')
                
        # data must be deleted for the next loop to work correctly
        del data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Process Precusor Source
                                                    Data and Calculate Running
                                                    Average""")
    
    parser.add_argument("casename", help="specifiy which case to use")
    
    parser.add_argument("-t", "--times", help="What times to report",
                        nargs='*', type=int)
    
    args = parser.parse_args()
    main(args.casename, args.times)