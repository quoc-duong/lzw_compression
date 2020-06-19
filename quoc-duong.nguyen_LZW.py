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


def create_dico(file_str):
    # Create a set from string to get unique chars and sort them lexicographically
    res = sorted(list(set(file_str)))
    res.insert(0, '%')
    return res


# Get filename without extension
def get_name(filename):
    temp = filename.split('/')[-1]
    return temp.split('.')[0]


def create_dico_file(filename, dico_arr):
    dico_file = open(filename + '_dico.csv', 'w')
    for i in range(len(dico_arr) - 1):
        dico_file.write(dico_arr[i] + ',')
    dico_file.write(dico_arr[-1])


def create_lzw_table(file_str, dico_arr, filename):
    file_lzw = open(filename + '_LZWTable.csv', 'w')
    # Starting number of bits to encode a character
    nb_bits = len(bin(len(dico_arr))[2:])
    df = pd.DataFrame([['Buffer', 'Input', 'New sequence', 'Address', 'Output']]
                      , columns=['Buffer', 'Input', 'New sequence', 'Address', 'Output'])

    # First character
    buf = file_str[0]
    temp_df = pd.DataFrame([[np.nan, buf, np.nan, np.nan, np.nan]]
                           , columns=['Buffer', 'Input', 'New sequence', 'Address', 'Output'])
    df = pd.concat([df, temp_df], ignore_index=True)
    for i in range(1, len(file_str)):
        buffer = buf
        input_str = file_str[i]
        buf += input_str

        # Sequence already exists in dictionary
        if buf in dico_arr:
            output = np.nan
            if nb_bits < len(bin(dico_arr.index(buf))[2:]):
                output = 0
                nb_bits += 1
            if output is np.nan:
                temp_df = pd.DataFrame([[buffer, input_str, np.nan, np.nan, output]]
                                       , columns=['Buffer', 'Input', 'New sequence', 'Address', 'Output'])
            else:
                temp_df = pd.DataFrame([[buffer, input_str, np.nan, np.nan, '@[%]' + '=' + str(output)]]
                                       , columns=['Buffer', 'Input', 'New sequence', 'Address', 'Output'])
            df = pd.concat([df, temp_df], ignore_index=True)
            continue
        new_seq = buf
        dico_arr.append(buf)
        address = len(dico_arr) - 1
        output = '@[' + buffer + ']' + '=' + str(dico_arr.index(buffer))
        temp_df = pd.DataFrame([[buffer, input_str, new_seq, address, output]]
                               , columns=['Buffer', 'Input', 'New sequence', 'Address', 'Output'])
        df = pd.concat([df, temp_df], ignore_index=True)
        buf = file_str[i]

    # EOF
    if not (buf in dico_arr):
        dico_arr.append(buf)
    output = '@[' + buf + ']' + '=' + str(dico_arr.index(buf))
    temp_df = pd.DataFrame([[buf, np.nan, np.nan, np.nan, output]]
                           , columns=['Buffer', 'Input', 'New sequence', 'Address', 'Output'])
    df = pd.concat([df, temp_df], ignore_index=True)

    print(df)
    return df


def main():
    args = parse_options()

    # Compress and uncompress options are either both enabled or not enabled
    if args.compress == args.uncompress:
        raise ValueError('Wrong options')

    filename = get_name(args.path)
    if args.compress:
        print("Compress mode")
        file_str = open(args.path, 'r').read().rstrip('\n')
        dico_arr = create_dico(file_str)
        create_dico_file(filename, dico_arr)

        df = create_lzw_table(file_str, dico_arr, filename)
        '''
                Create files 
                file_lzw = open(name + '.lzw', 'w')
        '''

    if args.uncompress:
        print("Uncompress mode")
        file_lzw = open(args.path, 'r')
        file_str = file_lzw.readline().rstrip('\n')
        print(file_str)


if __name__ == '__main__':
    main()
