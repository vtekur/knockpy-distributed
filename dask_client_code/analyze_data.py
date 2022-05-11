from os import listdir
from os.path import isfile, join

onlyfiles = [f for f in listdir('../dask_single_node_search') if isfile(join('../dask_single_node_search', f))]
print(len(onlyfiles))


