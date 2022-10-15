import argparse
import requests
import json
import tqdm
import pandas as pd

from commodities import COMMODITIES

resources = {
    90: 'Sub-orbital 2nd Stage',
    91: 'Sub-orbital Rocket',
    92: 'Orbital Booster',
    93: 'Starship',
    94: 'BFR',
    95: 'Jumbo Jet',
    96: 'Luxury Jet',
    97: 'Single Engine Plane',
}

resources.update(COMMODITIES)

def main():
    with requests.Session() as r:
        prod = []
        for id, commodity in tqdm.tqdm(resources.items()): 
            data = r.get(f"https://www.simcompanies.com/api/v3/en/encyclopedia/resources/1/{id}/").json()
            prod.append({'Commodity': commodity, 'Production': data['producedAnHour']})
        
        df = pd.DataFrame.from_records(prod, index='Commodity').sort_index()
        print(df)

        df.to_csv(f'production_rates.csv')

if __name__ == "__main__":
    main()
