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
        self.num_of_time_stamps = request_num  # trace请求数
        self.file_pool = []  # 文件池
        self.file_pool_size = 0  # 文件池总文件大小
        self.trace, self.attack_trace = None, None
        self.__make_files__()
        self.file_mapping = [i for i in range(self.file_num)]
        np.random.shuffle(self.file_mapping)  # 乱序
        self.__make_trace__()
        self.total_client_requests = np.sum(np.sum(self.trace))
        self.total_attack_requests = round(self.total_client_requests * 0.1)
        print('total_client_requests:', self.total_client_requests)

        """ # 并入simulation了
        self.__make_attack_trace__(self.total_attack_requests // self.num_of_time_stamps)  # // self.num_of_time_stamps
        self.total_attack_requests = np.sum(np.sum(self.trace_with_attack))
        print('total_attack_requests:', self.total_attack_requests)
        """

    def __make_files__(self):  # 生成文件池(no need to change)
        for i in range(self.file_num):
            file = File(i, int(np.random.exponential(scale=1000)))  # 文件大小负指数分布(no need to change)，大小0-1000
            self.file_pool.append(file)
            self.file_pool_size += file.size

    def make_requests(self, trace):  # 迭代器 产生文件请求流
        """不能按照文件流行程度产生request"""
        for time in trace:
            if sum(time):
                tmp = []
                for i in range(self.file_num):
                    tmp.extend([i] * time[i])
                np.random.shuffle(tmp)
                for i in tmp:
                    yield self.file_pool[i]

    def generate_normal_client_requests_for_single_time_stamp(self, single_requests_size=1000):
        """
        生成一个时间片的requests
        假设整个trace有1000个时间片
        正常的trace中，scan峰值出现在zipf流行度排20 % 处的文件
        :param
        single_requests_size:
        :param
        num_file_stored:
        :return:
        """
        # print('single_requests_size', single_requests_size)
        zipf_size = round(single_requests_size * 0.7)  # zipf files takes 70% of the total trace
        zipf = generate_zipf(a=2, size=zipf_size, file_num=self.file_num)

        scan_size = single_requests_size - zipf_size  # scan files takes 30% of the total trace
        pop_scan_width = round(
            0.05 * self.file_num)  # suppose the scan files comes from 5% of the total files in storage

        # the Scan peak is at files whose popularity rankings are at top 1/5, referencing LHD paper
        scan = generate_scan(width=pop_scan_width, num_for_scan=scan_size,
                             mu=np.random.normal(loc=0.2 * self.file_num, scale=0.01 * self.file_num))
        # mu=np.random.randint(0, self.file_num))  # mu=int(self.file_num * 0.2)
        # print(scan)
        request_files_before_mapping = np.concatenate((zipf, scan)).astype('int32')
        return [self.file_mapping[i] for i in request_files_before_mapping]

    def update_mapping(self, files_by_ranking):
        self.file_mapping = files_by_ranking

    def __make_trace__(self):  # 生成trace
        self.trace = np.zeros(shape=(self.num_of_time_stamps, self.file_num), dtype=np.int32)
        for time in range(self.num_of_time_stamps):
            # num_requests_for_single_time_stamp = self.request_num // self.num_of_time_stamps
            num_requests_for_single_time_stamp = np.random.randint(0, self.file_num * 0.25)
            ts = self.generate_normal_client_requests_for_single_time_stamp(num_requests_for_single_time_stamp)
            for i in ts:
                self.trace[time][i] += 1

    def __make_attack_trace__(self, single_attack_requests_size, attack_level='L', pattern='Random'):
        """
        to be used in __make_trace__
        :return:
        """
        level_percentage_mapping = {'H': 0.2, 'M': 0.02, 'L': 0.002, 'LL': 0.0002}
        self.attack_trace = np.zeros(shape=(self.file_num, self.num_of_time_stamps), dtype=np.int32)
        max_num_requests_for_single_time_stamp = round(
            self.total_client_requests / self.num_of_time_stamps * level_percentage_mapping[attack_level])
        step = 1
        while not max_num_requests_for_single_time_stamp:
            step *= 10
            max_num_requests_for_single_time_stamp = round(step * self.total_client_requests / self.num_of_time_stamps *
                                                           level_percentage_mapping[attack_level])
        print('max_num_requests_for_single_time_stamp:', max_num_requests_for_single_time_stamp)
        for time in range(self.num_of_time_stamps):
            # uniform
            if time % step:
                continue
            num_requests_for_single_time_stamp = np.random.randint(0, max_num_requests_for_single_time_stamp + 1)
            result_list = sample(range(0, self.file_num - 1), num_requests_for_single_time_stamp)  # random sample
            for i in result_list:
                self.attack_trace[i][time] += 1
        self.attack_trace = self.attack_trace.transpose()
