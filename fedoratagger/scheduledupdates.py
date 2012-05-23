from tgscheduler import start_scheduler
from tgscheduler.scheduler import add_interval_task

import logging
log = logging.getLogger(__name__)

def update_summaries():
    # Only do the first 150 since this takes so long to chew through.
    N = 150
    import fedoratagger.websetup.bootstrap
    # This could take a long time
    fedoratagger.websetup.bootstrap.import_pkgdb_tags()
    fedoratagger.websetup.bootstrap.import_koji_pkgs()
    fedoratagger.websetup.bootstrap.update_summaries(N=N)

def schedule():
    ONE_HOUR = 60 * 60

    add_interval_task(
        action=update_summaries,
        taskname='updatesummaries',
        interval=ONE_HOUR,
        initialdelay=8,
    )

    log.info("Starting Scheduler Manager")
    start_scheduler()
