#!/usr/bin/python3

"""
Tiger road data to OSM conversion script
Creates Karlsruhe-style address ways beside the main way
based on the Massachusetts GIS script by christopher schmidt

BUGS:
- On very tight curves, a loop may be generated in the address way.
- It would be nice if the ends of the address ways were not pulled back from dead ends
"""

import sys
import re
import csv
import math

from lib.parse import parse_shp_for_geom_and_tags
from lib.project import unproject
from lib.helpers import round_point, glom_all, length, interpolation_type, create_wkt_linestring


# Sets the distance that the address ways should be from the main way, in feet.
ADDRESS_DISTANCE = 30

# Sets the distance that the ends of the address ways should be pulled back
# from the ends of the main way, in feet
ADDRESS_PULLBACK = 45






def addressways(waylist, nodelist, first_id):
    id = first_id
    lat_feet = 364613  #The approximate number of feet in one degree of latitude
    distance = float(ADDRESS_DISTANCE)
    csv_lines = []

    for waykey, segments in waylist.items():
        waykey = dict(waykey)
        for segment in segments:
            lsegment = []
            rsegment = []
            lastpoint = None

            # Don't pull back the ends of very short ways too much
            seglength = length(segment, nodelist)
            if seglength < float(ADDRESS_PULLBACK) * 3.0:
                pullback = seglength / 3.0
            else:
                pullback = float(ADDRESS_PULLBACK)
            if "tiger:lfromadd" in waykey:
                lfromadd = waykey["tiger:lfromadd"]
            else:
                lfromadd = None
            if "tiger:ltoadd" in waykey:
                ltoadd = waykey["tiger:ltoadd"]
            else:
                ltoadd = None
            if "tiger:rfromadd" in waykey:
                rfromadd = waykey["tiger:rfromadd"]
            else:
                rfromadd = None
            if "tiger:rtoadd" in waykey:
                rtoadd = waykey["tiger:rtoadd"]
            else:
                rtoadd = None

            right = rfromadd is not None and rtoadd is not None
            left = lfromadd is not None and ltoadd is not None

            if left == False and right == False:
                continue

            first = True
            firstpointid, firstpoint = nodelist[ round_point( segment[0] ) ]

            finalpointid, finalpoint = nodelist[ round_point( segment[len(segment) - 1] ) ]
            for point in segment:
                pointid, (lat, lon) = nodelist[ round_point( point ) ]

                #The approximate number of feet in one degree of longitude
                lrad = math.radians(lat)
                lon_feet = 365527.822 * math.cos(lrad) - 306.75853 * math.cos(3 * lrad) + 0.3937 * math.cos(5 * lrad)

                #Calculate the points of the offset ways
                if lastpoint is not None:
                    #Skip points too close to start
                    if math.sqrt((lat * lat_feet - firstpoint[0] * lat_feet)**2 + (lon * lon_feet - firstpoint[1] * lon_feet)**2) < pullback:
                        #Preserve very short ways (but will be rendered backwards)
                        if pointid != finalpointid:
                            continue
                    #Skip points too close to end
                    if math.sqrt((lat * lat_feet - finalpoint[0] * lat_feet)**2 + (lon * lon_feet - finalpoint[1] * lon_feet)**2) < pullback:
                        #Preserve very short ways (but will be rendered backwards)
                        if (pointid != firstpointid) and (pointid != finalpointid):
                            continue

                    X = (lon - lastpoint[1]) * lon_feet
                    Y = (lat - lastpoint[0]) * lat_feet
                    if Y != 0:
                        theta = math.pi/2 - math.atan( X / Y)
                        Xp = math.sin(theta) * distance
                        Yp = math.cos(theta) * distance
                    else:
                        Xp = 0
                        if X > 0:
                            Yp = -distance
                        else:
                            Yp = distance

                    if Y > 0:
                        Xp = -Xp
                    else:
                        Yp = -Yp

                    if first:
                        first = False
                        dX =  - (Yp * (pullback / distance)) / lon_feet #Pull back the first point
                        dY = (Xp * (pullback / distance)) / lat_feet
                        if left:
                            lpoint = (lastpoint[0] + (Yp / lat_feet) - dY, lastpoint[1] + (Xp / lon_feet) - dX)
                            lsegment.append( (id, lpoint) )
                            id += 1
                        if right:
                            rpoint = (lastpoint[0] - (Yp / lat_feet) - dY, lastpoint[1] - (Xp / lon_feet) - dX)
                            rsegment.append( (id, rpoint) )
                            id += 1

                    else:
                        #round the curves
                        if delta[1] != 0:
                            theta = abs(math.atan(delta[0] / delta[1]))
                        else:
                            theta = math.pi / 2
                        if Xp != 0:
                            theta = theta - abs(math.atan(Yp / Xp))
                        else: theta = theta - math.pi / 2
                        r = 1 + abs(math.tan(theta/2))
                        if left:
                            lpoint = (lastpoint[0] + (Yp + delta[0]) * r / (lat_feet * 2), lastpoint[1] + (Xp + delta[1]) * r / (lon_feet * 2))
                            lsegment.append( (id, lpoint) )
                            id += 1
                        if right:
                            rpoint = (lastpoint[0] - (Yp + delta[0]) * r / (lat_feet * 2), lastpoint[1] - (Xp + delta[1]) * r / (lon_feet * 2))

                            rsegment.append( (id, rpoint) )
                            id += 1

                    delta = (Yp, Xp)

                lastpoint = (lat, lon)


            #Add in the last node
            dX =  - (Yp * (pullback / distance)) / lon_feet
            dY = (Xp * (pullback / distance)) / lat_feet
            if left:
                lpoint = (lastpoint[0] + (Yp + delta[0]) / (lat_feet * 2) + dY, lastpoint[1] + (Xp + delta[1]) / (lon_feet * 2) + dX )
                lsegment.append( (id, lpoint) )
                id += 1
            if right:
                rpoint = (lastpoint[0] - Yp / lat_feet + dY, lastpoint[1] - Xp / lon_feet + dX)
                rsegment.append( (id, rpoint) )
                id += 1

            # Generate the tags for ways and nodes
            zipr = ''
            zipl = ''
            name = ''
            county = ''
            state = ''
            if "tiger:zip_right" in waykey:
                zipr = waykey["tiger:zip_right"]
            if "tiger:zip_left" in waykey:
                zipl = waykey["tiger:zip_left"]
            if "name" in waykey:
                name = waykey["name"]
            if "tiger:county" in waykey:
                result = re.match('^(.+), ([A-Z][A-Z])', waykey["tiger:county"]) # e.g. 'Perquimans, NC'
                county = result[1]
                state = result[2]

            # Write the nodes of the offset ways
            if right:
                interpolationtype = interpolation_type(rfromadd, rtoadd, lfromadd, ltoadd)

                if interpolationtype is not None:
                    csv_lines.append({
                        'from': int(rfromadd),
                        'to': int(rtoadd),
                        'interpolation': interpolationtype,
                        'street': name,
                        'city': county,
                        'state': state,
                        'postcode': zipr,
                        'geometry': create_wkt_linestring(rsegment)
                    })

            if left:
                interpolationtype = interpolation_type(lfromadd, ltoadd, rfromadd, rtoadd)

                if interpolationtype is not None:
                    csv_lines.append({
                        'from': int(lfromadd),
                        'to': int(ltoadd),
                        'interpolation': interpolationtype,
                        'street': name,
                        'city': county,
                        'state': state,
                        'postcode': zipl,
                        'geometry': create_wkt_linestring(lsegment)
                    })

    return csv_lines

