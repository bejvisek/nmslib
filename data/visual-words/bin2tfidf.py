#!/usr/bin/python

import sys
import os
import argparse
import gzip

import math

import readbindata

import collections

p = argparse.ArgumentParser(description='reads in data objects in binary format (2 files) and prints out the same data as text', parents=[readbindata.get_arg_parser()])
p.add_argument('-f', '--df_file', help='text file (possibly .gz) with a dictionary of document frequencies', required=True)
p.add_argument('-o', '--output', help='output file (possible .gz) - use stdout, if not specified')
p.add_argument('-c', '--doc_count', help='number of documents in the collection', required=True, type=int) # 7411827
args = p.parse_args()

# output file
output = sys.stdout
if args.output:
    if os.path.splitext(args.output)[1] == ".gz":
        output = gzip.open(args.output, "wb")
    else:
        output = open(args.output, "w")

# read in the df file
df_dict = eval(gzip.open(args.df_file, 'r').read() if os.path.splitext(args.df_file)[1] == ".gz" else open(args.output, 'r').read())
print >> sys.stderr, "the DF dictionary read in, size: ", str(len(df_dict))

idf_dict = {}
n = float(args.doc_count)
for key, value in df_dict.items():
    idf_dict[key] = math.log10(n / value)


def print_vector(tfidf_vector):
    output.write(', '.join([str(key) + ': ' + str(value) for (key, value) in tfidf_vector]))
    output.write('\n')


def raw2tfidf(record):
    # iterate over the dimensions and build a vector map
    tf = collections.Counter()
    for dim in record:
        tf[dim] += 1
    # sort the values and multiply the TF them by IDF
    not_normalized = []
    sum_sq = float(0)
    for key, value in sorted(tf.items()):
        tfidf = value * idf_dict[key]
        sum_sq += tfidf * tfidf
        not_normalized.append((key, tfidf))
    norm = math.sqrt(sum_sq)
    # normalize the values
    normalized = []
    for (key, value) in not_normalized:
        normalized.append((key, value / norm))

    return normalized


counter = 0
for record in readbindata.read_records(args):
    print_vector(raw2tfidf(record))
    counter += 1
    if counter % 1000 == 0:
        print >> sys.stderr, "processed ", counter, " objects"


if args.output:
    output.close()

print >> sys.stderr, "processed ", counter, " objects"



