import numpy as np


def generate_zipf(a, size=1000):
    """
    :param a:float or array_like of floats
        Distribution parameter. Should be greater than 1.
    :param size:int or tuple of ints, optional
        Output shape. If the given shape is, e.g., (m, n, k),
        then m * n * k samples are drawn. If size is None (default),
        a single value is returned if a is a scalar.
        Otherwise, np.array(a).size samples are drawn.
    :return:ndarray or scalar
        Drawn samples from the parameterized Zipf distribution.
    """
    return np.random.zipf(a, size)


def generate_scan(width, num_for_scan, mu, sigma=3):
    """
    :param width: how wide the scan peak is
    :param num_for_scan: how many number to generate for scan distribution
    :param mu: expectation (or mean)
    :param sigma: variance
    :return: ndarray or scalar
        Drawn samples from the parameterized Scan distribution.
    """
    rest = num_for_scan % width
    tmp = np.random.normal(mu, sigma, int(num_for_scan / width))
    tmp = np.array([int(i) for i in (list(tmp) * width + list(np.random.normal(mu, sigma, rest)))])
    return tmp - min(tmp)  # make sure all the numbers are bigger or equal to zero
