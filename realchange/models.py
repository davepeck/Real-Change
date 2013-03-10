from google.appengine.ext import ndb


class AssignmentStatus(object):
    NONE = "none"
    ANY_TIME = "any"
    MORNING = "morning"
    AFTERNOON = "afternoon"


class ClubStatus(object):
    NONE = "none"
    THREE_HUNDRED_CLUB = "300"
    SIX_HUNDRED_CLUB = "600"


class Vendor(ndb.Model):
    # Basics
    vendor_id = ndb.StringProperty(indexed=True, required=True)  # As seen in the real change filemaker db
    private_name = ndb.StringProperty(indexed=True)
    public_name = ndb.StringProperty(indexed=True)
    is_public = ndb.BooleanProperty(indexed=True, default=False)

    # Profile
    profile_url = ndb.StringProperty()
    club_status = ndb.StringProperty(indexed=True)
    assignment_status = ndb.StringProperty(indexed=True)

    # GeoData
    geo_point = ndb.GeoPtProperty(indexed=True)  # XXX when do we actually do this?

    # Original (non-geocoded) data
    turf_address = ndb.StringProperty()
    turf_location = ndb.StringProperty()
    turf_city = ndb.StringProperty()

    # Photo (TODO)
    photo_url = ndb.StringProperty()  # NOTE access requires the RCN credentials.
    photo_blobstore = ndb.BlobKeyProperty()

    @classmethod
    def all(cls, keys_only=False):
        return Vendor.query(default_options=ndb.QueryOptions(keys_only=keys_only))

    @classmethod
    def delete_all(cls):
        # HERE BE DRAGONS
        ndb.delete_multi(cls.all(keys_only=True))

    @classmethod
    def save_all(cls, new_vendors):
        ndb.put_multi(new_vendors)

    @property
    def display_name(self):
        display_name = "Real Change Vendor #{0}".format(self.vendor_id)
        if self.is_public:
            if self.public_name:
                display_name = self.public_name
            elif self.private_name:
                display_name = self.private_name
        return display_name

    @property
    def display_location(self):
        return self.turf_location

    @property
    def public_profile_url(self):
        return self.profile_url

    @property
    def public_photo_url(self):
        return "XXX TODO"

    def to_display_jsonable(self):
        """
        Return a jsonable entry suitable for display.
        AKA if it's not public, we'll scrub the names.
        """
        return dict(
            vendor_id=self.vendor_id,
            display_name=self.display_name,
            public_profile_url=self.public_profile_url,
            club_status=self.club_status,
            assignment_status=self.assignment_status,
            latitude=self.geo_point[0],
            longitude=self.geo_point[1],
            display_location=self.display_location,
            public_photo_url=self.public_photo_url,
        )



