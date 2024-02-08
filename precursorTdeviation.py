#!/bin/python3
"""Written for python 3.12 for the sowfatools package.
Jeffrey Johnston. February 2024.

Calculates percentage deviation of T_mean from intial conditions over time.
To reduce the size of the dataset, we take only keep every N samples of 
sowftools/averaging data at heights_to_keep which is saved to a file.
Directly reports maximum deviation at height of occurence every t seconds as
well as the maximum deviation at the hub height."""

import logging
import sys
import gzip
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

import constants as const
import utils

logger = logging.getLogger(__name__)
LEVEL = logging.DEBUG

def main(casename, N=100, t=10000,
		 heights_to_keep=[const.TURBINE_HUB_HEIGHT,300,500,700,900]):
	casedir = const.CASES_DIR / casename
	utils.configure_logging((casedir / f'log.{Path(__file__).stem}'),
                            level=LEVEL)

	filename = (casedir / const.SOWFATOOLS_DIR / 'averaging'
			    / f'{casename}_T_mean.gz')
	
	logger.debug(f"Generating array from {filename}")
	T = np.genfromtxt(filename)
	
	logger.debug(f"Reducing dataset.")
	times = T[:,0]
	T = T[:,2::2] #ignore average columns

	logger.debug(f"Getting heights from {filename}")
	with gzip.open(filename, mode='rt') as file:
		header = file.readline().split()[3::2]

	heights = np.array([(i.split('_')[-1]) for i in header],dtype=int)

	logger.debug(f'Calculating temperature deviation')

	dev = np.empty(T.shape)
	dev[0,:] = 0

	for i in range(1, T.shape[0]):
		dev[i,:] = (T[i,:] - T[0,:]) / T[0,:]
	
	dev[1:,:] *= 100
	del T

	logger.debug("Calculating maximum deviation at each time")

	maxdev = np.empty(times.shape) # heights of maximum deviation for each time
	maxheights = np.empty(times.shape) # maximum deviation for each time
	for i in range(times.shape[0]):
		maxidx = np.argmax(dev[i,:])
		maxdev[i] = dev[i,maxidx]
		maxheights[i] = heights[maxidx]

	time_samples = int(times[-1] // t)
	time_indices = [np.argmin(np.abs(times-i*t)) for i in range(time_samples+1)]

	logger.info(f"Maximum deviation:")
	for i in range(1,time_samples+1):
		idx = time_indices[i]
		logger.info(f"	After {i*t}s: ")
		logger.info(f"		{maxdev[idx]:.2f}% at {maxheights[idx]}m")

	logger.debug(f"Reducing dataset time samples. {N=}")

	dev = [::N,:]
	
	indices = [np.argmin(np.abs(heights - i)) for i in heights_to_keep]

	for i in range(1, T.shape[0]):
		dev[i,:] = (T[i,:] - T[0,:]) / T[0,:]
	
	dev[1:,:] *= 100
	del T

	

	# Arbitrary reduction of dataset. Here we keep data for turbine hub height,
	# as well as a few other heights
		
	

	heights_to_plot = [const.TURBINE_HUB_HEIGHT, 300, 500, 700, 900]

	indices = [np.argmin(np.abs(heights - i)) for i in heights_to_plot]

	# reduce data further by skipping over time steps
	dev = dev[::N,indices]
	times = times[::N]

	labels = [f'{const.TURBINE_HUB_HEIGHT}m (Hub Height)']
	labels.extend([f'{i}m' for i in heights_to_plot[2:]])

	
	
	plt.ion()

	for i in range(dev.shape[1]):
		plt.plot(times,dev[:,i])

	import pdb; pdb.set_trace()

	plt.legend(labels=labels)
	plt.show()

if __name__=="__main__":
    main(sys.argv[1])
