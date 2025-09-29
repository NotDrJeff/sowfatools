#!/bin/python3

import pdb

import os
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

CASES = ["t101", "t103", "t105", "t106"]
LABELS = ["SmagorinskyABL, Medium (t101)", "OneEqEddyABL, Medium (t103)", "SmagorinskyABL, Coarse (t105)", "OneEqEddy, Coarse (t106)"]
PROBES = 6

def concatenate_files(parent_directory, filename):

    directories = os.listdir(parent_directory)

    concatenated_lines = []

    for directory in directories:
        with open(Path(parent_directory, directory, filename)) as file:
            concatenated_lines.extend(file.readlines())

    return concatenated_lines


def process_probe_data(case, probe_filename, quantity):
    lines = concatenate_files(Path(case, "postProcessing", probe_filename), quantity)

    data = []
    for line in lines:
        if line.startswith("#"): pass
        else:
             data.append(line.replace("(","").replace(")","").split())

    data = np.array(data, dtype="float")

    return data


def calculate_spectra(data):
    spectra = np.array([np.fft.rfft(data[:,i]) for i in range(1, data.shape[1])])
    spectra = np.abs(spectra) / data.shape[0]
    spectra = spectra.T

    if data.shape[0] % 2 == 0:
        spectra = spectra * 2
    else:
        spectra[0:-1] = spectra[0:-1] * 2

    dt = data[1,0] - data[0,0]
    freq = np.fft.rfftfreq(data.shape[0], dt)

    return spectra, freq


def main():
    plt.ioff()
    fig, axs = plt.subplots(2,PROBES, sharex=True, sharey=False)
    pdb.set_trace()
    plt.setp(axs, yscale="log")

    x = np.arange(0,3,2)
    for i in range(PROBES):
        for j in range(2):
            for k in range(6,12):
                axs[j,i].plot(x, np.exp(-5/3 * x - k), label="_nolegend_", color="gray", linestyle="dashed")

    for case in CASES:
        data = process_probe_data(case, "probe1", "U")
        pdb.set_trace()
        spectra, freq = calculate_spectra(data)
        for (i,j), value in np.ndenumerate(spectra):
            spectra[i,j] = 0.5 * 4 * np.pi * freq[i]**2 * spectra[i,j]**2

        for i in range(PROBES):
            for j in range(2):
                axs[j, i].plot(freq[1:], spectra[1:, (i*3)+j])

    fig.legend(labels=LABELS)

    plt.savefig("plots/velocitySpectraRaw.png")

if __name__ == "__main__":
    main()
