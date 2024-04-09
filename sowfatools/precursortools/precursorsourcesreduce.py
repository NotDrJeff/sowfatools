#!/bin/python3
"""Written for python 3.12 for the sowfatools package.
Jeffrey Johnston    NotDrJeff@gmail.com   February 2024.

Extracts a reduced dataset from sowfatools/SourceHistory for publishing and
plotting purposes"""

import argparse
import logging
import sys
import gzip
from pathlib import Path

import numpy as np

import sowfatools.constants as const
import sowfatools.utils as utils

logger = logging.getLogger(__name__)
LEVEL = logging.DEBUG

def main(casename,N):
	
	casedir = const.CASES_DIR / casename
	utils.configure_logging((casedir / f'log.{Path(__file__).stem}'),
                            level=LEVEL)
	
	srcdir = casedir / const.SOWFATOOLS_DIR / 'SourceHistory'
 
	filename = (srcdir / f'{casename}_sourceMomentum.gz')

	logger.debug(f"Reading heights from {filename}")
	with gzip.open(filename, mode='rt') as file:
		header = file.readline().split()[slice(0,2,4)]
  
	header = ' '.join(header)

	logger.info(f"Generating array from {filename}")
	data = np.genfromtxt(filename)

	logger.debug(f"Reducing dataset. {N=}")
	org_size = data.shape
	data = data[::N,:]
	data = data[:,[0,2,4]] # keep time, mag and avgmag cols
	new_size = data.shape

	logger.debug(f"Reduced data from {org_size} to {new_size}")

	filename = srcdir / f'{casename}_sourceMomentum_reduced.gz'
	logger.info(f"Writing output to {filename}")
	np.savetxt(filename, data, fmt='%.3e', header=header)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="""Reduce source history to
                                                    make dataset smaller""")
    
    parser.add_argument("casename", help="specifiy which case to use")
    
    parser.add_argument("-n", "--sampling", help="How frequently to save data",
                        type=int, default=10)
    
    args = parser.parse_args()
    main(args.casename, args.sampling)
