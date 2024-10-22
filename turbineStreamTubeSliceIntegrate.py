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
    t006_transformcalculatevtu = pv.XMLUnstructuredGridReader(registrationName='t006_transform&calculate.vtu',
                                                              FileName=[str(datafile)])
    t006_transformcalculatevtu.CellArrayStatus = ['UAvg']
    t006_transformcalculatevtu.TimeArray = 'None'
    
    logger.info(f'Loading file {datafile.name}')
    pv.UpdatePipeline(time=0, proxy=t006_transformcalculatevtu)
    
    # Initial distance
    distance = distances[0]
    
    slicefile = directory/f'{casename}_streamTube_{turbine}Turbine_slice_{distance}D_mesh.vtk'
    outputfile = directory/f'{casename}_streamTube_{turbine}Turbine_slice_{distance}D_integrated.csv'
    if not overwrite and outputfile.exists():
        logger.warning(f'{outputfile.name} exists. skipping.')
        continue
    
    # Load slice mesh
    t006_streamTube_upstreamTurbine_slice_1D_meshvtk = pv.LegacyVTKReader(registrationName='t006_streamTube_upstreamTurbine_slice_-1D_mesh.vtk',
                                                                            FileNames=[str(slicefile)])
    
    logger.debug(f'Loading file {slicefile.name}')
    pv.UpdatePipeline(time=0.0, proxy=t006_streamTube_upstreamTurbine_slice_1D_meshvtk)
    
    # Rotate and translate slice mesh
    # When the mesh was saved by pygalmesh, y was saved as x, and z was saved as y.
    # The streamwise (x) location of the slice was not saved by pygalmesh
    transform1 = pv.Transform(registrationName='Transform1', Input=t006_streamTube_upstreamTurbine_slice_1D_meshvtk)
    transform1.Transform = 'RotateAroundOriginTransform'
    transform1.Transform.Rotate = [90, 0, 90]
    
    x = distance*const.TURBINE_DIAMETER
    if distance == 12:  # 12D is slightly outside refined region.
        x -= 3          # a small adjustment fixes the issue.
    transform2 = pv.Transform(registrationName='Transform2', Input=transform1)
    transform2.Transform.Translate = [x, 0, 0]
    
    # Resample the case data using slice mesh
    resampleWithDataset2 = pv.ResampleWithDataset(registrationName='ResampleWithDataset2',
                                                    SourceDataArrays=t006_transformcalculatevtu,
                                                    DestinationMesh=transform2)
    resampleWithDataset2.PassPointArrays = 1
    resampleWithDataset2.PassFieldArrays = 0
    
    logger.debug(f'Resampling data with slice mesh')
    pv.UpdatePipeline(time=0.0, proxy=resampleWithDataset2)
    
    pointDatatoCellData1 = pv.PointDatatoCellData(registrationName='PointDatatoCellData1', Input=resampleWithDataset2)
    
    # create a new 'Integrate Variables'
    integrateVariables1 = pv.IntegrateVariables(registrationName='IntegrateVariables1', Input=pointDatatoCellData1)
    integrateVariables1.DivideCellDataByVolume = 1
    
    pv.UpdatePipeline(time=0.0, proxy=integrateVariables1)
    
    # save data
    logger.debug(f'Write file')
    pv.SaveData(str(outputfile), proxy=integrateVariables1, ChooseArraysToWrite=1,
        CellDataArrays=['Area', 'UAvg'],
        FieldAssociation='Cell Data')
    
    # For subsequent distances
    for distance in distances[1:]:
        
        slicefile = directory/f'{casename}_streamTube_{turbine}Turbine_slice_{distance}D_mesh.vtk'
        
        outputfile = directory/f'{casename}_streamTube_{turbine}Turbine_slice_{distance}D_integrated.csv'
        if not overwrite and outputfile.exists():
            logger.warning(f'{outputfile.name} exists. skipping.')
            continue
        
        pv.ReplaceReaderFileName(t006_streamTube_upstreamTurbine_slice_1D_meshvtk, [str(slicefile)], 'FileNames')
        
        # destroy integrateVariables1, resampleWithDataset2
        Delete(integrateVariables1)
        Delete(pointDatatoCellData1)
        Delete(resampleWithDataset2)
        Delete(transform2)
        Delete(transform1)
        
        del integrateVariables1, pointDatatoCellData1, resampleWithDataset2, transform2, transform1
        
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