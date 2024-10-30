#!/usr/bin/env python3

import logging
LEVEL = logging.INFO
logger = logging.getLogger(__name__)

import sys
import argparse

import numpy as np
import scipy as sp
import pygalmesh

import utils
import constants as const

################################################################################


def turbineStreamTubeSliceMesh(casename):
    """Created by Jeffrey Johnston for sowfatools. October 2024.
       Read streamtube slices, order points by nearest neighbor,
       and create mesh"""
                     
    directory = const.PARAVIEW_DIRECTORY/casename/'streamtube'
    
    # find files named e.g. t006_streamTube_upstreamTurbine_slice_6_5D.csv
    filepaths = [filepath for filepath in directory.iterdir()
                 if filepath.name.startswith(f'{casename}_streamtube')
                 and filepath.name.endswith('D.csv')]
    
    if not filepaths:
        logger.warning(f'No files found for case {casename}. Continuing.')
        return
    
    logger.info(f'Processing case {casename}')
    
    # extract numerical distance preceeding 'D' in filename
    distances = []
    for filepath in filepaths:
        filepath_parts = filepath.stem.removesuffix('D').split('_')
        
        distance = int(filepath_parts[4])
        
        if len(filepath_parts) == 6:
            if distance >= 0:
                distance += float(f'0.{filepath_parts[5]}')
            else:
                distance -= float(f'0.{filepath_parts[5]}')
            
        distances.append(distance)
    
    filepaths = list(zip(distances,filepaths))
    del distances
    
    filepaths.sort(key=lambda x: x[0])
    
    for filepath in filepaths:
        
        csv_filepath = directory/f'{filepath[1].stem}_sorted'
        vtk_filepath = directory/f'{filepath[1].stem}_mesh.vtk'
        
        # add overwrite option / filecheck here
        
        # Get polygon vertices
        logger.debug(f'Reading file {filepath[1].name}')
        original_points = np.genfromtxt(filepath[1], delimiter=',', skip_header=1)
        
        # We assume the polygon lies in the yz plane
        x = np.average(original_points[:,0])
        yz_points = np.copy(original_points[:,1:])
        
        dist_matrix = sp.spatial.distance_matrix(yz_points,yz_points)
        
        for i in range(yz_points.shape[0]-2): # stop at second last point
            
            # find idx of nearest neighbor from all subsequent points
            nearest_neighbor = np.argmin(dist_matrix[i,i+1:]) + i + 1
            
            # move nearest neighbor to next point and update dist_matrix
            yz_points[[i+1,nearest_neighbor]] = yz_points[[nearest_neighbor,i+1]]
            dist_matrix[[i+1,nearest_neighbor]] = dist_matrix[[nearest_neighbor,i+1]]
            dist_matrix[:,[i+1,nearest_neighbor]] = dist_matrix[:,[nearest_neighbor,i+1]]
        
        # Write new polygon
        logger.info(f'Writing file {csv_filepath.name}')
        np.savetxt(csv_filepath,yz_points)
        
        # Everything after this point should be separated into a new function
        
        edges = np.array([[i,i+1] for i in range(yz_points.shape[0])])
        edges[-1,-1] = 0  # close the polygon
        
        # generate_2d produces an error with 3D points,
        # abut vtk write produces a warning when only 2D points are supplied.
        # mesh must be tranformed using paraview
        mesh = pygalmesh.generate_2d(yz_points, edges, max_edge_size=2)
        logger.info(f'Writing file {vtk_filepath.name}')
        mesh.write(vtk_filepath)
        
################################################################################


if __name__ == '__main__':
    utils.configure_root_logger(level=LEVEL)
    logger.debug(f'Python version: {sys.version}')
    logger.debug(f'Python executable location: {sys.executable}')
    
    description = """Read streamtube slices, order points by nearest neighbor,
                     and create mesh"""
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument('cases', help='cases to perform analysis for',
                        nargs='+')
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed Command Line Arguments: {args}')
    
    for casename in args.cases:
        turbineStreamTubeSliceMesh(casename)
    