from client_revised import *

FILE_NUM = int(5e3)
TIMESTAMP_NUM = int(1e3)
# client = Client(FILE_NUM, TIMESTAMP_NUM)
# client.__make_attack_trace__('H')
# print(1)

from utils import ZipfGenerator
import matplotlib.pyplot as plt
zipf_generator = ZipfGenerator(n=FILE_NUM, alpha=0.7)
z_out = zipf_generator.gen_arr(100)
print(z_out)
plt.figure()
plt.scatter(range(len(z_out)), z_out)
plt.ylabel("file_id")
plt.xlabel("each request")
plt.legend()
plt.show()
