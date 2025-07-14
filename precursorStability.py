#!/usr/bin/env python3

"""Compatible with Python 3.13, SOWFA 2.4.x
Part of github.com/NotDrJeff/sowfatools
Jeffrey Johnston   jeffrey.johnston@qub.ac.uk  July 2025

Contains functions for calculating stability parameters from precursor
averaging data, including gradient and flux richardson numbers, Obukhov length.
Assumes data has been stitched with precursorAveraging.py

As a script, all derived quantities will be calculated.
Takes a list of cases as command line arguments.
"""

import logging

import argparse
import gzip

import numpy as np

import constants as const
import utils

LEVEL = logging.INFO
logger = logging.getLogger(__name__)


################################################################################

def precursor_richardson_gradient(casename, overwrite=False):
    """Calculates gradient Richardson number from SOWFA precursor averaging data.

    Ri = (g/theta)*(dtheta/dz) / ((dU/dz)^2+(dV/dz)^2)
    """

    casedir = const.CASES_DIR / casename
    sowfatoolsdir = casedir / const.SOWFATOOLS_DIR
    avgdir = sowfatoolsdir / 'averaging'

    if not avgdir.is_dir():
        logger.warning('%s directory does not exist. '
                       'Skipping %s.',
                       avgdir,casename)
        return

    logfilename = 'log.precursorRichardsonGradient'
    utils.configure_function_logger(sowfatoolsdir/logfilename, level=LEVEL)

    ############################################################################

    logger.info("Calculating gradient Richardson number for %s", casename)

    writefile = avgdir/f'{casename}_Ri.gz'
    if writefile.exists() and overwrite is False:
        logger.warning('%s already exists. Skippping %s.',
                       writefile.name, casename)
        return

    quantities = ['U_mean', 'V_mean', 'T_mean']
    readfiles = [avgdir/f'{casename}_{quantity}.gz' for quantity in quantities]
    for readfile in readfiles:
        if not readfile.is_file():
            logger.warning('%s file does not exist. Skipping %s',
                        readfile.name, casename)
            return

    logger.debug('Getting heights')
    with gzip.open(readfiles[0],mode='rt') as f:
        header = f.readline()
    header = header.removeprefix('# ').removesuffix('\n')
    z = np.array([float(height.removesuffix('m'))
                  for height in header.split()[2:]]) # exclude time and dt column

    logger.debug('Reading %s', readfiles[0])
    U = np.loadtxt(readfiles[0])

    logger.debug('Reading %s', readfiles[1])
    V = np.loadtxt(readfiles[1])

    logger.debug('Reading %s', readfiles[2])
    T = np.loadtxt(readfiles[2])

    ############################################################################

    # Estimate gradients in z

    dz = z[1:] - z[:-1]

    dUdz = np.empty((U.shape[0],U.shape[1]-1)) # Ignore final height
    dUdz[:,:2] = U[:,:2] # Time and dt columns
    dUdz[:,2:] = (U[:,3:] - U[:,2:-1]) / dz

    dVdz = np.empty((V.shape[0],V.shape[1]-1)) # Ignore final height
    dVdz[:,:2] = V[:,:2] # Time and dt columns
    dVdz[:,2:] = (V[:,3:] - V[:,2:-1]) / dz

    dTdz = np.empty((T.shape[0],T.shape[1]-1)) # Ignore final height
    dTdz[:,:2] = T[:,:2] # Time and dt columns
    dTdz[:,2:] = (T[:,3:] - T[:,2:-1]) / dz

    Ri = np.empty(dUdz.shape)
    Ri[:,:2] = dUdz[:,:2]
    Ri[:,2:] = ((const.g/T[:,2:-1]) * dTdz[:,2:]) / (dUdz[:,2:]**2 + dVdz[:,2:]**2)

    header = " ".join(header.split()[:-1])

    logger.info('Saving file %s',writefile.name)
    np.savetxt(writefile,Ri,header=header,fmt='%.12g')

################################################################################

