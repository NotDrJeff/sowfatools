from pathlib import Path
import numpy as np

from scipy.spatial.transform import Rotation as Rot

CASES_DIR = Path('/mnt/scratch2/users/40146600')

DOMAIN_HEIGHT = 1000
DOMAIN_X = 3000
DOMAIN_Y = 3000

TURBINE_RADIUS = 63.0
TURBINE_DIAMETER = 2 * TURBINE_RADIUS
TURBINE_HUB_HEIGHT = 90.0
TURBINE_BASE_COORDINATES = (1118.0, 1280.0)
TURBINE_ORIGIN = np.array([*TURBINE_BASE_COORDINATES, TURBINE_HUB_HEIGHT])

MEAN_WIND_SPEED = 8.0
WIND_DIRECTION_DEG = 240 # incoming direction, clockwise from North
WIND_DIRECTION_RAD = np.radians(WIND_DIRECTION_DEG)

WIND_UNIT_VECTOR = np.array([-np.sin(WIND_DIRECTION_RAD),
                             -np.cos(WIND_DIRECTION_RAD),
                             0])
MEAN_WIND_VELOCITY = MEAN_WIND_SPEED * WIND_UNIT_VECTOR

# For convenience in paraview, we rotate the domain so wind direction aligns
# with x coordinate
WIND_ROTATION = Rot.from_rotvec((0,0,WIND_DIRECTION_DEG+90),degrees=True)
TURBINE_ORIGIN_ROTATED = WIND_ROTATION.apply(TURBINE_ORIGIN)

CELLARRAYS = ['Q', 'Rmean', 'Rwall', 'SourceT', 'SourceU', 'T', 'TAvg', 'TRMS', 'TTPrime2', 'T_0', 'Tprime', 'U', 'UAvg', 'U_0', 'Uprime', 'bodyForce', 'epsilonSGSmean', 'kResolved', 'kSGS', 'kSGSmean', 'kappat', 'nuSGSmean', 'nuSgs', 'omega', 'omegaAvg', 'p', 'p_rgh', 'p_rghAvg', 'qmean', 'qwall', 'uRMS', 'uTPrime2', 'uuPrime2']