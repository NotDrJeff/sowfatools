#!/bin/python3
"""Written for Python 3.12
Jeffrey Johnston   NotDrJeff@gmail.com  March 2024"""

import logging
LEVEL = logging.INFO
logger = logging.getLogger(__name__)

import re

import constants as const
import utils

import precursorAveraging
import precursorTransform
import precursorIntensity

import precursorProfile
import precursorIntensityAlt


################################################################################

def main():
    cases = [path for path in const.CASES_DIR.iterdir()
             if path.is_dir() and re.fullmatch('p[0-9]{3}', path.name)]
    
    logger.info(f'Found {len(cases)} precursor cases')
    
    for casedir in cases:
        casename = casedir.name
        
        precursorAveraging.precursorAveraging(casename)
        precursorTransform.precursorTransform(casename)
        precursorIntensity.precursorIntensity(casename)
        
        ########################################################################
        
        width = 4000
        if casename in ['p001', 'p005', 'p013', 'p011']:  # NBL
            starttime = 16000
            
        elif casename in ['p003', 'p008', 'p014', 'p012']:  # CBL
            starttime = 8000
        
        precursorProfile.precursorProfile(casename,width,starttime)
        precursorIntensityAlt.precursorIntensityAlt(casename,width,starttime)
        
        ########################################################################
        
        if casename == 'p001':  # NBL, long runtime
            starttime = 80000
            precursorProfile.precursorProfile(casename,width,starttime)
            precursorProfile.precursorProfile(casename,width,offset=3000)
            
            precursorIntensityAlt.precursorIntensityAlt(casename,width,starttime)
        
        
################################################################################

if __name__ == '__main__':
    utils.configure_root_logger(level=LEVEL)
    main()
    