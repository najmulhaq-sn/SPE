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
    