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
    
    for distance in distances:
        
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
        
        # Rotate slice mesh
        # When the mesh was saved by pygalmesh, y was saved as x, and z was saved as y.
        transform1 = pv.Transform(registrationName='Transform1', Input=t006_streamTube_upstreamTurbine_slice_1D_meshvtk)
        transform1.Transform = 'RotateAroundOriginTransform'
        transform1.Transform.Rotate = [90, 0, 90]

        # toggle interactive widget visibility (only when running from the GUI)
        # ShowInteractiveWidgets(proxy=transform1.Transform)
        # # create a new 'Resample With Dataset'
        # resampleWithDataset1 = pv.ResampleWithDataset(registrationName='ResampleWithDataset1', SourceDataArrays=t006_transformcalculatevtu,
        #     DestinationMesh=transform1)
        # resampleWithDataset1.PassPointArrays = 1
        # resampleWithDataset1.PassFieldArrays = 0
        # pv.SetActiveSource(transform1)
        # # toggle interactive widget visibility (only when running from the GUI)
        # #ShowInteractiveWidgets(proxy=transform1.Transform)

        # Translate slice mesh
        # The streamwise (x) location of the slice was not saved by pygalmesh
        x = distance*const.TURBINE_DIAMETER
        if distance == 12:  # 12D is slightly outside refined region.
            x -= 3          # a small adjustment fixes the issue.
        transform2 = pv.Transform(registrationName='Transform2', Input=transform1)
        transform2.Transform.Translate = [x, 0, 0]
        
        logger.debug(f'Rotating,Translating')
        #pv.UpdatePipeline(time=0.0, proxy=transform1)
        pv.UpdatePipeline(time=0.0, proxy=transform2)
        
        # pv.SetActiveSource(resampleWithDataset1)
        # # toggle interactive widget visibility (only when running from the GUI)
        # HideInteractiveWidgets(proxy=transform2.Transform)
        # # set active source
        # pv.SetActiveSource(transform2)
        # toggle interactive widget visibility (only when running from the GUI)
        # ShowInteractiveWidgets(proxy=transform2.Transform)

        # Resample the case data using slice mesh
        resampleWithDataset2 = pv.ResampleWithDataset(registrationName='ResampleWithDataset2',
                                                      SourceDataArrays=t006_transformcalculatevtu,
                                                      DestinationMesh=transform2)
        resampleWithDataset2.PassPointArrays = 1
        resampleWithDataset2.PassFieldArrays = 0
        
        logger.debug(f'Resampling data with slice mesh')
        pv.UpdatePipeline(time=0.0, proxy=resampleWithDataset2)

    #     # create a new 'Point Data to Cell Data'
    #     pointDatatoCellData1 = pv.PointDatatoCellData(registrationName='PointDatatoCellData1', Input=resampleWithDataset2)

    #     pv.UpdatePipeline(time=0.0, proxy=pointDatatoCellData1)

    #     # create a new 'Integrate Variables'
    #     integrateVariables1 = pv.IntegrateVariables(registrationName='IntegrateVariables1', Input=pointDatatoCellData1)
    #     integrateVariables1.DivideCellDataByVolume = 1

    #     pv.UpdatePipeline(time=0.0, proxy=integrateVariables1)

    #     # save data
    #     pv.SaveData(str(outputfile), proxy=integrateVariables1, ChooseArraysToWrite=1,
    #         CellDataArrays=['Area', 'UAvg'],
    #         FieldAssociation='Cell Data')

        # # set active source
        # SetActiveSource(pointDatatoCellData1)

        # # destroy integrateVariables1
        # Delete(integrateVariables1)
        # del integrateVariables1

        # # set active source
        # SetActiveSource(resampleWithDataset2)

        # # destroy pointDatatoCellData1
        # Delete(pointDatatoCellData1)
        # del pointDatatoCellData1

        # # set active source
        # SetActiveSource(transform2)

        # # toggle interactive widget visibility (only when running from the GUI)
        # ShowInteractiveWidgets(proxy=transform2.Transform)

        # # destroy resampleWithDataset2
        # Delete(resampleWithDataset2)
        # del resampleWithDataset2

        # # set active source
        # SetActiveSource(t006_streamTube_upstreamTurbine_slice_1D_meshvtk)

        # # toggle interactive widget visibility (only when running from the GUI)
        # HideInteractiveWidgets(proxy=transform2.Transform)

        # # set active source
        # SetActiveSource(transform2)

        # # toggle interactive widget visibility (only when running from the GUI)
        # ShowInteractiveWidgets(proxy=transform2.Transform)

        # # set active source
        # SetActiveSource(transform1)

        # # toggle interactive widget visibility (only when running from the GUI)
        # HideInteractiveWidgets(proxy=transform2.Transform)

        # # toggle interactive widget visibility (only when running from the GUI)
        # ShowInteractiveWidgets(proxy=transform1.Transform)

        # # destroy transform2
        # Delete(transform2)
        # del transform2

        # # set active source
        # SetActiveSource(resampleWithDataset1)

        # # toggle interactive widget visibility (only when running from the GUI)
        # HideInteractiveWidgets(proxy=transform1.Transform)

        # # set active source
        # SetActiveSource(transform1)

        # # toggle interactive widget visibility (only when running from the GUI)
        # ShowInteractiveWidgets(proxy=transform1.Transform)

        # # destroy resampleWithDataset1
        # Delete(resampleWithDataset1)
        # del resampleWithDataset1

        # # set active source
        # SetActiveSource(t006_streamTube_upstreamTurbine_slice_1D_meshvtk)

        # # toggle interactive widget visibility (only when running from the GUI)
        # HideInteractiveWidgets(proxy=transform1.Transform)

        # # destroy transform1
        # Delete(transform1)
        # del transform1

        # ReplaceReaderFileName(t006_streamTube_upstreamTurbine_slice_1D_meshvtk, ["C:\\Users\\jeffr\\OneDrive - Queen's University Belfast\\04_research\\2020-2024_thesis\\postProcessing\\t006\\t006_streamTube_upstreamTurbine_slice_1D_mesh.vtk"], 'FileNames')
            
        # # Create a slice
        
            
        # logger.debug(f'Creating slice at {distance}D ({x:.0f}m)')
        # slice = pv.Slice(registrationName='slice', Input=streamtube)
        # slice.SliceType.Origin = [x,0,0]
        
        # logger.debug('Processing pipeline')
        # pv.UpdatePipeline(time=0.0, proxy=slice)
        
        # logger.info(f'Writing file {outputfile.name}')
        # pv.SaveData(str(outputfile), proxy=slice)

        # pv.Delete(slice)
        # pv.Delete(streamtube)
        # del slice, streamtube

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