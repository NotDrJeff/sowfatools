#!/bin/python3
"""Written for python 3.11
This module contains functions that can be used to postprocess SOWFA precursor
and turbine simulations using paraview's python interface, pvpython or pvbatch.

Created by Jeffrey Johnston, Jun. 2023
"""

import logging
from pathlib import Path

import numpy as np
import paraview
import paraview.simple as simple

import constants as const
import utils

paraview.compatibility.major = 5
paraview.compatibility.minor = 10
paraview.simple._DisableFirstRenderCameraReset()

logger = logging.getLogger(__name__)

###############################################################################

def loadof(filepath: Path, cellarrays: list[str] = None,
           casetype: str = 'Reconstructed Case',
           meshregions: list[str] = ['internalMesh'],
           filterdata: bool = 0,
           polyhedra: bool = 0) -> simple.OpenFOAMReader:
    """Load an openfoam case in paraview using the .foam file

    Args:
        filepath (Path): The path to the .foam file
        cellarrays (list[str], optional): Names of data arrays to load.
            Defaults to CELLARRAYS.
        casetype (str, optional): Reconstructed or decomposed.
            Defaults to 'Decomposed Case'.
        filterdata (bool, optional): Create cell to point filtered data.
            Defaults to 0 (False).
        polyhedra (bool, optional): Decompose polyhedra.
            Defaults to 0 (False).

    Returns:
        paraview.simple.OpenFOAMReader: A reader object which can be used as a
            source for paraview filters.
    """

    logger.debug(f'Loading OpenFOAM case from {filepath}')

    ofcase = simple.OpenFOAMReader(FileName=str(filepath))
    
    ofcase.MeshRegions = meshregions
    if cellarrays is not None: ofcase.CellArrays = cellarrays
    ofcase.CaseType = casetype
    ofcase.Createcelltopointfiltereddata = filterdata
    ofcase.Decomposepolyhedra = polyhedra
    
    ofcase.UpdatePipeline(max(ofcase.TimestepValues))

    return ofcase


def create_slice(source, origin: tuple, normal: tuple) -> simple.Slice:
    """Create a slice filter.

    Args:
        source (paraview object): The pipeline object to which the slice is
            applied.
        origin (tuple): 3 coordinates specifying the origin.
        normal (tuple): 3 coordinates specifying the normal vector.

    Returns:
        paraview.simple.Slice: An object in the paraview pipeline.
    """  

    logger.debug(f'Creating slice. {origin=} {normal=}')

    pvslice = simple.Slice(Input=source)

    pvslice.SliceType = 'Plane'
    pvslice.SliceType.Origin = origin
    pvslice.SliceType.Normal = normal

    return pvslice


def create_transform(input, rotation: tuple) -> simple.Transform:
    logger.debug(f"Creating Transfrom. {rotation=}")
    transform = simple.Transform(Input=input)
    transform.Transform = 'Transform'
    transform.Transform.Rotate = rotation
    
    return transform


def create_cellDataToPointData(input, cellarrays: list) -> simple.CellDatatoPointData:
    logger.debug("Creating Point Data")
    pointData = simple.CellDatatoPointData(Input=input)
    pointData.CellDataArraytoprocess = cellarrays
    
    return pointData


def create_cylinder_clip(source, origin: tuple, axis: tuple,
                         radius: float) -> simple.Clip:
    """Create a clip filter using a cylinder.

    Args:
        source (paraview object): The pipeline object to which the clip is
            applied.
        origin (tuple): 3 coordinates specifying the origin.
        axis (tuple): 3 coordinates specifying the axis vector.
        radius (float): Radius of the cylinder.

    Returns:
        paraview.simple.Clip: An object in the paraview pipeline.
    """    

    logger.debug(f'Creating clip using cylinder. {origin=} {axis=} {radius=}')

    pvclip = simple.Clip(Input=source)

    pvclip.ClipType = 'Cylinder'
    pvclip.ClipType.Center = origin
    pvclip.ClipType.Axis = axis
    pvclip.ClipType.Radius = radius

    return pvclip


def integrate_variables(source, per_volume=True) -> simple.IntegrateVariables:
    """Calculate area or volume average of all variables.

    Args:
        source (paraview object): The pipeline object to be integrated.

    Returns:
        paraview.simple.IntegrateVariables: An object in the paraview pipeline.
    """

    logger.debug(f'Integrating Variables for {source.__class__.__name__}')

    integrateVariables = simple.IntegrateVariables(Input=source)
    integrateVariables.DivideCellDataByVolume = 1 if per_volume else 0

    return integrateVariables


def extractRegion(input,position,length,rotation):
        logger.debug('Extracting Cells By Region')
        extractedCells = simple.ExtractCellsByRegion(Input=input)
        extractedCells.IntersectWith = 'Box'
        extractedCells.IntersectWith.Position = position
        extractedCells.IntersectWith.Length = length
        extractedCells.IntersectWith.Rotation = rotation
        
        return extractedCells


def create_ellipse(origin, normal, radius):
        logger.debug('Create Ellipse')
        ellipse = simple.Ellipse()
        ellipse.Center = origin
        ellipse.Normal = normal
        ellipse.MajorRadiusVector = radius
        
        return ellipse


