#!/bin/bash

# Job Name and Files (also --job-name)
#SBATCH -J FL33-regional_v01

#Output and error (also --output, --error):
#SBATCH -o ./%j.%x.out
#SBATCH -e ./%j.%x.err

#Initial working directory:
#SBATCH --chdir=./

#Notification and type
#SBATCH --mail-type=BEGIN,END,ARRAY_TASKS,FAIL
#SBATCH --mail-user=hyin@ucsd.edu

#Setup of execution environment
#SBATCH --export=ALL
#SBATCH --account=pn49ha
#SBATCH --no-requeue

#Number of nodes and MPI tasks per node:
#SBATCH --partition=test
#SBATCH --nodes=16
#SBATCH --time=00:30:00

#SBATCH --ntasks-per-node=1
#EAR may impact code performance
#SBATCH --ear=off

module load slurm_setup

#Run the program:
export MP_SINGLE_THREAD=no
unset KMP_AFFINITY
export OMP_NUM_THREADS=94
export OMP_PLACES="cores(47)"
#Prevents errors such as experience in Issue #691
export I_MPI_SHM_HEAP_VSIZE=8192

export XDMFWRITER_ALIGNMENT=8388608
export XDMFWRITER_BLOCK_SIZE=8388608
export SC_CHECKPOINT_ALIGNMENT=8388608

export SEISSOL_CHECKPOINT_ALIGNMENT=8388608
export SEISSOL_CHECKPOINT_DIRECT=1
export ASYNC_MODE=THREAD
export ASYNC_BUFFER_ALIGNMENT=8388608
source /etc/profile.d/modules.sh

echo 'num_nodes:' $SLURM_JOB_NUM_NODES 'ntasks:' $SLURM_NTASKS 'cpus_per_task:' $SLURM_CPUS_PER_TASK
ulimit -Ss 2097152

PARAMETERS='parameters.par'

# Define the OUTPUTDIR path
OUTPUTDIR="/hppfs/scratch/01/di35poq/haiti-rupture-outputs/dynamic-rupture-outputs/test/jobid_${SLURM_JOB_ID}"
# OutputFile='/hppfs/scratch/01/di35poq/haiti-rupture-outputs/dynamic-rupture-outputs/outputs_tmp/output' 

# Use sed to replace the specific line (line 63) in parameters.par that sets outputdir
sed -i "63s|.*|OutputFile='${OUTPUTDIR}/output'|" "$PARAMETERS"
echo "Line 63 replaced with: OutputFile='${OUTPUTDIR}'"

# Run SeisSol
SEISSOL=/dss/dsshome1/01/di35poq/SeisSol/build-release/SeisSol_Release_dskx_4_elastic
srun $SEISSOL $PARAMETERS

# Move to the outputs dir for postprocessing
pushd $OUTPUTDIR

# # Extract timesteps for relevant variables
seissol_output_extractor output-fault.xdmf --time "i1:" --variable ASl Sls Sld Ts0 Td0 Pn0 T_s T_d P_n Mud  --add2prefix "_jobid_${SLURM_JOB_ID}_extracted"
seissol_output_extractor output-surface.xdmf --time "i1:" --variable u1 u2 u3 --add2prefix "_jobid_${SLURM_JOB_ID}_extracted"

popd

# generate a log directory and copy inputs to it
../generate-job-log.sh $SLURM_JOB_ID $PARAMETERS

# Copy log & input files to the outputs directory
cp -r logs/jobid_${SLURM_JOB_ID} ${OUTPUTDIR}/logs

# Create moment rate plot and R-value xdmf
calc-moment-rate_R_supermuc.py ${SLURM_JOB_ID}
