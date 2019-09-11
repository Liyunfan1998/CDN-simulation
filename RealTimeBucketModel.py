from numpy.random import shuffle, choice
from cacheout.lfu import LFUCache
import time, gc
from copy import deepcopy


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
            return self.hit / (self.hit + self.miss)  # hit rate

    def __init__(self, requestsInPeriod, periodLength, cacheSize):
        """
        construct a real-time bucket model based on the given request pattern in a fixed period of time
        requestsInPeriod is a dict, mapping file to the number of times it is requested in a period
        eg. requestsInPeriod = {'a':3,'b':5,'c':11}
        """
        self.periodLength = periodLength
        self.cacheSize = cacheSize
        self.requestsInPeriod = requestsInPeriod
        self.repeatTimes = 50  # for calculating a mean for the attack pattern

        self.constructBucket()

    def findBestAttack(self, cacheSize, attackSize, historyCache=None):
        """try different attackTraffic and return a best choice, can use RL approach?"""
        globalMinHR, globalMinHR_allTraffic = 1, []

        for i in range(1000000 * attackSize):
            attackTraffic = choice(self.attackCandidates, size=self.periodLength * attackSize, replace=True)
            minHR, allTraffic = self.simAttack(cacheSize, attackTraffic, historyCache)
            if minHR < globalMinHR:
                globalMinHR_allTraffic = allTraffic
        return globalMinHR_allTraffic

    def constructBucket(self):
        self.bucket = {}
        for k, v in self.requestsInPeriod.items():
            if not self.bucket[v]:
                self.bucket[v] = [k]
            else:
                self.bucket[v].append(k)

    def featCacheSize(self):
        virtualCacheSize = 0
        sortedBucket = sorted(self.bucket.items(), key=lambda x: x[0])
        tmp_k_plus_one = []
        for item in sortedBucket:
            virtualCacheSize += item[0]
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

    def simAttack(self, cacheSize, attackTraffic, historyCache=None):
        """not focusing on the coming sequence"""
        hr_list = []
        la, lt = len(attackTraffic), len(trace)
        for i in range(self.repeatTimes):
            # shuffle(allTraffic) # don't make sense
            allTraffic = self.scatterAttackIntoTrace(attackTraffic, self.requestsInPeriod, la, lt)
            if historyCache:
                self.cache = historyCache
            else:
                self.cache = self.SimCache(cacheSize)  # new cache????
            hr_list.append(self.cache.processTrace(allTraffic))
        return min(hr_list), allTraffic

    def scatterAttackIntoTrace(self, attackTraffic, trace, la, lt):
        allTraffic = []
        allTrafficLength = la + lt
        p = [la, lt]
        shuffle(attackTraffic)
        attackTrafficCopy, traceCopy = deepcopy(attackTraffic), deepcopy(trace)
        for i in range(allTrafficLength):
            if choice([True, False], size=1, p=p):  # attack
                # allTraffic.append(choice(attackTrafficCopy, size=1, replace=False))
                # del XXX
                allTraffic.append(attackTrafficCopy[0])
                attackTrafficCopy = attackTrafficCopy[1:]
            else:
                allTraffic.append(traceCopy[0])
                traceCopy = traceCopy[1:]
        return allTraffic
