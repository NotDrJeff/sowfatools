#!/bin/python3

import logging
LEVEL = logging.DEBUG
logger = logging.getLogger(__name__)

import argparse

import numpy as np

import constants as const
import utils


################################################################################

def turbineOutputReduce(casename, N=10, blade_samples_to_keep = [0, -1],
                        quantities_to_keep=['powerRotor'], overwrite=False):
    """Extracts a reduced dataset from sowfatools/averaging for publishing and
    plotting purposes
    
    Written for python 3.12, SOWFA 2.4.x for sowfatools
    Jeffrey Johnston    NotDrJeff@gmail.com   June 2024.
    """
    
    casedir = const.CASES_DIR / casename
    readdirs = [casedir / const.TURBINEOUTPUT_DIR,
                casedir / const.SOWFATOOLS_DIR / 'turbineOutputAveraged']
    if all(not readdir.is_dir() for readdir in readdirs):
        logger.warning(f'Data directories do not exist. '
                       f'Skipping case {casename}.')
        return
    
    sowfatoolsdir = casedir / const.SOWFATOOLS_DIR
    logfilename = 'log.turbineOutputReduce'
    utils.configure_function_logger(sowfatoolsdir/logfilename, level=LEVEL)
    
    ############################################################################
    
    logger.info(f'Reducing turbineOutput for case {casename}')
    logger.info('')
    
    writedir = casedir / const.SOWFATOOLS_DIR / 'turbineOutputReduced'
    utils.create_directory(writedir)
    
    quantities,turbines,_ = utils.parse_turbineOutput_files(readdirs[0])
    
    ############################################################################
    
    for quantity in quantities_to_keep:
        
        if quantity not in quantities:
            logger.warning(f'{quantity} has no files in {readdirs[0]}. Skipping.')
            return
        
        for turbine in turbines:
            
            logger.debug(f'Reducing {casename}, {quantity}, turbine{turbine}')
            
            writefile = (writedir
                         / f'{casename}_{quantity}_turbine{turbine}_reduced.gz')
            
            if writefile.exists() and overwrite is False:
                logger.warning(f'{writefile.name} already exists. '
                               f'Skippping {quantity}.')
                logger.warning('')
                continue
            
            header = 'time '
            
            if quantity in const.TURBINE_QUANTITIES:
                filename = (readdirs[0]
                            / f'{casename}_{quantity}_turbine{turbine}.gz')
                
                logger.debug(f'Reading {filename}')
                data1 = np.genfromtxt(filename)
                
                filename = (readdirs[1]
                            / (f'{casename}_{quantity}_turbine{turbine}_'
                               f'averaged.gz'))
                
                logger.debug(f'Reading {filename}')
                data2 = np.genfromtxt(filename)
                
                idx = [2]
                header += f'{quantity} {quantity}_avg'
                
            elif quantity in const.BLADE_QUANTITIES:
                filename = readdirs[0] / (f'{casename}_{quantity}_'
                                        f'turbine{turbine}_blade0.gz')
                
                logger.debug(f'Reading {filename}')
                data1 = np.genfromtxt(filename)
                
                filename = (readdirs[1]
                            / (f'{casename}_{quantity}_turbine{turbine}_'
                               f'blade0_averaged.gz'))
                
                logger.debug(f'Reading {filename}')
                data2 = np.genfromtxt(filename)
                
                idx = [sample+2 for sample in blade_samples_to_keep]
                header += ' '.join([f'sample{sample} sample{sample}_avg'
                                    for sample in blade_samples_to_keep])
            
            rows = data1.shape[0]
            cols = idx.size + 1
            data = np.empty((rows,cols))
            data[:,0] = data1[:,0]
            for i in range(0,cols,2):
                data[:,i+1] = data1[:,idx(i)]
                data[:,i+2] = data2[:,idx(i)]
            
            org_size = data.shape
            data = data[::N,:] # keep time and selected samples (for blades)
            new_size = data.shape
            logger.debug(f"Reduced data from {org_size} to {new_size}")
            
            logger.info(f'Writing output to {writefile}')
            logger.info('')
            np.savetxt(writefile, data, fmt='%.4g', header=header)
            
            
################################################################################

if __name__=="__main__":
    utils.configure_root_logger(level=LEVEL)

    description = """Plot turbineOutput time histories"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('cases', help='list of cases to perform analysis for',
                        nargs='+')
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed the command line arguments: {args}')
    
    for casename in args.cases:
        turbineOutputReduce(casename)
