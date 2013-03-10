import PyFileMaker
from .models import AssignmentStatus, ClubStatus
from .secrets import REAL_CHANGE_FMDB, REAL_CHANGE_FMDB_HOST


class RealChangeAssignment(object):
    C_ASSIGNMENT_TYPE = "AssignmentType"
    C_TIME_SLOT = "TimeSlot"

    def __init__(self, data):
        super(RealChangeAssignment, self).__init__()
        self._data = data

    def _get(self, k, default=""):
        return self._data.get(k, default)

    @property
    def assignment_type(self):
        return self._get(RealChangeAssignment.C_ASSIGNMENT_TYPE)

    @property
    def time_slot(self):
        return self._get(RealChangeAssignment.C_TIME_SLOT)

    @property
    def assignment_status(self):
        status = AssignmentStatus.NONE
        if self.assignment_type:
            if self.time_slot.startswith('6am'):
                status = AssignmentStatus.MORNING
            elif self.time_slot.startswith('2pm'):
                status = AssignmentStatus.AFTERNOON
            else:
                status = AssignmentStatus.ANY_TIME
        return status


class RealChangeTurf(object):
    C_TURF_ID = "kIDTurf_p"
    C_TURF_ADDRESS = "TurfAddress"
    C_TURF_LOCATION = "TurfLocation"
    C_TURF_CITY = "TurfAddressCity"

    def __init__(self, data):
        super(RealChangeTurf, self).__init__()
        self._data = data

    def _get(self, k, default=""):
        return self._data.get(k, default)

    @property
    def turf_id(self):
        return str(self._get(RealChangeTurf.C_TURF_ID))

    @property
    def turf_address(self):
        return self._get(RealChangeTurf.C_TURF_ADDRESS)

    @property
    def turf_location(self):
        return self._get(RealChangeTurf.C_TURF_LOCATION)

    @property
    def turf_city(self):
        return self._get(RealChangeTurf.C_TURF_CITY)


class RealChangeDatabaseRow(object):
    C_VENDOR_ID = "kIDVendor_p"
    C_CLUB_STATUS = "ClubStatus"
    C_CURRENT_ASSIGNMENT = "AssignmentCurrent"
    C_CURRENT_TURF = "TurfCurrent"
    C_PRIVATE_NAME = "Name_FL"
    C_PUBLIC_NAME = "NamePublic"
    C_PHOTO_LINK = "Photo"
    C_PUBLIC_PROFILE_LINK = "PublicProfileLink"
    C_PUBLIC_PROFILE_OK = "PublicProfileOK"

    def __init__(self, data):
        super(RealChangeDatabaseRow, self).__init__()
        self._data = data

    def _get(self, k, default=None):
        return self._data.get(k, default)

    @property
    def vendor_id(self):
        return str(self._get(RealChangeDatabaseRow.C_VENDOR_ID))

    @property
    def club_status(self):
        raw_status = self._get(RealChangeDatabaseRow.C_CLUB_STATUS)
        status = ClubStatus.NONE
        if raw_status:
            if '300' in raw_status:
                status = ClubStatus.THREE_HUNDRED_CLUB
            elif '600' in raw_status:
                status = ClubStatus.SIX_HUNDRED_CLUB
        return status

    @property
    def current_assignment(self):
        return RealChangeAssignment(self._get(RealChangeDatabaseRow.C_CURRENT_ASSIGNMENT, default={}))

    @property
    def current_turf(self):
        return RealChangeTurf(self._get(RealChangeDatabaseRow.C_CURRENT_TURF, default={}))

    @property
    def private_name(self):
        return self._get(RealChangeDatabaseRow.C_PRIVATE_NAME)

    @property
    def public_name(self):
        return self._get(RealChangeDatabaseRow.C_PUBLIC_NAME)

    @property
    def photo_url(self):
        """
        Return the absolute url to the vendor's photo.
        This URL is behind HTTP basic auth; use the same credentials as before to access.
        """
        url = None
        relative_url = self._get(RealChangeDatabaseRow.C_PHOTO_LINK)
        if relative_url:
            url = "http://{0}{1}".format(REAL_CHANGE_FMDB_HOST, relative_url)
        return url

    @property
    def profile_url(self):
        """
        Return the abolute URL to the vendor's photo.
        This is a publicly accessible URL.
        """
        # XXX we have no idea what form this will ultimately take.
        return self._get(RealChangeDatabaseRow.C_PUBLIC_PROFILE_LINK)

    @property
    def is_public(self):
        """
        Return True if this is a public profile and does
        not need to be anonymized.
        """
        raw_public = self._get(RealChangeDatabaseRow.C_PUBLIC_PROFILE_OK, default="")
        return (raw_public.strip() == "1")

    @property
    def has_club_status(self):
        return self.club_status != ClubStatus.NONE

    @property
    def has_current_turf(self):
        return self.current_turf.turf_location.strip() != ""


class RealChangeFileMakerDatabase(object):
    DATABASE_NAME = "rcn_vendors"
    LAYOUT_NAME = "vendorturfinfo"

    def __init__(self):
        super(RealChangeFileMakerDatabase, self).__init__()
        self._server = PyFileMaker.FMServer(REAL_CHANGE_FMDB)
        self._rows = None

    def _fmdata_to_dict(self, fmdata):
        """
        The FMData objects that we get back from PyFileMaker
        are not pickleable. We'll recursively turn it into
        a python dictionary so that we can, y'know, do nice stuff.
        """
        d = {}
        for k in fmdata.__slots__:
            v = fmdata[k]
            if 'PyFileMaker.FMData' in str(type(v)):
                v = self._fmdata_to_dict(v)
            d[k] = v
        return d

    def download_latest_data(self):
        self._server.setDb(RealChangeFileMakerDatabase.DATABASE_NAME)
        self._server.setLayout(RealChangeFileMakerDatabase.LAYOUT_NAME)

        # NOTE -- this takes a minute or two because they don't seem to have
        # any indexes in their database and the layout has a bunch of joins.
        data = self._server.doFindAll()
        self._rows = [RealChangeDatabaseRow(self._fmdata_to_dict(d)) for d in data]

    def rows(self):
        return self._rows






