# -*- coding: utf-8 -*-
import pandas as pd

# 读取两个CSV文件
abaqus_df = pd.read_csv('coordinates-abaqus.csv')
flac_df = pd.read_csv('coordinates-flac.csv')

# 从coordinates-abaqus.csv中删除Z列
abaqus_df.drop(['Z'], axis=1, inplace=True)               ###$change

# 从coordinates-flac.csv中删除X列
flac_df.drop(['X'], axis=1, inplace=True)                    ###$change

# 清除两个数据表中的空单元格
abaqus_df.dropna(inplace=True)
flac_df.dropna(inplace=True)

# 创建一个新的Excel文件并将两个数据表保存到其中
with pd.ExcelWriter('combined_coordinates.xlsx') as writer:
    flac_df.to_excel(writer, sheet_name='coordinates-flac', index=False)
    abaqus_df.to_excel(writer, sheet_name='coordinates-abaqus', index=False)
