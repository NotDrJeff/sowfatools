#!/bin/python3
"""Written for python 3.12 for the sowfatools package.
Jeffrey Johnston    NotDrJeff@gmail.com   February 2024.

Plots all available timeaveraged profiles from sowfatools/averaging.

Accepts casename as input"""

import logging
import sys
from pathlib import Path

import numpy as np
logging.getLogger('matplotlib').setLevel(logging.WARNING)
import matplotlib.pyplot as plt

import constants as const
import utils

logger = logging.getLogger(__name__)
LEVEL = logging.INFO

def main(casename):    
    casedir = const.CASES_DIR / casename
    avgdir = casedir / const.SOWFATOOLS_DIR / 'averaging'
    utils.configure_logging((avgdir / f'log.{Path(__file__).stem}'),
                            level=LEVEL)
    
    logger.info(f'Searching for profiles in {avgdir}')
    
    filepaths = [path for path in avgdir.iterdir()
                 if 'timeaveraged' in path.stem]
    
    # Parse filenames to extract quantities
    filename_pieces = [(path.stem).split('_') for path in filepaths]
    filename_pieces = [['_'.join(i[1:-3]),*i[-2:]] for i in filename_pieces]
        # E.g. filename_pieces[0] = ['quantityname','starttime','endtime']
    quantities = set([i[0] for i in filename_pieces])
    
    logger.info(f'Found {len(filepaths)} files spanning {len(quantities)} quantities')
    
    for quantity in quantities:
        logger.info(f'Processing {quantity}')
        # sort start and end times in an array
        times = np.array([i[1:] for i in filename_pieces if i[0] == quantity],
                         dtype=int)
        times = times[np.lexsort((times[:,1],times[:,0]))]
        
        fig,ax = plt.subplots(layout='tight',figsize=(10,6))
        
        for startendtime in times:
            filename = \
                f'{casename}_{quantity}_timeaveraged_{startendtime[0]}_{startendtime[1]}.gz'
            filepath = avgdir/filename
            
            logger.debug(f"Generating array from {filepath.stem}")
            data = np.genfromtxt(filepath)
            
            logger.debug(f"Plotting")
            ax.plot(data[:,1],data[:,0],
                    label=f'{startendtime[0]}-{startendtime[1]}s')
            
        ax.set_title(f'{quantity} averaged over different time windows')
        ax.set_ylabel('Height (m)')
        
        ax.legend(bbox_to_anchor=(1,1))
        
        filepath = avgdir/f'{casename}_{quantity}_timeaverages.png'
        logger.debug(f"Writing output to {filepath}")
        
        plt.savefig(filepath)
        plt.close()
        
    logger.info(f'Finished {Path(__file__).stem} {casename}')
        
if __name__ == "__main__":
    main(*sys.argv[1:])
    