# import matplotlib.pyplot as plt
#
# a = [6, 1, 3, 7, 10, 4, 2, 1, 4, 1, 5, 0, 11, 7, 8, 7, 3, 11, 3, 1, 6, 10, 6, 2, 6, 11, 19, 16, 6, 10, 3, 16, 1, 1, 0,
#      4, 15, 0, 16, 1, 0, 0, 1, 4, 4, 13, 16, 11, 2, 8, 13, 4, 11, 2, 7, 7, 2, 9, 5, 4, 6, 10, 1, 3, 0, 21, 17, 3, 2, 0,
#      9, 4, 9, 2, 0, 20, 12, 9, 12, 4, 2, 22, 2, 7, 4, 5, 16, 16, 0, 6, 1, 1, 15, 0, 2, 1, 7, 1, 13, 8, 0, 3, 3, 14, 2,
#      0, 6, 8, 5, 7, 5, 8, 6, 2, 3, 1, 12, 13, 0, 16, 1, 3, 0, 11, 17, 6, 3, 3, 16, 0, 6, 0, 8, 0, 0, 2, 17, 7, 2, 0, 1,
#      13, 1, 0, 6, 5, 5, 9, 12, 2, 3, 4, 13, 11, 2, 2, 15, 4, 10, 9, 19, 4, 12, 7, 2, 7, 9, 15, 9, 13, 10, 12, 3, 11, 6,
#      4, 2, 2, 11, 8, 1, 4, 5, 18, 5, 1, 13, 13, 4, 11, 1, 4, 8, 1, 8, 6, 7, 2, 4, 1, 7, 6, 2, 4, 19, 15, 2, 3, 3, 3, 3,
#      0, 0, 18, 7, 9, 2, 6, 10, 2, 12, 3, 0, 3, 0, 12, 2, 16, 1, 7, 0, 2, 24, 0, 8, 5, 4, 0, 11, 17, 9, 12, 5, 6, 3, 12,
#      9, 15, 0, 3, 1, 28, 4, 3, 8, 7, 7, 8, 6, 13, 14, 0, 1, 4, 5, 2, 0, 6, 8, 8, 21, 10, 10, 16, 23, 15, 6, 0, 8, 1, 14,
#      10, 12, 6, 3, 2, 3, 10, 9, 3, 4, 0, 20, 17, 17, 8, 8, 12, 7, 2, 13, 14, 4, 14, 4, 6, 0, 4, 0, 9, 11, 9, 22, 7, 4,
#      6, 16, 13, 9, 9, 12, 5, 2, 10, 4, 4, 8, 3, 7, 7, 0, 6, 8, 14, 2, 9, 15, 24, 5, 10, 8, 1, 6, 7, 13, 15, 5, 1, 5, 10,
#      35, 12, 23, 3, 3, 19, 14, 5, 5, 1, 0, 0, 9, 7, 1, 5, 12, 0, 17, 4, 4, 0, 0, 14, 0, 7, 1, 5, 8, 11, 1, 10, 1, 12,
#      19, 2, 11, 9, 3, 10, 22, 8, 8, 1, 4, 0, 12, 0, 8, 4, 6, 19, 3, 14, 3, 6, 10, 19, 3, 3, 1, 17, 4, 7, 4, 6, 21, 7, 2,
#      0, 9, 14, 2, 16, 6, 9, 1, 9, 10, 0, 1, 5, 9, 5, 7, 1, 18, 10, 1, 11, 12, 1, 19, 12, 7, 3, 5, 7, 2, 16, 6, 1, 6, 7,
#      4, 12, 4, 4, 2, 6, 1, 4, 16, 13, 7, 7, 6, 10, 15, 8, 3, 7, 8, 7, 0, 8, 20, 4, 4, 4, 6, 9, 18, 16, 1, 12, 6, 1, 6,
#      3, 5, 19, 19, 16, 8, 12, 5, 28, 10, 11, 21, 15, 3, 11, 2, 2, 16, 11, 10, 23, 6, 7, 9, 8, 22, 16, 3, 0, 4, 1, 9, 2,
#      10, 9, 3, 3, 10, 6, 13, 3, 0, 13, 8, 16, 5, 3, 11, 6, 8, 8, 18, 0, 3, 27, 2, 17, 4, 8, 6, 9, 2, 14, 2, 3, 5, 5, 12,
#      7, 16, 1, 21, 10, 11, 1, 3, 12, 3, 25, 4, 9, 3, 5, 1, 6, 0, 17, 3, 0, 2, 3, 6, 17, 3, 11, 7, 11, 3, 4, 2, 3, 5, 5,
#      10, 13, 0, 2, 1, 10, 16, 7, 2, 11, 16, 1, 3, 8, 7, 8, 3, 15, 17, 2, 7, 13, 15, 7, 7, 12, 9, 6, 3, 10, 3, 14, 6, 7,
#      7, 0, 1, 15, 4, 1, 12, 12, 9, 4, 2, 3, 17, 3, 15, 13, 20, 6, 12, 2, 6, 1, 7, 7, 2, 1, 8, 10, 11, 0, 12, 0, 0, 5,
#      14, 4, 10, 1, 4, 0, 0, 1, 7, 6, 0, 1, 18, 4, 5, 9, 8, 5, 2, 4, 6, 1, 7, 9, 0, 4, 9, 0, 1, 25, 6, 9, 24, 2, 18, 0,
#      9, 4, 11, 5, 15, 6, 17, 4, 0, 23, 5, 16, 16, 2, 3, 0, 1, 9, 0, 4, 6, 12, 16, 11, 9, 15, 6, 2, 0, 2, 7, 12, 7, 13,
#      2, 22, 12, 24, 19, 10, 7, 4, 7, 18, 14, 6, 13, 5, 19, 8, 22, 6, 18, 14, 0, 0, 14, 1, 5, 4, 7, 3, 6, 16, 4, 15, 2,
#      13, 11, 2, 8, 0, 8, 3, 7, 18, 8, 2, 4, 4, 2, 5, 5, 10, 2, 3, 4, 5, 4, 3, 6, 2, 0, 3, 4, 17, 0, 1, 7, 7, 12, 7, 1,
#      7, 11, 12, 26, 17, 3, 3, 3, 3, 2, 2, 13, 10, 0, 4, 6, 1, 6, 27, 1, 17, 6, 7, 8, 7, 23, 7, 18, 5, 6, 5, 3, 1, 2, 0,
#      17, 24, 3, 0, 4, 10, 5, 11, 3, 12, 16, 11, 2, 2, 3, 8, 10, 8, 10, 10, 8, 11, 1, 14, 4, 6, 0, 3, 5, 0, 7, 7, 10, 1,
#      8, 16, 11, 7, 13, 4, 9, 11, 8, 5, 1, 9, 1, 4, 1, 5, 6, 2, 4, 1, 6, 13, 8, 1, 8, 11, 14, 10, 8, 5, 6, 7, 3, 1, 4,
#      14, 7, 4, 4, 3, 1, 1, 2, 12, 7, 9, 19, 6, 12, 1, 18, 7, 6, 6, 0, 15, 2, 2, 9, 12, 12, 15, 6, 15, 2, 6, 5, 3, 7, 0,
#      12, 7, 4, 11, 2, 7, 0, 11, 15, 25, 0, 11, 6, 8, 14, 11, 4, 16, 4, 16, 13, 1, 12, 19, 14, 3, 8, 9, 21, 2, 3, 16, 4,
#      0, 18, 6, 12, 7, 6, 12, 22, 1, 7, 6, 9, 19, 16, 3, 0, 6, 3, 9, 3, 9, 1, 0, 7, 11, 15, 9, 6, 13]
#
# print(len(set(a)))
# plt.hist(a)
# plt.show()


from cacheout.lfu import LFUCache
import time
cache = LFUCache(maxsize=4, ttl=0, timer=time.time, default=None)
for i in range(4):
    cache.add(1, 1)
    cache.add(2, 1)
for i in range(3):
    cache.add(3, 1)
    cache.add(4, 1)
cache.add(5, 1)
cache.add(6, 1)
cache.keys()