def compile_nodelist( parsed_gisdata, first_id=1 ):
    nodelist = {}

    i = first_id
    for geom, _tags in parsed_gisdata:
        if len(geom) == 0:
            continue

        for point in geom:
            r_point = round_point( point )
            if r_point not in nodelist:
                nodelist[ r_point ] = (i, unproject( point ))
                i += 1

    return (i, nodelist)



def compile_waylist( parsed_gisdata ):
    waylist = {}

    # Group by tiger:way_id
    for geom, tags in parsed_gisdata:
        way_key = tags.copy()
        way_key = ( way_key['tiger:way_id'], tuple( [(k,v) for k,v in way_key.items()] ) )

        if way_key not in waylist:
            waylist[way_key] = []

        waylist[way_key].append( geom )

    ret = {}
    for (_way_id, way_key), segments in waylist.items():
        ret[way_key] = glom_all( segments )
    return ret


def shape_to_csv( shp_filename, csv_filename ):

    print("parsing shpfile %s" % shp_filename)
    parsed_features = parse_shp_for_geom_and_tags( shp_filename )

    print("compiling nodelist")
    i, nodelist = compile_nodelist( parsed_features )

    print("compiling waylist")
    waylist = compile_waylist( parsed_features )

    print("preparing address ways")
    csv_lines = addressways(waylist, nodelist, i)

    print("writing %s" % csv_filename)
    fieldnames = ['from', 'to', 'interpolation', 'street', 'city', 'state', 'postcode', 'geometry']
    with open(csv_filename, 'w') as f:
        csv_writer = csv.DictWriter(f, delimiter=';', fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(csv_lines)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("%s input.shp output.csv" % sys.argv[0])
        sys.exit()
    shp_filename = sys.argv[1]
    csv_filename = sys.argv[2]
    shape_to_csv(shp_filename, csv_filename)
