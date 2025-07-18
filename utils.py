"""Compatible with Python 3.13, SOWFA 2.4.x
Part of github.com/NotDrJeff/sowfatools
Jeffrey Johnston   jeffrey.johnston@qub.ac.uk  July 2025

This module contains general utility functions
"""

import sys
import shutil
from pathlib import Path
import logging

import numpy as np

logger = logging.getLogger(__name__)

################################################################################

def configure_root_logger(level=logging.DEBUG) -> None:
    """Configures the root logger for console output at the desired level and
    above.
    """
    
    # Format the root logger
    logger = logging.getLogger()
    
    stream_formatter = logging.Formatter(fmt='%(levelname)-8s %(name)-20s - '
                                             '%(message)s')
    
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(stream_formatter)

    logger.addHandler(stream_handler)
    logger.setLevel(level)
    
    # Switch to local logger for output
    logger = logging.getLogger(__name__)
    logger.debug(f'__main__ logger configured for console output')

def configure_function_logger(filepath: Path, level=logging.DEBUG) -> None:
    """Configures a logger which outputs at the desired level and above to a
    file. logger name is determined by the name of the module which imported
    this function.
    """
    
    # Format the logger from the calling module/script
    loggername = __name__.split('.')[:-1]
    loggername = '.'.join(loggername)
    
    logger = logging.getLogger(loggername)
    
    file_formatter = logging.Formatter(datefmt="%d/%m/%Y %H:%M:%S",
                                       fmt='%(levelname)-8s %(asctime)s '
                                           '%(name)-20s - %(message)s')
    file_handler = logging.FileHandler(filepath, mode='w')
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(file_handler)
    logger.setLevel(level)
    
    # Switch to local logger for output
    logger = logging.getLogger(__name__)
    if loggername == '':
        loggername = 'Root'
    logger.debug(f'{loggername} logger configured for file {filepath}')


def create_directory(directory: Path, exist_ok=True):
    """Creates a directory with parents. If 'exist_ok' is False, then the user
    is prompted to confirm overwrite if thye directory already exists
    """
    
    try:
        Path.mkdir(directory, parents=True, exist_ok=exist_ok)
        logger.debug(f'Created directory {directory}')
    except FileExistsError:
        overwrite = input(f'Directory {directory} already '
                          f'exists. Overwrite? (y/n): ')
        overwrite = overwrite.lower()
        while overwrite not in ['y', 'yes', 'n', 'no']:
            overwrite = input(f'Enter yes/y or no/n: ')
            overwrite.lower()
        if overwrite in ['y', 'yes']:
            logger.warning(f'Overwriting existing directory {directory}')
            shutil.rmtree(directory)
            Path.mkdir(directory, parents=True, exist_ok=exist_ok)
        else:
            logger.info("Exiting")
            sys.exit()


def concatenate_files(parent_directory: Path, filename: str) -> list[str]:
    """Assumes sub-directories of 'parent_directory' are named numerically.
    The 'filename' file in each sub-directory, if it exists, is read and
    concatenated into a single list, 'concatenated_lines'
    """
    
    logger.debug(f"Concatenating {filename} files across sub-directories in "
                 f"{parent_directory}")
    
    child_directories = []
    for subdirectory in parent_directory.iterdir():
        try:
           float(subdirectory.name)
        except ValueError:
            logger.warning(f'Skipping subdirectory {subdirectory.name}. '
                           f'Not a numerical value.')
            continue

        child_directories.append(subdirectory)
    
    child_directories.sort(key=lambda x: float(x.name))

    concatenated_lines = []
    for child_directory in child_directories:
        with open(child_directory/filename) as file:
            concatenated_lines.extend(file.readlines())

    return concatenated_lines


