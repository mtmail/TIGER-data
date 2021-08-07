#!/usr/bin/env python3

# Input from STDIN is expected to be a CSV file with columns 'postcode' and
# 'geometry'
#
# from;to;interpolation;street;city;state;postcode;geometry
# 98;88;all;Sherman Rd;Putnam;NY;10541;LINESTRING(-73.790533 41.390289,-73.790590 41.390301,-73.790751 41.390279,-73.790739 41.390183)
#
# Output to STDOUT is a list of postcode-coordinate pairs
#
# postcode,lat,lon
# 10541;41.390289;-73.790533
# 10541;41.390301;-73.790590
# 10541;41.390279;-73.790751
# 10541;41.390183;-73.790739

import sys
import re
import csv

reader = csv.DictReader(sys.stdin, delimiter=';')
writer = csv.DictWriter(sys.stdout, delimiter=';', fieldnames=['postcode', 'lat', 'lon'])
writer.writeheader()

for row in reader:

    # If you 'cat *.csv' then you might end up with multiple CSV header lines.
    # Skip those
    if row['geometry'] == 'geometry':
        continue

    if row['postcode']:
        result = re.match('LINESTRING\((.+)\)$', row['geometry'])

        # fail if geometry can't be parsed
        assert result

        for coord_pair in result[1].split(','):
            [lon, lat] = coord_pair.split(' ')
            writer.writerow({
                'postcode': row['postcode'],
                'lat': lat,
                'lon': lon
            })
