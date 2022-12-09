# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 18:03:44 2022

@author: DELL
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Nov 21 13:11:44 2022

@author: DELL
"""

import numpy as np
import os
from Utils.read_coord import kml_coord
from Utils.sentinal_request import senti_api
from Utils.forest_cover import get_cover
from utils import plot_image
from Utils.forest_cover import get_cover,green_cover_plot, get_green_cover_plot_smooth
from Utils.carbon_seq_cal.seques_forecast import cal_existing
from Utils.carbon_seq_cal.forecast import plot_SEQ,growth_chart
from Utils.map_view import map_show
from Utils.tree_count import count_trees
from Utils.tree_count import tree_count
import webbrowser
from Utils import tree_models as tree_model
from Utils.carbon_seq_cal import def_allometric_AGB_multi_model as allometric_cal
from PIL import Image, ImageFilter

from flask import Flask,request
from flask_restful import Resource, Api, reqparse
import pandas as pd
#import ast

app = Flask(__name__)
api = Api(app)


def get_green_cover(kml_file_name,user_input) :
    file_path = os.path.join(os.getcwd(), 'test_kml_files', kml_file_name )
    
    if os.path.exists(file_path):
        
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
#     else:
#         return 

    # getting polygon coordinates
    poly_coord = kml_coord(file_path)
    kml_file_name_no_ext = kml_file_name.split(".")[0]
    dat_file_name = kml_file_name_no_ext + '.npy'
    file_path_to_sat_img = os.path.join( os.getcwd(), 'kml_to_ndarray', dat_file_name )

    img = None
    print(file_path_to_sat_img)
    if os.path.exists(file_path_to_sat_img):
        img = np.load(file_path_to_sat_img)
        resol = 10

    else:
                
        img,resol = senti_api(poly_coord)
        # img.tofile(file_path_to_sat_img)
        np.save(file_path_to_sat_img, img) 
    
    if user_input.lower() == '1':
        
        lo_thresh = 0.31
        up_thresh = 0.77
        

    elif user_input.lower() == '2':
        
        lo_thresh = 0.77
        up_thresh = 0.92
        
    
    elif user_input.lower() == '3':
        
        lo_thresh = 0.64
        up_thresh = 0.77
        
#     else:
#         return 

    NDVI_bounds = tree_model.NDVI_threasholds(lo_thresh, up_thresh)

    forest_area,forest_cover,green_pixel,green_cov,ndvi, ndvi_d, cloud_cover = get_cover(img,resol,NDVI_bounds.lower_bound, NDVI_bounds.upper_bound)
    img,path = get_green_cover_plot_smooth(ndvi,ndvi_d,forest_cover,kml_file_name_no_ext)
    return forest_cover,img,path

@app.route('/green_cover', methods=['POST'])
def green_cover():
    
        #parser = reqparse.RequestParser()  # initialize
    request_data = request.get_json()
        
    kml_path = None
    forest_class = None
        
    if request_data:
        if 'kml' in request_data:
            kml_path = request_data['kml']

        if 'forest_type' in request_data:
            forest_class = request_data['forest_type']


        
    green, img,path = get_green_cover(kml_path,forest_class)
        
    return {'data': green,'image':path}, 200  # return data with 200 OK
    
#api.add_resource(green_cover, '/green_cover')  # '/green_cover' is our entry point for green_cover


if __name__ == '__main__':
    app.run(debug = True)  # run our Flask app
