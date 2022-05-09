#!/bin/bash -x
#SBATCH -J dask_worker # A single job name for the array
#SBATCH -n 1                # Number of tasks
#SBATCH --cpus-per-task 4  # How to allocate CPUs when multithreading
#SBATCH --threads-per-core 1 # minimum number of threads in a core to specify to a job
#SBATCH -N 1                # Ensure that all cores are on one machine
#SBATCH -p shared,serial_requeue
#SBATCH -t 10:00:00         # Runtime in D-HH:MM:SS, minimum of 10 minutes
#SBATCH --mem=4G          # Memory pool for all cores (see also --mem-per-cpu) MBs
#SBATCH -o ../joblogs/%A_%a.out  # File to which STDOUT will be written, %j inserts jobid
#SBATCH -e ../joblogs/%A_%a.err  # File to which STDERR will be written, %j inserts jobid

dask-worker $1 --memory-limit="4 GiB" 
