import chunk
import sys
import argparse
from dask.distributed import Client, LocalCluster
import dask.array as da
from time import time
import knockpy as kpy
from knockpy.knockoff_filter import KnockoffFilter

parser = argparse.ArgumentParser(description='Gets desired dask testing properties')
parser.add_argument('index', metavar='i', type=int,
                    help='index into the parameter sweep')
parser.add_argument('--scheduler', type=str, default=None,
                    help='scheduler address')

args = parser.parse_args()
index = args.index
scheduler_add = args.scheduler

# Can re-set these, maybe abstract out to a JSON if we want to
function_types = ["eigh", "dot", "cholesky", "inverse"]
matrix_types = ["random", "gaussian", "sparse", "diagonal"]
chunk_types = [(100,100), (200, 200)] #XXX TODO TODO

# Use index to choose the above types
# (num_matrix * num_chunk) * f + num_chunk * m + c
num_funs, num_mats, num_chus = len(function_types), len(matrix_types), len(chunk_types)
num_combs = num_funs * num_mats * num_chus
index = index % num_combs

chunk_type = chunk_types[index % num_chus]
index = index - (index % num_chus)
matrix_type = matrix_types[(index % (num_mats * num_chus)) //num_chus]
index = index - (index % num_funs) 
function_type = function_types[index // (num_mats * num_chus)]

print(args.index, function_type, matrix_type, chunk_type)

# Now begin the actual code:

if scheduler_add is not None:
    client = Client(scheduler_add)

start = time()

if function_type == "eigh":
    pass


if scheduler_add is not None:
    client.close()


