#!/newEnv/bin/python
import os
from flask import Flask
from flask.ext.assets import Environment, Bundle
from flask.ext.cache import Cache
#NAME OF YOUR MODULE =...
app = Flask(__name__, static_url_path='')
#talk to config object...not sure about naming here.
#app.config.from_object('config')
#from CONTAINING FOLDER OF this file import NAME OF THIS FILE
from app import views
from libraries import Library



assets = Environment(app)
assets.load_path = [
    os.path.join(os.path.dirname(__file__), 'css'),
]


css = Bundle('style.css')
assets.register('css_all', css)