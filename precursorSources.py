#!/bin/python3

"""Written for python 3.12 for the sowfatools package.
Jeffrey Johnston    NotDrJeff@gmail.com    March 2024.

Reads sources from postprocessing/sources data. Data from multiple runs are
combined, overlapping data is removed, and a running average is calculated

The user must specify the casename.

The user can optionally specify times at which to report the running average
to the logging output (console/file)
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

def precursorSources(casename, times_to_report, overwrite=False):
    
    casedir = const.CASES_DIR / casename
    if not casedir.is_dir():
        logger.warning(f'{casename} directory does not exist. Skipping.')
        return
    
    sowfatoolsdir = casedir / const.SOWFATOOLS_DIR
    utils.create_directory(sowfatoolsdir)
    
    logfilename = 'log.precursorSources'
    utils.configure_function_logger(sowfatoolsdir/logfilename, level=LEVEL)
    
    ############################################################################
    
    logger.info(f'Processing sources for case {casename}')
    
    readdir = casedir / 'postProcessing/SourceHistory'
    if not readdir.is_dir():
        logger.warning(f'{readdir.stem} directory does not exist. '
                       f'Skipping case {casename}.')
        return
    
    writedir = sowfatoolsdir / 'SourceHistory'
    utils.create_directory(writedir)
    
    timefolders = [timefolder for timefolder in readdir.iterdir()]
    timefolders.sort(key=lambda x: float(x.name))
    
    QUANTITIES = ['SourceUXHistory.gz','SourceUYHistory.gz']
    HEADER = 'time dt Sx Sy Smag Sang SAvg_x SAvg_y SAvg_mag SAvg_dir'
    
    ############################################################################
    
    for quantity in QUANTITIES:
        logger.info(f'Processing {quantity} for {casename}')
        
        writefile = writedir / (f'{casename}_{quantity}')
        if writefile.exists() and overwrite is False:
            logger.warning(f'{writefile} exists. Skipping {quantity.stem}.')
            continue
        
        for timefolder in timefolders:
            readfile = timefolder / quantity
            logger.debug(f'Reading {readfile}')
            data_for_current_time = np.genfromtxt(readfile, skip_header=1)
            if 'data_for_current_quantity' in locals():
                data_for_current_quantity = \
                    np.vstack((data_for_current_quantity,
                               data_for_current_time))
            else:
                data_for_current_quantity = data_for_current_time
            
            # data must be deleted for the next loop to work correctly
            del data_for_current_time
        
        data_for_current_quantity = \
            utils.remove_overlaps(data_for_current_quantity,0)
        
        if 'completedata' in locals():
            completedata = np.column_stack((completedata,
                                            data_for_current_quantity[:,2]))
        else:
            completedata = data_for_current_quantity
        
        # data must be deleted for the next loop to work correctly
        del data_for_current_quantity
    
    ############################################################################
    
    for i,_ in enumerate(QUANTITIES):
        average = utils.calculate_moving_average(completedata,i+2,1)
        completedata = np.column_stack((completedata,average))
    
    mag = np.linalg.norm(completedata[:,4:6],axis=1)
    completedata = np.column_stack((completedata,mag))
    
    writefile = writedir / (f'{casename}_sourceMomentum.gz')
    logger.debug(f'Saving file {writefile.name}')
    np.savetxt(writefile,completedata,header=HEADER,fmt='%.12g')
    
    # Report running average at specified times if requested
    if times_to_report is not None:
        time_indices = np.array([np.argmin(np.abs(completedata[:,0] - time))
                                for time in times_to_report])
        
        for i, time in np.ndenumerate(times_to_report):
            logger.info(f'Average after {time} s is '
                        f'{completedata[time_indices[i],-1]:.3e}')


################################################################################

if __name__ == '__main__':
    utils.configure_root_logger(level=LEVEL)
    
    description = "Stitch precursor source data and calculate running average"
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument('cases', help='list of cases to perform analysis for',
                        nargs='+')
    
    parser.add_argument("-t", "--times", help="What times to report",
                        nargs='*', type=int)
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed the command line arguments: {args}')
    
    for casename in args.cases:
        precursorSources(casename, args.times)
        