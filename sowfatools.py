#!/bin/python3
"""Written for python 3.11
This module contains functions that can be used to read, process and plot
data from SOWFA precursor and turbine simulations. This includes tools
for time histories, time-averaged profiles, turbulence spectra, line-
samples and various stand-alone quantities.

Created by Jeffrey Johnston, Dec. 2021
"""

from pathlib import Path
import logging

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from pyTST import pyTST as tst

import utils

logger = logging.getLogger(__name__)

###############################################################################

def read_turbine_output(case_dir: Path, quantity: str) -> np.ndarray:
    """Reads the turbineOutput subdirectory in case_dir and returns concatenated
    time series data for the given quantity as a numpy array.
    """

    logger.debug(f'Reading {quantity} from turbine data for case {case_dir.name}')

    lines = utils.concatenate_files(case_dir/"turbineOutput", quantity)
    
    logger.debug('Filtering and converting to array')
    
    flat_data = []
    for line in lines:
        if line.startswith(("#", "\n")):
            pass
        else:
            flat_data.append(line.split())

    flat_data = np.array(flat_data, dtype="float")

    return flat_data


def check_power(case_dir: Path, convergence_dir: Path) -> None:
    logger.info(f'Checking Power Convergence for case {case_dir.name}')

    data = read_turbine_output(case_dir, "powerRotor")

    # Need to modify everything below to handle more than one turbine
    data = utils.remove_overlaps(data, data[:,1])

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
    lines = utils.concatenate_files(Path(case, "postProcessing", probe), quantity)

    data = []
    for line in lines:
        if line.startswith("#"): pass
        else:
             data.append(line.replace("(","").replace(")","").split())

    data = np.array(data, dtype="float")

    return data


def read_time_directories(base_directory):
    """Read 'base_directory' and return lists of quantities and time
    folders.
    """
    
    logger.info(f'Reading {base_directory} directory')
    
    # Get a list of all time folders in base_directory
    time_directories = [i.name for i in Path(base_directory).iterdir()]
    time_directories.sort(key=float)
    
    # Get a list of all quantities, even those only appearing in some time
    # folders.
    
    quantity_names = set()
    for time in time_directories:
        for quantity in Path(f'{base_directory}/{time}').iterdir():
            quantity_names.add(quantity.name)
            
    quantity_names = list(quantity_names)
    
    return time_directories, quantity_names


def read_vtk_file(filename, symbol):
    """Reads a VTK v2.0 polydata file containing hexahedral cell data for a
    single vector quantity, 'symbol'. Returns vector components and cell
    centre coordinates.
    """
    
    logger = logging.getLogger(f'{__name__}.read_vtk_file')
    logger.info(f'Reading {filename}')
    
    # Read VTK file and search to find start and end indices for each
    # section.
    # 'points' - Contains x, y, z coordinates for each mesh point
    # 'polygons' - Contains indices of points which make up a cell.  The
    #     first number is the number of points
    # 'vectors' - contains x,y,z components of vector at cell centers.
    
    with open(filename) as file:
        surface = file.readlines()
    
    for i, line in enumerate(surface):
        if line.startswith('POINTS'):
            points_start = i + 1
        elif line.startswith('POLYGONS'):
            points_end = i - 2
            polygons_start = i + 1
        elif line.startswith(symbol):
            polygons_end = i - 3
            vectors_start = i + 1
    
    points = surface[points_start:points_end + 1]
    polygons = surface[polygons_start:polygons_end + 1]
    vectors = surface[vectors_start:len(surface)]
    
    points = [i.split() for i in points]
    points = [[float(j) for j in i] for i in points]
    points = np.array(points)
    
    polygons = [i.split() for i in polygons]
    polygons = [[int(j) for j in i] for i in polygons]
    polygons = [i[1:len(i)] for i in polygons]
    polygons = np.array(polygons)
    
    vectors = [i.split() for i in vectors]
    vectors = [[float(j) for j in i] for i in vectors]
    vectors = np.array(vectors)
    
    # For each cell in 'polygons', obtain the indices of the cell
    # vertices; use those indices to obtain vertex coordinates;
    # then calculate the coordinates of the cell centers.
    
    cell_centres = []
    for i, polygon in enumerate(polygons):
        cell = np.array([points[j, :] for j in polygon])
        centre = np.mean(cell, axis=0)
        cell_centres.append(centre)
    cell_centres = np.array(cell_centres)
    
    return cell_centres, vectors


# def get_heights_to_plot(base_directory, time_directories, height_domain,
#                         height_bottom_inversion,
#                         height_top_inversion, hub_height, rotor_diameter):
#     """Read heights and use rotor, domain and capping inversion heights
#     to select suitable heights for plotting.
#     """
    
