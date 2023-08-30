#!/bin/python3

"""Written for python 3.11
This module contains general utility functions for sowfatools.

Created by Jeffrey Johnston, Dec. 2021
"""

import sys
import shutil
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

###############################################################################


def configure_logging(filename='log', level=logging.INFO) -> None:
    """Configures a logger which outputs at a given 'level' and
    above to both the console and a file called 'filename'.
    """
    
    file_handler = logging.FileHandler(filename, mode='w')
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    file_formatter = logging.Formatter(datefmt="%d/%m/%Y %H:%M:%S",
                                       fmt='%(levelname)-8s %(asctime)s '
                                           '%(name)-20s - %(message)s')
    stream_formatter = logging.Formatter(fmt='%(levelname)-8s %(name)-20s - '
                                             '%(message)s')
    file_handler.setFormatter(file_formatter)
    stream_handler.setFormatter(stream_formatter)
    logging.basicConfig(handlers=(file_handler, stream_handler),
                        level=level)
    
    logger.debug("Logging configured")


def create_directory(directory: Path, exist_ok=True):
    """Creates a directory with parents. If 'exist_ok' is False, then the user
    is prompted to confirm overwrite if thye directory already exists
    """
    
    logger.debug(f'Creating directory {directory}')
    
    try:
        Path.mkdir(directory, parents=True, exist_ok=exist_ok)
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