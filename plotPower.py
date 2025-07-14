#!/bin/python3

import logging
from pathlib import Path

logging.getLogger('matplotlib').setLevel(logging.WARNING)
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import constants as const
import utils

logger = logging.getLogger(__name__)

def main():
    
    logger.info(f'Plotting Comparison of Turbine Power Output')

    utils.configure_logging((const.CASES_DIR / const.SOWFATOOLS_DIR
                            / f'log.{Path(__file__).stem}'),
                            level=logging.INFO)
    
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
    
    names = [i[0] for i in power]
    
    degsym = u'\N{DEGREE SIGN}'
    
    # Turbine 1
    subset = [i for i in power if i[0] in ['t006', 't007', 't008','t017', 't012', 't009']]
    x = [f'{i[1]}\n{i[2]}{degsym}' for i in subset]
    y = [i[4] for i in subset]
    colors = ['tab:blue','tab:blue','tab:red','tab:red', 'tab:red', 'tab:red']
    
    plt.bar(x,y, color=colors)
    
    plt.title("Upstream Turbine Aerodynamic Power (MW)")
    plt.ylim([1,2.5])
    
    legend_lines = [Line2D([0], [0], color='tab:blue', lw=4),
                    Line2D([0], [0], color='tab:red', lw=4),
                   ]
    
    plt.legend(legend_lines, ['neutral', 'unstable'])
    
    labels = ['', #t006
              f'{(power[names.index("t007")][4] / power[names.index("t006")][4] - 1)*100:+.1f}%', #t007
              '', #t008
              f'{(power[names.index("t017")][4] / power[names.index("t008")][4] - 1)*100:+.1f}%', #t017
              f'{(power[names.index("t012")][4] / power[names.index("t008")][4] - 1)*100:+.1f}%', #t012
              f'{(power[names.index("t009")][4] / power[names.index("t008")][4] - 1)*100:+.1f}%' #t009
              ]
    
    for i in range(len(x)):
        plt.text(i, y[i], labels[i], ha="center", va="bottom")
    
    plt.savefig("plots/upstream.png")
    plt.close()
    
    # Turbine 2
    y = [i[5] for i in subset]
    plt.bar(x,y, color=colors)
    plt.title("Downstream Turbine Aerodynamic Power (MW)")
    plt.ylim([0.5,2])
    plt.legend(legend_lines, ['neutral', 'unstable'])
    
    labels = ['', #t006
              f'{(power[names.index("t007")][5] / power[names.index("t006")][5] - 1)*100:+.1f}%', #t007
              '', #t008
              f'{(power[names.index("t017")][5] / power[names.index("t008")][5] - 1)*100:+.1f}%', #t017
              f'{(power[names.index("t012")][5] / power[names.index("t008")][5] - 1)*100:+.1f}%', #t012
              f'{(power[names.index("t009")][5] / power[names.index("t008")][5] - 1)*100:+.1f}%' #t009
              ]
    
    for i in range(len(x)):
        plt.text(i, y[i], labels[i], ha="center", va="bottom")
    
    plt.savefig("plots/downstream.png")
    plt.close()
    
    # Total
    
    totalpower = [i[4] + i[5] for i in power]
    y = [i[4] + i[5] for i in subset]
    plt.bar(x,y, color=colors)
    plt.title("Total Turbine Aerodynamic Power (MW)")
    plt.ylim([2.0,3.5])
    plt.legend(legend_lines, ['neutral', 'unstable'])#, loc="upper center")
    
    labels = ['', #t006
              f'{(totalpower[names.index("t007")] / totalpower[names.index("t006")] - 1)*100:+.1f}%', #t007
              '', #t008
              f'{(totalpower[names.index("t017")] / totalpower[names.index("t008")] - 1)*100:+.1f}%', #t017
              f'{(totalpower[names.index("t012")] / totalpower[names.index("t008")] - 1)*100:+.1f}%', #t012
              f'{(totalpower[names.index("t009")] / totalpower[names.index("t008")] - 1)*100:+.1f}%' #t009
              ]
    
    for i in range(len(x)):
        plt.text(i, y[i], labels[i], ha="center", va="bottom")
    
    plt.savefig("plots/total.png")
    plt.close()
    

if __name__ == "__main__":
    main()
    