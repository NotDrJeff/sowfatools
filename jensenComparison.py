#!/bin/python3

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from constants import *
import waketools

#plot t006 only and save

CASES_DIR = Path('/mnt/scratch2/users/40146600')
DATA_REL_DIR = 'postProcessing/sowfatools'
PLOTS_REL_DIR = 'postProcessing/sowfaplots'
FILE_IDENTIFIER = 'turbineIntegratedWake'

CASE_LABELS = {'t006':'8m, Neutral, Std. Tilt',
               't007':'8m, Neutral, 30 deg Tilt',
               't008':'8m, Unstable, Std. Tilt',
               't009':'8m, Unstable, 30 deg Tilt'}

plt.ioff()

def intiate_plot():
    fig,ax = plt.subplots(figsize=(15,5), layout='constrained')
    ax.vlines([0,7],3,8,linestyles='dotted',colors='r')
    ax.set_title('Average Velocity in Turbine Wake')
    ax.set_xlabel('Distance in Diameters from Upstream Turbine')
    ax.set_ylabel('Velocity Integrated Over Rotor Area (m/s)')
    ax.grid()
    return fig,ax
    
fig,ax = intiate_plot()

# for case in ['t006','t007','t008','t009',]:
#     tools_dir = CASES_DIR / case / DATA_REL_DIR
#     plots_dir = CASES_DIR / case / PLOTS_REL_DIR

#     files = [file for file in tools_dir.iterdir()
#             if FILE_IDENTIFIER in file.name]

#     data = np.zeros((len(files),2))
#     for i, file in enumerate(files):
#         x = file.stem.removeprefix(f'{case}_{FILE_IDENTIFIER}').removesuffix('D')
#         contents = np.genfromtxt(file, delimiter=',', names=True)
#         velocity = np.array([contents['UAvg0'], contents['UAvg1'], contents['UAvg2']])
#         sw_velocity = np.dot(velocity, wind_unit_vector)
        
#         data[i,:] = np.hstack((x,sw_velocity))

#     data = data[data[:,0].argsort()]
    
#     np.savetxt(f'{case}_{FILE_IDENTIFIER}.txt', data)
    
#     ax.plot(data[:,0],data[:,1], label=CASE_LABELS[case])
    
# plt.legend()
# fig.savefig(f'integratedVelocity.png')

for case in ['t006','t007','t008','t009']:
    plt.close()
    print(f'CASE: {case}')
    fig,ax = intiate_plot()
    data = np.loadtxt(f'{case}_{FILE_IDENTIFIER}.txt')
    
    ax.plot(data[:,0],data[:,1], label=CASE_LABELS[case])
    
    v_r1 = float(data[np.where(data[:,0] == 0),1])
    a1 = 1 - v_r1/8
    print(f'{v_r1=} {a1=}')
    
    v_r2 = float(data[np.where(data[:,0] == 7),1])
    u2 = float(data[np.where(data[:,0] == 5),1])
    a2 = 1 - v_r2/u2
    
    print(f'{u2=} {v_r2=} {a2=}')
    
    for alpha in [x/100 for x in range(2,8,1)]:
        velocities = [waketools.jensen_velocity(8,a1,alpha,i)
                      for i in range(1,7)]
        
        ax.plot(range(1,7),velocities, label=f'{alpha=}')
        
        velocities = [waketools.jensen_velocity(u2,a2,alpha,i)
                      for i in range(1,5)]
        
        ax.plot(range(8,12),velocities,label=f'{alpha=} {a2=}')
        
    
    plt.legend()
    ax.set_xlim(-5)
    print('\n\n')
    