def remove_overlaps(data: np.ndarray, sorting_index: int) -> np.ndarray:
    """Takes a 2D numpy array, and checks that it is sorted by the
    sorting_index column and looks for overlapping ranges. The former data is
    removed. The Later data is kept.
    """

    logger.debug(f"Searching for overlaps across {data.shape[0]} records")

    finished = False
    start = 1
    while not finished:
        for i in range(start, data.shape[0]):
            if data[i, sorting_index] > data[i-1, sorting_index]:
                pass
            else:
                diff = data[:i, sorting_index] - data[i, sorting_index]
                diff[diff < 0] = np.inf
                j = np.argmin(diff)
                data = np.delete(data, np.arange(j, i), axis=0)
                start = j
                break

        if i == data.shape[0]-1:
            finished = True
            
    logger.debug(f"{data.shape[0]} records remaining")
    return data


def calculate_moving_average(data: np.ndarray, val_index = 0,
                             weight_index = None) -> np.ndarray:
    """Takes a 2D array and creates a moving average over column specified by
    'val_index'. Weights can be specified by 'weight_index'
    """
    logger.debug('Calculating moving average')
    
    average = np.empty_like(data[:,0])
    if weight_index is None:
        average[0] = data[0,val_index]
        for i in range(1,average.shape[0]):
            average[i] = average[i-1] + data[i,val_index]
            
        average = average / np.arange(1,average.shape[0]+1)
    else:
        weight_sum = np.empty_like(data[:,0])
        weight_sum[0] = data[0,weight_index]
        average[0] = data[0,val_index]*data[0,weight_index]
        for i in range(1,average.shape[0]):
            average[i] = (average[i-1]
                          + data[i,val_index]*data[i,weight_index])
            weight_sum[i] = (weight_sum[i-1]
                             + data[i,weight_index])
            
        average = average / weight_sum
        
    return average


def check_tolerance(data: np.ndarray, ref: float, tolerances: tuple) -> list:
    """Compare a list of values with prescribed percentage tolerances.
    Find the point after which the data remains within +/- each tolerance
    of the 'ref' value.
    """
    
    in_tolerance = [False] * len(tolerances)
    in_tolerance_idx = [None] * len(tolerances)
    for i, tol in enumerate(tolerances):
        for j, val in np.ndenumerate(data):
            if (val < ref*(1-tol/100)) or (val > ref*(1+tol/100)):
                if in_tolerance[i] is True:
                    in_tolerance[i] = False
                    in_tolerance_idx[i] = None
            elif in_tolerance[i] is False:
                in_tolerance[i] = True
                in_tolerance_idx[i] = j[0]
                
        if in_tolerance[i] is False:
            logger.warning(f"Data is never within a tolerance of +/- {tol}")
            
    return in_tolerance_idx


def parse_turbineOutput_files(readdir):
    """Reads turbineOutput files from readdir and returns the unique quantity
    names, turbines and blades
    """
    
    files = list(readdir.iterdir())
    
    filenames_parsed = [''] * len(files)
    for i,file in enumerate(files):
        
        filenames_parsed[i] = file.stem.replace('turbine','')
        
        if 'blade' in file.stem:
            filenames_parsed[i] = filenames_parsed[i].replace('blade','')
            
        filenames_parsed[i] = filenames_parsed[i].split('_') # type: ignore
        
        if 'blade' not in file.stem:
            filenames_parsed[i].append('') # type: ignore
            
    filenames_parsed = np.array(filenames_parsed)
    
    quantities = np.unique(filenames_parsed[:,1])
    turbines = np.unique(filenames_parsed[:,2])
    blades = np.unique(filenames_parsed[:,3])
    blades = blades[blades != ''] # Remove empty value
    
    logger.debug(f'Found {len(quantities)} quantities, {len(turbines)} '
                 f'turbines, {len(blades)} blades files in turbineOutput folder')
    logger.debug(f'Found {len(files)} files in turbineOutput folder')
    
    return quantities, turbines, blades


def get_time_idx(data, times_to_report):
    return [np.argmin(np.abs((data[:,0]-time))) for time in times_to_report]

if __name__ == '__main__':
    logger.error('This module is not intended to be run as a script')
