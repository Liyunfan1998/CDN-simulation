from client import Client
from server import Server
import matplotlib.pyplot as plt
import pandas as pd
from copy import deepcopy
import numpy as np

FILE_NUM = int(1e4)
REQUEST_NUM = int(1e3)
client = Client(FILE_NUM, REQUEST_NUM)
print("total number of requests", client.total_client_requests)
# pd.DataFrame(client.trace).to_csv('trace_normal.csv')  # 'trace_' + str(np.random.randint(1000)) + '.csv'
# pd.DataFrame(client.trace_with_attack).to_csv('trace_attack.csv')

fig = plt.figure(figsize=(15, 3))
ax = fig.add_subplot(111)
ax.imshow(client.trace, cmap='Greens')
plt.ylabel("time-slots")
plt.xlabel("file id")
plt.title("trace")
plt.show()

fig = plt.figure(figsize=(15, 3))
ax = fig.add_subplot(111)
ax.imshow(client.trace, cmap='Greens')
ax.imshow(client.trace_with_attack, cmap='Reds')
plt.ylabel("time-slots")
plt.xlabel("file id")
plt.title("attack-trace")
plt.show()

print('FILE_NUM', FILE_NUM)
print('REQUEST_NUM', REQUEST_NUM)
print('client.file_pool_size', client.file_pool_size)

plt.figure(figsize=(15, 8))
plt.xlabel("time")
plt.ylabel("file id")
plt.title("trace")
plt.imshow(client.trace.reshape((FILE_NUM, REQUEST_NUM)), aspect='auto')
plt.show()

server_hit_rate, server_hit_rate_with_attack = [], []
cache_size_array = []
for cache_size in range(client.file_pool_size // 10, client.file_pool_size, client.file_pool_size // 100):
    cache_size_array.append(cache_size / client.file_pool_size)
    # two identical servers
    server = Server(cache_size, 'LFU')
    server_under_attack = deepcopy(server)

    # just normal trace
    for request_file in client.make_requests(client.trace):
        server.handle(request_file)
    server_hit_rate.append(server.hit_rate())

    # normal trace with attack trace
    trace = client.trace + client.trace_with_attack
    # print(1000 == len(trace), np.sum(np.sum(client.trace_with_attack)))
    print('normal:', server_hit_rate[-1])

    for request_file in client.make_requests(trace):
        server_under_attack.handle(request_file)
    server_hit_rate_with_attack.append(server_under_attack.hit_rate())
    print('attack:', server_hit_rate_with_attack[-1])
# print(server_hit_rate)

plt.figure(figsize=(15, 8))
plt.plot(cache_size_array, server_hit_rate, color='green', label='cache')
plt.plot(cache_size_array, server_hit_rate_with_attack, color='red', label='cache_under_attack')
plt.xlabel("cache size / file pool total size")
plt.ylabel("hit rate")
plt.legend()
plt.show()
