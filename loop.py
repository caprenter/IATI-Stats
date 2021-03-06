import os
from lxml import etree
import inspect
import json
import sys
import traceback
import decimal
import argparse
import statsfunctions

from settings import *


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

def call_stats(this_stats, args):
    this_out = {}
    for name, function in inspect.getmembers(this_stats, predicate=inspect.ismethod):
        if not statsfunctions.use_stat(this_stats, name): continue
        try:
            this_out[name] = function()
        except KeyboardInterrupt:
            exit()
        except:
            traceback.print_exc(file=sys.stdout)
    if args.debug:
        print this_out
    return this_out


def process_file((inputfile, outputfile, args)):
    import importlib
    stats = importlib.import_module(args.stats_module)

    try:
        doc = etree.parse(inputfile)
        root = doc.getroot()
        def process_stats(FileStats, ElementStats, tagname=None):
            file_stats = FileStats()
            file_stats.doc = doc
            file_stats.root = root
            file_stats.strict = args.strict
            file_stats.context = 'in '+inputfile
            file_stats.fname = os.path.basename(inputfile)
            file_stats.inputfile = inputfile
            file_out = call_stats(file_stats, args)
            out = []
            for element in root:
                if tagname and tagname != element.tag: continue
                element_stats = ElementStats()
                element_stats.element = element
                element_stats.strict = args.strict
                element_stats.context = 'in '+inputfile
                element_out = call_stats(element_stats, args)
                out.append(element_out)
            with open(outputfile, 'w') as outfp:
                json.dump({'file':file_out, 'elements':out}, outfp, sort_keys=True, indent=2, default=decimal_default)

        if root.tag == 'iati-activities':
            process_stats(stats.ActivityFileStats, stats.ActivityStats, 'iati-activity')
        elif root.tag == 'iati-organisations':
            process_stats(stats.OrganisationFileStats, stats.OrganisationStats, 'iati-organisation')
        else:
            with open(outputfile, 'w') as outfp:
                json.dump({'file':{'nonstandardroots':1}, 'elements':[]}, outfp, sort_keys=True, indent=2)
    except etree.ParseError:
        print 'Could not parse file {0}'.format(inputfile)
        if os.path.getsize(inputfile) == 0:
            # Assume empty files are download errors, not invalid XML
            with open(outputfile, 'w') as outfp:
                json.dump({'file':{'emptyfile':1}, 'elements':[]}, outfp, sort_keys=True, indent=2)
        else:
            with open(outputfile, 'w') as outfp:
                json.dump({'file':{'invalidxml':1}, 'elements':[]}, outfp, sort_keys=True, indent=2)


def loop_folder(folder, args, data_dir=DATA_DIR, output_dir=OUTPUT_DIR):
    if not os.path.isdir(os.path.join(data_dir, folder)) or folder == '.git':
        return []
    files = []
    for xmlfile in os.listdir(os.path.join(data_dir, folder)):
        try: os.makedirs(os.path.join(output_dir,'loop',folder))
        except OSError: pass
        try:
            files.append((os.path.join(data_dir,folder,xmlfile),
                         os.path.join(output_dir,'loop',folder,xmlfile), args))
        except UnicodeDecodeError:
            traceback.print_exc(file=sys.stdout)
            continue
    return files

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="Output extra debugging information",
                        action="store_true")
    parser.add_argument("--strict", help="Follow the schema strictly",
                        action="store_true")
    parser.add_argument("--stats-module", help="Name of module to import stats from", default='stats')
    parser.add_argument("--folder", help="Limit to a specific folder in the data")
    parser.add_argument("--data", help="Data directory", default=DATA_DIR)
    parser.add_argument("--output", help="Output directory", default=OUTPUT_DIR)
    parser.add_argument("--multi", help="Number of processes", default=1, type=int)

    args = parser.parse_args()

    if args.folder:
        files = loop_folder(args.folder, args, data_dir=args.data, output_dir=args.output)
    else:
        files = []
        for folder in os.listdir(args.data):
            files += loop_folder(folder, args, data_dir=args.data, output_dir=args.output)

    if args.multi > 1:
        from multiprocessing import Pool
        pool = Pool(args.multi)
        pool.map(process_file, files)
    else:
        map(process_file, files)
