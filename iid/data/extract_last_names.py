#!/usr/bin/python3
import csv

surnames = []

with open('last_names.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        surnames.append(row[0].title())

with open('surnames.dat', 'w+') as f:
    for name in surnames:
        f.write(name)
        f.write('\n')

