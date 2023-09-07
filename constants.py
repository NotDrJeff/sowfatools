from pathlib import Path
import numpy as np

from scipy.spatial.transform import Rotation as Rot

CASES_DIR = Path('/mnt/scratch2/users/40146600')
SOWFATOOLS_DIR = Path('sowfatools')
CONVERGENCE_DIR = SOWFATOOLS_DIR / 'convergence'
STREAMLINES_DIR = SOWFATOOLS_DIR / 'streamLines'

DOMAIN_HEIGHT = 1000
DOMAIN_X = 3000
DOMAIN_Y = 3000
DOMAIN_MAXDISTANCE = np.linalg.norm([DOMAIN_X,DOMAIN_Y,DOMAIN_HEIGHT])

REFINEMENT_ORIGIN = (667,801,0)
REFINEMENT_BOX = ((1855,1071,0),(-189,327,0),(0,0,279))
REFINEMENT_SIZE = [np.linalg.norm(i) for i in REFINEMENT_BOX]

TURBINE_RADIUS = 63
TURBINE_DIAMETER = 2 * TURBINE_RADIUS
TURBINE_HUB_HEIGHT = 90
TURBINE_BASE_COORDINATES = (1118, 1280)
TURBINE_ORIGIN = np.array([*TURBINE_BASE_COORDINATES, TURBINE_HUB_HEIGHT])

# For multiple turbines
TURBINES_RADIUS = [TURBINE_RADIUS] * 2
TURBINES_DIAMETER = 2 * TURBINES_RADIUS
TURBINES_HUB_HEIGHT = [TURBINE_HUB_HEIGHT] * 2
TURBINES_BASE_COORDINATES = (TURBINE_BASE_COORDINATES, (1882,1721))
TURBINES_ORIGIN = np.array(TURBINE_ORIGIN)
for i,turbine in enumerate(TURBINES_BASE_COORDINATES[1:]):
    TURBINES_ORIGIN = np.vstack((TURBINES_ORIGIN,
                                 np.array([*turbine,TURBINES_HUB_HEIGHT[i]])))

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

CELLARRAYS = ['Q', 'Rmean', 'Rwall', 'SourceT', 'SourceU', 'T', 'TAvg', 'TRMS',
              'TTPrime2', 'T_0', 'Tprime', 'U', 'UAvg', 'U_0', 'Uprime',
              'bodyForce', 'epsilonSGSmean', 'kResolved', 'kSGS', 'kSGSmean',
              'kappat', 'nuSGSmean', 'nuSgs', 'omega', 'omegaAvg', 'p',
              'p_rgh', 'p_rghAvg', 'qmean', 'qwall', 'uRMS', 'uTPrime2',
              'uuPrime2']