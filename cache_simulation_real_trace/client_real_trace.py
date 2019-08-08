import numpy as np
from utils import *
from random import sample
import pandas as pd
import os, sys, json
import gc


class File:
    def __init__(self, fid, size):
        self.fid = fid  # 文件惟一id, 从0开始
        self.size = size  # 文件大小
        # self.is_attack_and_replaced_out_of_cache = False


def dtype_change(np_arr_list, dest_dtype):
    for np_arr in np_arr_list:
        np_arr = np_arr.astype(dest_dtype)


class Client:  # 用户端 请求文件
    def __init__(self, file_num, request_num, real_trace=None):
        self.num_of_time_stamps = request_num  # trace请求数
        self.file_pool, self.file_pool_set = {}, set()  # 文件池
        self.file_pool_size = 0  # 文件池总文件大小
        self.level_percentage_mapping = {'H': 0.2, 'M': 0.02, 'L': 0.002, 'LL': 0.0002}
        self.trace, self.attack_trace = [], [[]] * self.num_of_time_stamps
        self.num_attack_for_each_time_stamp = []
        df = pd.read_csv(real_trace, header=None)
        df.columns = ['Timestamp', 'Type', 'Offset', 'Size']
        # dtype_change([df.Timestamp, df.Offset, df.Size], int)
        del df['Type'], df['Timestamp']
        self.total_client_requests = len(df)
        print('total_client_requests:', self.total_client_requests)
        file_dict = {}
        p = real_trace[:-3] + '_file_dict.json'
        print('trace_file:', p)
        if os.path.isfile(p):
            if sys.version_info.major > 2:
                f = open(p, 'r', encoding='utf-8')
            else:
                f = open(p, 'r')
            file_dict = json.load(f)
        else:
            file_dict = dict(zip(list(df.Offset.astype(int)), list(df.Size.astype(int))))
            with open(p, 'w') as file:
                json.dump(file_dict, file)
                file.close()

        for file in file_dict:
            self.file_pool[file] = File(file, file_dict[file])
        self.file_num = len(file_dict)
        print('FILE_NUM', self.file_num)
        self.file_pool_size = sum(file_dict.values())
        print('client.file_pool_size', self.file_pool_size)
        self.file_pool_set = set(file_dict)
        self.trace = np.append(np.array(df.Offset), np.zeros(1000 - len(df) % 1000)).astype(int).reshape(1000, -1)
        del file_dict
        gc.collect()
        # file_df = pd.DataFrame.from_dict(file_dict, orient='index').reset_index()

    def __make_attack_trace__(self, attack_level='L', pattern='Random'):
        """
        to be used in __make_trace__
        :return:
        """
        # self.attack_trace = [[]] * self.num_of_time_stamps
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

        # print('total_attack_requests:', sum(self.num_attack_for_each_time_stamp))  # 理想化的total_attack_requests

    def __make_attack_trace_for_single_time_stamp__(self, cache, time, num_requests=100, pattern='Random', spy=None):
        if pattern == 'Random':
            # self.attack_trace[time] =\
            return sample(range(0, self.file_num - 1), num_requests)  # random sample
        elif pattern == 'KC':  # knowing what's in cache
            # self.attack_trace[time] = \
            return self.generate_attack_requests_knowing_cache_for_single_time_stamp(set(cache),
                                                                                     num_requests)
        elif pattern == 'KCS':  # knowing what's in cache and make attack files stay cached
            attack_files_kicked_out = self.generate_attack_requests_to_stay_in_cache_knowing_cache_for_single_time_stamp(
                spy)
            len_l = len(attack_files_kicked_out)
            # self.attack_trace[time] = \
            return attack_files_kicked_out[0:min(len_l, num_requests)] + \
                   self.generate_attack_requests_knowing_cache_for_single_time_stamp(
                       set(cache), num_requests - len_l)
        # if len(spy):
        #     print('time:', time, 'stay in cache:', min(len_l, num_requests), 'random:',
        #           max(num_requests - len_l, 0), 'out of cache:', len(spy))

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

    def clear_attack_trace(self):
        self.attack_trace = [[]] * self.num_of_time_stamps
