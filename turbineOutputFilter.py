#!/bin/python3

import logging
LEVEL = logging.INFO
logger = logging.getLogger(__name__)

import argparse

import numpy as np
import scipy.signal as sig

import constants as const
import utils


################################################################################

def turbineOutputFilter(casename, N=1000, blade_samples_to_keep = [27],
                        quantities_to_keep=['powerRotor'], overwrite=True):
    """Filters turbineOutput to create a smooth plot for publishing.
    Uses a gaussian filter with width N and standard deviation N/10.
    
    Written for python 3.12, SOWFA 2.4.x for sowfatools
    Jeffrey Johnston    NotDrJeff@gmail.com   June 2024.
    """
    
    casedir = const.CASES_DIR / casename
    readdir = casedir / const.TURBINEOUTPUT_DIR
    if not readdir.is_dir():
        logger.warning(f'Data directories do not exist. '
                       f'Skipping case {casename}.')
        return
    
    sowfatoolsdir = casedir / const.SOWFATOOLS_DIR
    logfilename = 'log.turbineOutputFilter'
    utils.configure_function_logger(sowfatoolsdir/logfilename, level=LEVEL)
    
    ############################################################################
    
    logger.info(f'Filtering turbineOutput for case {casename}')
    logger.info('')
    
    writedir = casedir / const.SOWFATOOLS_DIR / 'turbineOutputFiltered'
    utils.create_directory(writedir)
    
    quantities,turbines,_ = utils.parse_turbineOutput_files(readdir)
    
    ############################################################################
    
    for quantity in quantities_to_keep:
        
        if quantity not in quantities:
            logger.warning(f'{quantity} has no files in {readdir}. Skipping.')
            logger.warning('')
            return
        
        logger.info(f'Filtering {quantity} for case {casename}')
        
        for turbine in turbines:
            
            writefile = (writedir
                         /f'{casename}_{quantity}_turbine{turbine}_filtered.gz')
            if writefile.exists() and overwrite is False:
                logger.warning(f'{writefile.name} already exists. '
                               f'Skippping {quantity}.')
                logger.warning('')
                continue
            
            header = 'time '
            
            ####################################################################
            
            if quantity in const.TURBINE_QUANTITIES:
                filename = (readdir
                            / f'{casename}_{quantity}_turbine{turbine}.gz')
                
                logger.debug(f'Reading {filename}')
                data = np.genfromtxt(filename)
                
                filterwindow = sig.windows.gaussian(N,N/10)
                
                filtereddata = data[(N//2):-(N//2)+1,:]
                filtereddata[:,2] = sig.convolve(data[:,2],filterwindow,
                                                 mode='valid')
                filtereddata[:,2] /= sum(filterwindow)
                
                header += f'{quantity}'
                
            ####################################################################
                
            elif quantity in const.BLADE_QUANTITIES:
                filename = readdir / (f'{casename}_{quantity}_'
                                      f'turbine{turbine}_blade0.gz')
                
                logger.debug(f'Reading {filename}')
                data = np.genfromtxt(filename)
                
                filterwindow = sig.windows.gaussian(N,N/10)
                
                filtereddata = data[N//2,N//2,:]
                for i in range(2,data.shape[1]-2):
                    filtereddata[:,i] = sig.convolve(data[:,i],filterwindow,
                                                     mode='valid')
                filtereddata[:,2:] /= sum(filterwindow)
                
                header += ' '.join([f'sample{sample} '
                                    for sample in blade_samples_to_keep])
                
            ####################################################################
            
            logger.info(f'Writing output to {writefile}')
            logger.info('')
            np.savetxt(writefile, filtereddata, fmt='%.11e', header=header)
            
            
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
        turbineOutputFilter(casename)
