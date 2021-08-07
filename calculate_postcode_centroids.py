#!/usr/bin/env python3

# Input from STDIN is expected to be a CSV file with columns 'postcode', 'lat', 'lon'
#
# 10541;41.390289;-73.790533
# 10541;41.390301;-73.790590
# 10541;41.390279;-73.790751
# 10541;41.390183;-73.790739
#
# The input needs to be sorted by postcode. For each postcode a center point gets
# calculated. We use the median to account for possible errors in the input.
#
# Output to STDOUT is one line per postcode
#
# postcode,lat,lon
# 00535;43.089300;-72.613680
# 00586;18.343681;-67.028427
# 00601;18.181632;-66.757545

import sys
import csv
import statistics

reader = csv.DictReader(sys.stdin, delimiter=';')
writer = csv.DictWriter(sys.stdout, delimiter=';', fieldnames=['postcode', 'lat', 'lon'])
writer.writeheader()

latitudes = []
longitudes = []
previous_postcode = None

def print_summary():
    if latitudes and longitudes:
        writer.writerow({
            'postcode': previous_postcode,
            'lat': round(statistics.median(latitudes), 6),
            'lon': round(statistics.median(longitudes), 6)
        })


for row in reader:
    postcode = row['postcode']

    if previous_postcode and previous_postcode != postcode:
        print_summary()
        latitudes = []
        longitudes = []

    previous_postcode = postcode
    latitudes.append(float(row['lat']))
    longitudes.append(float(row['lon']))

print_summary()
