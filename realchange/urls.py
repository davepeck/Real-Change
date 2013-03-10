from webapp2 import Route
import cron
import handlers


URLS = [
    # Basic URLs
    Route(r'/', handlers.HomeHandler, name='home'),

    # CRON and TASK URLs
    Route(r'/cron/sync/fm/', cron.SyncFileMakerCronHandler, name='sync-filemaker'),
    Route(r'/task/sync/fm/', cron.SyncFileMakerTaskHandler, name='sync-filemaker'),

    # Vendor JSON API
    Route(r'/api/vendors/', handlers.VendorHandler, name='vendors'),
]