def streamTracerCustom(input,seed,vectors,maxlength,direction):
    logger.debug('Creating stream tracers')
    streamTracer = simple.StreamTracerWithCustomSource(Input=input,
                                                    SeedSource=seed)
    streamTracer.Vectors = vectors
    streamTracer.MaximumStreamlineLength = maxlength
    streamTracer.IntegrationDirection = direction
    
    return streamTracer


def create_line_sample(source, point1: tuple, point2: tuple,
                       samplingpattern: str = 'Sample Uniformly',
                       resolution=5000) -> simple.PlotOverLine:
    """Sample data over a line.

    Args:
        source (paraview object): The pipeline object from which the sample is
            taken.
        point1 (tuple): 3 coordinates specifying the first point of the line.
        point2 (tuple): 3 coordinates specifying the second point of the line.
        samplingpattern (str, optional): 'Sample Uniformly',
            'Sample at Segment Centers', or 'Sample at Cell Boundaries'.
            Defaults to 'Sample Uniformly'.
        resolution (int, optional): For 'Sample Uniformly'. How many samples to
            take. Defaults to 1000.

    Returns:
        paraview.simple.PlotOverLine: An object in the paraivew pipeline.
    """

    logger.debug(f'Taking line sample for {source.__class__.__name__}. '
                 f'{point1=} {point2=}')

    pvline = simple.PlotOverLine(Input=source)
    pvline.Point1 = point1
    pvline.Point2 = point2
    pvline.SamplingPattern = samplingpattern
    pvline.Resolution = resolution
    
    return pvline


def save_csv(source, filename: Path, field: str = 'Cell Data',
             arrays: list = None) -> None:

    logger.debug(f"Saving {source.__class__.__name__} to {filename}.csv")
    
    writearrays = 0 if arrays is None else 1

    simple.SaveData(f'{filename}.csv', proxy=source,
                    WriteTimeSteps=0,
                    ChooseArraysToWrite=writearrays,
                    CellDataArrays=arrays,
                    Precision=12,
                    FieldAssociation=field,
                    AddMetaData=1, AddTime=1)


def integrate_wake(ofcase, filename: Path, turbine_origin: np.array,
                   unit_normal: np.array, turbine_radius: np.array,
                   distances = range(-5,8)) -> None:
    
    pvslice = create_slice(ofcase, turbine_origin, unit_normal)
    pvclip = create_cylinder_clip(pvslice, turbine_origin, unit_normal,
                                            turbine_radius)

    pvintegrate = integrate_variables(pvclip)
    save_csv(pvintegrate, filename.parent / f'{filename.stem}0D')

    for i in distances:
        label = f'{i}D'
        slice_origin = (turbine_origin + i * 2* turbine_radius * unit_normal)
        logger.debug(f"Considering Flow at {label} Up/Down-stream. {slice_origin=}")
        pvslice.SliceType.Origin = slice_origin
        save_csv(pvintegrate, filename.parent / f'{filename.stem}{label}')
        
        
def create_line_sample_series(ofcase, filepaths: list, start_points: np.array,
                              end_points: np.array, resolution: int = 5000) -> None:
    
    for i, start_point in enumerate(start_points):
        end_point = end_points[i,:]
        
        if i == 0:
            pvline = create_line_sample(ofcase, start_point, end_point,
                                        resolution=resolution)
        else:
            logger.debug(f"Modifiying line. {start_point=} {end_point=}")
            pvline.Point1 = start_point
            pvline.Point2 = end_point
            
        save_csv(pvline, filepaths[i], field="Point Data")


def calculateDownstreamWakeLocation(casename,casefile,casedir):
    """For use with two aligned turbine cases. Tracks first turbines wake
    and finds intersection with second turbines rotor plane."""
    
    logger.info(f"Opening {casefile} in paraview and tracing turbine0 wake "
                f"downstream")
    cellarrays = ['UAvg']
    ofcase = loadof(casefile,cellarrays)
    
    extracted_region_origin = [(i+5) for i in const.REFINEMENT_ORIGIN]
    extracted_region_length = [(i-10) for i in const.REFINEMENT_SIZE]
    extractedCells = extractRegion(ofcase, extracted_region_origin,
                                   extracted_region_length,
                                   [0,0,(270-const.WIND_DIRECTION_DEG)])
        
    ellipse = create_ellipse(const.TURBINE_ORIGIN,const.WIND_UNIT_VECTOR,
                             [const.TURBINE_RADIUS,0,0])
    
    pointdata = create_cellDataToPointData(extractedCells,cellarrays)
        
    streamTracer = streamTracerCustom(pointdata,ellipse,['Points']+cellarrays,
                                      const.DOMAIN_MAXDISTANCE,'FORWARD')

    slice = create_slice(streamTracer,const.TURBINES_ORIGIN[1],
                         const.WIND_UNIT_VECTOR)
    
    streamline_dir = casedir / const.STREAMLINES_DIR
    utils.create_directory(streamline_dir)
    casefile = (streamline_dir
            / f'{casename}_streamLines_turbine0_forward_intersect_turbine1')
    save_csv(slice,casefile,'Point Data')


################################################################################