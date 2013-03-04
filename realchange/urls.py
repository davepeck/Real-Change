from webapp2 import Route
import handlers


URLS = [
    Route(r'/', handlers.HomeHandler, name='home'),
]

