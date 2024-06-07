#!/bin/bash

# Script runs after seissol main run


# extracts PSR, Vr and partition, at 2nd and 4th time steps and at simulation time 0.5, from test-fault.xdmf and write into test_new-fault.xdmf
# use seissol_output_extractor --h for additionnal info about the arguments
# seissol_output_extractor test-fault.xdmf --time "i2,i4,0.5" --variable PSR Vr partition --add2prefix "_new"

# set runname to the directory name and make an equivalent directory in the outputs directory
runname=$(basename $PWD)
mkdir $OUTPUTS/$runname


# seissol_output_extractor output-fault.xdmf --variable ASI Sld Sls T_d T_s --add2prefix "_extracted"

mv /hppfs/work/pn49ha/di35poq/dynamic-relaxation-outputs/tmp-outputs/ $OUTPUTS/dynamic-relaxation-outputs/$runname

mv $OUTPUTS/dynamic-relaxation-outputs/tmp-outputs $OUTPUTS/dynamic-relaxation-outputs/$runname