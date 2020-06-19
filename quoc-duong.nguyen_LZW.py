import numpy as np
import pandas as pd
import sys
import pathlib
import argparse
import csv


def parse_options():
    parser = argparse.ArgumentParser(description='Compress/Decompress text files with LZW')
    parser.add_argument("-c", dest='compress', help="Compress option", action='store_true')
    parser.add_argument("-u", dest='uncompress', help="Uncompress option", action='store_true')
    parser.add_argument("-p", dest='path', help="File to process", action='store')
    return parser.parse_args()


def get_unique_chars_ordered(file_str):
    # Remove newline from string
    temp = file_str.rstrip('\n')
    # Create a set from string to get unique chars and sort them lexicographically
    return sorted(set(temp))


# Get filename without extension
def get_name(filename):
    temp = filename.split('/')[-1]
    return temp.split('.')[0]


def create_dico(filename, dico_arr):
    dico_file = open(filename + '_dico.csv', 'w')
    dico_file.write('%')
    for i in range(len(dico_arr)):
        dico_file.write(',' + dico_arr[i])


def main():
    args = parse_options()

    # Compress and uncompress options are either both enabled or not enabled
    if args.compress == args.uncompress:
        raise ValueError('Wrong options')

    name = get_name(args.path)
    if args.compress:
        print("Compress mode")
        file_str = open(args.path, 'r').read()
        dico_arr = get_unique_chars_ordered(file_str)
        create_dico(name, dico_arr)

    else:
        print("Uncompress mode")
        file = open(args.path, 'r')
        file_str = file.readline().rstrip('\n')
        print(file_str)


if __name__ == '__main__':
    main()
