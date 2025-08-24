#!/bin/bash

# Get first log file and convert to absolute path
FIRST_FILE=$(ls $1 | head -1)
ABS_PATH=$(realpath "$FIRST_FILE")

# Extract directory name and create output directory
DIR=$(basename $(dirname "$ABS_PATH"))
LOG_DIR=$(dirname "$ABS_PATH")
OUTPUT_DIR="$LOG_DIR/sowfatools/logs"

echo "DIR = '$DIR'"
echo "Output directory = '$OUTPUT_DIR'"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Example lines
# uStarMean = 0.324725410973      LMean = -65.4456959029  phiMMean = 0.843234503782       Avg iterations = 0
# UParallelMeanMag = 6.57649536267        UParallelPMeanMag = 6.61557209505
# RwMagMean = 0.106073143308      RwMeanMag = 0.105446592531      sqrt(RwMagMean) = 0.325688721493        sqrt(RwMeanMag) = 0.324725410973        uStarMean = 0.324725410973

awk -v prefix="$DIR" -v outdir="$OUTPUT_DIR" '

BEGIN {
    print "Time\tdeltaT\tmean\tmax" > outdir "/" prefix "_courant.tsv"
    print "Time\tdeltaT\tuStarMean" > outdir "/" prefix "_uStarMean.tsv"
    print "Time\tdeltaT\tLMean"     > outdir "/" prefix "_LMean.tsv"
    print "Time\tdeltaT\tphiMMean"  > outdir "/" prefix "_phiMMean.tsv"
}

/^Time = / { time = $3 }
/^deltaT = / { deltaT = $3 }
/^Courant Number mean:/ { courant_mean = $4; courant_max = $6 }
/^uStarMean = / { ustar = $3; lmean = $6; phim_mean = $9}

# /^UParallelMeanMag = / { uparallel = $3 }
# /^RwMagMean = / { rwmag = $3 }

/^ExecutionTime/ { 
    print time "\t" deltaT "\t" courant_mean "\t" courant_max   > outdir "/" prefix "_courant.tsv"
    print time "\t" deltaT "\t" ustar                           > outdir "/" prefix "_uStarMean.tsv"
    print time "\t" deltaT "\t" lmean                           > outdir "/" prefix "_LMean.tsv"
    print time "\t" deltaT "\t" phim_mean                       > outdir "/" prefix "_phiMMean.tsv"
    # print time "\t" deltaT "\t" uparallel                     > outdir "/" prefix "_UParallelMeanMag.tsv"
    # print time "\t" deltaT "\t" rwmag                         > outdir "/" prefix "_RwMagMean.tsv"
}

' $(ls $1 | sort -V)
