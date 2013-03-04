from google.appengine.ext import ndb


class Example(ndb.Model):
    content = ndb.StringProperty()

