from cacheout import Cache
from cacheout.lru import LRUCache
from numpy.random import shuffle
from cacheout.lfu import LFUCache
import time

cache = LFUCache(maxsize=17, ttl=0, timer=time.time, default=None)

# every loop has 300 items
loop_size = 300
client1 = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'] * (loop_size // 10)
client2 = ['A', 'B', 'C', 'D', 'E', 'F'] * (loop_size // 6)
client3 = ['a', 'b'] * (loop_size // 2)
client1 = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'X'] * (loop_size // 11 + 1)

clients = [client1, client2, client3]

# client_attack = (['X'] + [None] * 14) * (loop_size // 15)  # 20 'X's
# client1 = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'X'] * 20 \
#           + ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'] * 10
# client_attack = (['X'] + [None] * 8) * 27 + [None] * (300 - 9 * 27)  # 27 'X's
hit, miss = 0, 0


def handle_request(req, cache, hit, miss):
    if req:
        if cache.has(req):
            hit += 1
        else:
            cache.add(req, 1)
            miss += 1
    return hit, miss


for i in range(loop_size):
    tmp = [item[i] for item in clients]
    shuffle(tmp)
    for t in tmp:
        print(t)
        hit, miss = handle_request(t, cache, hit, miss)

print(hit, miss)
print('hit_rate', hit / (hit + miss))
