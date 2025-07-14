#!/usr/bin/env python3

"""Compatible with Python 3.13, SOWFA 2.4.x
Part of github.com/NotDrJeff/sowfatools
Jeffrey Johnston   jeffrey.johnston@qub.ac.uk  July 2025

Runs a series of postProcessing functions on SOWFA precursor data.
"""

import logging
import re

import constants as const
import utils

import precursorAveraging
import precursorAveragingReduce
import precursorTransform
import precursorIntensity
import precursorStability
import precursorTdeviation
import precursorSources
import precursorSourcesReduce

import precursorProfile
import precursorIntensityAlt
import precursorPower
import precursorVelocityChange
import precursorConvectiveVelocity

LEVEL = logging.INFO
logger = logging.getLogger(__name__)

################################################################################

def precursorAllRun():
    """Runs a series of postProcessing functions on SOWFA precursor data."""

    cases = [path for path in const.CASES_DIR.iterdir()
             if path.is_dir() and re.fullmatch('p[0-9]{3}', path.name)]

    logger.info('Found %s precursor cases', len(cases))

    for casedir in cases:
        casename = casedir.name

        precursorAveraging.precursorAveraging(casename)
        #precursorAveragingReduce.main(casename)  # This script requires updating.
        precursorTransform.precursorTransform(casename)

        precursorIntensity.precursorIntensity(casename)
        precursorStability.precursor_richardson_gradient(casename)
        precursorStability.precursor_richardson_flux(casename)
        precursorStability.precursor_obukhov(casename)

        #precursorTdeviation.main(casename) # This script requires updating.
        #precursorSources.precursorSources(casename,times_to_report) # This script requires updating.
        #precursorSourcesReduce.main(casename,N) # This script requires updating.

        ########################################################################

        if casename in ['p007','p006']: # Alt SGS model cases
            width = 2000
        else:
            width = 3000

        if casename in ['p002', 'p202', 'p005', 'p006', 'p007', 'p011', 'p013']:  # NBL
           starttime = 18000

        elif casename in ['p004']:  # NBL, later time window
            starttime = 80000

        elif casename in ['p003', 'p008', 'p012', 'p014']:  # CBL
            starttime = 10000

        elif casename in ['p001']: # Long runtime case
            starttime = None
            offset = 2000

        else:
            raise ValueError('Unknown case %s',casename)

        # p001 is a long run which we use to compare the evolution of profiles over time.
        if casename == 'p001':
            precursorProfile.precursorProfile(casename,width,offset=offset)
        else:
            precursorProfile.precursorProfile(casename,width,starttime)
            precursorIntensityAlt.precursorIntensityAlt(casename,width,starttime)
            precursorPower.precursorPower(casename,width,starttime)
            # precursorVelocityChange.precursorVelocityChange(casename, width, starttime) # Requres update
            # precursorConvectiveVelocity.main() # Requires major refactoring

################################################################################

if __name__ == '__main__':
    utils.configure_root_logger(level=LEVEL)
    precursorAllRun()
