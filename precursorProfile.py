#!/bin/python3
"""Written for python 3.12, SOWFA 2.4.x
Part of github.com/NotDrJeff/sowfatools
Jeffrey Johnston    NotDrJeff@gmail.com    February 2024

Calculates time-average from SOWFA precursor averaging files for every height.
The casename and the time window width must be specified as command line
arguments. The user must also specify either a starttime or an offset.
Specifying a startime will mean one average is taken from that startime.
Specifying an offset means that multiple averages are taken, each one starting
an offset from the previous.
"""

import logging
LEVEL = logging.DEBUG
logger = logging.getLogger(__name__)

import argparse
import gzip
from pathlib import Path

import numpy as np

import constants as const
import utils


################################################################################

def precursorProfile(casename: str, width: int, starttime=None, offset=None,
                     overwrite=False):    
    
    casedir = const.CASES_DIR / casename
    sowfatoolsdir = casedir / const.SOWFATOOLS_DIR
    readdir = sowfatoolsdir / 'averaging'
    if not readdir.is_dir():
        logger.warning(f'{readdir} directory does not exist. '
                       f'Skipping {casename}.')
        return
    
    if offset is None and starttime is not None:
        starttime_mode = True
    elif starttime is None and offset is not None:
        starttime_mode = False
    else:
        logger.error('Both starttime and offset cannot be used at the same time')
        raise ValueError('Incompatible arguments')
    
    if starttime_mode:
        endtime = starttime + width
        logfilename = f'log.precursorProfile_{starttime}_{endtime}'
        writedir = sowfatoolsdir / f'profiles_{starttime}_{endtime}'
    else:
        logfilename = f'log.precursorProfile_w{width}_o{offset}'
        writedir = sowfatoolsdir / f'profiles_w{width}_o{offset}'
        
    utils.configure_function_logger(sowfatoolsdir/logfilename, level=LEVEL)
    
    ############################################################################
    
    logger.info(f'Creating profiles for case {casename}')
    
    utils.create_directory(writedir)
    
    readfiles = [readfile for readfile in readdir.iterdir()]
    logger.info(f'Found {len(readfiles)} quantities')
    
    logger.debug(f'Reading heights from {readfiles[0].name}')
    with gzip.open(readfiles[0], mode='rt') as f:
        heights = f.readline().split()[3:]
    heights = np.array([i.removesuffix('m') for i in heights],dtype=int)
    
    ############################################################################
    
    first_readfile = True
    for readfile in readfiles:
        quantity = readfile.stem.removeprefix(f'{casename}_')
        logger.info(f'Processing {quantity}')
        
        if starttime_mode:
            writefile = writedir / f'{readfile.stem}_{starttime}_{endtime}.gz'
            header = f'heights_m {starttime}_{endtime}'
        else: # offset mode
            writefile = writedir / f'{readfile.stem}_w{width}_o{offset}.gz'
            header = 'heights_m'
        
        if writefile.exists() and overwrite is False:
            logger.warning(f'{writefile.name} already exists. '
                           f'Skippping {casename}.')
            continue
        
        logger.debug(f'Reading {readfile}')
        fulldata = np.genfromtxt(readfile)
        
        ########################################################################
        
        if first_readfile:
            lower_time_limit = int( (fulldata[0,0]//10) * 10 )
            
            if fulldata[-1,0] % 10 == 0:
                upper_time_limit = int( fulldata[-1,0] )
            else:
                upper_time_limit = int( ((fulldata[-1,0] // 10) + 1) * 10 )
                
            logger.info(f'Total data range is {lower_time_limit:,} - '
                        f'{upper_time_limit:,} s.')
            
            if starttime_mode:
                if (starttime < lower_time_limit) or (endtime > upper_time_limit):
                    logger.error('starttime and/or endtime are out of range. '
                                'Exiting')
                    raise ValueError
                
                N_windows = 1
                
            else:
                N_windows = int( (upper_time_limit - lower_time_limit) // offset )
                logger.info(f'Identified {N_windows} windows to average')
                
            first_readfile = False
            
        ########################################################################
        
        data_to_write = heights
        for i in range(N_windows):
            if not starttime_mode:
                starttime = lower_time_limit + offset*i
                endtime = starttime + width
                header = header + f' {starttime}_{endtime}'
            
            startidx = np.argmin(np.abs(fulldata[:,0] - starttime))
            endidx = np.argmin(np.abs(fulldata[:,0] - endtime))
            
            logger.debug(f'Calculating time average for range '
                         f'{starttime:=7,} - {endtime:=7,} s')
            
            average_profile = np.average(fulldata[startidx:endidx+1,2:],
                                         axis=0,
                                         weights=fulldata[startidx:endidx+1,1])
            
            data_to_write = np.column_stack((data_to_write,average_profile))
        
        logger.info(f"Saving file {writefile}")
        np.savetxt(writefile, data_to_write, fmt='%.12g', header=header)
        
    logger.info(f'Finished processing case {casename}.')


################################################################################

if __name__ == '__main__':
    utils.configure_root_logger(level=LEVEL)
    
    description="""Calculate time-averaged vertical profiles"""
    parser = argparse.ArgumentParser(description=description)
    
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
    
    precursorProfile(args.casename, args.width, args.starttime, args.offset)
