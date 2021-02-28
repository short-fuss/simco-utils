from PIL import Image
import pytesseract
import pathlib
import argparse
import os, time
import numpy as np
import pandas as pd


def parse_term(t, return_quantity=False):
    eachs = [i for i in range(len(t)) if t.startswith('each', i)]
    if return_quantity:
        qs = [int(t[i+1]) for i in range(len(t)) if t.startswith('/', i)]
    
    ps = [int(t[:e-1].split('$')[-1].replace(',','')) for e in eachs]
    cs = [t[e+5:e+8] for e in eachs]
    prices = dict(zip(cs, ps))
    prices['Bonus'] = float(t[:t.find('%')].split('\n')[-1])

    if return_quantity:
        return prices, dict(zip(cs, qs))
    else:
        return prices


def load_screenshot(ss):
    '''Process PNGs with OCR and extract prices'''
    str = pytesseract.image_to_string(Image.open(ss))
    terms = str.split('TERMS')[1:]
    print(f'Found {len(terms)} terms')
    ps = [parse_term(t) for t in terms]
    return ps

def load_textfile(ss):
    '''Process screen text copy and extract prices and quantities'''
    str = open(ss).read()
    terms = str.split('TERMS')[1:-1]
    print(f'Found {len(terms)} terms')
    ps, qs = zip(*[parse_term(t, return_quantity=True) for t in terms])
    return ps, qs


def process_record(ps, ctime, economy, output_path, key):
    os.makedirs(output_path.parent, exist_ok=True)
    df = pd.DataFrame.from_records(ps)
    df['Time'] = ctime
    df['Economy'] = economy
    if output_path.suffix == '.hdf':
        df.to_hdf(output_path, key, mode='w')
    elif output_path.suffix == '.csv':
        df.to_csv(output_path, mode='w')
    print('Wrote file:', output_path)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="File to convert")
    parser.add_argument("--prices_dir", type=str, default="SalesOfficePrices", help="Directory to store prices")
    parser.add_argument("--quantities_dir", type=str, default="SalesOfficeQuantities", help="Directory to store quantities")
    parser.add_argument("--economy", choices=['R', 'N', 'B'], help="Economy")
    parser.add_argument("--overwrite", default=False, action='store_true', help="Overwrite existing results HDF")
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    print('Processing ', args.file)
    ext = os.path.splitext(args.file)[1]
    created = time.localtime(os.path.getmtime(args.file))
    ctime = np.datetime64(time.strftime('%Y-%m-%d %H:%M:%S', created))
    ftime = time.strftime('%Y-%m-%d T%H%M%S', created)

    prices_path = pathlib.Path(f'{args.prices_dir}/{ftime}.hdf')
    if os.path.exists(prices_path) and not(args.overwrite):
        print('Target already exists:', filename)
    else:
        if ext == '.png':
            # N.B. OCR doesn't recognise the quantities bar
            ps = load_screenshot(args.file)
        else:
            ps, qs = load_textfile(args.file)
            quantities_path = pathlib.Path(f'{args.quantities_dir}/{ftime}.hdf')
            process_record(qs, ctime, args.economy, quantities_path, 'quantities')            
        process_record(ps, ctime, args.economy, prices_path, 'prices')
    
    return

if __name__ == "__main__":
    main()
