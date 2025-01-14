import pytest

from lib.parse import parse_shp_for_geom_and_tags

def test_parse_shp_for_geom_and_tags():
    shapefile = 'tests/fixtures/tl_2020_37143_edges/tl_2020_37143_edges.shp'
    parsed = parse_shp_for_geom_and_tags(shapefile)

    assert(parsed[0]) == (
        [
            (-76.522227, 36.329937),
            (-76.52193799999999, 36.330121999999996),
            (-76.521714, 36.330247),
            (-76.52145399999999, 36.330357),
            (-76.51769399999999, 36.331181),
            (-76.516346, 36.331509),
            (-76.515559, 36.331801999999996),
            (-76.514725, 36.332294999999995),
            (-76.514395, 36.332496),
            (-76.514123, 36.332617),
            (-76.51303399999999, 36.333024),
            (-76.509675, 36.334396),
            (-76.508455, 36.334815),
            (-76.50688, 36.335142999999995),
            (-76.506269, 36.335206),
            (-76.505718, 36.3352),
            (-76.505175, 36.335131),
            (-76.504699, 36.335024),
            (-76.503739, 36.334719),
            (-76.503395, 36.334565),
            (-76.502934, 36.334308),
            (-76.502509, 36.334027),
            (-76.502053, 36.333681999999996),
            (-76.501632, 36.333304),
            (-76.50099399999999, 36.332805),
            (-76.500427, 36.332319999999996)
        ],
        {
            'tiger:way_id': 18401089,
            'name': 'Hickory Cross Rd',
            'tiger:county': 'Perquimans, NC',
            'tiger:lfromadd': '388',
            'tiger:rfromadd': '389',
            'tiger:ltoadd': '100',
            'tiger:rtoadd': '101',
            'tiger:zip_left': '27919',
            'tiger:zip_right': '27919'
        }
    )