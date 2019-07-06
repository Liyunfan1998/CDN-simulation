from collections import OrderedDict

from abc import ABCMeta, abstractmethod


class Server:  # 服务器(cache)
    __metaclass__ = ABCMeta

    def __init__(self, space, replacement_algo):
        self.space = space  # cache大小
        self.remain = space  # cache剩余空间
        self.cache = OrderedDict()  # OrderDict() 模拟cache LRU方法
        self.hit_count = 0  # 命中次数
        self.miss_count = 0  # 未命中次数
        self.replacement_algo = self.LRU  # By Default
        self.set_replacement_algo(replacement_algo)

    def _hit(self, key):
        self.hit_count += 1
        self.cache.move_to_end(key)

    def _miss(self, file):
        self.miss_count += 1
        while self.remain < file.size:
            self.remain += self.cache.popitem(last=False)[-1]  # pop出第一个item
        self.cache[file.fid] = file.size
        self.remain -= file.size

    def handle(self, file):  # 处理一次请求
        if file.fid in self.cache.keys():
            self._hit(file.fid)
        else:
            self._miss(file)

    def hit_rate(self):
        try:
            return self.hit_count / (self.hit_count + self.miss_count)
        except:
            return "Server has not been requested yet!"

    def reorganize_space(self):
        """
        reorganize the priority queue
        at the end of every time window
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def set_replacement_algo(self, replacement_algo):
        self.replacement_algo = replacement_algo
        raise NotImplementedError

    def LRU(self):
        raise NotImplementedError

    def LFU(self):
        raise NotImplementedError

    def GDSF(self):
        raise NotImplementedError

    def LHD(self):
        raise NotImplementedError

    def DeepCache(self):
        raise NotImplementedError

    def learn_attack_seq(self):
        raise NotImplementedError
