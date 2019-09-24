import numpy as np
from scipy import special
import math, bisect, random
from functools import reduce
from collections import defaultdict


class TraceGenerator:
    """
    store the args in self and createTrace with the params
    """

    def __init__(self, period_length=50):
        self.period = period_length

    def set_period_len(self, period_length):
        self.period = period_length

    def generate_zipf(self, n=100, alpha=0.7, num_samples=50):
        # Calculate Zeta values from 1 to n:
        tmp = np.power(np.arange(1, n + 1), -alpha)
        zeta = np.r_[0.0, np.cumsum(tmp)]
        # Store the translation map:
        distMap = [x / zeta[-1] for x in zeta]
        # Generate an array of uniform 0-1 pseudo-random values:
        u = np.random.random(num_samples)
        # bisect them with distMap
        v = np.searchsorted(distMap, u)
        samples = [t - 1 for t in v]
        return samples

    def generate_exponential(num_samples=50, scale=10):
        return np.random.exponential(scale=scale, size=num_samples).astype('int32')

    def generate_normal(num_samples=50, mu=0, sigma=25):
        return np.random.normal(mu, sigma, num_samples).astype('int32')


def cluster_by_freq_slow(frq_dict):
    bucket = {}
    for k, v in trace_in_period.items():
        if v not in bucket:
            bucket[v] = [k]
        else:
            bucket[v].append(k)
    return bucket


def cluster_by_freq(freq_dict):
    """
    freq_dict is a dict, mapping file to the number of times it is requested in a period
    eg. freq_dict = {'a':3,'b':5,'c':11}
    return {3:['a'],5:['b'],11:['c']}
    """
    d = defaultdict(list)
    pairs = enumerate(freq_dict) if isinstance(freq_dict, list) else freq_dict.items()
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
