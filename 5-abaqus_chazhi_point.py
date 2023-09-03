# -*- coding: utf-8 -*-
from abaqus import *
from abaqusConstants import *
import csv
import math


# 获取模型
myModel = mdb.models[mdb.models.keys()[0]]

# 获取集合
nset = myModel.rootAssembly.sets['Set-hezai']

# 初始化空列表用于存储坐标
coords = []

# 遍历集合中的每个节点
for node in nset.nodes:
    # 添加节点坐标到列表
    coords.append(node.coordinates)
    

cylindrical_coords=[]
for idx, (x, y, z) in enumerate(coords):
    r = math.sqrt(x**2 + y**2)
    theta = math.atan2(y, x)
    cylindrical_coords.append((r, theta, z, idx))

cylindrical_coords.sort(key=lambda coord: coord[1])

sorted_cartesian_coords = [coords[coord[3]] for coord in cylindrical_coords]

# 完整的坐标数据列表
data = sorted_cartesian_coords

# 定义CSV文件路径
csv_file_path = 'coordinates-abaqus.csv'

# 将数据写入CSV文件
with open(csv_file_path, 'w') as csvfile:
    csv_writer = csv.writer(csvfile)
    # 写入表头
    csv_writer.writerow(["X", "Y", "Z"])
    # 写入数据
    for row in data:
        csv_writer.writerow(row)
print('ok')
