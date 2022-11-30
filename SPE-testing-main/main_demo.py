# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 15:49:43 2022

@author: DELL
"""

import os
import sys
import numpy as np
from Utils.read_coord import kml_coord
from Utils.sentinal_request import senti_api
from Utils.forest_cover import get_cover,green_cover_plot,green_cover_plot2, green_cover_plot_smooth
from Utils.carbon_seq_cal.seques_forecast import cal_existing
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

kml_file_name = input('Enter kml name: ')
#print(file_path)
#C:\Users\Harith\EngenuityAI\SPE\SPE-development\sentinal\gAMPOLA TEST SITE 2.kml

file_path = os.path.join(os.getcwd(), 'test_kml_files', kml_file_name )
print("The KML file path:",file_path, end="")
if os.path.exists(file_path):
    print(' Exists')
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
else:
    print(' The specified file does NOT exist')

# getting polygon coordinates
poly_coord = kml_coord(file_path)


print('***********************************************************')
print('** Scenario 2: Estimation for Existing land with plants  **')
print('***********************************************************')

############################################################
#     Read the KML from saved directory if possible        #
############################################################
# this lookup may be turned-off after testing
# better to add a date tag to the saved file name; 

kml_file_name_no_ext = kml_file_name.split(".")[0]
dat_file_name = kml_file_name_no_ext + '.npy'
file_path_to_sat_img = os.path.join( os.getcwd(), 'kml_to_ndarray', dat_file_name )

img = None
print(file_path_to_sat_img)
if os.path.exists(file_path_to_sat_img):
    print('Sat ndarray image exist already')
    # img = np.fromfile(file_path_to_sat_img, dtype=float)
    img = np.load(file_path_to_sat_img)
    resol = 10

else:
    print("NeW KML file uploaded; ping to API")        
    img,resol = senti_api(poly_coord)
    # img.tofile(file_path_to_sat_img)
    np.save(file_path_to_sat_img, img) 

# show the map view
map_show(poly_coord)

############################################################
#                 Calculate green cover                    #
############################################################

print('***********************************************************')
print('**     Calculating Green Cover for Existing Lands        **')
print('***********************************************************')

while True:
    user_input = input('What type of forestration? (Pick 1 for Temperate Forest/ 2 for Tropical Rain Forests/ 3 for Coastal Forest): ')
    if user_input.lower() == '1':
        print('user typed Temperate Forest')
        lo_thresh = 0.31
        up_thresh = 0.77
        break

    elif user_input.lower() == '2':
        print('user typed Tropical Rain Forests')
        lo_thresh = 0.77
        up_thresh = 0.92
        break
    
    elif user_input.lower() == '3':
        print('user typed Coastal Forest')
        lo_thresh = 0.64
        up_thresh = 0.77
        break
    else:
        print('Type not recognized')
        
NDVI_bounds = tree_model.NDVI_threasholds(lo_thresh, up_thresh)

forest_area,forest_cover,green_pixel,green_cov,ndvi, ndvi_d, cloud_cover = get_cover(img,resol,NDVI_bounds.lower_bound, NDVI_bounds.upper_bound)
fig = green_cover_plot(ndvi,ndvi_d,forest_cover,cloud_cover)
fig.show()

############################################################
#                       Cal Carbon Seq                     #
############################################################

#tree_type = input('Enter the existing tree type: ')
#print(tree_type)
print('***********************************************************')
print('** Calculating Carbon Sequestration for Existing Lands   **')
print('***********************************************************')

species_type = input('Enter the existing species type ( broadLeavedSpecies/ ConiferousSpecies/ Palms): ')
'''while True:
    user_input = input('Enter the region type: (Pick 1 for broadLeavedSpecies/ 2 for ConiferousSpecies/ 3 for Palms): ')
    if user_input.lower() == '1':
        print('user typed broadLeavedSpecies')
        region_type = 'broadLeavedSpecies'
        break

    elif user_input.lower() == '2':
        print('user typed ConiferousSpecies')
        region_type = 'ConiferousSpecies'
        break
    elif user_input.lower() == '3':
        print('user typed Palms')
        region_type = "Palms"
        break
    else:
        print('Type not recognized')
'''
#print(tree_type)
count_exist = input('Enter the existing tree count: ')
count_exist = int(count_exist)

region_type = input('Enter the region type(tropicalDryRegions/tropicalHumidRegion/tropicalWetRegion): ')
'''while True:
    user_input = input('Enter the region type: (Pick 1 for tropicalDryRegions/ 2 for tropicalHumidRegion/ 3 for tropicalWetRegion): ')
    if user_input.lower() == '1':
        print('user typed tropicalDryRegions')
        species_type = "tropicalDryRegions"
        species_type = species_type.strip()
        break

    elif user_input.lower() == '2':
        print('user typed tropicalHumidRegion')
        species_type = "tropicalHumidRegion"
        
        break
    elif user_input.lower() == '3':
        print('user typed tropicalWetRegion')
        species_type = "tropicalWetRegion"
        break
    else:
        print('Type not recognized')
'''
annual_rainfall = input('Enter the Annual rainfall: ')
annual_rainfall = int(annual_rainfall)

#age_exist = input('Enter the age of the plantation: ')
#age_exist = int(age_exist)

DBH_cm = input('Enter the avg DBH of the Plants: ')
DBH_cm = int(DBH_cm)

Height_cm = input('Enter the avg Height of the Plants: ')
Height_cm = int(Height_cm)



tree_land_spec = tree_model.tree_geo_specifications(    tree_model.species_category[species_type],
                                                        tree_model.region_type[region_type],
                                                        annual_rainfall,
                                                        DBH_cm,
                                                        Height_cm
                                                    ) 




annual_rainFall_category = None
dbh_category = None

# once finalised this can be further simplified using binning
if 900 <= tree_land_spec.annual_rainfall < 1500:
    annual_rainFall_category = '900To1500'

elif 1500 <= tree_land_spec.annual_rainfall < 4000:
    annual_rainFall_category = '1500To4000'


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
    above_ground_biomass_kg = getattr(allometric_cal, function_name)(tree_land_spec, count_exist)
else:
    print("Looks like specifi function not implemented or Not enough information")
    print("Switch to basic calculation")
    above_ground_biomass_kg = allometric_cal.notKnown_notKnown_notKnown_notKnown(tree_land_spec, count_exist)

AGB_general_method = allometric_cal.notKnown_notKnown_notKnown_notKnown(tree_land_spec, count_exist)

print("C Seq Specific: ", round(above_ground_biomass_kg/1e3,2), 'T Vs General: ', round(AGB_general_method/1e3,2), 'T' )
fig2 = green_cover_plot2(ndvi,ndvi_d,forest_cover,count_exist,above_ground_biomass_kg)
fig3 = green_cover_plot_smooth(ndvi,ndvi_d,forest_cover,count_exist,above_ground_biomass_kg,kml_file_name_no_ext)

fig2.show()
#fig3.show()

print('***********************************************************')
print('**     Scenario : Carbon Sequestration Forecasting       **')
print('***********************************************************')

tree_type = input('Enter the type of the new tree: ')

t_count = input('Enter no of trees: ')
t_count = int(t_count)

age_max = input('Enter the max age: ')
age_max = int(age_max)

############################################################
#                       Growth Rates                    #
############################################################

#growth chart filtered by max age
chart = growth_chart(age_max,tree_type).reset_index() 

ag_biomass = []
general =[]
for index,row in chart.iterrows():
    
    tree_land_spec.height_m = row["Height "]
    tree_land_spec.dbh_cm = row["DBH "]
    if 0 <= tree_land_spec.dbh_cm < 40:
        dbh_category = '5To40'
    
    elif 40 <= tree_land_spec.dbh_cm < 60:
        dbh_category = '40To60'
    #print(type(tree_land_spec.species_general_type.name),type(tree_land_spec.region.name),type(annual_rainFall_category),dbh_category)

    function_name = tree_land_spec.species_general_type.name + '_' + \
                    tree_land_spec.region.name  + '_' +\
                    annual_rainFall_category + '_' +\
                    dbh_category                    
    #print(function_name)
    #function_name = 'broadLeavedSpecies_tropicalHumidRegion_le1500_5To40'
    if (hasattr(allometric_cal, function_name)) :
        #print("Selected Function:",function_name)
              
        above_ground_biomass_kg = getattr(allometric_cal, function_name)(tree_land_spec, t_count)
        ag_biomass.append(above_ground_biomass_kg)
    else:
        #print("Looks like specifi function not implemented or Not enough information")
        #print("Switch to basic calculation")
        '''
<<<<<<< Updated upstream
        #for index,row in chart.iterrows():

=======
>>>>>>> Stashed changes
        '''
        above_ground_biomass_kg = allometric_cal.notKnown_notKnown_notKnown_notKnown(tree_land_spec, t_count)
        ag_biomass.append(above_ground_biomass_kg)
        
    AGB_general_method = allometric_cal.notKnown_notKnown_notKnown_notKnown(tree_land_spec, t_count)
    general.append(AGB_general_method)
gen = chart.copy()
chart.insert(0, "AGB",ag_biomass )
gen.insert(0, "AGB",general )
#print(chart)
#print(gen)
plot = plot_SEQ(chart)
#plot2 = plot_SEQ(gen)
plot.show()
#plot2.show()

