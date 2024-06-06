#!/bin/bash

# Template from SeisSol Page Here: https://seissol.readthedocs.io/en/latest/supermuc.html

# Job Name and Files (also --job-name)
#SBATCH -J <job name>

#Output and error (also --output, --error):
#SBATCH -o ./%j.%x.out
#SBATCH -e ./%j.%x.err

#Initial working directory:
#SBATCH --chdir=<work directory>

#Notification and type
#SBATCH --mail-type=END
#SBATCH --mail-user=<your email address>

#Setup of execution environment
#SBATCH --export=ALL
#SBATCH --account=<project id>
#SBATCH --no-requeue

#Number of nodes and MPI tasks per node:
#SBATCH --partition=general
#SBATCH --nodes=40
#SBATCH --time=03:00:00

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
#Note: Fabian uses I_MPI_SHM_HEAP_VSIZE=8192, SeisSol template uses 32768
export I_MPI_SHM_HEAP_VSIZE=32768

export XDMFWRITER_ALIGNMENT=8388608
export XDMFWRITER_BLOCK_SIZE=8388608
export SC_CHECKPOINT_ALIGNMENT=8388608

export SEISSOL_CHECKPOINT_ALIGNMENT=8388608
export SEISSOL_CHECKPOINT_DIRECT=1
export ASYNC_MODE=THREAD
export ASYNC_BUFFER_ALIGNMENT=8388608
source /etc/profile.d/modules.sh

echo 'num_nodes:' $SLURM_JOB_NUM_NODES 'ntasks:' $SLURM_NTASKS
ulimit -Ss 2097152

# Note: Fabian uses mpiexec but I will use srun based on this advice: 
# https://stackoverflow.com/questions/51300165/any-use-case-for-mpirun-on-slurm-managed-cluster
srun SeisSol_Release_sskx_4_elastic parameters.par

# Fabian example: 
# mpiexec -n $SLURM_NTASKS /hppfs/work/pn49ha/ru64lev2/SeisSol/build-release/SeisSol_Release_dskx_5_elastic parameters_samos_noWL.par