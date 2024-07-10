#!/bin/bash

JOBID='000000'
OUTPUTFILE="/hppfs/scratch/01/di35poq/haiti-rupture-outputs/dynamic-rupture-outputs/jobid_${JOBID}"
# OUTPUTFILE='testobesto/'

# sed "s/\$OUTPUTFILE/$OUTPUTFILE/" parameters-template.par > parameters.par  # -e "s/\$USER/$USER/"

# sed "s/OUTPUTFILE/${OUTPUTFILE}/" test-input.par > test-output.par

sed "s|OUTPUTFILE|${OUTPUTFILE}/output|" parameters-template.par > parameters_${JOBID}.par