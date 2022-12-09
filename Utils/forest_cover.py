# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 16:31:21 2022

@author: Harith
"""

#import os
import numpy as np
import numpy.ma as ma
from Utils.vegetation_indices import normalized_diff
import matplotlib.pyplot as plt
#import cv2
#import rasterio
#import rioxarray as rxr
#import geopandas as gpd
#import earthpy as et
#import earthpy.spatial as es
import earthpy.plot as ep
from matplotlib.colors import ListedColormap
from PIL import Image, ImageFilter

#import imutils


# NDVI Calculation with sentinel hub API

def ndvi_api(red,nir):
    
    '''
    NDVI calculation with sentinel hub API (using red & nir value arrays)
    
    red: red array
    nir: NIR array
    
    retun: ndvi 2D array
    '''
    
    # calculate the NDVI
    ndvi = normalized_diff(nir, red)
    
    return ndvi

# Calculate the green area

def green_area(ndvi,res,l_thresh=0.77, up_thresh=0.92):
    
    '''
    Calculate the green area with specific threshold values
    
    ndvi: ndvi array
    res: image resolution
    thresh: threshold value to distinguish forect/ green area
    
    return: green cover in km2
    '''
    
    # get the ndvi data from masked array
    ndvi_data = ma.getdata(ndvi).copy()
    # get the row & col count
    rows, cols = ndvi_data.shape
    
    # replace ndvi values with 1, if ndvi >= threshold value
    for i in range(0,rows):
        for j in range(0,cols):
            if ((ndvi_data[i][j] >= l_thresh) and (ndvi_data[i][j] <= up_thresh)):
           # if ndvi_data[i][j] >= 0.6:
                ndvi_data[i][j] = 1
            else:
                ndvi_data[i][j] = 0
            
    # count the ones
    #ndvi_list = ndvi_data.tolist()
    #green_pixel = sum(x.count(1) for x in ndvi_list)
    green_pixel = np.sum(ndvi_data)
    
    # calculate the green area in km2
    green_area = np.round((green_pixel*res*res)/1e6,4)
    
    #print('Forest/ Green area: ',green_area,"km2")
    #print('Forest/ Green pixel: ',green_pixel)
    
    return green_pixel, green_area, ndvi_data

# Forest/ green cover with user input total area
def green_cover(green_area,total_area):
    green_cover = np.round((green_area/total_area)*100,2)
    #print("Forest/green cover: ",green_cover,"%")
    
    return green_cover

#polygon area calculation
def poly_area(req,res):
    bb = req[:,:,0].copy()
    r, c = bb.shape
    
    for i in range(0,r):
        for j in range(0,c):
            if bb[i][j] > 0.0:
                bb[i][j] = 0
            else:
                bb[i][j] = 1
            
    #bb_list = bb.tolist()
    #bg_pixel = sum(x.count(1) for x in bb_list)
    bg_pixel = np.sum(bb)
    poly_pixel = (r*c)-bg_pixel
    poly_area = np.round((poly_pixel*res*res)/1e6,4) # in km2
    #print("Land area: ",poly_area,"km2")
    #print("Land pixel: ",poly_pixel)
    
    return poly_area 

# Forest cover plot
def green_cover_plot(ndvi,
                     ndvi_data,
                     green_cover,
                     cloud_cover):
    
    '''
    ndvi: ndvi index values

    '''
    
    # Create classes and apply to NDVI results
    #ndvi_class_bins = [-np.inf, l_thresh, up_thresh, np.inf]
    #ndvi_landsat_class = np.digitize(ndvi, ndvi_class_bins)

    # Apply the nodata mask to the newly classified NDVI data
    ndvi_landsat_class = np.ma.masked_where(np.ma.getmask(ndvi), 
                                            ndvi_data)
    if green_cover == 0.00:
    
        # Define color map
        nbr_colors = ["gray"]
        nbr_cmap = ListedColormap(nbr_colors)

        # Define class names
        ndvi_cat_names = ["No Vegetation"]
        
        # Plot your data
        fig, ax = plt.subplots(figsize=(15, 6))
        im = ax.imshow(ndvi_landsat_class, cmap=nbr_cmap)
        ep.draw_legend(im_ax=im, titles=ndvi_cat_names)

        
    elif (green_cover > 0.00 and green_cover < 100.00):
            
        # Define color map
        nbr_colors = ["gray", "green"]
        nbr_cmap = ListedColormap(nbr_colors)

        # Define class names
        ndvi_cat_names = [
            "No Vegetation",
            "Vegetation"]


        # Get list of classes
        classes = np.unique(ndvi_landsat_class)
        classes = classes.tolist()

        # The mask returns a value of none in the classes. remove that
        classes = classes[0:2]
        
        # Plot your data
        fig, ax = plt.subplots(figsize=(15, 6))
        im = ax.imshow(ndvi_landsat_class, cmap=nbr_cmap)
        ep.draw_legend(im_ax=im, classes=classes, titles=ndvi_cat_names)
        
    else:
            
        # Define color map
        nbr_colors = ["green"]
        nbr_cmap = ListedColormap(nbr_colors)

        # Define class names
        ndvi_cat_names = [
            "Vegetation"]
        
        # Plot your data
        fig, ax = plt.subplots(figsize=(15, 6))
        im = ax.imshow(ndvi_landsat_class, cmap=nbr_cmap)
        ep.draw_legend(im_ax=im, titles=ndvi_cat_names)

        

    # text box
    textstr = '\n'.join((
        r'Forest cover: %.2f %%' % (green_cover, ),
        r'Cloud cover: %.2f %%' % (cloud_cover, )))
        #r'Total Sequestared Carbon amount: %.2f kg' % (seq_current, ),
        #r'No of trees: %.0f' % (t_count, )))
    
    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    
    # place a text box in upper left in axes coords
    ax.text(0.50, 0.00, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)

    ax.set_title(
    "Greenery Details of Your Land ",
    fontsize=14)
    ax.set_axis_off()
    plt.savefig('output/gren_cover.png',bbox_inches='tight')

    return plt

# Forest cover plot
def green_cover_plot2(ndvi,
                     ndvi_data,
                     green_cover,
                     t_count,
                     seq_current):
    
    '''
    ndvi: ndvi index values

    '''
    
    # Create classes and apply to NDVI results
    #ndvi_class_bins = [-np.inf, l_thresh, up_thresh, np.inf]
    #ndvi_landsat_class = np.digitize(ndvi, ndvi_class_bins)

    # Apply the nodata mask to the newly classified NDVI data
    ndvi_landsat_class = np.ma.masked_where(np.ma.getmask(ndvi), 
                                            ndvi_data)
    if green_cover == 0.00:
    
        # Define color map
        nbr_colors = ["gray"]
        nbr_cmap = ListedColormap(nbr_colors)

        # Define class names
        ndvi_cat_names = ["No Vegetation"]
        
        # Plot your data
        fig, ax = plt.subplots(figsize=(15, 6))
        im = ax.imshow(ndvi_landsat_class, cmap=nbr_cmap)
        ep.draw_legend(im_ax=im, titles=ndvi_cat_names)

        
    elif (green_cover > 0.00 and green_cover < 100.00):
            
        # Define color map
        nbr_colors = ["gray", "green"]
        nbr_cmap = ListedColormap(nbr_colors)

        # Define class names
        ndvi_cat_names = [
            "No Vegetation",
            "Vegetation"]


        # Get list of classes
        classes = np.unique(ndvi_landsat_class)
        classes = classes.tolist()

        # The mask returns a value of none in the classes. remove that
        classes = classes[0:2]
        
        # Plot your data
        fig, ax = plt.subplots(figsize=(15, 6))
        im = ax.imshow(ndvi_landsat_class, cmap=nbr_cmap)
        ep.draw_legend(im_ax=im, classes=classes, titles=ndvi_cat_names)
        
    else:
            
        # Define color map
        nbr_colors = ["green"]
        nbr_cmap = ListedColormap(nbr_colors)

        # Define class names
        ndvi_cat_names = [
            "Vegetation"]
        
        # Plot your data
        fig, ax = plt.subplots(figsize=(15, 6))
        im = ax.imshow(ndvi_landsat_class, cmap=nbr_cmap)
        ep.draw_legend(im_ax=im, titles=ndvi_cat_names)

    # text box
    textstr = '\n'.join((
        r'Forest cover: %.2f %%' % (green_cover, ),
        r'Total Sequestered Carbon amount: %.2f kg' % (seq_current, ),
        r'No of trees: %.0f' % (t_count, )))
    
    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    
    # place a text box in upper left in axes coords
    ax.text(0.50, 0.00, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)

    #ep.draw_legend(im_ax=im, classes=classes, titles=ndvi_cat_names)
    ax.set_title(
    "Greenery Details of Your Land ",
    fontsize=14)
    ax.set_axis_off()
    plt.savefig('output/gren_cover.png',bbox_inches='tight')

    return plt

# Forest cover plot
def green_cover_plot_smooth(ndvi,
                     ndvi_data,
                     green_cover,
                     t_count,
                     seq_current,file_name):

    # Apply the nodata mask to the newly classified NDVI data
    ndvi_landsat_class = np.ma.masked_where(np.ma.getmask(ndvi), 
                                            ndvi_data)
    if green_cover == 0.00:
    
        # Define color map
        nbr_colors = ["gray"]
        nbr_cmap = ListedColormap(nbr_colors)

        # Define class names
        ndvi_cat_names = ["No Vegetation"]
        
        # Plot your data
        fig, ax = plt.subplots(figsize=(15, 6))
        im = ax.imshow(ndvi_landsat_class, cmap=nbr_cmap)
        
        ax.set_axis_off()
        plt.savefig('output/gren_cover_no_legend-'+file_name+'.png',bbox_inches='tight')


        image = Image.open('output/gren_cover_no_legend-'+file_name+'.png')
        image_smoothed = image.filter(ImageFilter.ModeFilter(size=15))

        image_smoothed = ax.imshow(image_smoothed, cmap=nbr_cmap)
        
        ep.draw_legend(im_ax=image_smoothed, titles=ndvi_cat_names)
        

        
    elif (green_cover > 0.00 and green_cover < 100.00):
            
        # Define color map
        nbr_colors = ["gray", "green"]
        nbr_cmap = ListedColormap(nbr_colors)

        # Define class names
        ndvi_cat_names = [
            "No Vegetation",
            "Vegetation"]


        # Get list of classes
        classes = np.unique(ndvi_landsat_class)
        classes = classes.tolist()

        # The mask returns a value of none in the classes. remove that
        classes = classes[0:2]
        
        # Plot your data
        fig, ax = plt.subplots(figsize=(15, 6))
        im = ax.imshow(ndvi_landsat_class, cmap=nbr_cmap)
        
        ax.set_axis_off()
        plt.savefig('output/gren_cover_no_legend-'+file_name+'.png',bbox_inches='tight')


        image = Image.open('output/gren_cover_no_legend-'+file_name+'.png')
        image_smoothed = image.filter(ImageFilter.ModeFilter(size=15))

        image_smoothed = ax.imshow(image_smoothed, cmap=nbr_cmap)
        
        ep.draw_legend(im_ax=image_smoothed, classes=classes, titles=ndvi_cat_names)
        
    else:
            
        # Define color map
        nbr_colors = ["green"]
        nbr_cmap = ListedColormap(nbr_colors)

        # Define class names
        ndvi_cat_names = [
            "Vegetation"]
        
        # Plot your data
        fig, ax = plt.subplots(figsize=(15, 6))
        im = ax.imshow(ndvi_landsat_class, cmap=nbr_cmap)
        
        ax.set_axis_off()
        plt.savefig('output/gren_cover_no_legend-'+file_name+'.png',bbox_inches='tight')


        image = Image.open('output/gren_cover_no_legend-'+file_name+'.png')
        image_smoothed = image.filter(ImageFilter.ModeFilter(size=15))

        image_smoothed = ax.imshow(image_smoothed, cmap=nbr_cmap)
        
        ep.draw_legend(im_ax=image_smoothed, titles=ndvi_cat_names)

    # Plot your data
    #fig, ax = plt.subplots(figsize=(15, 6))
    #im = ax.imshow(ndvi_landsat_class, cmap=nbr_cmap)

    #ax.set_axis_off()
    #plt.savefig('output/gren_cover_no_legend.png',bbox_inches='tight')


    #image = Image.open('output/gren_cover_no_legend.png')
    #image_smoothed = image.filter(ImageFilter.ModeFilter(size=15))

    #image_smoothed = ax.imshow(image_smoothed, cmap=nbr_cmap)

    # text box
    textstr = '\n'.join((
        r'Forest cover: %.2f %%' % (green_cover, ),
        r'Total Sequestered Carbon amount: %.2f kg' % (seq_current, ),
        r'No of trees: %.0f' % (t_count, )))
    
    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    
    # place a text box in upper left in axes coords
    ax.text(0.50, 0.00, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)

    #ep.draw_legend(im_ax=image_smoothed, classes=classes, titles=ndvi_cat_names)
    ax.set_title(
    "Greenery Details of Your Land- Smoothed ",
    fontsize=14)
    
    plt.savefig('output/green_cover-'+file_name+'-'+str(green_cover).replace(".", "_" )+'-'+str(t_count)+'-smoothed.png',bbox_inches='tight')
    # plt.show()

    return plt,image
#green cover img save
# Forest cover plot
def get_green_cover_plot_smooth(ndvi,
                     ndvi_data,
                     green_cover,
                     file_name):

    # Apply the nodata mask to the newly classified NDVI data
    ndvi_landsat_class = np.ma.masked_where(np.ma.getmask(ndvi), 
                                            ndvi_data)
    if green_cover == 0.00:
    
        # Define color map
        nbr_colors = ["gray"]
        nbr_cmap = ListedColormap(nbr_colors)

        # Define class names
        ndvi_cat_names = ["No Vegetation"]
        
        # Plot your data
        fig, ax = plt.subplots(figsize=(15, 6))
        im = ax.imshow(ndvi_landsat_class, cmap=nbr_cmap)
        
        ax.set_axis_off()
        plt.savefig('output/green_cover/green_cover_no_legend-'+file_name+'.png',bbox_inches='tight')


        image = Image.open('output/green_cover/green_cover_no_legend-'+file_name+'.png')
        image_smoothed = image.filter(ImageFilter.ModeFilter(size=15))
        image_smoothed.save('output/green_cover_smooth/green_cover_no_legend-'+file_name+'.png', 'png')

        #image_smoothed = ax.imshow(image_smoothed, cmap=nbr_cmap)
        
        #ep.draw_legend(im_ax=image_smoothed, titles=ndvi_cat_names)
        

        
    elif (green_cover > 0.00 and green_cover < 100.00):
            
        # Define color map
        nbr_colors = ["gray", "green"]
        nbr_cmap = ListedColormap(nbr_colors)

        # Define class names
        ndvi_cat_names = [
            "No Vegetation",
            "Vegetation"]


        # Get list of classes
        classes = np.unique(ndvi_landsat_class)
        classes = classes.tolist()

        # The mask returns a value of none in the classes. remove that
        classes = classes[0:2]
        
        # Plot your data
        fig, ax = plt.subplots(figsize=(15, 6))
        im = ax.imshow(ndvi_landsat_class, cmap=nbr_cmap)
        
        ax.set_axis_off()
        plt.savefig('output/green_cover/green_cover_no_legend-'+file_name+'.png',bbox_inches='tight')


        image = Image.open('output/green_cover/green_cover_no_legend-'+file_name+'.png')
        image_smoothed = image.filter(ImageFilter.ModeFilter(size=15))
        image_smoothed.save('output/green_cover_smooth/green_cover_no_legend-'+file_name+'.png', 'png')
        
        #image_smoothed = ax.imshow(image_smoothed, cmap=nbr_cmap)
        
        #ep.draw_legend(im_ax=image_smoothed, classes=classes, titles=ndvi_cat_names)
        
    else:
            
        # Define color map
        nbr_colors = ["green"]
        nbr_cmap = ListedColormap(nbr_colors)

        # Define class names
        ndvi_cat_names = [
            "Vegetation"]
        
        # Plot your data
        fig, ax = plt.subplots(figsize=(15, 6))
        im = ax.imshow(ndvi_landsat_class, cmap=nbr_cmap)
        
        ax.set_axis_off()
        plt.savefig('output/green_cover/green_cover_no_legend-'+file_name+'.png',bbox_inches='tight')


        image = Image.open('output/green_cover/green_cover_no_legend-'+file_name+'.png')
        image_smoothed = image.filter(ImageFilter.ModeFilter(size=15))
        image_smoothed.save('output/green_cover_smooth/green_cover_no_legend-'+file_name+'.png', 'png')

        #image_smoothed = ax.imshow(image_smoothed, cmap=nbr_cmap)
        
        #ep.draw_legend(im_ax=image_smoothed, titles=ndvi_cat_names)

    # Plot your data
    #fig, ax = plt.subplots(figsize=(15, 6))
    #im = ax.imshow(ndvi_landsat_class, cmap=nbr_cmap)

    #ax.set_axis_off()
    #plt.savefig('output/gren_cover_no_legend.png',bbox_inches='tight')


    #image = Image.open('output/gren_cover_no_legend.png')
    #image_smoothed = image.filter(ImageFilter.ModeFilter(size=15))

    #image_smoothed = ax.imshow(image_smoothed, cmap=nbr_cmap)

    # text box
   
    # plt.show()
    path = 'output/green_cover_smooth/green_cover_no_legend-'+file_name+'.png'

    return image_smoothed,path

#return function

def get_cover(req,resol,l_thresh,up_thresh) :
    red = req[:, :, 2]
    nir = req[:, :, 3]
    ndvi = ndvi_api(red, nir)
    area = poly_area(req,resol)
    cloud_cover = np.count_nonzero(req[:, :, 4] == 1)*resol*resol*100/(area*1e6)
    g_pix, forest_area, ndvi_d = green_area(ndvi,resol,l_thresh,up_thresh)
    forest_cover = green_cover(forest_area,area)

    #fig = green_cover_plot(ndvi,forest_cover,t_count)
    #plt.show()
    
    return area,forest_cover, g_pix, forest_area,ndvi, ndvi_d, cloud_cover