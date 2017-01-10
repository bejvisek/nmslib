#!/usr/bin/python

import sys
import os
import argparse
import gzip
import readbindata


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


def print_vector(vector):
    output.write(': 1, '.join([str(x) for x in vector]))
    output.write('\n')


counter = 0
for record in readbindata.read_records(args):
    print_vector(record)
    counter += 1


if args.output:
    output.close()

print >> sys.stderr, "processed ", counter, " objects"



