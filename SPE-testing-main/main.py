# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 19:18:00 2022

@author: Harith
"""

import os
from Utils.read_coord import kml_coord
from Utils.sentinal_request import senti_api
from Utils.forest_cover import get_cover,green_cover_plot
from Utils.seques_forecast import plot_SEQ,cal_existing
from Utils.map_view import map_show
from Utils.tree_count import count_trees
from Utils.tree_count import tree_count
import webbrowser

file_path = input('Enter kml file path: ')
print(file_path)
#C:\Users\Harith\EngenuityAI\SPE\SPE-development\sentinal\gAMPOLA TEST SITE 2.kml
if os.path.exists(file_path):
    print('The file exists')

    with open(file_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

        #print(lines)
else:
    print('The specified file does NOT exist')



# getting polygon coordinates
poly_coord = kml_coord(file_path)
#print(poly_coord)

# show the map view
map_show(poly_coord)


tree_type = input('Enter the existing tree type: ')
#print(tree_type)
age_exist = input('Enter the age of the plantation: ')
age_exist = int(age_exist)
spacing = input('Enter the spacing between the trees in meters: ')
spacing = int(spacing)


img,resol = senti_api(poly_coord)
#print('resolution',resol)
#print(img.shape)
#print(img[:,:,2][40][10])

forest_area,forest_cover,green_pixel,green_cov,ndvi = get_cover(img,resol)
if spacing == 0:
    t_count = tree_count(tree_type, green_cov)
else:
    t_count = count_trees(resol,green_pixel,spacing)

seq = cal_existing(age_exist,t_count,tree_type)
seq_current = seq.item()
fig = green_cover_plot(ndvi,forest_cover,t_count,seq_current)

# CO2 forecasting
print("Forecasting for one tree type")
n_tree_type = input('Enter the new tree type to be planted: ')
n_tree = input('Enter the tree count: ')
n_tree = int(n_tree)
age_max = input('Enter the no of years ahead to forecast: ')
age_max = int(age_max)
plot_SEQ(n_tree_type,n_tree,age_max)

webbrowser.open("show_output.html",new=2)