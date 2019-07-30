import numpy as np
from utils import *
from random import sample


class File:
    def __init__(self, fid, size):
        self.fid = fid  # 文件惟一id, 从0开始
        self.size = size  # 文件大小
        # self.is_attack_and_replaced_out_of_cache = False


class Client:  # 用户端 请求文件
    def __init__(self, file_num, request_num):
        self.file_num = file_num  # 文件池数量
        self.zg = ZipfGenerator(n=self.file_num, alpha=0.7)
        self.num_of_time_stamps = request_num  # trace请求数
        self.file_pool, self.file_pool_set = [], set(range(self.file_num))  # 文件池
        self.file_pool_size = 0  # 文件池总文件大小
        self.level_percentage_mapping = {'H': 0.2, 'M': 0.02, 'L': 0.002, 'LL': 0.0002}
        self.trace, self.attack_trace = [], [[]] * self.num_of_time_stamps
        self.__make_files__()
        self.file_mapping = [i for i in range(self.file_num)]
        np.random.shuffle(self.file_mapping)  # 乱序
        self.__make_trace__()
        self.total_client_requests = sum([len(i) for i in self.trace])
        print('total_client_requests:', self.total_client_requests)
        self.num_attack_for_each_time_stamp = []

    def __make_files__(self):  # 生成文件池(no need to change)
        for i in range(self.file_num):
            file = File(i, int(np.random.exponential(scale=1000)))  # 文件大小负指数分布(no need to change)，大小0-1000
            self.file_pool.append(file)
            self.file_pool_size += file.size

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
        # zipf = generate_zipf(a=1.2, size=zipf_size, file_num=self.file_num)
        zipf = self.zg.gen_arr(zipf_size)

        scan_size = single_requests_size - zipf_size  # scan files takes 30% of the total trace
        pop_scan_width = round(
            0.05 * self.file_num)  # suppose the scan files comes from 5% of the total files in storage

        # the Scan peak is at files whose popularity rankings are at top 1/5, referencing LHD paper
        scan = generate_scan(width=pop_scan_width, num_for_scan=scan_size,
                             mu=np.random.normal(loc=0.2 * self.file_num, scale=0.01 * self.file_num))
        # mu=np.random.randint(0, self.file_num))  # mu=int(self.file_num * 0.2)
        # print(scan)
        request_files_before_mapping = np.concatenate((zipf, scan)).astype('int32')
        np.random.shuffle(request_files_before_mapping)
        return [self.file_mapping[i] for i in request_files_before_mapping]

    def __make_trace__(self):  # 生成trace
        """
        需要修改num_requests_for_single_time_stamp
        """
        for time in range(self.num_of_time_stamps):
            num_requests_for_single_time_stamp = np.random.randint(0, self.file_num * 0.25)  # 需要修改
            self.trace.append(
                self.generate_normal_client_requests_for_single_time_stamp(num_requests_for_single_time_stamp))

    def __make_attack_trace__(self, attack_level='L', pattern='Random'):
        """
        to be used in __make_trace__
        :return:
        """
        self.attack_trace = [[]] * self.num_of_time_stamps
        self.num_attack_for_each_time_stamp = []
        max_num_requests_for_single_time_stamp = round(
            self.total_client_requests / self.num_of_time_stamps * self.level_percentage_mapping[attack_level])
        step = 1
        while not max_num_requests_for_single_time_stamp:
            step *= 10
            max_num_requests_for_single_time_stamp = round(step * self.total_client_requests / self.num_of_time_stamps *
                                                           self.level_percentage_mapping[attack_level])
        # print('max_num_requests_for_single_time_stamp:', max_num_requests_for_single_time_stamp)
        for time in range(self.num_of_time_stamps):
            # uniform
            if time % step:
                # self.attack_trace[time] = []
                self.num_attack_for_each_time_stamp.append(0)
                continue
            num_requests_for_single_time_stamp = np.random.randint(0, max_num_requests_for_single_time_stamp + 1)
            self.num_attack_for_each_time_stamp.append(num_requests_for_single_time_stamp)

            # if pattern == 'Random':
            #     result_list = sample(range(0, self.file_num - 1), num_requests_for_single_time_stamp)  # random sample
            # elif pattern == "KC":  # knowing what's in cache
            #     pass
            # result_list = self.generate_attack_requests_knowing_cache_for_single_time_stamp(,num_requests_for_single_time_stamp)
            # result_list = []
            # self.attack_trace[time] = result_list

        print('total_attack_requests:', sum(self.num_attack_for_each_time_stamp))

    def __make_attack_trace_for_single_time_stamp__(self, cache, time, num_requests=100, pattern='Random', spy=None):
        if pattern == 'Random':
            self.attack_trace[time] = sample(range(0, self.file_num - 1), num_requests)  # random sample
        elif pattern == 'KC':  # knowing what's in cache
            self.attack_trace[time] = self.generate_attack_requests_knowing_cache_for_single_time_stamp(set(cache),
                                                                                                        num_requests)
        elif pattern == 'KCS':  # knowing what's in cache and make attack files stay cached
            attack_files_kicked_out = self.generate_attack_requests_to_stay_in_cache_knowing_cache_for_single_time_stamp(spy)
            len_l = len(attack_files_kicked_out)
            self.attack_trace[time] = attack_files_kicked_out[0:min(len_l, num_requests)] + \
                                      self.generate_attack_requests_knowing_cache_for_single_time_stamp(
                                          set(cache), num_requests - len_l)

    def generate_attack_requests_knowing_cache_for_single_time_stamp(self, file_cached,
                                                                     requests_size=100):  # file_cached is a set
        if requests_size <= 0: return []
        file_not_cached = list(self.file_pool_set - file_cached)
        try:
            return list(set(sample(file_not_cached, requests_size)))
        except ValueError:
            # print("ValueError: Sample larger than population or is negative")
            print('ValueError **** file_not_cached:', len(file_not_cached), 'requests_size:', requests_size)
            return list(set(sample(file_not_cached, len(file_not_cached))))

    @staticmethod
    def generate_attack_requests_to_stay_in_cache_knowing_cache_for_single_time_stamp(attack_file_kicked_out):
        """
        :param attack_file_kicked_out: 一个set
        :return: 一个list，每个被踢出的恶意文件请求一次，使其驻留服务器内存，如果被踢出的恶意文件太多，则只请求requests_size个
        """
        return list(attack_file_kicked_out)
