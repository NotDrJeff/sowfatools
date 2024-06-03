#!/bin/python3

import logging
LEVEL = logging.DEBUG
logger = logging.getLogger(__name__)

import argparse
import gzip

import numpy as np

import constants as const
import utils


################################################################################

def turbineOutputReduce(casename, N=10, blade_samples_to_keep = [0, -1],
                        quantities_to_keep=['powerRotor']):
    """Extracts a reduced dataset from sowfatools/averaging for publishing and
    plotting purposes
    
    Written for python 3.12, SOWFA 2.4.x for sowfatools
    Jeffrey Johnston    NotDrJeff@gmail.com   June 2024.
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
    
    logger.info(f'Reducing turbineOutput for case {casename}')
    logger.info('')
    
    writedir = casedir / const.SOWFATOOLS_DIR / 'turbineOutputReduced'
    utils.create_directory(writedir)
    
    files = list(readdir.iterdir())
    
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
    
    ############################################################################
    
    for quantity in quantities_to_keep:
        
        if quantity not in quantities:
            logger.warning(f'{quantity} has no files in {readdir}. Skipping.')
            return
        
        for turbine in turbines:
            
            logger.debug(f'Reducing {casename}, {quantity}, turbine{turbine}')
            
            writefile = (writedir
                         / f'{casename}_{quantity}_turbine{turbine}_reduced.gz')
            
            if writefile.exists():
                logger.warning(f'{writefile.name} already exists. '
                               f'Skippping {quantity}.')
                logger.warning('')
                continue
            
            idx = [0] # initialise list of column indices to keep.
            header = 'time '
            
            if quantity in const.TURBINE_QUANTITIES:
                filename = (readdir
                            / f'{casename}_{quantity}_turbine{turbine}.gz')
                
                logger.debug(f'Reading {filename}')
                try:
                    data = np.genfromtxt(filename)
                except FileNotFoundError:
                    logger.warning(f'File {filename} not found, skipping.')
                    continue
                
                idx += [2]
                header += f'{quantity}'
                
            elif quantity in const.BLADE_QUANTITIES:
                filename = readdir / (f'{casename}_{quantity}_'
                                        f'turbine{turbine}_blade0.gz')
                
                logger.debug(f'Reading {filename}')
                try:
                    data = np.genfromtxt(filename)
                except FileNotFoundError:
                    logger.warning(f'File {filename} not found, skipping.')
                    continue
                
                idx.extend(blade_samples_to_keep+2)
                header += ' '.join([f'sample{sample}'
                                    for sample in blade_samples_to_keep])
            
            org_size = data.shape
            data = data[::N,idx] # keep time and selected samples (for blades)
            new_size = data.shape
            logger.debug(f"Reduced data from {org_size} to {new_size}")
            
            logger.info(f'Writing output to {writefile}')
            logger.info('')
            np.savetxt(writefile, data, fmt='%.11e', header=header)
            
            
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
