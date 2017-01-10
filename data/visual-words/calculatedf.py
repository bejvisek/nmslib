#!/usr/bin/python

import sys
import os
import argparse
import gzip
import readbindata

from collections import Counter


p = argparse.ArgumentParser(description='reads in data objects in binary format (2 files) and prints out the same data as text', parents=[readbindata.get_arg_parser()])
p.add_argument('-o', '--output', help='output file (possible .gz) - use stdout, if not specified')
args = p.parse_args()

# output file
output = sys.stdout
if args.output:
    if os.path.splitext(args.output)[1] == ".gz":
        output = gzip.open(args.output, "wb")
    else:
        output = open(args.output, "w")


# def print_vector(vector):
#     output.write(': 1, '.join([str(x) for x in vector]))
#     output.write('\n')
#

dfs = Counter()


def update_dfs(record):
    for i in record:
        dfs[i] += 1


counter = 0
for record in readbindata.read_records(args):
    update_dfs(record)
    counter += 1

output.write(str(dict(dfs)))


if args.output:
    output.close()

if args.output:
    # try to read the data in again
    dfs_dict = eval(open(args.output, 'r').read())
    print >> sys.stderr, str(dfs_dict)


print >> sys.stderr, "processed ", counter, " objects"



