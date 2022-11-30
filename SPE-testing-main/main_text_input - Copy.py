# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 19:18:00 2022

@author: Harith
updated: Antony
"""

import os
import sys
import numpy as np
from Utils.read_coord import kml_coord
from Utils.sentinal_request import senti_api
from Utils.forest_cover import get_cover,green_cover_plot, green_cover_plot_smooth
from Utils.carbon_seq_cal.seques_forecast import plot_SEQ,cal_existing
from Utils.map_view import map_show
from Utils.tree_count import count_trees
from Utils.tree_count import tree_count
import webbrowser
from Utils import tree_models as tree_model
from Utils.carbon_seq_cal import def_allometric_AGB_multi_model as allometric_cal
from PIL import Image, ImageFilter


############################################################
#               Read and parse input from text file        #
############################################################
if os.path.isfile(sys.argv[1]):
    lines = []
    with open(sys.argv[1], 'r', encoding='UTF-8') as file:
        lines = (line.rstrip() for line in file) 
        lines = list(line for line in lines if (line and line[0] != '#') )
        # print(lines)
else:
    print('File does not appear to exist.')
    sys.exit()

# Assign inputs  - Need to put to a CSV
kml_file_name = lines[0].split(":")[1].strip()
file_path = os.path.join(os.getcwd(), 'test_kml_files', kml_file_name )
tree_type = lines[1].split(":")[1].strip()
age_exist = int(lines[2].split(":")[1].strip())
lo_thresh = float(lines[3].split(":")[1].strip())
up_thresh = float(lines[4].split(":")[1].strip())
space_availability = lines[5].split(":")[1].strip()
spacing_parallel = float(lines[6].split(":")[1].strip())
spacing_along = float(lines[7].split(":")[1].strip())
species_type = lines[8].split(":")[1].strip()
region_type = lines[9].split(":")[1].strip()
annual_rainfall = float(lines[10].split(":")[1].strip())
DBH_cm = float(lines[11].split(":")[1].strip())
Height_cm = float(lines[12].split(":")[1].strip())

NDVI_bounds = tree_model.NDVI_threasholds(lo_thresh, up_thresh)
tree_land_spec = tree_model.tree_geo_specifications(    tree_model.species_category[species_type],
                                                        tree_model.region_type[region_type],
                                                        annual_rainfall,
                                                        DBH_cm,
                                                        Height_cm
                                                    ) 


############################################################
#            Read the KML and plot the KML                 #
############################################################
print("The KML file path:",file_path, end="")
if os.path.exists(file_path):
    print(' Exists')
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
else:
    print(' The specified file does NOT exist')

# getting polygon coordinates
poly_coord = kml_coord(file_path)

# show the map view
map_show(poly_coord)

print('***********************************************************')
print('** Scenario 2: Estimation for Existing land with plants  **')
print('***********************************************************')

############################################################
#     Read the KML from saved directory if possible        #
############################################################
# this lookup may be turned-off after testing
# better to add a date tag to the saved file name; 
# https://stackoverflow.com/questions/28439701/how-to-save-and-load-numpy-array-data-properly
kml_file_name_no_ext = kml_file_name.split(".")[0]
dat_file_name = kml_file_name_no_ext + '.npy'
file_path_to_sat_img = os.path.join( os.getcwd(), 'kml_to_ndarray', dat_file_name )

img = None
print(file_path_to_sat_img)
if os.path.exists(file_path_to_sat_img):
    print('Sat ndarray image exist already')
    # img = np.fromfile(file_path_to_sat_img, dtype=float)
    img = np.load(file_path_to_sat_img)
    img,resol = senti_api(poly_coord)

else:
    print("NeW KML file uploaded; ping to API")        
    img,resol = senti_api(poly_coord)
    # img.tofile(file_path_to_sat_img)
    np.save(file_path_to_sat_img, img) 

# img,resol = senti_api(poly_coord)
#print('resolution',resol)
#print(img.shape)
#print(img[:,:,2][40][10])

############################################################
#    Calculate green cover and Estimate Num.Trees          #
############################################################

forest_area,forest_cover,green_pixel,green_cov,ndvi, ndvi_d = get_cover(img,resol,NDVI_bounds.lower_bound, NDVI_bounds.upper_bound)
print("Green pixel count: ", green_pixel)

if space_availability == 'yes':
    print('Tree spacing available: (', str(spacing_along),',',str(spacing_parallel), ') m')
    spacing = (spacing_parallel + spacing_along ) // 2
    t_count = count_trees(resol,green_pixel,spacing)
    print("Estimated Number of Trees in your land:",t_count)

elif space_availability == 'no':
    print('Tree spacing NOT available')
    t_count = tree_count(tree_type, green_cov)
    print("Estimated Number of Trees in your land:",t_count)


############################################################
#                       Cal Carbon Seq                     #
############################################################

annual_rainFall_category = None
dbh_category = None

# once finalised this can be further simplified using binning
if 0 <= tree_land_spec.annual_rainfall < 900:
    annual_rainFall_category = 'le900'
    
elif 900 <= tree_land_spec.annual_rainfall < 1500:
    annual_rainFall_category = '900To1500'

elif 1500 <= tree_land_spec.annual_rainfall < 4000:
    annual_rainFall_category = '1500To4000'

else:
    annual_rainFall_category = 'Gr4000'

if 5 <= tree_land_spec.dbh_cm < 40:
    dbh_category = '5To40'

elif 40 <= tree_land_spec.dbh_cm < 60:
    dbh_category = '40To60'

function_name = tree_land_spec.species_general_type.name + '_' + \
                tree_land_spec.region.name  + '_' +\
                annual_rainFall_category + '_' +\
                dbh_category

if (hasattr(allometric_cal, function_name)) :
    print("Selected Function:",function_name)
    above_ground_biomass_kg = getattr(allometric_cal, function_name)(tree_land_spec, t_count)
else:
    print("Looks like specifi function not implemented or Not enough information")
    print("Switch to basic calculation")
    above_ground_biomass_kg = allometric_cal.notKnown_notKnown_notKnown_notKnown(tree_land_spec, t_count)

AGB_general_method = allometric_cal.notKnown_notKnown_notKnown_notKnown(tree_land_spec, t_count)

print("C Seq Specific: ", round(above_ground_biomass_kg/1e3,2), 'T Vs General: ', round(AGB_general_method/1e3,2), 'T' )
# seq = cal_existing(age_exist,t_count,tree_type)
# seq_current = seq.item()
# fig = green_cover_plot(ndvi,ndvi_d,forest_cover,t_count,seq_current)

# If the land is bigger then do we need to do the smoothing ?
fig = green_cover_plot(ndvi,ndvi_d,forest_cover,t_count,above_ground_biomass_kg)
fig2 = green_cover_plot_smooth(ndvi,ndvi_d,forest_cover,t_count,above_ground_biomass_kg,kml_file_name_no_ext)

fig.show()
fig2.show()


# print('***********************************************************')
# print('**         Scenario 1: Forecasting for Bare lands        **')
# print('***********************************************************')

# # CO2 forecasting
# print("Forecasting for one tree type")
# n_tree_type = input('Enter the new tree type to be planted: ')
# n_tree = input('Enter the tree count: ')
# n_tree = int(n_tree)
# age_max = input('Enter the no of years ahead to forecast: ')
# age_max = int(age_max)
# plot_SEQ(n_tree_type,n_tree,age_max)

# webbrowser.open("show_output.html",new=2)
