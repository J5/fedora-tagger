#!/bin/bash

if [ -f /usr/local/turbogears/tagger/shell.py ] ; then
        echo "Using the /usr/local instance"
        /usr/local/pythonenv/tagger/bin/ipython -i /usr/local/turbogears/tagger/shell.py
else 
        echo "Using local dev instance"
        ipython -i -c 'execfile("shell.py")'
fi

