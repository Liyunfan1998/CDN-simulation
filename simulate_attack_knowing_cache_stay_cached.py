from client_revised import Client
from server_by_GJL import Server
import matplotlib.pyplot as plt
import pandas as pd
import operator
from copy import deepcopy
from functools import reduce
import numpy as np
import gc

FILE_NUM = int(5e5)
TIMESTAMP_NUM = int(1e3)
client = Client(FILE_NUM, TIMESTAMP_NUM)

print('FILE_NUM', FILE_NUM)
print('TIMESTAMP_NUM', TIMESTAMP_NUM)
print('client.file_pool_size', client.file_pool_size)

server_hit_rate_with_attack_dict, attack_in_cache = {'N': None}, {}
# cache_size_array = [1e4, 2e4, 5e4, 1e5, 2e5, 3e5, 4e5, 5e5, 6e5, 7e5, 8e5, 9e5, 1e6, 2e6, 3e6, 4e6, 5e6, 1e6, 2e6, 3e6, 4e6, 5e6]
cache_size_array = [1e4, 2e4, 5e4, 1e5, 2e5, 5e5, 1e6, 2e6, 3e6, 4e6, 5e6]
print('\n' + '#' * 80 + '\n')


def attack(attack_level):
    server_hit_rate, server_hit_rate_with_attack, server_hit_rate_with_attack_ignore_attack = [], [], []
    client.__make_attack_trace__(attack_level)
    attack_in_cache[attack_level] = {}

    for cache_size in cache_size_array:
        if cache_size > client.file_pool_size: continue
        attack_in_cache_percentage_changes = []
        # two identical servers
        server = Server(cache_size, 'LRU')
        server_under_attack = deepcopy(server)

        if not server_hit_rate_with_attack_dict['N']:
            # just normal trace
            for time in range(client.num_of_time_stamps):
                for request_file in client.trace[time]:
                    server.handle(client.file_pool[request_file])
            server_hit_rate.append(server.hit_rate())
            print('normal:', 'cache_size:', cache_size, server_hit_rate[-1])

        for time in range(client.num_of_time_stamps):
            if time >= 0.05 * TIMESTAMP_NUM:  # 不知道该不该做此限制，一开始需要让server启动再开始攻击才有针对性
                attack_trace = client.__make_attack_trace_for_single_time_stamp__(server_under_attack.cache, time,
                                                                                  client.num_attack_for_each_time_stamp[
                                                                                      time],
                                                                                  pattern='KCS',
                                                                                  spy=server_under_attack.spy)
                server_under_attack.spy.clear()
            requests_in_timestamp = [(f, True) for f in client.trace[time]] + [(f, False) for f in
                                                                               attack_trace]  # client.attack_trace[time]]
            np.random.shuffle(requests_in_timestamp)
            for request_file in requests_in_timestamp:
                server_under_attack.handle(client.file_pool[request_file[0]], request_file[1])
            # 记录attack file占总cache size的比例
            attack_in_cache_percentage_changes.append(
                sum([client.file_pool[f].size for f in server_under_attack.attack_in_cache]) / cache_size)
        print('total_attack_requests:', sum([len(i) for i in client.attack_trace]))
        server_hit_rate_with_attack.append(server_under_attack.hit_rate())
        server_hit_rate_with_attack_ignore_attack.append(server_under_attack.hit_rate(ignore_attack=True))
        attack_in_cache[attack_level][cache_size] = attack_in_cache_percentage_changes
        print('attack:', attack_level, 'cache_size:', cache_size, server_hit_rate_with_attack[-1])
        print('attack:', attack_level + '_ignore_attack', 'cache_size:', cache_size,
              server_hit_rate_with_attack_ignore_attack[-1])
    if not server_hit_rate_with_attack_dict['N']:
        server_hit_rate_with_attack_dict['N'] = server_hit_rate
    server_hit_rate_with_attack_dict[attack_level] = server_hit_rate_with_attack
    server_hit_rate_with_attack_dict[attack_level + '_ignore_attack'] = server_hit_rate_with_attack_ignore_attack


attack_levels = {'H'}  # , 'M', 'L', 'LL'
for attack_level in attack_levels:
    attack(attack_level)
    gc.collect()

# df = pd.DataFrame.from_dict(server_hit_rate_with_attack_dict)
# df.to_csv('./server_hit_rate_with_attack.csv')

df = pd.DataFrame.from_dict(attack_in_cache)
df.to_csv('./attack_in_cache.csv')

plt.figure(figsize=(10, 5))
for attack_level in server_hit_rate_with_attack_dict:
    plt.plot(cache_size_array, server_hit_rate_with_attack_dict[attack_level],
             label='cache_under_attack' + attack_level)
plt.xlabel("cache size")
plt.ylabel("hit rate")
plt.legend()
# plt.savefig("cache_under_attack_" + str(rdi) + ".png")
plt.show()

plt.figure(figsize=(20, 5))
for attack_level in attack_in_cache:
    for cache_size in attack_in_cache[attack_level]:
        len_l = len(attack_in_cache[attack_level][cache_size])
        plt.plot(range(len_l), attack_in_cache[attack_level][cache_size],
                 label='cache_under_attack' + str(cache_size) + attack_level)
plt.xlabel("time")
plt.ylabel("attack_in_cache_percentage")
plt.legend()
# plt.savefig("cache_under_attack_" + str(rdi) + ".png")
plt.show()
