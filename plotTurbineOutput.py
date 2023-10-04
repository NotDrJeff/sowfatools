#!/bin/python3

import logging
import sys
from pathlib import Path

import numpy as np
logging.getLogger('matplotlib').setLevel(logging.WARNING)
import matplotlib.pyplot as plt
            
import constants as const
import utils

logger = logging.getLogger(__name__)

def main(casenames):
    for casename in casenames:
        logger.info(f'Processing turbineOutput for case {casename}')
        
        casedir = const.CASES_DIR / casename
        utils.configure_logging((casedir / const.SOWFATOOLS_DIR
                                / f'log.{Path(__file__).stem}'),
                                level=logging.DEBUG)
        
        turbinedir = casedir / const.TURBINEOUTPUT_DIR
        outputdir = casedir / const.TURBINEPLOT_DIR
        utils.create_directory(outputdir)
        
        files = []
        for i, file in enumerate(turbinedir.iterdir()):
            if 'blade' in file.stem:
                files.append([file]
                             +file.stem.replace('turbine','')\
                                  .replace('blade','').split('_'))
            else:
                files.append([file]
                             +file.stem.replace('turbine','').split('_')+[''])
             
        files.sort(key= lambda x: (x[2],x[3],x[4]))
        files = np.array(files)
        
        quantities = np.unique(files[:,2])
        logger.info(f'Found {len(quantities)} quantities')
        
        for quantity in quantities:
            logger.info(f"Plotting {quantity}")
            
            for file in files[np.logical_and(files[:,2]==quantity,
                                             np.logical_or(files[:,4]=='',
                                                           files[:,4]=='0'))]:
                logger.debug(f'Reading {file[0].name}')
                data = np.genfromtxt(file[0])
                
                if quantity in const.TURBINE_QUANTITIES:
                    plt.plot(data[:,0],data[:,2],label=f'Turbine{file[3]}')
                    plt.plot(data[:,0],data[:,3],
                             label=f'Turbine{file[3]},Average')
                    
                    plt.title(f'{quantity}, {casename}')
                    plt.xlabel('Simulation Time')
                    plt.legend()
                    
                    fname = outputdir / f'{casename}_{quantity}.png'
                    logger.info(f'Saving file {fname.name}')   
                    plt.savefig(fname)
                    plt.close()
                    
                elif quantity in const.BLADE_QUANTITIES:
                    plt.plot(data[:,0],data[:,2],
                             label=f'Turbine{file[3]},Blade{file[4]},Root')
                    plt.plot(data[:,0],data[:,3],
                             label=f'Turbine{file[3]},Blade{file[4]},Root,'
                                   f'Average')
                    plt.plot(data[:,0],data[:,-2],
                             label=f'Turbine{file[3]},Blade{file[4]},Tip')
                    plt.plot(data[:,0],data[:,-1],
                             label=f'Turbine{file[3]},Blade{file[4]},Tip,'
                                   f'Average')
                    
                    plt.title(f'{quantity}, {casename}')
                    plt.xlabel('Simulation Time')
                    plt.legend()
                    
                    fname = outputdir / f'{casename}_{quantity}.png'
                    logger.info(f'Saving file {fname.name}')   
                    plt.savefig(fname)
                    plt.close()
                    
                    
if __name__ == "__main__":
    main(sys.argv[1:])
    