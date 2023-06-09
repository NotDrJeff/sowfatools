#!/bin/python3

import sys
import logging
from pathlib import Path

import numpy as np
import paraview
import paraview.simple as simple
import waketools

paraview.compatibility.major = 5
paraview.compatibility.minor = 11

logger = logging.getLogger(__name__)

###############################################################################

def loadof(filepath: Path, cellarrays: list[str] = None,
           casetype: str = 'Decomposed Case',
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

    logger.debug(f'Loading OpenFOAM case from {filepath}.')

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


def integrate_variables(source) -> simple.IntegrateVariables:
    """Calculate area or volume average of all variables.

    Args:
        source (paraview object): The pipeline object to be integrated.

    Returns:
        paraview.simple.IntegrateVariables: An object in the paraview pipeline.
    """

    logger.debug(f'Integrating Variables for {source.__class__.__name__}')

    integrateVariables = simple.IntegrateVariables(Input=source)
    integrateVariables.DivideCellDataByVolume = 1

    return integrateVariables


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

    logger.debug(f"Saving {source.__class__.__name__} to {filename}")
    
    if arrays is None:
        writearrays=0
    else:
        writearrays=1

    simple.SaveData(f'{filename}.csv', proxy=source,
                    WriteTimeSteps=0, WriteTimeStepsSeparately=0,
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
        logger.debug(f"Considering Flow at {label} Up/Down-stream")
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


################################################################################