#!/bin/python3

import logging
LEVEL = logging.INFO
logger = logging.getLogger(__name__)

from pathlib import Path
import argparse

import numpy as np

import utils
import constants as const

CASESDIR = Path('/mnt/d/johnston_2024_thesis')
HEADER = 'Distance    Momentum    Mean_KE    TKE    Total_KE'


################################################################################

def turbineLineSampleIntegrate(casename, overwrite=False):
    #casedir = const.CASES_DIR / casename
    casedir = CASESDIR / casename
    sowfatoolsdir = casedir / const.SOWFATOOLS_DIR
    lsdir = sowfatoolsdir / 'lineSample'
    if not lsdir.is_dir():
        logger.warning(f'{lsdir.name} directory does not exist. Skipping.')
        return
    
    logfilename = 'log.turbineLineSampleIntegrate'
    utils.configure_function_logger(sowfatoolsdir/logfilename, level=LEVEL)
    
    writedir = sowfatoolsdir / 'lineSampleIntegrated'
    utils.create_directory(writedir)
    
    ############################################################################
    
    logger.info(f'Integrating momentum and energy from lineSample data for '
                f'case {casename}')
    
    # Get linenames and times
    
    filepaths = [file for file in lsdir.iterdir()]
    times = set()
    linenames = set()
    for filepath in filepaths:
        
        # Separate information in filename           
        fileparts = filepath.stem.split('_')
        times.add(fileparts[-1])

        # Account for half diamters, e.g. lineV0_5
        if fileparts[1] == '5':
            linenames.add('_'.join(fileparts[:2]))
        else:
            linenames.add(fileparts[0])
            
    logger.debug(f'Found {len(linenames)} lines and {len(times)} times')
    
    # Identify vertical and horizontal line names and extract distances
    
    vlinenames = [linename for linename in linenames if 'V' in linename]
    hlinenames = [linename for linename in linenames if 'H' in linename]
    
    vdistances = [float( '.'.join( linename.removeprefix('lineV').split('_') ) )
                    for linename in vlinenames]
    
    hdistances = [float( '.'.join( linename.removeprefix('lineH').split('_') ) )
                    for linename in hlinenames]
    
    # Convert into list first for sorting
    vlinesDict = list(zip(vlinenames,vdistances))
    hlinesDict = list(zip(hlinenames,hdistances))
    vlinesDict.sort(key= lambda x: x[1])
    hlinesDict.sort(key= lambda x: x[1])
    
    # Then recombine into full list
    linenames = ([vline for vline,_ in vlinesDict] +
                 [hline for hline,_ in hlinesDict])
    
    # Finally, convert into dictionary for linename lookup
    vlinesDict = dict(vlinesDict)
    hlinesDict = dict(hlinesDict)
    
    del vlinenames,hlinenames,vdistances,hdistances
    
    logger.debug(f'Identified {len(vlinesDict)} vertical lines and '
                 f'{len(hlinesDict)} horizontal lines')
    
    ############################################################################
    
    for time in times:
        hfile = (writedir / f'horizontalLineSamples_integrated_{time}.gz')
        vfile = (writedir / f'verticalLineSamples_integrated_{time}.gz')
        
        if not overwrite:
            if hfile.exists() and vfile.exists():
                logger.warning(f'Files exist for time {time}. skipping. ')
                continue
            
        vdata = np.empty((len(vlinesDict),5))
        hdata = np.empty((len(hlinesDict),5))
        vcurrentrow = -1
        hcurrentrow = -1
        for linename in linenames:
            logger.info(f'Processing line {linename} for time {time}')
            
            if 'V' in linename:
                
                # vertical distance is measured relative to ground
                startx = const.TURBINE_HUB_HEIGHT - const.TURBINE_RADIUS
                endx = const.TURBINE_HUB_HEIGHT + const.TURBINE_RADIUS
                
                writefile = vfile
                data = vdata
                vcurrentrow += 1
                
            elif 'H' in linename:
                
                # horizontal distance is measured relative to hub centre
                startx = -const.TURBINE_RADIUS
                endx = const.TURBINE_RADIUS
                
                writefile = hfile
                data = hdata
                hcurrentrow += 1
            
            
            # Read U and TKE from files
            
            filepath = lsdir / f'{linename}_UAvg_transformed_{time}'
            logger.debug(f'Reading {filepath.name}')
            U = np.loadtxt(filepath)
            
            filepath = lsdir / f'{linename}_kResolved_{time}'
            logger.debug(f'Reading {filepath.name}')
            TKE = np.loadtxt(filepath)
            
            # Find idx of all samples within rotor diameter
            idx = np.column_stack((U[:,0] > startx, U[:,0] < endx))
            idx = np.all(idx,axis=1)
            
            # Remove unwanted samples and calculate mean and total KE
            U = U[idx,:]
            TKE = TKE[idx,:]
            MKE = ( U[:,1]**2 + U[:,2]**2 + U[:,3]**2 ) / 2
            KE = TKE[:,1] + MKE
            
            # Create weighting based on a circle, y**2 = r**2 - x**2
            x = U[:,0]
            dx = x[1] - x[0]
                
            if 'V' in linename:
                x -= const.TURBINE_HUB_HEIGHT # Make relative to hub center
            
            weighting = np.sqrt( const.TURBINE_RADIUS**2 - x**2 )
            
            # Weighting requires modification for end points
            weighting[0] += weighting[0] * (x[0] - dx/2 - startx) / dx
            weighting[-1] -= weighting[-1] * (x[-1] + dx/2 - endx) / dx
            
            # Finally, calculate weighted average over rotor width or height
            U = np.average(U[:,1],axis=0,weights=weighting)
            TKE = np.average(TKE[:,1],axis=0,weights=weighting)
            MKE = np.average(MKE,axis=0,weights=weighting)
            KE = np.average(KE,axis=0,weights=weighting)
            
            # Insert in appropriate row of data array
            if 'V' in linename:
                data[vcurrentrow,:] = np.array((vlinesDict[linename],
                                                U,MKE,TKE,KE))
                
            elif 'H' in linename:
                data[hcurrentrow,:] = np.array((hlinesDict[linename],
                                                U,MKE,TKE,KE))
            
            # Save the file
            logger.debug(f'Saving file {writefile.name}')
            np.savetxt(writefile,data,fmt='%.11e',header=HEADER)
            
            
################################################################################

if __name__=='__main__':
    utils.configure_root_logger(level=LEVEL)
    
    description = """Integrate Quantities across Rotor Area."""
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument('cases', help='cases to perform analysis for',
                        nargs='+')
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed Command Line Arguments: {args}')
    
    for casename in args.cases:
        turbineLineSampleIntegrate(casename)
        