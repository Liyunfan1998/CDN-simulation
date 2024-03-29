# -*- coding: UTF-8 -*-
import numpy as np
from scipy import special


def generate_zipf(a=10000, size=1000, file_num=100):
    """
    已弃置
    :param a:float or array_like of floats
        Distribution parameter. Should be greater than 1.
    :param size:int or tuple of ints, optional
        Output shape. If the given shape is, e.g., (m, n, k),
        then m * n * k samples are drawn. If size is None (default),
        a single value is returned; if a is a scalar;
        np.array(a).size samples are drawn.
    :return:ndarray or scalar
        Drawn samples from the parameterized Zipf distribution.
    """
    x = np.random.zipf(a, size)
    # y = x ** (-a) / special.zetac(a)
    if len(x) > 0:
        y = x / max(x) * (file_num - 1)
        return y.astype('int32')
    else:
        return np.array([])


import math, bisect, random
from functools import reduce


class ZipfGenerator:
    """
    alpha can be less than one
    """

    def __init__(self, n, alpha):
        # Calculate Zeta values from 1 to n:
        tmp = [1. / (math.pow(float(i), alpha)) for i in range(1, round(n) + 1)]
        zeta = reduce(lambda sums, x: sums + [sums[-1] + x], tmp, [0])

        # Store the translation map:
        self.distMap = [x / zeta[-1] for x in zeta]

    def next(self):
        # Take a uniform 0-1 pseudo-random value:
        u = random.random()
        # Translate the Zipf variable:
        return bisect.bisect(self.distMap, u) - 1

    def gen_arr(self, output_size):
        out = []
        for i in range(output_size):
            out.append(self.next())
        return np.array(out)


def generate_scan(width, num_for_scan, mu, sigma=3):
    """
    :param width: how wide the scan peak is
    :param num_for_scan: how many number to generate for scan distribution
    :param mu: expectation (or mean)
    :param sigma: variance
    :return: ndarray or scalar
        Drawn samples from the parameterized Scan distribution.
    """
    width = round(width)
    rest = num_for_scan % width
    tmp = np.random.normal(mu, sigma, round(num_for_scan // width))
    tmp = np.array([round(i) for i in (tmp.tolist() * width + np.random.normal(mu, sigma, rest).tolist())])
    return tmp - min(tmp) if len(tmp) and min(tmp) < 0 else tmp  # make sure all the numbers are bigger or equal to zero


def generate_exponential(num_for_scan, scale=1.0):
    return np.random.exponential(scale=scale, size=num_for_scan).astype('int32')


def generate_normal(num_for_scan, mu, sigma=3):
    """
    :param num_for_scan: how many number to generate for scan distribution
    :param mu: expectation (or mean)
    :param sigma: variance
    :return:
    """
    mu, sigma, num_for_scan = 10, 3, 100
    return np.random.normal(mu, sigma, num_for_scan).astype('int32')


def readTraceForBucketModel(path, map=True, periodSize=None):
    with open(path, 'r') as f:
        trace = f.readline().split(",")
    if map:
        countDict = generateMapDict(trace)
        trace = [countDict[i] for i in trace]
    if periodSize and type(periodSize) is int:
        cutSize = len(trace) // periodSize * periodSize
        trace = np.reshape(trace[:cutSize], (-1, periodSize))
    return trace


def generateMapDict(lst):
    countRepeatReq = generateCountDict(lst)
    mapDict = {}
    j = 0
    for i in countRepeatReq:
        mapDict[i[0]] = j
        j += 1
    return mapDict


def generateCountDict(lst):
    countRepeatReq = {}
    for req in lst:
        if req in countRepeatReq:
            countRepeatReq[req] += 1
        else:
            countRepeatReq[req] = 1
    countRepeatReq = sorted(countRepeatReq.items(), key=lambda d: d[1], reverse=True)
    return countRepeatReq
