import numpy as np
import knockpy
from time import time
from dask.distributed import Client
import dask.array as da
import h5py  

client = Client(processes=False,
                n_workers=1, 
                threads_per_worker=8,
                memory_limit='60GB')

start = time()
n = 82000 # number of data points
p = 82000 # number of features
Sigma = knockpy.dgp.AR1(p=p, rho=0.5, use_dask=True) # Stationary AR1 process with correlation 0.5
print(f"AR(1) generation: {time()-start}")


# Sample X
## get cholesky decomp
L = da.linalg.cholesky(Sigma, lower=True)
sn = da.random.standard_normal(size=(n, p))
X = L.dot(sn.T)
print(f"Data Shape: {X.shape}")
print(f"Sampling: {time()-start}")

# Save Data
X.to_hdf5('data_large.hdf5', '/X')
print(f"Saving: {time()-start}")   
client.close()