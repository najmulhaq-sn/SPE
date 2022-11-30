# -*- coding: utf-8 -*-
"""

"""

import numpy as np
import pandas as pd
import math
import os
# import tree_models as tree_model
from Utils import tree_models_new as tree_model

'''
DBH - in cm
H - in m
rainfall - in mm

'''

POUND_TO_KG = 0.453592
M_TO_FT = 3.28084
CM_TO_FT = 0.0328084
CM_TO_INCH = 0.393701 


# bellow functions will follow naming pattern of <species>_<Region>_<rainFall>_<DBH>
# this gives total dry weight ( below ground + above ground)
def notKnown_notKnown_notKnown_notKnown(tree_land_spec, num_trees):
    '''
        https://dreamcities.org/measure-carbon/
    '''
    height_ft = tree_land_spec.height_m * M_TO_FT
    dbh_inch = tree_land_spec.dbh_cm * CM_TO_INCH

    species_dep_coeff = None
    if dbh_inch < 11:
        species_dep_coeff = 0.25
    elif dbh_inch >= 11:
        species_dep_coeff = 0.15

    weight_above_ground_kg = species_dep_coeff*(dbh_inch**2) * height_ft * POUND_TO_KG

    # here not multiplying by the factor 1.2, since the 20% corresponds to below ground mass
    weight_total_green_weight_kg = weight_above_ground_kg

    weight_dry_weight_kg = 0.725*weight_total_green_weight_kg

    weight_carbon_kg = 0.5 * weight_dry_weight_kg

    return weight_carbon_kg*num_trees


def broadLeavedSpecies_tropicalDryRegions_le900_3To30(tree_land_spec, num_trees):

    above_ground_biomass_kg = 10 ** (-0.535 + (np.log10(np.pi * ((tree_land_spec.dbh_cm**2)/4))))
    
    c_seq = above_ground_biomass_kg * 0.5

    return c_seq * num_trees

def broadLeavedSpecies_tropicalDryRegions_900To1500_5To40(tree_land_spec, num_trees):

    above_ground_biomass_kg = np.exp(-1.996 + 2.32*np.log(tree_land_spec.dbh_cm))
    
    c_seq = above_ground_biomass_kg * 0.5

    return c_seq * num_trees


def broadLeavedSpecies_tropicalHumidRegion_1500To4000_le60(tree_land_spec, num_trees):

    above_ground_biomass_kg = np.exp(-2.134 + (2.530 * np.log(tree_land_spec.dbh_cm)))

    c_seq = above_ground_biomass_kg * 0.5

    return c_seq * num_trees

def broadLeavedSpecies_tropicalHumidRegion_1500To4000_60To148(tree_land_spec, num_trees):

    above_ground_biomass_kg = 42.69 - (12.800 * tree_land_spec.dbh_cm) + (1.242 * (tree_land_spec.dbh_cm**2))

    c_seq = above_ground_biomass_kg * 0.5

    return c_seq * num_trees

def broadLeavedSpecies_tropicalWetRegion_Gr4000_4To112(tree_land_spec, num_trees):

    above_ground_biomass_kg = 21.297 - (6.953 * tree_land_spec.dbh_cm) + (0.740 * (tree_land_spec.dbh_cm**2))

    c_seq = above_ground_biomass_kg * 0.5

    return c_seq * num_trees

def ConiferousSpecies_Any_Any_2To52(tree_land_spec, num_trees):

    above_ground_biomass_kg = np.exp(-1.170 + (2.119 * np.log(tree_land_spec.dbh_cm)))

    c_seq = above_ground_biomass_kg * 0.5

    return c_seq * num_trees

def ConiferousTaxodiumDistichumSpecies_Any_Any_Any(tree_land_spec, num_trees):

    above_ground_biomass_kg = -1.398 + (2.731 * np.log10(tree_land_spec.dbh_cm))

    c_seq = above_ground_biomass_kg * 0.5

    return c_seq * num_trees

def PalmSpecies_Any_Any_Gr7point5(tree_land_spec, num_trees):
    
    above_ground_biomass_kg = 10 + (6.4 * tree_land_spec.height_m)

    c_seq = above_ground_biomass_kg * 0.5

    return c_seq * num_trees


# For Testing & Validation

species_type = "broadLeavedSpecies"
region_type = "tropicalDryRegions"
annual_rainfall = 0
DBH_cm = 24.641
Height_m = 15.384

tree_land_spec = tree_model.tree_geo_specifications(    tree_model.species_category[species_type],
                                                        tree_model.region_type[region_type],
                                                        annual_rainfall,
                                                        DBH_cm,
                                                        Height_m
                                                    ) 
print(tree_land_spec.height_m)
print("Broad/dry/<900/3-30 : ", broadLeavedSpecies_tropicalDryRegions_le900_3To30(tree_land_spec,1))
print("Broad/dry/900-1500/5-40 : ", broadLeavedSpecies_tropicalDryRegions_900To1500_5To40(tree_land_spec,1))
print("Broad/humid/1500-4000/<60 : ", broadLeavedSpecies_tropicalHumidRegion_1500To4000_le60(tree_land_spec,1))
print("Broad/humid/1500-4000/60-148 : ", broadLeavedSpecies_tropicalHumidRegion_1500To4000_60To148(tree_land_spec,1))
print("Broad/wet/>4000/4-112 : ", broadLeavedSpecies_tropicalWetRegion_Gr4000_4To112(tree_land_spec,1))
print("Conifer/Any/Any/2-52 : ", ConiferousSpecies_Any_Any_2To52(tree_land_spec,1))
print("Conifer-TaxodiumD/Any/Any/2-52 : ", ConiferousTaxodiumDistichumSpecies_Any_Any_Any(tree_land_spec,1))
print("PaLm/Any/Any/>7.5 : ", PalmSpecies_Any_Any_Gr7point5(tree_land_spec, 1))

print("Gen Equation : ", notKnown_notKnown_notKnown_notKnown(tree_land_spec, 1))