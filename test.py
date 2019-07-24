from client_revised import *

FILE_NUM = int(5e3)
TIMESTAMP_NUM = int(1e3)
client = Client(FILE_NUM, TIMESTAMP_NUM)

client.__make_attack_trace__('H')
print(1)
