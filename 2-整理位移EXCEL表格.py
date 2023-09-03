# -*- coding: utf-8 -*-
"""
Created on Sat Aug 12 11:53:52 2023

@author: 86187
"""

import pandas as pd

# 初始化一个新的 Excel writer
with pd.ExcelWriter('combined.xlsx', engine='openpyxl') as writer:
    
    # 循环处理每个 csv 文件
    for i in range(1, 27): # 假设文件名的数字是从 1 到 3
        csv_filename = f"shell_disp_{i}.csv"
        
        try:
            # 读取 CSV 文件中的前三列，不使用 header，这样我们可以保留原始数据
            df = pd.read_csv(csv_filename, usecols=[0, 1, 2], header=None)
            
            # 设置列名
            df.columns = ['X_Displacement', 'Y_Displacement', 'Z_Displacement']
            
            # 将数据写入新的 Excel 工作表中
            df.to_excel(writer, sheet_name=csv_filename[:-4], index=False)
            print(f"Processed {csv_filename} with {df.shape[0]} rows of data.")

        except Exception as e:
            print(f"Error processing file {csv_filename}: {e}")

print("Excel file created successfully!")

