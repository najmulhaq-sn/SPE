# -*- coding: utf-8 -*-
"""

"""

import numpy as np
import pandas as pd
import math
import os
# import tree_models as tree_model

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


def broadLeavedSpecies_tropicalHumidRegion_le1500_5To40(tree_land_spec, num_trees):

    above_ground_biomass_kg = 34.4703 - 8.0671*tree_land_spec.dbh_cm + 0.6589*(tree_land_spec.dbh_cm**2)

    return above_ground_biomass_kg * num_trees * 0.5


def broadLeavedSpecies_tropicalHumidRegion_1500To4000_le60(tree_land_spec, num_trees):

    above_ground_biomass_kg = np.exp(-2.134 + 2.530 *np.log(tree_land_spec.dbh_cm) )

    return above_ground_biomass_kg * num_trees * 0.5


def broadLeavedSpecies_tropicalDryRegions_900To1500_5To40(tree_land_spec, num_trees):

    above_ground_biomass_kg = np.exp(-1.996 + 2.32*np.log(tree_land_spec.dbh_cm))

    return above_ground_biomass_kg * num_trees * 0.5