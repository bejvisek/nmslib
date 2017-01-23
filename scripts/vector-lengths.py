#!/usr/bin/python
import gzip
import os

import numpy as np
import argparse
from scipy import stats

import sys

parser = argparse.ArgumentParser('calculates distribution of the vector lengths')
parser.add_argument('-d', '--data_file', help='file with the NMSLIB sparse vector data', required=True)
parser.add_argument('-n', '--number', help='if used, just the first "n" lines are taken', type=int, default=sys.maxint)
args = parser.parse_args()

# output file
if os.path.splitext(args.data_file)[1] == ".gz":
    input = gzip.open(args.data_file, "rt")
else:
    input = open(args.data_file, "rt")

lengths = []
counter = 0
for line in input:
    if counter >= args.number:
        break
    lengths.append(len(line.strip().split(' ')))
    counter += 1


print "percentiles 10, 20, 30, 40, 50, 60, 70, 80, 99: ", stats.scoreatpercentile(lengths, [10, 20, 30, 40, 50, 60, 70, 80, 90])
print "average: ", stats.nanmean(lengths)
print "standard dev: ", np.std(lengths)