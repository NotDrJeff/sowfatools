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

import sowfatools.constants as const
import sowfatools.utils as utils

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
    
    quantities = ['SourceUXHistory.gz','SourceUYHistory.gz','SourceUZHistory.gz']
    for quantity in quantities:
        logger.info(f'Processing {quantity} for {casename}')
        
        for timefolder in timefolders:
            fname = timefolder / quantity
            logger.debug(f'Reading {fname}')
            data_for_current_time = np.genfromtxt(fname, skip_header=1)
            if 'data_for_current_quantity' in locals():
                data_for_current_quantity = np.vstack((data_for_current_quantity,
                                                       data_for_current_time))
            else:
                data_for_current_quantity = data_for_current_time
            
            # data must be deleted for the next loop to work correctly
            del data_for_current_time
        
        data_for_current_quantity = utils.remove_overlaps(data_for_current_quantity,0)
        
        if 'completedata' in locals():
            completedata = np.column_stack((completedata,data_for_current_quantity[:,2]))
        else:
            completedata = data_for_current_quantity
        
        # data must be deleted for the next loop to work correctly
        del data_for_current_quantity
    
    header = 'time dt Smag Sang Smag_avg Smag_ang'
    
    mag = np.linalg.norm(completedata[:,2:],axis=1)
    ang = np.degrees(np.arctan2(completedata[:,3], completedata[:,2]))
    completedata = np.column_stack((completedata[:,:2],mag,ang))
    
    avgmag = utils.calculate_moving_average(completedata,2,1)
    avgang = utils.calculate_moving_average(completedata,3,1)
    completedata = np.column_stack((completedata,avgmag,avgang))
    
    fname = outputdir / (f'{casename}_sourceMomentum.gz')
    logger.debug(f'Saving file {fname.name}')
    np.savetxt(fname,completedata,header=header)
    
    # Report running average at specified times if requested
    if times_to_report is not None:
        time_indices = np.array([np.argmin(np.abs(completedata[:,0] - time))
                                for time in times_to_report])
        
        for i, time in np.ndenumerate(times_to_report):
            logger.info(f'Average after {time} s is '
                        f'{completedata[time_indices[i],4]:.3e} at '
                        f'{completedata[time_indices[i],5]:.1f}\N{DEGREE SIGN}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Process Precusor Source
                                                    Data and Calculate Running
                                                    Average""")
    
    parser.add_argument("casename", help="specifiy which case to use")
    
    parser.add_argument("-t", "--times", help="What times to report",
                        nargs='*', type=int)
    
    args = parser.parse_args()
    main(args.casename, args.times)