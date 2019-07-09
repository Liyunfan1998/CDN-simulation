import numpy as np
from utils import *
from random import sample


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
        self.trace, self.trace_with_attack = None, None
        self.num_of_time_stamps = 1000  # self.num_of_time_stamps 和 self.request_num 是一码事
        self.popular_files = []
        self.__make_files__()
        self.file_mapping = [i for i in range(self.file_num)]
        np.random.shuffle(self.file_mapping)  # 乱序
        self.__make_trace__()
        self.total_client_requests = np.sum(np.sum(self.trace))
        self.total_attack_requests = round(self.total_client_requests * 0.1)
        print('total_client_requests:', self.total_client_requests)
        self.__make_attack_trace__(self.total_attack_requests // self.request_num)  # // self.num_of_time_stamps
        self.total_attack_requests = np.sum(np.sum(self.trace_with_attack))
        print('total_attack_requests:', self.total_attack_requests)

    def __make_files__(self):  # 生成文件池(no need to change)
        for i in range(self.file_num):
            file = File(i, int(np.random.exponential(scale=1000)))  # 文件大小负指数分布(no need to change)，大小0-1000
            self.file_pool.append(file)
            self.file_pool_size += file.size

    def __frac_exp__(self, s=0.5):
        res = np.random.rand() * np.random.exponential(scale=s)
        while res >= 1:
            res = np.random.rand() * np.random.exponential(scale=s)
        return res

    def __make_trace__(self):  # 生成trace
        self.trace = np.zeros(shape=(self.file_num, self.request_num), dtype=np.int32)  # trace
        for file in range(self.file_num):
            # 在整个trace中，几次对某文件请求的峰值（对文件的请求峰值就是，在某段时间，对某个文件的高频率请求），（// is "flooring division"）
            request_peaks = int(np.random.randint(1, self.request_num) * np.random.exponential(scale=0.2) // 50)
            # print(file, "peak at", request_peaks)
            if request_peaks <= 1:  # 不是峰值
                # print(file, "not peak")
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
                    self.trace[file][time] = 1  # 在start-end时间段有请求
        self.trace = self.trace.transpose()  # .reshape((self.request_num, self.file_num))
        self.total_client_requests = np.sum(self.trace)
        self.total_attack_requests = self.total_client_requests * 0.01

    def make_requests(self, trace):  # 迭代器 产生文件请求流
        for time in trace:
            for i in range(self.file_num):
                if time[i]:  # 在这个时间有请求
                    for j in range(time[i]):  # 每个文件可能对应有多个请求
                        yield self.file_pool[i]  # 对应的文件request

    def generate_normal_client_requests_for_single_time_stamp(self, single_requests_size=1000):
        """
        生成一个时间片的requests
        假设整个trace有1000个时间片
        正常的trace中，scan峰值出现在zipf流行度排20%处的文件
        :param single_requests_size:
        :param num_file_stored:
        :return:
        """
        # print('single_requests_size', single_requests_size)
        zipf_size = round(single_requests_size * 0.7)  # zipf files takes 70% of the total trace
        zipf = generate_zipf(a=1.414, size=zipf_size, file_num=self.file_num)

        scan_size = single_requests_size - zipf_size  # scan files takes 30% of the total trace
        pop_scan_width = round(
            0.05 * self.file_num)  # suppose the scan files comes from 5% of the total files in storage

        # the Scan peak is at files whose popularity rankings are at top 1/5, referencing LHD paper
        scan = generate_scan(width=pop_scan_width, num_for_scan=scan_size,
                             mu=np.random.randint(0, self.file_num))  # mu=int(self.file_num * 0.2)
        request_files_before_mapping = np.concatenate((zipf, scan)).astype('int32')
        return [self.file_mapping[i] for i in request_files_before_mapping]

    def update_mapping(self, files_by_ranking):
        self.file_mapping = files_by_ranking

    def __make_trace__2(self):  # 生成trace
        self.trace = np.zeros(shape=(self.num_of_time_stamps, self.file_num), dtype=np.int32)
        for time in range(self.num_of_time_stamps):
            # num_requests_for_single_time_stamp = self.request_num // self.num_of_time_stamps
            num_requests_for_single_time_stamp = np.random.randint(0, self.file_num * 0.25)
            ts = self.generate_normal_client_requests_for_single_time_stamp(num_requests_for_single_time_stamp)
            for i in ts:
                self.trace[time][i] += 1

    def make_requests2(self, trace):  # 迭代器 产生文件请求流
        for time in trace:
            for i in time:
                yield self.file_pool[i]  # 对应的文件request

    def __make_attack_trace__(self, single_attack_requests_size):
        """
        to be used in __make_trace__
        :return:
        """
        self.trace_with_attack = np.zeros(shape=(self.file_num, self.request_num), dtype=np.int32)
        for time in range(self.request_num):
            num_requests_for_single_time_stamp = np.random.randint(0, 10)
            resultlist = sample(range(0, self.file_num - 1), num_requests_for_single_time_stamp)  # random sample
            for i in resultlist:
                self.trace_with_attack[i][time] += 1
        self.trace_with_attack = self.trace_with_attack.transpose()
