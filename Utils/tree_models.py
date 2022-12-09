from dataclasses import dataclass, field
from enum import Enum 


class species_category(Enum):
    broadLeavedSpecies = 0
    coniferousTree = 1

class region_type(Enum):
    tropicalHumidRegion = 0
    tropicalDryRegions = 1


@dataclass
class NDVI_threasholds:
    lower_bound: float
    upper_bound: float

@dataclass
class geo_dependant_param:
    region: region_type
    annual_rainfall: float


@dataclass
class tree_geo_specifications:
    species_general_type: species_category
    region: region_type
    annual_rainfall: float
    dbh_cm: float
    height_m: float



