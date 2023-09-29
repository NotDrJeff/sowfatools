#!/bin/python3

import logging
import sys
from pathlib import Path

import numpy as np

import constants as const
import utils

logger = logging.getLogger(__name__)

def main(casename):
    casedir = const.CASES_DIR / casename
    utils.configure_logging((casedir / const.SOWFATOOLS_DIR
                             / f'log.{Path(__file__).stem}'),
                            level=logging.DEBUG)
    
    turbinedir = casedir / 'turbineOutput'
    outputdir = casedir / const.TURBINEOUTPUT_DIR
    utils.create_directory(outputdir)
    
    timefolders = [timefolder for timefolder in turbinedir.iterdir()]
    timefolders.sort(key=lambda x: float(x.name))
    
    quantities = set()
    for timefolder in timefolders:
        for quantity in timefolder.iterdir():
            quantities.add(quantity.name)
            
    logger.info(f'{len(quantities)} quantities in {casename}/turbineOutput')
    
    for quantity in quantities:
        logger.info(f'Stitching files for {quantity}')
        
        for timefolder in timefolders:
            fname = timefolder / quantity
            subdata = np.genfromtxt(fname)
            if 'data' in locals():
                data = np.vstack((data,subdata))
            else:
                data = np.array(subdata)
                
            del subdata
            
        for timefolder in timefolders:
                try:
                    with open(timefolder/quantity) as file:
                        names = file.readline().removeprefix('#')
                        firstrow = file.readline().removesuffix('\n').split()
                    names = names.removesuffix('\n').split('    ')
                    break
                except FileNotFoundError:
                    continue
                
        if quantity in const.BLADE_QUANTITIES:
            samples = len(firstrow) - len(names) + 1
            basename = names[-1]
            names[-1] = f'{basename}_0'
            names.append(f'average_{i}')
            for i in range(1,samples):
                names.append(f'{basename}_{i}')
                names.append(f'average_{i}')
            
        elif quantity in const.TURBINE_QUANTITIES:
            names.append('average')
        
        for turbine in np.unique(data[:,0]):
            if quantity in const.TURBINE_QUANTITIES:
                subdata = data[data[:,0] == turbine]
                subdata = utils.remove_overlaps(subdata,1)
                average = utils.calculate_moving_average(subdata,3,2)
                subdata = np.column_stack((subdata,average))
                
                # convert to structured array
                
                fname = outputdir / f'{casename}_{quantity}_turbine{turbine}.gz'
                logger.info(f'Saving file {fname.name}')    
                np.savetxt(fname,subdata)
                
                del subdata
                
            elif quantity in const.BLADE_QUANTITIES:
                for blade in np.unique(data[:,1]):
                    subdata = data[(data[:,0] == turbine
                                    and data[:,1] == blade)]
                    subdata = utils.remove_overlaps(subdata,1)
                    
                # Calculate running average
                # save to file
            
                # logging.getLogger('matplotlib').setLevel(logging.WARNING)
                # import matplotlib.pyplot as plt
                # plt.plot(subdata[:,1],subdata[:,-1])
                # plt.plot(subdata[:,1],average)
                # plt.savefig('test1.png')
                
                del subdata
                
        del data
        
        
if __name__ == "__main__":
    main(*sys.argv[1:])
    