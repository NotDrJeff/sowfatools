#!/bin/python3
"Generate slices at different locations downstream for a variety of turbine cases"

import logging
from pathlib import Path
import sys

import paraview.simple as simple

import constants
import utils
import pvtools

logger = logging.getLogger(__name__)

def main(case_name):
    CASE_DIR = constants.CASES_DIR / case_name
    SOWFATOOLS_DIR = CASE_DIR / 'sowfatools'
    SLICES_DIR = SOWFATOOLS_DIR / 'slices'
    CASE_FILE = CASE_DIR / f'{case_name}.foam'
    CELLARRAYS = ['Q', 'Rmean', 'TAvg', 'TRMS', 'TTPrime2', 'UAvg',
                  'kResolved', 'kSGSmean', 'p_rghAvg', 'qmean', 'uRMS',
                  'uTPrime2', 'uuPrime2']

    utils.configure_logging('log.generateSliceImages', level=logging.DEBUG)    
    
    utils.create_directory(SLICES_DIR)

    case = pvtools.loadof(CASE_FILE,CELLARRAYS)
    
    logger.info("Creating Transfrom")
    transform1 = simple.Transform(Input=case)
    transform1.Transform = 'Transform'
    transform1.Transform.Rotate = [0.0, 0.0, -30.0]
    
    logger.info("Creating Point Data")
    pointData1 = simple.CellDatatoPointData(Input=transform1)
    pointData1.CellDataArraytoprocess = CELLARRAYS
    
    logger.info("Creating Slice")
    slice1 = pvtools.create_slice(pointData1,(1608.2+126,549.5,90),(1,0,0))
    
    logger.info("Intialising Display")
    
    renderView1 = simple.GetActiveViewOrCreate('RenderView')
    renderView1.CameraParallelProjection = 1
    renderView1.ResetActiveCameraToPositiveX()
    renderView1.ResetCamera(False)
    
    slice1Display = simple.Show(slice1, renderView1, 'GeometryRepresentation')
    slice1Display.OSPRayScaleFunction.Points = [0.007899160496890545, 0.0, 0.5, 0.0, 1.3022315502166748, 1.0, 0.5, 0.0]
    slice1Display.ScaleTransferFunction.Points = [3.191281795501709, 0.0, 0.5, 0.0, 9.952427864074707, 1.0, 0.5, 0.0]
    slice1Display.OpacityTransferFunction.Points = [3.191281795501709, 0.0, 0.5, 0.0, 9.952427864074707, 1.0, 0.5, 0.0]
    
    logger.debug("Colour")
    simple.ColorBy(slice1Display, ('POINTS', 'UAvg', 'Magnitude'))
    slice1Display.RescaleTransferFunctionToDataRange(True, False)
    slice1Display.SetScalarBarVisibility(renderView1, True)
    
    logger.debug("Colours")
    uAvgLUT = simple.GetColorTransferFunction('UAvg')
    uAvgPWF = simple.GetOpacityTransferFunction('UAvg')
    uAvgTF2D = simple.GetTransferFunction2D('UAvg')
    uAvgLUTColorBar = simple.GetScalarBar(uAvgLUT, renderView1)
    
    logger.debug("rescale")
    # Rescale transfer function
    uAvgLUT.RescaleTransferFunction(2.0, 11.0)
    uAvgPWF.RescaleTransferFunction(2.0, 11.0)
    # Rescale 2D transfer function
    uAvgTF2D.RescaleTransferFunction(2.0, 11.0, 0.0, 1.0)

    logger.debug("placement")
    uAvgLUTColorBar.WindowLocation = 'Any Location'
    uAvgLUTColorBar.Position = [0.05459057071960298, 0.3224181360201511]
    uAvgLUTColorBar.ScalarBarLength = 0.32999999999999996

    # save data
    # simple.SaveData('/mnt/scratch2/users/40146600/t006/testData.vtm', proxy=slice1, PointDataArrays=['UAvg', 'uuPrime2'],
    #     FieldDataArrays=['CasePath'])

    logger.info("Creating Cylinder")
    cylinder1 = simple.Cylinder()
    cylinder1.Resolution = 24
    cylinder1.Height = 5.0
    cylinder1.Radius = constants.TURBINE_RADIUS
    cylinder1.Center = [1608.2, 549.5, constants.TURBINE_HUB_HEIGHT]

    logger.info("Setting Display")
    cylinder1Display = simple.Show(cylinder1, renderView1, 'GeometryRepresentation')
    cylinder1Display.OSPRayScaleFunction.Points = [0.007899160496890545, 0.0, 0.5, 0.0, 1.3022315502166748, 1.0, 0.5, 0.0]
    cylinder1Display.ScaleTransferFunction.Points = [-1.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]
    cylinder1Display.OpacityTransferFunction.Points = [-1.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]
    cylinder1Display.Orientation = [0.0, 0.0, 90.0]
    cylinder1Display.Origin = [1608.2, 549.5, 90.0]
    cylinder1Display.AmbientColor = [0.0, 0.0, 0.0]
    cylinder1Display.DiffuseColor = [0.0, 0.0, 0.0]
    cylinder1Display.Opacity = 0.5
    
    renderView1.Update()

    # get layout
    layout1 = simple.GetLayout()
    layout1.SetSize(1612, 794)

    # current camera placement for renderView1
    renderView1.CameraPosition = [-5231.190367659646, 730.8099975585938, 500.0]
    renderView1.CameraFocalPoint = [1734.199951171875, 730.8099975585938, 500.0]
    renderView1.CameraViewUp = [0.0, 0.0, 1.0]
    renderView1.CameraParallelScale = 1231.320040356749
    renderView1.CameraParallelProjection = 1

    logger.info("Saving Screenshot")
    #simple.SaveScreenshot(f'{SLICES_DIR}/test.png', renderView1, ImageResolution=[6448, 3176])
    simple.SaveScreenshot('test.png')
    logger.info("Finished")
    

if __name__ == "__main__":
    main(sys.argv[1])
    sys.exit()