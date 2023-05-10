#!/bin/python3

import sys 
from pathlib import Path
import logging

import numpy as np
import matplotlib.pyplot as plt
from pyTST import pyTST as tst

logger = logging.getLogger(__name__)
ANALYSIS_DIR = "dataAnalysis"

###############################################################################

def concatenate_files(parent_directory: Path, filename: str) -> list[str]:
    """Concatenates files with the same filename across all subdirectories
    within the parent_directory, sorted by the numerical value of the
    subdirectory name.
    """

    logger.debug(f'Concatenating {filename} files across directories in '
                 f'{parent_directory}')

    child_directories = []
    for subdirectory in parent_directory.iterdir():
        try:
           float(subdirectory.name)
        except ValueError:
            logger.warning(f'Skipping subdirectory {subdirectory.name}. '
                           f'Not a numerical value.')
            continue

        child_directories.append(subdirectory)

    child_directories.sort(key=lambda x: float(x))

    concatenated_lines = []
    for child_directory in child_directories:
        with open(parent_directory/child_directory/filename) as file:
            concatenated_lines.extend(file.readlines())

    return concatenated_lines


def read_turbine_output(case_dir: Path, quantity: str) -> np.ndarray:
    """Reads the turbineOutput subdirectory in case_dir and returns concatenated
    time series data for the given quantity as a numpy array.
    """

    logger.debug(f'Reading {qauntity} from turbine data for case {case}')

    lines = concatenate_files(case_dir/"turbineOutput", quantity)

    # flat_data includes all turbines in a flat 2D array
    flat_data = []
    for line in lines:
        if line.startswith(("#", "\n")):
            pass
        else:
            flat_data.append(line.split())

    flat_data = np.array(flat_data, dtype="float")

    # The following code has not been tested. It should separte the data in
    # cases of multiple turbines

    # flat_data is separated into a 2D array for each turbine, and combined
    # into a single 3D array, 3d_data

    # total_rows, total_cols = flat_data.shape
    # total_turbines = np.unique(flat_data[:,0]).size
    # separated_data = np.zeros((total_rows, total_cols, total_turbines))
    # new_row_indices = np.zeros(total_turbines, dtype=int)

    # for old_row_index in range(total_rows):
    #    current_row = flat_data[old_row_index, :]
    #    turbine = int(current_row[0])
    #    separated_data[new_row_indices[turbine], :, turbine] = current_row
    #    new_row_indices[turbine] += 1

    # return separated_data

    return flat_data


def remove_overlaps(data: np.ndarray, sorting_index: int) -> np.ndarray:
    """Takes a 2D numpy array, and checks that it is sorted by the
    sorting_index column and looks for overlapping ranges. The former data is
    removed. The Later data is kept.
    """

    logger.debug("Removing overlapping data")

    finished = False
    while not finished:
        for i in range(1, data.shape[1]+1):
            if data[i, sorting_index] > data[i-1, sorting_index]:
                pass
            else:
                diff = data[:i, sorting_index] - data[i, sorting_index]
                diff[diff < 0] = np.inf
                j = np.argmin(diff)
                data = np.delete(data, np.arange(j, i), axis=0)
                break

        if i == data.shape[1]:
            finished = True

    return data


def check_power(case_dir: Path, convergence_dir: Path) -> None:
    logger.info(f'Checking Power Convergence for case {case_dir.name}')

    data = read_turbine_output(case_dir, "powerRotor")

    # Need to modify everything below to handle more than one turbine
    data = remove_overlaps(data, data[:,1])

    average = np.empty_like(data[:,0])
    for i in range(len(average)):
        average[i] = np.average(data[:(i+1),3], weights=data[:(i+1),2])

    logger.info(f'The average power at time {float(data[-1,1]):.2f} s is '
                f'{float(average[-1]/1e6):.5f} MW')

    deviation = (average - average[-1]) / average[-1] * 100

    # Find times at which power is within a given tolerance of the final value
    tolerances = [5, 1]
    for i, tolerance in enumerate(tolerances):
        for j in range(deviation.size):
            if deviation[j] > tolerance:
                continue
            else:
                logger.info(f'The average power is within {tolerance}% at '
                            f'time {float(data[j,1]):.2f} s, '
                            f'{float(average[j]/1e6):.5f} MW')
                break

    with open(str(convergence_dir/"power.txt"), mode='w') as file:
        file.write("Time dt power averagePower deviation%\n")
        for i in range(data.shape[0]):
            for j in range(1, data.shape[1]):
                file.write(f'float({data[i,j]}) ')
            file.write(f'float({average[i]}) float({deviation[i]})\n')

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


def read_probe(case: str, probe: str, quantity: str):
    logger.info(f"Reading {probe} data from {quantity} file")
    lines = concatenate_files(Path(case, "postProcessing", probe), quantity)

    data = []
    for line in lines:
        if line.startswith("#"): pass
        else:
             data.append(line.replace("(","").replace(")","").split())

    data = np.array(data, dtype="float")

    return data


def main(_, case=None):
    """
    Script accepts up to 1 argument, the name of the case directory (a sub-
    directory in the current working direcctory) to be processed.
    Otherwise the current working directory is presumed to be the case
    directory.
    """

    logging.basicConfig()
    logger.setLevel(level=logging.DEBUG)

    case_dir = Path.cwd()
    if case != None:
        case_dir = case_dir/case
        if not case_dir.exists():
            raise FileNotFoundError
        elif not case_dir.is_dir():
            raise NotADirectoryError

    convergence_dir = case_dir/CONVERGENCE_DIR
    try:
        convergence_dir.mkdir
    except FileExistsError:
        if not convergence_dir.is_dir():
            raise NotADirectoryError
        else:
            pass

    check_power(case_dir, convergence_dir)
 

if __name__ == "__main__":
    main(*sys.argv)

