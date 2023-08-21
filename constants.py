from pathlib import Path
import numpy as np

CASES_DIR = Path('/mnt/scratch2/users/40146600')

TURBINE_RADIUS = 63.0
TURBINE_DIAMETER = 2 * TURBINE_RADIUS
TURBINE_HUB_HEIGHT = 90.0
TURBINE_BASE_COORDINATES = (1118.0, 1280.0)
MEAN_WIND = 8.0
# incoming wind direction in degrees clockwise from North
WIND_DIRECTION_DEG = 240
WIND_DIRECTION = np.radians(WIND_DIRECTION_DEG)
DOMAIN_HEIGHT = 1000
DOMAIN_X = 3000
DOMAIN_Y = 3000

turbine_origin = np.array([*TURBINE_BASE_COORDINATES, TURBINE_HUB_HEIGHT])
wind_unit_vector = np.array([-np.sin(WIND_DIRECTION),
                             -np.cos(WIND_DIRECTION),
                             0])
wind_velocity = MEAN_WIND * wind_unit_vector

CELLARRAYS = ['Q', 'Rmean', 'Rwall', 'SourceT', 'SourceU', 'T', 'TAvg', 'TRMS', 'TTPrime2', 'T_0', 'Tprime', 'U', 'UAvg', 'U_0', 'Uprime', 'bodyForce', 'epsilonSGSmean', 'kResolved', 'kSGS', 'kSGSmean', 'kappat', 'nuSGSmean', 'nuSgs', 'omega', 'omegaAvg', 'p', 'p_rgh', 'p_rghAvg', 'qmean', 'qwall', 'uRMS', 'uTPrime2', 'uuPrime2']