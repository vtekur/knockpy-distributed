import knockpy
import argparse
from time import time
from dask.distributed import Client
import dask.array as da

parser = argparse.ArgumentParser(description='dask args')
parser.add_argument('--cores', type=int, default=8,
                    help='number of cpu cores') 
parser.add_argument('--ram', type=str, default='10GB',
                    help='number of cpu cores') 
args = parser.parse_args()

client = Client(processes=False,
                n_workers=1, 
                threads_per_worker=args.cores,
                memory_limit=args.ram)

start = time()

# Generate X Data
n = 10000 # number of data points
p = 10000 # number of features
A = da.random.standard_normal(size=(p, p))
Sigma = A.dot(A.T)
print(f"Sigma Generation: {time()-start}")
L = da.linalg.cholesky(Sigma, lower=True)
sn = da.random.standard_normal(size=(n, p))
X = L.dot(sn.T)
print(f"Data Sampling: {time()-start}")

# Create random S matrix
S = da.diag(da.random.random_sample((p,)) ) * 0.001

# sample knockoffs
sampler = knockpy.knockoffs.GaussianSampler(X, Sigma=Sigma, S=S)
sampler.sample_knockoffs(use_dask=True).compute()
print(f"Knockoffs: {time()-start}")


# client.close()