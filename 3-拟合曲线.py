# -*- coding: utf-8 -*-
"""
Created on Sat Aug 12 12:14:58 2023

@author: 86187
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 设置Matplotlib使用微软雅黑字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 读取Excel文件
xls_combined = pd.ExcelFile('combined.xlsx')
sheet_names_combined = xls_combined.sheet_names

# 定义拟合函数
def fit_func(x, *params):
    p = np.poly1d(params)  # 此处不再需要逆转参数，因为我们在记录时已经处理过了
    return p(x)

# 散点和实线的样式设置
scatter_colors = ['red', 'green', 'blue']
scatter_size = 50
line_colors = ['darkred', 'darkgreen', 'darkblue']
line_width = 1.5

# 打开一个新的TXT文件以写入拟合公式的参数
with open("fitted_equations.txt", "w") as file:

    # 对每个工作表绘制图形，并保存为SVG格式
    for idx, sheet_name in enumerate(sheet_names_combined):
        df = pd.read_excel(xls_combined, sheet_name=sheet_name)
        x_data = np.arange(len(df))

        fig, ax = plt.subplots(figsize=(10, 5))

        for j, col in enumerate(['X_Displacement', 'Y_Displacement', 'Z_Displacement']):
            y_data = df[col].apply(lambda x: float(x)).values
            params = np.polyfit(x_data, y_data, 12)                                  ###$change
            
            # 使用更密集的x值生成圆滑的曲线
            x_smooth = np.linspace(x_data.min(), x_data.max(), 500)
            y_fit = fit_func(x_smooth, *params)

            ax.scatter(x_data, y_data, marker='.', color=scatter_colors[j], s=scatter_size, label=f"{col}")
            ax.plot(x_smooth, y_fit, color=line_colors[j], linewidth=line_width, label=f"{col} (拟合曲线)")

            # 将拟合公式的参数写入TXT文件
            equation_terms = [f"{p:.30f}x^{i}" for i, p in enumerate(reversed(params))]                   ###$change
            equation_str = " + ".join(equation_terms)
            file.write(f"{col} 拟合公式:\n")
            file.write(equation_str + '\n\n')  # 加入空行使得每个公式之间有间隔 

        ax.legend()
        plt.tight_layout()
        plt.show()
        fig.savefig(f"plot_corrected_{idx+1}.svg", format='svg')
        plt.close(fig)





