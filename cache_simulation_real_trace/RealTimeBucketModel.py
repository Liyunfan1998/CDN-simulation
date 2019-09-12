# -*- coding: UTF-8 -*-
from utils import readTraceForBucketModel, generateCountDict
from numpy.random import shuffle, choice, normal
from numpy import array
from cacheout.lfu import LFUCache
import time, gc
from collections import Counter
from copy import deepcopy
import multiprocessing

historyCache = None  # 要当全局变量


class RealTimeBucketModel:
    class SimCache:
        def __init__(self, cacheSize):
            self.cache = LFUCache(maxsize=cacheSize, ttl=0, timer=time.time, default=None)
            self.hit, self.miss = 0, 0

        def handle_request(self, req):
            if self.cache.has(req):
                self.hit += 1
            else:
                self.cache.add(req, 1)
                self.miss += 1

        def processTrace(self, trace):
            for req in trace:
                self.handle_request(req)
            return self.hit / (self.hit + self.miss + 0.01)  # hit rate

    def __init__(self, requestsInPeriod, periodLength, cacheSize, historyBucket=None):
        """
        construct a real-time bucket model based on the given request pattern in a fixed period of time
        requestsInPeriod is a dict, mapping file to the number of times it is requested in a period
        eg. requestsInPeriod = {'a':3,'b':5,'c':11}
        """
        self.periodLength = periodLength
        self.cacheSize = cacheSize
        self.cache = self.SimCache(cacheSize)  # new cache init
        self.requestsInPeriodDict = dict(generateCountDict(requestsInPeriod))
        self.attackCandidates = []
        if historyBucket:
            self.historyCountDict = historyBucket.requestsInPeriodDict
            X, Y = Counter(self.historyCountDict), Counter(self.requestsInPeriodDict)
            self.requestsInPeriodDict = dict(X + Y)
        self.repeatTimes = 50  # for calculating/finding a min for the attack pattern

        self.constructBucket(historyBucket)

    def findBestAttack(self, cacheSize, attackSize, historyCache=None):
        """try different attackTraffic and return a best choice, can use RL approach???"""
        print("attackSize", attackSize)
        globalMinHR, globalMinHR_allTraffic = 1, []
        self.historyCache = historyCache
        pool = multiprocessing.Pool(processes=50)
        for i in range(1 * attackSize):
            print("\tTime", i)
            if len(self.attackCandidates):
                attackTraffic = choice(self.attackCandidates, size=self.periodLength * attackSize, replace=True)
                la = len(attackTraffic)
                for i in range(1):
                # for i in range(self.repeatTimes):
                    allTraffic = self.scatterAttackIntoTrace(attackTraffic, self.requestsInPeriodDict, la, lt)
                    """太无奈了， multiprocessing不支持序列化自定义对象，numpy也不免"""
                    result = pool.apply(simAttack, args=(cacheSize, allTraffic))
                    # minHR, allTraffic = self.simAttack(cacheSize, attackTraffic, historyCache)
                    minHR, allTraffic = result  # .get()
                    if minHR < globalMinHR:
                        globalMinHR_allTraffic = allTraffic
                        globalMinHR = minHR
            # clean up the memory
            if i % 1000 == 0:
                gc.collect()

        pool.close()
        pool.join()
        print("found global Min HR", globalMinHR)
        print("#" * 30)
        # print("globalMinHR_allTraffic", globalMinHR_allTraffic)
        return globalMinHR_allTraffic

    def constructBucket(self, historyBucket):
        self.bucket = {}
        for k, v in self.requestsInPeriodDict.items():
            if v not in self.bucket:
                self.bucket[v] = [k]
            else:
                self.bucket[v].append(k)
        self.featCacheSize()

    def featCacheSize(self):
        virtualCacheSize = 0
        sortedBucket = sorted(self.bucket.items(), key=lambda x: x[0], reverse=True)
        tmp_k_plus_one = []
        for item in sortedBucket:
            virtualCacheSize += len(item[1])
            if virtualCacheSize >= self.cacheSize:
                # this indicates that <the recurrence item[0]> is <the k level>
                # (the k th level is most susceptible to replacement)
                self.kthLevelLength = len(item[1])
                # attack type 1
                self.attackCandidates = item[1]  # include the k th level into attackCandidates
                # attack type 2
                self.attackCandidates.extend(tmp_k_plus_one)
                return item[0]
            else:
                tmp_k_plus_one = item[1]
        return None

    def simAttack(self, cacheSize=None, attackTraffic=None, historyCache=None):
        """not focusing on the coming sequence"""
        hr_list = []
        la = len(attackTraffic)
        for i in range(self.repeatTimes):
            # shuffle(allTraffic) # don't make sense
            allTraffic = self.scatterAttackIntoTrace(self.attackTraffic, self.requestsInPeriodDict, la, lt)
            if self.historyCache:
                self.cache = self.historyCache
            else:
                self.cache = self.SimCache(self.cacheSize)  # new cache????
            c = self.cache
            hr = c.processTrace(allTraffic)
            hr_list.append(hr)
        print(min(hr_list))
        # print(allTraffic)
        return min(hr_list), allTraffic

    def scatterAttackIntoTrace(self, attackTraffic, trace, la, lt):
        allTraffic = []
        allTrafficLength = la + lt
        p = array([la, lt]) / allTrafficLength
        shuffle(attackTraffic)
        attackTrafficCopy, traceCopy = list(deepcopy(attackTraffic)), list(deepcopy(trace))
        time.sleep(1)
        for i in range(allTrafficLength):
            if choice([True, False], size=1, p=p):  # attack
                # allTraffic.append(choice(attackTrafficCopy, size=1, replace=False))
                # del XXX
                if len(attackTrafficCopy):
                    allTraffic.append(attackTrafficCopy[0])
                    attackTrafficCopy = attackTrafficCopy[1:]
            else:
                if len(traceCopy):
                    allTraffic.append(traceCopy[0])
                    traceCopy = traceCopy[1:]
        return allTraffic


def simAttack(cacheSize, allTraffic):
    """not focusing on the coming sequence"""
    if historyCache:
        c = deepcopy(historyCache)
    else:
        c = RealTimeBucketModel.SimCache(cacheSize)  # new cache????
    hr = c.processTrace(allTraffic)
    print('\t' + str(hr))
    return hr, allTraffic


if __name__ == '__main__':
    lt = periodSize = 50
    cacheSize = 20
    trace = readTraceForBucketModel("../sample.txt", map=True, periodSize=periodSize)
    realTimeBucketModel = None
    timeC = 0
    for requestsInPeriod in trace:
        timeC += 1
        OriginalCache = RealTimeBucketModel.SimCache(cacheSize)
        print("Baseline", timeC, OriginalCache.processTrace(requestsInPeriod))
        realTimeBucketModel = RealTimeBucketModel(requestsInPeriod, periodSize, cacheSize, realTimeBucketModel)
        attackSize = round(normal(loc=0.1 * periodSize, scale=1.0, size=None))
        globalMinHR_allTraffic = realTimeBucketModel.findBestAttack(cacheSize, attackSize, realTimeBucketModel.cache)
        realTimeBucketModel.cache.processTrace(globalMinHR_allTraffic)
