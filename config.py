import os

WTF_CSRF_ENABLED = False
SECRET_KEY = os.environ.get('CSRF_TOKEN')
