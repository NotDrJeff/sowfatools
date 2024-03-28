#!/bin/python3
"""Written for Python 3.12
Jeffrey Johnston   NotDrJeff@gmail.com  March 2024"""

import logging
LEVEL = logging.INFO
logger = logging.getLogger(__name__)

import argparse
import gzip

import numpy as np

import constants as const
import utils


################################################################################

def precursorTransform(casenames):
    
    casedir = const.CASES_DIR / casename
    sowfatoolsdir = casedir / const.SOWFATOOLS_DIR
    avgdir = sowfatoolsdir / 'averaging'
    
    if not avgdir.is_dir():
        logger.warning(f'{avgdir} directory does not exist. Skipping.')
        return
    
    deriveddir = sowfatoolsdir / 'derived'
    utils.create_directory(deriveddir)
    
    filename = 'log.precursorTransform'
    utils.configure_function_logger(sowfatoolsdir/filename, level=LEVEL)
    
    ############################################################################

    logger.info(f'Transforming fields for {casename}')
    
    with gzip.open(avgdir/f'{casename}_U_mean.gz',mode='rt') as file:
        header = file.readline()
    
    heights = (header.removeprefix('#').split())[2:]
    heights = [height.rstrip('m') for height in heights]
    heights = np.array(heights).astype('int')
    
    QUANTITIES = (('U_mean', 'V_mean', 'W_mean'),
                  ('q1_mean', 'q2_mean', 'q3_mean'),
                  ('Tu_mean', 'Tv_mean', 'Tw_mean'))

    SUFFIXES = ('sw','cs')
    
    ############################################################################
    
    for quantity in QUANTITIES:
        
        for i, component in enumerate(quantity):  
            fname = avgdir / f'{casename}_{component}.gz'
            logger.debug(f'Reading {fname}')
            rawdata = np.genfromtxt(fname)

            if i == 0:
                data = np.empty((*rawdata,3))

            data[:,:,i] = rawdata[:,:]
            del rawdata
        
        for j in range(2,data.shape[1]):
            data[:,j,:] = const.WIND_ROTATION.apply(data[:,j,:])
            
        for i, component in enumerate(quantity):
            fname = avgdir / (f'{casename}_{component}_{SUFFIXES[i]}.gz')
            logger.debug(f'Saving file {fname.name}')
            np.savetxt(fname,data[:,:,i],header=header)

        del data

    # add symmtensor rotations later
    # R11_mean    R12_mean    R13_mean
    #             R22_mean    R23_mean
    #                         R33_mean

    # uu_mean     uv_mean     uw_mean
    #             vv_mean     vw_mean
    #                         ww_mean

    # wuu_mean    wuv_mean    wuw_mean
    #             wvv_mean    wvw_mean
    #                         www_mean

    logger.info(f'Finished processing averaging for case {casename}')


################################################################################

if __name__ == "__main__":
    utils.configure_root_logger(level=LEVEL)

    description = """Calculate Streamwise and Cross-stream Components"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('cases', help='list of cases to perform analysis for',
                        nargs='+')
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed the command line arguments: {args}')
    
    for casename in args.cases:
        precursorTransform(casename)
        