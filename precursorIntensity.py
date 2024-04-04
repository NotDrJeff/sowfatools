#!/bin/python3

"""Written for python 3.12, SOWFA 2.4.x
Part of github.com/NotDrJeff/sowfatools
Jeffrey Johnston    NotDrJeff@gmail.com    March 2024

Calculates turbulence intensity from SOWFA precursor averaging data.
This version calculates an intensity for each time step, using the mean
velocity at the local height. For an alternative formulation in line with
Churchfield et al. 2012, see precursorIntensityAlt.py

TI = rms(u)/U
   = sqrt[ 1/3 * (ux^2 + uy^2 + uz^2) ] / sqrt[ Ux^2 + Uy^2 + Uz^2 ]

Takes a list of cases as command line arguments.
"""

import logging
LEVEL = logging.INFO
logger = logging.getLogger(__name__)

import argparse
import gzip

import numpy as np

import constants as const
import utils


################################################################################

def precursorIntensity(casename, overwrite=False):
    
    casedir = const.CASES_DIR / casename
    sowfatoolsdir = casedir / const.SOWFATOOLS_DIR
    avgdir = sowfatoolsdir / 'averaging'
    
    if not avgdir.is_dir():
        logger.warning(f'{avgdir} directory does not exist. '
                       f'Skipping {casename}.')
        return
    
    logfilename = 'log.precursorIntensity'
    utils.configure_function_logger(sowfatoolsdir/logfilename, level=LEVEL)
    
    ############################################################################
    
    logger.info(f"Calculating turbulence intensity for {casename}")
    
    writefile = avgdir/f'{casename}_TI.gz'
    if writefile.exists() and overwrite is False:
        logger.warning(f'{writefile.name} already exists. '
                       f'Skippping {casename}.')
        return
    
    # We assume resolved mean velocity magnitude has already been calculated by
    # precursorTransform
    
    readfile = avgdir/f'{casename}_U_mean_mag.gz'
    if not readfile.is_file():
        logger.warning(f'{readfile.name} file does not exist. '
                       f'Skipping {casename}')
        return
       
    with gzip.open(readfile,mode='rt') as f:
        header = f.readline()
        
    header = header.removeprefix('# ').removesuffix('\n')
    
    logger.debug(f'Reading {readfile}')
    U = np.loadtxt(readfile)
        
    ############################################################################

    for quantity in ('uu_mean', 'vv_mean', 'ww_mean'):
        readfile = avgdir / f'{casename}_{quantity}.gz'
        if not readfile.is_file():
            logger.warning(f'{readfile.name} file does not exist. '
                           f'Skipping {casename}')
            return
        
        logger.debug(f'Reading {readfile}')
        rawdata = np.genfromtxt(readfile)
        
        if 'TI' not in locals():
            TI = rawdata
        else:
            TI[:,2:] += rawdata[:,2:]
        
        del rawdata
    
    TI[:,2:] = np.sqrt(TI[:,2:]/3) / U[:,2:]
    
    logger.info(f'Saving file {writefile.name}')
    np.savetxt(writefile,TI,header=header)


################################################################################

if __name__ == '__main__':
    utils.configure_root_logger(level=LEVEL)
    
    description="""Calculate turbulence intensity at every height"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('cases', help='list of cases to perform analysis for',
                        nargs='+')
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed the command line arguments: {args}')
    
    for casename in args.cases:
        precursorIntensity(casename)
        