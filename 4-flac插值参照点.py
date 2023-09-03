# -*- coding: utf-8 -*-

import itasca as it
import math
import csv
it.command("python-reset-state false")


def shell_disp():
    node_=[]
    for shell_node in it.gridpoint.list():
        if shell_node.in_group('ti'):
            if shell_node.pos()[0]==-30:
                node_.append(shell_node.pos())
                
    
    unique_vec_list = []
    [unique_vec_list.append(vec) for vec in node_ if vec not in unique_vec_list]

    cylindrical_coords = []

    
    for idx, (x, y, z) in enumerate(unique_vec_list):
        r = math.sqrt((y-0)**2 + (z-7.89)**2)
        theta = math.atan2((z-7.89), (y-0))
        cylindrical_coords.append((r, theta, x, idx))

    cylindrical_coords.sort(key=lambda coord: coord[1])

    sorted_cartesian_coords = [unique_vec_list[coord[3]] for coord in cylindrical_coords]
    
    print(sorted_cartesian_coords)


    data = sorted_cartesian_coords


    csv_file_path =r 'C:\Users\CYZ\Desktop\flac001\coordinates-flac.csv'


    with open(csv_file_path, 'w') as csvfile:
        csv_writer = csv.writer(csvfile)

        csv_writer.writerow(["X", "Y", "Z"])

        for row in data:
            csv_writer.writerow(row)
    print('ok')

if __name__ == "__main__":
    shell_disp()  