from collections import OrderedDict, defaultdict

from abc import ABCMeta, abstractmethod
from LHD import LHD


class Server:  # 服务器(cache)
    __metaclass__ = ABCMeta

    def __init__(self, space, replacement_algo='LRU'):
        self.space = space  # cache大小
        self.remain = space  # cache剩余空间
        self.hit_count, self.miss_count = 0, 0
        self.hit_count_ignore_attack, self.miss_count_ignore_attack = 0, 0
        self.replacement_algo = replacement_algo
        self.clock = 0  # LHD 当前时刻
        if self.replacement_algo == 'LRU':
            self.cache = OrderedDict()  # OrderDict() 模拟cache LRU方法
        elif self.replacement_algo == 'LFU':
            self.mincount = 0
            self.cache = {}
            self.visited = {}
            # 默认字典嵌套一个有序字典，外层字典的键是访问次数，有序字典会根据放入元素的先后顺序进行排序
            self.key_list = defaultdict(OrderedDict)
        elif self.replacement_algo == 'LHD':
            self.lhd = LHD(base_size=32)
            self.cache = {}

    def _hit(self, file, not_attack=True):
        self.hit_count += 1
        if not_attack:
            self.hit_count_ignore_attack += 1
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
        elif self.replacement_algo == 'LHD':
            file_size = file.size
            file_age = self.clock - self.cache[file.fid][1]
            self.lhd.add_hit_age(file_size, file_age)
            # 算是重新的一个记录
            self.cache[file.fid] = (file_size, self.clock)

    def _miss(self, file, not_attack=True):
        self.miss_count += 1
        if not_attack:
            self.miss_count_ignore_attack += 1
        if self.replacement_algo == 'LRU':
            while self.remain < file.size:  # 如果缓存满了
                if len(self.cache):  # 防止cache empty
                    # pop出第一个item
                    self.remain += self.cache.popitem(last=False)[-1]
                else:
                    return
        elif self.replacement_algo == 'LFU':
            # 如果缓存已经满
            while self.remain < file.size and len(self.key_list[self.mincount]):
                temp_key, temp_val = self.key_list[self.mincount].popitem(
                    last=False)
                # next(iter(self.key_list[self.mincount].items()))
                del self.cache[temp_key]
                del self.visited[temp_key]
                del self.key_list[self.mincount][temp_key]
                self.remain += temp_val
            if self.remain < file.size:
                return
            self.visited[file.fid] = 1
            self.key_list[1][file.fid] = file.size
        elif self.replacement_algo == 'LHD':
            # 文件太大，缓存不下
            if self.space < file.size:
                return
            # 缓存得下 evict
            while self.remain < file.size:
                # evict LHD 最小的
                # 这里采用的是动态计算的方法，没有查表
                # 从上面的条件，可以知道 del_fid == -1 的情况不会发生
                del_fid = -1
                del_size = 0
                del_age = 0
                del_lhd = float('inf')
                for fid in self.cache:
                    size = self.cache[fid][0]
                    age = self.clock - self.cache[fid][1]
                    lhd = self.lhd.get_lhd(size, age)
                    if lhd < del_lhd:
                        del_fid = fid
                        del_size = size
                        del_age = age
                        del_lhd = lhd
                # 记录一次 miss_age，对应红盒子
                self.lhd.add_miss_age(del_size, del_age)
                # 腾出空间
                self.remain += del_size
                del self.cache[del_fid]
        # admit
        if self.replacement_algo == 'LHD':
            self.cache[file.fid] = (file.size, self.clock)
        else:
            self.cache[file.fid] = file.size
        # count = self.visited[file.fid]
        # self.key_list[count + 1][file.fid] = None
        self.remain -= file.size

    def handle(self, file, not_attack=True):  # 处理一次请求
        cached = file.fid in self.cache.keys()
        if cached:
            self._hit(file, not_attack)
        else:
            self._miss(file, not_attack)
        return cached

    def hit_rate(self, ignore_attack=False):
        if ignore_attack:
            hit_rate = self.hit_count_ignore_attack / (
                        self.hit_count_ignore_attack + self.miss_count_ignore_attack + 0.001)
        else:
            hit_rate = self.hit_count / (self.hit_count + self.miss_count + 0.001)
        # print("hit_rate:", hit_rate)
        return hit_rate
