# -*- coding: utf-8 -*-
"""
Created on Sat Aug 12 15:20:37 2023

@author: 86187
"""

from abaqus import *
from abaqusConstants import *
import math
import re


def zhuhuan(formula):
    # 将负号的数字加上括号
    corrected_formula_with_brackets = re.sub(r'(-\d+\.\d+)x', r'(\1)*x', formula)
    
    # 在所有数字和x之间加上"*"
    formula_with_multiplication = re.sub(r'(\d+\.\d+)x', r'\1*x', corrected_formula_with_brackets)
    
    # 将所有的x替换为Z
    formula_with_Z = formula_with_multiplication.replace('x', 'Z')
    
    # 将所有的"^"替换为"**"
    final_formula = formula_with_Z.replace('^', '**')
    
    
    return final_formula


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

a = mdb.models['Model-1'].rootAssembly

n1 = a.instances['model-mesh-1-1'].nodes

mdb.models['Model-1'].SmoothStepAmplitude(name='Amp-2', timeSpan=STEP, data=((
    0.0, 0.0), (1.0, 3.0)))

count=0
for n in sorted_cartesian_coords:
    count+=1
    
    with open(r'C:\Users\CYZ\Desktop\flac001\fixed-chazhi-function.txt', 'r',) as file:
        lines = file.readlines()
        
    x_formula = lines[6*count-5].strip()
    y_formula = lines[6*count-2].strip()
    
    

    
    mdb.models['Model-1'].ExpressionField(name='X-weiyi-'+str(count), localCsys=None, 
        description='', expression=zhuhuan(x_formula))
    
    mdb.models['Model-1'].ExpressionField(name='Y-weiyi-'+str(count), localCsys=None, 
        description='', expression=zhuhuan(y_formula))
    

    

    node_select=n1.getByBoundingCylinder((n[0],n[1],-0.5),(n[0],n[1],90.5),0.001)
    region = a.Set(nodes=node_select, name='Set-jiedian-'+str(count))
    
    mdb.models['Model-1'].DisplacementBC(name='X-'+str(count), createStepName='Step-1', 
        region=region, u1=1.0, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, 
        amplitude='Amp-2', fixed=OFF, distributionType=FIELD, 
        fieldName='X-weiyi-'+str(count), localCsys=None)
    
    mdb.models['Model-1'].DisplacementBC(name='Y-'+str(count), createStepName='Step-1', 
        region=region, u1=UNSET, u2=1.0, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, 
        amplitude='Amp-2', fixed=OFF, distributionType=FIELD, 
        fieldName='Y-weiyi-'+str(count), localCsys=None)
    


    
