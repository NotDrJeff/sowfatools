#!/usr/bin/env python3

"""Compatible with Python 3.13, SOWFA 2.4.x
Part of github.com/NotDrJeff/sowfatools
Jeffrey Johnston   jeffrey.johnston@qub.ac.uk  July 2025

Calculates the available power for a wind turbine based on horizontally and
temporally averaged precursor data.

Takes a list of cases as command line arguments.
"""

import logging
import argparse

import numpy as np

import constants as const
import utils

LEVEL = logging.INFO
logger = logging.getLogger(__name__)

################################################################################

def precursorPower(casename : str, width : int, starttime=0):
    """Calculates the available power for a wind turbine based on horizontally
    and temporally averaged precursor data.
    """

    casedir = const.CASES_DIR / casename
    sowfatoolsdir = casedir / const.SOWFATOOLS_DIR
    endtime = starttime + width
    datadir = sowfatoolsdir / f'profiles_{starttime}_{endtime}'
    
    if not datadir.is_dir():
        logger.warning(f'{datadir} directory does not exist. '
                       f'Skipping {casename}.')
        return
    
    logfilename = 'log.precursorPower'
    utils.configure_function_logger(sowfatoolsdir/logfilename, level=LEVEL)
    
    logger.info(f"Calculating available power for {casename}")

    readfile = datadir / f'{casename}_U_mean_sw_{starttime}_{endtime}.gz'
    logger.debug(f'Reading {readfile}')
    data = np.genfromtxt(readfile)

    rotor_bottom = const.TURBINE_HUB_HEIGHT - const.TURBINE_RADIUS
    rotor_top    = const.TURBINE_HUB_HEIGHT + const.TURBINE_RADIUS
    
    data = data[(data[:,0]>=rotor_bottom) & (data[:,0]<=rotor_top),:]

    # Convert z coordinate into area weighting
    data[:,0] -= const.TURBINE_HUB_HEIGHT # shift data to center on 0
    dz = data[1,0] - data[0,0]
    data[:,0] = 2 * np.sqrt(const.TURBINE_RADIUS**2 - data[:,0]**2) * dz
        # 2 * half-width of rotor slice using equation of circle * height of slice

    power = 0.5 * const.AIR_DENSITY * np.sum(data[:,0]*data[:,1]**3) # Area*velocity^3
    
    logger.info('Predicted power for case %s is %.3f MW',
                casename, power/1e6)


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
    
    precursorPower(args.casename, args.width, args.starttime)
    