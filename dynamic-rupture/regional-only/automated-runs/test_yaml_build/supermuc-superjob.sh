#!/bin/bash

# Loop through all directories in the current directory that start with "job_*"
for dir in job_*/; do
    echo "Working on dir: ${dir}" 
    # Check if the directory exists
    if [ -d "$dir" ]; then
        # Change to the directory
        pushd "$dir"
        # Run the sbatch command
        sbatch run-supermuc-slurm.sh
        # Return to the previous directory
        popd
    fi
done
