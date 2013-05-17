#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Run 'fab --list' to see list of available commands.

References:
# http://docs.fabfile.org/en/1.0.1/usage/execution.html#how-host-lists-are-constructed
'''

import platform
import os
import sys
import code
from fabric.api import local,task

assert ('2','6') <= platform.python_version_tuple() < ('3','0')
PROJ_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJ_DIR)
os.chdir(PROJ_DIR)

def testing_framework(run=False):
    from pprint import pprint
    from flask import Flask
    def show(obj):
        '''Show the dump of the properties of the object.'''
        pprint(vars(obj))

    # create our application
    app = Flask(__name__)

    # Register Blueprint modules
    from contact import contact_page
    app.register_blueprint(contact_page, url_prefix='/contact')

    if not run:
        print 'Loading Flask App in console mode. Use show(<obj)> to introspect.'
        code.interact(local=locals())
    elif run:
        app.debug = True
        app.run(host = "0.0.0.0", port = 8080)

@task
def console():
    '''Load the application in an interactive console.'''
    testing_framework(run=False)

@task
def server():
    '''Run the dev server'''
    testing_framework(run=True)

@task
def clean():
    '''Clear the cached .pyc files.'''
    local("find . \( -iname '*.pyc' -o -name '*~' \) -exec rm -v {} \;", capture=False)
