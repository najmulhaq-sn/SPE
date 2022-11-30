#!/usr/bin/env python
# coding: utf-8
"""
Created on Thu Nov 17 14:29:48 2022

@author: Venuri
"""

# Start by importing the kml module
from fastkml import geometry
from fastkml import kml
import numpy as np


def kml_coord(path):
    
    kml_filename = path
    with open(kml_filename) as kml_file:
        doc = kml_file.read().encode('utf-8')
        k = kml.KML()
        k.from_string(doc)
        
        # gives all the features inside kml - i.e. Document
        features = list(k.features())
        # gives all the features inside feature - i.e. Folder
        feature1 = list(features[0].features())
        # gives all the features inside feature1 - i.e. all Placemarks
        feature2 = list(feature1[0].features())

        coord_list=[]
        coord_new =[]

        for i in range(len(feature2)):

            coord_list=[]
            for coord in feature2[i].geometry.geoms[0].exterior.coords:
            # these are long, lat tuples
                coord_list.append(coord[:2])
            coord_new.append(coord_list)

        coordinates = np.array(coord_new)

        return coordinates        

