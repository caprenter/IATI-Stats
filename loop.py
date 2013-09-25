import os
from lxml import etree
import inspect
import json
import sys
import decimal
import argparse

from settings import *

parser = argparse.ArgumentParser()
parser.add_argument("--debug", help="Output extra debugging information",
                    action="store_true")
parser.add_argument("--strict", help="Follow the schema strictly",
                    action="store_true")
args = parser.parse_args()

import stats

def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

def process_file(inputfile, outputfile):
    try:
        root = etree.parse(inputfile).getroot()
        if root.tag == 'iati-activities':
            out = []
            for activity in root:
                activity_out = {}
                activity_stats = stats.ActivityStats(activity)
                activity_stats.strict = args.strict
                activity_stats.context = 'in '+inputfile
                for name, function in inspect.getmembers(activity_stats, predicate=inspect.ismethod):
                    if name.startswith('_'): continue
                    activity_out[name] = function()
                if args.debug:
                    print activity_out
                out.append(activity_out)
            with open(outputfile, 'w') as outfp:
                json.dump(out, outfp, sort_keys=True, indent=2, default=decimal_default)
        else:
            print 'No support yet for {0} in {1}'.format(root.tag, inputfile)
    except etree.ParseError:
        print 'Could not parse file {0}'.format(inputfile)

if __name__ == '__main__':
    for folder in os.listdir(DATA_DIR):
        if not os.path.isdir(os.path.join(DATA_DIR, folder)) or folder == '.git':
            continue
        for xmlfile in os.listdir(os.path.join(DATA_DIR, folder)):
            try: os.makedirs(os.path.join(OUTPUT_DIR,folder))
            except OSError: pass
            process_file(os.path.join(DATA_DIR,folder,xmlfile),
                         os.path.join(OUTPUT_DIR,folder,xmlfile))

