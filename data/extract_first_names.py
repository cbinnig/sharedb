#!/usr/bin/python3
import csv

names = set()

for year in range(1880, 2016):
    with open('names/yob{0}.txt'.format(year)) as f:
        reader = csv.reader(f)
        for row in reader:
            names.add(row[0].title())

with open('first_names.dat', 'w+') as f:
    for name in names:
        f.write(name)
        f.write('\n')

