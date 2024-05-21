#!/bin/python3

"""Written for python 3.12, SOWFA 2.4.x
Part of github.com/NotDrJeff/sowfatools
Jeffrey Johnston    NotDrJeff@gmail.com    May 2024

Calculates change in velocity magnitude and direction across rotor

Takes a list of cases as command line arguments.
"""

import logging
LEVEL = logging.DEBUG
logger = logging.getLogger(__name__)

import argparse

import numpy as np

import constants as const
import utils


################################################################################

def precursorVelocityChange(casename, width, starttime, overwrite=False):
    casedir = const.CASES_DIR / casename
    sowfatoolsdir = casedir / const.SOWFATOOLS_DIR
    endtime = starttime + width
    datadir = sowfatoolsdir / f'profiles_{starttime}_{endtime}'
    
    if not datadir.is_dir():
        logger.warning(f'{datadir} directory does not exist. '
                       f'Skipping {casename}.')
        return
    
    logfilename = 'log.precursorTransform'
    utils.configure_function_logger(sowfatoolsdir/logfilename, level=LEVEL)
    
    ############################################################################
    
    heights_to_report  = [const.TURBINE_HUB_HEIGHT - const.TURBINE_RADIUS,
                          const.TURBINE_HUB_HEIGHT + const.TURBINE_RADIUS,
                          const.DOMAIN_HEIGHT]

    # Magnitude
    fname = datadir / f'{casename}_U_mean_mag_{starttime}_{endtime}.gz'
    logger.debug(f'Reading {fname}')
    data = np.genfromtxt(fname)
    U = np.interp(heights_to_report[:2],data[:,0],data[:,1])
    
    logger.info(f'Wind speed at bottom of Rotor: {U[0]:.2f} m/s')
    logger.info(f'Wind speed at top of Rotor: {U[1]:.2f} m/s')
    logger.info(f'    Difference is {(U[1]-U[0]):.2f} m/s')
    
    # Direction
    fname = datadir / f'{casename}_U_mean_dir_{starttime}_{endtime}.gz'
    logger.debug(f'Reading {fname}')
    data = np.genfromtxt(fname)            
    theta = np.interp(heights_to_report[:2],data[:,0],data[:,1])
    
    logger.info(f'Wind direction at bottom of Rotor: {theta[0]:.2f} \N{DEGREE SIGN}')
    logger.info(f'Wind direction at top of Rotor: {theta[1]:.2f} \N{DEGREE SIGN}')
    logger.info(f'    Difference is {(theta[1]-theta[0]):.2f} \N{DEGREE SIGN}')
    
    # Geodtrophic Wind
    fname = datadir / f'{casename}_U_mean_{starttime}_{endtime}.gz'
    logger.debug(f'Reading {fname}')
    data = np.genfromtxt(fname)
    U = np.interp(heights_to_report[2],data[:,0],data[:,1])
    
    fname = datadir / f'{casename}_V_mean_{starttime}_{endtime}.gz'
    logger.debug(f'Reading {fname}')
    data = np.genfromtxt(fname)           
    V = np.interp(heights_to_report[2],data[:,0],data[:,1])
    
    logger.info(f'Geostrophic Wind is ({U:.2f}, {V:.2f}) m/s')


if __name__ == "__main__":
    utils.configure_root_logger(level=LEVEL)
    
    parser = argparse.ArgumentParser(description="""Calculate velocity change
                                                    across rotor""")
    
    parser.add_argument("casename", help="specifiy which case to use")
    parser.add_argument("width", help="specifiy the time window width",
                        type=int)
    
    conflicts = parser.add_mutually_exclusive_group(required=True)

    conflicts.add_argument("-t", "--starttime",
                                help=f"Specify starttime for averaging",
                                type=int)
    
    args = parser.parse_args()
    
    precursorVelocityChange(args.casename, args.width, args.starttime)
    