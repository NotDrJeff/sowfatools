import logging
from pathlib import Path
import utils

logger = logging.getLogger(__name__)

utils.configure_logging(f"log.{Path(__file__).stem}", level=logging.DEBUG)

logger.info("BEGIN")

# trace generated using paraview version 5.11.1
#import paraview
#paraview.compatibility.major = 5
#paraview.compatibility.minor = 11

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# create a new 'OpenFOAMReader'
logger.debug("Open casefile")
t006foam = OpenFOAMReader(registrationName='t006.foam', FileName='/mnt/scratch2/users/40146600/t006/t006.foam')
t006foam.MeshRegions = ['internalMesh']
t006foam.CellArrays = ['Q', 'Rmean', 'Rwall', 'SourceT', 'SourceU', 'T', 'TAvg', 'TRMS', 'TTPrime2', 'T_0', 'Tprime', 'U', 'UAvg', 'U_0', 'Uprime', 'bodyForce', 'epsilonSGSmean', 'kResolved', 'kSGS', 'kSGSmean', 'kappat', 'nuSGSmean', 'nuSgs', 'omega', 'omegaAvg', 'p', 'p_rgh', 'p_rghAvg', 'qmean', 'qwall', 'uRMS', 'uTPrime2', 'uuPrime2']

# get animation scene
animationScene1 = GetAnimationScene()

# update animation scene based on data timesteps
animationScene1.UpdateAnimationUsingDataTimeSteps()

# Properties modified on t006foam
t006foam.Createcelltopointfiltereddata = 0
t006foam.CellArrays = ['UAvg', 'uuPrime2']

logger.debug("Create renderview1")
# get active view
renderView1 = GetActiveViewOrCreate('RenderView')

# show data in view
t006foamDisplay = Show(t006foam, renderView1, 'UnstructuredGridRepresentation')

# trace defaults for the display properties.
t006foamDisplay.Representation = 'Surface'
t006foamDisplay.ColorArrayName = [None, '']
t006foamDisplay.SelectTCoordArray = 'None'
t006foamDisplay.SelectNormalArray = 'None'
t006foamDisplay.SelectTangentArray = 'None'
t006foamDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
t006foamDisplay.SelectOrientationVectors = 'None'
t006foamDisplay.ScaleFactor = 300.0
t006foamDisplay.SelectScaleArray = 'None'
t006foamDisplay.GlyphType = 'Arrow'
t006foamDisplay.GlyphTableIndexArray = 'None'
t006foamDisplay.GaussianRadius = 15.0
t006foamDisplay.SetScaleArray = [None, '']
t006foamDisplay.ScaleTransferFunction = 'PiecewiseFunction'
t006foamDisplay.OpacityArray = [None, '']
t006foamDisplay.OpacityTransferFunction = 'PiecewiseFunction'
t006foamDisplay.DataAxesGrid = 'GridAxesRepresentation'
t006foamDisplay.PolarAxes = 'PolarAxesRepresentation'
t006foamDisplay.ScalarOpacityUnitDistance = 11.555861023829266
t006foamDisplay.OpacityArrayName = ['CELLS', 'UAvg']
t006foamDisplay.SelectInputVectors = [None, '']
t006foamDisplay.WriteLog = ''

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
t006foamDisplay.OSPRayScaleFunction.Points = [0.007899160496890545, 0.0, 0.5, 0.0, 1.3022315502166748, 1.0, 0.5, 0.0]

# reset view to fit data
renderView1.ResetCamera(False)

# get the material library
materialLibrary1 = GetMaterialLibrary()

# update the view to ensure updated data information
logger.debug("Update renderview1")
renderView1.Update()

# create a new 'Transform'
logger.debug("Create transform1")
transform1 = Transform(registrationName='Transform1', Input=t006foam)
transform1.Transform = 'Transform'

# Properties modified on renderView1
renderView1.CameraParallelProjection = 1

# Properties modified on transform1.Transform
transform1.Transform.Rotate = [0.0, 0.0, -30.0]

# show data in view
transform1Display = Show(transform1, renderView1, 'UnstructuredGridRepresentation')

