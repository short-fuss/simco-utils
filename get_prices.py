import numpy as np
import pandas as pd
import argparse
import tqdm

from collections import OrderedDict
import urllib.request
import ast
import time, os

from commodities import COMMODITIES


def get_offers(id):
    #print('- Obtaining offers for %s' % commodity_dict[id])
    response = urllib.request.urlopen('https://www.simcompanies.com/api/v2/market/%d' % id)
    dict_str = response.read().decode("UTF-8").replace("false", "False").replace("true", "True").replace("null", "None")
    try:
        offers = ast.literal_eval(dict_str)
    except:
        raise Exception (dict_str)
    return offers


def print_offers(offers):
    print(COMMODITIES[id])
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
    parser.add_argument("--format", type=str, default='csv', help="Choose output format (CSV, HDF)")
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    # Main loop for obtaining offers and extracting prices by Q
    prices = [get_prices_by_q(get_offers(id)) for id, name in tqdm.tqdm(COMMODITIES.items())]

    # Convert to dataframe to facilitate writing to CSV/HDF
    df = pd.DataFrame(prices, index=COMMODITIES.values()).sort_index()
    print(df)

    timestr = time.strftime("%Y%m%d-%H%M%S")

    if args.format == 'csv':
        df.to_csv('prices.csv')
        df.to_csv(f'{args.output_dir}/{timestr}.csv')
    elif args.format == 'hdf':
        df.to_hdf('prices.hdf', 'commodity_prices')
        df.to_hdf(f'{args.output_dir}/{timestr}.hdf', 'commodity_prices')
    else:
        raise ValueError(f'Unknown format: {args.format}')


if __name__ == "__main__":
    main()
