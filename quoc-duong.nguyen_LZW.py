import numpy as np
import pandas as pd
import sys
from pathlib import Path
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
    dico_file.write('\r\n')


def create_lzw_table(file_str, dico_arr):
    # Starting number of bits to encode a character
    nb_bits = len(bin(len(dico_arr))[2:])
    df = pd.DataFrame([], columns=['Buffer', 'Input', 'New sequence', 'Address', 'Output'])

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

    return df


def create_lzw_file(filename, series, nb_bits, file_str):
    file_lzw = open(filename + '.lzw', 'w')
    # Remove null values
    np_arr = series.dropna().to_numpy()
    c_text = ''
    before_size = nb_bits * len(file_str)
    after_size = 0
    for el in np_arr:
        after_size += nb_bits
        bin_val = bin(int(el.split('=')[1]))[2:].zfill(nb_bits)
        c_text += bin_val
        if el[2] == '%':
            nb_bits += 1

    second = "Size before LZW compression: " + str(before_size) + " bits\n"
    third = "Size after LZW compression: " + str(after_size) + " bits\n"
    fourth = after_size / before_size
    file_lzw.writelines([c_text + '\n', second, third, "Compression ratio: {:.3f}".format(fourth)])


def uncompress_lzw(lzw_str, dico_arr, nb_bits):
    res = ""
    i = 0
    size = len(lzw_str)
    first = int(lzw_str[:nb_bits], base=2)
    lzw_str = lzw_str[nb_bits:]
    buf = dico_arr[first]
    while i < size:
        if not len(lzw_str):
            res += dico_arr[second]
            break
        second = int(lzw_str[:nb_bits], base=2)
        lzw_str = lzw_str[nb_bits:]
        if second:
            buf += dico_arr[second][0]
        i += nb_bits
        if second and not (buf in dico_arr):
            res += dico_arr[first]
            dico_arr = np.append(dico_arr, buf)
            first = second
            buf = dico_arr[second]
        elif second:
            first = buf
            buf = dico_arr[second]
            continue
        else:
            nb_bits += 1

    return res


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

        start_nb_bits = len(bin(len(dico_arr))[2:])
        df = create_lzw_table(file_str, dico_arr)
        df.to_csv(filename + '_LZWTable.csv', index=False, line_terminator='\r\n')
        create_lzw_file(filename, df['Output'], start_nb_bits, file_str)

    if args.uncompress:
        print("Uncompress mode")
        file_lzw = open(args.path, 'r')
        dico_path = Path(args.path).parent / (filename + '_dico.csv')
        dico_arr = pd.read_csv(dico_path, sep=',', header=None).values[0].tolist()
        start_nb_bits = len(bin(len(dico_arr))[2:])
        lzw_str = file_lzw.readline().rstrip('\n')
        result_str = uncompress_lzw(lzw_str, dico_arr, start_nb_bits)
        print(result_str)
        # Write into new txt file


if __name__ == '__main__':
    main()
