# -*- coding: utf-8 -*-
"""
Created on Sat Aug 12 10:47:52 2023

@author: 86187
"""

import itasca as it
import math
import csv
it.command("python-reset-state false")


def shell_disp(y_distance,y_zone_size,csv_path):
    node_=[]
    for shell_node in it.gridpoint.list():
        if shell_node.in_group('ti'):
            if shell_node.pos()[0]==-30:
                node_.append(shell_node.pos())
                
    
    unique_vec_list = []
    [unique_vec_list.append(vec) for vec in node_ if vec not in unique_vec_list]

    cylindrical_coords = []

    
    for idx, (x, y, z) in enumerate(unique_vec_list):
        r = math.sqrt((y-0)**2 + (z-7.55)**2)
        theta = math.atan2((z-7.55), (y-0))
        cylindrical_coords.append((r, theta, x, idx))

    cylindrical_coords.sort(key=lambda coord: coord[1])

    sorted_cartesian_coords = [unique_vec_list[coord[3]] for coord in cylindrical_coords]
    
    print(sorted_cartesian_coords)

    
    count=0

    for shell_ in sorted_cartesian_coords:
        count+=1
        disp=[]
        for num in range(61):
            position_vec=[num-30,shell_[1],shell_[2]]

            node_object=it.gridpoint.near(tuple(position_vec))
            disp.append(node_object.disp())
            
        name='shell_disp_'+str(count)+'.csv'
            
        csv_path=r'C:\Users\admin\Desktop\EXCEL'+'\\'+name

       
        with open(csv_path, 'wb') as csvfile:  
            writer = csv.writer(csvfile)
            for row in disp:
                writer.writerow(row)

if __name__ == "__main__":
    shell_disp(y_distance=10,y_zone_size=1,csv_path='shell_disp.csv')  


