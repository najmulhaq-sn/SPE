#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import os


# make file path platform independant
file_path = os.path.join('Data', 'CF - New.csv')
data_CFNew = pd.read_csv(file_path)


def count_trees(res,green_pixel,spacing):
    
    # Count no of trees per pixel
    tree_per_pixel = (res*res)/(spacing*spacing)
    tree_count = round(green_pixel*tree_per_pixel)
    
    # print('Estimated No of Trees: ',tree_count)
    return tree_count

"""
def tree_count(Species, green_cover, Age):
    
    #extract maturity age from table
    Mat_age = data_CFNew["Maturity Age"][data_CFNew['Species - Common Name'] == Species].item()
    
    #extract crown area from table
    Crown_area = data_CFNew["Crown Area"][data_CFNew['Species - Common Name'] == Species].item()
    
    #crown area for user input - age
    cr_area = (Crown_area/Mat_age)*Age
    #calculate number of trees using green cover and crown area
    trees_no = round(green_cover/cr_area)
    return trees_no
"""

def tree_count(Species, green_cover):
    
    #extract crown area for matured trees from table
    Crown_area = data_CFNew["Crown Area"][data_CFNew['Species - Common Name'] == Species].item()
    
    #calculate number of trees using green cover and crown area
    trees_no = round(green_cover/Crown_area)
    return trees_no