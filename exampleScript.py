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

def main():
    utils.configure_logging(const.SOWFATOOLS_DIR/f'log.{Path(__file__).stem}',
                            level=logging.DEBUG)
    
    # Add script details here

if __name__ == "__main__":
    main(*sys.argv[1:])
    