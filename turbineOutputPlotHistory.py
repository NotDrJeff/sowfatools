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
    
    filenames_parsed = [''] * len(files)
    for i,file in enumerate(files):
        
        filenames_parsed[i] = file.stem.replace('turbine','')
        
        if 'blade' in file.stem:
            filenames_parsed[i] = filenames_parsed[i].replace('blade','')
            
        filenames_parsed[i] = filenames_parsed[i].split('_')
        
        if 'blade' not in file.stem:
            filenames_parsed[i].append('')
            
    filenames_parsed.sort(key= lambda x: (x[1],x[2],x[3])) # qty,turbine,blade
    filenames_parsed = np.array(filenames_parsed)
    
    quantities = np.unique(filenames_parsed[:,1])
    turbines = np.unique(filenames_parsed[:,2])
    blades = np.unique(filenames_parsed[:,3])
    blades = blades[blades != '']
    
    ############################################################################
    
    for i, quantity in np.ndenumerate(quantities):
        logger.debug(f'Plotting {quantity} for {casename}')
        writefile = writedir / f'{casename}_{quantity}.png'
        
        if writefile.exists():
            logger.warning(f'{writefile.name} already exists. '
                           f'Skippping {quantity}.')
            logger.warning('')
            continue
        
        for turbine in turbines:
            
            if quantity in const.TURBINE_QUANTITIES:
                filename = readdir / f'{casename}_{quantity}_turbine{turbine}.gz'
                
                logger.debug(f'Reading {filename}')
                try:
                    data = np.genfromtxt(filename)
                except FileNotFoundError:
                    logger.warning(f'File {filename} not found, skipping.')
                    continue
                
                plt.plot(data[:,0], data[:,2], alpha=0.3,
                         label=f'Turbine{turbine}')
                
            elif quantity in const.BLADE_QUANTITIES:
                filename = readdir / (f'{casename}_{quantity}_'
                                        f'turbine{turbine}_blade{blades[0]}.gz')
                
                logger.debug(f'Reading {filename}')
                try:
                    data = np.genfromtxt(filename)
                except FileNotFoundError:
                    logger.warning(f'File {filename} not found, skipping.')
                    continue
                
                plt.plot(data[:,0], data[:,-1], alpha=0.3,
                            label=f'Turbine{turbine},Blade{blades[0]},Tip')
                    
        ########################################################################
        
        plt.title(f'{quantity}, {casename}')
        plt.xlabel('Simulation Time')
        plt.legend()
        
        writefile = writedir / f'{casename}_{quantity}.png'
        logger.info(f'Saving file {writefile.name}')
        logger.info(f'')
        plt.savefig(writefile)
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
    