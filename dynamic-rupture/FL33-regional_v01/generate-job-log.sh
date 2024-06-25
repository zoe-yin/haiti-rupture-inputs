#!/bin/bash

## Example usage: 
# ./generate-job-log.sh 3409365 parameters_kin_lowres_step500-smooth7_volumetric.par run-supermuc_kin-model_step500-smooth7_lowres_volumetric-test.sh

# >> appends to existing file
# echo "This is a test" > test-output.txt
# $1 will give the jobID as a string (i.e. 3409365)
# $2 will give the name of the parameter file (i.e. parameters_kin_lowres_step500-smooth7_volumetric.par)
# $3 will give the name of the .sh slurm script that called invoked this script (i.e. run-supermuc_kin-model_step500-smooth7_lowres_volumetric-test.sh)

# I can test this script by running ./generate-job-log.sh 3409365

# Pull variables from parameter file: 
# grep MeshFile* ${2}
# Returns: MeshFile = '../../mesh/Haiti_v05_lowres'

# -p flag makes the directory if doesn't already exist and any preceding directories
mkdir -p logs/jobid_${1}/inputs

# # test to see how slurm.sh script name is being passed 
# echo ${3} > logs/jobid_${1}/inputs/test.txt

# Copy slurm run .sh files
cp -r *.yaml logs/jobid_${1}/inputs/ 
cp -r ${2} logs/jobid_${1}/inputs/ 
cp run-supermuc-slurm.sh logs/jobid_${1}/inputs/ 
mv *${1}*.err *${1}*.out logs/jobid_${1}/


# echo "This should give the name of the script: " ${0##*/}

# echo $1 >> test-output.txt
# echo "The last line should be the jobID" >> test-output.txt