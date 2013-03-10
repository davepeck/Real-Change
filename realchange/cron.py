from __future__ import print_function
import logging
from geopy import geocoders
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from .handlers import RealChangeHandler
from .rcfmdb import RealChangeFileMakerDatabase
from .models import Vendor
from .secrets import GOOGLE_GEOCODE_KEY


class CronError(Exception):
    pass


class RealChangeCronHandler(RealChangeHandler):
    """
    Base class for all cron jobs, like filemaker syncing.
    """
    SAFE_CRON_HEADER = "X-Appengine-Cron"

    def ensure_cron(self):
        is_development = self.is_development
        has_cron_header = RealChangeCronHandler.SAFE_CRON_HEADER in self.request.headers
        if (not is_development) and (not has_cron_header):
            raise CronError("Illegal call to app engine cron.")


class SyncFileMakerCronHandler(RealChangeCronHandler):
    def get(self):
        self.ensure_cron()
        taskqueue.add(url='/task/sync/fm/', queue_name='sync', target=self.service_backend_name)
        self.respond_ok()


class SyncFileMakerTaskHandler(RealChangeHandler):
    def post(self):
        logging.info("SyncFileMakerTask :: START")

        # Download data
        logging.info("SyncFileMakerTask :: Download Data")
        db = RealChangeFileMakerDatabase()
        db.download_latest_data()  # THIS IS SLOW

        # Build the new vendors
        logging.info("SyncFileMakerTask :: Build Vendor Entities")
        new_vendors = []
        for row in db.rows():
            if row.has_club_status and row.has_current_turf:
                vendor = Vendor(
                    vendor_id=row.vendor_id,
                    private_name=row.private_name,
                    public_name=row.public_name,
                    is_public=row.is_public,
                    profile_url=row.profile_url,
                    club_status=row.club_status,
                    assignment_status=row.current_assignment.assignment_status,
                    turf_address=row.current_turf.turf_address,
                    turf_location=row.current_turf.turf_location,
                    turf_city=row.current_turf.turf_city,
                    photo_url=row.photo_url,
                )
                new_vendors.append(vendor)

        # Blow away the current database
        logging.info("SyncFileMakerTask :: Delete Old Entities")
        Vendor.delete_all()

        # Save the new database
        logging.info("SyncFileMakerTask :: Save New Entities")
        new_vendor_keys = Vendor.save_all(new_vendors)
        try:
            logging.info("SyncFileMakerTask :: there are {0} new_vendor_keys".format(len(new_vendor_keys)))
        except Exception:
            logging.info("SyncFileMakerTask :: new_vendor_keys is {0}".format(repr(new_vendor_keys)))

        # Queue up tasks to geocode our new thingies.
        for new_vendor_key in new_vendor_keys:
            taskqueue.add(url='/task/vendor/geocode/', queue_name='geocode', target=self.service_backend_name, params={'vendor_key': new_vendor_key.urlsafe()})

        logging.info("SyncFileMakerTask :: DONE")
        self.respond_ok()


class GeocodeTaskHandler(RealChangeHandler):
    def post(self):
        logging.info("GeocodeTaskHandler :: Geocoding {0}".format(self.request.get('vendor_key')))

        vendor_key = ndb.Key(urlsafe=self.request.get('vendor_key'))
        logging.info("GeocodeTaskHandler :: vendor_key = {0}".format(repr(vendor_key)))

        vendor = vendor_key.get()
        logging.info("GeocodeTaskHandler :: vendor = {0}".format(repr(vendor)))
        coder = geocoders.Google(api_key=GOOGLE_GEOCODE_KEY)

        geocodes = coder.geocode(vendor.address_for_geocoding, exactly_one=False)
        place, (lat, lng) = geocodes[0]
        vendor.new_geo_point = ndb.GeoPt(lat, lng)
        vendor.put()

        self.respond_ok()









