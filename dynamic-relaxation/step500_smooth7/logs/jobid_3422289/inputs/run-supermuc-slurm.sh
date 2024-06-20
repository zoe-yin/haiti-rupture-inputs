#!/bin/bash

# Job Name and Files (also --job-name)
#SBATCH -J dynamic-relaxation

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

echo 'num_nodes:' $SLURM_JOB_NUM_NODES 'ntasks:' $SLURM_NTASKS 'cpus_per_task:' $SLURM_CPUS_PER_TASK >& job.log
ulimit -Ss 2097152

# Run SeisSol
SEISSOL=/dss/dsshome1/01/di35poq/SeisSol/build-release/SeisSol_Release_dskx_4_elastic
PARAMETERS=parameters.par
srun $SEISSOL $PARAMETERS

# generate a log directory and copy inputs to it
./generate-job-log.sh $SLURM_JOB_ID $PARAMETERS


## Post processing jobs
OUTDIR='/hppfs/scratch/01/di35poq/haiti-rupture-outputs/dynamic-relaxation-outputs'
pushd ${OUTDIR}/outputs_tmp 
seissol_output_extractor output-fault.xdmf --time "i1::2" --variable ASl Ts0 Td0 --add2prefix "_extracted"
extractDataFromUnstructuredOutput.py --Data sigma_xx sigma_yy sigma_zz sigma_xy sigma_xz sigma_yz --time 20 output.xdmf
interpolate_seissol_data_to_grid.py --box "100 600000 700000 2020000 2060000 -40000 0" output_resampled.xdmf --Data sigma_xx sigma_yy sigma_zz sigma_xy sigma_xz sigma_yz --gaussian_smoothing
popd

# move outputs to a job-id-named folder
mv ${OUTDIR}/outputs_tmp ${OUTDIR}/jobid_${SLURM_JOB_ID}