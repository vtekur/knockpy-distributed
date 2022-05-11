import chunk
import sys
import argparse
from dask.distributed import Client, LocalCluster
import dask.array as da
from time import time
import knockpy as kpy
import logging
from knockpy.knockoff_filter import KnockoffFilter
import numpy as np

parser = argparse.ArgumentParser(description='Gets desired dask testing properties')
parser.add_argument('--index', metavar='i', type=int,
                    help='index into the parameter sweep')
parser.add_argument('--mat_size', type=int,
                    help='matrix size (one dimension, this is a square matrix)')
parser.add_argument('--cores', type=int,
                    help='number of cpu cores') 
parser.add_argument('--run', type=int,
                    help='run number')                         
parser.add_argument('--scheduler', type=str, default=None,
                    help='scheduler address')

def gen_random():
    return da.random.random_sample((MAT_SIZE,MAT_SIZE), chunks=CHUNK)

def gen_sparse():
    M = da.random.random_sample((MAT_SIZE,MAT_SIZE), chunks=CHUNK)
    M[M <= 0.95] = 0
    return M

def test_eigh():
    A = GEN_MAT()
    B, C = da.apply_gufunc(np.linalg.eigh, '(m,m)->(m),(m,m)', A, allow_rechunk=True)
    B.compute()

def test_dot():
    A = GEN_MAT()
    B = GEN_MAT()
    C = da.dot(A,B)
    C.compute()

def test_transpose():
    A = GEN_MAT()
    B = da.transpose(A)
    B.compute()

def test_inv():
    A = GEN_MAT()
    B = da.linalg.inv(A)
    B.compute()


SAVE_FOLDER_NAME = '../dask_single_node_search_2'
mem_types = ['15GB', '6GB', '3GB', '1GB']
function_types = [test_dot, test_inv, test_transpose, test_eigh]
matrix_types = [gen_random, gen_sparse]
chunk_types = ['auto', (1000,1000)]


args = parser.parse_args()

MAT_SIZE = args.mat_size
CORES = args.cores
scheduler_add = args.scheduler
index = args.index - 1
run = args.run

num_mems, num_funs, num_mats, num_chus = len(mem_types), len(function_types), len(matrix_types), len(chunk_types)
num_combs = num_mems * num_funs * num_mats * num_chus
index = index % num_combs
CHUNK = chunk_types[index % num_chus]
index = index - (index % num_chus)
GEN_MAT = matrix_types[(index % (num_mats * num_chus)) //num_chus]
index = index - (index % num_mats) 
test_func = function_types[(index % (num_mats * num_chus * num_funs)) // (num_mats * num_chus)]
index = index - (index % num_funs)
RAM = mem_types[(index // (num_mats * num_chus * num_funs))]
print(args.index, RAM, test_func.__name__, GEN_MAT.__name__, CHUNK, CORES, MAT_SIZE)

if scheduler_add is not None:
    client = Client(scheduler_add,
                    silence_logs=logging.ERROR)
else:
    client = Client(processes=False, 
                    n_workers=1, 
                    threads_per_worker=CORES, 
                    memory_limit=RAM,
                    silence_logs=logging.ERROR)

if not (GEN_MAT.__name__ ==  gen_sparse and test_func.__name__ == test_inv):
    start = time()
    test_func()
    total_time = time() - start
    f = open(f"{SAVE_FOLDER_NAME}/{index+1}_{RAM}_{test_func.__name__}_{GEN_MAT.__name__}_{CHUNK}_{CORES}_run{run}.txt", "w")
    f.write(f"{total_time}")
    f.close()

if scheduler_add is not None:
    client.close()







