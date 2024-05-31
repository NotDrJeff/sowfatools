#!/bin/python3

import logging
LEVEL = logging.INFO
logger = logging.getLogger(__name__)

import argparse
from pathlib import Path

import numpy as np

import constants as const
import utils


################################################################################

def turbineAveragePower(casename, times_to_report):
    """Reads powerRotor from sowfatools directory, calculates a running average
    and reports at requested times.
    
    Written for Python 3.12, SOWFA 2.4.x for sowfatools
    Jeffrey Johnston    NotDrJeff@gmail.com    May 2024
    """
    
    casedir = const.CASES_DIR / casename
    readdir = casedir / const.TURBINEOUTPUT_DIR
    if not readdir.is_dir():
        logger.warning(f'{readdir.stem} directory does not exist. '
                       f'Skipping case {casename}.')
        return
    
    sowfatoolsdir = casedir / const.SOWFATOOLS_DIR
    logfilename = 'log.turbineAveragePower'
    utils.configure_function_logger(sowfatoolsdir/logfilename, level=LEVEL)
    
    ############################################################################
    
    logger.info(f'Processing turbineOutput for case {casename}')
    
    quantities = set()
    for file in readdir.iterdir():
        if 'powerRotor' in file.name:
            quantities.add(Path(file.name))
    
    for quantity in quantities:
        logger.info(f'Processing {quantity.stem} for {casename}')
        readfile = readdir / quantity
        logger.debug(f'Reading {readfile}')
        data = np.genfromtxt(readfile)
        
        average = utils.calculate_moving_average(data,2,1)
        
        time_idx = [np.argmin(np.abs((data[:,0]-time)))
                    for time in times_to_report]
        
        for i,idx in enumerate(time_idx):
            label = readfile.stem.removeprefix(f'{casename}_powerRotor_')
            logger.info(f'Average power for {label} after '
                        f'{times_to_report[i]} s is {average[idx]/10**6} MW')

################################################################################

if __name__ == '__main__':
    utils.configure_root_logger(level=LEVEL)

    description = "Calculate Running Average for powerRotor"""
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument('cases', help='list of cases to perform analysis for',
                        nargs='+')
    
    parser.add_argument("-t", "--times", help="What times to report",
                        nargs='*', type=int, required=True)
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed the command line arguments: {args}')
    
    for casename in args.cases:
        turbineAveragePower(casename, args.times)