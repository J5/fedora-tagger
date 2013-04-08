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
- [ ] Get rid of the /app/ blueprint.  The original idea was to have nice
      separation of the api and the js app, however, making users navigate
      to https://apps.fedoraproject.org/tagger/app/nethack feels a little
      cumbersome.  If we can un-nest the URLs while keeping the blueprint,
      that would be best.  My bet is that we'll have to attach all the
      @FRONTEND routes to @APP instead (and get rid of the frontend
      blueprint all together).
