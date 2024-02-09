#!/bin/python3

import logging
from pathlib import Path

import numpy as np
logging.getLogger('matplotlib').setLevel(logging.WARNING)
import matplotlib.pyplot as plt

import constants as const
import utils

logger = logging.getLogger(__name__)

def main():    
    utils.configure_logging((const.CASES_DIR / const.SOWFATOOLS_DIR
                            / f'log.{Path(__file__).stem}'),
                            level=logging.DEBUG)
    
    logger.info(f'Plotting Mesh Covergence')
    
    power = [['t001', 'neutral', 5, 10, 1.94, 0.983],
             ['t006', 'neutral', 5, 8, 1.95, 0.961],
             ['t013', 'neutral', 5, 6, 1.95, 0.972],
             
             ['t011', 'neutral', 30, 10, 1.49, 1.59],
             ['t007', 'neutral', 30, 8, 1.49, 1.61],
             
             ['t004', 'unstable', 5, 10, 2.01, 1.34],   
             ['t008', 'unstable', 5, 8, 2.02, 1.30],
             ['t015', 'unstable', 5, 6, 2.00, 1.48],
             
             ['t017', 'unstable', 15, 8, 1.90, 1.43],
             ['t012', 'unstable', 20, 8, 1.81, 1.51],
             ['t009', 'unstable', 30, 8, 1.54, 1.62]
            ]
    
    cases = [i[0] for i in power]
    for casename in cases:
        if casename == 't012':
            continue
        
        #######################################################################
        
        casedir = const.CASES_DIR / casename
        linedir = casedir / 'postProcessing/lineSample'
        timedirs = [dir for dir in linedir.iterdir()]
        timedirs.sort(key = lambda x: float(x.name))
    
        fname = linedir / timedirs[-1] / f'lineV6_qmean_Uprime_UAvg_omegaAvg_uRMS_omega_U_uTPrime2.xy'
        data = np.genfromtxt(fname)
        height_idx = np.argmin(np.abs(data[:,0] - const.TURBINE_HUB_HEIGHT))
        U = const.WIND_ROTATION.apply(data[height_idx,7:10])
        
        power[cases.index(casename)].append(U[0])    
        del data
        
        #######################################################################
        
        casedir = const.CASES_DIR / casename
        linedir = casedir / 'postProcessing/lineSample'
        timedirs = [dir for dir in linedir.iterdir()]
        timedirs.sort(key = lambda x: float(x.name))
    
        fname = linedir / timedirs[-1] / f'lineV3_qmean_Uprime_UAvg_omegaAvg_uRMS_omega_U_uTPrime2.xy'
        data = np.genfromtxt(fname)
        height_idx = np.argmin(np.abs(data[:,0] - const.TURBINE_HUB_HEIGHT))
        U = const.WIND_ROTATION.apply(data[height_idx,7:10])
        
        power[cases.index(casename)].append(U[0])
        del data
    
    ###########################################################################
    
    subset = [i for i in power if i[0] in ['t001', 't006', 't013']]
    x = [subset[0][3]/i[3] for i in subset]
    y = [i[7] for i in subset]
    
    plt.plot(x,y)
    for i, val in enumerate(x):
        plt.text(val, y[i], f'{subset[i][7]:.2f}', ha="center", va="bottom")
        
    ###########################################################################
        
    subset = [i for i in power if i[0] in ['t011', 't007']]
    x = [subset[0][3]/i[3] for i in subset]
    y = [i[7] for i in subset]
    
    plt.plot(x,y)
    for i, val in enumerate(x):
        plt.text(val, y[i], f'{subset[i][7]:.2f}', ha="center", va="bottom")
        
    ###########################################################################
        
    subset = [i for i in power if i[0] in ['t004', 't008', 't015']]
    x = [subset[0][3]/i[3] for i in subset]
    y = [i[7] for i in subset]
    
    plt.plot(x,y)
    for i, val in enumerate(x):
        plt.text(val, y[i], f'{subset[i][7]:.2f}', ha="center", va="bottom")
        
    ###########################################################################
    
    plt.title("Streamwise Velocity at 3D Downstream (MW)")
    #plt.ylim([1,2.5])
    plt.xlabel("Refinement factor")
    
    plt.legend(labels=[f'Neutral, 5{const.deg}', f'Neutral, 30{const.deg}',
                       f'Unstable, 5{const.deg}', f'Unstable, 30{const.deg}'])
    
    plt.savefig("plots/gridConvergence3D_Usw.png")
    plt.close()

if __name__ == "__main__":
    main()
    