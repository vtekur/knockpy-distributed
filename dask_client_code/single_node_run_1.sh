#!/bin/bash -x
#SBATCH -J dask_worker       # A single job name for the array
#SBATCH -n 1                # Number of cores (-n)
#SBATCH -N 1                # Ensure that all cores are on one Node (-N)
#SBATCH -t 0-06:00          # Runtime in D-HH:MM, minimum of 10 minutes
#SBATCH -p shared           # Partition to submit to
#SBATCH --mem=25G            # Memory pool for all cores (see also --mem-per-cpu)
#SBATCH -o logs/generate_data_%j.out  # File to which STDOUT will be written, %j inserts jobid
#SBATCH -e logs/generate_data_%j.err  # File to which STDERR will be written, %j inserts jobid
module load Anaconda3/2020.11
source activate cs260r
python evaluate_dask.py --cores 1 --index $1 --run $2 --mat_size 20000

