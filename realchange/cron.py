from __future__ import print_function
import os
import logging
from google.appengine.api import taskqueue
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
        is_development = os.environ.get("SERVER_SOFTWARE", "").startswith("Development")
        has_cron_header = RealChangeCronHandler.SAFE_CRON_HEADER in self.request.headers
        if (not is_development) and (not has_cron_header):
            raise CronError("Illegal call to app engine cron.")



class SyncFileMakerCronHandler(RealChangeCronHandler):
    def get(self):
        self.ensure_cron()
        taskqueue.add(url='/task/sync/fm/', queue_name='sync', target='service')


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
                    # XXX TODO geo_point = row.current_turf.geo_point
                    photo_url=row.photo_url,
                )
                new_vendors.append(vendor)

        # Blow away the current database
        logging.info("SyncFileMakerTask :: Delete Old Entities")
        Vendor.delete_all()

        # Save the new database
        logging.info("SyncFileMakerTask :: Save New Entities")
        Vendor.save_all(new_vendors)

        logging.info("SyncFileMakerTask :: DONE")
        self.respond_ok()









