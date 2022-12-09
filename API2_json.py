# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 00:21:31 2022

@author: DELL
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 09:28:07 2022

@author: DELL
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 18:37:51 2022

@author: DELL
"""
import numpy as np
import os
from Utils.read_coord import kml_coord
from Utils.sentinal_request import senti_api
from Utils.forest_cover import get_cover
from utils import plot_image
from Utils.forest_cover import get_cover,green_cover_plot,green_cover_plot2, green_cover_plot_smooth
from Utils.carbon_seq_cal.seques_forecast import cal_existing
from Utils.carbon_seq_cal.forecast import plot_SEQ,growth_chart,forecast
from Utils.map_view import map_show
from Utils.tree_count import count_trees
from Utils.tree_count import tree_count
import webbrowser
from Utils import tree_models as tree_model
from Utils.carbon_seq_cal import def_allometric_AGB_multi_model_New as allometric_cal
from PIL import Image, ImageFilter
import earthpy.plot as ep
import matplotlib.pyplot as plt

from flask import Flask,request
from flask_restful import Resource, Api, reqparse
import pandas as pd
#import ast

app = Flask(__name__)
api = Api(app)

def get_fuction_name(species_type,count_exist,region_type,annual_rainfall,DBH_cm,Height_m) :
    
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

@app.route('/carbon_seq', methods=['POST'])

def carbon_seq():
    
    request_data = request.get_json()  # initialize
        
    """parser.add_argument('species_type', required=True,location='form')  # add args
        parser.add_argument('Species', required=True,location='form')  # add args
        parser.add_argument('age_max',type=int, required=True,location='form')
        parser.add_argument('count_exist',type=int, required=True,location='form')
        parser.add_argument('region_type', required=True,location='form')  # add args
        parser.add_argument('annual_rainfall',type=int, required=True,location='form')
        parser.add_argument('DBH_cm',type=int, required=True,location='form')  # add args
        parser.add_argument('Height_m',type=int, required=True,location='form')
        
        args = parser.parse_args()  # parse arguments to dictionary"""
    species_type = None
    Species = None
    age_max = None
    count_exist = None
    region_type = None
    annual_rainfall = None
    DBH_cm = None
    Height_m = None
    
    if request_data:
        if 'species_type' in request_data:
            species_type = request_data['species_type']
        if 'Species' in request_data:
            Species = request_data['Species']
        if 'age_max' in request_data:    
            age_max = request_data['age_max']
        if 'count_exist' in request_data:
            count_exist = request_data['count_exist']
        if 'region_type' in request_data:
            region_type = request_data['region_type']
        if 'annual_rainfall' in request_data:
            annual_rainfall = request_data['annual_rainfall']
        if 'DBH_cm' in request_data:
            DBH_cm = request_data['DBH_cm']
        if 'Height_m' in request_data:
            Height_m = request_data['Height_m']
        
    abg = get_fuction_name(species_type,count_exist,region_type,annual_rainfall,DBH_cm,Height_m)
        
    try:
        data = pd.read_csv("Data/Math_Est_Data.csv")
        df1 = data[(data['Species - Common name'] == Species) & (data['DBH '] >= DBH_cm)]
        index = data.index[df1.first_valid_index()]
        df2 = data[(data['Species - Common name'] == Species) & (data['Age '] >= data['Age '].loc[index]) &  (data['Age '] < data['Age '].loc[index]+age_max)]   
        df2 = df2.reset_index()
        ch = forecast(df2,species_type,count_exist,region_type,annual_rainfall)
        years = list(range(1, age_max+1))
        seq = ch["AGB"].to_list()
    
        #if (df2['index'].max()<index+age_max):
        maturity = "Maturity age is"+" "+str(max(years))
        json = {'C_seq':abg, 'maturity_stat' : maturity, 'forecast' : [{'years':years},{'carbon_seq':seq}]}
            
    except:
        maturity="Plant cannot be forcasted"
        json = {'C_seq':abg, 'maturity_stat' : maturity, 'forecast' : [{'years':[]},{'carbon_seq':[]}]}
        
        
    return {'out':json}, 200  # return data with 200 OK
    
#api.add_resource(carbon_seq, '/carbon_seq')  # '/carbon_seq' is our entry point for carbon_seq


if __name__ == '__main__':
    app.run(debug = True)  # run our Flask app


