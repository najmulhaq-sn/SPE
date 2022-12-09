# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 15:24:35 2022

@author: DELL
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 16:00:38 2022

@author: Harith
"""

#importing required libraries
#import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
from Utils import tree_models as tree_model
from Utils.carbon_seq_cal import def_allometric_AGB_multi_model_New as allometric_cal

#import os

# Considering only the 1st Use Case - Bare Land/ Afforestation 
# User Inputs - Type of Species, Number of Trees

# Reading the csv with the stored data 

#reading the Growth chart related data
data = pd.read_csv("Data/Math_Est_Data.csv")


def plot_SEQ(result_SEQ):
    

    result_SEQ.plot(x ='Age ', y='AGB', kind = 'line')
    plt.title('Carbon Sequestration Estimation')
    plt.xlabel('Years')
    plt.ylabel('C-Seq in kg')
    plt.savefig('forecast.png',bbox_inches='tight')
    return plt

#cal for existing trees
def growth_chart(age_max,Species):
    
    df1 = data[data['Species - Common name'] == Species]
    df1 = df1[df1['Age '] <= age_max ]
    #CF = data_CF["Carbon Fraction"][data_CF['Species - Common Name'] == Species].item()
    
 
    df1 = df1[['Age ','DBH ','Height ']]

    #Converting DBH in cm to mm
    #Converting Height in m to cm
    df1["DBH_in_mm"]=10*df1["DBH "]
    df1["Height_in_cm"] = 100*df1["Height "]
    #SEQ_lst = calculate_SEQ(n, CF, df1)
    #SEQ_df = SEQ_lst.to_frame(name="Total Carbon Sequestration")
    return df1
    #SEQ_df = SEQ_lst.to_frame(name="Total Carbon Sequestration")
    
def get_abg(species_type,count_exist,region_type,annual_rainfall,DBH_cm,Height_m) :
    
    tree_land_spec = tree_model.tree_geo_specifications(    tree_model.species_category[species_type],
                                                            tree_model.region_type[region_type],
                                                            annual_rainfall,
                                                            DBH_cm,
                                                            Height_m
                                                        ) 

    annual_rainFall_category = None
    dbh_category = None
    

    # once finalised this can be further simplified using binning

    # defining Rainfall categories
    if 0 <= tree_land_spec.annual_rainfall < 900:
        annual_rainFall_category = 'le900'

    elif 900 <= tree_land_spec.annual_rainfall < 1500:
        annual_rainFall_category = '900To1500'

    elif 1500 <= tree_land_spec.annual_rainfall < 4000:
        annual_rainFall_category = '1500To4000'

    else:
        annual_rainFall_category = 'Gr4000'   

    # Nested functions for C-seq calculation
    if tree_land_spec.species_general_type.name == "broadLeavedSpecies":

        if annual_rainFall_category == 'le900':

            if 3 <= tree_land_spec.dbh_cm <= 30:
                dbh_category = '3To30'

        elif annual_rainFall_category == '900To1500':

            if 5 <= tree_land_spec.dbh_cm <= 40:
                dbh_category = '5To40'

        elif annual_rainFall_category == '1500To4000':

            if tree_land_spec.dbh_cm < 60:
                dbh_category = 'le60'

            elif 60 <= tree_land_spec.dbh_cm <= 148:
                dbh_category = '6To148'
        else:

            if 4 <= tree_land_spec.dbh_cm <= 112:
                dbh_category = '4To112'

    if tree_land_spec.species_general_type.name == "ConiferousSpecies": 

        annual_rainFall_category = 'notKnown'
        tree_land_spec.region = 'notKnown'

        if 2 <= tree_land_spec.dbh_cm <= 52:
            dbh_category = '2To52'

    if tree_land_spec.species_general_type.name == "ConiferousTaxodiumDistichumSpecies": 

        annual_rainFall_category = 'notKnown'
        dbh_category = 'notKnown'
        tree_land_spec.region = 'notKnown'


    if tree_land_spec.species_general_type.name == "PalmSpecies":

        annual_rainFall_category = 'notKnown'
        tree_land_spec.region = 'notKnown'

        if tree_land_spec.dbh_cm > 7.5:
            dbh_category = 'Gr7point5'


    if tree_land_spec.species_general_type.name in ["ConiferousSpecies","ConiferousTaxodiumDistichumSpecies","PalmSpecies"]:
        function_name = tree_land_spec.species_general_type.name + '_' + \
                        tree_land_spec.region  + '_' +\
                        annual_rainFall_category + '_' +\
                        dbh_category

    else:
        function_name = tree_land_spec.species_general_type.name + '_' + \
                    tree_land_spec.region.name  + '_' +\
                    annual_rainFall_category + '_' +\
                    dbh_category

    if (hasattr(allometric_cal, function_name)) :
        #print("Selected Function:",function_name)
        above_ground_biomass_kg = getattr(allometric_cal, function_name)(tree_land_spec, count_exist)
    else:
        #print("Looks like specific function not implemented or Not enough information")
        #print("Switch to basic calculation")
        above_ground_biomass_kg = allometric_cal.notKnown_notKnown_notKnown_notKnown(tree_land_spec, count_exist)
    
    return above_ground_biomass_kg

def forecast(df,species_type,count_exist,region_type,annual_rainfall):
    #growth chart filtered by max age
    chart = df.reset_index() 

    ag_biomass = []
    
    for index,row in chart.iterrows():

        #tree_land_spec.height_m = row["Height "]
        #tree_land_spec.dbh_cm = row["DBH "]
        #print(row["DBH "])
        agb = get_abg(species_type,count_exist,region_type,annual_rainfall,row["DBH "],row["Height "])
        #print(agb)
        ag_biomass.append(agb)

    #gen = chart.copy()
    chart.insert(0, "AGB",ag_biomass )
    #gen.insert(0, "AGB",general )
    #print(chart)
    #print(gen)
    return chart