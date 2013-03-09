from __future__ import print_function
import os
from .handlers import RealChangeHandler


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



class SyncFilemakerHandler(RealChangeCronHandler):
    def get(self):
        self.ensure_cron()
        self.respond("OK", status=200)










