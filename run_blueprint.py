#!env python
import sys
from pprint import pprint
from flask import Flask

def show(obj):
    '''Show the dump of the properties of the object.'''
    pprint(vars(obj))

# create our application
app = Flask(__name__)

# Register Blueprint modules
from contact import contact_page
app.register_blueprint(contact_page, url_prefix='/')

if sys.flags.interactive:
    print 'Loading Flask App in console mode. Use show(<obj)> to introspect.'
elif __name__ == '__main__':
    app.debug = True
    app.run(host = "0.0.0.0", port = 8080)
