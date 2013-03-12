from nose.tools import *
from pygeocoder import Geocoder

def test_index():
    (lat, lng) = Geocoder.geocode("10900 Euclid Ave in Cleveland")[0].coordinates
    print "%.5f, %.5f" % (lat, lng)

