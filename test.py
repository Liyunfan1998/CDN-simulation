import matplotlib as mpl
import matplotlib.pyplot as pyplot
import numpy as np
import pandas as pd

"""
# make values from -5 to 5, for this example
zvals = np.random.rand(100, 100) * 10

# make a color map of fixed colors
cmap = mpl.colors.ListedColormap(['blue', 'black', 'red'])
bounds = [-6, -2, 2, 6]
norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

# tell imshow about color map so that only set colors are used
img = pyplot.imshow(zvals, interpolation='nearest',
                    cmap='Reds', norm=norm)

# make a color bar
pyplot.colorbar(img, cmap='Reds', 
                norm=norm, boundaries=bounds, ticks=[-5, 0, 5])
pyplot.show()
"""

"""
fig, ax = pyplot.subplots(1, 1)
# ax = ax.flatten()
x = np.random.rand(10000)
y = np.random.rand(10000)

ax0 = ax.scatter(x, y, c=x, cmap='Reds')
fig.colorbar(ax0, ax=ax)
pyplot.show()
"""

"""
# -*- coding:utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np

data = np.clip(np.random.randn(500, 500), -1, 1)  # 生成随机数据,5行5列,最大值1,最小值-1
df = pd.read_csv('trace_20.csv')
data=df.as_matrix()
fig = plt.figure()
# 第一个子图,按照默认配置
ax = fig.add_subplot(111)
ax.imshow(data, cmap='Reds')
plt.show()
"""

"""
# -*- coding: utf-8 -*-
# P(r) = C / r^α zipf分布函数
import numpy as np

a = 2.  # float类型，应该比1大
# Samples are drawn from a Zipf distribution with specified parameter a > 1
s = np.random.zipf(a, 2000)
print(s)
import matplotlib.pyplot as plt
from scipy import special
import scipy.stats as stats

count, bins, ignored = plt.hist(s[s < 100], 100, density=True)
x = np.arange(1., 100.)
y = x ** (-a) / special.zetac(a)
print(x)
print(y)
plt.plot(x, y, linewidth=2, color='r')
plt.show()
"""

from client import Client
from server import Server
import matplotlib.pyplot as plt
import pandas as pd
from copy import deepcopy
import numpy as np

FILE_NUM = int(1e2)
REQUEST_NUM = int(1e4)
client = Client(FILE_NUM, REQUEST_NUM)
print("total number of requests", client.total_client_requests)
server_hit_rate, server_hit_rate_with_attack = [], []
cache_size_array = []
cache_size = 10
print('cache_size / client.file_pool_size', cache_size / client.file_pool_size)
# two identical servers
server = Server(cache_size, 'LFU')
server_under_attack = deepcopy(server)

print(client.trace)
# just normal trace
for request_file in client.make_requests(client.trace):
    server.handle(request_file)
server_hit_rate.append(server.hit_rate())

# normal trace with attack trace
trace = client.trace + client.attack_trace
# print(1000 == len(trace), np.sum(np.sum(client.trace_with_attack)))
print('normal:', server_hit_rate[-1])

for request_file in client.make_requests(trace):
    server_under_attack.handle(request_file)
server_hit_rate_with_attack.append(server_under_attack.hit_rate())
print('attack:', server_hit_rate_with_attack[-1])
