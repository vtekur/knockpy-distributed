import os
import pandas as pd
# assign directory
directory = 'output_files'
 
# iterate over files in
# that directory
rams = []
functions = []
matrixtypes = []
chunktypes = []
cores = []
times = []
for filename in os.listdir(directory):
    if 'Store' in filename:
        continue
    f = os.path.join(directory, filename)
    print(filename.split('_'))
    atts = filename.split('_')
    rams.append(int(atts[1][:-2]))
    functions.append(atts[3])
    matrixtypes.append(atts[5])
    chunktypes.append(atts[6])
    cores.append(atts[7])
    # checking if it is a file
    file1 = open(f, 'r')
    lines = file1.readlines()
    print(float(lines[0]))
    times.append(float(lines[0]))

df = pd.DataFrame({
    'RAM': rams,
    'function': functions,
    'matrix_type': matrixtypes,
    'chunk_type': chunktypes,
    'num_cores': cores,
    'time': times
})

print(df)
df.to_csv('knockpy_times.csv')
