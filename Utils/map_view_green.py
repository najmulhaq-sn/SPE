# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 12:32:59 2022

@author: User
"""
import pandas as pd
import folium
from folium import plugins
import webbrowser

### Create map
def plot_map(loc_array):
    loc_cord = pd.DataFrame(loc_array, columns = ['lon','lat'])
    
    country_map = folium.Map(location=[loc_cord.lat.mean(), 
                           loc_cord.lon.mean()], #center the map
                 zoom_start=18)
    poly_cord = []
    for index, row in loc_cord.iterrows():
        poly_cord.append((row['lat'],row['lon']))
    
    folium.Polygon(poly_cord,
               color="blue",
               weight=5,
               fill=True,
               opacity=0.4).add_to(country_map)
    
    folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = False,
        control = True
       ).add_to(country_map)
    
    country_map.save("green_bounded_map.html")
#     
    return country_map

#show
def map_show(poly_coord):
    for poly in poly_coord:
        country_map = plot_map(poly)
    webbrowser.open("green_bounded_map.html",new=2)