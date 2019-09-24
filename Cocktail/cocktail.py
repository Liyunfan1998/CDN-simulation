# -*- coding: UTF-8 -*-
import utils
from numpy.random import shuffle, choice, normal
from numpy import array
from cacheout.lfu import LFUCache
from cacheout.lru import LRUCache
import time, gc
from collections import Counter
from copy import deepcopy
import multiprocessing


def cluster_by_freq(frq_dict):
    """
    freq_dict is a dict, mapping file to the number of times it is requested in a period
    eg. freq_dict = {'a':3,'b':5,'c':11}
    return {3:['a'],5:['b'],11:['c']}
    """
    d = defaultdict(list)
    pairs = enumerate(data) if isinstance(data, list) else data.items()
    for k, v in pairs:
        d[v].append(k)
    return d


def count_freq(req_list):
    """
    trace_in_period is a list of requests
    eg. trace_in_period=[a,b,c,c,b,c,c,c,b,b,a,c,c,c,c,a,b,c,c]
    freq_dict is a dict, mapping file to the number of times it is requested in a period
    eg. freq_dict = {'a':3,'b':5,'c':11}
    """
    return dict((a, req_list.count(a)) for a in set(req_list))


class TraceGenerator:
    """
    store the args in self and createTrace with the params
    """

    def __init__(self):
        pass

    def param_setter(self, distribution, params=dict()):
        pass

    def create_trace(self):
        pass


class CocktailModel:
    """
    given a distribution and a trace,
    given the pre-fixed settings of a cache,
    provide the calculated hit rate
    """

    def __init__(self, trace_in_period, cacheSize, history_stage=None, history_importance=0.5):
        """
        construct a cocktail model based on the given request pattern in a fixed period of time
        """
        self.cacheSize = cacheSize
        bartending_cocktail(trace_in_period)

    def moving_average_for_freq(self, freq_dict, history_freq_dict):
        for k in history_stage:
            history_freq_dict[k] = history_freq_dict[k] / 2
        X, Y = Counter(freq_dict), Counter(history_freq_dict)
        self.history_freq_dict = self.freq_dict = dict(X + Y)

    def featCacheSize(self):
        """
        find and return kth level index ---- k
        """
        virtualCacheSize = 0
        sortedBucket = sorted(self.stage.items(), key=lambda x: x[0], reverse=True)
        for item in sortedBucket:
            virtualCacheSize += len(item[1])
            if virtualCacheSize >= self.cacheSize:
                # this indicates that <the recurrence item[0]> is <the k level>
                # (the k th level is most susceptible to replacement)
                return item[0]
        return None

    def bartending_cocktail(self, trace_in_period):
        freq_dict = count_frq(trace_in_period)
        self.moving_average_for_freq(freq_dict, self.history_freq_dict)
        bucket = cluster_by_freq(self.freq_dict)
        self.surface_level_freq = self.featCacheSize()

    def calculate_hitrate_theo(self, cache, distribution, params):
        """
        provide a quick formula for calculation of hit rate
        """
        if distribution == 'absolute order':
            miss = len([k for k, v in self.freq_dict.items() if v >= self.surface_level_freq])
            return 1 - miss / len(self.freq_dict)
        elif distribution == 'normal':
            pass
        elif distribution == 'exp':
            pass
        elif distribution == 'zipf':
            pass
        elif distribution == 'bino':
            pass


class RealCache:
    """
    create a realCache using the 'cacheout' lib
    """

    def __init__(self, cacheSize, policy='LFU'):
        if policy == 'LFU':
            self.cache = LFUCache(maxsize=cacheSize, ttl=0, timer=time.time, default=None)
        elif policy == 'LRU':
            self.cache = LRUCache(maxsize=cacheSize, ttl=0, timer=time.time, default=None)
        self.hit, self.miss = 0, 0

    def handle_request(self, req):
        if self.cache._has(req):
            self.hit += 1
        else:
            self.cache._add(req, 1)
            self.miss += 1

    def hit_rate(self, trace):
        """
        return hit rate for trace
        """
        for req in trace:
            self.handle_request(req)
        return self.hit / (self.hit + self.miss + 0.01)  # hit rate
