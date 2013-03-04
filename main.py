import webapp2
from realchange.urls import URLS


app = webapp2.WSGIApplication(URLS, debug=True)


