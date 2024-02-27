#!/bin/python3
"""Written for python 3.12 for the sowfatools package.
Jeffrey Johnston    NotDrJeff@gmail.com    February 2024.

Calculates time-average from sowfatools/averaging at every height.

The user must specify the casename and the time window width.

The user must also specify either a starttime or an offset.

Specifying a startime will mean one average is taken from that startime.

Specifying an offset means that multiple averages are taken, each one starting
an offset from the previous."""

import logging
import argparse
import gzip
from pathlib import Path

import numpy as np

import constants as const
import utils

logger = logging.getLogger(__name__)
LEVEL = logging.DEBUG

def main(casename: str, width: int, starttime=0, offset=None):    
    casedir = const.CASES_DIR / casename
    avgdir = casedir / const.SOWFATOOLS_DIR / 'averaging'
    
    # Set up logging
    
    if starttime is not None: # starttime_width mode
        endtime = starttime + width
        logfilename = f'log.{Path(__file__).stem}_{starttime}_{endtime}'
    else: # width_offset mode
        logfilename = f'log.{Path(__file__).stem}_w{width}_o{offset}'
    
    utils.configure_logging((avgdir / logfilename), level=LEVEL)
    
    logger.info(f'Processing averaging for case {casename}')
    
    # Find which quantities exist in the averaging directory
    
    quantities = set()
    for quantity in const.AVERAGING_QUANTITIES:
        filepath = avgdir/f'{casename}_{quantity}.gz'
        if (filepath.is_file()):
            quantities.add(quantity)
            
    logger.info(f'Found {len(quantities)} quantities')
    
    # Loop through each quantity
    
    first_quantity = True
    for quantity in quantities:
        filepath = avgdir/f'{casename}_{quantity}.gz'
        logger.info(f'Processing {quantity}')
        logger.debug(f'{filepath=}')
        fulldata = np.genfromtxt(filepath)
        
        # Some steps are only performed once, for first quantity.
        if first_quantity:
            
            # Read file header to get heights
            logger.debug('Reading heights from header')
            with gzip.open(filepath, mode='rt') as file:
                heights = file.readline().split()[3::2]
            heights = np.array([(i.split('_')[-1]) for i in heights],dtype=int)
            
            # Get lower and upper limits of data
            
            lower_limit = int( (fulldata[0,0,]//10) * 10 )
            
            if fulldata[-1,0] % 10 == 0:
                upper_limit = int( fulldata[-1,0] )
            else:
                upper_limit = int( ((fulldata[-1,0] // 10) + 1) * 10 )
            logger.info(f'Total data range is {lower_limit:,} - '
                        f'{upper_limit:,} s.')
            
            # Check starttime if necessary and set N_windows
            
            if starttime is not None: # starttime mode
                if (starttime < lower_limit) or (endtime > upper_limit):
                    logger.error('starttime and/or endtime are out of range. '
                                'Exiting')
                    raise ValueError
                
                N_windows = 1
                
            else: # offset mode
                N_windows = int( (upper_limit - lower_limit) // offset )
                logger.info(f'Identified {N_windows} windows to average')
                
            first_quantity = False
            
        # Repeat averaging for each time window
        
        header = 'heights_m'
        data_to_write = heights
        for i in range(N_windows):
            if N_windows > 1: # offset mode
                starttime = lower_limit + offset*i
                endtime = starttime + width
            
            startidx = np.argmin(np.abs(fulldata[:,0] - starttime))
            endidx = np.argmin(np.abs(fulldata[:,0] - endtime))
            
            logger.debug(f'Calculating time average for range '
                         f'{starttime:=7,} - {endtime:=7,} s')
            
            average_profile = np.average(fulldata[startidx:endidx+1,2::2],
                                         axis=0,
                                         weights=fulldata[startidx:endidx+1,1])
            
            # stack averages together for each time window
            data_to_write = np.column_stack((data_to_write,average_profile))
            header = header + f' {quantity}_{starttime}_{endtime}'
            
        # Save averages
        
        if N_windows == 1: # starttime_width mode
            filename = f'{casename}_{quantity}_timeaveraged_{starttime}_{endtime}.gz'
        else: # width_offset mode
            filename = f'{casename}_{quantity}_timeaveraged_w{width}_o{offset}.gz'
        
        filepath = avgdir/filename
        logger.info(f"Writing output to {filepath}")
        
        np.savetxt(filepath, data_to_write, fmt='%.3e', header=header)
        
    logger.info(f'Finished processing case {casename}.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""Calculate time-averaged
                                                    vertical profiles for
                                                    precursor averaging""")
    
    parser.add_argument("casename", help="specifiy which case to average")
    parser.add_argument("width", help="specifiy the time window width",
                        type=int)
    
    conflicts = parser.add_mutually_exclusive_group(required=True)

    conflicts.add_argument("-t", "--starttime",
                                help=f"Specify starttime for averaging",
                                type=int)
    
    conflicts.add_argument("-o", "--offset",
                             help=f"Specify offset of subsequent time window",
                             type=int)
    
    args = parser.parse_args()
    
    main(args.casename, args.width, args.starttime, args.offset)
