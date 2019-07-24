from collections import OrderedDict, defaultdict

from abc import ABCMeta, abstractmethod


class Server:  # 服务器(cache)
    __metaclass__ = ABCMeta

    def __init__(self, space, replacement_algo='LRU'):
        self.space = space  # cache大小
        self.remain = space  # cache剩余空间
        self.hit_count = 0  # 命中次数
        self.miss_count = 0  # 未命中次数
        self.replacement_algo = replacement_algo
        if self.replacement_algo == 'LRU':
            self.cache = OrderedDict()  # OrderDict() 模拟cache LRU方法
        elif self.replacement_algo == 'LFU':
            self.mincount = 0
            self.cache = {}
            self.visited = {}
            # 默认字典嵌套一个有序字典，外层字典的键是访问次数，有序字典会根据放入元素的先后顺序进行排序
            self.key_list = defaultdict(OrderedDict)

    def _hit(self, file):
        self.hit_count += 1
        if self.replacement_algo == 'LRU':
            self.cache.move_to_end(file.fid)
        elif self.replacement_algo == 'LFU':
            # 取出该key的访问次数
            if file.fid not in self.visited:
                self.visited[file.fid] = 1
            count = self.visited[file.fid]
            # 对访问次数进行+1
            self.visited[file.fid] += 1
            # 对记录字典进行更新
            self.key_list[count].pop(file.fid)
            self.key_list[count + 1][file.fid] = None
            # 如果访问次数等于最小访问次数，并且该次数下已经没有值了，则最小访问次数+1，为下次加入做准备
            if count == self.mincount and len(self.key_list[count]) == 0:
                self.mincount += 1

    def _miss(self, file):
        self.miss_count += 1
        if self.replacement_algo == 'LRU':
            while self.remain < file.size:  # 如果缓存满了
                if len(self.cache):  # 防止cache empty
                    self.remain += self.cache.popitem(last=False)[-1]  # pop出第一个item
                else:
                    return
        elif self.replacement_algo == 'LFU':
            while self.remain < file.size and len(self.key_list[self.mincount]):  # 如果缓存已经满
                temp_key, temp_val = self.key_list[self.mincount].popitem(last=False)
                # next(iter(self.key_list[self.mincount].items()))
                del self.cache[temp_key]
                del self.visited[temp_key]
                del self.key_list[self.mincount][temp_key]
                self.remain += temp_val
            if self.remain < file.size:
                return
            self.visited[file.fid] = 1
            self.key_list[1][file.fid] = file.size
        self.cache[file.fid] = file.size
        # count = self.visited[file.fid]
        # self.key_list[count + 1][file.fid] = None
        self.remain -= file.size

    def handle(self, file):  # 处理一次请求
        if file.fid in self.cache.keys():
            self._hit(file)
        else:
            self._miss(file)

    def hit_rate(self):
        # try:
        hit_rate = self.hit_count / (self.hit_count + self.miss_count + 0.001)
        # print("hit_rate:", hit_rate)
        return hit_rate
