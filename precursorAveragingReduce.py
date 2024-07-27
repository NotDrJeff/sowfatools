#!/bin/python3
"""Written for python 3.12 for the sowfatools package.
Jeffrey Johnston    NotDrJeff@gmail.com   February 2024.

Extracts a reduced dataset from sowfatools/averaging for publishing and
plotting purposes"""

import logging
import sys
import gzip
from pathlib import Path

import numpy as np

import constants as const
import utils

logger = logging.getLogger(__name__)
LEVEL = logging.DEBUG

def main(casename, N=10, heights_to_keep=[const.TURBINE_HUB_HEIGHT,250,500],
		 quantities_to_keep=const.AVERAGING_QUANTITIES):
	
	casedir = const.CASES_DIR / casename
	utils.configure_logging((casedir / f'log.{Path(__file__).stem}'),
                            level=LEVEL)
	
	avgdir = casedir / const.SOWFATOOLS_DIR / 'averaging'

	for quantity in quantities_to_keep:
		filename = (avgdir / f'{casename}_{quantity}.gz')

		logger.debug(f"Reading heights from {filename}")
		with gzip.open(filename, mode='rt') as file:
			header = file.readline().split()[3::2]

		heights = np.array([(i.split('_')[-1]) for i in header],dtype=int)
		
		# create array of indices for keeping time and selected heights
		idx = np.empty(len(heights_to_keep)+1, dtype=int)
		idx[0] = 0
		for i, height in enumerate(heights_to_keep):
			idx[i+1] = np.argmin(np.abs(heights - height))
		
		# offset idx to ignore time, dt and averages columns
		idx[1:] = 2*idx[1:] + 2

		logger.info(f"Generating array from {filename}")
		data = np.genfromtxt(filename)

		logger.debug(f"Reducing dataset. {N=}")
		org_size = data.shape
		data = data[::N,idx] # keep time column and select heights
		new_size = data.shape

		logger.debug(f"Reduced data from {org_size} to {new_size}")

		filename = avgdir / f'{casename}_{quantity}_reduced.gz'
		logger.info(f"Writing output to {filename}")

		header = ' '.join(['time'] + [f'{i}m' for i in heights_to_keep])

		np.savetxt(filename, data, fmt='%.4g', header=header)

if __name__=="__main__":
    main(sys.argv[1])
