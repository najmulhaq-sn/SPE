#!/usr/bin/env python
# coding: utf-8

# In[4]:


#importing required libraries
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt

# Considering only the 1st Use Case - Bare Land/ Afforestation 
# User Inputs - Type of Species, Number of Trees

# Reading the csv with the stored data 

#reading the Growth chart related data
data = pd.read_csv(r"C:\Users\DELL\Documents\Python Scripts\SPE\Math_Est_Data.csv")

#reading the Carbon Fraction data
data_CF = pd.read_csv(r"C:\Users\DELL\Documents\Python Scripts\SPE\CF.csv")

#Above-ground Biomass estimation equation for Rubber trees:
#log10 W = 0.18 + 0.007 log10 D + 0.705 log10 HT+ 0.002 log10 AG
#where W – biomass, D – diameter, HT – height and AG - age of rubber trees 
#And W is in g/tree, D is in mm, HT is in cm
#------------------------------------------------------------------------------------------------------------------
#Log10_AGB[i] = 0.18 + (0.007*math.log(DBH[i],10)) + (0.705*math.log(Height[i],10)) + (0.002*math.log(Age[i],10))
#AGB[i] = 10**(Log10_AGB[i])

#AGB estimation for one Rubber tree
def calculate_AGB(df1):
    AGB_rubber = (10**(0.18 + (0.007*math.log(df1["DBH_in_mm"],10)) + (0.705*math.log(df1["Height_in_cm"],10)) + (0.002*math.log(df1["Age "],10))))
    return AGB_rubber

#AGB estimation for n Rubber trees
def calculate_totalAGB(n,df1):
    return n*df1.apply(calculate_AGB, axis=1)

#Carbon Sequestration estimation for n Rubber trees
def calculate_SEQ(n,CF,df1):
    return n*CF*df1.apply(calculate_AGB, axis=1)

def plot_SEQ(Species,n):
    
    df1 = data[data['Species - Common name'] == Species]
    CF = data_CF["Carbon Fraction"][data_CF['Species - Common Name'] == Species].item()
    
 
    df1 = df1[['Age ','DBH ','Height ']]

    #Converting DBH in cm to mm
    #Converting Height in m to cm
    df1["DBH_in_mm"]=10*df1["DBH "]
    df1["Height_in_cm"] = 100*df1["Height "]

    
    SEQ_lst = calculate_SEQ(n, CF, df1)
    SEQ_df = SEQ_lst.to_frame(name="Total Carbon Sequestration")
    #SEQ_df
    
    #Age vs Total C seq Estimation
    finaldf_SEQ = [df1["Age "], SEQ_df]

    result_SEQ = pd.concat(finaldf_SEQ, axis=1, join='inner')
    #display(result_SEQ)

    result_SEQ.plot(x ='Age ', y='Total Carbon Sequestration', kind = 'line')
    plt.title('Carbon Sequestration Estimation')
    plt.xlabel('Years')
    plt.ylabel('C-Seq in grams')
    plt.show()


# In[5]:


plot_SEQ("Rubber",50)


# In[6]:


plot_SEQ("Palmyrah",100)


# In[4]:




