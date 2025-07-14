#!/bin/python3

import logging
from pathlib import Path
import gzip

import numpy as np
logging.getLogger('matplotlib').setLevel(logging.WARNING)
import matplotlib.pyplot as plt

import constants as const
import utils

logger = logging.getLogger(__name__)

def main():
    utils.configure_logging((const.CASES_DIR / const.SOWFATOOLS_DIR
                            / f'log.{Path(__file__).stem}'),
                            level=logging.INFO)
    
    logger.info(f'Plotting Turbine Profiles')
    
    fig, axs = plt.subplots(1,3,sharey=True, sharex=True,figsize=(20,5))
    labels = ['Precursor, Neutral', 'Precursor, Unstable',
              f'Neutral, 5{const.deg}', f'Neutral, 30{const.deg}',
              f'Unstable, 5{const.deg}', f'Unstable, 30{const.deg}']
    
    for casename in ['p005','p008']:
        casedir = const.CASES_DIR / casename
        avgdir = casedir / const.SOWFATOOLS_DIR / 'averaging'
        
        fname = avgdir / f'{casename}_uu_mean.gz'
        data = np.genfromtxt(fname)
        
        fname = avgdir / f'{casename}_vv_mean.gz'
        data[:,1:] += np.genfromtxt(fname)[:,1:]
        
        fname = avgdir / f'{casename}_ww_mean.gz'
        data[:,1:] += np.genfromtxt(fname)[:,1:]
        
        data[:,1:] /= 2
        
        with gzip.open(fname,mode='rt') as file:
            heights = (file.readline().removeprefix('#').split())[2:]
            
        heights = np.unique([height.split('_')[-1] for height in heights]).astype('float')
        heights.sort()
        
        for i in range(len(axs)):
            axs[i].plot(data[-1,3::2],heights, '--')
            axs[i].set_ylim(10,250)
            #axs[i].set_xlim(0,1.3)
            
        del data
        
    for casename in ['t006', 't007', 't008', 't009']:
        casedir = const.CASES_DIR / casename
        linedir = casedir / 'postProcessing/lineSample'
        timedirs = [dir for dir in linedir.iterdir()]
        timedirs.sort(key = lambda x: float(x.name))
        
        for i,D in np.ndenumerate(range(2, 2*len(axs)+1, 2)):
            fname = linedir / timedirs[-1] / f'lineV{D}_kSGSmean_p_Q_TAvg_TTPrime2_epsilonSGSmean_nuSgs_kappat_nuSGSmean_T_kResolved_p_rghAvg_Tprime_kSGS_p_rgh_TRMS.xy'
            # UAvg contained in columns 1-3
            data = np.genfromtxt(fname)
            # U = const.WIND_ROTATION.apply(data[:,7:10])
            
            axs[i].plot(data[:,11], data[:,0])
            del data
            
            plt.text(0.95,0.95,f'+{D}D',transform=axs[i].transAxes, va='bottom', ha='right')
    
    for i in range(len(axs)):
        axs[i].axhline(y=90+63, color='gray', linestyle='--')
        axs[i].axhline(y=90-63, color='gray', linestyle='--')
    
    plt.suptitle("Downstream Profile of Resolved TKE")
    axs[0].set_ylabel("Height (m)")
    fig.supxlabel("TKE $(m^2/s^2)$")
    fig.legend(labels=labels, loc='center right')
    plt.savefig('plots/kProfile.png')
    

if __name__ == "__main__":
    main()
    