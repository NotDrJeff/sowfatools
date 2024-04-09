import logging
LEVEL = logging.INFO
logger = logging.getLogger(__name__)

import gzip
from pathlib import Path

import numpy as np

import sowfatools.constants as const
import sowfatools.utils as utils


################################################################################

def precursorAveraging(casename, overwrite=False):
    """Stitches SOWFA precursor averaging files from mutliple run start times
    together, removing overlaps. Takes a list of cases as command line
    arguments.
    """
    
    casedir = const.CASES_DIR / casename
    if not casedir.is_dir():
        logger.warning(f'{casename} directory does not exist. Skipping.')
        return
    
    sowfatoolsdir = casedir / const.SOWFATOOLS_DIR
    utils.create_directory(sowfatoolsdir)
    
    logfilename = 'log.precursorAveraging'
    utils.configure_function_logger(sowfatoolsdir/logfilename, level=LEVEL)
    
    ############################################################################
    
    logger.info(f'Processing averaging for case {casename}')
    
    readdir = casedir / 'postProcessing/averaging'
    if not readdir.is_dir():
        logger.warning(f'{readdir.stem} directory does not exist. '
                       f'Skipping case {casename}.')
        return
    
    writedir = sowfatoolsdir / 'averaging'
    utils.create_directory(writedir)
    
    timefolders = [timefolder for timefolder in readdir.iterdir()]
    timefolders.sort(key=lambda x: float(x.name))
    
    quantities = set()
    for timefolder in timefolders:
        for file in timefolder.iterdir():
            if file.stem != 'hLevelsCell':
                quantities.add(Path(file.name))
            
    logger.info(f'Found {len(quantities)} quantities across '
                f'{len(timefolders)} time folders')
    
    for timefolder in timefolders:
        try:
            heights = np.genfromtxt(timefolder/'hLevelsCell')
            break
        except FileNotFoundError:
            continue
            
    if 'heights' not in locals():
        logger.error('hLevelsCell file not found in any timefolder. Exiting.')
        raise FileNotFoundError('hLevelsCell not found')
                
    header = ['time','dt']
    header.extend([f'{int(i)}m' for i in heights])
    header = ' '.join(header)
    
    ############################################################################
    
    for quantity in quantities:
        logger.info(f'Processing {quantity.stem} for {casename}')
        
        writefile = writedir / (f'{casename}_{quantity.stem}.gz')
        if writefile.exists() and overwrite is False:
            logger.warning(f'{writefile} exists. Skipping {quantity.stem}.')
            continue
        
        for timefolder in timefolders:
            readfile = timefolder / quantity
            logger.debug(f'Reading {readfile}')
            rawdata = np.genfromtxt(readfile)
            if 'data' not in locals():
                data = np.array(rawdata)
            else:
                data = np.vstack((data,rawdata))
                
            del rawdata  # Deleted for memory efficiency only
            
        data = utils.remove_overlaps(data,0)
        
        writefile = writedir / (f'{casename}_{quantity.stem}.gz')
        logger.debug(f'Saving file {writefile.name}')
        np.savetxt(writefile,data,header=header)
        
        del data  # Must be deleted for next loop to work
        
    logger.info(f'Finished processing averaging for case {casename}')
    

################################################################################

def precursoraveragingreduce(casename, N=10,
                             heights_to_keep=[const.TURBINE_HUB_HEIGHT,250,500],
		                     quantities_to_keep=const.AVERAGING_QUANTITIES):
    """Extracts a reduced dataset from sowfatools/averaging for publishing and
    plotting purposes
    """
    
    casedir = const.CASES_DIR / casename
    utils.configure_logging((casedir / f'log.{Path(__file__).stem}'),
                            level=LEVEL)
	
    avgdir = casedir / const.SOWFATOOLS_DIR / 'averaging'
    
    for quantity in quantities_to_keep:
        filename = (avgdir / f'{casename}_{quantity}.gz')
        
        logger.debug(f"Reading heights from {filename}")
        with gzip.open(filename, mode='rt') as file:
            header = file.readline().split()[3::2]
            
        heights = np.array([(i.split('_')[-1]) for i in header],dtype=int)
        
        # create array of indices for keeping time and selected heights
        idx = np.empty(len(heights_to_keep)+1, dtype=int)
        idx[0] = 0
        for i, height in enumerate(heights_to_keep):
            idx[i+1] = np.argmin(np.abs(heights - height))
            
        # offset idx to ignore time, dt and averages columns
        idx[1:] = 2*idx[1:] + 2
        
        logger.info(f"Generating array from {filename}")
        data = np.genfromtxt(filename)
        
        logger.debug(f"Reducing dataset. {N=}")
        org_size = data.shape
        data = data[::N,idx] # keep time column and select heights
        new_size = data.shape
        
        logger.debug(f"Reduced data from {org_size} to {new_size}")
        
        filename = avgdir / f'{casename}_{quantity}_reduced.gz'
        logger.info(f"Writing output to {filename}")
        
        header = ' '.join(['time'] + [f'{i}m' for i in heights_to_keep])
        
        np.savetxt(filename, data, fmt='%.3e', header=header)
        
        
################################################################################

