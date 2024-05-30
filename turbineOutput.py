#!/bin/python3

import logging
LEVEL = logging.DEBUG
logger = logging.getLogger(__name__)

import argparse
import gzip
from pathlib import Path

import numpy as np

import constants as const
import utils


################################################################################

def turbineOutput(casename, overwrite=False):
    """Stitches SOWFA turbineOutput files from multiple run start times together,
    removing overlaps. Takes a list of cases as command line arguments.
    
    Written for Python 3.12, SOWFA 2.4.x for sowfatools
    Jeffrey Johnston   NotDrJeff@gmail.com  May 2024
    """
    
    casedir = const.CASES_DIR / casename
    readdir = casedir / 'turbineOutput'
    if not readdir.is_dir():
        logger.warning(f'{readdir.stem} directory does not exist. '
                       f'Skipping case {casename}.')
        return
    
    sowfatoolsdir = casedir / const.SOWFATOOLS_DIR
    utils.create_directory(sowfatoolsdir)
    
    logfilename = 'log.turbineOutput'
    utils.configure_function_logger(sowfatoolsdir/logfilename, level=LEVEL)
    
    ############################################################################
    
    logger.info(f'Processing turbineOutput for case {casename}')
    
    writedir = casedir / const.TURBINEOUTPUT_DIR
    utils.create_directory(writedir)
    
    timefolders = [timefolder for timefolder in readdir.iterdir()]
    timefolders.sort(key=lambda x: float(x.name))
    
    quantities = set()
    for timefolder in timefolders:
        for file in timefolder.iterdir():
            quantities.add(Path(file.name))
            
    logger.info(f'Found {len(quantities)} quantities across '
                f'{len(timefolders)} time folders')
    
    ############################################################################
    
    #plotoutputddir = casedir / const.TURBINEPLOT_DIR
    #utils.create_directory(plotoutputddir)
    
    for quantity in quantities:
        logger.info(f'Processing {quantity.stem} for {casename}')
        
        for timefolder in timefolders:
            readfile = timefolder / quantity
            logger.debug(f'Reading {readfile}')
            rawdata = np.genfromtxt(readfile)
            if 'data' not in locals():
                data = rawdata
            else:
                data = np.vstack((data,rawdata))
                
            del rawdata
        
        for timefolder in timefolders:
            try:
                readfile = timefolder / quantity
                with gzip.open(readfile,mode='rt') as f:
                    header = f.readline()
                    firstrow = f.readline()
                break
            except FileNotFoundError:
                continue
        
        firstrow = firstrow.removesuffix('\n').split()
        names = header.removeprefix('#').removesuffix('\n').split('    ')
        names = [name.replace(' ','_') for name in names]
        
        if quantity.stem in const.BLADE_QUANTITIES:
            samples = len(firstrow) - len(names) + 1
            names = names[2:] # Remove "Turbine" and "Blade" headers
            basename = names[-1]
            names[-1] = f'{basename}_0'
            for i in range(1,samples): # Generate header for each sample point
                names.append(f'{basename}_{i}')
            
        elif quantity.stem in const.TURBINE_QUANTITIES:
            names = names[1:] # Remove "Turbine" header
        
        # dtype = [(name, 'float') for name in names]
        header = ' '.join(names)
        
        ########################################################################
        
        turbines = np.unique(data[:,0]).astype('int')
        for turbine in turbines:
            turbinedata = data[data[:,0] == turbine]
            
            if quantity.stem in const.TURBINE_QUANTITIES:
                
                turbinedata = utils.remove_overlaps(turbinedata,1)
                turbinedata = turbinedata[:,1:] # Remove "Turbine" column
                writefile = writedir / (f'{casename}_{quantity.stem}_'
                                        f'turbine{int(turbine)}.gz')
                logger.info(f'Saving file {writefile.name}')    
                np.savetxt(writefile,turbinedata,header=header)
                
            elif quantity.stem in const.BLADE_QUANTITIES:
                
                blades = np.unique(turbinedata[:,1]).astype('int')
                for blade in blades:
                    bladedata = turbinedata[turbinedata[:,1] == blade]
                    bladedata = utils.remove_overlaps(bladedata,2)
                    bladedata = bladedata[:,1:] # Remove "Blade" column
                    writefile = writedir / (f'{casename}_{quantity.stem}_'
                                            f'turbine{int(turbine)}_'
                                            f'blade{int(blade)}.gz')
                    logger.info(f'Saving file {writefile.name}')
                    np.savetxt(writefile,bladedata,header=header)
                    
                del bladedata # Deleted for memory efficiency only
                
        del turbinedata # Deleted for memory efficiency only
        del data # Data must be deleted for loop to work correctly
        
        
################################################################################
        
if __name__ == '__main__':
    utils.configure_root_logger(level=LEVEL)

    description = """Stitch turbineOutput data, removing overlaps"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('cases', help='list of cases to perform analysis for',
                        nargs='+')
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed the command line arguments: {args}')
    
    for casename in args.cases:
        turbineOutput(casename)
    