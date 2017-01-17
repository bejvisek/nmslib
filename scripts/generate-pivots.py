#!/usr/bin/python


import numpy as np
import argparse

parser = argparse.ArgumentParser('generate random projection pivots for sparse vectors')
parser.add_argument('-t', '--termid_number', help='dimensions taken from interval [0, termid_number)', type=int, required=True)
parser.add_argument('-d', '--dimensionality', help='number of random projections to generate', type=int, required=True)
parser.add_argument('-n', '--pivot_number', help='number of pivots to generate', type=int, required=True)
args = parser.parse_args()

value = np.sqrt(float(1) / float(args.dimensionality))
for i in range(0, args.pivot_number):
    pivots = set()
    while len(pivots) < args.dimensionality:
        pivots.update(np.random.choice(args.termid_number, args.dimensionality - len(pivots)))

    sorted = list(pivots)
    sorted = np.sort(sorted)
    pivotstr = ''
    for d in sorted:
        pivotstr += str(d) + ':' + ('%.3f' % value) + ' '
    print pivotstr