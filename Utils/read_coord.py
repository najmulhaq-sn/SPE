# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 19:59:28 2022

@author: Harith
"""

from fastkml import geometry
from fastkml import kml
import numpy as np

def kml_coord(path):
    coord_list=[]
    kml_filename = path
    with open(kml_filename) as kml_file:
        doc = kml_file.read().encode('utf-8')
        k = kml.KML()
        k.from_string(doc)
        for feature0 in k.features():
            #print("{}, {}".format(feature0.name, feature0.description))
            for feature1 in feature0.features():
                if isinstance(feature1.geometry, geometry.Polygon):
                    polygon = feature1.geometry
                    for coord in polygon.exterior.coords:
                        # these are long, lat tuples
                        coord_list.append(coord[:2])
    coord_list = np.array(coord_list)
    return coord_list
                    