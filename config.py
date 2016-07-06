import os

WTF_CSRF_ENABLED = False
SECRET_KEY = os.environ.get('SECRET_KEY')
