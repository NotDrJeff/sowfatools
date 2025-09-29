#!/bin/python3

"""
Created by Jeffrey Johnston. Jun, 2023.
"""

import logging
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

import utils
import waketools

def check_power(case_dir: Path, convergence_dir: Path) -> None:
    plt.ioff()
    plt.rc('font', size=11)
    fig, ax = plt.subplots(figsize=(7,2.6), dpi=200, layout='constrained')
    colors = iter([plt.cm.Set2(i) for i in range(8)])
    
    ax.plot(data[:,1], data[:,3]/1e6, alpha=0.3, c=(next(colors)))
    ax.plot(data[:,1], average/1e6, c=(next(colors)))

    for tolerance in tolerances:
        ymin = average[-1]/1e6*(1-tolerance/100)
        ymax = average[-1]/1e6*(1+tolerance/100)
        solid_color = next(colors)
        trans_color = list(solid_color)
        trans_color[-1] = 0.5
        ax.axhspan(ymin, ymax, edgecolor=solid_color, facecolor=trans_color, linewidth=0.3)

    #plt.xlim(left=60000)
    #plt.ylim([0.1,0.3])
    #plt.yticks(np.arange(0,3,1))

    plt.xlabel("Time (s)")
    plt.ylabel("Aerodynamic Power (MW)")

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    legend_labels = ["Raw Power", "Time-average"]
    for tolerance in tolerances:
        legend_labels.append(f'{tolerance}% tolerance band')
    ax.legend(labels=legend_labels, bbox_to_anchor=(1,0.5), loc="center left")
    #for i, tolerance in enumerate(tolerances):
    #    plt.annotate(f'{tolerance}%', (*tolerance_xy[i,:],))

    plt.grid()

    plt.savefig(str(convergence_dir/"power.png"))


if __name__=='__main__':
    #utils.configure_logger(filename=f'log.{__name__}')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    TURBINE_CASE = 't007'
    PRECURSOR_CASE = 'p005'
    
    CASES_DIR = Path('/mnt/scratch2/users/40146600')
    TURBINE_CASE_DIR = CASES_DIR / TURBINE_CASE
    PRECURSOR_CASE_DIR = CASES_DIR / PRECURSOR_CASE
    
    TURBINE_CASE_FILE = TURBINE_CASE_DIR/f'{TURBINE_CASE}.foam'
    
    SOWFATOOLS_DIR = TURBINE_CASE_DIR / 'postProcessing/sowfatools'
    SOWFAPLOTS_DIR = TURBINE_CASE_DIR / 'postProcessing/sowfaplots'
    
    logger.debug(f'Creating directory {SOWFAPLOTS_DIR}')
    SOWFAPLOTS_DIR.mkdir(parents=True, exist_ok=True)

    TURBINE_TIP_RADIUS = 63.0
    TURBINE_DIAMETER = 2 * TURBINE_TIP_RADIUS
    TURBINE_HUB_HEIGHT = 90.0
    TURBINE_BASE_COORDINATES = (1118.0, 1280.0)
    # incoming wind direction in degrees clockwise from North
    WIND_DIRECTION = np.radians(240)
    DOMAIN_HEIGHT = 1000

    CELLARRAYS = [
                  'U', 'UAvg',
                  'Uprime', 'uRMS', 'uuPrime2',
                  'p_rgh', 'p_rghAvg',
                  'T', 'TAvg',
                  'Tprime', 'TRMS', 'TTPrime2', 'uTPrime2',
                  'Rmean', 'qmean',
                  'kResolved', 'kSGS', 'kSGSmean',
                  'bodyForce',
                  'Rwall', 'qwall',
                  'SourceT', 'SourceU',
                  'T_0', 'U_0',
                  'epsilonSGSmean', 'kappat', 'nuSGSmean', 'nuSgs',
                  'omega', 'omegaAvg',
                  'Q'
                 ]

    turbine_origin = np.array([*TURBINE_BASE_COORDINATES, TURBINE_HUB_HEIGHT])
    turbine_radius = TURBINE_TIP_RADIUS
    wind_vector = np.array([-np.sin(WIND_DIRECTION),
                            -np.cos(WIND_DIRECTION),
                            0])
    rangetoplot = range(-5,8)
    
    plt.ioff()
    plt.rc('font', size=11)

    fig, axes = plt.subplots(1, 13, squeeze=True, sharey=True, sharex=True,
                            layout="constrained", figsize=[20,5], dpi=600)

    for ax in axes:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(bottom=False, labelbottom=False)
        
    for ax in axes[1:]:
        ax.spines['left'].set_visible(False)
        ax.tick_params(left=False)

    a, u0, ur = waketools.calculate_induction((SOWFATOOLS_DIR
                                              / f'{TURBINE_CASE}_turbineInte gratedWake-5D'),
                                             (SOWFATOOLS_DIR
                                              / f'{TURBINE_CASE}_turbineInte gratedWake0D'),
                                             wind_vector)
    a = 1 - ur/8
    u0 = 8

    for i in range(-5,8):
        label = f"{i}D"
        data = np.genfromtxt((SOWFATOOLS_DIR
                              /f'{TURBINE_CASE}_verticaLineSample_{label}.csv'), dtype=float, delimiter=',',
                             names=True)
        velocity = np.column_stack((data['UAvg0'], data['UAvg1'], data['UAvg2']))
        #import pdb; pdb.set_trace()
        
        sw_velocity = []
        for vel in velocity:
            sw_velocity.append(np.linalg.norm(np.dot(vel, wind_vector)))
        
        sw_velocity = np.array(sw_velocity)
        #sw_velocity = np.apply_along_axis(np.dot, 1, velocity, wind_vector)

        axes[i+5].plot(sw_velocity, data['Points2'])
        
        top = TURBINE_HUB_HEIGHT + TURBINE_TIP_RADIUS
        bottom = TURBINE_HUB_HEIGHT - TURBINE_TIP_RADIUS
        axes[i+5].vlines(ur, bottom, top, color='red')
        axes[i+5].text(ur, top, f'{ur:.1f}', ha='right', va='bottom',
                                    color='red')
        
        alpha = 0.05
        if i >= 1:
            jensenvelocity = (u0 * (1 - (2*a) / (1 + 2*alpha*i)**2))
            import pdb; pdb.set_trace()
            rw = TURBINE_DIAMETER * (1 + 2*alpha*i) / 2
            jensenbottom = TURBINE_HUB_HEIGHT - rw
            jensentop = TURBINE_HUB_HEIGHT + rw
            axes[i+5].vlines(jensenvelocity, jensenbottom, jensentop, color='green')
            axes[i+5].text(jensenvelocity, 60, f'{jensenvelocity:.1f}', ha='left',
                           va='top', color='green')
        
    plt.ylim(0,250)

    # plt.xlabel("Vel (s)")
    # plt.ylabel("Aerodynamic Power (MW)")

    # legend_labels = ["Raw Power", "Time-average"]

    # ax.legend(labels=legend_labels, bbox_to_anchor=(1,0.5), loc="center left")


    # plt.savefig(SOWFAPLOTS_DIR/f'{TURBINE_CASE}_horizontalwakeprofile.png')
    plt.savefig(SOWFAPLOTS_DIR/f'{TURBINE_CASE}_verticalwakeprofile.png')
    
    logger.info("Finished")
