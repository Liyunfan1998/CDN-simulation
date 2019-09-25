# -*- coding: UTF-8 -*-
from utils import *
from numpy.random import shuffle, choice, normal
from numpy import array,reshape
from cacheout.lfu import LFUCache
from cacheout.lru import LRUCache
import time, gc
from collections import Counter
from pandas import DataFrame
from copy import deepcopy
import multiprocessing

rg = [0., 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.]


class CocktailModel:
    """
    given a distribution and a trace,
    given the pre-fixed settings of a cache,
    provide the calculated hit rate
    """

    def __init__(self, trace_in_period, cacheSize, history_importance=0.5):
        """
        construct a cocktail model based on the given request pattern in a fixed period of time
        """
        self.cacheSize = cacheSize
        self.history_freq_dict = {}
        self.history_importance = history_importance
        self.bartending_cocktail(trace_in_period)

    def moving_average_for_freq(self, freq_dict, history_freq_dict):
        for k in history_freq_dict:
            history_freq_dict[k] = history_freq_dict[k] * self.history_importance
        for k in freq_dict:
            freq_dict[k] = freq_dict[k] * (1 - self.history_importance)
        X, Y = Counter(freq_dict), Counter(history_freq_dict)
        self.history_freq_dict = self.freq_dict = dict(X + Y)

    def featCacheSize(self):
        """
        find and return kth level index ---- k
        """
        virtualCacheSize = 0
        sortedBucket = sorted(self.bucket.items(), key=lambda x: x[0], reverse=True)
        for item in sortedBucket:
            virtualCacheSize += len(item[1])
            if virtualCacheSize >= self.cacheSize:
                # this indicates that <the recurrence item[0]> is <the k level>
                # (the k th level is most susceptible to replacement)
                return item[0]
        return None

    def bartending_cocktail(self, trace_in_period):
        freq_dict = count_freq(trace_in_period)
        self.moving_average_for_freq(freq_dict, self.history_freq_dict)
        self.bucket = cluster_by_freq(self.freq_dict)
        self.surface_level_freq = self.featCacheSize()

    def calculate_hitrate_theo(self, distribution='absolute order', params=None):
        """
        provide a quick formula for calculation of hit rate
        """
        if distribution == 'absolute order':
            if not self.surface_level_freq:
                return 1
            miss = len([k for k, v in self.freq_dict.items() if v >= self.surface_level_freq])
            return 1 - miss / len(self.freq_dict)
        elif distribution == 'normal':
            pass
        elif distribution == 'exp':
            pass
        elif distribution == 'zipf':
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


if __name__ == '__main__':
    traceGenerator = TraceGenerator(50)
    # trace = [traceGenerator.generate_zipf(n=100, alpha=0.7, num_samples=50) for i in range(20)]
    # print('zipf: n=100, alpha=0.7, num_samples=50')

    # trace = [traceGenerator.generate_exponential(scale=20) for i in range(20)]
    # print('exp: n=100, scale=10')

    trace = [list(traceGenerator.generate_normal(sigma=10)) for i in range(20)]
    # print('normal: mu=0, sigma=25')
    print(trace)
    exit(0)

    for cache_Size in range(10, 100, 10):
        global_plot_record = {'lfu': [], 'lru': [], 0.: [], 0.1: [], 0.2: [], 0.3: [], 0.4: [], 0.5: [], 0.6: [],
                              0.7: [], 0.8: [], 0.9: [], 1: []}
        real_cache_lfu = RealCache(cache_Size, 'LFU')
        real_cache_lru = RealCache(cache_Size, 'LRU')
        last_cocktail = None
        cocktails = None
        for period_trace in trace:
            # print('lfu', real_cache_lfu.hit_rate(period_trace))
            # print('lru', real_cache_lru.hit_rate(period_trace))
            global_plot_record['lfu'].append(real_cache_lfu.hit_rate(period_trace))
            global_plot_record['lru'].append(real_cache_lru.hit_rate(period_trace))
            if not cocktails:
                x = rg
                y = [CocktailModel(period_trace, cache_Size, history_importance=hi) for hi in rg]
                cocktails = dict(zip(x, y))

            for history_importance in rg:
                cocktails[history_importance].bartending_cocktail(period_trace)
                global_plot_record[history_importance].append(
                    cocktails[history_importance].calculate_hitrate_theo())
            #     print('cocktail with history_importance', history_importance, cocktail.calculate_hitrate_theo())
            # print('*' * 20)
        DataFrame(global_plot_record).to_excel('./cache_Size' + str(cache_Size) + '.xlsx')
        # DataFrame(global_plot_record).to_csv('./cache_Size' + str(cache_Size) + '.csv')
        print('cache_Size:', cache_Size, global_plot_record)
