import pandas as pd
import numpy as np
import pathlib
import argparse

df0 = pd.DataFrame(columns=['Time', 'Economy', 'SEP', 'Luxury Jet', 'Jumbo', 'SOR', 'BFR', 'Satellite'])
mapper = {'Sin': 'SEP', 'Lux':'Luxury Jet', 'Jum': 'Jumbo', 'Sub': 'SOR', 'Sat': 'Satellite'}
    
def load_prices(prices_dir: str):
    dfs = []
    for file in pathlib.Path(prices_dir).glob('*.hdf'):
        try:
            df = pd.read_hdf(file, 'prices').rename(columns=mapper)
        except:
            df = pd.read_hdf(file, 'test')
        dfs.append(df)
    print(f'Loaded {len(dfs)} files')    
    as_prices = pd.concat([df0] + dfs, join='outer').sort_values('Time')

    return as_prices

def load_quantities(quantities_dir: str):
    dfs = []
    for file in pathlib.Path(quantities_dir).glob('*.hdf'):
        try:
            df = pd.read_hdf(file, 'quantities').rename(columns=mapper)
        except:
            pass
        dfs.append(df)        
    as_quantities = pd.concat([df0] + dfs, join='outer').sort_values('Time').fillna(0)
    return as_quantities

def weighted_avg_and_std(values, weights):
    average = np.average(values, weights=weights)
    variance = np.average((values-average)**2, weights=weights)
    return (average, np.sqrt(variance))

def get_stats_weighted(as_prices, commodity, economy, decay=1.0):
    cond1 = [not(np.isnan(x)) for x in as_prices[commodity].values]
    cond2 = as_prices['Economy'] == economy
    locs = np.where(cond1 & cond2)[0]
    #print(commodity, ':', len(locs))
    if len(locs) > 0:
        x = as_prices.iloc[locs][commodity]
        ts = as_prices['Time'].values[locs]
        ws = np.exp(-decay*(ts[-1] - ts) / np.timedelta64(1, 'D'))
        return weighted_avg_and_std(x, ws)
    else:
        return np.nan, np.nan

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prices_dir", type=str, default="SalesOfficePrices", help="Directory to read prices from")
    parser.add_argument("--quantities_dir", type=str, default="SalesOfficeQuantities", help="Directory to store quantities")
    parser.add_argument("--weight_decay", type=float, default=0.1, help="Decay of weights over time")
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()

    # Load prices
    as_prices = load_prices(args.prices_dir)

    # Get stats (weighted)
    aerospace = ['SEP','Luxury Jet','Jumbo','SOR','BFR','Satellite']
    recession = [get_stats_weighted(as_prices, commodity, 'R', decay=args.weight_decay) for commodity in aerospace]
    normal = [get_stats_weighted(as_prices, commodity, 'N', decay=args.weight_decay) for commodity in aerospace]
    boom = [get_stats_weighted(as_prices, commodity, 'B', decay=args.weight_decay) for commodity in aerospace]
    
    # Get average quantity
    as_quantities = load_quantities(args.quantities_dir)
    p = np.array([3.5, 2.5, 2.5, 2.5, 2.5, 2.5])
    n = as_quantities.shape[0]
    freq = [len(np.where(as_quantities[commodity]>0)[0])/n for commodity in aerospace]
    quantity = np.atleast_2d(freq * p).T

    # Store results
    df = pd.DataFrame(np.hstack([quantity, recession, normal, boom]), columns=['Quantity','Recession Mean','Recession Std. dev.','Normal Mean','Normal Std. dev.','Boom Mean','Boom Std. dev.'], index=aerospace)
    df.to_csv('salesoffice_stats.csv')
    print(df)
    
    return

if __name__ == "__main__":
    main()
