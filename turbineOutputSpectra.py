#!/bin/python3

import logging
LEVEL = logging.DEBUG
logger = logging.getLogger(__name__)

import argparse
import gzip

import numpy as np

import constants as const
import utils


################################################################################

def turbineOutputAverage(casename,blade_sample_to_report=27,overwrite=False):
    """Reads powerRotor from sowfatools directory and calculates amplitude
    spectra
    
    Written for Python 3.12, SOWFA 2.4.x for sowfatools
    Jeffrey Johnston    NotDrJeff@gmail.com    June 2024
    """
    
    casedir = const.CASES_DIR / casename
    readdir = casedir / const.TURBINEOUTPUT_DIR
    if not readdir.is_dir():
        logger.warning(f'{readdir.stem} directory does not exist. '
                       f'Skipping case {casename}.')
        return
    
    sowfatoolsdir = casedir / const.SOWFATOOLS_DIR
    logfilename = 'log.turbineOutputSpectra'
    utils.configure_function_logger(sowfatoolsdir/logfilename, level=LEVEL)
    
    ############################################################################
    
    logger.info(f'Calculating Amplitude Spectra from turbineOutput for case '
                f'{casename}')
    logger.info('')
    
    writedir = casedir / const.SOWFATOOLS_DIR / 'turbineOutputSpectra'
    utils.create_directory(writedir)
    
    quantities,turbines,blades = utils.parse_turbineOutput_files(readdir)
    
    for quantity in quantities:
        for turbine in turbines:
            
            if quantity in const.TURBINE_QUANTITIES:
                
                logger.info(f'{casename}, {quantity}, turbine{turbine}')
                
                writefile = writedir / (f'{casename}_{quantity}_'
                                        f'turbine{turbine}_spectra.gz')
                if (writefile.exists() and overwrite is False
                    and blade_sample_to_report is not None):
                    logger.warning(f'{writefile.name} already exists. '
                                   f'Skippping.')
                    logger.warning('')
                    continue
                
                readfile = (readdir
                            / f'{casename}_{quantity}_turbine{turbine}.gz')
                logger.debug(f'Reading {readfile}')
                data = np.genfromtxt(readfile)
                        
                header = f'freq {quantity}'
                
                freq = np.fft.rfftfreq(data.shape[0])
                fft = np.abs(np.fft.rfft(data[:,2],norm='forward',axis=0))
                fft[1:] *= 2
                
                if data.shape[0] % 2 == 0:
                    fft[0] *=2
                    
                data = np.column_stack((freq,fft))
                
                if (not writefile.exists() or overwrite is True):
                    np.savetxt(writefile,data,fmt='%.12g',header=header)
                
                mean = data[0,1]
                
            elif quantity in const.BLADE_QUANTITIES:
                for blade in blades:
                    
                    logger.info(f'{casename}, {quantity}, turbine{turbine}, '
                                f'blade{blade}')
                    
                    writefile = writedir / (f'{casename}_{quantity}_'
                                            f'turbine{turbine}_blade{blade}_'
                                            f'spectra.gz')
                    if (writefile.exists() and overwrite is False
                        and blade_sample_to_report is not None):
                        logger.warning(f'{writefile.name} already exists. '
                                    f'Skippping.')
                        logger.warning('')
                        continue
                    
                    readfile = readdir / (f'{casename}_{quantity}_'
                                          f'turbine{turbine}_blade{blade}.gz')
                    logger.debug(f'Reading {readfile}')
                    data = np.genfromtxt(readfile)
                        
                    header = f'freq ' + ' '.join([f'{quantity}_{i}'
                                                  for i in range(data.shape[1]-2)])
                    
                    fft = np.empty((data.shape[0],data.shape[1]-1)) # exclude dt col
                    fft[:,0] = np.fft.rfftfreq(data.shape[0])
                    
                    fft[:,1] = np.abs(np.fft.rfft(data[:,2],norm='forward'))
                    
                    # Account for frequency folding
                    if data.shape[0] % 2 == 0:
                        fft[:,1] *=2
                    else:
                        fft[1:,1] *= 2
                    
                    if (not writefile.exists() or overwrite is True):
                        np.savetxt(writefile,data,fmt='%.12g',header=header)
                    
                    mean = data[0,blade_sample_to_report]
                        
            
                logger.info(f'Mean amplitude from spectra is is {mean:.5e}')
                logger.info('')
                
    logger.info(f'Finished case {casename}')
    logger.info('')

################################################################################

if __name__ == '__main__':
    utils.configure_root_logger(level=LEVEL)

    description = "Calculate Running Average for turbineOutput"""
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument('cases', help='list of cases to perform analysis for',
                        nargs='+')
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed the command line arguments: {args}')
    
    for casename in args.cases:
        turbineOutputAverage(casename)