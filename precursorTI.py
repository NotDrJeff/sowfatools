#!/bin/python3

""" Calculate Turbulence Intensity for precursor simulation.

TI = rms(u)/U
    = (sqrt(1/3 * (ux^2_mean + uy^2_mean + uz^2_mean))
        / sqrt(Ux^2 + Uy^2 + Uz^2))
"""

import logging
import sys
from pathlib import Path
import gzip

import numpy as np
import numpy.core.records as rec
logging.getLogger('matplotlib').setLevel(logging.WARNING)
import matplotlib.pyplot as plt

import constants as const
import utils

logger = logging.getLogger(__name__)

def main(casenames):
    for casename in casenames:
        casedir = const.CASES_DIR / casename
        utils.configure_logging((casedir / const.SOWFATOOLS_DIR
                                / f'log.{Path(__file__).stem}'),
                                level=logging.INFO)

        logger.info(f'Calculating Derived Quantities for case {casename}')
        
        avgdir = casedir / const.SOWFATOOLS_DIR / 'averaging'
        outputdir = casedir / const.SOWFATOOLS_DIR / 'derived'
        utils.create_directory(outputdir)
        
        with gzip.open(avgdir/f'{casename}_U_mean.gz',mode='rt') as file:
            heights = (file.readline().removeprefix('#').split())[2:]

        heights = np.unique([height.split('_')[-1] for height in heights]).astype('float')
        heights.sort()
        
        height_to_plot = np.argmin(np.abs(const.TURBINE_HUB_HEIGHT - heights))

        logger.info("Caculating Turbulence Intensity")

        for quantity in ['U_mean', 'V_mean', 'W_mean']:
            fname = avgdir / f'{casename}_{quantity}.gz'
            logger.debug(f'Reading {fname}')
            rawdata = np.genfromtxt(fname)

            if 'UU' in locals():
                UU[:,2::2] += rawdata[:,2::2]**2
            else:
                UU = rawdata
                UU[:,2::2] **= 2

            del rawdata

        for quantity in ['uu_mean', 'vv_mean', 'ww_mean']:
            fname = avgdir / f'{casename}_{quantity}.gz'
            logger.debug(f'Reading {fname}')
            rawdata = np.genfromtxt(fname)

            if 'uu' in locals():
                uu[:,2::2] += rawdata[:,2::2]
            else:
                uu = rawdata

            del rawdata

        TI = UU 
        TI[:,2::2] = np.sqrt(uu[:,2::2]/3) / np.sqrt(UU[:,2::2])
        del uu,UU

        for i in range(heights.shape[0]):
            TI[:,2*i+3] = utils.calculate_moving_average(TI,2*i+2,1)

        logger.info(f'Average turbulence intensity at turbine '
                    f'{heights[height_to_plot]:.2f}m after {TI[-1,0]:.2f}s '
                    f'is {TI[-1,2*height_to_plot+3]*100:.1f}%')

        plt.plot(TI[:,0],TI[:,2*height_to_plot+2])
        plt.plot(TI[:,0],TI[:,2*height_to_plot+3])
            
        fname = outputdir / (f'{casename}_TI.png')
        logger.info(f'Saving file {fname.name}')
        plt.savefig(fname)
        plt.close()
            
        names = ['time','dt']
            
        for i in heights:
            names.append(f'TI_{int(i)}')
            names.append(f'average_{int(i)}')
            
        dtype = [(name, 'float') for name in names]
        header = ' '.join(names)
            
        TI = np.array(rec.fromarrays(TI.transpose(), dtype))
            
        fname = outputdir / (f'{casename}_TI.gz')
        logger.info(f'Saving file {fname.name}')
        np.savetxt(fname,TI,header=header)

        del TI


if __name__ == "__main__":
    main(sys.argv[1:])
    