#!/bin/python3

"""Written for python 3.12 for the sowfatools package.
Jeffrey Johnston    NotDrJeff@gmail.com    March 2024.

Calculates turbulence intensity from sowfatools/averaging data.

The user must specify the casename.

This version calculates an intensity for each time step, using the mean
velocity at the local height. For an alternative formulation in line with
Churchfield et al. 2012, see precursorIntensityAlt.py

TI = rms(u)/U
   = sqrt[ 1/3 * (ux^2 + uy^2 + uz^2) ] / sqrt[ Ux^2 + Uy^2 + Uz^2 ]
   
"""

import logging
import argparse
from pathlib import Path
import gzip

import numpy as np

import constants as const
import utils

logger = logging.getLogger(__name__)
LEVEL = logging.INFO

def main(casename: str):
    casedir = const.CASES_DIR / casename
    sowfatooolsdir = casedir / const.SOWFATOOLS_DIR
    avgdir = sowfatooolsdir / 'averaging'
    deriveddir = sowfatooolsdir / 'derived'
    
    utils.configure_logging((sowfatooolsdir / f'log.{Path(__file__).stem}'),
                            level=LEVEL)
    
    utils.create_directory(deriveddir)
    
    logger.info(f"Calculating Turbulence Intensity for {casename}")
    
    with gzip.open(avgdir/f'{casename}_uu_mean.gz',mode='rt') as file:
        heights = (file.readline().removeprefix('#').split())
    
    heights = [height.split('_')[-1] for height in heights[2::2]]
    heights = np.array(heights).astype('int')
    
    heights_to_report  = [const.TURBINE_HUB_HEIGHT - const.TURBINE_RADIUS,
                          const.TURBINE_HUB_HEIGHT,
                          const.TURBINE_HUB_HEIGHT + const.TURBINE_RADIUS]
    
    height_indices = [np.argmin(np.abs(height - heights))
                      for height in heights_to_report]
    
    for quantity in ['U_mean', 'V_mean', 'W_mean']:
        fname = avgdir / f'{casename}_{quantity}.gz'
        logger.debug(f'Reading {fname}')
        rawdata = np.genfromtxt(fname)
        
        if 'UU' not in locals():
            UU = rawdata
            UU[:, 3::2] = 0 # we will ignore average columns
            UU[:, 2::2] = rawdata[:,2::2]
            UU[:, 2::2] **= 2
            
            TI = np.zeros(rawdata.shape)
            TI[:,:2] = rawdata[:,:2] 
        else:
            UU[:, 2::2] += rawdata[:,2::2]**2

        del rawdata

    for quantity in ['uu_mean', 'vv_mean', 'ww_mean']:
        fname = avgdir / f'{casename}_{quantity}.gz'
        logger.debug(f'Reading {fname}')
        rawdata = np.genfromtxt(fname)

        if 'uu' not in locals():
            uu = rawdata
            uu[:, 3::2] = 0 # we will ignore average columns
            uu[:, 2::2] = rawdata[:,2::2]
        else:
            uu[:, 2::2] += rawdata[:,2::2]
        
        del rawdata
    
    TI[:, 2::2] = np.sqrt(uu[:, 2::2]/3) / np.sqrt(UU[:, 2::2])
    
    logger.info(f'Turbulence intensity based on local mean velocity:')
                
    for i in height_indices:
        logger.info(f'  At {heights[i]:4,}m at {TI[-1,0]:,.2f} s '
                    f'  is {TI[-1,2*i+2]*100:.1f}%')
        
    header = 'time dt '
    header += ' '.join([f'TI_{height}m NULL' for height in heights])
        
    fname = deriveddir / (f'{casename}_TI.gz')
    logger.info(f'Saving file {fname.name}')
    np.savetxt(fname,TI,header=header)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""Calculate turbulence
                                                    intensity for precursor""")
    parser.add_argument("casename", help="specifiy which case to use")
    args = parser.parse_args()
    
    main(args.casename)
    