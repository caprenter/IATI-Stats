import json
import os, sys
from collections import defaultdict
from settings import *

def invert(basedirname, out_filename):
    """
    This 'inverts' the aggregated json files produced by aggregate.py
    ie. it creates a json file of the stats grouped by value, and then by
    publisher.

    """
    out = defaultdict(lambda: defaultdict(dict))

    for dirname, dirs, files in os.walk(os.path.join(OUTPUT_DIR, basedirname)):
        for f in files:
            with open(os.path.join(dirname ,f)) as fp:
                for stats_name,stats_values in json.load(fp).items():
                    if type(stats_values) == dict:
                        for k,v in stats_values.items():
                            if type(v) == dict:
                                if not k in out[stats_name]:
                                    out[stats_name][k] = defaultdict(dict)
                                for k2,v2 in v.items():
                                    out[stats_name][k][k2][f[:-5]] = v2
                            else:
                                out[stats_name][k][f[:-5]] = v
                    elif type(stats_values) == int:
                        if not stats_name in out:
                            out[stats_name] = defaultdict(int)
                        out[stats_name][f[:-5]] += stats_values

    with open(os.path.join(OUTPUT_DIR, out_filename+'.json'), 'w') as fp:
            json.dump(out, fp, sort_keys=True, indent=2)

    for statname, inverted in out.items():
        with open(os.path.join(OUTPUT_DIR, out_filename, statname+'.json'), 'w') as fp:
            json.dump(inverted, fp, sort_keys=True, indent=2)

if __name__ == '__main__':
    for dirname in ['inverted-publisher', 'inverted-file', 'inverted-file-publisher']:
        try:
            os.mkdir(os.path.join(OUTPUT_DIR, dirname))
        except OSError: pass
    invert('aggregated-publisher', 'inverted-publisher')
    invert('aggregated-file', 'inverted-file')
    for folder in os.listdir(os.path.join(OUTPUT_DIR, 'aggregated-file')):
        try:
            os.mkdir(os.path.join(OUTPUT_DIR, 'inverted-file-publisher', folder))
        except OSError: pass
        invert(os.path.join('aggregated-file', folder), os.path.join('inverted-file-publisher', folder))
