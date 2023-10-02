#!/bin/python3

import logging
import sys
from pathlib import Path

import constants as const
import utils
import sowfatools as sowfa
import plottools as plot
import pvtools as pv
import waketools as wake

logger = logging.getLogger(__name__)

def main(casenames):
    for casename in casenames:
        casedir = const.CASES_DIR / casename
        utils.configure_logging((casedir / const.SOWFATOOLS_DIR
                                / f'log.{Path(__file__).stem}'),
                                level=logging.DEBUG)
        
        # Add script details here
        
        # logging.getLogger('matplotlib').setLevel(logging.WARNING)
        # import matplotlib.pyplot as plt
        # plt.plot(subdata[:,1],subdata[:,-1])
        # plt.plot(subdata[:,1],average)
        # plt.savefig('test1.png')

if __name__ == "__main__":
    main(*sys.argv[1:])
    