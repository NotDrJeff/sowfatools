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
        logger.info(f'Calculating Reynolds Number for case {casename}')
        
        casedir = const.CASES_DIR / casename
        outputdir = casedir / const.SOWFATOOLS_DIR
        utils.create_directory(outputdir)
        utils.configure_logging((outputdir / f'log.{Path(__file__).stem}'),
                                level=logging.DEBUG)
        
        geodir = casedir / 'postProcessing/geostrophicWind'
        
        timefolders = [timefolder for timefolder in geodir.iterdir()]
        timefolders.sort(key=lambda x: float(x.name))
                
        logger.info(f'Found {len(timefolders)} time folders')
            
        for timefolder in timefolders:
            fname = timefolder / 'faceSource.dat.gz'
            logger.debug(f'Reading {fname}')
            rawdata = np.genfromtxt(fname,dtype='str')
            for i,val in np.ndenumerate(rawdata):
                rawdata[i] = val.replace('(','').replace(')','')
                
            rawdata = rawdata.astype('float')
            
            if 'data' in locals():
                data = np.vstack((data,rawdata))
            else:
                data = np.array(rawdata)
                
            del rawdata
            
        data = utils.remove_overlaps(data,0)
        
        dt = np.empty_like(data[:,0])
        dt[0] = data[0,0] - np.floor(data[0,0])
        for i in range(1,len(dt)):
            dt[i] = data[i,0] - data[i-1,0]
        
        data = np.insert(data,1,dt,axis=1)
        
        names = ['time','dt','Ux','Uy','Uz','Umag','UAvg']
        dtype = [(name, 'float') for name in names]
        header = ' '.join(names)
        
        umag = np.linalg.norm(data[:,2:],axis=1)
        data = np.column_stack((data,umag))
        average = utils.calculate_moving_average(data,-1,1)
        finalvalue = average[-1]
        data = np.column_stack((data,average))
        
        logging.getLogger('matplotlib').setLevel(logging.WARNING)
        import matplotlib.pyplot as plt
        plt.plot(data[:,0],umag)
        plt.plot(data[:,0],average)
        
        data = np.array(rec.fromarrays(data.transpose(), dtype))
        
        fname = outputdir / (f'{casename}_geostrophicWind.png')
        logger.info(f'Saving file {fname.name}')
        plt.savefig(fname)
        
        fname = outputdir / (f'{casename}_geostrophicWind.gz')
        logger.info(f'Saving file {fname.name}')
        np.savetxt(fname,data,header=header)
        
        logger.info(f'Finished case {casename}.')
        logger.info(f'Average geostrophic wind magnitude is {finalvalue:.2f}')

if __name__ == "__main__":
    main(sys.argv[1:])
    