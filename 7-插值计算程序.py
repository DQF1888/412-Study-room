import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.interpolate import splprep, splev
import numpy as np
import re
from scipy.interpolate import Rbf
from sympy import symbols, parse_expr


class App:
    def __init__(self, root, scale=0.85):
        self.root = root
        self.root.title("Excel Data Plotter")

        self.scale = scale

        # Excel Input area
        self.input_label = ttk.Label(root, text="插值EXCEL文件：")
        self.input_label.grid(row=0, column=0, sticky="w")

        self.input_entry = ttk.Entry(root, width=int(50 * self.scale))
        self.input_entry.grid(row=0, column=1)

        self.browse_button = ttk.Button(root, text="浏览", command=self.browse_excel_file)
        self.browse_button.grid(row=0, column=2)

        # TXT Input area
        self.txt_input_label = ttk.Label(root, text="参照点拟合曲线txt文件：")
        self.txt_input_label.grid(row=1, column=0, sticky="w")

        self.txt_input_entry = ttk.Entry(root, width=int(50 * self.scale))
        self.txt_input_entry.grid(row=1, column=1)

        self.txt_browse_button = ttk.Button(root, text="浏览", command=self.browse_txt_file)
        self.txt_browse_button.grid(row=1, column=2)

        # Plot area with increased plot size
        self.fig, self.ax = plt.subplots(figsize=(10 * self.scale, 8 * self.scale))
        self.canvas = FigureCanvasTkAgg(self.fig, self.root)
        self.canvas.get_tk_widget().grid(row=2, column=0, columnspan=3)

        # Setting up 4-quadrant coordinate system
        self.ax.axhline(0, color='black', lw=2)
        self.ax.axvline(0, color='black', lw=2)
        self.ax.set_xlim([-10, 10])
        self.ax.set_ylim([-10, 10])
        self.ax.set_aspect('equal', 'box')

        # New input fields below the plot
        self.ref_point_label = ttk.Label(root, text="参照点数：")
        self.ref_point_label.grid(row=3, column=0)
        self.ref_point_entry = ttk.Entry(root, width=int(10 * self.scale))
        self.ref_point_entry.grid(row=3, column=1)

        self.interp_point_label = ttk.Label(root, text="插值点数：")
        self.interp_point_label.grid(row=4, column=0)
        self.interp_point_entry = ttk.Entry(root, width=int(10 * self.scale))
        self.interp_point_entry.grid(row=4, column=1)

        self.coord_label = ttk.Label(root, text="编号1位置坐标（平面）：")
        self.coord_label.grid(row=5, column=0)
        self.coord_entry = ttk.Entry(root, width=int(20 * self.scale))
        self.coord_entry.grid(row=5, column=1)

        # New interpolation button on the right below the plot
        self.interp_button = ttk.Button(root, text="开始插值", command=self.start_interpolation)
        self.interp_button.grid(row=3, column=2, rowspan=3)

        # Beautify input fields and labels
        style = ttk.Style()
        style.configure('TLabel', font=('微软雅黑', 14 * int(self.scale)), background='grey')
        style.configure('TEntry', font=('微软雅黑', 14 * int(self.scale)))
        style.configure('TButton', font=('微软雅黑', 14 * int(self.scale)))

        # Add a button to show instructions
        self.instr_button = ttk.Button(root, text="显示说明", command=self.show_instructions)
        self.instr_button.grid(row=0, column=3)

        # 在其他Tkinter控件之后添加进度条
        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress.grid(row=6, column=0, columnspan=3)


    # (Methods for browsing and loading data are here)

    def show_instructions(self):
        instr_window = tk.Toplevel(self.root)
        instr_window.title("说明和使用方法")
        instr_text = scrolledtext.ScrolledText(instr_window, wrap=tk.WORD, width=100, height=25, font=("微软雅黑", 12))
        instr_text.pack(padx=10, pady=10)

        instructions = """
        *******************************************************************************************************************
        程序功能介绍：                                                                                   
        有限元计算中，为了满足不同计算需求，对有限元模型提出了要求。我们假设有两个不同网格尺寸的有限元模型A和B，
        模型A的计算结果是已知的，而模型B的边界和荷载条件依赖于模型A的结果数据，由于网格大小不同，模型A的数据无
        法与模型B进行一一映射，需要对模型A数据进行插值处理，才能满足映射关系。本程序在模型A数据曲线已知的情况下，
        依据模型A与模型B同一断面（以隧道为例，纵向距离等于0的断面）的平面坐标关系，借助Rbf插值算法，得到模型B的
        数据曲线。
        说明：此处数据曲线定义为隧道横、竖向坐标相同，纵向坐标变化的节点数据构成的曲线！
        *******************************************************************************************************************
        程序使用介绍：
        1. 点击“浏览”按钮选择存储模型A与模型B同一断面处所有节点坐标的EXCEL xlsx文件。当选择好EXCEL文件，点击文件
        管理器的“打开”按钮，程序下方的直角坐标系会读取EXCEL数据点，并以不同颜色的空心圆显示；
        2. 点击“浏览”按钮，选择存储模型A数据曲线的txt文件；
        3. 点击“开始插值”按钮，进行插值计算；下方会实时显示进度；
        4. 插值完成后，弹出弹窗提醒，表示插值已完成；
        5. 输出了存储模型B数据曲线的txt文件，以及模型B数据曲线的图像。
        *******************************************************************************************************************
        更多详细信息，请联系QQ:2093531610，或邮箱：2093531610@qq.com
        鸣谢：
        MYT YMQ LW ZYZ WZP YY ZTL CYZ ZKX LHJ YL TJF ZM WS WYB CXS WB
        特别鸣谢：
        LWJ HXM HWG 赵今麦
        """
        instr_text.insert(tk.INSERT, instructions)

    def browse_excel_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, filepath)
        self.load_and_plot_data(filepath)

    def browse_txt_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("TXT files", "*.txt")])
        self.txt_input_entry.delete(0, tk.END)
        self.txt_input_entry.insert(0, filepath)
        # Here you can add code to read the TXT file and do something with it
        

    def load_and_plot_data(self, filepath):
        # (Code for loading and plotting data is here)
        df1 = pd.read_excel(filepath, sheet_name=0)
        df2 = pd.read_excel(filepath, sheet_name=1)
        x1, y1 = df1['Y'], df1['Z']               ###$change
        x2, y2 = df2['X'], df2['Y']                ###$change
 
        self.ax.clear()

        # Resetting 4-quadrant coordinate system
        self.ax.axhline(0, color='black', lw=2)
        self.ax.axvline(0, color='black', lw=2)
        self.ax.set_xlim([-10, 10])
        self.ax.set_ylim([-10, 10])
        self.ax.set_aspect('equal', 'box')  # Set aspect ratio to be equal

        # Plotting data points from both sheets with empty circles
        self.ax.scatter(x1, y1, facecolors='none', edgecolors='green', s=100 * self.scale, label='Sheet 1')
        self.ax.scatter(x2, y2, facecolors='none', edgecolors='purple', s=50 * self.scale, label='Sheet 2')

        # Function to create a closed spline curve
        def closed_spline(x, y):
            tck, u = splprep([x, y], s=0, per=True)
            unew = np.linspace(0, 1, 100)
            out = splev(unew, tck)
            return out

        # Spline interpolation and plotting for both sheets
        out1 = closed_spline(x1, y1)
        out2 = closed_spline(x2, y2)
        self.ax.plot(out1[0], out1[1], '--', c='green', linewidth=0.5)
        self.ax.plot(out2[0], out2[1], '--', c='purple', linewidth=0.5)

        # Annotating points from the second sheet
        # Convert to polar coordinates and sort by angle
        r2 = np.sqrt(x2 ** 2 + y2 ** 2)
        theta2 = np.arctan2(y2, x2)
        
        sort_order = np.argsort(theta2)

        
        # Annotating points from both sheets
        # Convert to polar coordinates and sort by angle
        
        for x, y,color in [(x1, y1, 'green'), (x2, y2, 'red')]:
            r = np.sqrt(x ** 2 + y ** 2)
            theta = np.arctan2(y, x)
            sort_order = np.argsort(theta)
            for i, idx in enumerate(sort_order):
                xi, yi = x.iloc[idx], y.iloc[idx]
                if i == 0:  # Only annotate the first point after sorting by smallest angle
                    self.ax.text(xi, yi, str(i + 1), color=color, fontsize=12 * self.scale)

        self.ax.legend()
        self.ax.set_title("Scatter Plot of Data Points")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")

        self.canvas.draw()

        # Automatically populate the new input fields
        self.update_input_fields(x1, y1, x2, y2)
        self.green_points_x = x1.tolist()
        self.green_points_y = y1.tolist()
        self.purple_points_x = x2.tolist()
        self.purple_points_y = y2.tolist()
        #print(self.green_points_x)


    def update_input_fields(self, x1, y1, x2, y2):
        # (Code for updating input fields is here)
        ref_point_count = len(x1)
        interp_point_count = len(x2)

        theta1 = np.arctan2(y1, x1)
        theta2 = np.arctan2(y2, x2)
        
        min_angle_index1 = np.argsort(theta1)[0]
        min_angle_index2 = np.argsort(theta2)[0]
        
        coord_1 = f"({x1.iloc[min_angle_index1]}, {y1.iloc[min_angle_index1]})"
        coord_2 = f"({x2.iloc[min_angle_index2]}, {y2.iloc[min_angle_index2]})"
        
        self.ref_point_entry.delete(0, tk.END)
        self.ref_point_entry.insert(0, str(ref_point_count))
        
        self.interp_point_entry.delete(0, tk.END)
        self.interp_point_entry.insert(0, str(interp_point_count))
        
        self.coord_entry.delete(0, tk.END)
        self.coord_entry.insert(0, coord_1)

    def start_interpolation(self):
        # Load TXT Data
        txt_filepath = self.txt_input_entry.get()
        if txt_filepath:  # Only proceed if the filepath is not empty
            self.load_txt_data(txt_filepath)
        
        # Your existing code for interpolation logic

        self.chazhi()
        self.export_polynomial_txt()
        self.read_polynomial_from_file()

        self.progress["value"] = 0
        self.root.update_idletasks()

        total_polynomials = len(self.polynomials)
        step_value = 100 / total_polynomials  # 每完成一个多项式应该增加的进度量


        for i in range(0, len(self.polynomials), 2):
            self.plot_polynomials(self.polynomials[i:i+2],figure_index=1+i//2,step_value=step_value)

        messagebox.showinfo("信息", "插值完成！已输出txt文件及插值曲线图像！")



    def load_txt_data(self,filepath):
        green_points = []  # List to store coefficients for all green points
        var_dict = {}  # Dictionary to store coefficients for each variable (X, Z) for a single green point
        start_extracting = False  # Flag to indicate whether to start extracting polynomial from the next line
        
        with open(filepath, 'r', encoding='GBK') as f:  # Open the file using GBK encoding
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if '拟合公式' in line:  # Lines containing '拟合公式' indicate that the next line will have the polynomial
                    var = line.split('_')[0]  # Extract the variable (X, Y, Z)
                    start_extracting = True  # Set the flag to start extracting polynomial from the next line
                    continue
                
                if start_extracting:  # If the flag is set, start extracting polynomial
                    # Reset the flag
                    start_extracting = False
                    
                    # Use regular expression to find all terms like "-0.47984281490189434338233809285156894475221633911133x^0"
                    terms = re.findall(r'[-+]?[\d.]+x\^\d+', line)
                    
                    coefficients = []  # Initialize as empty list
                    for term in terms:
                        coef_str, _, power_str = term.partition('x^')
                        coef = float(coef_str) if coef_str else 1.0  # Take the first element as coefficient
                        power = int(power_str)
                        # Extend the list to make sure there is enough space
                        while len(coefficients) <= power:
                            coefficients.append(0.0)
                        coefficients[power] = coef  # Assign coefficient to the corresponding power
                    
                    # Assign coefficients to the corresponding variable
                    var_dict[var] = coefficients
                    
                    # If both X and Z coefficients are extracted, append them to green_points
                    if 'Y' in var_dict and 'Z' in var_dict:                         ###$change
                        green_points.append(var_dict.copy())
                        var_dict.clear()
        print(green_points)

        self.green_points_coef_x = [point['Y'] for point in green_points]                  ###$change
        self.green_points_coef_z = [point['Z'] for point in green_points]                  ###$change
        #print(self.green_points_coef_x)
        #print("Extracted coefficients for each green point:", green_points)

    def chazhi(self):
        green_points_x = self.green_points_x
        green_points_y = self.green_points_y
        green_points_coef_x = self.green_points_coef_x
        green_points_coef_z = self.green_points_coef_z

        # Dummy data for purple points (interpolation points)
        purple_points_x = self.purple_points_x
        purple_points_y = self.purple_points_y

        green_points_coef_x = [{str(i): val for i, val in enumerate(lst)} for lst in green_points_coef_x]
        green_points_coef_z = [{str(i): val for i, val in enumerate(lst)} for lst in green_points_coef_z]


        # Find the maximum number of terms in the polynomials
        max_terms_x = max(len(coef) for coef in green_points_coef_x)
        max_terms_z = max(len(coef) for coef in green_points_coef_z)

        # Initialize RBF objects for each term
        rbf_objects_x = []
        rbf_objects_z = []
        for i in range(max_terms_x):
            term_values = [point.get(str(i), 0) for point in green_points_coef_x]
            rbf_objects_x.append(Rbf(green_points_x, green_points_y, term_values, function='gaussian'))
            
        for i in range(max_terms_z):
            term_values = [point.get(str(i), 0) for point in green_points_coef_z]
            rbf_objects_z.append(Rbf(green_points_x, green_points_y, term_values, function='gaussian'))

        # Perform interpolation for purple points
        purple_points_coef_x = []
        purple_points_coef_z = []
        for x, y in zip(purple_points_x, purple_points_y):
            coef_x = {str(i): rbf(x, y) for i, rbf in enumerate(rbf_objects_x)}
            coef_z = {str(i): rbf(x, y) for i, rbf in enumerate(rbf_objects_z)}
            purple_points_coef_x.append(coef_x)
            purple_points_coef_z.append(coef_z)
        
        self.purple_points_coef_x=purple_points_coef_x
        self.purple_points_coef_z=purple_points_coef_z


    def generate_polynomial_string(self,coeff_dict):
        
        # Initialize an empty string to hold the polynomial
        polynomial_str = ""

        # Loop through each item in the dictionary to construct the polynomial string
        for exponent, coeff in coeff_dict.items():
            # Format the coefficient and exponent
            coeff_str = f"{coeff:.50f}"
            # Construct each term of the polynomial
            term = f"{coeff_str}x^{exponent}"
            # Add to the polynomial string, taking care of the sign
            if polynomial_str:
                if coeff >= 0:
                    polynomial_str += " + "
                else:
                    polynomial_str += " - "
                    term = term[1:]  # Remove the negative sign from the term as it's already added
            polynomial_str += term

        return polynomial_str
    def export_polynomial_txt(self):
        with open('fixed-chazhi-function.txt','w',encoding='utf-8') as f:
            for coeff_dict_x, coeff_dict_z in zip(self.purple_points_coef_x,self.purple_points_coef_z):
                f.write("Y_Displacement 拟合公式:"+'\n'+str(self.generate_polynomial_string(coeff_dict_x))+'\n\n')            ###$change
                f.write("Z_Displacement 拟合公式:"+'\n'+str(self.generate_polynomial_string(coeff_dict_z))+'\n\n')                ###$change

            f.close()


    def read_polynomial_from_file(self):
        polynomials = []
        with open('fixed-chazhi-function.txt', 'r', encoding='utf-8') as f:
            for line in f:
                if 'x^0' in line:  # Assuming the polynomial line contains 'x^0'
                    # Replace '^' with '**' to make it compatible with sympy
                    polynomial_str = line.replace('^', '**').replace('x', '*x').strip()
                    polynomials.append(polynomial_str)
        self.polynomials=polynomials
        return self.polynomials
    
    def plot_polynomials(self, polynomial_strs, step_value,x_start=0, x_end=60, num_points=500, figure_index=0):
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体为黑体
        plt.rcParams['axes.unicode_minus'] = False
        x = symbols('x')
        plt.figure(figsize=(5, 3))
        
        for i, polynomial_str in enumerate(polynomial_strs):
            polynomial_expr = parse_expr(polynomial_str)
            x_values = np.linspace(x_start, x_end, num_points)
            y_values = [float(polynomial_expr.subs(x, val)) for val in x_values]
            
            plt.plot(x_values, y_values, label=f'位移插值曲线 {i+1}')

        
        plt.xlabel('隧道纵向距离/m')
        plt.ylabel('位移值/mm')
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'figure_{figure_index}.png')
        plt.close()

        self.progress["value"] += step_value * len(polynomial_strs)
        self.root.update_idletasks()

    


if __name__ == "__main__":
    scale = 0.8
    root = tk.Tk()
    app = App(root, scale)
    root.mainloop()
