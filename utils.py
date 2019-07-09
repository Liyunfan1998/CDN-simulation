import numpy as np
from scipy import special


def generate_zipf(a=10000, size=1000, file_num=100):
    """
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
        y = y.astype('int32')
        return y
    else:
        return np.array([])


def generate_scan(width, num_for_scan, mu, sigma=3):
    """
    :param width: how wide the scan peak is
    :param num_for_scan: how many number to generate for scan distribution
    :param mu: expectation (or mean)
    :param sigma: variance
    :return: ndarray or scalar
        Drawn samples from the parameterized Scan distribution.
    """
    width = int(width)
    rest = num_for_scan % width
    tmp = np.random.normal(mu, sigma, int(num_for_scan / width))
    tmp = np.array([round(i) for i in (tmp.tolist() * width + np.random.normal(mu, sigma, rest).tolist())])
    return tmp - min(tmp) if len(tmp) > 0 else tmp  # make sure all the numbers are bigger or equal to zero
