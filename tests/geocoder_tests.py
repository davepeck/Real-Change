from nose.tools import *
from geopy import geocoders  

def test_index():
    g = geocoders.Google()
    assert g
    place, (lat, lng) = g.geocode("10900 Euclid Ave in Cleveland")  
    print "%s: %.5f, %.5f" % (place, lat, lng)