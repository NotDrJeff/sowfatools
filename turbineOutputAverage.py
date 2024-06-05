#!/bin/python3

import logging
LEVEL = logging.INFO
logger = logging.getLogger(__name__)

import argparse
import gzip

import numpy as np

import constants as const
import utils


################################################################################

def turbineOutputAverage(casename, times_to_report=None,
                         blade_sample_to_report=27,overwrite=False):
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
    logfilename = 'log.turbineOutputAverage'
    utils.configure_function_logger(sowfatoolsdir/logfilename, level=LEVEL)
    
    ############################################################################
    
    logger.info(f'Calculating Average turbineOutput for case {casename}')
    logger.info('')
    
    writedir = casedir / const.SOWFATOOLS_DIR / 'turbineOutputAveraged'
    utils.create_directory(writedir)
    
    quantities,turbines,blades = utils.parse_turbineOutput_files(readdir)
    
    for quantity in quantities:
        logger.info(f'Processing {casename}, {quantity}')
        
        for turbine in turbines:
            logger.info(f'{casename}, {quantity}, turbine{turbine}')
            
            if quantity in const.TURBINE_QUANTITIES:
                
                writefile = writedir / (f'{casename}_{quantity}_'
                                        f'turbine{turbine}_averaged.gz')
                if (writefile.exists() and overwrite is False
                    and times_to_report is None):
                    logger.warning(f'{writefile.name} already exists. '
                                   f'Skippping.')
                    logger.warning('')
                    continue
                
                readfile = (readdir
                            / f'{casename}_{quantity}_turbine{turbine}.gz')
                logger.debug(f'Reading {readfile}')
                data = np.genfromtxt(readfile)
                
                with gzip.open(readfile,mode='rt') as f:
                        header = f.readline()
                        
                header = header.removeprefix('# ').removesuffix('\n')
                
                data[:,2] = utils.calculate_moving_average(data,2,1)
                
                if (not writefile.exists() or overwrite is True):
                    np.savetxt(writefile,data,fmt='%.12g',header=header)
                else:
                    logger.warning(f'{writefile.name} already exists. '
                                   f'Not overwriting.')
                
                if times_to_report is not None:
                    if 'time_idx' not in locals():
                        time_idx = utils.get_time_idx(data, times_to_report)
                        
                    data_to_report = data[time_idx,2]
                
            elif quantity in const.BLADE_QUANTITIES:
                
                for blade in blades:
                    
                    writefile = writedir / (f'{casename}_{quantity}_'
                                            f'turbine{turbine}_blade{blade}_'
                                            f'averaged.gz')
                    if (writefile.exists() and overwrite is False
                        and times_to_report is None):
                        logger.warning(f'{writefile.name} already exists. '
                                    f'Skippping.')
                        logger.warning('')
                        continue
                    
                    readfile = readdir / (f'{casename}_{quantity}_'
                                          f'turbine{turbine}_blade{blade}.gz')
                    logger.debug(f'Reading {readfile}')
                    data = np.genfromtxt(readfile)
                    
                    with gzip.open(readfile,mode='rt') as f:
                        header = f.readline()
                        
                    header = header.removeprefix('# ').removesuffix('\n')
                    
                    for i in range(2,data.shape[1]):
                        data[:,i] = utils.calculate_moving_average(data,i,1)
                    
                    if (not writefile.exists() or overwrite is True):
                        np.savetxt(writefile,data,fmt='%.12g',header=header)
                    else:
                        logger.warning(f'{writefile.name} already exists. '
                                       f'Not overwriting.')
                    
                    if times_to_report is not None:
                        if 'time_idx' not in locals():
                            time_idx = utils.get_time_idx(data, times_to_report)
                        
                        data_to_report = data[time_idx,blade_sample_to_report]
                        
            if times_to_report is not None:
                for i,time in enumerate(times_to_report):
                    logger.info(f'Average after {time} s is {data_to_report[i]:.5e}')
                    
                logger.info('')
                
    logger.info(f'Finished case {casename}')
    logger.info('')

################################################################################

if __name__ == '__main__':
    utils.configure_root_logger(level=LEVEL)

    description = "Calculate Running Average for turbineOutput"""
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument('cases', help='list of cases to perform analysis for',
                        nargs='+')
    
    parser.add_argument("-t", "--times", help="What times to report",
                        nargs='*', type=int)
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed the command line arguments: {args}')
    
    for casename in args.cases:
        turbineOutputAverage(casename, args.times)