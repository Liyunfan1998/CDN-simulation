import numpy as np
import matplotlib.pyplot as plt
from random import randint
from utils import *

class LHD:
    def __init__(self, base_size=128):
        self.base_size = base_size
        self.hit_ages = {}
        self.miss_ages = {}
        self.size_total = {}

    def get_lhd(self, size, age):
        future_hit = self.get_future_hit(size, age)
        total= self.get_size_total(size)
        if total:
            future_hit_prob = future_hit/self.get_size_total(size)
        else:
            future_hit_prob = 0
        remain_age = self.get_age_expectation(size, age) - age
        if remain_age:
            return future_hit_prob/(size*remain_age)
        return 0

    def get_size_group(self, size):
        if size < self.base_size:
            return 0
        group_index = 1
        size = size//self.base_size
        while size > 1:
            group_index += 1
            size = size//2
        return group_index

    def get_size_total(self, size):
        group_index = self.get_size_group(size)
        if group_index in self.size_total:
            return self.size_total[group_index]
        return 0

    def get_future_hit(self, size, age):
        group_index = self.get_size_group(size)
        if group_index not in self.hit_ages:
            return 0
        hist = self.hit_ages[group_index]
        right = 0
        for i in hist:
            if i > age:
                right += hist[i]
        return right

    def get_future_miss(self, size, age):
        group_index = self.get_size_group(size)
        if group_index not in self.miss_ages:
            return 0
        hist = self.miss_ages[group_index]
        right = 0
        for i in hist:
            if i > age:
                right += hist[i]
        return right

    def get_age_expectation(self, size, age=0):
        group_index = self.get_size_group(size)
        total_num = 0
        total_age = 0.0
        if group_index in self.hit_ages:
            hist = self.hit_ages[group_index]
            for i in hist:
                if i > age:
                    total_num += hist[i]
                    total_age += i*hist[i]
        if group_index in self.miss_ages:
            hist = self.miss_ages[group_index]
            for i in hist:
                if i > age:
                    total_num += hist[i]
                    total_age += i*hist[i]
        if total_num == 0:
            # live to this moment
            return age
        else:
            return total_age/total_num

    def add_hit_age(self, size, age):
        group_index = self.get_size_group(size)
        if group_index not in self.size_total:
            self.size_total[group_index] = 1
        else:
            self.size_total[group_index] += 1

        if group_index not in self.hit_ages:
            self.hit_ages[group_index] = {}

        if age in self.hit_ages[group_index]:
            self.hit_ages[group_index][age] += 1
        else:
            self.hit_ages[group_index][age] = 1

    def add_miss_age(self, size, age):
        group_index = self.get_size_group(size)
        if group_index not in self.size_total:
            self.size_total[group_index] = 1
        else:
            self.size_total[group_index] += 1

        if group_index not in self.miss_ages:
            self.miss_ages[group_index] = {}

        if age in self.miss_ages[group_index]:
            self.miss_ages[group_index][age] += 1
        else:
            self.miss_ages[group_index][age] = 1

    def show(self, size, floor=0, ceil=150):
        group_index = self.get_size_group(size)
        hit_histo = {}
        miss_histo = {}
        if group_index in self.hit_ages:
            hit_histo = self.hit_ages[group_index]
        if group_index in self.miss_ages:
            miss_histo = self.miss_ages[group_index]

        x = []
        hit_num = []
        miss_num = []
        lhd_num = []
        lhd_prob = []
        lhd_age = []
        for age in range(floor, ceil):
            if age in hit_histo:
                hit_num.append(hit_histo[age])
            else:
                hit_num.append(0)
            if age in miss_histo:
                miss_num.append(miss_histo[age])
            else:
                miss_num.append(0)
            x.append(age)
            lhd_num.append(self.get_lhd(129, age))
            lhd_prob.append(self.get_future_hit(
                size, age)/self.get_size_total(size))
            lhd_age.append(self.get_age_expectation(size,age)-age)
        print(lhd_num)
        # plt.plot(x, hit_num, color='g', label='hit')
        # plt.plot(x, miss_num, color='deepskyblue', label='miss')
        plt.plot(x, lhd_num, label='lhd')
        # plt.plot(x, lhd_prob, label='prob')
        # plt.plot(x, lhd_age, label='age')
        plt.legend()
        plt.show()
        plt.clf()
        plt.plot(x, hit_num, color='g', label='hit')
        plt.plot(x, miss_num, color='deepskyblue', label='miss')
        plt.show()


# lhd = LHD(base_size=128)

# norm = np.random.normal(10, 20, size=100000)
# for i in norm:
#     if i > 0:
#         lhd.add_hit_age(129, int(i))
# norm = np.random.normal(20, 25, size=30000)
# for i in norm:
#     if i > 0:
#         lhd.add_miss_age(129, int(i))

# lhd.show(129)
# print(lhd.get_age_expectation(129, 0))
