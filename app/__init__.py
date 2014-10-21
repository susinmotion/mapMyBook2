#!/newEnv/bin/python
from flask import Flask
from flask.ext.cache import Cache
#NAME OF YOUR MODULE =...
app = Flask(__name__, static_url_path='')
cache = Cache(app,config={'CACHE_TYPE': 'simple'})
#talk to config object...not sure about naming here.
#app.config.from_object('config')
#from CONTAINING FOLDER OF this file import NAME OF THIS FILE
from app import views
from libraries import Library