#!/bin/python3

import logging
import sys
from pathlib import Path

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
        utils.configure_logging((casedir / f'log.{Path(__file__).stem}'),
                                level=logging.INFO)
        
        logger.info(f'Processing turbineOutput for case {casename}')
        
        turbinedir = casedir / 'turbineOutput'
        dataoutputdir = casedir / const.TURBINEOUTPUT_DIR
        plotoutputddir = casedir / const.TURBINEPLOT_DIR
        utils.create_directory(dataoutputdir)
        utils.create_directory(plotoutputddir)
        
        timefolders = [timefolder for timefolder in turbinedir.iterdir()]
        timefolders.sort(key=lambda x: float(x.name))
        
        quantities = set()
        for timefolder in timefolders:
            for quantity in timefolder.iterdir():
                quantities.add(Path(quantity.name))
                
        logger.info(f'Found {len(quantities)} quantities across '
                    f'{len(timefolders)} time folders')
        
        for quantity in quantities:
            logger.info(f'Processing {quantity} for {casename}')
            
            for timefolder in timefolders:
                fname = timefolder / quantity
                logger.debug(f'Reading {fname}')
                rawdata = np.genfromtxt(fname)
                if 'data' in locals():
                    data = np.vstack((data,rawdata))
                else:
                    data = np.array(rawdata)
                    
                del rawdata
            
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
            
            if quantity.stem in const.BLADE_QUANTITIES:
                samples = len(firstrow) - len(names) + 1
                names = names[2:]
                basename = names[-1]
                names[-1] = f'{basename}_0'
                names.append(f'average_0')
                for i in range(1,samples):
                    names.append(f'{basename}_{i}')
                    names.append(f'average_{i}')
                
            elif quantity.stem in const.TURBINE_QUANTITIES:
                names = names[1:]
                names.append('average')
            
            dtype = [(name, 'float') for name in names]
            header = ' '.join(names)
            
            turbines = np.unique(data[:,0]).astype('int')
            for turbine in turbines:
                turbinedata = data[data[:,0] == turbine]
                if quantity.stem in const.TURBINE_QUANTITIES:
                    turbinedata = utils.remove_overlaps(turbinedata,1)
                    average = utils.calculate_moving_average(turbinedata,3,2)
                    turbinedata = np.column_stack((turbinedata,average))
                    
                    turbinedata = turbinedata[:,1:]
                    
                    logger.info(f'Average for {quantity.stem}, '
                                f'turbine{turbine} at '
                                f'{turbinedata[-1,0]:.3f}s is '
                                f'{turbinedata[-1,-1]:.2e}')
                    
                    label = f'turbine{turbine}'
                    plt.plot(turbinedata[:,0],turbinedata[:,2],alpha=0.3,
                             label=label)
                    plt.plot(turbinedata[:,0],turbinedata[:,3],
                             label=f'{label} (average)')
                    
                    turbinedata = np.array(rec.fromarrays(turbinedata.transpose(),
                                                          dtype))
                    
                    fname = dataoutputdir / (f'{casename}_{quantity.stem}_'
                                        f'turbine{int(turbine)}.gz')
                    logger.info(f'Saving file {fname.name}')    
                    np.savetxt(fname,turbinedata,header=header)
                    
                    del turbinedata
                    
                elif quantity.stem in const.BLADE_QUANTITIES:
                    blades = np.unique(turbinedata[:,1]).astype('int')
                    for blade in blades:
                        bladedata = turbinedata[turbinedata[:,1] == blade]
                        bladedata = utils.remove_overlaps(bladedata,2)
                        
                        stackeddata = np.empty((bladedata.shape[0],4+samples*2))
                        stackeddata[:,:3] = bladedata[:,:3]
                        for i in range(samples):
                            stackeddata[:,2*i+4] = bladedata[:,i+4]
                            stackeddata[:,2*i+5] \
                                = utils.calculate_moving_average(bladedata,i+4,3)
                            
                        bladedata = stackeddata[:,2:]
                        
                        logger.info(f'Average for {quantity.stem}, '
                                    f'turbine{turbine}, blade{blade} at '
                                    f'{bladedata[-1,0]:.3f}s is '
                                    f'{bladedata[-1,-1]:.2e}')

                        bladedata \
                            = np.array(rec.fromarrays(bladedata.transpose(),
                                                      dtype))
                        
                        fname = dataoutputdir / (f'{casename}_{quantity.stem}_'
                                            f'turbine{int(turbine)}_blade{int(blade)}.gz')
                        logger.info(f'Saving file {fname.name}')
                        np.savetxt(fname,bladedata,header=header)
                        
                        del bladedata
                        
                    del turbinedata
                    
                    label = f'turbine{turbine},blade{blade},tip'
                    plt.plot(stackeddata[:,2],stackeddata[:,-2],alpha=0.3,
                             label=label)
                    plt.plot(stackeddata[:,2],stackeddata[:,-1],
                             label=f'{label} (average)')
                    
                    del stackeddata

            del data
            
            fname = plotoutputddir / (f'{casename}_{quantity.stem}.png')
            logger.info(f'Saving file {fname.name}')
            plt.legend()
            plt.savefig(fname)
            plt.close()
            
        
if __name__ == "__main__":
    main(sys.argv[1:])
    