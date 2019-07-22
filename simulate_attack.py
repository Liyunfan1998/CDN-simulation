from client_new import Client
# from client import Client
from server import Server
import matplotlib.pyplot as plt
import pandas as pd
from copy import deepcopy
import numpy as np

FILE_NUM = int(1e5)
TIMESTAMP_NUM = int(5e5)
client = Client(FILE_NUM, TIMESTAMP_NUM)

print('FILE_NUM', FILE_NUM)
print('REQUEST_NUM', TIMESTAMP_NUM)
print('client.file_pool_size', client.file_pool_size)
# pd.DataFrame(client.trace).to_csv('trace_normal.csv')  # 'trace_' + str(np.random.randint(1000)) + '.csv'
# pd.DataFrame(client.trace_with_attack).to_csv('trace_attack.csv')
"""
# fig = plt.figure(figsize=(15, 3))  # LRU
# fig = plt.figure(figsize=(3, 15))  # LFU
fig = plt.figure()
ax = fig.add_subplot(111)
ax.imshow(client.trace, cmap='Greens')
plt.ylabel("time-slots")
plt.xlabel("file id")
plt.title("trace")
plt.show()
"""

server_hit_rate_dict, server_hit_rate_with_attack_dict = {}, {}
cache_size_array = [1e3, 2e3, 5e3, 1e4, 2e4, 5e4, 1e5, 2e5, 5e5, 1e6]
print('\n' + '#' * 80 + '\n')

hit_rate_stable_for_all = {}


def attack(attack_level):
    server_hit_rate, server_hit_rate_with_attack = [], []
    client.__make_attack_trace__(client.total_attack_requests // client.num_of_time_stamps, attack_level)
    client.total_attack_requests = np.sum(np.sum(client.attack_trace))
    print('total_attack_requests:', client.total_attack_requests)

    # fig = plt.figure(figsize=(15, 3))  # LRU
    # fig = plt.figure(figsize=(3, 15))  # LFU
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.imshow(client.attack_trace, cmap='Reds')
    plt.ylabel("time-slots")
    plt.xlabel("file id")
    plt.title("attack-trace" + attack_level)
    plt.show()
    """
    # for cache_size in range(client.file_pool_size // 100, client.file_pool_size // 2, client.file_pool_size // 500):
    for cache_size in cache_size_array:
        print('cache_size', cache_size)
        # two identical servers
        server = Server(cache_size, 'LRU')
        server_under_attack = deepcopy(server)

        if cache_size not in hit_rate_stable_for_all:
            hit_rate_stable_for_all[cache_size] = {}

        if not len(server_hit_rate_dict):
            hit_rate_stable = []  # record hit_rate after each file request
            # just normal trace
            for request_file in client.make_requests(client.trace):
                server.handle(request_file)
                hit_rate_stable.append(server.hit_rate())  # record hit_rate after each file request
            hit_rate_stable_for_all[cache_size]['N'] = hit_rate_stable
            server_hit_rate.append(server.hit_rate())
            print('normal:', server_hit_rate[-1])

        # normal trace with attack trace
        trace = client.trace + client.attack_trace
        hit_rate_stable = []  # reset hit_rate_stable
        for request_file in client.make_requests(trace):
            server_under_attack.handle(request_file)
            hit_rate_stable.append(server_under_attack.hit_rate())  # record hit_rate after each file request

        hit_rate_stable_for_all[cache_size][attack_level] = hit_rate_stable
        server_hit_rate_with_attack.append(server_under_attack.hit_rate())
        print('attack:', attack_level, server_hit_rate_with_attack[-1])
    if not len(server_hit_rate_dict):
        server_hit_rate_dict['H'] = server_hit_rate
    server_hit_rate_with_attack_dict[attack_level] = server_hit_rate_with_attack


attack_levels = {'H', 'M', 'L', 'LL'}  #
for attack_level in attack_levels:
    attack(attack_level)

rdi = np.random.randint(0, 100)

plt.figure(figsize=(15, 15))
for cache_size in hit_rate_stable_for_all:
    for attack_level in hit_rate_stable_for_all[cache_size]:
        tmp = hit_rate_stable_for_all[cache_size][attack_level]
        lb = str(cache_size) + attack_level
        plt.plot(range(len(tmp)), tmp, label=lb)
plt.ylabel("hit_rate_stable@cache_size")
plt.xlabel("time")
plt.title("attack-hit_rate-changes")
plt.legend()
plt.savefig("attack-hit_rate-changes_" + rdi + ".png")
plt.show()

plt.figure(figsize=(10, 5))
plt.plot(cache_size_array, server_hit_rate_dict['H'], color='green', label='cache')
for attack_level in attack_levels:
    plt.plot(cache_size_array, server_hit_rate_with_attack_dict[attack_level],
             label='cache_under_attack' + attack_level)
plt.xlabel("cache size")
plt.ylabel("hit rate")
plt.legend()
plt.savefig("cache_under_attack_" + rdi + ".png")
plt.show()
