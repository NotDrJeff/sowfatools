#!/bin/python3

""" Calculate Streamwise and Cross-stream components
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

        logger.info(f"Transforming fields for {casename}")
        
        avgdir = casedir / const.SOWFATOOLS_DIR / 'averaging'
        
        with gzip.open(avgdir/f'{casename}_U_mean.gz',mode='rt') as file:
            heights = (file.readline().removeprefix('#').split())[2:]

        heights = np.unique([height.split('_')[-1] for height in heights]).astype('float')
        heights.sort()

        component_groups = (('U_mean', 'V_mean'),
                            ('q1_mean', 'q2_mean'),
                            ('Tu_mean', 'Tv_mean'))

        suffixes = ('sw','cs') 

        for components in component_groups:
            for i, component in enumerate(components):
                fname = avgdir / f'{casename}_{component}.gz'
                logger.debug(f'Reading {fname}')
                rawdata = np.genfromtxt(fname)
  
                if 'data' not in locals():
                    data = np.empty((*rawdata.shape,len(components)))

                data[:,0:2,i] = rawdata[:,0:2]
                data[:,2::2,i] = rawdata[:,2::2]
                del rawdata

            for j in range(2,data.shape[1],2):
                data[:,j,i] = const.WIND_ROTATION.apply(data[:,j,i])

            for i, component in enumerate(components):
                for j in range(3,data.shape[1],2):
                    data[:,j,i] = utils.calculate_moving_average(data[:,j-1,i])

                names = ['times,dt']
                quantity = f'{component.split('_')[0]}_{suffixes[i]'
                for j in heights:
                    names.append(f'{quantity}_{int(j)}')
                    names.append(f'average_{int(j)}')
            
                dtype = [(name, 'float') for name in names]
                header = ' '.join(names)
                
                fname = avgdir / (f'{casename}_{quantity}.gz')
                fname = Path('test.gz')
                logger.info(f'Saving file {fname.name}')
                np.savetxt(fname,data[:,:,i],header=header)

            del data

        """ add symmtensor rotations later
        R11_mean    R12_mean    R13_mean
                    R22_mean    R23_mean
                                R33_mean

        uu_mean     uv_mean     uw_mean
                    vv_mean     vw_mean
                                ww_mean

        wuu_mean    wuv_mean    wuw_mean
                    wvv_mean    wvw_mean
                                www_mean
        """

    logger.info("Finished")


if __name__ == "__main__":
    main(sys.argv[1:])
    
