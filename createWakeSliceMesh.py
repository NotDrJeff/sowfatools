#!/usr/bin/env python3

import logging
LEVEL = logging.INFO
logger = logging.getLogger(__name__)

import sys
import argparse
from pathlib import Path

import numpy as np
import scipy as sp
import pygalmesh

import paraview
paraview.compatibility.major = 5
paraview.compatibility.minor = 13

import paraview.simple as pv

import utils
import constants as const


################################################################################

def turbineWakeStreamTubeSlice(casename,distances):
    """
    python 3.12, paraview 5.13.0
    """
    
    # symlink to postProcessing directory
    CASE_DIR = Path(__file__).parent / 'postProcessing' / casename
    
    # create a new 'XML PolyData Reader'
    streamTube = pv.XMLPolyDataReader(registrationName='streamTube', FileName=[CASE_DIR/f'{casename}_streamTube_upstreamTurbine.vtp'])

    # Properties modified on t006_streamTube_upstreamTurbinevtp
    streamTube.TimeArray = 'None'
    
    for distance in distances:
        # create a new 'Slice'
        slice = pv.Slice(registrationName=f'slice_{distance}D', Input=streamTube)

        # Properties modified on slice1.SliceType
        slice.SliceType.Origin = [distance*const.TURBINE_DIAMETER, 0.0, 0.0]
        pv.UpdatePipeline(time=0.0, proxy=slice)

    # save data
    pv.SaveData("C:\\Users\\jeffr\\OneDrive - Queen's University Belfast (1)\\04_research\\2020-2024_thesis\\postProcessing\\t006\\t006_streamTube_slice_6D.csv", proxy=slice1, PointDataArrays=['UAvg'])
    
    
    
    
    # for distance in distances:
    #     filepath = CASES_DIR / casename / f'{casename}_streamTube_slice_{distance}D.csv'
    
    # # Get polygon vertices
    # original_points = np.genfromtxt(filepath,
    #                                 delimiter=',', skip_header=1)
    
    # # We assume the polygon lies in the yz plane
    # x = np.average(original_points[:,0])
    # yz_points = np.copy(original_points[:,1:])
    
    # dist_matrix = sp.spatial.distance_matrix(yz_points,yz_points)
    
    # for i in range(yz_points.shape[0]-2): # stop at second last point
        
    #     # find idx of nearest neighbor from all subsequent points
    #     nearest_neighbor = np.argmin(dist_matrix[i,i+1:]) + i + 1
        
    #     # move nearest neighbor to next point and update dist_matrix
    #     yz_points[[i+1,nearest_neighbor]] = yz_points[[nearest_neighbor,i+1]]
    #     dist_matrix[[i+1,nearest_neighbor]] = dist_matrix[[nearest_neighbor,i+1]]
    #     dist_matrix[:,[i+1,nearest_neighbor]] = dist_matrix[:,[nearest_neighbor,i+1]]
        
    # edges = np.array([[i,i+1] for i in range(yz_points.shape[0])])
    # edges[-1,-1] = 0  # close the polygon
    
    
    # mesh_2d = pygalmesh.generate_2d(yz_points, edges, max_edge_size=2)

    # # mesh_3d = pygalmesh.Extrude(mesh_2d, [0.0,0.0,1.0])
    
    # mesh_2d.write("extruded_mesh.vtk")
    
    
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
    
    description = """Take slices from a streamTube. Find area, center and
                     calculate average velocity"""
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument('-c','--case', required=True,
                        help='Case to operate on')
    parser.add_argument('-d','--distances', nargs='+',required=True, type=int
                        help='Distance in rotor diameters')
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed Command Line Arguments: {args}')
    
    turbineWakeStreamTubeSlice(args.case,args.distance)
    