import numpy as np
from utils import *


class File:
    def __init__(self, fid, size):
        self.fid = fid  # 文件惟一id, 从0开始
        self.size = size  # 文件大小


class Client:  # 用户端 请求文件
    def __init__(self, file_num, request_num):
        self.file_num = file_num  # 文件池数量
        self.request_num = request_num  # trace请求数
        self.file_pool = []  # 文件池
        self.file_pool_size = 0  # 文件池总文件大小
        self.trace = np.zeros(shape=(file_num, request_num), dtype=np.int32)  # trace
        self.__make_files__()
        self.__make_trace__()

    def __make_files__(self):  # 生成文件池
        for i in range(self.file_num):
            file = File(i, int(np.random.exponential(scale=100)))  # 文件大小负指数分布
            self.file_pool.append(file)
            self.file_pool_size += file.size

    def __frac_exp__(self, s=0.5):
        res = np.random.rand() * np.random.exponential(scale=s)
        while res >= 1:
            res = np.random.rand() * np.random.exponential(scale=s)
        return res

    def __make_trace__(self):  # 生成trace
        for file in range(self.file_num):
            # 在整个trace中，几次对某文件请求的峰值（对文件的请求峰值就是，在某段时间，对某个文件的高频率请求），（// is "flooring division"）
            request_peaks = int(np.random.randint(1, self.request_num // 100) * np.random.exponential(scale=0.2))
            if request_peaks <= 1:  # 不是峰值
                continue
            gap = self.request_num // request_peaks  # 是峰值，则计算整个trace中可以有几个这样的峰值，记为gap
            for peak in range(request_peaks):
                front = peak * gap
                back = front + gap  # 每一段起落（front-peak-back）
                mid = np.random.randint(front, back)
                start = mid - int(self.__frac_exp__(0.5) * (mid - front))
                end = mid + int(self.__frac_exp__(0.5) * (back - mid))
                # 同一个时间点的时候扫描所有的文件，看在这个时间点的时候有没有请求
                for time in range(start, end):
                    self.trace[file][time] = 1
        self.trace = self.trace.reshape((self.request_num, self.file_num))

    def make_requests(self):  # 迭代器 产生文件请求流
        for time in self.trace:
            for i in range(self.file_num):
                if time[i]:
                    yield self.file_pool[i]

    def generate_normal_client_trace(self, trace_size, num_file_stored):
        """
        :param trace_size:
        :param num_file_stored:
        :return:
        """
        zipf_size = int(trace_size * 0.7)  # zipf files takes 70% of the total trace
        zipf = generate_zipf(a=num_file_stored, size=zipf_size)

        scan_size = trace_size - zipf_size  # scan files takes 30% of the total trace
        pop_scan_width = 0.05 * num_file_stored  # suppose the scan files comes from 5% of the total files in storage
        # the peak is at files whose popularity rankings are at top 1/5, referencing LHD paper
        scan = generate_scan(width=pop_scan_width, num_for_scan=scan_size, mu=int(num_file_stored * 0.2))
        self.trace = np.concatenate((zipf, scan))

    def generate_attack_seq(self):
        """
        to be used in __make_trace__
        :return:
        """
        raise NotImplementedError
