#!/bin/python3

import sys 
from pathlib import Path
import logging

import constants as const
import utils
import sowfatools as st

logger = logging.getLogger(__name__)

def main(case_name):
    utils.configure_logging((const.CASES_DIR / case_name / const.SOWFATOOLS_DIR
                             / f'log.{Path(__file__).stem}'),
                            level=logging.DEBUG)
    
    average,_,data = st.calculate_average_power(case_name,(5, 1))
    
    # import matplotlib.pyplot as plt
    # plt.ioff()
    # plt.plot(data[:,1],average)
    # plt.savefig('test.png')
    

if __name__ == "__main__":
    main(*sys.argv[1:])
