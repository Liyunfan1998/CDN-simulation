from client_real_trace import Client
from server_by_GJL import Server
import matplotlib.pyplot as plt
import pandas as pd
import operator
from copy import deepcopy
from functools import reduce
import numpy as np
import gc

FILE_NUM = int(5e3)
TIMESTAMP_NUM = int(1e3)
client = Client(FILE_NUM, TIMESTAMP_NUM)

print('FILE_NUM', FILE_NUM)
print('TIMESTAMP_NUM', TIMESTAMP_NUM)
print('client.file_pool_size', client.file_pool_size)

server_hit_rate_with_attack_dict, hit_rate_stable_for_all = {'N': None}, {}
cache_size_array = [1e3, 2e3, 5e3, 1e4, 2e4, 5e4, 1e5, 2e5, 5e5, 7.5e5, 1e6, 2e6, 3e6, 4e6, 5e6]
print('\n' + '#' * 80 + '\n')


def attack(attack_level):
    server_hit_rate, server_hit_rate_with_attack, server_hit_rate_with_attack_ignore_attack = [], [], []
    client.__make_attack_trace__(attack_level)

    for cache_size in cache_size_array:
        # hit_rate_stable_for_all[cache_size] = {}
        # print('cache_size', cache_size)
        # two identical servers
        server = Server(cache_size, 'LRU')
        server_under_attack = deepcopy(server)

        if not server_hit_rate_with_attack_dict['N']:
            # hit_rate_stable = []  # record hit_rate after each file request
            # just normal trace
            for time in range(client.num_of_time_stamps):
                for request_file in client.trace[time]:
                    server.handle(client.file_pool[request_file])
                    # hit_rate_stable.append(server.hit_rate())  # record hit_rate after each file request
                # if time >= 0.05 * TIMESTAMP_NUM:  # 不知道该不该做此限制，一开始需要让server启动再开始攻击才有针对性
                #     client.__make_attack_trace_for_single_time_stamp__(server.cache, time,
                #                                                        client.num_attack_for_each_time_stamp[time],
                #                                                        pattern='KC')
            # hit_rate_stable_for_all[cache_size]['N'] = hit_rate_stable
            server_hit_rate.append(server.hit_rate())
            print('normal:', 'cache_size:', cache_size, server_hit_rate[-1])

        # normal trace with attack trace ---- (f,not_attack)
        # trace = [[(f, True) for f in client.trace[i]] + [(f, False) for f in client.attack_trace[i]] for i in
        #          range(client.num_of_time_stamps)]
        # for lst in trace:
        #     np.random.shuffle(lst)  # 再次打乱同一时间片内的请求
        # hit_rate_stable = []  # reset hit_rate_stable
        # for request_file in reduce(operator.concat, trace):
        for time in range(client.num_of_time_stamps):
            if time >= 0.05 * TIMESTAMP_NUM:  # 不知道该不该做此限制，一开始需要让server启动再开始攻击才有针对性
                client.__make_attack_trace_for_single_time_stamp__(server_under_attack.cache, time,
                                                                   client.num_attack_for_each_time_stamp[time],
                                                                   pattern='KCS', spy=server_under_attack.spy)
                server_under_attack.spy.clear()
            requests_in_timestamp = [(f, True) for f in client.trace[time]] + [(f, False) for f in
                                                                               client.attack_trace[time]]
            np.random.shuffle(requests_in_timestamp)
            for request_file in requests_in_timestamp:
                server_under_attack.handle(client.file_pool[request_file[0]], request_file[1])
                # hit_rate_stable.append(
                #     server_under_attack.hit_rate(ignore_attack=True))  # record hit_rate after each file request

        # hit_rate_stable_for_all[cache_size][attack_level] = hit_rate_stable
        server_hit_rate_with_attack.append(server_under_attack.hit_rate())
        server_hit_rate_with_attack_ignore_attack.append(server_under_attack.hit_rate(ignore_attack=True))
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

df = pd.DataFrame.from_dict(server_hit_rate_with_attack_dict)
df.to_csv('./server_hit_rate_with_attack.csv')

plt.figure(figsize=(10, 5))
for attack_level in server_hit_rate_with_attack_dict:
    plt.plot(cache_size_array, server_hit_rate_with_attack_dict[attack_level],
             label='cache_under_attack' + attack_level)
plt.xlabel("cache size")
plt.ylabel("hit rate")
plt.legend()
# plt.savefig("cache_under_attack_" + str(rdi) + ".png")
plt.show()
