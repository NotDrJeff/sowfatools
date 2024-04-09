#!/bin/python3

"""Written for python 3.12, SOWFA 2.4.x
Part of github.com/NotDrJeff/sowfatools
Jeffrey Johnston    NotDrJeff@gmail.com    March 2024

Calculates turbulence intensity from SOWFA precursor averaging data.
This version implements the approach described in Churchfield et al. 2012 which
uses time-averaged values of each velocity component in the calculation and uses
the hub height mean velocity as reference. For a more general approach, see
precursorIntensity.py

TI = sqrt[ 1/3 * (uu_mean_timeaveraged
                  + vv_mean_timeaveraged
                  + ww_mean_timeaveraged) ] / U_mean_hub

Takes a list of cases as command line arguments.
"""

import logging
LEVEL = logging.DEBUG
logger = logging.getLogger(__name__)

import argparse
from pathlib import Path
import gzip

import numpy as np

import sowfatools.constants as const
import sowfatools.utils as utils

################################################################################

def precursorIntensityAlt(casename, width, starttime, overwrite=False):
    casedir = const.CASES_DIR / casename
    sowfatooolsdir = casedir / const.SOWFATOOLS_DIR
    avgdir = sowfatooolsdir / 'averaging'
    deriveddir = sowfatooolsdir / 'derived'
    
    utils.configure_logging((sowfatooolsdir / f'log.{Path(__file__).stem}'),
                            level=LEVEL)
    
    utils.create_directory(deriveddir)
    
    logger.info(f"Calculating Turbulence Intensity for {casename}")
    
    endtime = starttime + width
    
    heights_to_report  = [const.TURBINE_HUB_HEIGHT - const.TURBINE_RADIUS,
                          const.TURBINE_HUB_HEIGHT,
                          const.TURBINE_HUB_HEIGHT + const.TURBINE_RADIUS]
    
    for quantity in ['U_mean', 'V_mean', 'W_mean']:
        fname = avgdir / f'{casename}_{quantity}_timeaveraged_{starttime}_{endtime}.gz'
        logger.debug(f'Reading {fname}')
        rawdata = np.genfromtxt(fname)
        
        if 'UU' not in locals():
            heights = rawdata[:,0]
            height_indices = [np.argmin(np.abs(height - heights))
                      for height in heights_to_report]
            
            UU = rawdata[height_indices[1],1]**2
        else:
            UU += rawdata[height_indices[1],1]**2

        del rawdata

    for quantity in ['uu_mean', 'vv_mean', 'ww_mean']:
        fname = avgdir / f'{casename}_{quantity}_timeaveraged_{starttime}_{endtime}.gz'
        logger.debug(f'Reading {fname}')
        rawdata = np.genfromtxt(fname)

        if 'uu' not in locals():
            uu = rawdata[:,1]
        else:
            uu += rawdata[:,1]
        
        del rawdata
    
    U = np.sqrt(UU)
    u_rms = np.sqrt(uu/3)
    TI = u_rms / U
    
    logger.info(f'Turbulence intensity based on hub mean velocity:')
                
    for i in height_indices:
        logger.info(f'  At {heights[i]:4,}m is {TI[i]*100:.1f}%')
    
    header = f'height_m TI_{starttime}_{endtime}'
        
    fname = deriveddir / (f'{casename}_TIalt_{starttime}_{endtime}.gz')
    logger.info(f'Saving file {fname.name}')
    np.savetxt(fname,TI,header=header)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""Calculate turbulence
                                                    intensity from
                                                    time-averaged data""")
    
    parser.add_argument("casename", help="specifiy which case to use")
    parser.add_argument("width", help="specifiy the time window width",
                        type=int)
    
    conflicts = parser.add_mutually_exclusive_group(required=True)

    conflicts.add_argument("-t", "--starttime",
                                help=f"Specify starttime for averaging",
                                type=int)
    
    args = parser.parse_args()
    
    precursorIntensityAlt(args.casename, args.width, args.starttime)
    