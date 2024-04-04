#!/bin/python3
"""Written for Python 3.12
Jeffrey Johnston   NotDrJeff@gmail.com  March 2024"""

import logging
LEVEL = logging.INFO
logger = logging.getLogger(__name__)

import argparse

import constants as const
import utils

import precursorAveraging
import precursorTransform
import precursorIntensity

import precursorProfile
import precursorIntensityAlt


def main(cases):
    for casename in cases:
        casedir = const.CASES_DIR / casename
        if not casedir.is_dir():
            logger.error(f'{casename} directory does not exist. Skipping.')
            continue
        
        precursorAveraging.precursorAveraging(casename)
        precursorTransform.precursorTransform(casename)
        precursorIntensity.precursorIntensity(casename)
        
        width = 4000
        if casename == 'p001':
            precursorProfile.precursorProfile(casename,width,starttime=16000)
            precursorProfile.precursorProfile(casename,width,starttime=80000)
            precursorProfile.precursorProfile(casename,width,offset=3000)
            
            precursorIntensityAlt.precursorIntensityAlt(casename,width,starttime=16000)
            
        elif casename == 'p003':
            precursorProfile.precursorProfile(casename,width,starttime=8000)
            precursorProfile.precursorProfile(casename,width,offset=3000)
            
            precursorIntensityAlt.precursorIntensityAlt(casename,width,starttime=8000)
        
        


if __name__ == '__main__':
    utils.configure_root_logger(level=LEVEL)
    
    description = """Run through various postprocessing tools for the list of
                     specified cases"""
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument('cases', help='list of cases to perform analysis for',
                        nargs='*')
    
    args = parser.parse_args()
    main(args.cases)
    