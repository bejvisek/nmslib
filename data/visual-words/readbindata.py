#!/usr/bin/python

import sys
import os
import argparse
import gzip

import struct

p = argparse.ArgumentParser(add_help=False)
p.add_argument('-d', '--data', required=True, help='data file name')
p.add_argument('-l', '--lengths', required=True, help='file with the lengths of the visual documents')
p.add_argument('-n', '--number', help='max number of records to print (optional)', type=int)


def get_arg_parser():
    return p


def lengths(length_file):
    length_stream = open(length_file, 'rb')
    while True:
        try:
            retval = struct.unpack('i', length_stream.read(4))[0]
            if retval and retval is not '':
                yield retval
            else:
                break
        except Exception:
            break


def read_records(args):
    maxvalue = sys.maxint
    if args.number:
        maxvalue = args.number
    datafile = open(args.data, 'rb')

    counter = 0
    for length in lengths(args.lengths):
        if counter >= maxvalue:
            break
        vector = struct.unpack('i'*length, datafile.read(4*length))
        yield vector
        counter += 1