#     logger = logging.getLogger(f'{__name__}.get_heights_to_plot')
#     """logger.info('Reading sampled heights')
    
#     # Get a list of all heights at which averages were taken.  Heights
#     # are taken from first time folder.
    
#     with open(f'{base_directory}/{time_directories[0]}/hLevelsCell') \
#             as hLevelsCell:
#         heights = hLevelsCell.read().split()
#     heights = np.array([int(i) for i in heights])"""
    
#     logger.info('Choosing heights for plotting')
    
#     # Search heights for closest matches to rotor-bottom, hub and
#     # rotor-top heights and store indices in 'rotor_height_idx'.
    
#     rotor_bottom_height = hub_height - rotor_diameter / 2
#     rotor_top_height = hub_height + rotor_diameter / 2
    
#     rotor_height_idx = [0, 0, 0]
#     rotor_height_idx[0] = np.argmin(np.abs(heights - rotor_bottom_height))
#     rotor_height_idx[1] = np.argmin(np.abs(heights - hub_height))
#     rotor_height_idx[2] = np.argmin(np.abs(heights - rotor_top_height))

#     logger.info(f'Actual heights of rotor-bottom, hub-centre and rotor-'
#                 f'top are: {rotor_bottom_height}m, {hub_height}m, and '
#                 f'{rotor_top_height}m')
    
#     logger.info(f'Closest match for rotor-bottom, hub-centre and '
#                 f'rotor-top heights are: {heights[rotor_height_idx[0]]}m, '
#                 f'{heights[rotor_height_idx[1]]}m, and '
#                 f'{heights[rotor_height_idx[2]]}m.')
    
#     # Time series will be plotted on three plots for each quantity.  One
#     # for heights below the capping inversion; one for heights in the
#     # inversion; and one for heights above it.
    
#     # Heights for first plot
    
#     """if rotor_height_idx[0] > 1:
#         heights_idx1 = [1] + rotor_height_idx
#     else:
#         heights_idx1 = list(rotor_height_idx)
        
#     interval = (height_bottom_inversion - heights[rotor_height_idx[-1]]) / 4
#     for i in range(3, 0, -1):
#         difference = heights - (height_bottom_inversion - interval * i)
#         heights_idx1.append(int(np.argmin(np.abs(difference))))
#     heights_to_plot = [str(heights[i]) for i in heights_idx1]
    
#     logger.info(f'Heights below capping inversion to be plotted are:'
#                 f' {"m ".join(heights_to_plot)}m')
    
#     # Heights for second plot
    
#     heights_idx2 = []
#     interval = (height_top_inversion - height_bottom_inversion) / 2
#     for i in range(2, -1, -1):
#         difference = heights - (height_top_inversion - interval * i)
#         heights_idx2.append(int(np.argmin(np.abs(difference))))
#     heights_to_plot = [str(heights[i]) for i in heights_idx2]
    
#     logger.info(f'Heights within capping inversion to be plotted are:'
#                 f' {"m ".join(heights_to_plot)}m')
    
#     # Heights for third plot
    
#     heights_idx3 = []
#     interval = (height_domain - height_top_inversion) / 4
#     for i in range(3, -1, -1):
#         difference = heights - (height_domain - interval * i)
#         heights_idx3.append(int(np.argmin(np.abs(difference))))
#     heights_to_plot = [str(heights[i]) for i in heights_idx3]
    
#     logger.info(f'Heights below capping inversion to be plotted are:'
#                 f' {"m ".join(heights_to_plot)}m')"""
    
#     # return heights, heights_idx1, heights_idx2, heights_idx3,
#     # rotor_height_idx
    
#     return rotor_height_idx


def read_averaging_files(base_directory, time_histories_directory,
                         time_directories, quantity, heights):
    """Read averaging files for a quantity. Format and return as numpy
    arrays.
    """
    
    logger = logging.getLogger(f'{__name__}.read_averaging_files')
    logger.info(f'Reading Files for {quantity}')
    
    # Loop through each time directory in averaging and combine data from
    # quantity files into a list, 'data'.  Each element of data is an
    # entire line from the averaging files, containing data at a given
    # time for various heights.
    
    data = []
    for time in time_directories:
        try:
            with open(f'{base_directory}/{time}/{quantity}') as \
                    quantity_read_file:
                data.extend(quantity_read_file.readlines())
        except FileNotFoundError:
            logger.warning(f'File {base_directory}/{time}/{quantity} not'
                           f' found, skipping.')
    
    # Each element in date is split into a list. The sub-elements of data are
    # converted to floats and the elements of data are sorted by time (in
    # case of simulation re-runs causing overlaps).
    
    data = [i.split() for i in data]
    data = [[float(j) for j in i] for i in data]
    data.sort(key=lambda x: x[0])
    
    # Write combined data to new file
    
    logger.info(f'Writing {quantity} to new file {time_histories_directory}/'
                f'{quantity}_time_history')
    
    with open(f'{time_histories_directory}/{quantity}_time_history',
              mode='w') as quantity_write_file:
        quantity_write_file.write(f'time time-step '
                                  f'{" ".join(str(i) for i in heights)}')
        quantity_write_file.write('\n')
        for i in data:
            for j in i:
                quantity_write_file.write(f'{j} ')
            quantity_write_file.write('\n')

    data = np.array(data)
    
    times = data[:, 0]
    
    time_steps = np.diff(times)
    time_steps = np.append(time_steps, data[-1, 1])
    
    data = data[:, 2:]
    
    return data, times, time_steps


