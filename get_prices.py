import numpy as np
import pandas as pd
import argparse

from collections import OrderedDict
import urllib.request
import ast
import time, os

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
    47: 'On-board computer',
    48: 'Electric motor',
    49: 'Luxury car interior',
    50: 'Basic interior',
    51: 'Car body',
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
    80: 'Flight computer',
    81: 'Cockpit',
    82: 'Attitude Control',
    83: 'Rocket Fuel',
    84: 'Propellant Tank',
    85: 'Solid Fuel Booster',
    86: 'Rocket Engine',
    87: 'Heat Shield',
    88: 'Ion Drive',
    89: 'Jet Engine',
    
    98:  'Quadcopter',

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


def get_offers(id):
    print('- Obtaining offers for %s' % commodity_dict[id])
    response = urllib.request.urlopen('https://www.simcompanies.com/api/v2/market/%d' % id)
    dict_str = response.read().decode("UTF-8").replace("false", "False").replace("true", "True").replace("null", "None")
    try:
        offers = ast.literal_eval(dict_str)
    except:
        raise Exception (dict_str)
    return offers


def print_offers(offers):
    print(commodity_dict[id])
    for offer in offers:
        quality = offer["quality"]
        price = offer["price"]
        quantity = offer["quantity"]
        print('Q%d: %1.1f (%d)' % (quality, price, quantity))
    

def get_prices_by_q(offers):
    qp = np.array([[offer['quality'], offer['price']] for offer in offers])
    qs = np.array(qp[:,0], dtype=int)
    ps = qp[:,1]
    qmax = np.max(qs)
    prices = {0:ps[0]}
    for q in range(1,qmax+1):
        p = ps[np.where(qs >= q)[0][0]]
        #print('Q%d: %1.1f' % (q, p))
        prices[q] = p
    
    return prices


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", type=str, default="CommodityPrices", help="Directory to store outputs")
    parser.add_argument("--format", type=str, default='hdf', help="Choose output format (CSV, HDF)")
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    # Main loop for obtaining offers and extracting prices by Q
    prices = [get_prices_by_q(get_offers(id)) for id, name in commodity_dict.items()]

    # Convert to dataframe to facilitate writing to CSV/HDF
    df = pd.DataFrame(prices, index=commodity_dict.values()).sort_index()
    print(df)

    timestr = time.strftime("%Y%m%d-%H%M%S")

    if args.format == 'csv':
        df.to_csv('prices.csv')
        df.to_csv(f'{args.output_dir}/{timestr}.csv')
    elif args.format == 'hdf':
        df.to_hdf('prices.hdf', 'commodity_prices')
        df.to_csv(f'{args.output_dir}/{timestr}.hdf', 'commodity_prices')
    else:
        raise ValueError(f'Unknown format: {args.format}')


if __name__ == "__main__":
    main()
