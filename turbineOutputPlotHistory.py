#!/bin/python3

import logging
LEVEL = logging.DEBUG
logger = logging.getLogger(__name__)

import argparse
import sys
from pathlib import Path

import numpy as np
logging.getLogger('matplotlib').setLevel(logging.WARNING)
import matplotlib.pyplot as plt
            
import constants as const
import utils


################################################################################

def turbineOutputPlotHistory(casename, overwrite=False):
    """Reads turbineOutput from sowfatools directory and creates a plot for
    each time history.
    
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
    logfilename = 'log.turbineOutputPlotHistory'
    utils.configure_function_logger(sowfatoolsdir/logfilename, level=LEVEL)
    
    ############################################################################
    
    logger.info(f'Plotting turbineOutput for case {casename}')
    
    writedir = casedir / const.TURBINEPLOT_DIR
    utils.create_directory(writedir)
    
    files = list(readdir.iterdir())
    logger.info(f'Found {len(files)} files')
    logger.info('')
    
    ############################################################################
    
    filenames_parsed = []
    for file in files:
        
        if 'blade' in file.stem:
            filename_parsed = filename_parsed.replace('blade','')
            
        filename_parsed = file.stem.replace('turbine','')
        filename_parsed = filename_parsed.split('_')
        
        if 'blade' not in file.stem:
            filename_parsed.append('')
        
        filenames_parsed.append([file, *filename_parsed])
        del filename_parsed
        
    del files
            
    filenames_parsed.sort(key= lambda x: (x[2],x[3],x[4])) # qty,turbine,blade
    filenames_parsed = np.array(filenames_parsed)
    
    quantities = np.unique(filenames_parsed[:,2])
    turbines = np.unique(filenames_parsed[:,3])
    blades = np.unique(filenames_parsed[:,4])
    
    for quantity in quantities:
        logger.info(f'Plotting {quantity} for {casename}')
        writefile = writedir / f'{quantity}.png'
        
        for turbine in turbines:
            
            if quantity in 
        
        quantityfiles = filenames_parsed[]
        
        for file in files[np.logical_and(files[:,2]==quantity,
                                            np.logical_or(files[:,4]=='',
                                                        files[:,4]=='0'))]:
            logger.debug(f'Reading {file[0].name}')
            data = np.genfromtxt(file[0])
            
            if quantity in const.TURBINE_QUANTITIES:
                plt.plot(data[:,0],data[:,2],label=f'Turbine{file[3]}')
                plt.plot(data[:,0],data[:,3],
                            label=f'Turbine{file[3]},Average')
                
                plt.title(f'{quantity}, {casename}')
                plt.xlabel('Simulation Time')
                plt.legend()
                
                fname = outputdir / f'{casename}_{quantity}.png'
                logger.info(f'Saving file {fname.name}')   
                plt.savefig(fname)
                plt.close()
                
            elif quantity in const.BLADE_QUANTITIES:
                plt.plot(data[:,0],data[:,2],
                            label=f'Turbine{file[3]},Blade{file[4]},Root')
                plt.plot(data[:,0],data[:,3],
                            label=f'Turbine{file[3]},Blade{file[4]},Root,'
                                f'Average')
                plt.plot(data[:,0],data[:,-2],
                            label=f'Turbine{file[3]},Blade{file[4]},Tip')
                plt.plot(data[:,0],data[:,-1],
                            label=f'Turbine{file[3]},Blade{file[4]},Tip,'
                                f'Average')
                
                plt.title(f'{quantity}, {casename}')
                plt.xlabel('Simulation Time')
                plt.legend()
                
                fname = outputdir / f'{casename}_{quantity}.png'
                logger.info(f'Saving file {fname.name}')   
                plt.savefig(fname)
                plt.close()
                    
                    
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
    