#!/bin/pvpython

import sys
import logging
from pathlib import Path
import numpy as np
import paraview.simple as simple

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('log.t006', mode='w')
stream_handler = logging.StreamHandler(stream=sys.stdout)
logging.basicConfig(handlers=(file_handler, stream_handler),
                    level=logging.DEBUG)
logger.info("Logging configured")

CASE_NAME = 't006copy'
CASE_DIR = Path('/mnt/scratch2/users/40146600') / CASE_NAME
WAKESAMPLING_DIR =  CASE_DIR / 'sowfatools' / 'wakeSampling'
CASE_FILE = CASE_DIR / f'{CASE_NAME}.foam'
CELLARRAYS = ['UAvg']

logger.info("Opening Case")
ofcase = simple.OpenFOAMReader(FileName=str(CASE_FILE))
ofcase.MeshRegions = ['internalMesh']
ofcase.CellArrays = CELLARRAYS
ofcase.CaseType = 'Reconstructed Case'
ofcase.Createcelltopointfiltereddata = 0
ofcase.Decomposepolyhedra = 0
ofcase.UpdatePipeline(max(ofcase.TimestepValues))

logger.info("Transform")
transform = simple.Transform(Input=ofcase)
transform.Transform = 'Transform'
transform.Transform.Rotate = (0,0,330)

logger.info("PointData")
pointData = simple.CellDatatoPointData(Input=transform)
pointData.CellDataArraytoprocess = CELLARRAYS

def calculateSliceOrigin(i):
    return ( np.array([1608.216, 549.513, 90])
            + i * np.array([126, 0, 0]) )

slice_origin = calculateSliceOrigin(0)
logger.info(f"{slice_origin}")

logger.info("Slice")
pvslice = simple.Slice(Input=pointData)
pvslice.SliceType = 'Plane'
pvslice.SliceType.Origin = slice_origin
pvslice.SliceType.Normal = (1,0,0)

logger.info("Clip")
pvclip = simple.Clip(Input=pvslice)
pvclip.ClipType = 'Cylinder'
pvclip.ClipType.Center = slice_origin
pvclip.ClipType.Axis = (1,0,0)
pvclip.ClipType.Radius = 63

logger.info("Integrate")
integrateVariables = simple.IntegrateVariables(Input=pvclip)
integrateVariables.DivideCellDataByVolume = 0

logger.info("Save CSV")
filename = WAKESAMPLING_DIR / f'{CASE_NAME}_wakeMassFlow.csv'
simple.SaveData(str(filename), proxy=integrateVariables,
                WriteTimeSteps=0,
                ChooseArraysToWrite=0,
                Precision=12,
                FieldAssociation='Point Data',
                AddMetaData=1, AddTime=1)

slice_origin = calculateSliceOrigin(2)
logger.info(f"{slice_origin=}")
pvslice.SliceType.Origin = slice_origin

logger.info(f"Save CSV")
filename = WAKESAMPLING_DIR / f'{CASE_NAME}_wakeMassFlow_1D.csv'
simple.SaveData(str(filename), proxy=integrateVariables,
                WriteTimeSteps=0,
                ChooseArraysToWrite=0,
                Precision=12,
                FieldAssociation='Point Data',
                AddMetaData=1, AddTime=1)

sys.exit()