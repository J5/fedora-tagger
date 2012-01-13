Fedora-Tagger
=============

A TurboGears 2 app for helping us tag fedora packages.  Users who login with
their `FAS <https://admin.fedoraproject.org/accounts>`_ credentials can upvote
and downvote tags on packages as well as add new tags alltogether.

Vote it up!  The votes you place are tracked and rank you against other users.

Hotkeys
-------

.. hotkeys

+--------------------+----------------+
| ``j`` *or* ``↓``   | next item      |
+--------------------+----------------+
| ``k`` *or* ``↑``   | previous item  |
+--------------------+----------------+
| ``l`` *or* ``→``   | upvote tag     |
+--------------------+----------------+
| ``h`` *or* ``←``   | downvote tag   |
+--------------------+----------------+
| ``i`` *or* ``a``   | add new tag    |
+--------------------+----------------+
| ``b``              | leaderboard    |
+--------------------+----------------+
| ``s``              | search packages|
+--------------------+----------------+
| ``esc``            | help           |
+--------------------+----------------+

.. hotkeys

Running from source
-------------------

Setup a virtual environment::

  $ virtualenv ~/tagger-env
  $ source ~/tagger-env/bin/activate

Get ``python-fedora``::

  $ wget https://fedorahosted.org/releases/p/y/python-fedora/python-fedora-0.3.25.tar.gz
  $ tar -xzvf python-fedora-0.3.25.tar.gz
  $ pushd python-fedora-0.3.25
  $ python setup.py develop
  $ popd

Get fedora-tagger::

  $ git clone git://github.com/ralphbean/fedora-tagger.git
  $ cd fedora-tagger
  $ python setup.py develop
  $ paster setup-app development.ini
  $ paster serve development.ini

The setup-app step will try and use ``yum`` to get package summaries.  It won't
be able to find it if you specify ``--no-site-packages`` with virtualenv.

Old Notes
=========

Workflow
--------

 * Randomly select two packages (you will need to cache a list of all packages and randomly generate an index)
 * Display the first package on the center card w/ the top 3 tags and randomly select 2 tags from the list of tags associated with this package (not including the tags already selected)
 * Do the same for the right card with the second package but make sure they can't be clicked
 * With each tag the user can click if they like or dislike the tag, once they select they can change their mind
 * A form element is also needed to add new tags
 * new tags start with a count of one in the like field
 * clicking on the right card generates a new right card moves all cards one place to the left
 * all fields should be instantly recorded
 * regardless of the format used to store the results a command line script shall be provided that outputs the data in JSON format
 * The script must be able to be run even if the web service is not running
 * Output should be in this format::

     {_format_version: ${current_version},
      ${package_name}:[{tag: ${tag_label},
                        like: ${num_likes},
                        dislike: ${num_dislike}},
                        total: ${num_likes} - ${num_dislike}
                        ...
                      ]
     }

 * The tag list for each package should be sorted in descending order by the total score, ties are broken by the number of votes cast and if there is still a tie, alphabetically by the tag


User Scoring
------------

Eventually we want users to be able to log in and get points for participating.  This is not a priotity for the initial implementation.

