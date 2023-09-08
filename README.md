# sowfatools

################################################################################

This package (not yet published) contains a miscellaneous assortment of
postprocessing functionality for use with CFD simulations peformed in NREL's
SOWFA code. It's FAR from complete!

I'm writing it for my own use primarily, so it's very specialised to my
simulation cases. But maybe if your're working on a similar case you'll find
something useful here. Then again, maybe not!

It would be great to produce a standardised set of postprocessing scripts and
functions so that reulsts from these cases can be quickly compared with other
published studies. But I think that is a bit fanciful right now. If you do
happen to stumble on this and want to contribute, crack ahead.

################################################################################

PYTHON

Here's how you can set up the same python environment as me:

I'm using conda 22.9.0. If you're using a HPC cluster, you may have restrictive
file quotas in your home directory. In this case you'll need to set your package
and environment paths to somewhere else (becuase they end up having a LOT of
files!)

You may need to run "conda init" the first time your using it.

To get paraview, you'll need the conda-forge channel to your condarc file with
the command

conda config --add channels conda-forge

Then you can create an evironment (I call mine sowfapy) with python 3.11 and
the neccesary packages like this:

conda create -n sowfapy python=3.11 numpy scipy matplotlib sympy paraview

You can activate the environment with

conda activate sowfapy

################################################################################

PARAVIEW

Getting paraview (pvbatch) working in parallel sucessfully is another kettle of
fish. But downloading the precompiled binaries and using the mpi binary
included with that seems to work (with some limitations).

On my system, I submit a SLURM job script with the following command:

if [ -f $1 ]; then
    ~/OpenFOAM/ParaView-5.11.1/bin/mpiexec -n 16 ~/OpenFOAM/ParaView-5.11.1/bin/pvbatch "$@" 2>&1
fi

Submit the script with the python filename as the first argument. All other
arguments will then be passed to the script.

Good luck!

################################################################################
