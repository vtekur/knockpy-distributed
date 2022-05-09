import sys

from dask.distributed import Client, LocalCluster
import dask.array as da

if len(sys.argv) != 2:
    raise ValueError("Correct usage: python test_dask.py [scheduler address]")
sched_address = sys.argv[1]


client = Client(sched_address)

a = da.random.randint(5, size=(10000, 10000))
b = da.random.randint(5, size=(10000, 10000))

print(da.matmul(a, b))

client.close()