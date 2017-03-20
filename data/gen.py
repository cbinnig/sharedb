#!/usr/bin/env python3
"""
A generator of synthetic personal information for testing purposes.
This pulls from various CSV files and generator functions to create a new
CSV with a variable number of rows.
"""
import argparse
import csv
import random

def file_generator(path):
    """A simple generator for files where each line is a piece of data."""
    data = [line.strip() for line in open(path, 'r').readlines()]
    while True:
        yield random.choice(data)

def ssn_generator():
    """A simple generator for SSNs."""
    while True:
        leading = random.randrange(1, 900)
        # SSNs must not start with 000, 666, or 900-999
        if leading == 666:
            continue
        aaa = str(leading).zfill(3)
        gg = str(random.randrange(1, 100)).zfill(2)
        ssss = str(random.randrange(1, 10000)).zfill(4)
        yield aaa + '-' + gg + '-' + ssss

first_name_gen = file_generator('first_names.dat')
last_name_gen = file_generator('last_names.dat')
ssn_gen = ssn_generator()
generators = [('last_name', last_name_gen),
              ('first_name', first_name_gen),
              ('ssn', ssn_gen)]

def main():
    """Generates a random set of data to an output file."""
    parser = argparse.ArgumentParser(description='Generate fake PII for testing.')
    parser.add_argument('-out', help='Output path.')
    parser.add_argument('-n', nargs='?', type=int, default=100, help='Number of lines to output.')
    args = parser.parse_args()

    # Validate generators
    assert len(set([name for name, gen in generators])) == len([name for name, gen in generators])

    with open(args.out, 'w+') as out:
        writer = csv.writer(out)
        writer.writerow([name for name, gen in generators])
        for _ in range(args.n):
            writer.writerow([next(gen) for name, gen in generators])


if __name__ == '__main__':
    main()
