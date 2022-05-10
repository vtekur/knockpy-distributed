#!/bin/bash
#SBATCH -n 8                # Number of cores (-n)
#SBATCH -N 1                # Ensure that all cores are on one Node (-N)
#SBATCH -t 0-00:30          # Runtime in D-HH:MM, minimum of 10 minutes
#SBATCH -p shared           # Partition to submit to
#SBATCH --mem=5G            # Memory pool for all cores (see also --mem-per-cpu)
#SBATCH -o generate_data_%j.out  # File to which STDOUT will be written, %j inserts jobid
#SBATCH -e generate_datas_%j.err  # File to which STDERR will be written, %j inserts jobid
module load Anaconda3/2020.11
source activate cs260r
python run_gaussian.py