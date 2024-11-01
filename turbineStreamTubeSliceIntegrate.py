#!/usr/bin/env python3

import logging
LEVEL = logging.INFO
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

def turbineStreamTubeSlice(casename,overwrite=True):
    """Created by Jeffrey Johnston for sowfatools. October 2024.
    Remesh case data onto slice meshes and average velocity.
    
    Distances must be specified as rotor diameters from turbine.
    Distances can be negative.
    """
    
    directory = const.PARAVIEW_DIRECTORY/casename
    stdirectory = directory/'streamtube'
    if not stdirectory.is_dir():
        logger.warning(f'No directory found for case {casename}')
        return
    
    # find files named e.g. t006_streamtube_upstreamTurbine_slice_6_5D_mesh.vtk
    filepaths = [filepath for filepath in stdirectory.iterdir()
                 if filepath.name.startswith(f'{casename}_streamtube')
                 and filepath.name.endswith('D_mesh.vtk')]
    
    if not filepaths:
        logger.warning(f'No files found for case {casename}. Continuing.')
        return
    
    ############################################################################
    
    logger.info(f'Processing case {casename}')
    
    # extract numerical distance preceeding 'D' in filename
    distances = []
    for filepath in filepaths:
        filepath_parts = filepath.stem.removesuffix('D_mesh').split('_')
        
        distance = int(filepath_parts[4])
        
        if len(filepath_parts) == 6:
            if distance >= 0:
                distance += float(f'0.{filepath_parts[5]}')
            else:
                distance -= float(f'0.{filepath_parts[5]}')
            
        distances.append(distance)
    
    filepaths = list(zip(distances,filepaths))
    del distances
    
    logger.debug(f'Found {len(filepaths)} slice mesh files')
    
    ############################################################################
    
    datafile = directory/f'{casename}_transform&calculate.vtu'
    data = pv.XMLUnstructuredGridReader(registrationName='data',
                                        FileName=[str(datafile)])
    data.CellArrayStatus = ['UAvg']
    data.TimeArray = 'None'
    
    logger.debug(f'Loading file {datafile.name}')
    pv.UpdatePipeline(time=0, proxy=data)
    
    # Initial distance
    distance,slicefile = filepaths[0]
    outputfile = stdirectory/f'{slicefile.stem.removesuffix("_mesh")}_integrated.csv'
    
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
    if len(filepaths) > 1 :
        for filepath in filepaths[1:]:
            distance,slicefile = filepath
            outputfile = stdirectory/f'{slicefile.stem.removesuffix("_mesh")}_integrated.csv'
            
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
    
    description = """Remesh case data onto slice meshes and average velocity"""
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument('cases',
                        help='cases to perform analysis for',
                        nargs='+')
    
    args = parser.parse_args()
    
    logger.debug(f'Parsed Command Line Arguments: {args}')
    
    for casename in args.cases:
        turbineStreamTubeSlice(casename)
        
