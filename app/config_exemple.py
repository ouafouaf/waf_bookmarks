import os
basedir = os.path.abspath(os.path.dirname(__file__))

## EXEMPLE OF CONFIG.PY FILE
## Change content
## Rename to config.py

class Config(object):
    SECRET_KEY = 'something'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_DEBUG = True