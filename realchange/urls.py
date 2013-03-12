from webapp2 import Route
import cron
import handlers


URLS = [
    # Basic URLs
    Route(r'/', handlers.HomeHandler, name='home'),
    Route(r'/embed/', handlers.EmbedHandler, name='embed'),

    # CRON and TASK URLs
    Route(r'/cron/sync/fm/', cron.SyncFileMakerCronHandler, name='cron-sync-filemaker'),
    Route(r'/task/sync/fm/', cron.SyncFileMakerTaskHandler, name='task-sync-filemaker'),
    Route(r'/task/vendor/geocode/', cron.GeocodeTaskHandler, name='task-vendor-geocode'),

    # Vendor JSON API
    Route(r'/api/vendors/', handlers.VendorHandler, name='vendors'),
]


