#!/bin/python3
"""Written for Python 3.12, SOWFA 2.4.x
Part of github.com/NotDrJeff/sowfatools
Jeffrey Johnston    NotDrJeff@gmail.com     March 2024

Transforms vector quantities from SOWFA precursor averaging data into
streamwise and cross stream components, calculates their magnitude and angle.
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

def precursorTransform(casename, overwrite=True):
    
    casedir = const.CASES_DIR / casename
    sowfatoolsdir = casedir / const.SOWFATOOLS_DIR
    avgdir = sowfatoolsdir / 'averaging'  # Same directory for read and write
    
    if not avgdir.is_dir():
        logger.warning(f'{avgdir} directory does not exist. '
                       f'Skipping {casename}.')
        return
    
    logfilename = 'log.precursorTransform'
    utils.configure_function_logger(sowfatoolsdir/logfilename, level=LEVEL)
    
    ############################################################################

    logger.info(f'Transforming vectors for {casename}')
    
    QUANTITIES = {'U_mean'  : ('U_mean',  'V_mean',  'W_mean'),
                  'q_mean'  : ('q1_mean', 'q2_mean', 'q3_mean'),
                  'Tu_mean' : ('Tu_mean', 'Tv_mean', 'Tw_mean')}
    
    header_found = False
    for components in QUANTITIES.values():
        for component in components:
            readfile = avgdir/f'{casename}_{component}.gz'
            if readfile.is_file():
                with gzip.open(readfile,mode='rt') as f:
                    header = f.readline()
                    logger.debug(f'Using header from file {readfile}')
                    logger.debug(f'{header=}')
                header_found = True
                break
        if header_found: break
            
    if 'header' not in locals():
        logger.error('No file could be found to supply a header. Exiting.')
        raise FileNotFoundError(f'No relevant files found for case {casename}')
    
    header = header.removeprefix('# ').removesuffix('\n')
            
    ############################################################################
    
    for quantity,components in QUANTITIES.items():
        logger.info(f'Processing {quantity} for {casename}')
        
        outputfiles = [(avgdir / f'{casename}_{quantity}_{suffix}.gz')
                       for suffix in ('sw', 'cs', 'mag', 'dir')]
        
        if ( all([outputfile.exists() for outputfile in outputfiles])
             and overwrite is False ):
            logger.warning(f'Files already exist. Skippping {quantity}.')
            continue
        
        for i, component in enumerate(components):
            readfile = avgdir / f'{casename}_{component}.gz'
            logger.debug(f'Reading {readfile}')
            rawdata = np.loadtxt(readfile)
            
            if i == 0:
                data = np.empty((*rawdata.shape,4))

            data[:,:,i] = rawdata[:,:]
            del rawdata
            
        data[:,:,3] = data[:,:,0]
        
        logger.debug('Transforming vectors')
        for j in range(2,data.shape[1]):
            data[:,j,3] = 180 + np.degrees(np.arctan2(data[:,j,0], data[:,j,1]))
            data[:,j,:3] = const.WIND_ROTATION.apply(data[:,j,:3])
            
            # Replace vertical component with magnitude
            data[:,j,2] = np.linalg.norm(data[:,j,:],axis=-1)
            
        for i, outputfile in enumerate(outputfiles):
            logger.debug(f'Saving file {outputfile.name}')
            np.savetxt(outputfile,data[:,:,i],header=header, fmt='%.11e')

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

    logger.info(f'Finished transforming vectors for case {casename}')


################################################################################

if __name__ == '__main__':
    utils.configure_root_logger(level=LEVEL)

    description = """Calculate streamwise and cross-stream components of vector
                     quantities and their magnitude"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('cases', help='list of cases to perform analysis for',
                        nargs='+')
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed the command line arguments: {args}')
    
    for casename in args.cases:
        precursorTransform(casename)
        