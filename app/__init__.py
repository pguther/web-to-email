from flask import Flask
import os

app = Flask(__name__)
app.config.from_object('config')

if os.environ.get('HEROKU') is not None:
    import logging
    stream_handler = logging.StreamHandler()
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('web-to-email startup')

from app import views
