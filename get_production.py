import argparse
import requests
import json
import tqdm
import pandas as pd
from collections import OrderedDict

commodity_dict = OrderedDict({
    1:  'Power',
    2:  'Water',
    3:  'Apples',
    4:  'Oranges',
    5:  'Grapes',
    6:  'Grain',
    7:  'Steak',
    8:  'Sausages',
    9:  'Eggs',
    10: 'Crude Oil',
    11: 'Petrol',
    12: 'Diesel',
    13: 'Transport',
    14: 'Minerals',
    15: 'Bauxite',
    16: 'Silicon',
    17: 'Chemicals',
    18: 'Aluminium',
    19: 'Plastic',
    20: 'Processors',
    21: 'Electronic Components',
    22: 'Batteries',
    23: 'Displays',
    24: 'Smart Phones',
    25: 'Tablets',
    26: 'Laptops',
    27: 'Monitors',
    28: 'Televisions',
    29: 'Plant Research',
    30: 'Energy Research',
    31: 'Mining Research',
    32: 'Electronics Research',
    33: 'Breeding Research',
    34: 'Chemistry Research',
    35: 'Software',
    
    40: 'Cotton',
    41: 'Fabric',
    42: 'Iron Ore',
    43: 'Steel',
    44: 'Sand',
    45: 'Glass',
    46: 'Leather',
    47: 'On-board Computer',
    48: 'Electric Motor',
    49: 'Luxury Car Interior',
    50: 'Basic Interior',
    51: 'Car Body',
    52: 'Combustion Engine',
    53: 'Economy E-car',
    54: 'Luxury E-car',
    55: 'Economy Car',
    56: 'Luxury Car',
    57: 'Truck',
    58: 'Automotive Research',
    59: 'Fashion Research',
    60: 'Underwear',
    61: 'Gloves',
    62: 'Dresses',
    63: 'Stilletto Heel',
    64: 'Handbags',
    65: 'Sneakers',
    66: 'Seeds',
    67: 'Crackers',
    68: 'Gold Ore',
    69: 'Golden Bars',
    70: 'Luxury Watch',
    71: 'Necklace',
    72: 'Sugar Cane',
    73: 'Ethanol',
    74: 'Methane',
    75: 'Carbon Fibers',
    76: 'Carbon Composite',
    77: 'Fuselage',
    78: 'Wing',
    79: 'High-grade E-comps',
    80: 'Flight Computer',
    81: 'Cockpit',
    82: 'Attitude Control',
    83: 'Rocket Fuel',
    84: 'Propellant Tank',
    85: 'Solid Fuel Booster',
    86: 'Rocket Engine',
    87: 'Heat Shield',
    88: 'Ion Drive',
    89: 'Jet Engine',
    90: 'Sub-orbital 2nd Stage',
    91: 'Sub-orbital Rocket',
    92: 'Orbital Booster',
    93: 'Starship',
    94: 'BFR',
    95: 'Jumbo Jet',
    96: 'Luxury Jet',
    97: 'Single Engine Plane',
    98: 'Quadcopter',
    99: 'Satellite',
    100: 'Aerospace Research',
    101: 'Reinforced Concrete',
    102: 'Bricks',
    103: 'Cement',
    104: 'Clay',
    105: 'Limestone',
    106: 'Wood',
    107: 'Steel Beams',
    108: 'Planks',
    109: 'Windows',
    110: 'Tools',
    111: 'Construction Units',
    112: 'Bulldozer',
    113: 'Materials Research'
})

def main():
    with requests.Session() as r:
        prod = []
        for id, commodity in tqdm.tqdm(commodity_dict.items()): 
            data = r.get(f"https://www.simcompanies.com/api/v3/en/encyclopedia/resources/1/{id}/").json()
            prod.append({'Commodity': commodity, 'Production': data['producedAnHour']})
        
        df = pd.DataFrame.from_records(prod, index='Commodity').sort_index()
        print(df)

        df.to_csv(f'production_rates.csv')

if __name__ == "__main__":
    main()
