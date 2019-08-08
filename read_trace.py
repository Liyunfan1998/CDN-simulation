import numpy as np
import pandas as pd
from collections import OrderedDict
import matplotlib.pyplot as plt

df = pd.read_csv('mds_0.csv', header=None)
df.columns = ['Timestamp', 'Hostname', 'DiskNumber',
              'Type', 'Offset', 'Size', 'ResponseTime']
df['Timestamp'] = df['Timestamp'].astype(np.int64)

# sort
df = df.sort_values(by='Timestamp')
# display
print("overview:\n", df.head())
print("total size: ", df.drop_duplicates(['Offset'])['Size'].sum())


def make_requests(df):
    for row in df.itertuples():
        yield getattr(row, 'Offset'), getattr(row, 'Size')


for fid, size in make_requests(df):
    print(fid, size)