def plot_time_history(quantity, data, times, heights, heights_idx1,
                      heights_idx2, heights_idx3, directory):
    """Plots the horizontally averaged quantity against simulation time
    for various heights. Creates three different plots.
    """
    
    logger = logging.getLogger(f'{__name__}.plot_time_history')
    logger.info(f'Plotting time history of {quantity}')
    
    for j in range(3):
        plt.ioff()
        fig, ax = plt.subplots()
        if j == 0:
            ax.set_title(f'Time-Series of {quantity} (Below Capping '
                         f'Inversion)')
            filename = "below_inversion"
            heights_idx = heights_idx1
        elif j == 1:
            ax.set_title(f'Time-Series of {quantity} (In Capping '
                         f'Inversion)')
            filename = "in_inversion"
            heights_idx = heights_idx2
        else:
            ax.set_title(f'Time-Series of {quantity} (Above Capping '
                         f'Inversion)')
            filename = "above_inversion"
            heights_idx = heights_idx3
        
        ax.set_xlabel(f'Simulation Time ($s$)')
        ax.set_ylabel(f'{quantity} (Planar Averaged)')
        
        for idx in heights_idx:
            ax.plot(times, data[:, idx])
        
        ax.legend([str(heights[idx]) for idx in heights_idx], loc='best')
        
        plt.savefig(f'{directory}/{quantity}_time_history_{filename}.png')
        plt.close()


def get_data_to_average(times, time_steps, data, user_arguments):
    """For first quantity ('q3_mean') only, extract time data; identify
    start- and end-time indices for profile averaging; and calculate zi
    for normalising heights.
    """
    
    logger = logging.getLogger(f'{__name__}.get_data_to_average')
    logger.info('Extracting averaging times')
    
    # Get start and end times.
    
    try:
        start_time = round(float(user_arguments[1]))
        if start_time < round(times[0]) or start_time > round(times[-1]):
            logger.warning('Start time for profile averaging is out of '
                           'range. Averaging from first time step.')
            start_index = 0
            start_time = round(times[start_index])
        else:
            # Search array for closest match
            start_index = np.argmin(np.abs(times - start_time))
    except IndexError:
        logger.warning('Start time for profile averaging was not given. '
                       'Averaging from first time step.')
        start_index = 0
        start_time = round(times[start_index])
        
    logger.info(f'Using start time {times[start_index]} for profile '
                f'averaging')
    
    try:
        end_time = round(float(user_arguments[2]))
        if end_time < round(times[0]) or end_time > round(times[-1]):
            logger.warning('End time for profile averaging is out of '
                           'range. Averaging to last time step.')
            end_index = len(times) - 1
            end_time = round(times[end_index])
        else:
            # Search array for first element after end time
            end_index = np.argmin(np.abs(times - end_time))
    except IndexError:
        logger.warning('End time for profile averaging was not given. '
                       'Averaging to last time step.')
        end_index = len(times) - 1
        end_time = round(times[end_index])
    
    logger.info(f'Using end time {times[end_index]} for profile '
                f'averaging')
    
    data_to_average = data[start_index:end_index, :]
    times_to_average = times[start_index:end_index]
    time_steps_to_average = time_steps[start_index:end_index]
    
    directory = f'profile_{start_time}_{end_time}'
    
    return times_to_average, time_steps_to_average, data_to_average, directory


def get_time_averages(quantity, data_to_average, time_steps_to_average):
    """Function to calculate time-averages of quantities;
    non-dimensionalise the height; and return quantity.
    """
    
    logger = logging.getLogger(f'{__name__}.get_time_averages')
    logger.info(f'Calculating time-averaged profile for {quantity}')
    
    _, num_cols = data_to_average.shape
    total_time = sum(time_steps_to_average)
    
    time_averages = []
    for i in range(num_cols):
        f_deltat = data_to_average[:, i] * time_steps_to_average
        time_averages.append(sum(f_deltat) / total_time)
        
    return np.array(time_averages)


