#!/usr/bin/env python3
"""
A generator of synthetic personal information for testing purposes.
This pulls from various CSV files and generator functions to create a new
CSV with a variable number of rows.
"""
import argparse
import csv
from faker import Faker

fake = Faker()

def name_generator():
    while True:
        yield fake.name()

def ssn_generator():
    """A simple generator for SSNs."""
    while True:
        yield fake.ssn()

def zip_generator():
    """A simple generator for ZIP codes."""
    while True:
        yield fake.postalcode()

def address_generator():
    while True:
        yield fake.address()

def date_generator():
    """A simple generator for dates."""
    while True:
        yield fake.date_time_between(start_date="-100y", end_date="now", tzinfo=None)

def mac_generator():
    while True:
        yield fake.mac_address()

def email_generator():
    while True:
        yield fake.email()

def face_generator():
    while True:
        yield 'img/obama.jpg'

name_gen = name_generator()
ssn_gen = ssn_generator()
zip_gen = zip_generator()
address_gen = address_generator()
date_gen = date_generator()
mac_gen = mac_generator()
email_gen = email_generator()
face_gen = face_generator()
generators = [('name', name_gen),
              ('ssn', ssn_gen),
              ('zip', zip_gen),
              ('address', address_gen),
              ('date', date_gen),
              ('device_id', mac_gen),
              ('email', email_gen),
              ('face', face_gen)
              ]

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
