#!/bin/python3

import os
from pathlib import Path

import numpy as np

THETA = 30
theta = np.radians(30)

for case in ["p105"]:
    times = os.listdir(Path(case,"postProcessing/SourceHistory"))
    times.sort(key=lambda x: float(x))
    
    data_x = []
    data_y = []
    
    for time in times:
        with open(Path(case,"postProcessing/SourceHistory",time,"SourceUXHistory")) as file:
            data_x.extend(file.readlines())
            
        with open(Path(case,"postProcessing/SourceHistory",time,"SourceUYHistory")) as file:
            data_y.extend(file.readlines())
            
    data_x = [i.split() for i in data_x]
    data_y = [i.split() for i in data_y]
    
    finished = False
    while not finished:
        for i, val in enumerate(data_x):
            try:
                _ = float(val[0])
            except ValueError:
                data_x.pop(i)
                break
            
        if i == len(data_x)-1:
            finished = True
            
    finished = False
    while not finished:
        for i, val in enumerate(data_y):
            try:
                _ = float(val[0])
            except ValueError:
                data_y.pop(i)
                break
            
        if i == len(data_y)-1:
            finished = True

    data_x = np.array(data_x, dtype="float")
    data_y = np.array(data_y, dtype="float")
    
    source_x = np.average(data_x[:,2], weights=data_x[:,1])
    source_y = np.average(data_y[:,2], weights=data_y[:,1])
    
    trans_x = data_x[:,2]*np.cos(theta) + data_y[:,2]*np.sin(theta)
    trans_y = data_y[:,2]*np.cos(theta) - data_x[:,2]*np.sin(theta)
    
    source_tx = np.average(trans_x, weights=data_x[:,1])
    source_ty = np.average(trans_y, weights=data_y[:,1])
    
    print(f'Summary for case, {case}')
    print(f'\tAverage x source = {source_x}')
    print(f'\tAverage y source = {source_y}')
    print(f'\tAverage x source (transformed) = {source_tx}')
    print(f'\tAverage y source (transformed) = {source_ty}')
    print('\n')
