import knockpy
from time import time
from dask.distributed import Client
import dask.array as da
import logging

client = Client(processes=False,
                n_workers=1, 
                threads_per_worker=8,
                memory_limit='10GB',
                silence_logs=logging.ERROR)

start = time()

# Generate X Data
n = 20000 # number of data points
p = 20000 # number of features
A = da.random.standard_normal(size=(p, p))
Sigma = A.dot(A.T)
print(f"Sigma Generation: {time()-start}")
L = da.linalg.cholesky(Sigma, lower=True)
sn = da.random.standard_normal(size=(n, p))
X = L.dot(sn.T)
print(f"Data Sampling: {time()-start}")

# # Create random S matrix
S = da.diag(da.random.random_sample((p,)) )

# # sample knockoffs
sampler = knockpy.knockoffs.GaussianSampler(X, Sigma=Sigma, S=S)
sampler.sample_knockoffs(use_dask=True)
print(f"Knockoffs: {time()-start}")


client.close()