from cacheout import Cache
from cacheout.lru import LRUCache
from numpy.random import shuffle
from numpy import reshape
from cacheout.lfu import LFUCache
import time

periodSize = 50

cache = LFUCache(maxsize=30, ttl=0, timer=time.time, default=None)
hit, miss = 0, 0

with open("../sample.txt", 'r') as f:
    sample_trace = f.readline().split(",")


# print(len(set(sample_trace))) # 713

def mapping(lst):
    countRepeatReq, mappingDict = {}, {}
    for req in lst:
        if req in countRepeatReq:
            countRepeatReq[req] += 1
        else:
            countRepeatReq[req] = 0
    countRepeatReq = sorted(countRepeatReq.items(), key=lambda d: d[1], reverse=True)
    j = 0
    for i in countRepeatReq:
        mappingDict[i[0]] = j
        j += 1
    return mappingDict


mappingDict = mapping(sample_trace)
sample_trace = [mappingDict[i] for i in sample_trace]

sample_trace = reshape(sample_trace, (20, periodSize))


shuffle(sample_trace)

def handle_request(req, cache, hit, miss):
    if req:
        if cache.has(req):
            hit += 1
            if req not in hashtable:
                hashtable[req] = 0
            hashtable[req] += 1
        else:
            cache.add(req, 1)
            miss += 1
    return hit, miss


for t in sample_trace:
    hashtable = {}
    for i in t:
        hit, miss = handle_request(i, cache, hit, miss)
    print('\n', hit, miss)
    print('hit_rate', hit / (hit + miss))
    print(sorted(hashtable.items(), key=lambda d: d[1], reverse=True))
