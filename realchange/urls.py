from webapp2 import Route
import cron
import handlers


URLS = [
    # Basic URLs
    Route(r'/', handlers.HomeHandler, name='home'),

    # CRON URLs
    Route(r'/cron/sync/fm/', cron.SyncFileMakerHandler, name='sync-filemaker'),

    # Vendor JSON API
    Route(r'/api/vendors/', handlers.VendorHandler, name='vendors'),
]


