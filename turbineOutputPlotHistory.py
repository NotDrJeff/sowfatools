#!/bin/python3

import logging
LEVEL = logging.DEBUG
logger = logging.getLogger(__name__)

import argparse

import numpy as np
logging.getLogger('matplotlib').setLevel(logging.WARNING)
import matplotlib.pyplot as plt

import constants as const
import utils


################################################################################

def turbineOutputPlotHistory(casename, overwrite=False):
    """Reads turbineOutput from sowfatools directory and creates a plot for
    each time history a with running average.
    
    Written for Python 3.12, SOWFA 2.4.x for sowfatools
    Jeffrey Johnston    NotDrJeff@gmail.com    May 2024
    """
    
    casedir = const.CASES_DIR / casename
    readdir_raw = casedir / const.TURBINEOUTPUT_DIR
    if not readdir_raw.is_dir():
        logger.warning(f'{readdir_raw.stem} directory does not exist. '
                       f'Skipping case {casename}.')
        return
    
    readdir_avg = casedir / const.SOWFATOOLS_DIR / 'turbineOutputAveraged'
    if not readdir_avg.is_dir():
        logger.warning(f'{readdir_avg.stem} directory does not exist. '
                       f'Skipping case {casename}.')
        return
    
    sowfatoolsdir = casedir / const.SOWFATOOLS_DIR
    logfilename = 'log.turbineOutputPlotHistory'
    utils.configure_function_logger(sowfatoolsdir/logfilename, level=LEVEL)
    
    ############################################################################
    
    logger.info(f'Plotting turbineOutput for case {casename}')
    
    writedir = casedir / const.TURBINEPLOT_DIR
    utils.create_directory(writedir)
    
    quantities,turbines,_ = utils.parse_turbineOutput_files(readdir_raw)
    
    ############################################################################
    
    for i, quantity in np.ndenumerate(quantities):
        logger.debug(f'Plotting {quantity} for {casename}')
        writefile = writedir / f'{casename}_{quantity}.png'
        
        if writefile.exists() and overwrite is False:
            logger.warning(f'{writefile.name} already exists. '
                           f'Skippping {quantity}.')
            logger.warning('')
            continue
        
        for turbine in turbines:
            
            if quantity in const.TURBINE_QUANTITIES:
                filename = (readdir_raw
                            / f'{casename}_{quantity}_turbine{turbine}.gz')
                logger.debug(f'Reading {filename}')
                data = np.genfromtxt(filename)
                
                plt.plot(data[:,0], data[:,2], alpha=0.3,
                         label=f'Turbine{turbine}')
                
                filename = (readdir_avg
                            / f'{casename}_{quantity}_turbine{turbine}.gz')
                logger.debug(f'Reading {filename}')
                data = np.genfromtxt(filename)
                
                plt.plot(data[:,0], data[:,2],
                         label=f'Turbine{turbine} (Avg)')
                
            elif quantity in const.BLADE_QUANTITIES:
                filename = readdir_raw / (f'{casename}_{quantity}_'
                                        f'turbine{turbine}_blade0.gz')
                logger.debug(f'Reading {filename}')
                data = np.genfromtxt(filename)
                
                plt.plot(data[:,0], data[:,-1], alpha=0.3,
                            label=f'Turbine{turbine},Blade0,Tip')
                
                filename = readdir_avg / (f'{casename}_{quantity}_'
                                        f'turbine{turbine}_blade0.gz')
                logger.debug(f'Reading {filename}')
                data = np.genfromtxt(filename)
                
                plt.plot(data[:,0], data[:,-1],
                         label=f'Turbine{turbine},Blade0,Tip (Avg)')
                    
        ########################################################################
        
        plt.title(f'{quantity}, {casename}')
        plt.xlabel('Simulation Time')
        plt.legend()
        
        writefile = writedir / f'{casename}_{quantity}.png'
        logger.info(f'Saving file {writefile.name}')
        logger.info(f'')
        plt.savefig(writefile)
        plt.cla()
        
         
if __name__ == "__main__":
    utils.configure_root_logger(level=LEVEL)

    description = """Plot turbineOutput time histories"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('cases', help='list of cases to perform analysis for',
                        nargs='+')
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed the command line arguments: {args}')
    
    for casename in args.cases:
        turbineOutputPlotHistory(casename)
    