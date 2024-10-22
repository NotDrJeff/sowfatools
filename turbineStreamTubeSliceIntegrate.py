#!/usr/bin/env python3

import logging
LEVEL = logging.DEBUG
logger = logging.getLogger(__name__)

import sys
import argparse

import paraview
paraview.compatibility.major = 5
paraview.compatibility.minor = 13
import paraview.simple as pv
pv._DisableFirstRenderCameraReset()  # disable automatic camera reset on 'Show'

import utils
import constants as const

################################################################################

def turbineStreamTubeSlice(casename,distances,turbine,overwrite=True):
    """Created by Jeffrey Johnston for sowfatools. October 2024.
    Use paraview to slice a streamtube at specified distances
    and export resulting points as .csv files.
    Distances must be specified as integer rotor diameters from turbine.
    Distances can be negative.
    """
    
    directory = const.PARAVIEW_DIRECTORY/casename
    if not directory.is_dir():
        logger.warning(f'No directory found for case {casename}')
        return
    
    logger.info(f'Processing case {casename}')
    
    # Load case data
    datafile = directory/f'{casename}_transform&calculate.vtu'
    data = pv.XMLUnstructuredGridReader(registrationName='data',
                                        FileName=[str(datafile)])
    data.CellArrayStatus = ['UAvg']
    data.TimeArray = 'None'
    
    logger.debug(f'Loading file {datafile.name}')
    pv.UpdatePipeline(time=0, proxy=data)
    
    # Initial distance
    distance = distances[0]
    slicefile = directory/f'{casename}_streamTube_{turbine}Turbine_slice_{distance}D_mesh.vtk'
    outputfile = directory/f'{casename}_streamTube_{turbine}Turbine_slice_{distance}D_integrated.csv'
    
    # add overwrite prevention
    
    # Load slice mesh
    slicemesh = pv.LegacyVTKReader(registrationName='slicemesh',
                                   FileNames=[str(slicefile)])
    
    # Rotate and translate slice mesh
    # When the mesh was saved by pygalmesh, y was saved as x, and z as y.
    # The streamwise (x) location of the slice was not saved by pygalmesh
    rotation = pv.Transform(registrationName='rotation', Input=slicemesh)
    rotation.Transform = 'RotateAroundOriginTransform'
    rotation.Transform.Rotate = [90, 0, 90]
    
    x = distance*const.TURBINE_DIAMETER
    if distance == 12:  # 12D is slightly outside refined region.
        x -= 3          # a small adjustment fixes the issue.
    
    translation = pv.Transform(registrationName='translation', Input=rotation)
    translation.Transform.Translate = [x, 0, 0]
    
    # Resample the case data using slice mesh
    remeshed_data = pv.ResampleWithDataset(registrationName='remeshed_data',
                                           SourceDataArrays=data,
                                           DestinationMesh=translation)
    remeshed_data.PassPointArrays = 1
    remeshed_data.PassFieldArrays = 0
    
    logger.debug(f'Resampling data with slice mesh')
    pv.UpdatePipeline(time=0.0, proxy=remeshed_data)
    
    celldata = pv.PointDatatoCellData(registrationName='celldata',
                                      Input=remeshed_data)
    
    # Integrate velocities
    integrated = pv.IntegrateVariables(registrationName='integrated',
                                       Input=celldata)
    integrated.DivideCellDataByVolume = 1
    
    pv.UpdatePipeline(time=0.0, proxy=integrated)
    
    logger.info(f'Writing file {outputfile}')
    pv.SaveData(str(outputfile), proxy=integrated, ChooseArraysToWrite=1,
                CellDataArrays=['Area', 'UAvg'],
                FieldAssociation='Cell Data')
    
    # For subsequent distances
    if len(distances) > 1 :
        for distance in distances[1:]:
            
            slicefile = directory/f'{casename}_streamTube_{turbine}Turbine_slice_{distance}D_mesh.vtk'
            outputfile = directory/f'{casename}_streamTube_{turbine}Turbine_slice_{distance}D_integrated.csv'
            if not overwrite and outputfile.exists():
                logger.warning(f'{outputfile.name} exists. skipping.')
                continue
            
            x = distance*const.TURBINE_DIAMETER
            if distance == 12:  # 12D is slightly outside refined region.
                x -= 3          # a small adjustment fixes the issue.
            translation.Transform.Translate = [x, 0, 0]
            
            pv.ReplaceReaderFileName(slicemesh, [str(slicefile)], 'FileNames')
            pv.UpdatePipeline(time=0.0, proxy=integrated)
            
            logger.info(f'Writing file {outputfile}')
            pv.SaveData(str(outputfile), proxy=integrated,
                        ChooseArraysToWrite=1,
                        CellDataArrays=['Area', 'UAvg'],
                        FieldAssociation='Cell Data')
            
    pv.Delete(integrated)
    pv.Delete(celldata)
    pv.Delete(remeshed_data)
    pv.Delete(translation)
    pv.Delete(rotation)
    pv.Delete(slicemesh)
    pv.Delete(data)
    
    del integrated, celldata, remeshed_data, translation, rotation, slicemesh, data
        
################################################################################


if __name__ == '__main__':
    utils.configure_root_logger(level=LEVEL)
    logger.debug(f'Python version: {sys.version}')
    logger.debug(f'Python executable location: {sys.executable}')
    
    description = """Use paraview to slice a streamtube at specified distances
                     and export resulting points as .csv files"""
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument('-c', '--cases', help='cases to perform analysis for',
                        nargs='+', required=True)
    parser.add_argument('-d', '--distances', help='distances (in diameters) to slice',
                        nargs='+',type=int,required=True)
    parser.add_argument('-t', '--turbine', help='which turbine? upstream or downstream',
                        choices=['upstream','downstream'], required=True)
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed Command Line Arguments: {args}')
    
    for casename in args.cases:
        turbineStreamTubeSlice(casename,args.distances,args.turbine)
        