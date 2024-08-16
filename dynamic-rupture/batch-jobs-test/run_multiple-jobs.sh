#!/bin/bash

# List of parameter values to iterate over
MU_S_VALUES=("value1" "value2" "value3")  # Add more values as needed
MU_D_VALUES=("value1" "value2" "value3")  # Add more values as needed
D_C_VALUES=("value1" "value2" "value3")  # Add more values as needed
R_CRITA_VALUES=("value1" "value2" "value3")  # Add more values as needed

# Loop over the parameter values
for PARAM_VALUE in "${PARAMETER_VALUES[@]}"; do

    # Create a new directory for this run
    RUN_DIR="${BASE_DIR}/run_${PARAM_VALUE}"
    mkdir -p "$RUN_DIR"

    # Copy all parameter files to the new directory
    cp ${PARAM_FILES_DIR}/* "$RUN_DIR/"

    # Modify the parameter file with the current parameter value
    sed -i "s/parameter_name=.*/parameter_name=${PARAM_VALUE}/" "${RUN_DIR}/parameter_file.par"

    # (Optional) Modify other files as needed
    # sed -i "s/another_parameter=.*/another_parameter=${PARAM_VALUE}/" "${RUN_DIR}/another_file.par"

    # Submit the job with sbatch from the new directory
    (cd "$RUN_DIR" && sbatch /path/to/run-supermuc-slurm.sh)

    # Wait a few seconds to avoid overwhelming the scheduler (optional)
    sleep 5

done