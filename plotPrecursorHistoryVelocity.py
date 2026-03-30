#!/usr/bin/env python3
"""
Jeffrey Johnston jeffrey.johnston@qub.ac.uk August 2025
"""

import gzip as gz

import numpy as np
import matplotlib.pyplot as plt

################################################################################

def hubheightidx(file,height_to_plot):
    with gz.open(file,'rt') as f:
        header = f.readline()
    header = header.removeprefix('# ')
    heights = header.split()[2:]
    heights = [height.removesuffix('m') for height in heights]
    heights = np.array(heights,dtype=float)
    diff = heights - height_to_plot
    diff[diff<0] = np.inf
    return heights, np.argmin(diff)

def interpolateheight(data1,data2,height1,height2,height_to_plot):
    frac = (height_to_plot-height1) / (height2-height1)
    return data1 + (data2-data1)*frac

def plotU(case, height_to_plot,label):
    file = f'{case}/sowfatools/averaging/{case}_U_mean_sw.gz'
    data = np.loadtxt(file)
    heights, idx = hubheightidx(file,height_to_plot)
    time = data[:,0]
    data = interpolateheight(data[:,idx+2-1],
                             data[:,idx+2],
                             heights[idx-1],
                             heights[idx],
                             height_to_plot)
    print(f'plotting case {case}: '
          f'interpolated between {heights[idx-1]} and {heights[idx]}')
    if case == 'p004': time -= 62000
    plt.plot(time,data,label=label)

################################################################################

HEIGHTS_TO_PLOT = (27,153)

CASES_NBL = {'p001' : 'PN-10m-LR', 'p005' : 'PN-8m', 'p013' : 'PN-6m', 'p011' : 'PN-5m'}

CASES_CBL = {'p003' : 'PC-10m', 'p008' : 'PC-8m', 'p014' : 'PC-6m', 'p012' : 'PC-5m'}

CASES_TW  = {'p002' : 'PN-10m', 'p202' : 'PN-10m-RR', 'p004' : 'PN-10m-TW2'}

################################################################################

# Plot first height

for i, cases in enumerate((CASES_NBL, CASES_CBL, CASES_TW)):
    for j, height_to_plot in enumerate(HEIGHTS_TO_PLOT):

        for case,label in cases.items():
            print(f'Starting new plot')
            plotU(case,height_to_plot,label)

        plt.grid()
        plt.legend()
        plt.xlabel('Time (s)')
        plt.ylabel(f'Streamwise Velocity (m/s) at z={height_to_plot} m')

        ########################################################################

        match i:
            case 0: # NBL cases
                if j == 1: # 153 m
                    plt.xlim(4000,22000)
                    plt.ylim(8,9.6)
                else: # 27 m
                    plt.xlim(4000,22000)
                    plt.ylim(6.2,7.8)
            
                plt.savefig(f'precursor_historyVelocity_meshComparison_nbl_{height_to_plot}m.png')

            ####################################################################

            case 1: # CBL cases
                if j == 1:
                    plt.xlim(4000,14000)
                    plt.ylim(7,8.6)
                else:
                    plt.xlim(0,14000)
                    plt.ylim(7,8.6)

                plt.savefig(f'precursor_historyVelocity_meshComparison_cbl_{height_to_plot}m.png')

            ####################################################################

            case 2: # TW cases
                if j ==1:
                    plt.xlim(18000,21000)
                    plt.ylim(8,9)
                else:
                    plt.xlim(18000,21000)
                    plt.ylim(6.5,7.5)

                plt.savefig(f'precursor_historyVelocity_meshComparison_tw_{height_to_plot}m.png')

        ########################################################################

        plt.cla()

