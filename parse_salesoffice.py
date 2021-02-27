from PIL import Image
import pytesseract
from pathlib import Path
import glob
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


def process_record(ps, ctime, economy, filename, key):
    df = pd.DataFrame.from_records(ps)
    df['Time'] = ctime
    df['Economy'] = economy
    df.to_hdf(filename, key, mode='w')
    print('Wrote file:', filename)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="File to convert")
    parser.add_argument("--output_dir", type=str, default="SalesOfficePrices", help="Directory to store outputs")
    parser.add_argument("--economy", type=str, help="Economy")
    parser.add_argument("--overwrite", action='store_true', help="Overwrite existing results HDF")
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    print('Processing ', args.file)
    ext = os.path.splitext(args.file)[1]
    created = time.localtime(os.path.getmtime(args.file))
    ctime = np.datetime64(time.strftime('%Y-%m-%d %H:%M:%S', created))
    ftime = time.strftime('%Y-%m-%d T%H%M%S', created)

    os.makedirs(args.output_dir, exist_ok=True)
    filename = f'{args.output_dir}/{ftime}.hdf'
    if os.path.exists(filename) and not(args.overwrite):
        print('Target already exists:', filename)
    else:
        if ext == '.png':
            # N.B. OCR doesn't recognise the quantities bar
            ps = load_screenshot(args.file)
        else:
            ps, qs = load_textfile(args.file)
            process_record(qs, ctime, args.economy, filename, 'quantities')            
        process_record(ps, ctime, args.economy, filename, 'prices')
    
    return

if __name__ == "__main__":
    main()
