#!/usr/bin/env python3

import logging
LEVEL = logging.INFO
logger = logging.getLogger(__name__)

import sys
import argparse

import numpy as np

import utils
import constants as const

################################################################################


def turbineStreamTubeSliceIntegrated(casename):
    """Created by Jeffrey Johnston for sowfatools. October 2024.
    Read csv files containing integrated velocity data for streamtube slices and
    stitch together. One file created for each turbine.
    """
    
    directory = const.PARAVIEW_DIRECTORY/casename
    
    upstream_filepath = directory/f'{casename}_streamTube_upstreamTurbine_integratedAreaVelocity'
    downstream_filepath = directory/f'{casename}_streamTube_downstreamTurbine_integratedAreaVelocity'
    
    # add overwrite option / filecheck here
    
    # find files named e.g. t006_streamTube_upstreamTurbine_slice_6D_integrated.csv
    filepaths = [filepath for filepath in directory.iterdir()
                 if filepath.name.startswith(f'{casename}_streamTube')
                 and filepath.name.endswith('D_integrated.csv')]
    
    if not filepaths:
        logger.warning(f'No files found for case {casename}. Continuing.')
        return
    
    # extract numerical distance preceeding 'D' in filename
    # extract numerical distance preceeding 'D' in filename
    distances = []
    for filepath in filepaths:
        filepath_parts = filepath.stem.split('_')
        
        if len(filepath_parts) == 6:
            distance = int(filepath_parts[4].removesuffix('D'))
        else:
            distance = float('.'.join(filepath_parts[4:6]).removesuffix('D'))
            
        distances.append(distance)
    
    filepaths = list(zip(distances,filepaths))
    del distances
    
    filepaths.sort(key=lambda x: x[0])
    
    upstream = len([filepath for filepath in filepaths
                    if 'upstream' in filepath[1].name])
    
    downstream = len([filepath for filepath in filepaths
                      if 'downstream' in filepath[1].name])
    
    logger.debug(f'Found {len(filepaths)} files: {upstream=}, {downstream=}')
    
    upstream_data = np.empty((upstream,3))
    downstream_data = np.empty((downstream,3))
    
    upstream_i = 0
    downstream_i = 0
    for filepath in filepaths:
        
        data = np.genfromtxt(filepath[1], delimiter=',', skip_header=1)
        row_to_write = np.array([filepath[0],data[3],data[0]])
        
        if 'upstream' in filepath[1].name:
            upstream_data[upstream_i,:] = row_to_write
            upstream_i += 1
        
        if 'downstream' in filepath[1].name:
            downstream_data[downstream_i,:] = row_to_write
            downstream_i += 1
            
    np.savetxt(upstream_filepath,upstream_data,fmt='%.4e')
    np.savetxt(downstream_filepath,downstream_data,fmt='%.4e')
    
################################################################################


if __name__ == '__main__':
    utils.configure_root_logger(level=LEVEL)
    logger.debug(f'Python version: {sys.version}')
    logger.debug(f'Python executable location: {sys.executable}')
    
    description = """Read csv files containing integrated velocity data for
                     streamtube slices and stitch together."""
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument('cases', help='cases to perform analysis for',
                        nargs='+')
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed Command Line Arguments: {args}')
    
    for casename in args.cases:
        turbineStreamTubeSliceIntegrated(casename)
    