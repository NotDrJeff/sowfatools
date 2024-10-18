#!/usr/bin/env python3

import logging
LEVEL = logging.INFO
logger = logging.getLogger(__name__)

import sys
import argparse

import numpy as np
import scipy as sp
import pygalmesh
logging.getLogger('pygalmesh').setLevel(logging.ERROR)

import utils
import constants as const

################################################################################


def turbineStreamTubeSliceMesh(casename):
    
    directory = const.PARAVIEW_DIRECTORY/casename
    
    # find files named e.g. t006_streamTube_slice_6D.csv
    filepaths = [filepath for filepath in directory.iterdir()
                 if filepath.name.startswith(f'{casename}_streamTube')
                 and 'slice' in filepath.name
                 and 'sorted' not in filepath.name
                 and 'mesh' not in filepath.name]
    
    if not filepaths:
        logger.warning(f'No files found for case {casename}. Continuing.')
        return
    
    # extract numerical distance preceeding 'D' in filename
    distances = [int(filepath.stem.split('_')[-1].removesuffix('D'))
                 for filepath in filepaths]
    
    filepaths = list(zip(distances,filepaths))
    del distances
    
    filepaths.sort(key=lambda x: x[0])
    
    for filepath in filepaths:
        
        csv_filepath = directory/f'{filepath[1].stem}_sorted'
        vtk_filepath = directory/f'{filepath[1].stem}_mesh.vtk'
        
        # add overwrite option / filecheck here
        
        # Get polygon vertices
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
        np.savetxt(csv_filepath,yz_points)
        
        # Everything after this point should be separated into a new function
        
        edges = np.array([[i,i+1] for i in range(yz_points.shape[0])])
        edges[-1,-1] = 0  # close the polygon
        
        mesh_2d = pygalmesh.generate_2d(yz_points, edges, max_edge_size=2)

        # mesh_3d = pygalmesh.Extrude(mesh_2d, [0.0,0.0,1.0])
        
        mesh_2d.write(vtk_filepath)
        
        # To visualise the original and new point order
        # import matplotlib.pyplot as plt
        # plt.ion()
        # plt.plot(original_points[:,0],original_points[:,1],
        #             marker='x',color='blue')
        # plt.plot(points[:,0],points[:,1],
        #          color='red')
        # import pdb; pdb.set_trace()
    
    
    
################################################################################


if __name__ == '__main__':
    utils.configure_root_logger(level=LEVEL)
    logger.debug(f'Python version: {sys.version}')
    logger.debug(f'Python executable location: {sys.executable}')
    
    description = """Read a csv of an in-plane polygon extracted from paraview,
                     reorder the points and save as a new csv file"""
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument('cases', help='cases to perform analysis for',
                        nargs='+')
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed Command Line Arguments: {args}')
    
    for casename in args.cases:
        turbineStreamTubeSliceMesh(casename)
    