# trace defaults for the display properties.
transform1Display.Representation = 'Surface'
transform1Display.ColorArrayName = [None, '']
transform1Display.SelectTCoordArray = 'None'
transform1Display.SelectNormalArray = 'None'
transform1Display.SelectTangentArray = 'None'
transform1Display.OSPRayScaleFunction = 'PiecewiseFunction'
transform1Display.SelectOrientationVectors = 'None'
transform1Display.ScaleFactor = 409.8076171875
transform1Display.SelectScaleArray = 'None'
transform1Display.GlyphType = 'Arrow'
transform1Display.GlyphTableIndexArray = 'None'
transform1Display.GaussianRadius = 20.490380859375
transform1Display.SetScaleArray = [None, '']
transform1Display.ScaleTransferFunction = 'PiecewiseFunction'
transform1Display.OpacityArray = [None, '']
transform1Display.OpacityTransferFunction = 'PiecewiseFunction'
transform1Display.DataAxesGrid = 'GridAxesRepresentation'
transform1Display.PolarAxes = 'PolarAxesRepresentation'
transform1Display.ScalarOpacityUnitDistance = 15.591614972563665
transform1Display.OpacityArrayName = ['CELLS', 'UAvg']
transform1Display.SelectInputVectors = [None, '']
transform1Display.WriteLog = ''

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
transform1Display.OSPRayScaleFunction.Points = [0.007899160496890545, 0.0, 0.5, 0.0, 1.3022315502166748, 1.0, 0.5, 0.0]

# hide data in view
Hide(t006foam, renderView1)

# update the view to ensure updated data information
logger.debug("Update renderview1")
renderView1.Update()

# create a new 'Cell Data to Point Data'
logger.debug("Create point Data")
cellDatatoPointData1 = CellDatatoPointData(registrationName='CellDatatoPointData1', Input=transform1)
cellDatatoPointData1.CellDataArraytoprocess = ['UAvg', 'uuPrime2']

# show data in view
cellDatatoPointData1Display = Show(cellDatatoPointData1, renderView1, 'UnstructuredGridRepresentation')

