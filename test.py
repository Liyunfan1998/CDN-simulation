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
