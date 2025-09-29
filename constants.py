"""Compatible with Python 3.13, SOWFA 2.4.x
Part of github.com/NotDrJeff/sowfatools
Jeffrey Johnston   jeffrey.johnston@qub.ac.uk  July 2025

This module contains constants used throughtout other scripts
"""

from pathlib import Path
import logging

import numpy as np
from scipy.spatial.transform import Rotation as Rot

logger = logging.getLogger(__name__)

#CASES_DIR = Path('/mnt/scratch2/users/40146600')
CASES_DIR = Path('/mnt/autofs/mcclayrds-projects/ad00069/johnston_2024_thesis')
#CASES_DIR = Path('/mnt/autofs/mcclayrds-projects/ad00069')
SOWFATOOLS_DIR = Path('sowfatools')
TURBINEOUTPUT_DIR = SOWFATOOLS_DIR / 'turbineOutput'
TURBINEPLOT_DIR = SOWFATOOLS_DIR / 'turbinePlots'
CONVERGENCE_DIR = SOWFATOOLS_DIR / 'convergence'
STREAMLINES_DIR = SOWFATOOLS_DIR / 'streamLines'
PARAVIEW_DIRECTORY = Path('postProcessing') # temporary

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

TURBINE_SPACING = 7
TURBINE_SPACING_m = TURBINE_SPACING*TURBINE_DIAMETER

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


# TURBINE_QUANTITES and BLADE_QUANTITIES refer to files in turbineOutput folder
TURBINE_QUANTITIES = ['azimuth','nacYaw','pitch','powerGenerator',
                      'powerRotor','rotSpeed','rotSpeedFiltered','thrust',
                      'torqueGen','torqueRotor']

BLADE_QUANTITIES = ['alpha','axialForce','Cd','Cl','drag','lift',
                    'tangentialForce','Vaxial','Vmag','Vradial','Vtangential',
                    'x','y','z']


# AVERAGING_QUANTITIES refers to files in averaging folder (precursors)
AVERAGING_QUANTITIES = ['q3_mean', 'R22_mean', 'Tw_mean', 'R11_mean', 'uu_mean',
                        'wuu_mean', 'R12_mean', 'wuv_mean', 'www_mean',
                        'uw_mean', 'q1_mean', 'Tv_mean', 'TI', 'vv_mean',
                        'R13_mean', 'ww_mean', 'wuw_mean', 'Tu_mean', 'nu_SGS_mean',
                        'uv_mean', 'wvw_mean', 'R33_mean', 'wvv_mean',
                        'U_mean', 'R23_mean', 'W_mean', 'vw_mean', 'q2_mean',
                        'T_mean', 'V_mean']


# SCALAR_QUANTITIES, VECTOR_QUANTITIES and SYMMTENSOR_QUANTITIES refer to fields
# produced by windPlantSolver
SCALAR_QUANTITIES = {'T', 'TAvg', 'Tprime', 'TTPrime2', 'TRMS', 'SourceT',
                     'p_rgh', 'p_rghAvg', 'Q',
                     'nuSgs', 'nuSGSmean', 'kSGS', 'kSGSmean', 'kResolved',
                     'omega', 'omegaAvg', 'kappat', 'epsilonSGSmean'}

VECTOR_QUANTITIES = {'U', 'UAvg', 'Uprime', 'uRMS', 'SourceU', 'phi',
                     'bodyForce', 'qmean', 'qwall'}

SYMMTENSOR_QUANTITIES = {'uuPrime2', 'uTPrime2', 'Rmean', 'Rwall'}

CELLARRAYS = (SCALAR_QUANTITIES | VECTOR_QUANTITIES | SYMMTENSOR_QUANTITIES
              | {'T_0', 'U_0', 'p'}) # OR operator to find union of sets

deg = u'\N{DEGREE SIGN}'

g = 9.81 # m/s^2
VONKARMAN = 0.4
AIR_DENSITY = 1.225 # kg/m^3

if __name__ == '__main__':
    logger.error('This module is not intended to be run as a script')