# trace defaults for the display properties.
cellDatatoPointData1Display.Representation = 'Surface'
cellDatatoPointData1Display.ColorArrayName = [None, '']
cellDatatoPointData1Display.SelectTCoordArray = 'None'
cellDatatoPointData1Display.SelectNormalArray = 'None'
cellDatatoPointData1Display.SelectTangentArray = 'None'
cellDatatoPointData1Display.OSPRayScaleArray = 'UAvg'
cellDatatoPointData1Display.OSPRayScaleFunction = 'PiecewiseFunction'
cellDatatoPointData1Display.SelectOrientationVectors = 'None'
cellDatatoPointData1Display.ScaleFactor = 409.8076171875
cellDatatoPointData1Display.SelectScaleArray = 'None'
cellDatatoPointData1Display.GlyphType = 'Arrow'
cellDatatoPointData1Display.GlyphTableIndexArray = 'None'
cellDatatoPointData1Display.GaussianRadius = 20.490380859375
cellDatatoPointData1Display.SetScaleArray = ['POINTS', 'UAvg']
cellDatatoPointData1Display.ScaleTransferFunction = 'PiecewiseFunction'
cellDatatoPointData1Display.OpacityArray = ['POINTS', 'UAvg']
cellDatatoPointData1Display.OpacityTransferFunction = 'PiecewiseFunction'
cellDatatoPointData1Display.DataAxesGrid = 'GridAxesRepresentation'
cellDatatoPointData1Display.PolarAxes = 'PolarAxesRepresentation'
cellDatatoPointData1Display.ScalarOpacityUnitDistance = 15.591614972563665
cellDatatoPointData1Display.OpacityArrayName = ['POINTS', 'UAvg']
cellDatatoPointData1Display.SelectInputVectors = ['POINTS', 'UAvg']
cellDatatoPointData1Display.WriteLog = ''

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
cellDatatoPointData1Display.OSPRayScaleFunction.Points = [0.007899160496890545, 0.0, 0.5, 0.0, 1.3022315502166748, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
cellDatatoPointData1Display.ScaleTransferFunction.Points = [2.4045069217681885, 0.0, 0.5, 0.0, 9.969176292419434, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
cellDatatoPointData1Display.OpacityTransferFunction.Points = [2.4045069217681885, 0.0, 0.5, 0.0, 9.969176292419434, 1.0, 0.5, 0.0]

# hide data in view
Hide(transform1, renderView1)

# update the view to ensure updated data information
logger.debug("Update renderview1")
renderView1.Update()

# create a new 'Slice'
logger.debug("Create slice1")
slice1 = Slice(registrationName='Slice1', Input=cellDatatoPointData1)
slice1.SliceType = 'Plane'
slice1.HyperTreeGridSlicer = 'Plane'
slice1.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice1.SliceType.Origin = [2049.0380859375, 549.0380859375, 500.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice1.HyperTreeGridSlicer.Origin = [2049.0380859375, 549.0380859375, 500.0]

# toggle interactive widget visibility (only when running from the GUI)
HideInteractiveWidgets(proxy=slice1.SliceType)

# Properties modified on slice1.SliceType
slice1.SliceType.Origin = [1734.2, 549.5, 90.0]

# show data in view
slice1Display = Show(slice1, renderView1, 'GeometryRepresentation')

# trace defaults for the display properties.
slice1Display.Representation = 'Surface'
slice1Display.ColorArrayName = [None, '']
slice1Display.SelectTCoordArray = 'None'
slice1Display.SelectNormalArray = 'None'
slice1Display.SelectTangentArray = 'None'
slice1Display.OSPRayScaleArray = 'UAvg'
slice1Display.OSPRayScaleFunction = 'PiecewiseFunction'
slice1Display.SelectOrientationVectors = 'None'
slice1Display.ScaleFactor = 346.41016845703126
slice1Display.SelectScaleArray = 'None'
slice1Display.GlyphType = 'Arrow'
slice1Display.GlyphTableIndexArray = 'None'
slice1Display.GaussianRadius = 17.320508422851564
slice1Display.SetScaleArray = ['POINTS', 'UAvg']
slice1Display.ScaleTransferFunction = 'PiecewiseFunction'
slice1Display.OpacityArray = ['POINTS', 'UAvg']
slice1Display.OpacityTransferFunction = 'PiecewiseFunction'
slice1Display.DataAxesGrid = 'GridAxesRepresentation'
slice1Display.PolarAxes = 'PolarAxesRepresentation'
slice1Display.SelectInputVectors = ['POINTS', 'UAvg']
slice1Display.WriteLog = ''

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
slice1Display.OSPRayScaleFunction.Points = [0.007899160496890545, 0.0, 0.5, 0.0, 1.3022315502166748, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice1Display.ScaleTransferFunction.Points = [3.191281795501709, 0.0, 0.5, 0.0, 9.952427864074707, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice1Display.OpacityTransferFunction.Points = [3.191281795501709, 0.0, 0.5, 0.0, 9.952427864074707, 1.0, 0.5, 0.0]

# hide data in view
Hide(cellDatatoPointData1, renderView1)

# update the view to ensure updated data information
logger.debug("Update renderview1")
renderView1.Update()

renderView1.ResetActiveCameraToPositiveX()

# reset view to fit data
renderView1.ResetCamera(False)

# set scalar coloring
logger.debug("Create colours")
ColorBy(slice1Display, ('POINTS', 'UAvg', 'Magnitude'))

# rescale color and/or opacity maps used to include current data range
slice1Display.RescaleTransferFunctionToDataRange(True, False)

# show color bar/color legend
slice1Display.SetScalarBarVisibility(renderView1, True)

# get color transfer function/color map for 'UAvg'
uAvgLUT = GetColorTransferFunction('UAvg')

# get opacity transfer function/opacity map for 'UAvg'
uAvgPWF = GetOpacityTransferFunction('UAvg')

# get 2D transfer function for 'UAvg'
uAvgTF2D = GetTransferFunction2D('UAvg')

# get color legend/bar for uAvgLUT in view renderView1
uAvgLUTColorBar = GetScalarBar(uAvgLUT, renderView1)

# change scalar bar placement
uAvgLUTColorBar.WindowLocation = 'Any Location'
uAvgLUTColorBar.Position = [0.05459057071960298, 0.3224181360201511]
uAvgLUTColorBar.ScalarBarLength = 0.32999999999999996

# save data
# SaveData('/mnt/scratch2/users/40146600/t006/testData.vtm', proxy=slice1, PointDataArrays=['UAvg', 'uuPrime2'],
#     FieldDataArrays=['CasePath'])

# Rescale transfer function
uAvgLUT.RescaleTransferFunction(2.0, 11.0)

# Rescale transfer function
uAvgPWF.RescaleTransferFunction(2.0, 11.0)

# Rescale 2D transfer function
uAvgTF2D.RescaleTransferFunction(2.0, 11.0, 0.0, 1.0)

# create a new 'Cylinder'
logger.debug("Create cylinder")
cylinder1 = Cylinder(registrationName='Cylinder1')

# Properties modified on cylinder1
cylinder1.Resolution = 124
cylinder1.Height = 5.0
cylinder1.Radius = 63.0
cylinder1.Center = [25.0, 25.0, 23.0]

# show data in view
cylinder1Display = Show(cylinder1, renderView1, 'GeometryRepresentation')

# trace defaults for the display properties.
cylinder1Display.Representation = 'Surface'
cylinder1Display.ColorArrayName = [None, '']
cylinder1Display.SelectTCoordArray = 'TCoords'
cylinder1Display.SelectNormalArray = 'Normals'
cylinder1Display.SelectTangentArray = 'None'
cylinder1Display.OSPRayScaleArray = 'Normals'
cylinder1Display.OSPRayScaleFunction = 'PiecewiseFunction'
cylinder1Display.SelectOrientationVectors = 'None'
cylinder1Display.ScaleFactor = 12.600000000000001
cylinder1Display.SelectScaleArray = 'None'
cylinder1Display.GlyphType = 'Arrow'
cylinder1Display.GlyphTableIndexArray = 'None'
cylinder1Display.GaussianRadius = 0.63
cylinder1Display.SetScaleArray = ['POINTS', 'Normals']
cylinder1Display.ScaleTransferFunction = 'PiecewiseFunction'
cylinder1Display.OpacityArray = ['POINTS', 'Normals']
cylinder1Display.OpacityTransferFunction = 'PiecewiseFunction'
cylinder1Display.DataAxesGrid = 'GridAxesRepresentation'
cylinder1Display.PolarAxes = 'PolarAxesRepresentation'
cylinder1Display.SelectInputVectors = ['POINTS', 'Normals']
cylinder1Display.WriteLog = ''

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
cylinder1Display.OSPRayScaleFunction.Points = [0.007899160496890545, 0.0, 0.5, 0.0, 1.3022315502166748, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
cylinder1Display.ScaleTransferFunction.Points = [-1.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
cylinder1Display.OpacityTransferFunction.Points = [-1.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

# update the view to ensure updated data information
logger.debug("Update renderview1")
renderView1.Update()

# Properties modified on cylinder1Display
logger.debug("Modify cylinder")
cylinder1Display.Orientation = [25.0, 0.0, 0.0]

# Properties modified on cylinder1Display.PolarAxes
cylinder1Display.PolarAxes.Orientation = [25.0, 0.0, 0.0]

# Properties modified on cylinder1Display
cylinder1Display.Orientation = [25.0, 23.0, 0.0]

# Properties modified on cylinder1Display.PolarAxes
cylinder1Display.PolarAxes.Orientation = [25.0, 23.0, 0.0]

# Properties modified on cylinder1Display
cylinder1Display.Orientation = [25.0, 23.0, 45.0]

# Properties modified on cylinder1Display.PolarAxes
cylinder1Display.PolarAxes.Orientation = [25.0, 23.0, 45.0]

# Properties modified on cylinder1Display
cylinder1Display.Position = [0.0, 0.0, 30.0]

# Properties modified on cylinder1Display.DataAxesGrid
cylinder1Display.DataAxesGrid.Position = [0.0, 0.0, 30.0]

# Properties modified on cylinder1Display.PolarAxes
cylinder1Display.PolarAxes.Translation = [0.0, 0.0, 30.0]

# Properties modified on cylinder1Display
cylinder1Display.Orientation = [0.0, 23.0, 45.0]

# Properties modified on cylinder1Display.PolarAxes
cylinder1Display.PolarAxes.Orientation = [0.0, 23.0, 45.0]

# Properties modified on cylinder1Display
cylinder1Display.Orientation = [0.0, 0.0, 45.0]

# Properties modified on cylinder1Display.PolarAxes
cylinder1Display.PolarAxes.Orientation = [0.0, 0.0, 45.0]

# Properties modified on cylinder1Display
cylinder1Display.Orientation = [0.0, 0.0, 0.0]

# Properties modified on cylinder1Display.PolarAxes
cylinder1Display.PolarAxes.Orientation = [0.0, 0.0, 0.0]

# Properties modified on cylinder1Display
cylinder1Display.Position = [0.0, 0.0, 0.0]

# Properties modified on cylinder1Display.DataAxesGrid
cylinder1Display.DataAxesGrid.Position = [0.0, 0.0, 0.0]

# Properties modified on cylinder1Display.PolarAxes
cylinder1Display.PolarAxes.Translation = [0.0, 0.0, 0.0]

# Properties modified on cylinder1Display
cylinder1Display.Orientation = [0.0, 0.0, 30.0]

# Properties modified on cylinder1Display.PolarAxes
cylinder1Display.PolarAxes.Orientation = [0.0, 0.0, 30.0]

# Properties modified on cylinder1Display
cylinder1Display.Origin = [54.0, 0.0, 0.0]

# Properties modified on cylinder1Display
cylinder1Display.Origin = [54.0, 54.0, 0.0]

# Properties modified on cylinder1Display
cylinder1Display.Origin = [54.0, 54.0, 54.0]

# change solid color
cylinder1Display.AmbientColor = [0.0, 0.0, 0.0]
cylinder1Display.DiffuseColor = [0.0, 0.0, 0.0]

# Properties modified on cylinder1Display
cylinder1Display.Opacity = 0.47

# Properties modified on cylinder1Display
cylinder1Display.Opacity = 0.44

# Properties modified on cylinder1Display
cylinder1Display.Opacity = 0.41

# Properties modified on cylinder1Display
cylinder1Display.Opacity = 0.38

# Properties modified on cylinder1Display
cylinder1Display.Opacity = 0.41

# Properties modified on cylinder1Display
cylinder1Display.Opacity = 0.44

# get layout
layout1 = GetLayout()

# layout/tab size in pixels
layout1.SetSize(1612, 794)

# current camera placement for renderView1
renderView1.CameraPosition = [-5231.190367659646, 730.8099975585938, 500.0]
renderView1.CameraFocalPoint = [1734.199951171875, 730.8099975585938, 500.0]
renderView1.CameraViewUp = [0.0, 0.0, 1.0]
renderView1.CameraParallelScale = 1231.320040356749
renderView1.CameraParallelProjection = 1

# save screenshot

#================================================================
# addendum: following script captures some of the application
# state to faithfully reproduce the visualization during playback
#================================================================

#--------------------------------
# saving layout sizes for layouts

# layout/tab size in pixels
logger.debug("Final layout / camera changes")
layout1.SetSize(1612, 794)

#-----------------------------------
# saving camera placements for views

# current camera placement for renderView1
renderView1.CameraPosition = [-5231.190367659646, 730.8099975585938, 500.0]
renderView1.CameraFocalPoint = [1734.199951171875, 730.8099975585938, 500.0]
renderView1.CameraViewUp = [0.0, 0.0, 1.0]
renderView1.CameraParallelScale = 1231.320040356749
renderView1.CameraParallelProjection = 1

#--------------------------------------------
# uncomment the following to render all views
# RenderAllViews()
# alternatively, if you want to write images, you can use SaveScreenshot(...).
logger.debug("Create screenshot")
# SaveScreenshot('/users/40146600/scripts/sowfatools/test.png', renderView1, ImageResolution=[6448, 3176])
SaveScreenshot('/users/40146600/scripts/sowfatools/test.png')

logger.info("END")