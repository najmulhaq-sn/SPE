# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 15:02:42 2022

@author: Harith
"""

import os
import sys
import numpy as np
from Utils.read_coord import kml_coord
from Utils.sentinal_request import senti_api
from Utils.forest_cover import get_cover,green_cover_plot, green_cover_plot_smooth
from Utils.carbon_seq_cal.forecast import plot_SEQ,growth_chart
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
t_count = int(lines[2].split(":")[1].strip())
species_type = lines[3].split(":")[1].strip()
region_type = lines[4].split(":")[1].strip()
annual_rainfall = float(lines[5].split(":")[1].strip())
age_max = int(lines[6].split(":")[1].strip())

DBH_cm = 0
Height_cm = 0

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
print('** Scenario 1: Forecasting for future plnats  **')
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
    
############################################################
#                       Growth Rates                    #
############################################################

#growth chart filtered by max age
chart = growth_chart(age_max,tree_type).reset_index() 



############################################################
#                       Cal Carbon Seq                     #
############################################################

annual_rainFall_category = None
dbh_category = None

# once finalised this can be further simplified using binning
if 900 <= tree_land_spec.annual_rainfall < 1500:
    annual_rainFall_category = '900To1500'

elif 1500 <= tree_land_spec.annual_rainfall < 4000:
    annual_rainFall_category = '1500To4000'

ag_biomass = []
for index,row in chart.iterrows():
    
    tree_land_spec.height_m = row["Height "]
    tree_land_spec.dbh_cm = row["DBH "]
    if 0 <= tree_land_spec.dbh_cm < 40: #changed the range to accomodate lower
        dbh_category = '5To40'
    
    elif 40 <= tree_land_spec.dbh_cm < 60:
        dbh_category = '40To60'
    #print(type(tree_land_spec.species_general_type.name),type(tree_land_spec.region.name),type(annual_rainFall_category),dbh_category)

    function_name = tree_land_spec.species_general_type.name + '_' + \
                    tree_land_spec.region.name  + '_' +\
                    annual_rainFall_category + '_' +\
                    dbh_category                    
    #print(function_name)

    if (hasattr(allometric_cal, function_name)) :
        print("Selected Function:",function_name)
              
        above_ground_biomass_kg = getattr(allometric_cal, function_name)(tree_land_spec, t_count)
        ag_biomass.append(above_ground_biomass_kg)
    else:
        print("Looks like specifi function not implemented or Not enough information")
        print("Switch to basic calculation")
        for index,row in chart.iterrows():

            above_ground_biomass_kg = allometric_cal.notKnown_notKnown_notKnown_notKnown(tree_land_spec, t_count)
            ag_biomass.append(above_ground_biomass_kg)
        
#AGB_general_method = allometric_cal.notKnown_notKnown_notKnown_notKnown(tree_land_spec, t_count)
chart.insert(0, "AGB",ag_biomass )
#print(chart)
plot = plot_SEQ(chart)
plot.show()