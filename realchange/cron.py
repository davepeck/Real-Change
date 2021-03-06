from __future__ import print_function
import logging
from pygeocoder import Geocoder
from google.appengine.api import taskqueue
from google.appengine.api import memcache
from google.appengine.ext import ndb
from .handlers import RealChangeHandler
from .rcfmdb import RealChangeFileMakerDatabase
from .models import Vendor


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

    def is_safe_to_sync(self):
        safe_to_sync = memcache.add(key="_safe_to_sync", value="ignore", time=300)
        return safe_to_sync

    def kick_off_sync(self):
        taskqueue.add(url='/task/sync/fm/', queue_name='sync', target=self.service_backend_name)


class SyncHandler(RealChangeCronHandler):
    """This is the manually-triggered entrance to the sync tasks."""
    def get(self):
        safe = self.is_safe_to_sync()
        if safe:
            self.kick_off_sync()
        return self.respond_with_template('sync.dhtml', {"safe": safe})


class SyncFileMakerCronHandler(RealChangeCronHandler):
    """This is the cron-triggered entrance to the sync tasks."""
    def get(self):
        self.ensure_cron()
        if self.is_safe_to_sync():
            self.kick_off_sync()
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
        results = Geocoder.geocode(vendor.address_for_geocoding)
        (lat, lng) = results[0].coordinates
        vendor.new_geo_point = ndb.GeoPt(lat, lng)
        vendor.put()

        self.respond_ok()