def precursor_richardson_flux(casename, overwrite=False):
    """Calculates flux Richardson number from SOWFA precursor averaging data.

    Rf = (g/theta)*(w'theta') / (u'w'(dU/dz)+v'w'(dV/dz))
    """

    casedir = const.CASES_DIR / casename
    sowfatoolsdir = casedir / const.SOWFATOOLS_DIR
    avgdir = sowfatoolsdir / 'averaging'

    if not avgdir.is_dir():
        logger.warning('%s directory does not exist. '
                       'Skipping %s.',
                       avgdir,casename)
        return

    logfilename = 'log.precursorRichardsonFlux'
    utils.configure_function_logger(sowfatoolsdir/logfilename, level=LEVEL)

    ############################################################################

    logger.info("Calculating flux Richardson number for %s", casename)

    writefile = avgdir/f'{casename}_Rf.gz'
    if writefile.exists() and overwrite is False:
        logger.warning('%s already exists. Skippping %s.',
                       writefile.name, casename)
        return

    quantities = ['U_mean', 'V_mean', 'T_mean', 'uw_mean','vw_mean','Tw_mean']
    readfiles = [avgdir/f'{casename}_{quantity}.gz' for quantity in quantities]
    for readfile in readfiles:
        if not readfile.is_file():
            logger.warning('%s file does not exist. Skipping %s',
                        readfile.name, casename)
            return

    logger.debug('Getting heights')
    with gzip.open(readfiles[0],mode='rt') as f:
        header = f.readline()
    header = header.removeprefix('# ').removesuffix('\n')
    z = np.array([float(height.removesuffix('m'))
                  for height in header.split()[2:]]) # exclude time and dt column

    logger.debug('Reading %s', readfiles[0])
    U = np.loadtxt(readfiles[0])

    logger.debug('Reading %s', readfiles[1])
    V = np.loadtxt(readfiles[1])

    logger.debug('Reading %s', readfiles[2])
    T = np.loadtxt(readfiles[2])

    logger.debug('Reading %s', readfiles[3])
    uw = np.loadtxt(readfiles[3])

    logger.debug('Reading %s', readfiles[4])
    vw = np.loadtxt(readfiles[4])

    logger.debug('Reading %s', readfiles[5])
    Tw = np.loadtxt(readfiles[5])

    ############################################################################

    # Estimate gradients in z

    dz = z[1:] - z[:-1]

    dUdz = np.empty((U.shape[0],U.shape[1]-1)) # Ignore final height
    dUdz[:,:2] = U[:,:2] # Time and dt columns
    dUdz[:,2:] = (U[:,3:] - U[:,2:-1]) / dz

    dVdz = np.empty((V.shape[0],V.shape[1]-1)) # Ignore final height
    dVdz[:,:2] = V[:,:2] # Time and dt columns
    dVdz[:,2:] = (V[:,3:] - V[:,2:-1]) / dz

    Rf = np.empty(dUdz.shape)
    Rf[:,:2] = dUdz[:,:2]
    Rf[:,2:] = (  ((const.g/T[:,2:-1]) * Tw[:,2:-1])
                / (uw[:,2:-1]*dUdz[:,2:] + vw[:,2:-1]*dVdz[:,2:]))

    header = " ".join(header.split()[:-1])

    logger.info('Saving file %s',writefile.name)
    np.savetxt(writefile,Rf,header=header,fmt='%.12g')

################################################################################

def precursor_obukhov(casename, overwrite=False):
    """Calculates Obukhov length from SOWFA precursor averaging data.
    Technically, Obukhov is calculated only from surface layer, where turbulent
    fluxes are approximately constant with height. Here it is calculated as a
    function of height, so that the variation and extent of the surface layer
    can be visualised

    L = (-theta * ustar^3) / ( kappa*g*(w'theta') )
    ustar = ( (u'w')^2 + (v'w')^2 )^(1/4)
    """

    casedir = const.CASES_DIR / casename
    sowfatoolsdir = casedir / const.SOWFATOOLS_DIR
    avgdir = sowfatoolsdir / 'averaging'

    if not avgdir.is_dir():
        logger.warning('%s directory does not exist. '
                       'Skipping %s.',
                       avgdir,casename)
        return

    logfilename = 'log.precursorObukhov'
    utils.configure_function_logger(sowfatoolsdir/logfilename, level=LEVEL)

    ############################################################################

    logger.info("Calculating Obukhov length for %s", casename)

    writefile = avgdir/f'{casename}_OL.gz'
    if writefile.exists() and overwrite is False:
        logger.warning('%s already exists. Skippping %s.',
                       writefile.name, casename)
        return

    quantities = ['T_mean', 'uw_mean','vw_mean','Tw_mean']
    readfiles = [avgdir/f'{casename}_{quantity}.gz' for quantity in quantities]
    for readfile in readfiles:
        if not readfile.is_file():
            logger.warning('%s file does not exist. Skipping %s',
                        readfile.name, casename)
            return

    logger.debug('Getting heights')
    with gzip.open(readfiles[0],mode='rt') as f:
        header = f.readline()
    header = header.removeprefix('# ').removesuffix('\n')
    z = np.array([float(height.removesuffix('m'))
                  for height in header.split()[2:]]) # exclude time and dt column

    logger.debug('Reading %s', readfiles[0])
    T = np.loadtxt(readfiles[0])

    logger.debug('Reading %s', readfiles[1])
    uw = np.loadtxt(readfiles[1])

    logger.debug('Reading %s', readfiles[2])
    vw = np.loadtxt(readfiles[2])

    logger.debug('Reading %s', readfiles[3])
    Tw = np.loadtxt(readfiles[3])

    ############################################################################

    # Calculate friction velocity

    ustar = np.empty(uw.shape)
    ustar[:,:2] = uw[:,:2]
    ustar[:,2:] = ( uw[:,2:]**2 + vw[:,2:]**2 )**(1/4)

    L = np.empty(T.shape)
    L[:,:2] = T[:,:2]
    L[:,2:] = -T[:,2:] * ustar[:,2:] / (const.VONKARMAN*const.g*Tw[:,2:])

    logger.info('Saving file %s',writefile.name)
    np.savetxt(writefile,L,header=header,fmt='%.12g')

################################################################################

if __name__ == '__main__':
    utils.configure_root_logger(level=LEVEL)

    DESCRIPTION ="""Calculate turbulence intensity at every height"""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('cases', help='list of cases to perform analysis for',
                        nargs='+')
    parser.add_argument('-o', '--overwrite', help='option to overwrite exisiting files',
                        action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    logger.debug('Parsed the command line arguments: %s', args)

    for casename in args.cases:
        precursor_richardson_gradient(casename, args.overwrite)
        precursor_richardson_flux(casename, args.overwrite)
        precursor_obukhov(casename, args.overwrite)
