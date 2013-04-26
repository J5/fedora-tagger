= Pre-Staging TODO list =

This is a list of stuff we need to figure out before we should trying
moving from a dev box to a staging box.  Please add items as you see fit.

- [x] Static resources.  Resources should be served from
      /usr/share/fedoratagger
- [x] Encoding issues.  It looks like using mako>=0.4.2 solves this.
- [x] Spec file.  We need an rpm.
- [x] Re-enable fedmsg.  It is hardcoded disabled for rank changes.  We need
      to add the old messages back in.  Refer to
      http://fedmsg.com/en/latest/topics/ for examples of the old messages.
- [x] Get rid of the /app/ blueprint.  The original idea was to have nice
      separation of the api and the js app, however, making users navigate
      to https://apps.fedoraproject.org/tagger/app/nethack feels a little
      cumbersome.  If we can un-nest the URLs while keeping the blueprint,
      that would be best.  My bet is that we'll have to attach all the
      @FRONTEND routes to @APP instead (and get rid of the frontend
      blueprint all together).

      Nope -- I didn't have to ditch it, just change the mount path.
- [x] yumdb - so bodhi can slurp down the tags for mashing
      For this, hit /api/tag/dump
- [x] notification toggling
- [x] force _update from pkgdb and koji.  Tagger needs to be made aware of
      new packages that get introduced.
      There is now a fedoratagger-update-db script which can be run as a
      cron job.
- [x] add support for blacklisted tags.
- [x] remove anonymous user from the leaderboard
- [x] add fedmsg support for ratings, other things?
- [x] frontend for rating (stars?)
- [x] make sure jenkins tests are passing for completeness' sake.
- [x] Package up python-flask-mako
      https://bugzilla.redhat.com/show_bug.cgi?id=948626
- [ ] Build an rpm in koji and get it into the infra-testing repo.
      Lather, rinse, repeat.
