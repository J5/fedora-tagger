#!/bin/bash
PYTHONPATH=fedoratagger nosetests --with-coverage --cover-erase \
    --cover-package=fedoratagger $*
