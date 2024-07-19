#!/bin/python3

import logging
LEVEL = logging.INFO
logger = logging.getLogger(__name__)

from pathlib import Path
import argparse

import numpy as np

import utils
import constants as const

CASESDIR = Path('/mnt/d/johnston_2024_thesis')

SCALAR_QUANTITIES = {'T', 'TAvg', 'Tprime', 'TTPrime2', 'TRMS', 'SourceT',
                     'p_rgh', 'p_rghAvg', 'Q',
                     'nuSgs', 'nuSGSmean', 'kSGS', 'kSGSmean', 'kResolved',
                     'omega', 'omegaAvg', 'kappat', 'epsilonSGSmean'}

VECTOR_QUANTITIES = {'U', 'UAvg', 'Uprime', 'uRMS', 'SourceU', 'phi',
                     'bodyForce', 'qmean', 'qwall'}

SYMMTENSOR_QUANTITIES = {'uuPrime2', 'uTPrime2', 'Rmean', 'Rwall'}

 
QUANTITIES_TO_KEEP = {'UAvg', 'Uprime', 'uuPrime2', 'kResolved'}

HORIZONTAL_LINE_LENGTH = 5


################################################################################

def turbineLineSample(casename, time, overwrite=False):
    #casedir = const.CASES_DIR / casename
    casedir = CASESDIR / casename
    if not casedir.is_dir():
        logger.warning(f'{casename} directory does not exist. Skipping.')
        return
    
    sowfatoolsdir = casedir / const.SOWFATOOLS_DIR
    utils.create_directory(sowfatoolsdir)
    
    logfilename = 'log.turbineLineSample'
    utils.configure_function_logger(sowfatoolsdir/logfilename, level=LEVEL)
    
    ############################################################################
    
    logger.info(f'Processing lineSample for case {casename}')
    
    readdir = casedir / 'postProcessing/lineSample' / time
    if not readdir.is_dir():
        logger.warning(f'{readdir.name} directory does not exist. Skipping.')
        return
    
    writedir = sowfatoolsdir / 'lineSample'
    utils.create_directory(writedir)
        
    filepaths = [file for file in readdir.iterdir()]
        
    logger.debug(f'Found {len(filepaths)} filenames')
    
    ############################################################################
    
    for filepath in filepaths:
        logger.debug(f'Processing file {filepath.name}')
        
        # Account for possible gzipped files
        if filepath.name.endswith('.gz'):
            filestem = filepath.name.removesuffix('.xy.gz')
        else:
            filestem = filepath.name.removesuffix('.xy')
            
        # Separate information in filename           
        fileparts = filestem.split('_')
        
        # Account for half diamters, e.g. lineV0_5
        if fileparts[1] == '5':
            linename = '_'.join(fileparts[:2])
            quantities_found = fileparts[2:]
        else:
            linename = fileparts[0]
            quantities_found = fileparts[1:] 
        
        # Account for p_rgh and p_rghAvg
        finished = False
        start_idx = 0
        while not finished:
            
            for i in range(start_idx,len(quantities_found)-1):
                if (quantities_found[i] == 'p'
                    and quantities_found[i+1].startswith('rgh')):
                    quantities_found[i] += quantities_found[i+1]
                    quantities_found.pop(i+1)
                    
                    start_idx = i+1
                    break
                
            if i == len(quantities_found)-2:
                finished  = True
        
        # Identify scalar, vector or tensor
        scalar = False
        vector = False
        tensor = False
        if quantities_found[0] in SCALAR_QUANTITIES:
            scalar = True
            quantities_to_keep = set.intersection(QUANTITIES_TO_KEEP,
                                                  SCALAR_QUANTITIES)
            
        elif quantities_found[0] in VECTOR_QUANTITIES:
            vector = True
            quantities_to_keep = set.intersection(QUANTITIES_TO_KEEP,
                                                  VECTOR_QUANTITIES)
            
        elif quantities_found[0] in SYMMTENSOR_QUANTITIES:
            tensor = True
            quantities_to_keep = set.intersection(QUANTITIES_TO_KEEP,
                                                  SYMMTENSOR_QUANTITIES)
            
        ########################################################################
        
        if not overwrite:
            files_exist = True
            for quantity in quantities_to_keep:
                writefile = (writedir / f'{linename}_{quantity}_{time}.gz')
                if not writefile.exists():
                    files_exist = False
            if files_exist:
                logger.warning(f'Files exist. skipping. ')
                continue
            
        data = np.loadtxt(filepath)
        
        if 'V' in linename: # continue # Not sure of coordinates yet   
            distance = data[:,0]
        elif 'H' in linename:
            distance = np.linspace(-HORIZONTAL_LINE_LENGTH/2,
                                   HORIZONTAL_LINE_LENGTH/2,
                                   data.shape[0])
        
        for quantity in quantities_to_keep:
            writefile = (writedir / f'{linename}_{quantity}_{time}.gz')
            if writefile.exists() and not overwrite:
                logger.warning(f'{writefile.name} exists. skipping. ')
                continue
            
            logger.info(f'Processing quantity {quantity}')
            if quantity not in quantities_found:
                logger.warning(f'{quantity} not found. Skipping')
                continue
            
            if scalar:
                idx = quantities_found.index(quantity) + 1
                data_to_write = np.column_stack((distance,data[:,idx]))
                
            elif vector:
                idx = (quantities_found.index(quantity) * 3) + 1
                data_to_write = np.column_stack((distance,data[:,idx]))
                for i in range(1,3):
                    data_to_write = np.column_stack((data_to_write,data[:,idx+i]))
                
            elif tensor:
                idx = (quantities_found.index(quantity) * 6) + 1
                data_to_write = np.column_stack((distance,data[:,idx]))
                for i in range(1,6):
                    data_to_write = np.column_stack((data_to_write,data[:,idx+i]))
            
            logger.debug(f'Saving file {writefile.name}')
            np.savetxt(writefile,data_to_write,fmt='%.11e')


################################################################################

if __name__=='__main__':
    utils.configure_root_logger(level=LEVEL)
    
    description = """Stitch lineSample data from different time directories"""
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument('cases', help='cases to perform analysis for',
                        nargs='+')
    parser.add_argument('-t','--times', help='times to perfrom analysis for',
                        nargs='+', required=True)
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed Command Line Arguments: {args}')
    
    for casename in args.cases:
        for time in args.times:
            turbineLineSample(casename,time)
        