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
import precursorTransform
import precursorIntensity
import precursorStability

import precursorProfile
import precursorIntensityAlt

LEVEL = logging.INFO
logger = logging.getLogger(__name__)


################################################################################

def main():
    """Runs a series of postProcessing functions on SOWFA precursor data."""

    cases = [path for path in const.CASES_DIR.iterdir()
             if path.is_dir() and re.fullmatch('p[0-9]{3}', path.name)]

    logger.info('Found %s precursor cases', len(cases))

    for casedir in cases:
        casename = casedir.name

        precursorAveraging.precursorAveraging(casename)
        precursorTransform.precursorTransform(casename,overwrite=True)
        precursorIntensity.precursorIntensity(casename,overwrite=True)
        precursorStability.precursor_richardson_gradient(casename,overwrite=True)
        precursorStability.precursor_richardson_flux(casename,overwrite=True)
        precursorStability.precursor_obukhov(casename,overwrite=True)

        ########################################################################

        width = 3000
        offset = 2000 # only used for p001
        if casename in ['p002', 'p202', 'p005', 'p006', 'p007', 'p011', 'p013']:  # NBL
            starttime = 18000

        elif casename in ['p004']:  # NBL, later time window
            starttime = 80000

        elif casename in ['p003', 'p008', 'p012', 'p014']:  # CBL
            starttime = 8000

        # p001 is a long run which we use to compare the evolution of profiles over time.
        if casename == 'p001':
            precursorProfile.precursorProfile(casename,width,offset=offset,overwrite=True)
        else:
            precursorProfile.precursorProfile(casename,width,starttime, overwrite=True)

        precursorIntensityAlt.precursorIntensityAlt(casename,width,starttime, overwrite=True)

################################################################################

if __name__ == '__main__':
    utils.configure_root_logger(level=LEVEL)
    main()
