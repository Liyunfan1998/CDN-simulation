# -*- coding: utf-8 -*-
from pyspark import SparkContext, SparkConf
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql import SQLContext
from pyspark import SparkContext
import matplotlib.pyplot as plt
import numpy as np
import sys, getopt

import findspark

findspark.init()
from pyspark.sql import functions as F
from pyspark.sql import SparkSession


def spark_init():
    spark = SparkSession \
        .builder \
        .appName("network_trace_analysis") \
        .getOrCreate()
    spark.conf.set("spark.executor.memory", "30g")
    spark.conf.set('spark.driver.memory', '30g')
    sc = SparkContext.getOrCreate()
    return spark, sc


# filePath = './MSR-Cambridge 2/web_3.csv'
# data = sc.textFile(filePath, 4).map(lambda l: l.split(','))
# data = data.map(lambda l: [l[0]] + l[3:6])
# # data.take(1)
# schema = ['Timestamp', 'Type', 'Offset', 'Size']
# df = spark.createDataFrame(data, schema)

def map_by_popularity(real_trace):
    df = pd.read_csv(real_trace, header=None)
    df.columns = ['Timestamp', 'Hostname', 'DiskNumber', 'Type', 'Offset', 'Size', 'ResponseTime']
    del df['Hostname'], df['DiskNumber']
    df2 = pd.DataFrame(df['Offset'], df['Size']).reset_index()
    file_set = set(df.Offset)
    # len(file_set)
    file_dict = {}
    for i in range(len(df)):
        file_dict[df.loc[i].Offset] = df.loc[i].Size


def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('test.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    print('输入的文件为：', inputfile)
    print('输出的文件为：', outputfile)


if __name__ == "__main__":
    main(sys.argv[1:])
