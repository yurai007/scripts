#!/usr/bin/python3

import os
import csv
import sys

def get_symbol_and_overhead_from_perf_report(filename):
    separator = ' '
    with open(filename, newline='') as f:
        reader = csv.reader(f, delimiter=separator, skipinitialspace=True)
        try:
            for line in reader:
                if line:
                    yield line[0], line[4]
        except csv.Error as e:
            print(f"  Error: {e}")

def process_file(filename):
    symbol_to_overhead = dict()
    for (overhead, symbol) in get_symbol_and_overhead_from_perf_report(filename):
        # when encountered duplicates just take first one
        if symbol not in symbol_to_overhead:
            symbol_to_overhead[symbol] = overhead
    return symbol_to_overhead

def main():
    if len(sys.argv) != 3:
        return
    map1 = process_file(sys.argv[1])
    map2 = process_file(sys.argv[2])
    symbols_to_diffs = dict()

    for symbol, overhead in map1.items():
        f1 = float(overhead[:-1])
        if symbol in map2:
            f2 = float(map2[symbol][:-1])
            diff = round(abs(f2 - f1), 5)
            symbols_to_diffs[symbol] = diff
        else:
            if f1 > 0:
                print(f"  Warning: unknown {symbol} {f1}")

    for symbol in sorted(symbols_to_diffs, key=symbols_to_diffs.get, reverse=True):
        print(symbols_to_diffs[symbol], symbol)

if __name__ == '__main__':
    main()
