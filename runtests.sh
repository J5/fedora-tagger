#!/bin/bash
PYTHONPATH=taggerapi nosetests --with-coverage --cover-erase \
--cover-package=taggerapi $*
