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
                logger.debug(f'Reading {fname}')
                turbinedata = np.genfromtxt(fname)
                if 'data' in locals():
                    data = np.vstack((data,turbinedata))
                else:
                    data = np.array(turbinedata)
                    
                del turbinedata
            
            for timefolder in timefolders:
                    try:
                        with open(timefolder/quantity) as file:
                            names = file.readline()
                            firstrow = file.readline().removesuffix('\n').split()
                        break
                    except FileNotFoundError:
                        continue
                    
            names = names.removeprefix('#').removesuffix('\n').split('    ')
            names = [name.replace(' ','_') for name in names]
                    
            if quantity in const.BLADE_QUANTITIES:
                samples = len(firstrow) - len(names) + 1
                basename = names[-1]
                names[-1] = f'{basename}_0'
                names.append(f'average_0')
                for i in range(1,samples):
                    names.append(f'{basename}_{i}')
                    names.append(f'average_{i}')
                
            elif quantity in const.TURBINE_QUANTITIES:
                names.append('average')
            
            names = names[2:]
            dtype = [(name, 'float') for name in names]
            header = ' '.join(names)
            
            for turbine in np.unique(data[:,0]):
                turbinedata = data[data[:,0] == turbine]
                if quantity in const.TURBINE_QUANTITIES:
                    turbinedata = utils.remove_overlaps(turbinedata,1)
                    average = utils.calculate_moving_average(turbinedata,3,2)
                    turbinedata = np.column_stack((turbinedata,average))
                    
                    turbinedata = turbinedata[:,2:]
                    turbinedata = np.array(rec.fromarrays(turbinedata.transpose(),
                                                        dtype))
                    
                    fname = outputdir / (f'{casename}_{quantity}_'
                                        f'turbine{int(turbine)}.gz')
                    logger.info(f'Saving file {fname.name}')    
                    np.savetxt(fname,turbinedata,header=header)
                    
                    del turbinedata,average
                    
                elif quantity in const.BLADE_QUANTITIES:
                    for blade in np.unique(data[:,1]):
                        bladedata = turbinedata[turbinedata[:,1] == blade]
                        bladedata = utils.remove_overlaps(bladedata,2)
                        
                        stackeddata = np.empty((bladedata.shape[0],4+samples*2))
                        stackeddata[:,:3] = bladedata[:,:3]
                        for i in range(samples):
                            stackeddata[:,2*i+4] = bladedata[:,i+4]
                            stackeddata[:,2*i+5] \
                                = utils.calculate_moving_average(bladedata,i+4,3)
                            
                        bladedata = bladedata[:,2:]
                        bladedata \
                            = np.array(rec.fromarrays(stackeddata.transpose(),
                                                    dtype))
                        
                        fname = outputdir / (f'{casename}_{quantity}_'
                                            f'turbine{int(turbine)}_blade{int(blade)}.gz')
                        logger.info(f'Saving file {fname.name}')
                        np.savetxt(fname,bladedata,header=header)
                
                    del bladedata,stackeddata
                

                    
                del turbinedata
                    
            del data
        
        
if __name__ == "__main__":
    main(sys.argv[1:])
    