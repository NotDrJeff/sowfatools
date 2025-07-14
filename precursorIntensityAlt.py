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
LEVEL = logging.INFO
logger = logging.getLogger(__name__)

import argparse

import numpy as np

import constants as const
import utils


################################################################################

def precursorIntensityAlt(casename, width, starttime, overwrite=False):
    casedir = const.CASES_DIR / casename
    sowfatoolsdir = casedir / const.SOWFATOOLS_DIR
    endtime = starttime + width
    datadir = sowfatoolsdir / f'profiles_{starttime}_{endtime}'
    
    if not datadir.is_dir():
        logger.warning(f'{datadir} directory does not exist. '
                       f'Skipping {casename}.')
        return
    
    logfilename = 'log.precursorIntensityAlt'
    utils.configure_function_logger(sowfatoolsdir/logfilename, level=LEVEL)
    
    logger.info(f"Calculating Turbulence Intensity for {casename}")
    
    heights_to_report  = [const.TURBINE_HUB_HEIGHT - const.TURBINE_RADIUS,
                          const.TURBINE_HUB_HEIGHT,
                          const.TURBINE_HUB_HEIGHT + const.TURBINE_RADIUS]

    for quantity in ['uu_mean', 'vv_mean', 'ww_mean']:
        fname = datadir / f'{casename}_{quantity}_{starttime}_{endtime}.gz'
        logger.debug(f'Reading {fname}')
        rawdata = np.genfromtxt(fname)

        if 'uu' not in locals():
            heights = rawdata[:,0]
            uu = rawdata[:,1]
        else:
            uu += rawdata[:,1]
        
        del rawdata
    
    u_rms = np.sqrt(uu/3)
    TI = u_rms / const.MEAN_WIND_SPEED
    
    logger.info(f'Turbulence intensity based on hub mean velocity:')
                
    for i in heights_to_report:
        local_TI = np.interp(i,heights,TI)
        logger.info(f'  At {i:4,}m is {local_TI*100:.1f}%')


if __name__ == "__main__":
    utils.configure_root_logger(level=LEVEL)
    
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
    