#!/bin/python3

import logging
import sys
from pathlib import Path

import numpy as np
import numpy.core.records as rec

import constants as const
import utils

logger = logging.getLogger(__name__)

def main(casenames):
    for casename in casenames:
        logger.info(f'Processing averaging for case {casename}')
        
        casedir = const.CASES_DIR / casename
        utils.configure_logging((casedir / const.SOWFATOOLS_DIR
                                / f'log.{Path(__file__).stem}'),
                                level=logging.INFO)
        
        avgdir = casedir / 'postProcessing/averaging'
        outputdir = casedir / const.SOWFATOOLS_DIR / 'averaging'
        utils.create_directory(outputdir)
        
        timefolders = [timefolder for timefolder in avgdir.iterdir()]
        timefolders.sort(key=lambda x: float(x.name))
        
        quantities = set()
        for timefolder in timefolders:
            for quantity in timefolder.iterdir():
                if quantity.stem != 'hLevelsCell':
                    quantities.add(Path(quantity.name))
                
        logger.info(f'Found {len(quantities)} quantities across '
                    f'{len(timefolders)} time folders')
        
        for timefolder in timefolders:
                    try:
                        heights = np.genfromtxt(timefolder/'hLevelsCell')
                        break
                    except FileNotFoundError:
                        continue
        
        height_to_plot = np.argmin(90 - heights)
        
        for quantity in quantities:
            logger.info(f'Processing {quantity.stem} for {casename}')
            
            for timefolder in timefolders:
                fname = timefolder / quantity
                logger.debug(f'Reading {fname}')
                rawdata = np.genfromtxt(fname)
                if 'data' in locals():
                    data = np.vstack((data,rawdata))
                else:
                    data = np.array(rawdata)
                    
                del rawdata
                
            data = utils.remove_overlaps(data,0)
            
            stackeddata = np.empty((data.shape[0],2+heights.shape[0]*2))
            stackeddata[:,:2] = data[:,:2]
            for i in range(heights.shape[0]):
                stackeddata[:,2*i+2] = data[:,i+2]
                stackeddata[:,2*i+3] \
                    = utils.calculate_moving_average(data,i+2,1)
            
            logging.getLogger('matplotlib').setLevel(logging.WARNING)
            import matplotlib.pyplot as plt
            plt.plot(data[:,0],stackeddata[:,2*height_to_plot+2])
            plt.plot(data[:,0],stackeddata[:,2*height_to_plot+3])
            
            fname = outputdir / (f'{casename}_{quantity.stem}.png')
            logger.info(f'Saving file {fname.name}')
            plt.savefig(fname)
            plt.close()
            
            names = ['time','dt']
            
            for i in heights:
                names.append(f'{quantity.stem}_{int(i)}')
                names.append(f'average_{int(i)}')
            
            dtype = [(name, 'float') for name in names]
            header = ' '.join(names)
            
            data \
                = np.array(rec.fromarrays(stackeddata.transpose(),
                                          dtype))
            
            fname = outputdir / (f'{casename}_{quantity.stem}.gz')
            logger.info(f'Saving file {fname.name}')
            np.savetxt(fname,data,header=header)
            
            del data, stackeddata, names, dtype, header
            
        
if __name__ == "__main__":
    main(sys.argv[1:])
    