#!/bin/bash


## Inputs:
# ./generate-job-log.sh $SLURM_JOB_ID $PARAMETERS
## Example usage: 
# ./generate-job-log.sh 3409365 parameters_kin_lowres_step500-smooth7_volumetric.par

# I can test this script by running ./generate-job-log.sh 3409365

# -p flag makes the directory if doesn't already exist and any preceding directories
mkdir -p logs/jobid_${1}/inputs

# Copy slurm run .sh files
cp -r *.yaml logs/jobid_${1}/inputs/ 
cp -r ${2} logs/jobid_${1}/inputs/ 
cp run-supermuc-slurm.sh logs/jobid_${1}/inputs/ 
mv *${1}*.err *${1}*.out logs/jobid_${1}/

