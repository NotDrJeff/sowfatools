#!/usr/bin/env python3
"""
Jeffrey Johnston jeffrey.johnston@qub.ac.uk August 2025
"""

import gzip as gz

import numpy as np
import matplotlib.pyplot as plt

################################################################################

def plotU(case,turbine,label):
    file = f'{case}/sowfatools/turbineOutput/{case}_powerRotor_turbine{turbine}.gz'
    data = np.loadtxt(file)
    print(f'plotting case {case}, turbine {turbine}')
    plt.plot(data[:,0],data[:,2]*1e-6,label=label)

    time = data[:,0]
    data = data[time>300,2]
    print(f'Average power = {np.average(data*1e-6)}')

################################################################################

CASES_NBL = {'t001' : 'TN-10m-std', 't006' : 'TN-8m-std', 't013' : 'TN-6m-std'}

CASES_CBL = {'t004' : 'TC-10m-std', 't008' : 'TC-8m-std', 't015' : 'TC-6m-std'}

CASES_DT  = {'t011' : 'TN-10m-30Down', 't007' : 'TN-8m-30Down'}

################################################################################

for i, cases in enumerate((CASES_NBL, CASES_CBL, CASES_DT)):
    for turbine in range(2):

        print(f'Starting new plot')
        for case,label in cases.items():
            plotU(case,turbine,label)

        plt.grid()
        plt.legend()
        plt.xlabel('Time (s)')
        plt.ylabel(f'Aerodynamic Power (MW)')

        ########################################################################

        match i:
            case 0: # NBL cases
                if turbine == 0: # Upstream
                    plt.xlim(18000,21000)
                    plt.ylim(1,4)
                else: # Downstream
                    plt.xlim(18000,21000)
                    plt.ylim(0,3)
            
                plt.savefig(f'turbine_historyPower_meshComparison_nbl_turbine{turbine}.png')

            ####################################################################

            case 1: # CBL cases
                if turbine == 0:
                    plt.xlim(10000,13000)
                    plt.ylim(1,4)
                else:
                    plt.xlim(10000,13000)
                    plt.ylim(0,3)

                plt.savefig(f'turbine_historyPower_meshComparison_cbl_turbine{turbine}.png')

            ####################################################################

            case 2: # TW cases
                if turbine == 0:
                    plt.xlim(18000,21000)
                    plt.ylim(0,3)
                else:
                    plt.xlim(18000,21000)
                    plt.ylim(0,3)

                plt.savefig(f'turbine_historyPower_meshComparison_dt_turbine{turbine}.png')

        ########################################################################

        plt.cla()