def get_boundary_layer_height(heights, time_averages):
    """Calculate the boundary layer height, zi, defined as the height at
    which the time-averaged vertical heat flux (q3_mean) is minimum.
    """
    
    logger = logging.getLogger(f'{__name__}.get_boundary_layer_height')
    logger.info("Calculating boundary layer height, zi from q3_mean")
    
    boundary_layer_height = heights[np.argmin(time_averages)]
    
    nondimensional_heights = heights / boundary_layer_height
    
    logger.info(f'Boundary layer height = {boundary_layer_height}m')
    
    return boundary_layer_height, nondimensional_heights


def write_time_averages(directory, quantity, time_averages, heights,
                        nondimensional_heights):
    """Write an array of time-averages to a text file in 'directory' called
    'quantity'_profile.
    """

    logger = logging.getLogger(f'{__name__}.write_time_averages')
    logger.info(f'Writing time averaged profile to new file '
                f'{directory}/{quantity}_profile')

    with open(f'{directory}/{quantity}_profile', mode='w') as \
            quantity_write_file:
        quantity_write_file.write(f'height non-dimensional_height '
                                  f'{quantity}\n')
        for i, value in enumerate(time_averages):
            quantity_write_file.write(f'{str(heights[i])} '
                                      f'{str(nondimensional_heights[i])} '
                                      f'{str(value)}\n')


def plot_profile(quantity, time_averages, nondimensional_heights, directory):
    """Function to plot time-averaged profiles"""
    
    logger = logging.getLogger(f'{__name__}.plot_profile')
    logger.info(f'Plotting profile for {quantity}')
    
    plt.ioff()
    fig, ax = plt.subplots()
    
    ax.set_title(f'Horizontally- and Time-Averaged Profile of {quantity}')
    ax.set_ylabel('Height/$z_i$')
    ax.set_xlabel(quantity)
    
    if quantity == 'Streamwise Velocity':
        ax.set(ylim=[0.0, 1.0])
        ax.set(xlim=[0.0, 2.0])
        
    ax.plot(time_averages, nondimensional_heights)
    
    plt.savefig(f'{directory}/{quantity}_profile.png')
    plt.close()


def plot_field(x, y, field, directory, filename, title='', x_y_label='',
               z_label=''):
    """Plots 2D velocity field as surface"""
    
    logger = logging.getLogger(f'{__name__}.plot_field')
    logger.info(f'Plotting velocity field to {filename}')
    
    plt.ioff()
    plt.figure(figsize=(10, 10))
    ax = plt.axes(projection='3d')
    
    ax.set_title(title)
    ax.set_xlabel(x_y_label)
    ax.set_ylabel(x_y_label)
    ax.set_zlabel(z_label)
    
    ax.plot_surface(x, y, field, linewidth=0, cmap=cm.seismic)
    
    plt.savefig(f'{directory}/{filename}.png')
    plt.close()


def write_spectra(directory, filename, wavenumbers, intensities):
    """Write wavenumbers and spectra intensities to a file in 'directory'
    called 'filename'
    """
    
    logger = logging.getLogger(f'{__name__}.write_spectra')
    logger.info(f'Writing {directory}/{filename}')
    
    with open(f'{directory}/{filename}', mode='w') as \
            quantity_write_file:
        quantity_write_file.write(f'wavenumber intensity\n')
        for i, value in enumerate(intensities):
            quantity_write_file.write(f'{str(wavenumbers[i])} '
                                      f'{str(intensities)}\n')


def plot_spectra(directory, filename, unique_wavenumbers,
                 rounded_wavenumbers, raw_spectra, averaged_spectra, title=''):
    """Plot raw and averaged spectra.  Also plots a straight line
    representing the inertial range
    """
    
    logger = logging.getLogger(f'{__name__}.plot_spectra')
    logger.info('Plotting ')
    
    plt.ioff()
    fig, ax = plt.subplots()
    plt.yscale('log')
    plt.xscale('log')
    ax.set_title(title)
    ax.set_ylabel("Turbulent Kinetic Energy Intensity ($m^{2}/s^{2}$)")
    ax.set_xlabel("Wavenumber")
    ax.set(ylim=[10 ** -6, 1])
    ax.set(xlim=[10 ** -3, 1])
    
    ax.plot(unique_wavenumbers, raw_spectra)
    ax.plot(rounded_wavenumbers, averaged_spectra)
    ax.plot(rounded_wavenumbers, 10E-6 * rounded_wavenumbers ** (-5 / 3))
    
    plt.savefig(f'{directory}/{filename}')
    plt.close()



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

    convergence_dir = case_dir/'convergence'
    try:
        convergence_dir.mkdir
    except FileExistsError:
        if not convergence_dir.is_dir():
            raise NotADirectoryError
        else:
            pass

    check_power(case_dir, convergence_dir)